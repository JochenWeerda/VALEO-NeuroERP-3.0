import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { BackButton } from '@/components/BackButton'
import { AlertCircle, Euro, FileDown, Search } from 'lucide-react'
import { useKreditorenOP, type KreditOP } from '@/lib/api/fibu'
import { ErrorState } from '@/components/ErrorState'
import { normalizeOperationalStatus } from '@/lib/operational-status'

export default function KreditorenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: items, isLoading, isError, error, refetch } = useKreditorenOP()

  const list = useMemo(() => {
    const source = items ?? []
    const needle = searchTerm.trim().toLowerCase()
    if (!needle) return source
    return source.filter((op) =>
      [op.rechnungsnr, op.lieferant, op.lieferantennr]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(needle)),
    )
  }, [items, searchTerm])

  if (isLoading) return (
    <div className="p-3 md:p-6 space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-[400px] w-full" />
    </div>
  )

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const columns = [
    {
      key: 'rechnungsnr' as const,
      label: 'Rechnung',
      render: (op: KreditOP) => <span className="font-mono font-bold">{op.rechnungsnr}</span>,
    },
    { key: 'lieferant' as const, label: 'Lieferant' },
    { key: 'lieferantennr' as const, label: 'Lief-Nr', render: (op: KreditOP) => <span className="font-mono text-sm">{op.lieferantennr}</span> },
    { key: 'datum' as const, label: 'Re-Datum', render: (op: KreditOP) => new Date(op.datum).toLocaleDateString('de-DE') },
    {
      key: 'faelligkeit' as const,
      label: 'Faelligkeit',
      render: (op: KreditOP) => new Date(op.faelligkeit).toLocaleDateString('de-DE'),
    },
    {
      key: 'offen' as const,
      label: 'Offen',
      render: (op: KreditOP) => (
        <span className="font-bold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(op.offen)}
        </span>
      ),
    },
    {
      key: 'skonto' as const,
      label: 'Skonto',
      render: (op: KreditOP) => {
        const bis = new Date(op.skontoBis)
        const verfuegbar = bis >= new Date()
        return verfuegbar ? (
          <div>
            <span className="font-semibold text-green-600">{op.skonto}%</span>
            <div className="text-xs text-muted-foreground">bis {bis.toLocaleDateString('de-DE')}</div>
          </div>
        ) : (
          <span className="text-muted-foreground">-</span>
        )
      },
    },
    {
      key: 'zahlbar' as const,
      label: 'Status',
      render: (op: KreditOP) => (
        <Badge variant={op.zahlbar ? 'outline' : 'secondary'}>
          {op.zahlbar ? 'Zahlbar' : 'Geprueft'}
        </Badge>
      ),
    },
  ]

  const gesamtOffen = list.reduce((sum, op) => sum + op.offen, 0)
  const zahlbar = list.filter((op) => op.zahlbar).length
  const skontoVerfuegbar = list.filter((op) => new Date(op.skontoBis) >= new Date()).length
  const overdueCount = list.filter((op) => new Date(op.faelligkeit) < new Date() && op.offen > 0).length
  const operationalStatus = normalizeOperationalStatus(
    overdueCount > 0 ? 'eskaliert' : zahlbar > 0 ? 'wartet_auf_mensch' : list.length > 0 ? 'in_pruefung' : 'offen',
  )
  const contextSections = [
    {
      title: 'Kreditorenlage',
      items: [
        { label: 'Offene Posten', value: `${list.length}` },
        { label: 'Zahlbar', value: `${zahlbar}` },
        { label: 'Ueberfaellig', value: `${overdueCount}` },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        { label: 'Gesamt offen', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtOffen) },
        { label: 'Skonto verfuegbar', value: `${skontoVerfuegbar}` },
        { label: 'Naechste Aktion', value: overdueCount > 0 ? 'Ueberfaellige Positionen priorisieren' : 'Zahlungslauf vorbereiten' },
      ],
    },
  ]
  const timelineItems = [
    {
      label: overdueCount > 0 ? 'Ueberfaelligkeiten aktiv' : 'Keine akute Ueberfaelligkeit',
      detail: overdueCount > 0
        ? `${overdueCount} Positionen benoetigen priorisierte Freigabe oder Klaerung.`
        : 'Die aktuelle Sicht zeigt keine akuten Faelligkeitsverletzungen.',
    },
    {
      label: skontoVerfuegbar > 0 ? 'Skonto-Fenster nutzbar' : 'Kein aktives Skonto-Fenster',
      detail: skontoVerfuegbar > 0
        ? `${skontoVerfuegbar} Positionen koennen mit Skonto in den Lauf.`
        : 'Skontoeffekte sind im aktuellen Fenster nicht verfuegbar.',
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kreditorenbuchhaltung</h1>
          <p className="text-muted-foreground">Offene Posten Lieferanten</p>
        </div>
        <BackButton to="/fibu/op-verwaltung" label="Zurueck zur OP-Verwaltung" />
      </div>

      <OperationalCaseHeader
        title="Kreditorenbuchhaltung"
        description="Offene Kreditoren werden als operativer Follow-up-Fall mit Faelligkeits- und Exportdruck gefuehrt."
        status={operationalStatus}
        owner="Kreditorenbuchhaltung"
        blocker={overdueCount > 0 ? `${overdueCount} ueberfaellige Positionen warten auf Entscheidung.` : null}
        nextAction={overdueCount > 0 ? 'Ueberfaellige Positionen priorisieren und Zahlungslauf planen' : 'Zahlungslauf oder DATEV-Buchungsuebergabe starten'}
        caseLabel="Vorgang: Kreditoren-OP"
        tags={['FIBU', 'L3-kompatibel']}
      />
      <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
        <OperationalTimeline title="Kreditorenverlauf" items={timelineItems} />
        <OperationalContextPanel title="Kreditoren-Kontext" sections={contextSections} />
      </div>

      {skontoVerfuegbar > 0 && (
        <Card className="border-green-500 bg-green-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-green-900">
              <AlertCircle className="h-5 w-5" />
              <span className="font-semibold">{skontoVerfuegbar} Rechnung(en) mit Skonto-Option!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Posten</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{list.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold text-blue-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtOffen)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Zahlbar</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{zahlbar}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Skonto verfuegbar</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{skontoVerfuegbar}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Aktionen</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button onClick={() => navigate('/fibu/zahlungslaeufe')}>Zahlungslauf</Button>
            <Button variant="outline" className="gap-2" onClick={() => navigate('/fibu/schnittstelle-fibu?context=kreditoren')}>
              <FileDown className="h-4 w-4" />
              DATEV Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={list} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
