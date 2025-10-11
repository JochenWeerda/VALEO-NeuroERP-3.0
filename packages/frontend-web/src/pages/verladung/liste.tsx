import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Truck } from 'lucide-react'

type Verladung = {
  id: string
  kennzeichen: string
  artikel: string
  menge: number
  lieferscheinNr: string
  datum: string
  status: 'geplant' | 'in-verladung' | 'abgeschlossen'
}

const mockVerladungen: Verladung[] = [
  { id: '1', kennzeichen: 'AB-CD 1234', artikel: 'Weizen', menge: 25.0, lieferscheinNr: 'LS-2025-042', datum: '2025-10-11', status: 'in-verladung' },
  { id: '2', kennzeichen: 'EF-GH 5678', artikel: 'Raps', menge: 18.5, lieferscheinNr: 'LS-2025-043', datum: '2025-10-11', status: 'geplant' },
]

export default function VerladungenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'kennzeichen' as const,
      label: 'Kennzeichen',
      render: (v: Verladung) => <span className="font-mono font-bold">{v.kennzeichen}</span>,
    },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'menge' as const, label: 'Menge (t)', render: (v: Verladung) => `${v.menge} t` },
    { key: 'lieferscheinNr' as const, label: 'Lieferschein', render: (v: Verladung) => <span className="font-mono text-sm">{v.lieferscheinNr}</span> },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (v: Verladung) => new Date(v.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (v: Verladung) => (
        <Badge variant={v.status === 'abgeschlossen' ? 'outline' : v.status === 'in-verladung' ? 'secondary' : 'default'}>
          {v.status === 'geplant' ? 'Geplant' : v.status === 'in-verladung' ? 'In Verladung' : 'Abgeschlossen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Verladungen</h1>
          <p className="text-muted-foreground">LKW-Beladungen</p>
        </div>
        <Button onClick={() => navigate('/verladung/lkw-beladung')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Beladung
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Verladungen Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockVerladungen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Verladung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockVerladungen.filter((v) => v.status === 'in-verladung').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockVerladungen.filter((v) => v.status === 'abgeschlossen').length}</span>
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
          <DataTable data={mockVerladungen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
