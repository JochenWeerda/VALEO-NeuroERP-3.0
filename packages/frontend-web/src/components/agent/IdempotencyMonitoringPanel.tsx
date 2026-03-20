import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import { History, Layers3, Repeat2, ShieldAlert, ShieldCheck, Workflow } from 'lucide-react'

export type IdempotencyOverview = {
  schema_version: number
  confidence_score: number
  catalog: {
    total_commands: number
    idempotent_commands: number
    human_confirmation_commands: number
    agent_ready_commands: number
    idempotent_coverage_pct: number
  }
  store: {
    total_records: number
    tenant_count: number
    execution_count: number
    command_count: number
    aggregate_count: number
    commands: string[]
    aggregates: string[]
  }
  recommended_action: string
  lookup_paths: string[]
}

export type IdempotencyMonitoringPanelProps = {
  overview: IdempotencyOverview
  className?: string
}

function metricTone(value: number): 'default' | 'secondary' | 'outline' {
  if (value >= 80) {
    return 'default'
  }
  if (value >= 60) {
    return 'secondary'
  }
  return 'outline'
}

export function IdempotencyMonitoringPanel({
  overview,
  className,
}: IdempotencyMonitoringPanelProps): JSX.Element {
  const { catalog, store, confidence_score } = overview
  return (
    <Card className={cn('border-slate-200', className)}>
      <CardHeader className="space-y-2">
        <CardTitle className="flex items-center gap-2 text-xl">
          <Repeat2 className="h-5 w-5 text-slate-700" />
          Idempotency Monitoring
        </CardTitle>
        <CardDescription>
          Rest-Nachweis fuer sichere Retries, Replay-Schutz und Command-Abdeckung aus dem Process Kernel.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-lg border bg-white p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Monitoring Confidence</p>
              <p className="text-3xl font-bold">{confidence_score}%</p>
            </div>
            <Badge variant={metricTone(confidence_score)}>
              <ShieldCheck className="mr-1 h-3.5 w-3.5" />
              {confidence_score >= 80 ? 'robust' : confidence_score >= 60 ? 'beobachten' : 'prüfen'}
            </Badge>
          </div>
          <Progress value={confidence_score} className="mt-3 h-2" />
        </div>

        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-lg border bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Workflow className="h-4 w-4" />
              Commands gesamt
            </div>
            <div className="mt-2 text-3xl font-bold">{catalog.total_commands}</div>
            <p className="mt-1 text-xs text-muted-foreground">{catalog.idempotent_coverage_pct}% idempotent</p>
          </div>

          <div className="rounded-lg border bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <ShieldAlert className="h-4 w-4" />
              Replay-sicher
            </div>
            <div className="mt-2 text-3xl font-bold">{catalog.idempotent_commands}</div>
            <p className="mt-1 text-xs text-muted-foreground">Commands mit `idempotent=true`</p>
          </div>

          <div className="rounded-lg border bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <History className="h-4 w-4" />
              Store Records
            </div>
            <div className="mt-2 text-3xl font-bold">{store.total_records}</div>
            <p className="mt-1 text-xs text-muted-foreground">{store.execution_count} Execution-IDs hinterlegt</p>
          </div>

          <div className="rounded-lg border bg-slate-50 p-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Layers3 className="h-4 w-4" />
              Tenants
            </div>
            <div className="mt-2 text-3xl font-bold">{store.tenant_count}</div>
            <p className="mt-1 text-xs text-muted-foreground">{store.aggregate_count} Aggregate-Typen beobachtet</p>
          </div>
        </div>

        <div className="space-y-2 rounded-lg border bg-white p-4">
          <div className="flex items-center gap-2 text-sm font-medium">
            <ShieldCheck className="h-4 w-4" />
            Kern-Nachweis
          </div>
          <p className="text-sm text-muted-foreground">{overview.recommended_action}</p>
          <div className="flex flex-wrap gap-2 pt-1">
            {overview.lookup_paths.map((path) => (
              <Badge key={path} variant="outline" className="font-mono text-[11px]">
                {path}
              </Badge>
            ))}
          </div>
          <div className="flex flex-wrap gap-2 pt-2">
            {store.commands.slice(0, 6).map((command) => (
              <Badge key={command} variant="secondary">
                {command}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
