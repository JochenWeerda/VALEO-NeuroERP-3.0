import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search } from 'lucide-react'

type Futter = {
  id: string
  artikel: string
  art: string
  protein: number
  gvoStatus: string
  verfuegbar: number
}

const mockFutter: Futter[] = [
  {
    id: '1',
    artikel: 'Sojaschrot 44%',
    art: 'Eiweißfutter',
    protein: 44.0,
    gvoStatus: 'GVO-frei (VLOG)',
    verfuegbar: 150,
  },
  {
    id: '2',
    artikel: 'Weizen Futterqualität',
    art: 'Getreide',
    protein: 11.5,
    gvoStatus: 'GVO-frei',
    verfuegbar: 200,
  },
]

export default function EinzelfutterListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'artikel' as const,
      label: 'Artikel',
      render: (f: Futter) => (
        <button onClick={() => navigate(`/futter/einzel/stamm/${f.id}`)} className="font-medium text-blue-600 hover:underline">
          {f.artikel}
        </button>
      ),
    },
    {
      key: 'art' as const,
      label: 'Art',
    },
    {
      key: 'protein' as const,
      label: 'Protein',
      render: (f: Futter) => `${f.protein}%`,
    },
    {
      key: 'gvoStatus' as const,
      label: 'GVO-Status',
      render: (f: Futter) => <Badge variant="outline">{f.gvoStatus}</Badge>,
    },
    {
      key: 'verfuegbar' as const,
      label: 'Verfügbar (t)',
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Einzelfuttermittel</h1>
          <p className="text-muted-foreground">Übersicht</p>
        </div>
        <Button onClick={() => navigate('/futter/einzel/stamm/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues Futtermittel
        </Button>
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
          <DataTable data={mockFutter} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
