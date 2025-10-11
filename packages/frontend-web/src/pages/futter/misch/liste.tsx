import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search } from 'lucide-react'

type Mischfutter = {
  id: string
  typ: string
  tierart: string
  protein: number
  verfuegbar: number
}

const mockMischfutter: Mischfutter[] = [
  { id: '1', typ: 'Milchviehfutter Hochleistung', tierart: 'Rind (Milch)', protein: 18.5, verfuegbar: 80 },
  { id: '2', typ: 'Mastbullenfutter', tierart: 'Rind (Mast)', protein: 16.0, verfuegbar: 120 },
]

export default function MischfutterListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (m: Mischfutter) => (
        <button onClick={() => navigate(`/futter/misch/stamm/${m.id}`)} className="font-medium text-blue-600 hover:underline">
          {m.typ}
        </button>
      ),
    },
    { key: 'tierart' as const, label: 'Tierart' },
    { key: 'protein' as const, label: 'Protein (%)', render: (m: Mischfutter) => `${m.protein}%` },
    { key: 'verfuegbar' as const, label: 'Verfügbar (t)' },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Mischfuttermittel</h1>
          <p className="text-muted-foreground">Übersicht</p>
        </div>
        <Button onClick={() => navigate('/futter/misch/stamm/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues Mischfutter
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
          <DataTable data={mockMischfutter} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
