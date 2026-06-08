import { Link } from '@/app/routing/typed-router'
import { ArrowLeft, CheckCircle2, CircleHelp, ExternalLink } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useAdminSuiteSetup, useUpdateAdminSuiteSetupStep, type SetupStepStatus } from '@/lib/api/admin-suite'

function statusLabel(status: SetupStepStatus): string {
  if (status === 'completed') return 'Abgeschlossen'
  if (status === 'in_progress') return 'In Arbeit'
  if (status === 'warning') return 'Warnung'
  if (status === 'blocked') return 'Blockiert'
  return 'Nicht begonnen'
}

function statusVariant(status: SetupStepStatus): 'default' | 'destructive' | 'outline' | 'secondary' {
  if (status === 'completed') return 'default'
  if (status === 'blocked') return 'destructive'
  if (status === 'unchecked') return 'outline'
  return 'secondary'
}

export default function AdminSuiteSetupPage(): JSX.Element {
  const setupQuery = useAdminSuiteSetup()
  const updateStep = useUpdateAdminSuiteSetupStep()

  if (setupQuery.isLoading) return <LoadingState message="Setup-Fortschritt wird geladen..." />
  if (setupQuery.isError || !setupQuery.data) {
    return <ErrorState error={setupQuery.error instanceof Error ? setupQuery.error : null} onRetry={() => void setupQuery.refetch()} />
  }

  const setup = setupQuery.data
  const score = Math.round((100 * setup.completed_count) / setup.total_count)
  return (
    <div className="container mx-auto space-y-6 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">Ersteinrichtungs-Assistent</h1>
          <p className="mt-2 text-muted-foreground">Tenant {setup.tenant_id}: Schritte explizit pruefen und dokumentiert abschliessen.</p>
        </div>
        <Button asChild variant="outline"><Link to="/admin-suite"><ArrowLeft className="mr-2 h-4 w-4" />Zur Admin Suite</Link></Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Fortschritt: {setup.completed_count} / {setup.total_count}</CardTitle>
          <CardDescription>Das Oeffnen einer Fachmaske schliesst keinen Schritt automatisch ab.</CardDescription>
        </CardHeader>
        <CardContent><Progress value={score} aria-label={`Setup-Fortschritt ${score}%`} /></CardContent>
      </Card>
      <div className="grid gap-4 lg:grid-cols-2">
        {setup.steps.map((step) => (
          <Card key={step.key}>
            <CardHeader>
              <div className="flex items-center justify-between gap-3">
                <CardTitle className="text-base">{step.label}</CardTitle>
                <Badge variant={statusVariant(step.status)}>{statusLabel(step.status)}</Badge>
              </div>
              <CardDescription>{step.evidence ?? 'Noch keine Evidenz hinterlegt.'}</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              {step.target_path ? (
                <Button asChild size="sm" variant="outline"><Link to={step.target_path}>Fachmaske <ExternalLink className="ml-2 h-4 w-4" /></Link></Button>
              ) : null}
              <Button size="sm" variant="outline" disabled={updateStep.isPending} onClick={() => updateStep.mutate({ key: step.key, status: 'in_progress' })}>
                <CircleHelp className="mr-2 h-4 w-4" />In Arbeit
              </Button>
              <Button size="sm" disabled={updateStep.isPending} onClick={() => updateStep.mutate({ key: step.key, status: 'completed' })}>
                <CheckCircle2 className="mr-2 h-4 w-4" />Abschliessen
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
