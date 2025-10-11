import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { CalendarDays, FileDown, Plus, Search } from 'lucide-react'

type Massnahme = {
  id: string
  datum: string
  schlag: string
  typ: 'Aussaat' | 'Düngung' | 'PSM' | 'Ernte'
  mittel: string
  menge: number
}

const mockMassnahmen: Massnahme[] = [
  { id: '1', datum: '2025-10-11', schlag: 'Nordfeld 1', typ: 'Düngung', mittel: 'NPK-Dünger', menge: 200 },
  { id: '2', datum: '2025-10-10', schlag: 'Südacker', typ: 'PSM', mittel: 'Roundup', menge: 3.5 },
  { id: '3', datum: '2025-10-09', schlag: 'Nordfeld 1', typ: 'Aussaat', mittel: 'Weizen Asano', menge: 180 },
]

export default function MassnahmenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (m: Massnahme) => new Date(m.datum).toLocaleDateString('de-DE'),
    },
    { key: 'schlag' as const, label: 'Schlag' },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (m: Massnahme) => (
        <Badge variant={m.typ === 'PSM' ? 'destructive' : 'outline'}>
          {m.typ}
        </Badge>
      ),
    },
    { key: 'mittel' as const, label: 'Mittel' },
    { key: 'menge' as const, label: 'Menge', render: (m: Massnahme) => `${m.menge} ${m.typ === 'PSM' ? 'l' : 'kg'}` },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Maßnahmen-Dokumentation</h1>
          <p className="text-muted-foreground">Feldbuch</p>
        </div>
        <Button onClick={() => navigate('/agrar/feldbuch/massnahme/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Maßnahme
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Maßnahmen (7 Tage)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CalendarDays className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockMassnahmen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Düngungen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockMassnahmen.filter((m) => m.typ === 'Düngung').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">PSM-Anwendungen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockMassnahmen.filter((m) => m.typ === 'PSM').length}</span>
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
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockMassnahmen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
