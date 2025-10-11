import { useCallback, useEffect, useMemo, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { CheckCircle2, ExternalLink, Loader2 } from 'lucide-react'

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

  const hasCredentials = useMemo(() => isNonEmptyString(baseUrl) && isNonEmptyString(token), [baseUrl, token])
  const isConfigured = status?.configured === true
  const configuredBaseUrl = isConfigured && isNonEmptyString(status?.base) ? status.base : undefined

  const loadStatus = useCallback(async (): Promise<void> => {
    try {
      const response = await fetch('/api/admin/dms/status')
      const data = (await response.json()) as DmsStatus

      setStatus(data)
      if (isNonEmptyString(data.base)) {
        setBaseUrl(data.base)
      }
    } catch (error) {
      console.error('Failed to load DMS status:', error)
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
      const response = await fetch('/api/admin/dms/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base: baseUrl, token }),
      })

      const payload = (await response.json()) as TestConnectionResult
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
        description: error instanceof Error ? error.message : UNKNOWN_ERROR_MESSAGE,
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
      const response = await fetch('/api/admin/dms/bootstrap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base: baseUrl, token }),
      })

      const payload = (await response.json()) as BootstrapResult
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
        description: error instanceof Error ? error.message : UNKNOWN_ERROR_MESSAGE,
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
        {isConfigured ? (
          <div className="space-y-3 p-6">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Base-URL:</span>
              <code className="bg-gray-100 px-2 py-1 rounded text-xs">{configuredBaseUrl}</code>
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
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button>Jetzt einrichten</Button>
            </DialogTrigger>
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
                      testState === 'ok' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                    }`}
                  >
                    <p
                      className={`text-sm font-medium ${
                        testState === 'ok' ? 'text-green-900' : 'text-red-900'
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
        )}
      </CardContent>
    </Card>
  )
}
