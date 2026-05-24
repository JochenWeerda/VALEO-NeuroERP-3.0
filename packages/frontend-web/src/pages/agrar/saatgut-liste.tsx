import { type JSX, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { type ColumnDef } from '@/components/ui/data-table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { ListReport } from '@/components/patterns/ListReport'
import { useToast } from '@/hooks/use-toast'
import { CheckCircle, Edit, Eye, FileDown, Sprout, XCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

interface SaatgutItem {
  id: string
  artikelnummer: string
  name: string
  sorte: string
  art: string
  zuechter: string
  bsa_zulassung: boolean
  eu_zulassung: boolean
  vk_preis: number | null
  lagerbestand: number
  reserviert: number
  verfuegbar: number
}

const buildColumns = (
  onView: (itemId: string) => void,
  onEdit: (itemId: string) => void,
): ColumnDef<SaatgutItem>[] => [
  { accessorKey: 'artikelnummer', header: 'Artikelnummer', cell: ({ row }): JSX.Element => <span className="font-mono text-sm">{row.original.artikelnummer}</span> },
  { accessorKey: 'name', header: 'Name' },
  { accessorKey: 'sorte', header: 'Sorte' },
  { accessorKey: 'art', header: 'Art' },
  { accessorKey: 'zuechter', header: 'Zuechter' },
  {
    accessorKey: 'zulassungen',
    header: 'Zulassungen',
    cell: ({ row }): JSX.Element => {
      const item = row.original
      const badges = []
      if (item.bsa_zulassung) badges.push(<Badge key="bsa" variant="secondary" className="bg-green-100 text-green-800"><CheckCircle className="mr-1 w-3 h-3" />BSA</Badge>)
      if (item.eu_zulassung) badges.push(<Badge key="eu" variant="secondary" className="bg-blue-100 text-blue-800"><CheckCircle className="mr-1 w-3 h-3" />EU</Badge>)
      if (!item.bsa_zulassung && !item.eu_zulassung) badges.push(<Badge key="none" variant="secondary" className="bg-gray-100 text-gray-600"><XCircle className="mr-1 w-3 h-3" />Keine Zulassung</Badge>)
      return <div className="flex flex-wrap gap-1">{badges}</div>
    },
  },
  {
    accessorKey: 'lagerstatus',
    header: 'Lagerstatus',
    cell: ({ row }): JSX.Element => {
      const available = row.original.verfuegbar || 0
      if (available <= 0) return <Badge variant="destructive">Nicht verfuegbar</Badge>
      if (available < 100) return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Niedrig</Badge>
      return <Badge variant="secondary" className="bg-green-100 text-green-800">Verfuegbar</Badge>
    },
  },
  { accessorKey: 'vk_preis', header: 'VK-Preis', cell: ({ row }): string => (row.original.vk_preis ? `EUR ${row.original.vk_preis.toFixed(2)}` : '-') },
  {
    accessorKey: 'actions',
    header: 'Aktionen',
    cell: ({ row }): JSX.Element => (
      <div className="flex gap-2">
        <Button variant="outline" size="sm" onClick={() => onView(row.original.id)} title="Anzeigen"><Eye className="w-4 h-4" /></Button>
        <Button variant="outline" size="sm" onClick={() => onEdit(row.original.id)} title="Bearbeiten"><Edit className="w-4 h-4" /></Button>
      </div>
    ),
  },
]

export default function SaatgutListePage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [search, setSearch] = useState('')

  const { data: saatgutList, isLoading } = useQuery<{ items: SaatgutItem[] }>({
    queryKey: ['saatgut-list'],
    queryFn: async () => {
      const r = await apiClient.get<{ items: SaatgutItem[] }>('/api/v1/agrar/saatgut?limit=100')
      return r.data
    },
  })

  const columns = useMemo(
    () => buildColumns(
      (itemId) => navigate(`/agrar/saatgut-stamm/${itemId}?mode=view`),
      (itemId) => navigate(`/agrar/saatgut-stamm/${itemId}`),
    ),
    [navigate],
  )

  const filteredData = useMemo<SaatgutItem[]>(() => {
    if (!Array.isArray(saatgutList?.items)) return []
    const term = search.trim().toLowerCase()
    if (term.length === 0) return saatgutList.items
    return saatgutList.items.filter((item: SaatgutItem) =>
      item.name.toLowerCase().includes(term) ||
      item.artikelnummer.toLowerCase().includes(term) ||
      item.sorte.toLowerCase().includes(term) ||
      item.art.toLowerCase().includes(term) ||
      item.zuechter?.toLowerCase().includes(term),
    )
  }, [saatgutList, search])

  const stats = useMemo(() => ({
    total: filteredData.length,
    available: filteredData.filter((item) => (item.verfuegbar || 0) > 0).length,
    approved: filteredData.filter((item) => item.bsa_zulassung || item.eu_zulassung).length,
    lowStock: filteredData.filter((item) => (item.verfuegbar || 0) > 0 && (item.verfuegbar || 0) < 100).length,
  }), [filteredData])

  const exportSaatgut = (): void => {
    const header = 'Artikelnummer;Name;Sorte;Art;Zuechter;BSA;EU;VK-Preis;Lager;Reserviert;Verfuegbar\n'
    const rows = filteredData.map((item) =>
      [item.artikelnummer, item.name, item.sorte, item.art, item.zuechter, item.bsa_zulassung ? 'ja' : 'nein', item.eu_zulassung ? 'ja' : 'nein', item.vk_preis ?? '', item.lagerbestand, item.reserviert, item.verfuegbar]
        .map((v) => `"${String(v).replace(/"/g, '""')}"`)
        .join(';'),
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Saatgut_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredData.length} Saatgut-Eintraege exportiert.` })
  }

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-12 w-1/2" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-72 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Saatgut Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Sprout className="h-5 w-5 text-green-600" /><span className="text-2xl font-bold">{stats.total}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Verfuegbar</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{stats.available}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Mit Zulassung</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{stats.approved}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Niedriger Bestand</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{stats.lowStock}</span></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Operative Folgewege</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button variant="outline" onClick={() => filteredData[0] && navigate(`/agrar/saatgut-stamm/${filteredData[0].id}`)} disabled={filteredData.length === 0}>Stammsatz oeffnen</Button>
          <Button variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumente</Button>
          <Button variant="outline" onClick={exportSaatgut}><FileDown className="mr-2 h-4 w-4" />Export</Button>
        </CardContent>
      </Card>

      <ListReport
        title="Saatgut-Verwaltung"
        subtitle="Uebersicht aller Saatgut-Arten und -Sorten"
        data={filteredData}
        columns={columns}
        primaryActions={[{ id: 'create-saatgut', label: 'Neues Saatgut', onClick: (): void => navigate('/agrar/saatgut-stamm') }]}
        overflowActions={[{ id: 'export-saatgut', label: 'Export CSV', onClick: exportSaatgut }]}
        searchPlaceholder="Saatgut suchen (Name, Artikelnummer, Sorte, Art, Zuechter)"
        onSearch={setSearch}
        filterOptions={[
          { field: 'art', label: 'Art', type: 'select', options: [{ value: 'Weizen', label: 'Weizen' }, { value: 'Gerste', label: 'Gerste' }, { value: 'Roggen', label: 'Roggen' }, { value: 'Hafer', label: 'Hafer' }, { value: 'Mais', label: 'Mais' }, { value: 'Raps', label: 'Raps' }] },
          { field: 'bsa_zulassung', label: 'BSA-Zulassung', type: 'select', options: [{ value: 'true', label: 'Ja' }, { value: 'false', label: 'Nein' }] },
          { field: 'eu_zulassung', label: 'EU-Zulassung', type: 'select', options: [{ value: 'true', label: 'Ja' }, { value: 'false', label: 'Nein' }] },
        ]}
        selectable
        mcpContext={{ pageDomain: 'agrar', currentDocument: 'saatgut' }}
      />
    </div>
  )
}
