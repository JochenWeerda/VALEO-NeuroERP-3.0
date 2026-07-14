import { Link } from '@/app/routing/typed-router'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import {
  ArrowLeft,
  ArrowRight,
  ExternalLink,
  FileText,
  ShieldCheck,
  Truck,
  FileSearch,
  AlertTriangle,
  Loader2,
  PlayCircle,
  Clock3,
  CheckCircle2,
} from 'lucide-react'
import { summarizeMeldewesenFeedback } from '@/lib/domain-depth'
import { getJobArtifacts, listConnectors, listJobs, listReportingUnits, listSchedules } from '@/lib/api/meldewesen'
import { useDokumenteAblage, useWiegungen } from '@/lib/api/betrieb'
import { useWarteschlange } from '@/lib/api/inventory'
import { useFrachtbriefe } from '@/lib/api/misc-modules'
import { normalizeOperationalStatus } from '@/lib/operational-status'

function formatDateTime(value?: string | null): string {
  if (!value) return 'n/a'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('de-DE')
}

export default function AtlasPage(): JSX.Element {
  const connectorsQuery = useQuery({
    queryKey: ['meldewesen', 'connectors', 'atlas'],
    queryFn: listConnectors,
    staleTime: 60_000,
  })
  const unitsQuery = useQuery({
    queryKey: ['meldewesen', 'units', 'atlas'],
    queryFn: listReportingUnits,
    staleTime: 60_000,
  })
  const schedulesQuery = useQuery({
    queryKey: ['meldewesen', 'schedules', 'atlas'],
    queryFn: listSchedules,
    staleTime: 60_000,
  })
  const jobsQuery = useQuery({
    queryKey: ['meldewesen', 'jobs', 'atlas'],
    queryFn: async () => listJobs({ limit: 8 }),
    staleTime: 30_000,
  })
  const { data: dokumente = [] } = useDokumenteAblage()
  const { data: wiegungen = [] } = useWiegungen()
  const { data: warteschlange } = useWarteschlange()
  const { data: frachtbriefe = [] } = useFrachtbriefe()

  const connectors = connectorsQuery.data ?? []
  const reportingUnits = unitsQuery.data ?? []
  const schedules = schedulesQuery.data ?? []
  const jobs = jobsQuery.data ?? []

  const atlasConnectors = connectors.filter((item) => {
    const haystack = `${item.connector_key} ${item.display_name ?? ''} ${JSON.stringify(item.config_json ?? {})}`.toLowerCase()
    return haystack.includes('atlas') || haystack.includes('zoll') || haystack.includes('intrastat') || haystack.includes('eudr')
  })

  const activeSchedules = schedules.filter((item) => item.is_active)
  const failedJobs = jobs.filter((item) => item.status === 'failed')
  const runningJobs = jobs.filter((item) => item.status === 'running' || item.status === 'queued')
  const successfulJobs = jobs.filter((item) => item.status === 'success')
  const latestJob = jobs[0]
  const latestArtifactsQuery = useQuery({
    queryKey: ['meldewesen', 'job-artifacts', latestJob?.id],
    queryFn: () => {
      if (!latestJob?.id) {
        return Promise.resolve([])
      }
      return getJobArtifacts(latestJob.id)
    },
    enabled: Boolean(latestJob?.id),
    staleTime: 30_000,
  })
  const latestArtifacts = latestArtifactsQuery.data ?? []
  const isLoading = connectorsQuery.isLoading || unitsQuery.isLoading || schedulesQuery.isLoading || jobsQuery.isLoading
  const feedbackSummary = summarizeMeldewesenFeedback({
    failedJobs: failedJobs.length,
    runningJobs: runningJobs.length,
    artifactCount: latestArtifacts.length,
    queueCount: warteschlange?.items?.length ?? 0,
    weighingCount: wiegungen.length,
    freightCount: frachtbriefe.length,
    documentCount: dokumente.length,
  })
  const operationalStatus = normalizeOperationalStatus(
    feedbackSummary.feedbackRisk === 'hoch'
      ? 'eskaliert'
      : runningJobs.length > 0
        ? 'in_pruefung'
        : atlasConnectors.length > 0
          ? 'offen'
          : 'wartet_auf_extern',
  )
  const contextSections = [
    {
      title: 'Meldeobjekt',
      items: [
        { label: 'Connectoren', value: `${atlasConnectors.length}` },
        { label: 'Reporting Units', value: `${reportingUnits.length}` },
        { label: 'Aktive Zeitplaene', value: `${activeSchedules.length}` },
      ],
    },
    {
      title: 'Rueckmeldung',
      items: [
        { label: 'Artefakte letzter Lauf', value: `${latestArtifacts.length}` },
        { label: 'Fehlerjobs', value: `${failedJobs.length}` },
        { label: 'Naechste Aktion', value: feedbackSummary.nextAction },
      ],
    },
    {
      title: 'Objektkette',
      items: [
        { label: 'Rohware-Faelle', value: `${warteschlange?.items?.length ?? 0}` },
        { label: 'Wiegungen', value: `${wiegungen.length}` },
        { label: 'Fracht / Dokumente', value: `${frachtbriefe.length} / ${dokumente.length}` },
      ],
    },
  ]
  const timelineItems = [
    {
      label: latestJob ? 'Letzter Meldejob vorhanden' : 'Noch kein Meldejob',
      detail: latestJob ? `${latestJob.job_type} mit Status ${latestJob.status}` : 'Der Rueckmeldepfad startet erst mit dem ersten Joblauf.',
      timestamp: latestJob?.triggered_at ?? latestJob?.created_at ?? null,
    },
    {
      label: latestArtifacts.length > 0 ? 'Artefakte rueckgekoppelt' : 'Artefaktpfad offen',
      detail: latestArtifacts.length > 0
        ? `${latestArtifacts.length} Artefakte sind dem letzten Lauf zugeordnet.`
        : 'Fuer den letzten sichtbaren Lauf liegen noch keine Artefakte vor.',
    },
    {
      label: failedJobs.length > 0 ? 'Rueckmeldefehler offen' : 'Keine offenen Rueckmeldefehler',
      detail: failedJobs.length > 0
        ? `${failedJobs.length} Jobs muessen fachlich nachverfolgt werden.`
        : 'Der sichtbare Rueckmeldepfad ist aktuell ohne Fehler.',
    },
  ]

  const workstreams = [
    {
      title: 'Meldewesen-Konsole',
      description: 'Connectoren, Reporting Units, Zeitplaene und Job-Laeufe fuer Zoll- und Exportmeldungen.',
      path: '/compliance/meldewesen-konsole',
      cta: 'Konsole oeffnen',
      icon: FileSearch,
      metric: `${atlasConnectors.length} relevante Connectoren`,
    },
    {
      title: 'Schnittstellen-Center',
      description: 'Mandantenprofile, Exportpfade und angrenzende FIBU-Connectoren fuer Ausfuhr- und Zollfaelle.',
      path: '/fibu/schnittstellen-center',
      cta: 'Connectoren oeffnen',
      icon: Truck,
      metric: `${reportingUnits.length} Reporting Units`,
    },
    {
      title: 'ELSTER / Steuerexporte',
      description: 'Steuer- und Exportdaten vorbereiten, wenn ein Ausfuhrvorgang finanzseitige Folgemeldungen ausloest.',
      path: '/fibu/elster-online',
      cta: 'Steuerpfade oeffnen',
      icon: FileText,
      metric: `${successfulJobs.length} erfolgreiche Jobs`,
    },
  ]

  const nextSteps = [
    `${atlasConnectors.length > 0 ? 'Atlas-/Zoll-Connectoren prüfen' : 'Zoll-Connector im Meldewesen anlegen oder aktivieren'}.`,
    `${activeSchedules.length > 0 ? 'Aktive Zeitplaene und Fuehrungstage verifizieren' : 'Zeitplan fuer den Mandanten aufsetzen und Fuehrungstage festlegen'}.`,
    `${failedJobs.length > 0 ? 'Fehlgeschlagene Laeufe analysieren und erneut einplanen' : 'Letzten Job-Lauf und Artefaktpfad kontrollieren'}.`,
    'Rueckmeldungen, Behoerdenstatus und externe Portalaktivitaeten im Leitstand dokumentieren.',
  ]

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-semibold">ATLAS (Zoll)</h1>
            <Badge variant="outline" className="border-emerald-200 bg-emerald-50 text-emerald-700">
              Operations Console
            </Badge>
          </div>
          <p className="max-w-3xl text-sm text-muted-foreground">
            Operative Leitseite fuer Zoll- und Exportvorgaenge. Sie verdichtet Connector-Lage, Meldeeinheiten,
            Zeitplaene und letzte Job-Laeufe in ein Arbeitsbild fuer Disposition, FIBU und Compliance.
          </p>
        </div>
        <Link to="/fibu/schnittstellen-center">
          <Button variant="outline" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Zurueck zum Schnittstellen-Center
          </Button>
        </Link>
      </div>

      <OperationalCaseHeader
        title="Zoll- und Meldepfad steuern"
        description="Rueckmeldungen, Artefakte und die physische Objektkette werden in einem kompakten Nachweisfall verdichtet."
        status={operationalStatus}
        owner="Compliance / Export"
        blocker={feedbackSummary.feedbackRisk === 'hoch' ? 'Fehlgeschlagene Jobs oder fehlende Artefakte blockieren den revisionssicheren Nachweis.' : null}
        nextAction={feedbackSummary.nextAction}
        caseLabel="Melde- und Bescheidpfad"
        tags={['Compliance', 'Nachweis']}
      />

      <div className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <OperationalTimeline title="Rueckmeldungsverlauf" items={timelineItems} />
        <OperationalContextPanel title="Nachweiskontext" sections={contextSections} />
      </div>

      <Alert className="border-amber-200 bg-amber-50 text-amber-900">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>Kein isoliertes Zoll-Subprodukt</AlertTitle>
        <AlertDescription>
          VALEO buendelt hier den Betriebs- und Kontrollkontext. Die eigentliche Uebermittlung bleibt ueber vorhandene
          Connectoren, Schedules und externe Fachportale organisiert.
        </AlertDescription>
      </Alert>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-xs uppercase tracking-wide text-muted-foreground">Relevante Connectoren</div>
            <div className="mt-2 text-2xl font-semibold">{atlasConnectors.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-xs uppercase tracking-wide text-muted-foreground">Aktive Zeitplaene</div>
            <div className="mt-2 text-2xl font-semibold">{activeSchedules.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-xs uppercase tracking-wide text-muted-foreground">Fehlgeschlagene Jobs</div>
            <div className="mt-2 text-2xl font-semibold">{failedJobs.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-xs uppercase tracking-wide text-muted-foreground">Letzte Aktivitaet</div>
            <div className="mt-2 text-sm font-semibold">{formatDateTime(latestJob?.created_at ?? latestJob?.triggered_at)}</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {workstreams.map((item) => {
          const Icon = item.icon
          return (
            <Card key={item.title} className="flex h-full flex-col">
              <CardHeader className="space-y-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="rounded-lg border bg-muted/40 p-2">
                    <Icon className="h-5 w-5" />
                  </span>
                  <Badge variant="secondary">{item.metric}</Badge>
                </div>
                <div>
                  <CardTitle className="text-base">{item.title}</CardTitle>
                  <CardDescription className="mt-1 text-sm">{item.description}</CardDescription>
                </div>
              </CardHeader>
              <CardContent className="mt-auto">
                <Link to={item.path}>
                  <Button variant="outline" className="w-full justify-between">
                    {item.cta}
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <ShieldCheck className="h-5 w-5 text-status-success" />
              Operativer Ablauf
            </CardTitle>
            <CardDescription>Naechste Schritte fuer einen Zoll- oder Exportfall auf Basis des aktuellen Systemzustands.</CardDescription>
          </CardHeader>
          <CardContent>
            <ol className="space-y-3 text-sm text-muted-foreground">
              {nextSteps.map((step, index) => (
                <li key={step} className="flex gap-3">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                    {index + 1}
                  </span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Systemlage</CardTitle>
            <CardDescription>Verdichteter Betriebsstatus aus Meldewesen und Job-Steuerung.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            {isLoading ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Lade Betriebsdaten...</span>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between rounded-lg border px-3 py-2">
                  <span className="text-muted-foreground">Connector-Lage</span>
                  <Badge variant={atlasConnectors.length > 0 ? 'default' : 'secondary'}>
                    {atlasConnectors.length > 0 ? 'arbeitsfaehig' : 'vorbereiten'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between rounded-lg border px-3 py-2">
                  <span className="text-muted-foreground">Job-Lage</span>
                  <Badge variant={failedJobs.length === 0 ? 'outline' : 'destructive'}>
                    {failedJobs.length === 0 ? 'stabil' : `${failedJobs.length} Fehler`}
                  </Badge>
                </div>
                <div className="flex items-center justify-between rounded-lg border px-3 py-2">
                  <span className="text-muted-foreground">Wartende / laufende Jobs</span>
                  <span className="font-medium">{runningJobs.length}</span>
                </div>
                <div className="flex items-center justify-between rounded-lg border px-3 py-2">
                  <span className="text-muted-foreground">Reporting Units</span>
                  <span className="font-medium">{reportingUnits.length}</span>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Relevante Connectoren</CardTitle>
            <CardDescription>Zoll-, Intrastat- und angrenzende Meldestecker fuer den aktuellen Betriebsrahmen.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {atlasConnectors.length > 0 ? atlasConnectors.slice(0, 5).map((connector) => (
              <div key={connector.id} className="rounded-lg border p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-medium">{connector.display_name ?? connector.connector_key}</div>
                    <div className="text-xs text-muted-foreground">{connector.connector_type}</div>
                  </div>
                  <Badge variant={connector.is_active ? 'default' : 'secondary'}>
                    {connector.is_active ? 'aktiv' : 'inaktiv'}
                  </Badge>
                </div>
              </div>
            )) : (
              <p className="text-sm text-muted-foreground">Noch keine explizit als Zoll-/ATLAS-relevant erkannten Connectoren vorhanden.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Letzte Job-Laeufe</CardTitle>
            <CardDescription>Aktuelle Rueckmeldungen aus der Job-Steuerung fuer Export- und Meldepfade.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {jobs.length > 0 ? jobs.slice(0, 5).map((job) => (
              <div key={job.id} className="rounded-lg border p-3">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-medium">{job.job_type}</div>
                    <div className="text-xs text-muted-foreground">{formatDateTime(job.triggered_at ?? job.created_at)}</div>
                  </div>
                  <Badge variant={job.status === 'failed' ? 'destructive' : job.status === 'success' ? 'outline' : 'secondary'}>
                    {job.status}
                  </Badge>
                </div>
                {job.error_message ? <p className="mt-2 text-xs text-amber-700">{job.error_message}</p> : null}
              </div>
            )) : (
              <p className="text-sm text-muted-foreground">Noch keine Job-Laeufe vorhanden.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Rückmeldungen und Artefakte</CardTitle>
            <CardDescription>Letzter Meldejob, Bescheidpfad und exportierte Artefakte direkt am Vorgang.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="rounded-lg border p-3 text-sm">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="font-medium">{latestJob?.job_type ?? 'Noch kein Lauf'}</div>
                  <div className="text-xs text-muted-foreground">{formatDateTime(latestJob?.triggered_at ?? latestJob?.created_at)}</div>
                </div>
                <Badge variant={latestJob?.status === 'failed' ? 'destructive' : latestJob?.status === 'success' ? 'outline' : 'secondary'}>
                  {latestJob?.status ?? 'n/a'}
                </Badge>
              </div>
              {latestJob?.error_message ? <p className="mt-2 text-xs text-amber-700">{latestJob.error_message}</p> : null}
            </div>
            {latestArtifacts.length > 0 ? latestArtifacts.map((artifact) => (
              <div key={artifact.id} className="rounded-lg border p-3 text-sm">
                <div className="font-medium">{artifact.artifact_key}</div>
                <div className="text-xs text-muted-foreground">{artifact.content_type} · {artifact.checksum_sha256?.slice(0, 12) ?? 'ohne checksum'}</div>
              </div>
            )) : (
              <p className="text-sm text-muted-foreground">Für den letzten Lauf liegen noch keine repo-seitig sichtbaren Artefakte vor.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Objektbezug im Vorgang</CardTitle>
            <CardDescription>Verzahnung mit Rohware, Waage, Fracht und Dokumenten.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-center justify-between rounded-lg border px-3 py-2">
              <span className="text-muted-foreground">Wartende Rohware-Fälle</span>
              <span className="font-medium">{warteschlange?.items?.length ?? 0}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border px-3 py-2">
              <span className="text-muted-foreground">Wiegungen</span>
              <span className="font-medium">{wiegungen.length}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border px-3 py-2">
              <span className="text-muted-foreground">Frachtbriefe</span>
              <span className="font-medium">{frachtbriefe.length}</span>
            </div>
            <div className="flex items-center justify-between rounded-lg border px-3 py-2">
              <span className="text-muted-foreground">Dokumente / Bescheide</span>
              <span className="font-medium">{dokumente.length}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_1fr_0.8fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Meldeeinheiten</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            {reportingUnits.length > 0 ? reportingUnits.slice(0, 4).map((unit) => (
              <div key={unit.id} className="flex items-center justify-between rounded-lg border px-3 py-2">
                <span>{unit.display_name}</span>
                <Badge variant={unit.is_active ? 'outline' : 'secondary'}>{unit.is_active ? 'aktiv' : 'inaktiv'}</Badge>
              </div>
            )) : <p>Keine Reporting Units vorhanden.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Zeitplaene</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            {schedules.length > 0 ? schedules.slice(0, 4).map((schedule) => (
              <div key={schedule.id} className="flex items-center justify-between rounded-lg border px-3 py-2">
                <div>
                  <div className="font-medium text-foreground">{schedule.display_name}</div>
                  <div className="text-xs">{schedule.cron_expr ?? 'kein Cron gesetzt'}</div>
                </div>
                <Badge variant={schedule.is_active ? 'outline' : 'secondary'}>{schedule.is_active ? 'aktiv' : 'inaktiv'}</Badge>
              </div>
            )) : <p>Keine Zeitplaene vorhanden.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Direktaktionen</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link to="/compliance/meldewesen-konsole">
              <Button variant="outline" className="w-full justify-between">
                <span className="flex items-center gap-2">
                  <PlayCircle className="h-4 w-4" />
                  Jobs / Konsole
                </span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link to="/admin/control-center">
              <Button variant="outline" className="w-full justify-between">
                <span className="flex items-center gap-2">
                  <Clock3 className="h-4 w-4" />
                  Leitstand
                </span>
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <a
              href="https://www.zoll-portal.de/"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="outline" className="w-full justify-between">
                <span className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4" />
                  Externes Portal
                </span>
                <ExternalLink className="h-4 w-4" />
              </Button>
            </a>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
