import { Link } from '@/app/routing/typed-router'
import { ArrowLeft, Network } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useAdminSuiteConnectors } from '@/lib/api/admin-suite'

export default function AdminSuiteConnectorsPage(): JSX.Element {
  const query = useAdminSuiteConnectors()
  if (query.isLoading) return <LoadingState message="Connector Hub wird geladen..." />
  if (query.isError || !query.data) return <ErrorState error={query.error instanceof Error ? query.error : null} onRetry={() => void query.refetch()} />
  return <div className="container mx-auto space-y-6 py-8">
    <div className="flex justify-between gap-3"><div><h1 className="text-3xl font-bold">Connector Hub</h1><p className="mt-2 text-muted-foreground">Credential-Metadaten ohne Secret-Werte. Live-Probes bleiben getrennt.</p></div><Button asChild variant="outline"><Link to="/admin-suite"><ArrowLeft className="mr-2 h-4 w-4" />Zurueck</Link></Button></div>
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{query.data.map((item) => <Card key={item.key}><CardHeader><Network className="h-5 w-5 text-primary" /><CardTitle className="text-base">{item.label}</CardTitle><CardDescription>{item.notes}</CardDescription></CardHeader><CardContent className="space-y-2 text-xs"><div className="flex gap-2"><Badge variant="outline">Config: {item.config_status}</Badge><Badge variant="outline">Live: {item.live_status}</Badge></div><p className="text-muted-foreground">Credentials: {item.credential_status}</p><p className="break-all text-muted-foreground">Quelle: {item.source}</p></CardContent></Card>)}</div>
  </div>
}
