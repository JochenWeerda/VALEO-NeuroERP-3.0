import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Building2, FileDown, Plus, Search } from 'lucide-react'

type Anlage = {
  id: string
  anlagennr: string
  bezeichnung: string
  anschaffung: string
  anschaffungswert: number
  nutzungsdauer: number
  afaSatz: number
  kumulierteAfa: number
  buchwert: number
}

const mockAnlagen: Anlage[] = [
  { id: '1', anlagennr: 'ANL-001', bezeichnung: 'Mähdrescher Claas Lexion 770', anschaffung: '2022-04-15', anschaffungswert: 420000, nutzungsdauer: 10, afaSatz: 10, kumulierteAfa: 126000, buchwert: 294000 },
  { id: '2', anlagennr: 'ANL-012', bezeichnung: 'Traktor John Deere 6210R', anschaffung: '2020-06-20', anschaffungswert: 185000, nutzungsdauer: 12, afaSatz: 8.33, kumulierteAfa: 92500, buchwert: 92500 },
  { id: '3', anlagennr: 'ANL-024', bezeichnung: 'Lagerhalle (Neubau)', anschaffung: '2018-09-10', anschaffungswert: 850000, nutzungsdauer: 33, afaSatz: 3.03, kumulierteAfa: 180000, buchwert: 670000 },
]

export default function AnlagenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'anlagennr' as const,
      label: 'Anlagen-Nr',
      render: (a: Anlage) => (
        <button onClick={() => navigate(`/fibu/anlage/${a.id}`)} className="font-medium text-blue-600 hover:underline font-mono">
          {a.anlagennr}
        </button>
      ),
    },
    { key: 'bezeichnung' as const, label: 'Bezeichnung', render: (a: Anlage) => <span className="font-semibold">{a.bezeichnung}</span> },
    { key: 'anschaffung' as const, label: 'Anschaffung', render: (a: Anlage) => new Date(a.anschaffung).toLocaleDateString('de-DE') },
    {
      key: 'anschaffungswert' as const,
      label: 'AK',
      render: (a: Anlage) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(a.anschaffungswert),
    },
    {
      key: 'afaSatz' as const,
      label: 'AfA',
      render: (a: Anlage) => <Badge variant="outline">{a.afaSatz}%</Badge>,
    },
    {
      key: 'kumulierteAfa' as const,
      label: 'Kum. AfA',
      render: (a: Anlage) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(a.kumulierteAfa),
    },
    {
      key: 'buchwert' as const,
      label: 'Buchwert',
      render: (a: Anlage) => (
        <span className="font-bold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(a.buchwert)}
        </span>
      ),
    },
  ]

  const gesamtAK = mockAnlagen.reduce((sum, a) => sum + a.anschaffungswert, 0)
  const gesamtBuchwert = mockAnlagen.reduce((sum, a) => sum + a.buchwert, 0)
  const gesamtAfa = mockAnlagen.reduce((sum, a) => sum + a.kumulierteAfa, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Anlagenbuchhaltung</h1>
          <p className="text-muted-foreground">AfA-Verwaltung & Anlagevermögen</p>
        </div>
        <Button onClick={() => navigate('/fibu/anlage/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Anlage
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Anlagen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockAnlagen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Anschaffungskosten</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtAK)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kumulierte AfA</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtAfa)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Buchwert Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtBuchwert)}
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
              AfA-Liste Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockAnlagen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
