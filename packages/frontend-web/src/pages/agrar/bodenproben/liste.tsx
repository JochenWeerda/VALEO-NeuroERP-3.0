import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Beaker, FileDown, Plus, Search } from 'lucide-react'

type Bodenprobe = {
  id: string
  schlag: string
  datum: string
  labor: string
  n: number
  p: number
  k: number
  ph: number
  status: 'offen' | 'analysiert'
}

const mockProben: Bodenprobe[] = [
  { id: '1', schlag: 'Nordfeld 1', datum: '2025-09-15', labor: 'Labor Nord', n: 12.5, p: 18.2, k: 25.8, ph: 6.8, status: 'analysiert' },
  { id: '2', schlag: 'Südacker', datum: '2025-10-05', labor: 'Labor Süd', n: 0, p: 0, k: 0, ph: 0, status: 'offen' },
]

export default function BodenprobenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'schlag' as const,
      label: 'Schlag',
      render: (b: Bodenprobe) => (
        <button onClick={() => navigate(`/agrar/bodenprobe/${b.id}`)} className="font-medium text-blue-600 hover:underline">
          {b.schlag}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: 'Probenahme',
      render: (b: Bodenprobe) => new Date(b.datum).toLocaleDateString('de-DE'),
    },
    { key: 'labor' as const, label: 'Labor' },
    { key: 'n' as const, label: 'N', render: (b: Bodenprobe) => b.n > 0 ? `${b.n} mg` : '-' },
    { key: 'p' as const, label: 'P', render: (b: Bodenprobe) => b.p > 0 ? `${b.p} mg` : '-' },
    { key: 'k' as const, label: 'K', render: (b: Bodenprobe) => b.k > 0 ? `${b.k} mg` : '-' },
    { key: 'ph' as const, label: 'pH', render: (b: Bodenprobe) => b.ph > 0 ? b.ph.toFixed(1) : '-' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (b: Bodenprobe) => (
        <Badge variant={b.status === 'analysiert' ? 'outline' : 'default'}>
          {b.status === 'offen' ? 'Offen' : 'Analysiert'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bodenproben</h1>
          <p className="text-muted-foreground">Nährstoff-Analysen</p>
        </div>
        <Button onClick={() => navigate('/agrar/bodenprobe/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Bodenprobe
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Proben Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Beaker className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockProben.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Analysiert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockProben.filter((p) => p.status === 'analysiert').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockProben.filter((p) => p.status === 'offen').length}</span>
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
          <DataTable data={mockProben} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
