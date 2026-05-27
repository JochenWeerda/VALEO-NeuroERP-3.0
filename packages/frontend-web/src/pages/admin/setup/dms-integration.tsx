import { useCallback, useEffect, useMemo, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { Badge } from '@/components/ui/badge'
import { CheckCircle2, ExternalLink, Loader2 } from 'lucide-react'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type BootstrapResult = {
  ok: boolean
  created?: number
  updated?: number
  message?: string
  document_types?: number
  metadata_types?: number
  error?: string
}

type DmsStatus = {
  ok: boolean
  configured: boolean
  base?: string
  document_types?: number
  metadata_types?: number
  message?: string
}

type TestConnectionResult = {
  ok: boolean
  error?: string
}

type TestState = 'idle' | 'ok' | 'fail'
type DmsSetupRole = 'it' | 'fachbereich' | 'datenschutz' | 'leitung'

const dmsSetupRoles = [
  { id: 'it', label: 'IT', description: 'Richtet Verbindung, Token und technischen Verbindungstest ein.' },
  { id: 'fachbereich', label: 'Fachbereich', description: 'Prueft, ob Dokumenttypen und Metadaten fuer die Arbeit passen.' },
  { id: 'datenschutz', label: 'Datenschutz', description: 'Achtet auf Zugriff, Aufbewahrung und saubere Verarbeitung im DMS.' },
  { id: 'leitung', label: 'Leitung', description: 'Sieht, ob die DMS-Anbindung fuer produktive Dokumentarbeit bereit ist.' },
] satisfies Array<{ id: DmsSetupRole; label: string; description: string }>

const DEFAULT_BASE_URL = 'http://localhost:8010'
const UNKNOWN_ERROR_MESSAGE = 'Unbekannter Fehler'
const BOOTSTRAP_SUCCESS_TITLE = 'Mayan-DMS integriert'
const BOOTSTRAP_FAILURE_TITLE = 'Bootstrap-Fehler'
const VALIDATION_FAILURE_TITLE = 'Validierung fehlgeschlagen'
const VALIDATION_FAILURE_DESCRIPTION = 'Bitte Base-URL und Token eingeben'

const isNonEmptyString = (value: unknown): value is string => {
  return typeof value === 'string' && value.trim().length > 0
}

const formatBootstrapSummary = (result: BootstrapResult): string => {
  const docTypes = typeof result.document_types === 'number' ? result.document_types : 0
  const metadataTypes = typeof result.metadata_types === 'number' ? result.metadata_types : 0
  const created = typeof result.created === 'number' ? result.created : 0
  const updated = typeof result.updated === 'number' ? result.updated : 0

  return `${docTypes} Dokumenttypen, ${metadataTypes} Metadaten, ${created} Bindings, ${updated} aktualisiert`
}

const openExternal = (target?: string): void => {
  if (isNonEmptyString(target)) {
    window.open(target, '_blank', 'noopener')
  }
}

export default function DmsIntegrationCard(): JSX.Element {
  const { toast } = useToast()
  const [dialogOpen, setDialogOpen] = useState<boolean>(false)
  const [baseUrl, setBaseUrl] = useState<string>(DEFAULT_BASE_URL)
  const [token, setToken] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [testState, setTestState] = useState<TestState>('idle')
  const [status, setStatus] = useState<DmsStatus | null>(null)
  const [roleFocus, setRoleFocus] = useState<DmsSetupRole>('it')

  const hasCredentials = useMemo(() => isNonEmptyString(baseUrl) && isNonEmptyString(token), [baseUrl, token])
  const isConfigured = status?.configured === true
  const configuredBaseUrl = isConfigured && isNonEmptyString(status?.base) ? status.base : undefined
  const dmsSetupBlockers = [
    !isConfigured ? 'DMS noch nicht eingerichtet' : null,
    isConfigured && !configuredBaseUrl ? 'Base-URL fehlt' : null,
    testState === 'fail' ? 'Verbindungstest fehlgeschlagen' : null,
  ].filter((item): item is string => Boolean(item))
  const dmsSetupReady = isConfigured && dmsSetupBlockers.length === 0
  const nextSetupAction = dmsSetupReady
    ? 'DMS oeffnen und Dokumenttypen im produktiven Ablauf pruefen.'
    : testState === 'ok'
      ? 'Einrichtung starten, damit Dokumenttypen und Metadaten angelegt werden.'
      : hasCredentials
        ? 'Verbindung testen und danach die Einrichtung starten.'
        : 'Base-URL und API-Token eintragen.'

  const loadStatus = useCallback(async (): Promise<void> => {
    try {
      const res = await apiClient.get<DmsStatus>('/api/v1/admin/dms/status')
      const data = res.data
      setStatus(data)
      if (data && isNonEmptyString(data.base)) {
        setBaseUrl(data.base)
      }
    } catch (error) {
      setStatus(null)
    }
  }, [])

  useEffect(() => {
    void loadStatus()
  }, [loadStatus])

  const notifyValidationFailure = (): void => {
    toast({
      title: VALIDATION_FAILURE_TITLE,
      description: VALIDATION_FAILURE_DESCRIPTION,
      variant: 'destructive',
    })
  }

  const testConnection = useCallback(async (): Promise<void> => {
    if (!hasCredentials) {
      notifyValidationFailure()
      return
    }

    setLoading(true)
    try {
      const res = await apiClient.post<TestConnectionResult>('/api/v1/admin/dms/test', { base: baseUrl, token })
      const payload = res.data
      const nextState: TestState = payload.ok ? 'ok' : 'fail'
      setTestState(nextState)

      toast({
        title: payload.ok ? 'Verbindung getestet' : 'Verbindung fehlgeschlagen',
        description: payload.ok ? 'Die Mayan-API ist erreichbar.' : (payload.error ?? UNKNOWN_ERROR_MESSAGE),
        variant: payload.ok ? 'default' : 'destructive',
      })
    } catch (error) {
      setTestState('fail')
      toast({
        title: 'Verbindungsfehler',
        description: getAxiosErrorMessage(error),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [baseUrl, hasCredentials, toast, token])

  const bootstrap = useCallback(async (): Promise<void> => {
    if (!hasCredentials) {
      notifyValidationFailure()
      return
    }

    setLoading(true)
    try {
      const res = await apiClient.post<BootstrapResult>('/api/v1/admin/dms/bootstrap', { base: baseUrl, token })
      const payload = res.data
      if (payload.ok) {
        toast({
          title: BOOTSTRAP_SUCCESS_TITLE,
          description: formatBootstrapSummary(payload),
          variant: 'default',
        })
        setDialogOpen(false)
        setTestState('ok')
        await loadStatus()
        return
      }

      toast({
        title: BOOTSTRAP_FAILURE_TITLE,
        description: payload.message ?? UNKNOWN_ERROR_MESSAGE,
        variant: 'destructive',
      })
    } catch (error) {
      toast({
        title: BOOTSTRAP_FAILURE_TITLE,
        description: getAxiosErrorMessage(error),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [baseUrl, hasCredentials, loadStatus, toast, token])

  return (
    <Card className="border border-dashed">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle>Mayan DMS</CardTitle>
            <CardDescription>DMS-Integration fuellt Inbox, Dokument-Metadaten und Workflow.</CardDescription>
          </div>
          {isConfigured && (
            <Badge variant="default" className="gap-1">
              <CheckCircle2 className="h-4 w-4" />
              Aktiv
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="p-0 space-y-4">
        <div className="space-y-4 p-6 pb-0">
          <RoleFocusBar roles={dmsSetupRoles} value={roleFocus} onChange={setRoleFocus} title="Wer richtet das DMS ein?" />
          <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
            <ManagementDecisionPanel
              decision={{
                allowed: dmsSetupReady,
                allowedLabel: 'DMS bereit',
                blockedLabel: 'Einrichtung offen',
                summary: dmsSetupReady
                  ? 'Die DMS-Anbindung ist eingerichtet. Dokumenttypen, Metadaten und Zugriff koennen im Fachprozess genutzt werden.'
                  : `Vor produktiver Dokumentarbeit fehlen noch: ${dmsSetupBlockers.join(', ') || 'Verbindungstest und Einrichtung'}.`,
                blockerCount: dmsSetupBlockers.length || (dmsSetupReady ? 0 : 1),
                nextFocus: dmsSetupReady ? 'Dokumenttypen pruefen' : nextSetupAction,
                template: { label: 'DMS-Einrichtungsprotokoll', href: '/docs/dms/dms-einrichtungsprotokoll.md' },
              }}
            />
            <div className="space-y-4">
              <NextActionPanel action={nextSetupAction} tone={dmsSetupReady ? 'emerald' : 'amber'} />
              <EvidenceTemplateLink link={{ label: 'DMS-Betriebsnachweis', href: '/docs/dms/dms-betriebsnachweis.md' }} />
            </div>
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <OperationalTaskPlan
              title="Einrichtungsplan"
              items={[
                { label: 'Zugangsdaten eintragen', done: hasCredentials || isConfigured, hint: isConfigured ? 'DMS ist bereits konfiguriert.' : 'Base-URL und API-Token sind erforderlich.' },
                { label: 'Verbindung testen', done: testState === 'ok' || isConfigured, hint: testState === 'fail' ? 'Letzter Test ist fehlgeschlagen.' : 'Test bestaetigt, dass das DMS erreichbar ist.' },
                { label: 'Dokumenttypen anlegen', done: Boolean(status?.document_types), hint: `${status?.document_types ?? 0} Dokumenttypen bekannt.` },
                { label: 'Metadaten anlegen', done: Boolean(status?.metadata_types), hint: `${status?.metadata_types ?? 0} Metadatenfelder bekannt.` },
              ]}
            />
            <CrudCapabilityChecklist
              capabilities={[
                { key: 'create', label: 'Einrichtung starten', available: true, hint: 'Bootstrap legt Dokumenttypen und Metadaten an.' },
                { key: 'read', label: 'Status lesen', available: true, hint: 'Konfiguration, Base-URL und Anzahl Typen sind sichtbar.' },
                { key: 'update', label: 'Neu konfigurieren', available: true, hint: 'Bestehende Verbindung kann angepasst werden.' },
                { key: 'approve', label: 'Verbindung testen', available: true, hint: 'Erfolgreicher Test ist Voraussetzung fuer Einrichtung.' },
                { key: 'evidence', label: 'Betriebsnachweis', available: true, hint: 'Einrichtungs- und Betriebsnachweis sind verlinkt.' },
                { key: 'audit', label: 'Aenderungshistorie', available: false, hint: 'Eigene Audit-Zeitleiste ist hier noch nicht angebunden.' },
              ]}
            />
          </div>
        </div>

        {isConfigured ? (
          <div className="space-y-3 p-6">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Base-URL:</span>
              <code className="rounded bg-muted px-2 py-1 text-xs">{configuredBaseUrl}</code>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Document Types:</span>
              <Badge variant="outline">{status?.document_types ?? 0}</Badge>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Metadata Types:</span>
              <Badge variant="outline">{status?.metadata_types ?? 0}</Badge>
            </div>
            <div className="flex gap-2 pt-2">
              <Button variant="outline" onClick={() => openExternal(configuredBaseUrl)} disabled={!isNonEmptyString(configuredBaseUrl)}>
                <ExternalLink className="h-4 w-4 mr-2" />
                Im DMS oeffnen
              </Button>
              <Button variant="outline" onClick={() => setDialogOpen(true)}>
                Neu konfigurieren
              </Button>
            </div>
          </div>
        ) : (
          <>
            <Button onClick={() => setDialogOpen(true)}>Jetzt einrichten</Button>
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogContent className="sm:max-w-[560px]">
              <DialogHeader>
                <DialogTitle>Mayan-DMS verbinden</DialogTitle>
              </DialogHeader>

              <div className="grid gap-4 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="base">DMS-Basis-URL</Label>
                  <Input
                    id="base"
                    value={baseUrl}
                    onChange={(event) => setBaseUrl(event.target.value)}
                    placeholder="http://localhost:8010"
                    disabled={loading}
                  />
                  <p className="text-xs text-muted-foreground">
                    URL zu Ihrer Mayan-DMS-Instanz (inklusive http:// oder https://).
                  </p>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="token">API-Token</Label>
                  <Input
                    id="token"
                    type="password"
                    value={token}
                    onChange={(event) => setToken(event.target.value)}
                    placeholder="Token aus dem Mayan-Admin-Panel"
                    disabled={loading}
                  />
                  <p className="text-xs text-muted-foreground">
                    Erstellen Sie einen API-Token in Mayan unter Einstellungen -&gt; API-Token.
                  </p>
                </div>

                {testState !== 'idle' && (
                  <div
                    className={`p-3 rounded-lg ${
                      testState === 'ok'
                        ? 'border border-[hsl(var(--color-semantic-success-500-hsl)/0.3)] bg-[hsl(var(--color-semantic-success-50-hsl))]'
                        : 'border border-destructive/30 bg-destructive/10'
                    }`}
                  >
                    <p
                      className={`text-sm font-medium ${
                        testState === 'ok' ? 'text-[hsl(var(--color-semantic-success-700-hsl))]' : 'text-destructive'
                      }`}
                    >
                      {testState === 'ok' ? 'Verbindung erfolgreich getestet' : 'Verbindung fehlgeschlagen'}
                    </p>
                  </div>
                )}
              </div>

              <DialogFooter className="gap-2">
                <Button type="button" variant="secondary" onClick={() => { void testConnection() }} disabled={loading || !hasCredentials}>
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Teste...
                    </>
                  ) : (
                    <>
                      Verbindung testen
                      {testState === 'ok' && ' OK'}
                      {testState === 'fail' && ' Fehler'}
                    </>
                  )}
                </Button>

                <Button
                  type="button"
                  onClick={() => { void bootstrap() }}
                  disabled={loading || !hasCredentials || testState !== 'ok'}
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Einrichten...
                    </>
                  ) : (
                    'Einrichten'
                  )}
                </Button>
              </DialogFooter>
            </DialogContent>
            </Dialog>
          </>
        )}
      </CardContent>
    </Card>
  )
}
