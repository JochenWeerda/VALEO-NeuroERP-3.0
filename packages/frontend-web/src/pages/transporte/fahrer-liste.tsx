import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useFahrerListe, type Fahrer } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Truck } from 'lucide-react'

const mockFahrer: Fahrer[] = [
  { id: '1', name: 'Max Schmidt', fuehrerschein: 'C', fahrzeug: 'LKW-01', status: 'unterwegs', tourenHeute: 2 },
  { id: '2', name: 'Tom Mueller', fuehrerschein: 'C', fahrzeug: 'LKW-02', status: 'verfuegbar', tourenHeute: 1 },
  { id: '3', name: 'Anna Weber', fuehrerschein: 'CE', fahrzeug: 'LKW-03', status: 'pause', tourenHeute: 3 },
]

export default function FahrerListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: fahrer = mockFahrer } = useFahrerListe()

  const columns = [
    { key: 'name' as const, label: 'Name', render: (f: Fahrer) => <button onClick={() => navigate(`/transporte/fahrer/${f.id}`)} className="font-medium text-blue-600 hover:underline">{f.name}</button> },
    { key: 'fuehrerschein' as const, label: 'Fuehrerschein', render: (f: Fahrer) => <Badge variant="outline">Klasse {f.fuehrerschein}</Badge> },
    { key: 'fahrzeug' as const, label: 'Fahrzeug' },
    { key: 'tourenHeute' as const, label: 'Touren Heute' },
    { key: 'status' as const, label: 'Status', render: (f: Fahrer) => <Badge variant={f.status === 'verfuegbar' ? 'outline' : f.status === 'unterwegs' ? 'secondary' : 'default'}>{f.status === 'verfuegbar' ? 'Verfuegbar' : f.status === 'unterwegs' ? 'Unterwegs' : 'Pause'}</Badge> },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold">Fahrer</h1><p className="text-muted-foreground">Fahrer-Verwaltung</p></div><Button onClick={() => navigate('/transporte/fahrer/neu')} className="gap-2"><Plus className="h-4 w-4" />Neuer Fahrer</Button></div>
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Fahrer Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Truck className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{fahrer.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Verfuegbar</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{fahrer.filter((f) => f.status === 'verfuegbar').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Unterwegs</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{fahrer.filter((f) => f.status === 'unterwegs').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Touren Heute</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{fahrer.reduce((sum, f) => sum + f.tourenHeute, 0)}</span></CardContent></Card>
      </div>
      <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex gap-4"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div><Button variant="outline" className="gap-2"><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
      <Card><CardContent className="pt-6"><DataTable data={fahrer} columns={columns} /></CardContent></Card>
    </div>
  )
}
