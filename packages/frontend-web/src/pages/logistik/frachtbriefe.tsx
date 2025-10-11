import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, FileText, Plus, Search } from 'lucide-react'

type Frachtbrief = {
  id: string
  nummer: string
  kennzeichen: string
  artikel: string
  menge: number
  absender: string
  empfaenger: string
  datum: string
  status: 'erstellt' | 'unterwegs' | 'zugestellt'
}

const mockFrachtbriefe: Frachtbrief[] = [
  { id: '1', nummer: 'FB-2025-042', kennzeichen: 'AB-CD 1234', artikel: 'Weizen', menge: 25.0, absender: 'VALEO Landhandel', empfaenger: 'Mühle Nord', datum: '2025-10-11', status: 'unterwegs' },
  { id: '2', nummer: 'FB-2025-043', kennzeichen: 'EF-GH 5678', artikel: 'Raps', menge: 18.5, absender: 'VALEO Landhandel', empfaenger: 'Ölmühle Süd', datum: '2025-10-11', status: 'erstellt' },
]

export default function FrachtbriefePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Frachtbrief-Nr.',
      render: (f: Frachtbrief) => (
        <button onClick={() => navigate(`/logistik/frachtbrief/${f.id}`)} className="font-medium text-blue-600 hover:underline font-mono">
          {f.nummer}
        </button>
      ),
    },
    { key: 'kennzeichen' as const, label: 'LKW', render: (f: Frachtbrief) => <span className="font-mono">{f.kennzeichen}</span> },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'menge' as const, label: 'Menge (t)', render: (f: Frachtbrief) => `${f.menge} t` },
    {
      key: 'empfaenger' as const,
      label: 'Von → Nach',
      render: (f: Frachtbrief) => (
        <div className="text-sm">
          <div>{f.absender}</div>
          <div className="text-muted-foreground">→ {f.empfaenger}</div>
        </div>
      ),
    },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (f: Frachtbrief) => new Date(f.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (f: Frachtbrief) => (
        <Badge variant={f.status === 'zugestellt' ? 'outline' : f.status === 'unterwegs' ? 'secondary' : 'default'}>
          {f.status === 'erstellt' ? 'Erstellt' : f.status === 'unterwegs' ? 'Unterwegs' : 'Zugestellt'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Frachtbriefe</h1>
          <p className="text-muted-foreground">Transport-Dokumentation</p>
        </div>
        <Button onClick={() => navigate('/logistik/frachtbrief/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Frachtbrief
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Frachtbriefe Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockFrachtbriefe.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Unterwegs</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockFrachtbriefe.filter((f) => f.status === 'unterwegs').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Zugestellt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockFrachtbriefe.filter((f) => f.status === 'zugestellt').length}</span>
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
          <DataTable data={mockFrachtbriefe} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
