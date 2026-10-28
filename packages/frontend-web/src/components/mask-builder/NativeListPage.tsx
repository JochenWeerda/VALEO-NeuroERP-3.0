import { useCallback, useEffect, useMemo, useRef, useState, type RefObject } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import { useScreenDefinition } from '@/lib/api/masks'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { exportToCSV } from '@/lib/export-utils'
import { UniversalNativeCockpitPage } from './UniversalNativeCockpitPage'
import { ActionInputDialog } from './renderers/ActionInputDialog'
import { useScreenPermissions } from './runtime/screen-permissions'
import { readDownload, saveReadDownload, type ReadDownloadResult } from './runtime/read-download'
import type { ScreenActionDefinition, ScreenDefinition } from './schema'
import { saveFlowSpineResumeCheckpoint } from '@/lib/api/flow-spines'
import { listNavigationTarget, listCSV } from './runtime/list-navigation'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useTouchDevice } from '@/hooks/useTouchDevice'

type Row = Record<string, unknown>

function ListWorkflowContext({ onChange }: { onChange: (query: URLSearchParams) => void }): null {
  const [query] = useSearchParams()
  useEffect(() => onChange(new URLSearchParams(query)), [query, onChange])
  return null
}

function ListKeyboardNavigation({ onNew, surface }: { onNew: () => void; surface: RefObject<HTMLDivElement | null> }): JSX.Element | null {
  const isTouch = useTouchDevice()
  const shortcuts = buildCoreMaskShortcuts({ onNew, onSearch: () => surface.current?.querySelector<HTMLInputElement>('input[type="search"]')?.focus() })
  useKeyboardShortcuts(shortcuts)
  return isTouch ? null : <KeyboardShortcutBar shortcuts={shortcuts} />
}

type Aktion = Pick<ScreenActionDefinition, 'key' | 'label'> & {
  permission?: string
  commandEndpoint?: string
  method?: 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  navigationRoute?: string
  localEffect?: ScreenActionDefinition['localEffect']
  inputFields?: ScreenActionDefinition['inputFields']
  download?: ScreenActionDefinition['download']
  requiresConfirmation?: boolean
  auditReasonRequired?: boolean
  dangerLevel?: string
}
/** Maskenkommando (``success``) oder ein Fachweg ohne Umschlag: dort zaehlt die 2xx-Antwort als Erfolg. */
type MaskCommandResult = { success?: boolean; summary?: string | null; error?: string | null } | null

const ernst = new Set(['moderate', 'high', 'critical'])

function findeAktion(schema: ScreenDefinition | undefined, key: string): Aktion | undefined {
  const kopf = (schema?.actions ?? []).find(action => action.key === key)
  if (kopf) return kopf as Aktion
  for (const table of schema?.tables ?? []) {
    const zeile = table.rowActions?.find(action => action.key === key)
    if (zeile) return zeile as Aktion
  }
  return undefined
}

function vorbelegung(aktion: Aktion, row: Row): Row {
  return Object.fromEntries((aktion.inputFields ?? [])
    .filter(feld => row[feld.key] !== undefined && row[feld.key] !== null)
    .map(feld => [feld.key, row[feld.key]]))
}

function zielRoute(vorlage: string, row: Row): string {
  return vorlage.replace(/\{(\w+)\}/g, (_ganz, feld: string) =>
    encodeURIComponent(String(feld === 'entity_id' ? row.id ?? '' : row[feld] ?? '')))
}

/**
 * Liste einer ScreenDefinition mit allen Aktionen aus der Definition (MASK-STUDIO-ROLLOUT): Navigation,
 * Kommando-Wege mit deklarierten Eingaben, Bestaetigung und Pflichtgrund. Kein seitenspezifischer Code; dieselben
 * Kommando-Wege rufen CLI und MCP. Je Zeile und Aktion laeuft hoechstens ein Auftrag.
 */
