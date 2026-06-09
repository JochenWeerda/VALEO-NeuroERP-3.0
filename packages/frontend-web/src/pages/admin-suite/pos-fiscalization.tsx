import { useEffect, useState } from 'react'
import { Link } from '@/app/routing/typed-router'
import { AlertTriangle, ArrowLeft, CheckCircle2, RefreshCw, Save, ShieldCheck } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Switch } from '@/components/ui/switch'
import { useToast } from '@/hooks/use-toast'
import {
  getFiscalConfig,
  getFiscalReadiness,
  saveFiscalConfig,
  type FiscalConfig,
  type FiscalProviderName,
  type FiscalReadiness,
} from '@/lib/services/fiskaly-tse'

const EMPTY_CONFIG: FiscalConfig = {
  configured: false,
  provider: 'fiskaly',
  dsfinvk_provider: 'fiskaly',
  cash_register_id: '',
  client_id: '',
  simulation_allowed: false,
  settings: { terminal_id: '' },
}

export default function PosFiscalizationAdminPage(): JSX.Element {
  const { toast } = useToast()
  const [config, setConfig] = useState<FiscalConfig>(EMPTY_CONFIG)
  const [readiness, setReadiness] = useState<FiscalReadiness | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const [nextConfig, nextReadiness] = await Promise.all([getFiscalConfig(), getFiscalReadiness()])
      setConfig({ ...EMPTY_CONFIG, ...nextConfig, settings: { ...EMPTY_CONFIG.settings, ...nextConfig.settings } })
      setReadiness(nextReadiness)
    } catch (error) {
      toast({
        title: 'Fiskalisierung konnte nicht geladen werden',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const save = async () => {
    if (!config.cash_register_id?.trim() || !config.client_id?.trim()) {
      toast({ title: 'Kassen-/TSS-ID und Client-ID sind erforderlich', variant: 'destructive' })
      return
    }
    setSaving(true)
    try {
      await saveFiscalConfig({
        provider: config.provider,
        dsfinvk_provider: config.dsfinvk_provider,
        cash_register_id: config.cash_register_id.trim(),
        client_id: config.client_id.trim(),
        simulation_allowed: config.simulation_allowed,
        settings: { terminal_id: config.settings?.terminal_id?.trim() || config.client_id.trim() },
      })
      await load()
      toast({ title: 'Fiskalisierungskonfiguration gespeichert' })
    } catch (error) {
      toast({
        title: 'Konfiguration konnte nicht gespeichert werden',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="container mx-auto space-y-6 py-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">POS-Fiskalisierung</h1>
          <p className="mt-2 text-muted-foreground">
            fiskaly oder Swissbit als TSE; DSFinV-K bleibt ein getrennt konfigurierter Vertrag.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => void load()} disabled={loading}>
            <RefreshCw className="mr-2 h-4 w-4" />Neu pruefen
          </Button>
          <Button asChild variant="outline"><Link to="/admin-suite"><ArrowLeft className="mr-2 h-4 w-4" />Zurueck</Link></Button>
        </div>
      </div>

      {readiness ? (
        <Alert variant={readiness.ready ? 'success' : 'warning'}>
          {readiness.ready ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
          <AlertTitle>{readiness.ready ? 'POS-Fiskalisierung bereit' : 'Betriebs-Gates offen'}</AlertTitle>
          <AlertDescription>
            {[...readiness.config_blockers, ...readiness.sign.blockers, ...readiness.dsfinvk.blockers].join(' · ')
              || 'Provider, Kassenkontext und DSFinV-K sind einsatzbereit.'}
          </AlertDescription>
        </Alert>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Mandantenkonfiguration</CardTitle>
          <CardDescription>Secrets werden ausschliesslich als Server-Umgebungsvariablen verwaltet.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="fiscal-provider">TSE-Provider</Label>
            <NativeSelect
              id="fiscal-provider"
              value={config.provider}
              disabled={loading || saving}
              onValueChange={(value) => setConfig((current) => ({ ...current, provider: value as FiscalProviderName }))}
              options={[
                { value: 'fiskaly', label: 'fiskaly SIGN DE' },
                { value: 'swissbit_cloud', label: 'Swissbit Cloud TSE' },
                { value: 'swissbit_gateway', label: 'Swissbit Hardware-Gateway' },
                { value: 'simulation', label: 'Explizite Simulation' },
              ]}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="dsfinvk-provider">DSFinV-K-Provider</Label>
            <NativeSelect
              id="dsfinvk-provider"
              value={config.dsfinvk_provider}
              disabled={loading || saving}
              onValueChange={(value) => setConfig((current) => ({ ...current, dsfinvk_provider: value as 'fiskaly' | 'simulation' }))}
              options={[
                { value: 'fiskaly', label: 'fiskaly DSFINVK DE' },
                { value: 'simulation', label: 'Explizite Simulation' },
              ]}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="cash-register-id">Kassen-/TSS-ID</Label>
            <Input id="cash-register-id" value={config.cash_register_id ?? ''} disabled={loading || saving} onChange={(event) => setConfig((current) => ({ ...current, cash_register_id: event.target.value }))} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="client-id">Client-ID</Label>
            <Input id="client-id" value={config.client_id ?? ''} disabled={loading || saving} onChange={(event) => setConfig((current) => ({ ...current, client_id: event.target.value }))} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="terminal-id">Terminal-ID</Label>
            <Input id="terminal-id" value={config.settings?.terminal_id ?? ''} disabled={loading || saving} onChange={(event) => setConfig((current) => ({ ...current, settings: { ...current.settings, terminal_id: event.target.value } }))} />
          </div>
          <div className="flex items-center justify-between rounded-md border p-3">
            <div>
              <Label htmlFor="simulation-allowed">Simulation freigeben</Label>
              <p className="text-xs text-muted-foreground">In Produktion serverseitig immer gesperrt.</p>
            </div>
            <Switch id="simulation-allowed" checked={config.simulation_allowed} disabled={loading || saving} onCheckedChange={(checked) => setConfig((current) => ({ ...current, simulation_allowed: checked }))} />
          </div>
          <div className="md:col-span-2">
            <Button onClick={() => void save()} disabled={loading || saving} data-testid="save-fiscal-config">
              <Save className="mr-2 h-4 w-4" />{saving ? 'Speichert...' : 'Konfiguration speichern'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        {readiness ? [
          { key: 'sign', label: 'TSE-Signatur', item: readiness.sign },
          { key: 'dsfinvk', label: 'DSFinV-K', item: readiness.dsfinvk },
        ].map(({ key, label, item }) => (
          <Card key={`${item.provider}-${key}`}>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <CardTitle>{label}</CardTitle>
                <Badge variant={item.ready ? 'default' : 'destructive'}>{item.ready ? 'Bereit' : 'Blockiert'}</Badge>
              </div>
              <CardDescription>{item.provider}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>Faehigkeiten: {item.capabilities.join(', ') || 'keine'}</p>
              {item.blockers.map((blocker) => <p key={blocker} className="text-destructive">- {blocker}</p>)}
            </CardContent>
          </Card>
        )) : null}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Optionale fiskaly-Produkte</CardTitle>
          <CardDescription>Produktvertrag und Credentials sind getrennte Go-Live-Gates; es gibt keinen stillen Fallback.</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          {readiness?.products.map((product) => (
            <div key={product.product} className="space-y-2 rounded-md border p-4" data-testid={`product-${product.product}`}>
              <div className="flex items-center justify-between gap-2">
                <h3 className="font-semibold">{product.label}</h3>
                <Badge variant={product.ready ? 'default' : 'outline'}>{product.ready ? 'Vertrag bereit' : 'Nicht freigegeben'}</Badge>
              </div>
              {product.blockers.map((blocker) => <p key={blocker} className="text-xs text-muted-foreground">- {blocker}</p>)}
              <p className="text-xs text-muted-foreground">{product.details.execution_note}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Alert variant="info">
        <ShieldCheck className="h-4 w-4" />
        <AlertTitle>Swissbit-Vertragsgrenze</AlertTitle>
        <AlertDescription>
          Cloud- und Hardwareadapter werden erst nach Freigabe der partnergeschuetzten Vertragsversion live. DSFinV-K wird separat ueber fiskaly angebunden.
        </AlertDescription>
      </Alert>
    </div>
  )
}
