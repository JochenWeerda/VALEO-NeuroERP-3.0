import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { BookMarked, FileDown, Loader2, Plus, Search } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { exportToCSV } from '@/lib/export-utils'
import { useToast } from '@/hooks/use-toast'
import { ErrorState } from '@/components/ErrorState'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type Konto = {
  id: string
  kontonummer: string
  bezeichnung: string
  kontoart: string
  saldo: number
  typ: 'aktiv' | 'passiv' | 'aufwand' | 'ertrag'
}

function mapApiAccount(a: { id: string; account_number: string; name: string; category?: string }): Konto {
  const num = parseInt(a.account_number, 10)
  let typ: Konto['typ'] = 'aktiv'
  if (num >= 4000 && num < 7000) typ = 'aufwand'
  else if (num >= 8000) typ = 'ertrag'
  else if (num >= 1600 && num < 2000) typ = 'passiv'
  return {
    id: a.id,
    kontonummer: a.account_number,
    bezeichnung: a.name,
    kontoart: a.category || 'Sonstige',
    saldo: 0,
    typ,
  }
}

export default function KontenplanPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')

  const { data: konten = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ['fibu', 'chart-of-accounts'],
    queryFn: async () => {
      const res = await apiClient.get<{ items: Array<{ id: string; account_number: string; name: string; category?: string }> }>(
        '/api/v1/chart-of-accounts'
      )
      if (!res.data?.items) {
        throw new Error('Ungültige Antwort für Kontenplan')
      }
      return res.data.items.map(mapApiAccount)
    },
    staleTime: 2 * 60 * 1000,
  })

  const filteredKonten = useMemo(() => {
    if (!searchTerm.trim()) return konten
    const q = searchTerm.trim().toLowerCase()
    return konten.filter((k) => k.kontonummer.toLowerCase().includes(q) || k.bezeichnung.toLowerCase().includes(q))
  }, [konten, searchTerm])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = () => {
    try {
      exportToCSV(
        filteredKonten,
        `kontenplan-${new Date().toISOString().slice(0, 10)}.csv`,
        [
          { key: 'kontonummer', label: 'Konto' },
          { key: 'bezeichnung', label: 'Bezeichnung' },
          { key: 'kontoart', label: 'Kontoart' },
          { key: 'typ', label: 'Typ' },
          { key: 'saldo', label: 'Saldo' },
        ]
      )
      toast({ title: 'Export', description: `${filteredKonten.length} Konten exportiert.` })
    } catch (e) {
      toast({ title: 'Export fehlgeschlagen', description: String(e), variant: 'destructive' })
    }
  }

  const columns = [
    {
      key: 'kontonummer' as const,
      label: 'Konto',
      render: (k: Konto) => (
        <button onClick={() => navigate(`/fibu/sachkonto/${k.id}`)} className="font-medium text-blue-600 hover:underline font-mono text-lg">
          {k.kontonummer}
        </button>
      ),
    },
    { key: 'bezeichnung' as const, label: 'Bezeichnung', render: (k: Konto) => <span className="font-semibold">{k.bezeichnung}</span> },
    { key: 'kontoart' as const, label: 'Kontoart' },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (k: Konto) => (
        <Badge variant="outline">
          {k.typ === 'aktiv' ? 'Aktiva' : k.typ === 'passiv' ? 'Passiva' : k.typ === 'aufwand' ? 'Aufwand' : 'Ertrag'}
        </Badge>
      ),
    },
    {
      key: 'saldo' as const,
      label: 'Saldo',
      render: (k: Konto) => (
        <span className={`font-bold ${k.saldo < 0 ? 'text-red-600' : 'text-green-600'}`}>
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(Math.abs(k.saldo))}
          {k.saldo < 0 ? ' H' : ' S'}
        </span>
      ),
    },
  ]
  const ertragskonten = konten.filter((k) => k.typ === 'ertrag').length
  const aufwandskonten = konten.filter((k) => k.typ === 'aufwand').length
  const operationalStatus = normalizeOperationalStatus(filteredKonten.length > 0 ? 'in_pruefung' : 'offen')
  const contextSections = [
    {
      title: 'Kontenraum',
      items: [
        { label: 'Konten gesamt', value: String(konten.length) },
        { label: 'Gefiltert', value: String(filteredKonten.length) },
        { label: 'Suche', value: searchTerm || 'Keine Einschraenkung' },
      ],
    },
    {
      title: 'Struktur',
      items: [
        { label: 'Aktiva', value: String(konten.filter((k) => k.typ === 'aktiv').length) },
        { label: 'Aufwand', value: String(aufwandskonten) },
        { label: 'Ertrag', value: String(ertragskonten) },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: filteredKonten.length > 0 ? 'Konten pruefen oder exportieren' : 'Konto anlegen oder Suchraum erweitern' },
        { label: 'Blocker', value: 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Kontenplan geladen', detail: `${konten.length} Konten im aktuellen Stand` },
    filteredKonten.length !== konten.length ? { label: 'Filter aktiv', detail: `${filteredKonten.length} Konten im Fokus` } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  return (
    <div className="space-y-4 p-6">
      <OperationalCaseHeader
        title="Kontenplan"
        description="Steuerungsraum fuer Kontenstruktur, Nutzung und Folgepfade ins Sachkonto."
        status={operationalStatus}
        owner="Finanzbuchhaltung"
        blocker={null}
        nextAction={filteredKonten.length > 0 ? 'Konten pruefen oder exportieren' : 'Konto anlegen oder Filter anpassen'}
        caseLabel="SKR03"
        tags={['FIBU', 'Stammdaten']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Kontenverlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kontenplan</h1>
          <p className="text-muted-foreground">SKR03 Standardkontenrahmen</p>
        </div>
        <Button onClick={() => navigate('/fibu/sachkonto/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues Konto
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Konten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BookMarked className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{konten.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiva</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{konten.filter((k) => k.typ === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aufwand</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{konten.filter((k) => k.typ === 'aufwand').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ertrag</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{konten.filter((k) => k.typ === 'ertrag').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Kontonummer oder Bezeichnung..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-sm text-muted-foreground">Lade Kontenplan...</span>
            </div>
          ) : (
            <DataTable data={filteredKonten} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
