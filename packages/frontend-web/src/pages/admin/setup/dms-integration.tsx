import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from '@/hooks/use-toast'
import { Badge } from '@/components/ui/badge'
import { Loader2, CheckCircle2, ExternalLink } from 'lucide-react'

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

export default function DmsIntegrationCard() {
  const { toast } = useToast()
  const [open, setOpen] = useState(false)
  const [base, setBase] = useState('http://localhost:8010')
  const [token, setToken] = useState('')
  const [loading, setLoading] = useState(false)
  const [tested, setTested] = useState<'idle' | 'ok' | 'fail'>('idle')
  const [status, setStatus] = useState<DmsStatus | null>(null)

  useEffect(() => {
    loadStatus()
  }, [])

  async function loadStatus() {
    try {
      const r = await fetch('/api/admin/dms/status')
      const data: DmsStatus = await r.json()
      setStatus(data)
      if (data.base) {
        setBase(data.base)
      }
    } catch (e) {
      console.error('Failed to load DMS status:', e)
    }
  }

  async function testConnection() {
    if (!base || !token) {
      toast({
        title: 'Validierung fehlgeschlagen',
        description: 'Bitte Base-URL und Token eingeben',
        variant: 'destructive',
      })
      return
    }

    setLoading(true)
    try {
      const r = await fetch('/api/admin/dms/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base, token }),
      })
      const j = await r.json()
      setTested(j.ok ? 'ok' : 'fail')
      
      toast({
        title: j.ok ? '✅ Verbindung OK' : '❌ Fehlgeschlagen',
        description: j.ok ? 'Mayan-API erreichbar.' : (j.error ?? 'Unbekannter Fehler'),
        variant: j.ok ? 'default' : 'destructive',
      })
    } catch (e) {
      setTested('fail')
      toast({
        title: 'Verbindungsfehler',
        description: e instanceof Error ? e.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  async function bootstrap() {
    if (!base || !token) {
      toast({
        title: 'Validierung fehlgeschlagen',
        description: 'Bitte Base-URL und Token eingeben',
        variant: 'destructive',
      })
      return
    }

    setLoading(true)
    try {
      const r = await fetch('/api/admin/dms/bootstrap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base, token }),
      })
      const j: BootstrapResult = await r.json()
      
      if (j.ok) {
        toast({
          title: '✅ Mayan-DMS integriert',
          description: `${j.document_types} DocTypes, ${j.metadata_types} Metadata, ${j.created} Bindings`,
        })
        setOpen(false)
        loadStatus()  // Reload status
      } else {
        toast({
          title: '❌ Bootstrap-Fehler',
          description: j.message ?? 'Bitte Logs prüfen',
          variant: 'destructive',
        })
      }
    } catch (e) {
      toast({
        title: 'Bootstrap-Fehler',
        description: e instanceof Error ? e.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6 space-y-4">
      <CardHeader className="p-0">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-xl">Mayan-DMS integrieren</CardTitle>
            <CardDescription>
              Zentrale Dokumentenablage mit OCR, Versionierung & Volltext. 
              Wird nahtlos mit VALEO NeuroERP verbunden.
            </CardDescription>
          </div>
          {status?.configured && (
            <Badge variant="default" className="bg-green-600">
              <CheckCircle2 className="h-3 w-3 mr-1" />
              Verbunden
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="p-0 space-y-4">
        {status?.configured ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Base-URL:</span>
              <code className="bg-gray-100 px-2 py-1 rounded text-xs">{status.base}</code>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Document Types:</span>
              <Badge variant="outline">{status.document_types}</Badge>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span>Metadata Types:</span>
              <Badge variant="outline">{status.metadata_types}</Badge>
            </div>
            <div className="flex gap-2 pt-2">
              <Button
                variant="outline"
                onClick={() => window.open(status.base, '_blank')}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Im DMS öffnen
              </Button>
              <Button
                variant="outline"
                onClick={() => setOpen(true)}
              >
                Neu konfigurieren
              </Button>
            </div>
          </div>
        ) : (
          <Dialog open={open} onOpenChange={setOpen}>
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
                    value={base}
                    onChange={(e) => setBase(e.target.value)}
                    placeholder="http://localhost:8010"
                    disabled={loading}
                  />
                  <p className="text-xs text-muted-foreground">
                    URL zu Ihrer Mayan-DMS-Instanz (inkl. http:// oder https://)
                  </p>
                </div>
                
                <div className="grid gap-2">
                  <Label htmlFor="token">API-Token</Label>
                  <Input
                    id="token"
                    type="password"
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                    placeholder="Token aus Mayan-Admin-Panel"
                    disabled={loading}
                  />
                  <p className="text-xs text-muted-foreground">
                    Erstellen Sie einen API-Token in Mayan unter: Einstellungen → API-Token
                  </p>
                </div>

                {tested !== 'idle' && (
                  <div className={`p-3 rounded-lg ${tested === 'ok' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                    <p className={`text-sm font-medium ${tested === 'ok' ? 'text-green-900' : 'text-red-900'}`}>
                      {tested === 'ok' ? '✅ Verbindung erfolgreich getestet' : '❌ Verbindung fehlgeschlagen'}
                    </p>
                  </div>
                )}
              </div>

              <DialogFooter className="gap-2">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={testConnection}
                  disabled={loading || !token || !base}
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Teste...
                    </>
                  ) : (
                    <>
                      Verbindung testen
                      {tested === 'ok' && ' ✅'}
                      {tested === 'fail' && ' ❌'}
                    </>
                  )}
                </Button>
                
                <Button
                  type="button"
                  onClick={bootstrap}
                  disabled={loading || !token || !base || tested !== 'ok'}
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

