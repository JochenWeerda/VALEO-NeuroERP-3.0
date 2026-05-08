import { useMemo } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, CalendarCheck, CheckCircle2, Clock, FileDown, Route, ShieldCheck, Truck, Users } from 'lucide-react'
import { useTimeCockpit, useZeiterfassung, type DriverTimeEvent, type DriverTimeFindingSeverity, type TimeCockpit, type ZeitEintrag } from '@/lib/api/personal'

const getFindingBadgeVariant = (severity: DriverTimeFindingSeverity): 'destructive' | 'secondary' | 'outline' => {
  if (severity === 'blocker') return 'destructive'
  if (severity === 'warning') return 'secondary'
  return 'outline'
}

export default function ZeiterfassungPage(): JSX.Element {
  const today = new Date().toISOString().split('T')[0]
  const { data: zeiten, isLoading } = useZeiterfassung(today)
  const { data: cockpit, isLoading: isCockpitLoading } = useTimeCockpit(today)
  const list = useMemo(() => zeiten ?? [], [zeiten])
  const driverTime = cockpit.driverTime
  const driverRows = useMemo(() => driverTime.events, [driverTime.events])

  const columns = [
    { key: 'mitarbeiter' as const, label: 'Mitarbeiter' },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (z: ZeitEintrag) => new Date(z.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kommen' as const,
      label: 'Kommen',
      render: (z: ZeitEintrag) => <span className="font-mono">{z.kommen}</span>,
    },
    {
      key: 'gehen' as const,
      label: 'Gehen',
      render: (z: ZeitEintrag) => <span className="font-mono">{z.gehen}</span>,
    },
    {
      key: 'stunden' as const,
      label: 'Stunden',
      render: (z: ZeitEintrag) => <span className="font-semibold">{z.stunden} h</span>,
    },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (z: ZeitEintrag) => (
        <Badge variant={z.typ === 'Ueberstunden' ? 'destructive' : z.typ === 'Urlaub' ? 'secondary' : 'outline'}>
          {z.typ}
        </Badge>
      ),
    },
  ]

  const gesamtStunden = list.reduce((sum, z) => sum + z.stunden, 0)
  const driverBlocker = driverTime.kpis.blocker
  const driverWarnings = driverTime.kpis.warnings
  const fahrzeitStunden = driverTime.kpis.fahrzeitStunden
  const complianceColumns = [
    { key: 'severity' as const, label: 'Schwere', render: (row: TimeCockpit['complianceIssues'][number]) => (
      <Badge variant={getFindingBadgeVariant(row.severity)}>{row.severity}</Badge>
    ) },
    { key: 'employeeRef' as const, label: 'Mitarbeiter' },
    { key: 'datum' as const, label: 'Datum' },
    { key: 'code' as const, label: 'Code', render: (row: TimeCockpit['complianceIssues'][number]) => (
      <span className="font-mono text-xs">{row.code}</span>
    ) },
    { key: 'message' as const, label: 'Befund' },
  ]
  const approvalColumns = [
    { key: 'employeeRef' as const, label: 'Mitarbeiter' },
    { key: 'datum' as const, label: 'Datum' },
    { key: 'hours' as const, label: 'Stunden', render: (row: TimeCockpit['approvalQueue'][number]) => (
      <span className="font-semibold">{row.hours.toFixed(2)} h</span>
    ) },
    { key: 'entryType' as const, label: 'Typ' },
    { key: 'risk' as const, label: 'Risiko', render: (row: TimeCockpit['approvalQueue'][number]) => (
      <Badge variant={row.risk === 'blockiert' ? 'destructive' : 'secondary'}>{row.risk}</Badge>
    ) },
    { key: 'nextAction' as const, label: 'Naechste Aktion' },
  ]
  const driverColumns = [
    { key: 'fahrer' as const, label: 'Fahrer' },
    {
      key: 'tour' as const,
      label: 'Tour',
      render: (row: DriverTimeEvent) => <span className="font-mono text-xs">{row.tour ?? '-'}</span>,
    },
    {
      key: 'fahrzeug' as const,
      label: 'Fahrzeug',
      render: (row: DriverTimeEvent) => (
        <span className={!row.fahrzeug ? 'font-semibold text-destructive' : 'font-mono text-xs'}>
          {row.fahrzeug ?? 'fehlt'}
        </span>
      ),
    },
    {
      key: 'start' as const,
      label: 'Zeit',
      render: (row: DriverTimeEvent) => <span className="font-mono">{row.start} - {row.ende}</span>,
    },
    { key: 'taetigkeit' as const, label: 'Taetigkeit' },
    {
      key: 'quelle' as const,
      label: 'Quelle',
      render: (row: DriverTimeEvent) => <Badge variant="outline">{row.quelle}</Badge>,
    },
    {
      key: 'dauer' as const,
      label: 'Dauer',
      render: (row: DriverTimeEvent) => <span className="font-semibold">{row.dauer.toFixed(2)} h</span>,
    },
    {
      key: 'findings' as const,
      label: 'Check',
      render: (row: DriverTimeEvent) => (
        <div className="flex flex-wrap gap-1">
          {row.findings.length === 0 ? (
            <Badge variant="outline">ok</Badge>
          ) : row.findings.map((finding) => (
            <Badge key={`${row.id}-${finding.code}`} variant={getFindingBadgeVariant(finding.severity)}>
              {finding.message}
            </Badge>
          ))}
        </div>
      ),
    },
  ]

  if (isLoading || isCockpitLoading) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold">Zeiterfassung</h1>
            <p className="text-muted-foreground">Time & Labor, Abwesenheiten, Fahrerzeit und Payroll-Freigabe</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm">
              <Clock className="mr-2 h-4 w-4" />
              Heute
            </Button>
            <Button variant="outline" size="sm">
              <FileDown className="mr-2 h-4 w-4" />
              Payroll vorbereiten
            </Button>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Mitarbeiter Anwesend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{cockpit.kpis.presentEmployees}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Stunden Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{cockpit.kpis.totalHours.toFixed(1)} h</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Urlaub</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{cockpit.kpis.absentEmployees}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fahrerzeit Blocker</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-destructive" />
              <span className="text-2xl font-bold">{driverBlocker}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Freigaben offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-sky-700" />
              <span className="text-2xl font-bold">{cockpit.kpis.pendingApprovals}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Payroll Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle2 className={cockpit.payrollReadiness.status === 'ready' ? 'h-5 w-5 text-emerald-700' : 'h-5 w-5 text-amber-700'} />
              <span className="text-2xl font-bold">{cockpit.payrollReadiness.status === 'ready' ? 'bereit' : 'blockiert'}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Payroll bereit</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{cockpit.kpis.payrollReadyEntries}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Payroll blockiert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{cockpit.kpis.payrollBlockedEntries}</span>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fahrzeit Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-emerald-700" />
              <span className="text-2xl font-bold">{fahrzeitStunden.toFixed(2)} h</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Touren</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
            <Route className="h-5 w-5 text-cyan-700" />
              <span className="text-2xl font-bold">{driverTime.kpis.tourCount}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abwesenheitskollisionen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CalendarCheck className="h-5 w-5 text-amber-700" />
              <span className="text-2xl font-bold">
                {driverTime.findings.filter((finding) => finding.code === 'ABSENCE_COLLISION').length}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Tacho-Abgleich</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-indigo-700" />
              <span className="text-2xl font-bold">{driverWarnings}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="steuerung" className="space-y-4">
        <TabsList>
          <TabsTrigger value="steuerung">Steuerung</TabsTrigger>
          <TabsTrigger value="driver">Fahrerzeit</TabsTrigger>
          <TabsTrigger value="zeiten">Arbeitszeit</TabsTrigger>
          <TabsTrigger value="payroll">Payroll</TabsTrigger>
        </TabsList>

        <TabsContent value="steuerung" className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Freigabequeue</CardTitle>
              </CardHeader>
              <CardContent>
                <DataTable data={cockpit.approvalQueue} columns={approvalColumns} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Compliance-Befunde</CardTitle>
              </CardHeader>
              <CardContent>
                <DataTable data={cockpit.complianceIssues} columns={complianceColumns} />
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="driver">
          <Card>
            <CardHeader>
              <CardTitle>Driver-Time</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable data={driverRows} columns={driverColumns} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="zeiten">
          <Card>
            <CardHeader>
              <CardTitle>Klassische Arbeitszeit</CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <DataTable data={list} columns={columns} />
              <div className="mt-6 flex justify-between border-t pt-4 font-bold">
                <span>Gesamt-Stunden Heute:</span>
                <span>{gesamtStunden.toFixed(1)} h</span>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="payroll">
          <Card>
            <CardHeader>
              <CardTitle>Payroll-Readiness</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <p className="text-xl font-semibold">{cockpit.payrollReadiness.status}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Bereite Eintraege</p>
                  <p className="text-xl font-semibold">{cockpit.payrollReadiness.readyEntries}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Blockierte Eintraege</p>
                  <p className="text-xl font-semibold">{cockpit.payrollReadiness.blockedEntries}</p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">{cockpit.payrollReadiness.exportHint}</p>
              <div className="space-y-2">
                {cockpit.payrollReadiness.blockers.map((blocker, index) => (
                  <Badge key={`${blocker}-${index}`} variant="destructive">{blocker}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
