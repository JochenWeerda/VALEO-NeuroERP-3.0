import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Users } from 'lucide-react'

type Kunde = {
  id: string
  name: string
  ort: string
  umsatz: number
  zahlungsziel: number
  status: 'aktiv' | 'gesperrt'
}

const mockKunden: Kunde[] = [
  { id: '1', name: 'Landhandel Nord GmbH', ort: 'Nordhausen', umsatz: 125000, zahlungsziel: 30, status: 'aktiv' },
  { id: '2', name: 'Agrar Süd AG', ort: 'Südhausen', umsatz: 98000, zahlungsziel: 30, status: 'aktiv' },
  { id: '3', name: 'Müller Landwirtschaft', ort: 'Mühlhausen', umsatz: 45000, zahlungsziel: 14, status: 'aktiv' },
]

export default function KundenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Kunde',
      render: (k: Kunde) => (
        <button onClick={() => navigate(`/verkauf/kunde/${k.id}`)} className="font-medium text-blue-600 hover:underline">
          {k.name}
        </button>
      ),
    },
    { key: 'ort' as const, label: 'Ort' },
    {
      key: 'umsatz' as const,
      label: 'Jahresumsatz',
      render: (k: Kunde) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(k.umsatz),
    },
    { key: 'zahlungsziel' as const, label: 'Zahlungsziel', render: (k: Kunde) => `${k.zahlungsziel} Tage` },
    {
      key: 'status' as const,
      label: 'Status',
      render: (k: Kunde) => (
        <Badge variant={k.status === 'aktiv' ? 'outline' : 'destructive'}>
          {k.status === 'aktiv' ? 'Aktiv' : 'Gesperrt'}
        </Badge>
      ),
    },
  ]

  const gesamtUmsatz = mockKunden.reduce((sum, k) => sum + k.umsatz, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kunden</h1>
          <p className="text-muted-foreground">Kundenverwaltung</p>
        </div>
        <Button onClick={() => navigate('/verkauf/kunde/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Kunde
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kunden Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockKunden.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Jahresumsatz</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtUmsatz)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockKunden.filter((k) => k.status === 'aktiv').length}</span>
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
          <DataTable data={mockKunden} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
