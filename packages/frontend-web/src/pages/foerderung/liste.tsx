import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, FileText, Plus, Search } from 'lucide-react'

type Antrag = {
  id: string
  nummer: string
  programm: string
  antragsdatum: string
  flaeche: number
  betrag: number
  status: 'eingereicht' | 'in-pruefung' | 'bewilligt' | 'abgelehnt'
}

const mockAntraege: Antrag[] = [
  { id: '1', nummer: 'FA-2025-001', programm: 'Greening', antragsdatum: '2025-03-15', flaeche: 250, betrag: 21250, status: 'bewilligt' },
  { id: '2', nummer: 'FA-2025-002', programm: 'Biodiversität', antragsdatum: '2025-06-01', flaeche: 15.8, betrag: 18960, status: 'in-pruefung' },
]

export default function FoerderantraegeListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Antragsnummer',
      render: (a: Antrag) => (
        <button onClick={() => navigate(`/foerderung/antrag/${a.id}`)} className="font-medium text-blue-600 hover:underline">
          {a.nummer}
        </button>
      ),
    },
    { key: 'programm' as const, label: 'Programm', render: (a: Antrag) => <Badge variant="outline">{a.programm}</Badge> },
    {
      key: 'antragsdatum' as const,
      label: 'Antragsdatum',
      render: (a: Antrag) => new Date(a.antragsdatum).toLocaleDateString('de-DE'),
    },
    { key: 'flaeche' as const, label: 'Fläche (ha)', render: (a: Antrag) => `${a.flaeche} ha` },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (a: Antrag) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(a.betrag),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (a: Antrag) => (
        <Badge variant={a.status === 'bewilligt' ? 'outline' : a.status === 'abgelehnt' ? 'destructive' : 'secondary'}>
          {a.status === 'eingereicht' ? 'Eingereicht' : a.status === 'in-pruefung' ? 'In Prüfung' : a.status === 'bewilligt' ? 'Bewilligt' : 'Abgelehnt'}
        </Badge>
      ),
    },
  ]

  const gesamtBetrag = mockAntraege.filter((a) => a.status === 'bewilligt').reduce((sum, a) => sum + a.betrag, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Förderanträge</h1>
          <p className="text-muted-foreground">EU-Agrarförderung</p>
        </div>
        <Button onClick={() => navigate('/foerderung/antrag')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Antrag
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Anträge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockAntraege.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bewilligt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockAntraege.filter((a) => a.status === 'bewilligt').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Prüfung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockAntraege.filter((a) => a.status === 'in-pruefung').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bewilligte Summe</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtBetrag)}
            </span>
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
          <DataTable data={mockAntraege} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