export function NativeListPage({ screenId, testId }: { screenId: string; testId?: string }): JSX.Element {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const schema = useScreenDefinition(screenId).data
  const permissions = useScreenPermissions(schema)
  const surface = useRef<HTMLDivElement | null>(null)
  const listData = useRef<Row[] | null>(null)
  const workflowQuery = useRef(new URLSearchParams())
  const captureRows = useCallback((rows: Row[]) => { listData.current = rows }, [])
  const captureQuery = useCallback((query: URLSearchParams) => { workflowQuery.current = query }, [])
  const laufend = useRef(new Set<string>())
  const absicht = useRef<{ inhalt: string; id: string } | null>(null)
  const [auftrag, setAuftrag] = useState<{ aktion: Aktion; row: Row; werte: Row } | null>(null)
  const [stufe, setStufe] = useState<'eingabe' | 'bestaetigung' | null>(null)
  const [grund, setGrund] = useState('')
  const [sendet, setSendet] = useState(false)
  const [downloadResult, setDownloadResult] = useState<ReadDownloadResult | null>(null)
  const initialInputs = useMemo(() => ({ ...vorbelegung(auftrag?.aktion ?? { key: '', label: '' }, auftrag?.row ?? {}),
    ...auftrag?.werte }), [auftrag])

  async function herunterladen(aktion: Aktion, values: Row): Promise<void> {
    if (laufend.current.has('read-download')) return
    laufend.current.add('read-download')
    setSendet(true)
    try {
      setDownloadResult(await readDownload(aktion as ScreenActionDefinition, values))
      schliessen()
    } catch (error) {
      toast({ title: 'Export fehlgeschlagen', description: getAxiosErrorMessage(error), variant: 'destructive' })
    } finally {
      laufend.current.delete('read-download')
      setSendet(false)
    }
  }

  function schliessen(): void {
    setAuftrag(null)
    setStufe(null)
    setGrund('')
  }

  async function ausfuehren(aktion: Aktion, row: Row, werte: Row, begruendung: string): Promise<void> {
    const schluessel = `${String(row.id ?? '')}:${aktion.key}`
    if (!aktion.commandEndpoint || laufend.current.has(schluessel)) return
    laufend.current.add(schluessel)
    setSendet(true)
    try {
      // Jeder Platzhalter aus der Zeile ({entity_id} = id, sonst gleichnamiges Feld), wie bei Navigationsrouten.
      const pfad = zielRoute(aktion.commandEndpoint, row)
      const versioniert = /^\/api\/v1\/studio\/entities\/studio_[a-z0-9_]+\/[^/]+\/actions\/(update|delete)$/.test(pfad)
      if (versioniert && (!Number.isInteger(row.version) || Number(row.version) < 1)) {
        throw new Error('Die angezeigte Version fehlt. Bitte die Liste neu laden.')
      }
      const inhalt = JSON.stringify([screenId, pfad, row.version, werte, begruendung])
      if (absicht.current?.inhalt !== inhalt) absicht.current = { inhalt, id: crypto.randomUUID() }
      const { data } = await apiClient.request<MaskCommandResult>({
        url: pfad,
        method: aktion.method ?? 'POST',
        data: { ...werte, ...(versioniert ? { expected_version: row.version } : {}),
          ...(begruendung ? { _auditReason: begruendung } : {}), _idempotencyKey: absicht.current.id },
      })
      if (data && typeof data === 'object' && data.success === false) {
        throw new Error(data.error ?? 'Die Aktion wurde abgelehnt.')
      }
      // Entity queries start with screenId; tenant-isolated table queries with tenantId.
      await queryClient.invalidateQueries({ predicate: query =>
        query.queryKey[0] === screenId || query.queryKey[1] === screenId })
      toast({ title: aktion.label, description: data?.summary ?? 'Ausgefuehrt.' })
      absicht.current = null
      schliessen()
    } catch (error) {
      toast({ title: `${aktion.label} fehlgeschlagen`, description: getAxiosErrorMessage(error), variant: 'destructive' })
    } finally {
      laufend.current.delete(schluessel)
      setSendet(false)
    }
  }

  async function navigateList(path: string, create: boolean): Promise<void> {
    if (laufend.current.has('navigation')) return
    laufend.current.add('navigation')
    try {
      const target = listNavigationTarget(path, workflowQuery.current, schema?.listExperience?.workflowResume, create)
      if (target.checkpoint) {
        const checkpoint = target.checkpoint
        await saveFlowSpineResumeCheckpoint(checkpoint.process, checkpoint.instanceId, checkpoint.payload)
      }
      navigate(target.url)
    } catch {
      toast({ title: 'Vorgang konnte nicht geöffnet werden', description: 'Bitte erneut versuchen.', variant: 'destructive' })
    } finally {
      laufend.current.delete('navigation')
    }
  }

  async function exportieren(): Promise<void> {
    if (schema?.listExperience) {
      const rows = listData.current
      if (!rows?.length) {
        toast({ title: 'Keine Daten', description: 'Es gibt nichts zu exportieren.', variant: 'destructive' })
        return
      }
      const declaration = schema.listExperience.export
      const blob = new Blob([listCSV(rows, declaration.columns, declaration.delimiter)], { type: 'text/csv;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${declaration.filenamePrefix}${new Date().toISOString().slice(0, 10)}.csv`
      link.click()
      URL.revokeObjectURL(url)
      return
    }
    // Older definitions retain their existing export contract.
    const tabelle = schema?.tables?.[0]
    const quelle = schema?.dataSources?.find(ds => ds.key === tabelle?.dataSourceKey)
    if (!tabelle || !quelle?.endpoint) return
    try {
      const antwort = (await apiClient.get<unknown>(quelle.endpoint)).data
      const zeilen = (Array.isArray(antwort) ? antwort
        : ((antwort as { items?: Row[]; data?: Row[] })?.items ?? (antwort as { data?: Row[] })?.data ?? [])) as Row[]
      if (zeilen.length === 0) {
        toast({ title: 'Keine Daten', description: 'Es gibt nichts zu exportieren.', variant: 'destructive' })
        return
      }
      exportToCSV(zeilen, `${screenId.replaceAll('/', '-')}-${new Date().toISOString().slice(0, 10)}.csv`,
        tabelle.columns.map(spalte => ({ key: spalte.key, label: spalte.label })))
    } catch (error) {
      toast({ title: 'Export fehlgeschlagen', description: getAxiosErrorMessage(error), variant: 'destructive' })
    }
  }

  function handleAction(key: string, payload: Row): void {
    const aktion = findeAktion(schema, key)
    if (!aktion || (aktion.permission && !permissions.includes(aktion.permission))) return
    if (aktion.download) {
      setAuftrag({ aktion, row: payload, werte: {} })
      setStufe('eingabe')
      return
    }
    if (aktion.localEffect === 'download' && !aktion.commandEndpoint) {
      void exportieren()
      return
    }
    if (aktion.navigationRoute) {
      const path = zielRoute(aktion.navigationRoute, payload)
      if (schema?.listExperience?.workflowResume) void navigateList(path, payload.id == null)
      else navigate(path)
      return
    }
    if (!aktion.commandEndpoint) return
    setAuftrag({ aktion, row: payload, werte: {} })
    setStufe(aktion.inputFields?.length ? 'eingabe' : 'bestaetigung')
  }

  const rowRoute = schema?.tables?.[0]?.rowRouteTemplate
  const aktion = auftrag?.aktion
  const grundPflicht = Boolean(aktion?.auditReasonRequired)
  const grundOk = !grundPflicht || grund.trim().length >= 5

  return (
    <div ref={surface}>
      {schema?.listExperience?.workflowResume && <ListWorkflowContext onChange={captureQuery} />}
      <UniversalNativeCockpitPage screenId={screenId} testId={testId} permissions={permissions}
        onListData={schema?.listExperience ? captureRows : undefined}
        onRowSelect={schema?.listExperience?.workflowResume && rowRoute
          ? (row) => { void navigateList(zielRoute(rowRoute, row), false) }
          : undefined}
        onAction={(key, payload) => { handleAction(key, payload) }} />
      {aktion && stufe === 'eingabe' && (
        <ActionInputDialog
          action={aktion as ScreenActionDefinition}
          // Zeilenaktionen beginnen mit den Werten der Zeile (Bearbeiten), Kopfaktionen leer.
          initialValues={initialInputs}
          open
          onCancel={() => { if (!sendet) schliessen() }}
          submitLabel={sendet ? 'Wird erstellt…' : aktion.download ? aktion.label : 'Weiter'}
          onSubmit={(werte) => {
            setAuftrag({ ...auftrag, werte })
            if (aktion.download) { void herunterladen(aktion, werte); return }
            setStufe('bestaetigung')
          }}
        />
      )}
      {downloadResult && (
        <Dialog open onOpenChange={(open) => { if (!open) setDownloadResult(null) }}>
          <DialogContent aria-describedby="download-preview-description" className="max-w-3xl">
            <DialogHeader><DialogTitle>Exportvorschau</DialogTitle>
              <DialogDescription id="download-preview-description">{downloadResult.filename}</DialogDescription>
            </DialogHeader>
            <pre className="max-h-72 overflow-auto rounded bg-muted p-3 text-xs text-foreground">{downloadResult.content}</pre>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDownloadResult(null)}>Schließen</Button>
              <Button onClick={() => saveReadDownload(downloadResult)}>Datei herunterladen</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
      {aktion && auftrag && stufe === 'bestaetigung' && (
        <Dialog open onOpenChange={(offen) => { if (!offen && !sendet) schliessen() }}>
          <DialogContent aria-describedby="liste-bestaetigung">
            <DialogHeader>
              <DialogTitle>{aktion.label}</DialogTitle>
              <DialogDescription id="liste-bestaetigung">
                {ernst.has(aktion.dangerLevel ?? '')
                  ? 'Diese Aktion aendert den Vorgang und wird protokolliert.'
                  : 'Aktion fuer den gewaehlten Eintrag ausfuehren?'}
              </DialogDescription>
            </DialogHeader>
            {grundPflicht && (
              <div className="space-y-1">
                <Label htmlFor="liste-grund">Begruendung (Pflicht, mind. 5 Zeichen)</Label>
                <Textarea id="liste-grund" value={grund} onChange={(e) => setGrund(e.target.value)} />
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={schliessen} disabled={sendet}>Abbrechen</Button>
              <Button
                variant={ernst.has(aktion.dangerLevel ?? '') ? 'destructive' : 'default'}
                disabled={sendet || !grundOk}
                onClick={() => { void ausfuehren(aktion, auftrag.row, auftrag.werte, grund.trim()) }}
              >
                {sendet ? 'Wird ausgefuehrt…' : aktion.label}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
      {schema?.listExperience && <ListKeyboardNavigation surface={surface}
        onNew={() => { const action = schema.actions?.find(item => item.kind === 'primary' && item.navigationRoute); if (action) handleAction(action.key, {}) }} />}
    </div>
  )
}
