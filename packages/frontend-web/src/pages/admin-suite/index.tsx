import { Link } from 'react-router-dom'
import {
  AlertTriangle,
  CheckCircle2,
  CircleHelp,
  Database,
  HardDrive,
  Network,
  RefreshCw,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Wrench,
} from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useAdminSuiteReadiness, type ReadinessEvidence, type ReadinessStatus } from '@/lib/api/admin-suite'

const CARD_LINKS: Record<string, string | null> = {
  setup: '/admin-suite/setup',
  migration: null,
  security: '/admin/rollen-verwaltung',
  connectors: '/admin/control-center/superglue',
  devices: null,
  compliance: '/admin/compliance',
  backup_restore: null,
  system_status: '/admin/control-center',
}

const CARD_ICONS = {
  setup: Settings,
  migration: Database,
  security: ShieldCheck,
  connectors: Network,
  devices: Wrench,
  compliance: SlidersHorizontal,
  backup_restore: HardDrive,
  system_status: RefreshCw,
} as const

function badgeVariant(status: ReadinessStatus): 'default' | 'destructive' | 'outline' | 'secondary' {
  if (status === 'blocked') return 'destructive'
  if (status === 'ready') return 'default'
  if (status === 'warning') return 'secondary'
  return 'outline'
}

function statusLabel(status: ReadinessStatus): string {
  if (status === 'ready') return 'Bereit'
  if (status === 'warning') return 'Warnung'
  if (status === 'blocked') return 'Blockiert'
  return 'Nicht geprueft'
}

function StatusIcon({ status }: { status: ReadinessStatus }): JSX.Element {
  if (status === 'ready') return <CheckCircle2 className="h-5 w-5 text-[hsl(var(--color-semantic-success-500-hsl))]" />
  if (status === 'blocked') return <AlertTriangle className="h-5 w-5 text-destructive" />
  return <CircleHelp className="h-5 w-5 text-muted-foreground" />
}

function EvidenceCard({ item }: { item: ReadinessEvidence }): JSX.Element {
  const Icon = CARD_ICONS[item.key as keyof typeof CARD_ICONS] ?? CircleHelp
  const link = CARD_LINKS[item.key]
  return (
    <Card>
      <CardHeader className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <Icon className="h-5 w-5 text-primary" />
          <Badge variant={badgeVariant(item.status)}>{statusLabel(item.status)}</Badge>
        </div>
        <div>
          <CardTitle className="text-base">{item.label}</CardTitle>
          <CardDescription className="mt-2">{item.evidence}</CardDescription>
        </div>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <p className="break-all text-xs text-muted-foreground">Quelle: {item.source}</p>
        {item.details.length > 0 ? (
          <ul className="space-y-1 text-xs text-muted-foreground">
            {item.details.map((detail) => <li key={detail}>- {detail}</li>)}
          </ul>
        ) : null}
        {link ? (
          <Button asChild size="sm" variant="outline">
            <Link to={link}>Bereich oeffnen</Link>
          </Button>
        ) : (
          <p className="text-xs text-muted-foreground">Cockpit folgt in einem spaeteren Slice.</p>
        )}
      </CardContent>
    </Card>
  )
}

export default function AdminSuiteHomePage(): JSX.Element {
  const readinessQuery = useAdminSuiteReadiness()

  if (readinessQuery.isLoading) return <LoadingState message="Admin Suite Readiness wird geladen..." />
  if (readinessQuery.isError || !readinessQuery.data) {
    return <ErrorState error={readinessQuery.error instanceof Error ? readinessQuery.error : null} onRetry={() => void readinessQuery.refetch()} />
  }

  const readiness = readinessQuery.data
  return (
    <div className="container mx-auto space-y-6 py-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">VALEO Admin Suite</h1>
        <p className="text-muted-foreground">
          Gefuehrte Produktionsvorbereitung mit nachvollziehbarer Evidenz. Nicht gepruefte Nachweise bleiben sichtbar offen.
        </p>
      </div>

      <Alert variant={readiness.status === 'blocked' ? 'destructive' : 'warning'}>
        <StatusIcon status={readiness.status} />
        <AlertTitle>Go-Live Readiness: {readiness.score}%</AlertTitle>
        <AlertDescription>
          Der Score zaehlt nur bewertete Evidenz. Externe Live-Probes und offene Abnahmen werden nicht als Erfolg gewertet.
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>Production Readiness</CardTitle>
          <CardDescription>Stand: {new Date(readiness.checked_at).toLocaleString('de-DE')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Progress value={readiness.score} aria-label={`Go-Live Readiness ${readiness.score}%`} />
          <div className="flex flex-wrap gap-2 text-sm">
            <Badge>Bereit: {readiness.ready_count}</Badge>
            <Badge variant="secondary">Warnungen: {readiness.warning_count}</Badge>
            <Badge variant="destructive">Blockiert: {readiness.blocked_count}</Badge>
            <Badge variant="outline">Nicht geprueft: {readiness.unchecked_count}</Badge>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {readiness.evidence.map((item) => <EvidenceCard key={item.key} item={item} />)}
      </div>
    </div>
  )
}
