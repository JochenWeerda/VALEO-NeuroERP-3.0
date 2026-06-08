import { useEffect, useState } from 'react'
import { Link } from '@/app/routing/react-router-compat'
import { ArrowLeft, BrainCircuit, CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useToast } from '@/hooks/use-toast'
import {
  useLlmGateway,
  useUpdateLlmGateway,
  useTestLlmGateway,
  type LlmProvider,
  type LlmTestResult,
} from '@/lib/api/admin-suite'

const PROVIDER_LABEL: Record<LlmProvider, string> = {
  anthropic: 'Anthropic (Claude)',
  openai_compatible: 'OpenAI-kompatibel (OpenAI / OpenRouter / lokal: Hermes, LM Studio, Ollama /v1)',
  ollama: 'Ollama (lokaler Dienst)',
}

const PROVIDER_HINT: Record<LlmProvider, string> = {
  anthropic: 'Base-URL i. d. R. https://api.anthropic.com — API-Key erforderlich.',
  openai_compatible: 'Base-URL z. B. https://openrouter.ai/api/v1 oder http://localhost:1234/v1 — API-Key je nach Anbieter.',
  ollama: 'Base-URL z. B. http://localhost:11434 — kein API-Key nötig (lokal, DSGVO-konform).',
}

export default function AdminSuiteKiAnbieterPage(): JSX.Element {
  const query = useLlmGateway()
  const update = useUpdateLlmGateway()
  const test = useTestLlmGateway()
  const { toast } = useToast()

  const [provider, setProvider] = useState<LlmProvider>('anthropic')
  const [baseUrl, setBaseUrl] = useState('')
  const [model, setModel] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [temperature, setTemperature] = useState('0.2')
  const [enabled, setEnabled] = useState(true)
  const [testResult, setTestResult] = useState<LlmTestResult | null>(null)

  // Formular aus der gespeicherten Konfiguration initialisieren (Key wird nie geladen).
  useEffect(() => {
    if (query.data) {
      setProvider(query.data.provider)
      setBaseUrl(query.data.base_url)
      setModel(query.data.model)
      setTemperature(String(query.data.temperature))
      setEnabled(query.data.enabled)
    }
  }, [query.data])

  if (query.isLoading) return <LoadingState message="KI-Anbieter-Konfiguration wird geladen..." />
  if (query.isError || !query.data) {
    return <ErrorState error={query.error instanceof Error ? query.error : null} onRetry={() => void query.refetch()} />
  }

  const handleSave = async () => {
    try {
      await update.mutateAsync({
        provider,
        base_url: baseUrl,
        model,
        temperature: Number(temperature),
        enabled,
        ...(apiKey ? { api_key: apiKey } : {}),
      })
      setApiKey('')
      toast({ title: 'Gespeichert', description: 'KI-Anbieter-Konfiguration aktualisiert.' })
    } catch (err) {
      toast({ title: 'Fehler', description: err instanceof Error ? err.message : 'Speichern fehlgeschlagen', variant: 'destructive' })
    }
  }

  const handleTest = async () => {
    setTestResult(null)
    try {
      const res = await test.mutateAsync()
      setTestResult(res)
      toast({
        title: res.ok ? 'Verbindung OK' : 'Test fehlgeschlagen',
        description: res.detail,
        variant: res.ok ? 'default' : 'destructive',
      })
    } catch (err) {
      toast({ title: 'Fehler', description: err instanceof Error ? err.message : 'Test fehlgeschlagen', variant: 'destructive' })
    }
  }

  return (
    <div className="container mx-auto max-w-3xl space-y-6 py-8">
      <div className="flex justify-between gap-3">
        <div>
          <h1 className="flex items-center gap-2 text-3xl font-bold">
            <BrainCircuit className="h-7 w-7 text-emerald-700" /> KI-Anbieter (NeuroAI)
          </h1>
          <p className="mt-2 text-muted-foreground">
            Anbieterunabhängige LLM-Konfiguration für NeuroAI-Dossiers und Textassistenten.
            Wählbar: lokaler Dienst (DSGVO/kostenlos), günstiger Aggregator oder Cloud-Anbieter.
          </p>
        </div>
        <Button asChild variant="outline">
          <Link to="/admin-suite"><ArrowLeft className="mr-2 h-4 w-4" />Zurück</Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Aktueller Status
            {query.data.available
              ? <Badge className="bg-emerald-600"><CheckCircle2 className="mr-1 h-3 w-3" />Einsatzbereit</Badge>
              : <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" />Nicht konfiguriert</Badge>}
          </CardTitle>
          <CardDescription>
            API-Key hinterlegt: {query.data.api_key_set ? 'ja' : 'nein'} · Ohne erreichbaren Anbieter
            nutzt das System automatisch einen deterministischen Fallback.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="provider">Anbieter</Label>
            <NativeSelect id="provider" value={provider} onChange={(e) => setProvider(e.target.value as LlmProvider)}>
              {query.data.providers.map((p) => (
                <option key={p} value={p}>{PROVIDER_LABEL[p]}</option>
              ))}
            </NativeSelect>
            <p className="text-xs text-muted-foreground">{PROVIDER_HINT[provider]}</p>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="base_url">Base-URL</Label>
              <Input id="base_url" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} placeholder="(Standard des Anbieters)" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="model">Modell</Label>
              <Input id="model" value={model} onChange={(e) => setModel(e.target.value)} placeholder="(Standardmodell)" />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="api_key">API-Key {query.data.api_key_set && <span className="text-xs text-muted-foreground">(gesetzt — leer lassen zum Behalten)</span>}</Label>
              <Input id="api_key" type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} placeholder={query.data.api_key_set ? '••••••••' : 'API-Key eingeben'} autoComplete="off" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="temperature">Temperatur</Label>
              <Input id="temperature" type="number" step="0.1" min="0" max="2" value={temperature} onChange={(e) => setTemperature(e.target.value)} />
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} />
            KI aktiviert (deaktiviert = immer deterministischer Fallback)
          </label>

          {testResult && (
            <div className={`rounded-md border p-3 text-sm ${testResult.ok ? 'border-emerald-200 bg-emerald-50 text-emerald-900' : 'border-red-200 bg-red-50 text-red-900'}`}>
              <strong>{testResult.ok ? 'Verbindung OK' : 'Test fehlgeschlagen'}</strong> — {testResult.provider}/{testResult.model}: {testResult.detail}
            </div>
          )}

          <div className="flex gap-2">
            <Button onClick={handleSave} disabled={update.isPending}>
              {update.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Speichern
            </Button>
            <Button variant="outline" onClick={handleTest} disabled={test.isPending}>
              {test.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}Verbindung testen
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
