import { useMemo } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, CalendarCheck, Clock, Route, ShieldCheck, Truck } from 'lucide-react'
import { useZeiterfassung, type ZeitEintrag } from '@/lib/api/personal'

type DriverTimeFindingSeverity = 'blocker' | 'warning' | 'info'

type DriverTimeFinding = {
  code: string
  severity: DriverTimeFindingSeverity
  message: string
}

type DriverTimePilotRow = {
  id: string
  fahrer: string
  tour: string
  fahrzeug: string
  start: string
  ende: string
  taetigkeit: string
  quelle: 'Manuell' | 'Tacho' | 'Telematik' | 'Dispo'
  dauer: number
  findings: DriverTimeFinding[]
}

const driverTimePilotRows: DriverTimePilotRow[] = [
  {
    id: 'dt-001',
    fahrer: 'M. Krueger',
    tour: 'TOUR-2407',
    fahrzeug: 'WL-VA 1840',
    start: '05:45',
    ende: '07:55',
    taetigkeit: 'Fahren',
    quelle: 'Tacho',
    dauer: 2.17,
    findings: [],
  },
  {
    id: 'dt-002',
    fahrer: 'M. Krueger',
    tour: 'TOUR-2407',
    fahrzeug: 'WL-VA 1840',
    start: '07:55',
    ende: '09:10',
    taetigkeit: 'Entladen',
    quelle: 'Manuell',
    dauer: 1.25,
    findings: [
      {
        code: 'TACHO_MANUAL_DEVIATION',
        severity: 'warning',
        message: 'Tacho-Abgleich offen',
      },
    ],
  },
  {
    id: 'dt-003',
    fahrer: 'S. Weber',
    tour: 'TOUR-2411',
    fahrzeug: 'fehlt',
    start: '06:20',
    ende: '08:00',
    taetigkeit: 'Fahren',
    quelle: 'Dispo',
    dauer: 1.67,
    findings: [
      {
        code: 'MISSING_VEHICLE',
        severity: 'blocker',
        message: 'Fahrzeug fehlt',
      },
    ],
  },
  {
    id: 'dt-004',
    fahrer: 'A. Brandt',
    tour: 'TOUR-2409',
    fahrzeug: 'WL-VA 1217',
    start: '08:00',
    ende: '08:45',
    taetigkeit: 'Pause',
    quelle: 'Manuell',
    dauer: 0.75,
    findings: [],
  },
]

const getFindingBadgeVariant = (severity: DriverTimeFindingSeverity): 'destructive' | 'secondary' | 'outline' => {
  if (severity === 'blocker') return 'destructive'
  if (severity === 'warning') return 'secondary'
  return 'outline'
}

export default function ZeiterfassungPage(): JSX.Element {
  const today = new Date().toISOString().split('T')[0]
  const { data: zeiten, isLoading } = useZeiterfassung(today)
  const list = useMemo(() => zeiten ?? [], [zeiten])
  const driverRows = useMemo(() => driverTimePilotRows, [])

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
  const driverBlocker = driverRows.reduce(
    (sum, row) => sum + row.findings.filter((finding) => finding.severity === 'blocker').length,
    0,
  )
  const driverWarnings = driverRows.reduce(
    (sum, row) => sum + row.findings.filter((finding) => finding.severity === 'warning').length,
    0,
  )
  const fahrzeitStunden = driverRows
    .filter((row) => row.taetigkeit === 'Fahren')
    .reduce((sum, row) => sum + row.dauer, 0)
  const driverColumns = [
    { key: 'fahrer' as const, label: 'Fahrer' },
    {
      key: 'tour' as const,
      label: 'Tour',
      render: (row: DriverTimePilotRow) => <span className="font-mono text-xs">{row.tour}</span>,
    },
    {
      key: 'fahrzeug' as const,
      label: 'Fahrzeug',
      render: (row: DriverTimePilotRow) => (
        <span className={row.fahrzeug === 'fehlt' ? 'font-semibold text-destructive' : 'font-mono text-xs'}>
          {row.fahrzeug}
        </span>
      ),
    },
    {
      key: 'start' as const,
      label: 'Zeit',
      render: (row: DriverTimePilotRow) => <span className="font-mono">{row.start} - {row.ende}</span>,
    },
    { key: 'taetigkeit' as const, label: 'Taetigkeit' },
    {
      key: 'quelle' as const,
      label: 'Quelle',
      render: (row: DriverTimePilotRow) => <Badge variant="outline">{row.quelle}</Badge>,
    },
    {
      key: 'dauer' as const,
      label: 'Dauer',
      render: (row: DriverTimePilotRow) => <span className="font-semibold">{row.dauer.toFixed(2)} h</span>,
    },
    {
      key: 'findings' as const,
      label: 'Check',
      render: (row: DriverTimePilotRow) => (
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

  if (isLoading) {
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
        <h1 className="text-3xl font-bold">Zeiterfassung</h1>
        <p className="text-muted-foreground">Arbeitszeit, Abwesenheiten und Fahrerzeit</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Mitarbeiter Anwesend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{list.filter((z) => z.typ === 'Arbeit').length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Stunden Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtStunden.toFixed(1)} h</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Urlaub</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{list.filter((z) => z.typ === 'Urlaub').length}</span>
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
              <span className="text-2xl font-bold">{new Set(driverRows.map((row) => row.tour)).size}</span>
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
              <span className="text-2xl font-bold">0</span>
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

      <Card>
        <CardHeader>
          <CardTitle>Driver-Time-Pilot</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable data={driverRows} columns={driverColumns} />
        </CardContent>
      </Card>

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
    </div>
  )
}
