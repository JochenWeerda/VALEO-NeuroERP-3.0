import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { BookMarked, FileDown, Plus, Search } from 'lucide-react'

type Konto = {
  id: string
  kontonummer: string
  bezeichnung: string
  kontoart: string
  saldo: number
  typ: 'aktiv' | 'passiv' | 'aufwand' | 'ertrag'
}

const mockKonten: Konto[] = [
  { id: '1', kontonummer: '1200', bezeichnung: 'Bank', kontoart: 'Umlaufvermögen', saldo: 285000, typ: 'aktiv' },
  { id: '2', kontonummer: '1600', bezeichnung: 'Verbindlichkeiten aus LuL', kontoart: 'Verbindlichkeiten', saldo: -125000, typ: 'passiv' },
  { id: '3', kontonummer: '4200', bezeichnung: 'Wareneinkauf', kontoart: 'Aufwendungen', saldo: 450000, typ: 'aufwand' },
  { id: '4', kontonummer: '8400', bezeichnung: 'Erlöse', kontoart: 'Erträge', saldo: 680000, typ: 'ertrag' },
  { id: '5', kontonummer: '1800', bezeichnung: 'Kasse', kontoart: 'Umlaufvermögen', saldo: 12500, typ: 'aktiv' },
]

export default function KontenplanPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'kontonummer' as const,
      label: 'Konto',
      render: (k: Konto) => (
        <button onClick={() => navigate(`/fibu/sachkonto/${k.id}`)} className="font-medium text-blue-600 hover:underline font-mono text-lg">
          {k.kontonummer}
        </button>
      ),
    },
    { key: 'bezeichnung' as const, label: 'Bezeichnung', render: (k: Konto) => <span className="font-semibold">{k.bezeichnung}</span> },
    { key: 'kontoart' as const, label: 'Kontoart' },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (k: Konto) => (
        <Badge variant="outline">
          {k.typ === 'aktiv' ? 'Aktiva' : k.typ === 'passiv' ? 'Passiva' : k.typ === 'aufwand' ? 'Aufwand' : 'Ertrag'}
        </Badge>
      ),
    },
    {
      key: 'saldo' as const,
      label: 'Saldo',
      render: (k: Konto) => (
        <span className={`font-bold ${k.saldo < 0 ? 'text-red-600' : 'text-green-600'}`}>
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(Math.abs(k.saldo))}
          {k.saldo < 0 ? ' H' : ' S'}
        </span>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kontenplan</h1>
          <p className="text-muted-foreground">SKR03 Standardkontenrahmen</p>
        </div>
        <Button onClick={() => navigate('/fibu/sachkonto/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues Konto
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Konten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BookMarked className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockKonten.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiva</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockKonten.filter((k) => k.typ === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aufwand</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockKonten.filter((k) => k.typ === 'aufwand').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ertrag</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockKonten.filter((k) => k.typ === 'ertrag').length}</span>
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
              <Input placeholder="Suche Kontonummer oder Bezeichnung..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
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
          <DataTable data={mockKonten} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
