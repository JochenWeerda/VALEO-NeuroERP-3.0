import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, Package, Search } from 'lucide-react'

type Charge = {
  id: string
  chargenId: string
  artikel: string
  menge: number
  lagerort: string
  eingang: string
  status: 'freigegeben' | 'gesperrt' | 'in-pruefung'
}

const mockChargen: Charge[] = [
  { id: '1', chargenId: '251011-WEI-001', artikel: 'Weizen Premium', menge: 25.0, lagerort: 'Silo 1', eingang: '2025-10-11', status: 'freigegeben' },
  { id: '2', chargenId: '251010-RAP-002', artikel: 'Raps', menge: 18.5, lagerort: 'Silo 2', eingang: '2025-10-10', status: 'freigegeben' },
  { id: '3', chargenId: '251009-WEI-003', artikel: 'Weizen', menge: 22.0, lagerort: 'Silo 1', eingang: '2025-10-09', status: 'in-pruefung' },
]

export default function ChargenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const inPruefung = mockChargen.filter((c) => c.status === 'in-pruefung').length

  const columns = [
    {
      key: 'chargenId' as const,
      label: 'Chargen-ID',
      render: (c: Charge) => (
        <button onClick={() => navigate(`/charge/stamm/${c.id}`)} className="font-medium text-blue-600 hover:underline font-mono">
          {c.chargenId}
        </button>
      ),
    },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'menge' as const, label: 'Menge (t)', render: (c: Charge) => `${c.menge} t` },
    { key: 'lagerort' as const, label: 'Lagerort' },
    {
      key: 'eingang' as const,
      label: 'Eingang',
      render: (c: Charge) => new Date(c.eingang).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (c: Charge) => (
        <Badge variant={c.status === 'freigegeben' ? 'outline' : c.status === 'gesperrt' ? 'destructive' : 'secondary'}>
          {c.status === 'freigegeben' ? '✓ Freigegeben' : c.status === 'gesperrt' ? '✗ Gesperrt' : '⏳ In Prüfung'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Chargen</h1>
          <p className="text-muted-foreground">Chargenverwaltung</p>
        </div>
        <Button onClick={() => navigate('/charge/wareneingang')}>Wareneingang</Button>
      </div>

      {inPruefung > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{inPruefung} Charge(n) in Qualitätsprüfung</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Chargen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockChargen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Freigegeben</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockChargen.filter((c) => c.status === 'freigegeben').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Prüfung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{inPruefung}</span>
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
              <Input placeholder="Chargen-ID oder Artikel..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
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
          <DataTable data={mockChargen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
