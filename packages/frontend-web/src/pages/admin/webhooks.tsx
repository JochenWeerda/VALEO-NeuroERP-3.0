import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'
import { Plus, Search, Trash2, Webhook } from 'lucide-react'

/**
 * Die Antwort des Backends. Bis zum 01.10.2026 erwartete diese Maske `name`,
 * `events[]`, `aktiv` und `last_triggered` — Felder, die der Endpunkt nie
 * geliefert hat. Sichtbar wurde das nie, weil die Liste immer leer war: Die
 * Tabelle, aus der gelesen wurde, legte keine Migration an, und ein Lesefehler
 * kam als `[]` zurueck. Beim ersten echten Webhook waere `w.name.toLowerCase()`
 * in der Suche gelaufen.
 */
type WebhookItem = {
  id: string
  nr: number
  url: string
  bereich: string
  is_active: boolean
  erstellt_am: string | null
  letzte_auslosung_am: string | null
  fehler_count: number
  signiert: boolean
}

type Zustellversuch = {
  versucht_am: string | null
  erfolgreich: boolean
  status_code: number | null
  dauer_ms: number | null
  fehler: string | null
}

function zeitpunkt(wert: string | null): string {
  return wert ? new Date(wert).toLocaleString('de-DE') : '–'
}

function fehlertext(fehler: unknown): string {
  const detail = (fehler as { response?: { data?: { detail?: string } } })?.response?.data?.detail
  return detail ?? (fehler as Error).message
}

