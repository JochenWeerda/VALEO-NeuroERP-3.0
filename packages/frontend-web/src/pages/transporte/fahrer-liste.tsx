import { useMemo, useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { FileDown, Plus, Search, Truck } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { ErrorState } from '@/components/ErrorState'
import { toast } from '@/hooks/use-toast'
import { useFahrerListe, type Fahrer } from '@/lib/api/betrieb'

export default function FahrerListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: fahrer = [], isError, error, refetch } = useFahrerListe()

  const filteredFahrer = useMemo(() => {
    if (!searchTerm) return fahrer
    const term = searchTerm.toLowerCase()
    return fahrer.filter((f) =>
      f.name.toLowerCase().includes(term) ||
      f.fahrzeug.toLowerCase().includes(term) ||
      f.status.toLowerCase().includes(term),
    )
  }, [fahrer, searchTerm])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = () => {
    const header = 'Name;Fuehrerschein;Fahrzeug;Status;Touren Heute\n'
    const rows = filteredFahrer.map((f) =>
      [f.name, f.fuehrerschein, f.fahrzeug, f.status, f.tourenHeute]
        .map((value) => `"${String(value).replace(/"/g, '""')}"`)
        .join(';'),
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Fahrer_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredFahrer.length} Fahrer exportiert.` })
  }

  const columns = [
    {
      key: 'name' as const,
      label: 'Name',
      render: (f: Fahrer) => (
        <button onClick={() => navigate(`/transporte/fahrer/${f.id}`)} className="font-medium text-blue-600 hover:underline">
          {f.name}
        </button>
      ),
    },
    { key: 'fuehrerschein' as const, label: 'Fuehrerschein', render: (f: Fahrer) => <Badge variant="outline">Klasse {f.fuehrerschein}</Badge> },
    { key: 'fahrzeug' as const, label: 'Fahrzeug' },
    { key: 'tourenHeute' as const, label: 'Touren Heute' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (f: Fahrer) => (
        <Badge variant={f.status === 'verfuegbar' ? 'outline' : f.status === 'unterwegs' ? 'secondary' : 'default'}>
          {f.status === 'verfuegbar' ? 'Verfuegbar' : f.status === 'unterwegs' ? 'Unterwegs' : 'Pause'}
        </Badge>
      ),
    },
  ]

  const availableDrivers = filteredFahrer.filter((f) => f.status === 'verfuegbar')

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fahrer</h1>
          <p className="text-muted-foreground">Fahrer-Verwaltung</p>
        </div>
        <Button onClick={() => navigate('/transporte/fahrer/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Fahrer
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Fahrer Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Truck className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{filteredFahrer.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Verfuegbar</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-success">{availableDrivers.length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Unterwegs</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-status-warning">{filteredFahrer.filter((f) => f.status === 'unterwegs').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Touren Heute</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{filteredFahrer.reduce((sum, f) => sum + f.tourenHeute, 0)}</span></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Disposition</CardTitle></CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button variant="outline" onClick={() => availableDrivers[0] && navigate(`/transporte/fahrer/${availableDrivers[0].id}`)} disabled={availableDrivers.length === 0}>
            Verfuegbaren Fahrer oeffnen
          </Button>
          <Button variant="outline" onClick={() => navigate('/logistik/tourenplanung')}>Tourenplanung</Button>
          <Button variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumente</Button>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredFahrer} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
