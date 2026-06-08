import { Link } from '@/app/routing/typed-router'
import { ArrowLeft, ExternalLink, ShieldCheck } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useAdminSuiteCompliance, type ComplianceEvidence } from '@/lib/api/admin-suite'

function implementationVariant(status: ComplianceEvidence['implementation_status']): 'default' | 'outline' | 'secondary' {
  return status === 'available' ? 'default' : status === 'partial' ? 'secondary' : 'outline'
}

function gateLabel(gate: ComplianceEvidence['external_gate']): string {
  if (gate === 'required') return 'Externe Freigabe erforderlich'
  if (gate === 'not_required') return 'Keine externe Freigabe'
  return 'Externe Freigabe ungeprueft'
}

export default function AdminSuiteCompliancePage(): JSX.Element {
  const query = useAdminSuiteCompliance()
  if (query.isLoading) return <LoadingState message="Compliance Evidence Center wird geladen..." />
  if (query.isError || !query.data) return <ErrorState error={query.error instanceof Error ? query.error : null} onRetry={() => void query.refetch()} />

  return <div className="container mx-auto space-y-6 py-8">
    <div className="flex justify-between gap-3">
      <div>
        <h1 className="text-3xl font-bold">Compliance Evidence Center</h1>
        <p className="mt-2 text-muted-foreground">Implementierter Vertrag, produktiver Laufzeitnachweis und externe Freigabe bleiben getrennt sichtbar.</p>
      </div>
      <Button asChild variant="outline"><Link to="/admin-suite"><ArrowLeft className="mr-2 h-4 w-4" />Zurueck</Link></Button>
    </div>

    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {query.data.map((item) => <Card key={item.key}>
        <CardHeader>
          <ShieldCheck className="h-5 w-5 text-primary" />
          <CardTitle className="text-base">{item.label}</CardTitle>
          <CardDescription>{item.notes}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          <div className="flex flex-wrap gap-2">
            <Badge variant={implementationVariant(item.implementation_status)}>Implementierung: {item.implementation_status}</Badge>
            <Badge variant="outline">Runtime: {item.runtime_status}</Badge>
            <Badge variant="outline">{gateLabel(item.external_gate)}</Badge>
          </div>
          <p className="break-all text-muted-foreground">Quelle: {item.source}</p>
          {item.target_path ? <Button asChild size="sm" variant="outline"><Link to={item.target_path}>Fachbereich oeffnen<ExternalLink className="ml-2 h-3 w-3" /></Link></Button> : null}
        </CardContent>
      </Card>)}
    </div>
  </div>
}
