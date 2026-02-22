import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { toast } from '@/hooks/use-toast'
import { useConnectorEventQuarantine, useResolveConnectorEvent, useRetryConnectorEvent } from '@/lib/api/admin'

export default function IntegrationenQuarantaenePage(): JSX.Element {
  const { data: items = [], isLoading } = useConnectorEventQuarantine({ limit: 200 })
  const retryMutation = useRetryConnectorEvent()
  const resolveMutation = useResolveConnectorEvent()

  const onRetry = async (id: string) => {
    try {
      await retryMutation.mutateAsync(id)
      toast({ title: 'Retry eingeplant' })
    } catch (error) {
      toast({ title: 'Retry fehlgeschlagen', description: String(error), variant: 'destructive' })
    }
  }

  const onResolve = async (id: string) => {
    try {
      await resolveMutation.mutateAsync(id)
      toast({ title: 'Event auf geloest gesetzt' })
    } catch (error) {
      toast({ title: 'Resolve fehlgeschlagen', description: String(error), variant: 'destructive' })
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Integrationen-Quarantaene</h1>
        <p className="text-muted-foreground">Fehlerqueue fuer Connector-Events mit Retry- und Resolve-Aktionen.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Fehlerevents ({items.length})</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {isLoading ? <div className="text-sm text-muted-foreground">Lade...</div> : null}
          {items.map((item) => (
            <div key={item.id} className="flex items-center justify-between rounded border p-3">
              <div>
                <div className="font-medium">{item.event_type}</div>
                <div className="text-xs text-muted-foreground">
                  connector={item.connector_id} · retries={item.retry_count} · {item.created_at}
                </div>
                {item.message ? <div className="text-xs text-red-600">{item.message}</div> : null}
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="destructive">{item.status}</Badge>
                <Button size="sm" variant="outline" onClick={() => onRetry(item.id)} disabled={retryMutation.isPending}>Retry</Button>
                <Button size="sm" onClick={() => onResolve(item.id)} disabled={resolveMutation.isPending}>Resolve</Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
