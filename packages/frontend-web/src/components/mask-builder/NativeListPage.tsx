import { useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@/app/routing/typed-router'
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
import type { ScreenActionDefinition, ScreenDefinition } from './schema'

type Row = Record<string, unknown>
type Aktion = Pick<ScreenActionDefinition, 'key' | 'label'> & {
  commandEndpoint?: string
  method?: 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  navigationRoute?: string
  localEffect?: ScreenActionDefinition['localEffect']
  inputFields?: ScreenActionDefinition['inputFields']
  requiresConfirmation?: boolean
  auditReasonRequired?: boolean
  dangerLevel?: string
}
type MaskCommandResult = { success: boolean; summary?: string | null; error?: string | null }

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
  const laufend = useRef(new Set<string>())
  const [auftrag, setAuftrag] = useState<{ aktion: Aktion; row: Row; werte: Row } | null>(null)
  const [stufe, setStufe] = useState<'eingabe' | 'bestaetigung' | null>(null)
  const [grund, setGrund] = useState('')
  const [sendet, setSendet] = useState(false)

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
      const pfad = aktion.commandEndpoint.replace('{entity_id}', encodeURIComponent(String(row.id ?? '')))
      const { data } = await apiClient.request<MaskCommandResult>({
        url: pfad,
        method: aktion.method ?? 'POST',
        data: { ...werte, ...(begruendung ? { _auditReason: begruendung } : {}), _idempotencyKey: crypto.randomUUID() },
      })
      if (!data?.success) throw new Error(data?.error ?? 'Die Aktion wurde abgelehnt.')
      await queryClient.invalidateQueries({ queryKey: [screenId] })
      toast({ title: aktion.label, description: data.summary ?? 'Ausgefuehrt.' })
      schliessen()
    } catch (error) {
      toast({ title: `${aktion.label} fehlgeschlagen`, description: getAxiosErrorMessage(error), variant: 'destructive' })
    } finally {
      laufend.current.delete(schluessel)
      setSendet(false)
    }
  }

  async function exportieren(): Promise<void> {
    // Export der Liste mit den Spalten der Definition (wie zuvor die handgebauten Listen, jetzt deklarativ).
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
    if (!aktion) return
    if (aktion.localEffect === 'download' && !aktion.commandEndpoint) {
      void exportieren()
      return
    }
    if (aktion.navigationRoute) {
      navigate(zielRoute(aktion.navigationRoute, payload))
      return
    }
    if (!aktion.commandEndpoint) return
    setAuftrag({ aktion, row: payload, werte: {} })
    setStufe(aktion.inputFields?.length ? 'eingabe' : 'bestaetigung')
  }

  const aktion = auftrag?.aktion
  const grundPflicht = Boolean(aktion?.auditReasonRequired)
  const grundOk = !grundPflicht || grund.trim().length >= 5

  return (
    <>
      <UniversalNativeCockpitPage screenId={screenId} testId={testId} permissions={permissions}
        onAction={(key, payload) => { handleAction(key, payload) }} />
      {aktion && stufe === 'eingabe' && (
        <ActionInputDialog
          action={aktion as ScreenActionDefinition}
          open
          onCancel={schliessen}
          onSubmit={(werte) => {
            setAuftrag({ ...auftrag, werte })
            setStufe('bestaetigung')
          }}
        />
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
    </>
  )
}
