import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, Plus, Search, Truck } from 'lucide-react'

type Fahrzeug = {
  id: string
  kennzeichen: string
  typ: string
  kilometerstand: number
  naechsteInspektion: string
  status: 'verfuegbar' | 'unterwegs' | 'werkstatt'
}

const mockFahrzeuge: Fahrzeug[] = [
  { id: '1', kennzeichen: 'AB-LH 101', typ: 'LKW 7,5t', kilometerstand: 125000, naechsteInspektion: '2025-11-15', status: 'unterwegs' },
  { id: '2', kennzeichen: 'AB-LH 102', typ: 'LKW 12t', kilometerstand: 98000, naechsteInspektion: '2025-12-01', status: 'verfuegbar' },
  { id: '3', kennzeichen: 'AB-LH 103', typ: 'Traktor', kilometerstand: 5600, naechsteInspektion: '2025-10-20', status: 'werkstatt' },
]

export default function FahrzeugePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const inspektionFaellig = mockFahrzeuge.filter((f) => new Date(f.naechsteInspektion) < new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)).length

  const columns = [
    {
      key: 'kennzeichen' as const,
      label: 'Kennzeichen',
      render: (f: Fahrzeug) => (
        <button onClick={() => navigate(`/fuhrpark/fahrzeug/${f.id}`)} className="font-medium text-blue-600 hover:underline font-mono">
          {f.kennzeichen}
        </button>
      ),
    },
    { key: 'typ' as const, label: 'Typ' },
    { key: 'kilometerstand' as const, label: 'km-Stand', render: (f: Fahrzeug) => f.kilometerstand.toLocaleString('de-DE') },
    {
      key: 'naechsteInspektion' as const,
      label: 'Inspektion',
      render: (f: Fahrzeug) => {
        const datum = new Date(f.naechsteInspektion)
        const faellig = datum < new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
        return (
          <span className={faellig ? 'font-semibold text-orange-600' : ''}>
            {datum.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (f: Fahrzeug) => (
        <Badge variant={f.status === 'verfuegbar' ? 'outline' : f.status === 'unterwegs' ? 'secondary' : 'destructive'}>
          {f.status === 'verfuegbar' ? 'Verfügbar' : f.status === 'unterwegs' ? 'Unterwegs' : 'Werkstatt'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fuhrpark</h1>
          <p className="text-muted-foreground">Fahrzeug-Verwaltung</p>
        </div>
        <Button onClick={() => navigate('/fuhrpark/fahrzeug/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues Fahrzeug
        </Button>
      </div>

      {inspektionFaellig > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{inspektionFaellig} Inspektion(en) in den nächsten 14 Tagen fällig!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fahrzeuge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockFahrzeuge.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Verfügbar</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockFahrzeuge.filter((f) => f.status === 'verfuegbar').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Unterwegs</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockFahrzeuge.filter((f) => f.status === 'unterwegs').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Inspektion fällig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{inspektionFaellig}</span>
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
          <DataTable data={mockFahrzeuge} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
