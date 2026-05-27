import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, Search, Webhook } from 'lucide-react'

type WebhookItem = {
  id: string
  name: string
  url: string
  events: string[]
  aktiv: boolean
  last_triggered: string | null
}

export default function WebhooksPage(): JSX.Element {
  const [search, setSearch] = useState('')

  const { data: webhooks = [], isError, error, refetch } = useQuery<WebhookItem[]>({
    queryKey: ['webhooks'],
    queryFn: async () => (await apiClient.get<WebhookItem[]>('/api/v1/webhooks')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const filtered = webhooks.filter(
    (w) =>
      w.name.toLowerCase().includes(search.toLowerCase()) ||
      w.url.toLowerCase().includes(search.toLowerCase()),
  )

  const columns = [
    { key: 'name' as const, label: 'Name', render: (w: WebhookItem) => <span className="font-medium">{w.name}</span> },
    { key: 'url' as const, label: 'URL', render: (w: WebhookItem) => <span className="font-mono text-xs">{w.url}</span> },
    { key: 'events' as const, label: 'Events', render: (w: WebhookItem) => <span className="text-sm">{w.events.join(', ')}</span> },
    { key: 'aktiv' as const, label: 'Aktiv', render: (w: WebhookItem) => <Badge variant={w.aktiv ? 'success' : 'secondary'}>{w.aktiv ? 'Ja' : 'Nein'}</Badge> },
    { key: 'last_triggered' as const, label: 'Letzter Aufruf', render: (w: WebhookItem) => w.last_triggered ? new Date(w.last_triggered).toLocaleString('de-DE') : '–' },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Webhook-Verwaltung</h1>
            <p className="text-muted-foreground">Ausgehende Webhooks für externe Systeme konfigurieren</p>
          </div>
          <Button className="gap-2"><Plus className="h-4 w-4" />Neuer Webhook</Button>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Webhook className="h-4 w-4" />Gesamt</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{webhooks.length}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Aktiv</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-[hsl(var(--color-semantic-success-700-hsl))]">{webhooks.filter((w) => w.aktiv).length}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Inaktiv</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-muted-foreground">{webhooks.filter((w) => !w.aktiv).length}</span></CardContent></Card>
        </div>

        <Card>
          <CardHeader><CardTitle>Webhooks ({filtered.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="mb-4 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Name oder URL suchen..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
            </div>
            <DataTable data={filtered} columns={columns} />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
