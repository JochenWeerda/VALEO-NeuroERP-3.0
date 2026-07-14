import { useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { apiClient } from '@/lib/api-client'
import { Truck, Search, FileText, RefreshCw } from 'lucide-react'
import { recordArrayFromResponse, stringValue } from '@/lib/record-utils'

type Branch = {
  id: string
  branch_number: number
  name: string
}

type Frachtauftrag = {
  id: string
  datum: string
  auftragNr: string
  kdAuftragNr: string
  kundenName: string
  lieferTermin: string
  ladeDatum: string
  spediteurNr: string
  spediteurName: string
  eingangsLieferschein: string
  info: string
  frachtArtikel: string
  status: string
}

function mapFrachtauftrag(row: Record<string, unknown>): Frachtauftrag {
  return {
    id: stringValue(row.id),
    datum: stringValue(row.datum),
    auftragNr: stringValue(row.auftragNr, stringValue(row.auftrag_nr)),
    kdAuftragNr: stringValue(row.kdAuftragNr, stringValue(row.kd_auftrag_nr)),
    kundenName: stringValue(row.kundenName, stringValue(row.kunden_name)),
    lieferTermin: stringValue(row.lieferTermin, stringValue(row.liefer_termin)),
    ladeDatum: stringValue(row.ladeDatum, stringValue(row.lade_datum)),
    spediteurNr: stringValue(row.spediteurNr, stringValue(row.spediteur_nr)),
    spediteurName: stringValue(row.spediteurName, stringValue(row.spediteur_name)),
    eingangsLieferschein: stringValue(row.eingangsLieferschein, stringValue(row.eingangs_lieferschein)),
    info: stringValue(row.info),
    frachtArtikel: stringValue(row.frachtArtikel, stringValue(row.fracht_artikel)),
    status: stringValue(row.status),
  }
}

export default function EinkaufLieferscheinFrachtauftragPage(): JSX.Element {
  const searchInputRef = useRef<HTMLInputElement | null>(null)
  const today = new Date().toISOString().slice(0, 10)
  const yearStart = `${new Date().getFullYear()}-01-01`

  const [niederlassung, setNiederlassung] = useState('')
  const [von, setVon] = useState(yearStart)
  const [bis, setBis] = useState(today)
  const [spediteurNr, setSpediteurNr] = useState('')
  const [kundenNr, setKundenNr] = useState('')

  // Branches from API
  const { data: branches, isLoading: branchesLoading } = useQuery<Branch[]>({
    queryKey: ['admin', 'branches'],
    queryFn: async () => {
      const res = await apiClient.get<Branch[]>('/api/v1/admin/branches', {
        params: { active_only: true },
      })
      return res.data
    },
    staleTime: 5 * 60 * 1000,
  })

  const { data: frachtauftraege = [], refetch: refetchFracht } = useQuery<Frachtauftrag[]>({
    queryKey: ['einkauf', 'frachtauftraege'],
    queryFn: async (): Promise<Frachtauftrag[]> => {
      try {
        const res = await apiClient.get<{ data: Frachtauftrag[] } | Frachtauftrag[]>(
          '/api/v1/einkauf/frachtauftraege',
        )
        return recordArrayFromResponse(res.data).map(mapFrachtauftrag)
      } catch {
        return []
      }
    },
    staleTime: 2 * 60 * 1000,
  })

  const filtered = useMemo(() => {
    let items = frachtauftraege
    if (niederlassung) {
      items = items.filter((f) => f.id.includes(niederlassung))
    }
    if (spediteurNr.trim()) {
      const term = spediteurNr.trim().toLowerCase()
      items = items.filter(
        (f) =>
          f.spediteurNr.toLowerCase().includes(term) ||
          f.spediteurName.toLowerCase().includes(term),
      )
    }
    if (kundenNr.trim()) {
      const term = kundenNr.trim().toLowerCase()
      items = items.filter(
        (f) =>
          f.kundenName.toLowerCase().includes(term) ||
          f.kdAuftragNr.toLowerCase().includes(term),
      )
    }
    return items
  }, [frachtauftraege, niederlassung, spediteurNr, kundenNr])

  const shortcuts = buildCoreMaskShortcuts({
    onSearch: () => searchInputRef.current?.focus(),
    onRefresh: () => {
      refetchFracht()
    },
  })
  useKeyboardShortcuts(shortcuts)

  const columns = [
    { key: 'datum' as const, label: 'Datum' },
    {
      key: 'auftragNr' as const,
      label: 'Auftrag-Nr.',
      render: (row: Frachtauftrag) => (
        <span className="font-mono font-medium">{row.auftragNr}</span>
      ),
    },
    { key: 'kdAuftragNr' as const, label: 'KD-Auftrag' },
    {
      key: 'kundenName' as const,
      label: 'Kunden-Name',
      render: (row: Frachtauftrag) => (
        <div className="max-w-[200px] truncate" title={row.kundenName}>
          {row.kundenName}
        </div>
      ),
    },
    { key: 'lieferTermin' as const, label: 'Liefer-Termin' },
    { key: 'ladeDatum' as const, label: 'Lade-Datum' },
    { key: 'spediteurNr' as const, label: 'Sped.-Nr.' },
    { key: 'spediteurName' as const, label: 'Spediteur' },
    { key: 'eingangsLieferschein' as const, label: 'E.-Lief.-Schein' },
    { key: 'info' as const, label: 'Info' },
    { key: 'frachtArtikel' as const, label: 'Fracht-Artikel' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (row: Frachtauftrag) => (
        <Badge
          variant={
            row.status === 'erledigt'
              ? 'outline'
              : row.status === 'in-bearbeitung'
                ? 'secondary'
                : 'default'
          }
        >
          {row.status || 'Offen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-6 overflow-auto p-6">
        {/* Header */}
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold">Frachtauftraege</h1>
            <p className="text-muted-foreground">
              Frachtauftraege nach Niederlassung, Zeitraum und Spediteur filtern.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <FileText className="h-4 w-4" />
              Frachtauftrag anlegen
            </Button>
            <Button variant="outline" size="sm" className="gap-2">
              <RefreshCw className="h-4 w-4" />
              Aktualisieren
            </Button>
          </div>
        </div>

        {/* Filter bar */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Filter</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
              {/* Branch selector */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Niederlassung</label>
                {branchesLoading ? (
                  <Skeleton className="h-9 w-full" />
                ) : (
                  <NativeSelect
                    value={niederlassung}
                    onChange={(e) => setNiederlassung(e.target.value)}
                  >
                    <option value="">Alle Niederlassungen</option>
                    {(branches ?? []).map((b) => (
                      <option key={b.id} value={String(b.branch_number)}>
                        {b.branch_number} — {b.name}
                      </option>
                    ))}
                  </NativeSelect>
                )}
              </div>

              {/* Date range */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Liefer-Termin von</label>
                <Input
                  type="date"
                  value={von}
                  onChange={(e) => setVon(e.target.value)}
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">bis</label>
                <Input
                  type="date"
                  value={bis}
                  onChange={(e) => setBis(e.target.value)}
                />
              </div>

              {/* Spediteur */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Spediteur-Nr.</label>
                <Input
                  ref={searchInputRef}
                  placeholder="Sped.-Nr. oder Name"
                  value={spediteurNr}
                  onChange={(e) => setSpediteurNr(e.target.value)}
                />
              </div>

              {/* Kunden-Nr */}
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Kunden-Nr.</label>
                <Input
                  placeholder="KD-Nr. oder Name"
                  value={kundenNr}
                  onChange={(e) => setKundenNr(e.target.value)}
                />
              </div>

              {/* Search button */}
              <div className="flex items-end">
                <Button className="w-full gap-2">
                  <Search className="h-4 w-4" />
                  Suchen
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Summary cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Offene Auftraege</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Truck className="h-5 w-5 text-blue-600" />
                <span className="text-2xl font-bold">
                  {filtered.filter((f) => f.status !== 'erledigt').length}
                </span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Erledigte Auftraege</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-status-success">
                {filtered.filter((f) => f.status === 'erledigt').length}
              </span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
            </CardHeader>
            <CardContent>
              <span className="text-2xl font-bold">{filtered.length}</span>
            </CardContent>
          </Card>
        </div>

        {/* Data table */}
        <Card>
          <CardContent className="pt-6">
            {filtered.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                <Truck className="mb-4 h-12 w-12 opacity-30" />
                <p className="text-lg font-medium">Keine Frachtauftraege gefunden</p>
                <p className="text-sm">
                  {niederlassung || spediteurNr || kundenNr
                    ? 'Passen Sie die Filterkriterien an.'
                    : 'Der Frachtauftrags-Endpoint ist noch nicht implementiert.'}
                </p>
              </div>
            ) : (
              <DataTable data={filtered} columns={columns} />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Bottom shortcut bar */}
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
