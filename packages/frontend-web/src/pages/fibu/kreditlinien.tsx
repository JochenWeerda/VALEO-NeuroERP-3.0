import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { AlertTriangle, CreditCard, Plus, Search, TrendingDown } from 'lucide-react'
import { useKreditlinien, type Kreditlinie } from '@/lib/api/fibu'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type FilterMode = 'alle' | 'ueberzogen' | 'bonitaet_cd'

export default function KreditlinienPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterMode, setFilterMode] = useState<FilterMode>('alle')
  const { data: items, isLoading } = useKreditlinien()

  if (isLoading) return (
    <div className="p-3 md:p-6 space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-[400px] w-full" />
    </div>
  )

  const list = items ?? []
  const filteredList = list.filter((k) => {
    const matchSearch = !searchTerm || k.kunde.toLowerCase().includes(searchTerm.toLowerCase()) || (k.kundennr ?? '').toLowerCase().includes(searchTerm.toLowerCase())
    if (!matchSearch) return false
    if (filterMode === 'ueberzogen') return k.status === 'ueberzogen'
    if (filterMode === 'bonitaet_cd') return k.bonitaet === 'C' || k.bonitaet === 'D'
    return true
  })

  const columns = [
    {
      key: 'kunde' as const,
      label: 'Kunde',
      render: (k: Kreditlinie) => (
        <div>
          <button onClick={() => navigate(`/verkauf/kunden-stamm/${k.id}`)} className="font-medium text-blue-600 hover:underline">
            {k.kunde}
          </button>
          <div className="text-xs text-muted-foreground font-mono">{k.kundennr}</div>
        </div>
      ),
    },
    {
      key: 'bonitaet' as const,
      label: 'Bonität',
      render: (k: Kreditlinie) => {
        const colors = { A: 'text-green-600', B: 'text-blue-600', C: 'text-orange-600', D: 'text-red-600' }
        return <span className={`text-2xl font-bold ${colors[k.bonitaet]}`}>{k.bonitaet}</span>
      },
    },
    {
      key: 'limit' as const,
      label: 'Kreditlimit',
      render: (k: Kreditlinie) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(k.limit),
    },
    {
      key: 'ausgenutzt' as const,
      label: 'Ausgenutzt',
      render: (k: Kreditlinie) => {
        const prozent = (k.ausgenutzt / k.limit) * 100
        return (
          <div className="space-y-1">
            <div className="font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(k.ausgenutzt)}</div>
            <div className="h-2 w-32 bg-gray-200 rounded-full overflow-hidden">
              <div className={`h-full ${prozent >= 100 ? 'bg-red-500' : prozent > 80 ? 'bg-orange-500' : 'bg-green-500'}`} style={{ width: `${Math.min(prozent, 100)}%` }} />
            </div>
            <div className="text-xs text-muted-foreground">{prozent.toFixed(0)}%</div>
          </div>
        )
      },
    },
    {
      key: 'verfuegbar' as const,
      label: 'Verfügbar',
      render: (k: Kreditlinie) => (
        <span className={k.verfuegbar < 10000 ? 'font-semibold text-red-600' : 'font-semibold text-green-600'}>
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(k.verfuegbar)}
        </span>
      ),
    },
    {
      key: 'ueberfaellig' as const,
      label: 'Überfällig',
      render: (k: Kreditlinie) =>
        k.ueberfaellig > 0 ? (
          <span className="font-semibold text-red-600">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(k.ueberfaellig)}</span>
        ) : (
          <span className="text-muted-foreground">–</span>
        ),
    },
    {
      key: 'zahlungsziel' as const,
      label: 'Zahlungsziel',
      render: (k: Kreditlinie) => `${k.zahlungsziel} Tage`,
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (k: Kreditlinie) => (
        <Badge variant={k.status === 'aktiv' ? 'outline' : k.status === 'gesperrt' ? 'destructive' : 'secondary'}>
          {k.status === 'aktiv' ? 'Aktiv' : k.status === 'gesperrt' ? 'Gesperrt' : 'Überzogen'}
        </Badge>
      ),
    },
  ]

  const ueberzogen = filteredList.filter((k) => k.status === 'ueberzogen').length
  const gesamtLimit = filteredList.reduce((sum, k) => sum + k.limit, 0)
  const gesamtAusgenutzt = filteredList.reduce((sum, k) => sum + k.ausgenutzt, 0)
  const gesamtVerfuegbar = filteredList.reduce((sum, k) => sum + k.verfuegbar, 0)
  const operationalStatus = normalizeOperationalStatus(
    ueberzogen > 0 ? 'eskaliert' : filteredList.some((k) => k.bonitaet === 'C' || k.bonitaet === 'D') ? 'wartet_auf_mensch' : 'in_pruefung'
  )
  const contextSections = [
    {
      title: 'Limitlage',
      items: [
        { label: 'Kreditlinien', value: String(filteredList.length) },
        { label: 'Ueberzogen', value: String(ueberzogen) },
        { label: 'Filter', value: filterMode },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        { label: 'Gesamtlimit', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtLimit) },
        { label: 'Ausgenutzt', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtAusgenutzt) },
        { label: 'Verfuegbar', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtVerfuegbar) },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: ueberzogen > 0 ? 'Ueberzogene Linien eskalieren' : 'Bonitaet und Limits pruefen' },
        { label: 'Blocker', value: ueberzogen > 0 ? 'Mindestens eine Kreditlinie ist ueberzogen.' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Kreditlinienraum geladen', detail: `${filteredList.length} Linie(n) im Fokus` },
    ueberzogen > 0 ? { label: 'Ueberziehung erkannt', detail: `${ueberzogen} Linie(n) ueberzogen` } : null,
    filteredList.some((k) => k.bonitaet === 'C' || k.bonitaet === 'D') ? { label: 'Bonitaetsrisiko aktiv', detail: 'Linien mit C/D-Bonitaet im Ausschnitt' } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  return (
    <div className="space-y-4 p-3 md:p-6">
      <OperationalCaseHeader
        title="Kreditlinien-Verwaltung"
        description="Risiko-, Limit- und Bonitaetsraum fuer Forderungsschutz und Freigabeentscheidungen."
        status={operationalStatus}
        owner="Kreditmanagement"
        blocker={ueberzogen > 0 ? 'Es liegen ueberzogene Kreditlinien vor.' : null}
        nextAction={ueberzogen > 0 ? 'Ueberzogene Linien sperren oder eskalieren' : 'Bonitaet und Limitauslastung pruefen'}
        caseLabel="Kreditlinien"
        tags={['FIBU', 'Risiko']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Kreditlinienverlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <CreditCard className="h-10 w-10 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Kreditlinien-Verwaltung</h1>
            <p className="text-muted-foreground">Bonitätsprüfung & Limit-Monitoring</p>
          </div>
        </div>
        <Button onClick={() => navigate('/fibu/kreditlinie-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Kreditlinie
        </Button>
      </div>

      {ueberzogen > 0 && (
        <Card className="border-red-500 bg-red-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-red-900">
              <TrendingDown className="h-5 w-5" />
              <span className="font-semibold">{ueberzogen} Kreditlinie(n) überzogen!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="rounded-lg bg-orange-50 p-4 text-sm text-orange-900">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4" />
          <p className="font-semibold">Automatische Kreditprüfung</p>
        </div>
        <p className="mt-1">
          Bonität: <strong>A</strong> = sehr gut (Limit bis 500k) • <strong>B</strong> = gut (bis 200k) • <strong>C</strong> = befriedigend (bis 50k) • <strong>D</strong> = mangelhaft (nur Vorkasse)
        </p>
        <p className="mt-1 text-xs">Automatische Sperrung bei Überschreitung oder überfälligen Rechnungen &gt; 30 Tage</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kreditlinien Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{filteredList.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Limit</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtLimit)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ausgenutzt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtAusgenutzt)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Verfügbar</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtVerfuegbar)}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Kunde..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant={filterMode === 'ueberzogen' ? 'default' : 'outline'} onClick={() => setFilterMode((m) => (m === 'ueberzogen' ? 'alle' : 'ueberzogen'))}>
              Nur Überzogene
            </Button>
            <Button variant={filterMode === 'bonitaet_cd' ? 'default' : 'outline'} onClick={() => setFilterMode((m) => (m === 'bonitaet_cd' ? 'alle' : 'bonitaet_cd'))}>
              Nur Bonität C/D
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredList} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