export default function WebhooksPage(): JSX.Element {
  const [search, setSearch] = useState('')
  const [anlegenOffen, setAnlegenOffen] = useState(false)
  const [url, setUrl] = useState('')
  const [bereich, setBereich] = useState('')
  const [secret, setSecret] = useState('')
  const [protokollVon, setProtokollVon] = useState<WebhookItem | null>(null)
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const { data: webhooks = [], isError, error, refetch } = useQuery<WebhookItem[]>({
    queryKey: ['webhooks'],
    queryFn: async () => (await apiClient.get<WebhookItem[]>('/api/v1/webhooks')).data,
  })

  const { data: bereiche = [] } = useQuery<string[]>({
    queryKey: ['webhook-bereiche'],
    queryFn: async () => (await apiClient.get<string[]>('/api/v1/webhooks/bereiche')).data,
  })

  const { data: versuche = [] } = useQuery<Zustellversuch[]>({
    queryKey: ['webhook-zustellversuche', protokollVon?.id],
    enabled: protokollVon !== null,
    queryFn: async () =>
      (
        await apiClient.get<Zustellversuch[]>(
          `/api/v1/webhooks/${protokollVon?.id}/zustellversuche`,
        )
      ).data,
  })

  const anlegen = useMutation({
    mutationFn: async () => {
      await apiClient.post(`/api/v1/webhooks/bereiche/${bereich}`, {
        url,
        bereich,
        secret: secret || undefined,
      })
    },
    onSuccess: async () => {
      toast({ title: 'Webhook registriert', description: url })
      setAnlegenOffen(false)
      setUrl('')
      setSecret('')
      await queryClient.invalidateQueries({ queryKey: ['webhooks'] })
    },
    onError: (fehler: unknown) => {
      toast({
        title: 'Registrierung fehlgeschlagen',
        description: fehlertext(fehler),
        variant: 'destructive',
      })
    },
  })

  const abmelden = useMutation({
    mutationFn: async (eintrag: WebhookItem) => {
      await apiClient.delete(`/api/v1/webhooks/abmelden/${eintrag.nr}`)
    },
    onSuccess: async () => {
      toast({ title: 'Webhook abgemeldet' })
      await queryClient.invalidateQueries({ queryKey: ['webhooks'] })
    },
    onError: (fehler: unknown) => {
      toast({
        title: 'Abmeldung fehlgeschlagen',
        description: fehlertext(fehler),
        variant: 'destructive',
      })
    },
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = webhooks.filter(
    (w) =>
      w.url.toLowerCase().includes(search.toLowerCase()) ||
      w.bereich.toLowerCase().includes(search.toLowerCase()),
  )

  const columns = [
    {
      key: 'nr' as const,
      label: 'Nr.',
      render: (w: WebhookItem) => <span className="font-medium">{w.nr}</span>,
    },
    {
      key: 'bereich' as const,
      label: 'Ereignis',
      render: (w: WebhookItem) => <span className="text-sm">{w.bereich}</span>,
    },
    {
      key: 'url' as const,
      label: 'Ziel-URL',
      render: (w: WebhookItem) => <span className="font-mono text-xs">{w.url}</span>,
    },
    {
      key: 'signiert' as const,
      label: 'Signiert',
      render: (w: WebhookItem) => (
        <Badge variant={w.signiert ? 'success' : 'warning'}>{w.signiert ? 'Ja' : 'Nein'}</Badge>
      ),
    },
    {
      key: 'is_active' as const,
      label: 'Aktiv',
      render: (w: WebhookItem) => (
        <Badge variant={w.is_active ? 'success' : 'secondary'}>{w.is_active ? 'Ja' : 'Nein'}</Badge>
      ),
    },
    {
      key: 'letzte_auslosung_am' as const,
      label: 'Letzter Versuch',
      render: (w: WebhookItem) => (
        <button
          type="button"
          className="text-sm underline underline-offset-2"
          onClick={() => setProtokollVon(w)}
        >
          {zeitpunkt(w.letzte_auslosung_am)}
        </button>
      ),
    },
    {
      key: 'fehler_count' as const,
      label: 'Fehlschläge',
      render: (w: WebhookItem) => (
        <span className={w.fehler_count > 0 ? 'text-status-error' : 'text-muted-foreground'}>
          {w.fehler_count}
        </span>
      ),
    },
    {
      key: 'id' as const,
      label: '',
      render: (w: WebhookItem) => (
        <Button
          variant="ghost"
          size="sm"
          className="gap-2"
          disabled={abmelden.isPending}
          onClick={() => abmelden.mutate(w)}
        >
          <Trash2 className="h-4 w-4" />
          Abmelden
        </Button>
      ),
    },
  ]

  const ohneSignatur = webhooks.filter((w) => !w.signiert).length

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Webhook-Verwaltung</h1>
            <p className="text-muted-foreground">
              Ausgehende Webhooks für externe Systeme konfigurieren
            </p>
          </div>
          <Button className="gap-2" onClick={() => setAnlegenOffen(true)}>
            <Plus className="h-4 w-4" />
            Neuer Webhook
          </Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Webhook className="h-4 w-4" />
                Gesamt
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">{webhooks.length}</span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Aktiv</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-status-success">
                {webhooks.filter((w) => w.is_active).length}
              </span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Ohne Signatur</CardTitle>
            </CardHeader>
            <CardContent>
              <span
                className={
                  ohneSignatur > 0
                    ? 'text-2xl font-bold text-status-warning'
                    : 'text-2xl font-bold text-muted-foreground'
                }
              >
                {ohneSignatur}
              </span>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Webhooks ({filtered.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Ziel-URL oder Ereignis suchen..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>

      <Dialog open={anlegenOffen} onOpenChange={setAnlegenOffen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Neuer Webhook</DialogTitle>
            <DialogDescription>
              Die Ziel-URL muss mit https:// beginnen und darf nicht in das eigene Netz zeigen.
              Mit Geheimnis wird jeder Aufruf signiert.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1">
              <Label htmlFor="webhook-bereich">Ereignis</Label>
              <NativeSelect
                id="webhook-bereich"
                value={bereich}
                onChange={(e) => setBereich(e.target.value)}
              >
                <option value="">Bitte wählen…</option>
                {bereiche.map((b) => (
                  <option key={b} value={b}>
                    {b}
                  </option>
                ))}
              </NativeSelect>
            </div>
            <div className="space-y-1">
              <Label htmlFor="webhook-url">Ziel-URL</Label>
              <Input
                id="webhook-url"
                placeholder="https://partner.example/hook"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="webhook-secret">Geheimnis (optional)</Label>
              <Input
                id="webhook-secret"
                type="password"
                value={secret}
                onChange={(e) => setSecret(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setAnlegenOffen(false)}
              disabled={anlegen.isPending}
            >
              Abbrechen
            </Button>
            <Button disabled={anlegen.isPending || !url || !bereich} onClick={() => anlegen.mutate()}>
              {anlegen.isPending ? 'Wird registriert…' : 'Registrieren'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={protokollVon !== null}
        onOpenChange={(offen) => {
          if (!offen) setProtokollVon(null)
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Zustellversuche</DialogTitle>
            <DialogDescription>
              {protokollVon ? `${protokollVon.bereich} → ${protokollVon.url}` : ''}
            </DialogDescription>
          </DialogHeader>
          {versuche.length === 0 ? (
            <p className="text-sm text-muted-foreground">Noch kein Zustellversuch protokolliert.</p>
          ) : (
            <ul className="space-y-2">
              {versuche.map((v, i) => (
                <li
                  key={`${v.versucht_am ?? 'ohne'}-${i}`}
                  className="flex items-center justify-between gap-4 text-sm"
                >
                  <span className="font-mono text-xs">{zeitpunkt(v.versucht_am)}</span>
                  <Badge variant={v.erfolgreich ? 'success' : 'destructive'}>
                    {v.erfolgreich ? 'zugestellt' : (v.fehler ?? 'fehlgeschlagen')}
                  </Badge>
                  <span className="text-muted-foreground">{v.dauer_ms ?? '–'} ms</span>
                </li>
              ))}
            </ul>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
