import { Link } from '@/app/routing/react-router-compat'
import { ArrowLeft, ExternalLink, RefreshCw } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useAdminSuiteSystemStatus, type SystemStatusEvidence } from '@/lib/api/admin-suite'

function probeVariant(status: SystemStatusEvidence['probe_status']): 'default' | 'outline' | 'secondary' {
  return status === 'available' ? 'default' : status === 'partial' ? 'secondary' : 'outline'
}

export default function AdminSuiteSystemStatusPage(): JSX.Element {
  const query = useAdminSuiteSystemStatus()
  if (query.isLoading) return <LoadingState message="System Status Evidence Center wird geladen..." />
  if (query.isError || !query.data) return <ErrorState error={query.error instanceof Error ? query.error : null} onRetry={() => void query.refetch()} />

  return <div className="container mx-auto space-y-6 py-8">
    <div className="flex justify-between gap-3">
      <div>
        <h1 className="text-3xl font-bold">System Status Evidence Center</h1>
        <p className="mt-2 text-muted-foreground">Vorhandene Probe-Vertraege sind sichtbar. Dieser Bereich startet keine Live-Probes.</p>
      </div>
      <Button asChild variant="outline"><Link to="/admin-suite"><ArrowLeft className="mr-2 h-4 w-4" />Zurueck</Link></Button>
    </div>

    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {query.data.map((item) => <Card key={item.key}>
        <CardHeader>
          <RefreshCw className="h-5 w-5 text-primary" />
          <CardTitle className="text-base">{item.label}</CardTitle>
          <CardDescription>{item.notes}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          <div className="flex flex-wrap gap-2">
            <Badge variant={probeVariant(item.probe_status)}>Probe: {item.probe_status}</Badge>
            <Badge variant="outline">Runtime: {item.runtime_status}</Badge>
          </div>
          <p className="break-all text-muted-foreground">Quelle: {item.source}</p>
          {item.target_path ? <Button asChild size="sm" variant="outline"><Link to={item.target_path}>Bereich oeffnen<ExternalLink className="ml-2 h-3 w-3" /></Link></Button> : null}
        </CardContent>
      </Card>)}
    </div>
  </div>
}
