import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, FileText, Plus, Search } from 'lucide-react'

type Vertrag = {
  id: string
  nummer: string
  partner: string
  typ: 'Einkauf' | 'Verkauf'
  artikel: string
  menge: number
  restmenge: number
  laufzeitBis: string
  status: 'aktiv' | 'auslaufend' | 'abgelaufen'
}

const mockVertraege: Vertrag[] = [
  { id: '1', nummer: 'RV-2025-001', partner: 'Landhandel Nord', typ: 'Verkauf', artikel: 'Weizen', menge: 500, restmenge: 120, laufzeitBis: '2026-06-30', status: 'aktiv' },
  { id: '2', nummer: 'RV-2025-002', partner: 'Müller Agrar', typ: 'Verkauf', artikel: 'Raps', menge: 300, restmenge: 45, laufzeitBis: '2025-12-31', status: 'auslaufend' },
]

export default function RahmenvertraegePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const auslaufend = mockVertraege.filter((v) => v.status === 'auslaufend').length

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Vertragsnummer',
      render: (v: Vertrag) => (
        <button onClick={() => navigate(`/vertrag/${v.id}`)} className="font-medium text-blue-600 hover:underline">
          {v.nummer}
        </button>
      ),
    },
    { key: 'partner' as const, label: 'Partner' },
    { key: 'typ' as const, label: 'Typ', render: (v: Vertrag) => <Badge variant="outline">{v.typ}</Badge> },
    { key: 'artikel' as const, label: 'Artikel' },
    {
      key: 'restmenge' as const,
      label: 'Restmenge',
      render: (v: Vertrag) => (
        <span className={v.restmenge < v.menge * 0.2 ? 'font-semibold text-orange-600' : ''}>
          {v.restmenge} / {v.menge} t
        </span>
      ),
    },
    {
      key: 'laufzeitBis' as const,
      label: 'Laufzeit bis',
      render: (v: Vertrag) => new Date(v.laufzeitBis).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (v: Vertrag) => (
        <Badge variant={v.status === 'aktiv' ? 'outline' : v.status === 'auslaufend' ? 'secondary' : 'destructive'}>
          {v.status === 'aktiv' ? 'Aktiv' : v.status === 'auslaufend' ? 'Auslaufend' : 'Abgelaufen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Rahmenverträge</h1>
          <p className="text-muted-foreground">Lieferverträge</p>
        </div>
        <Button onClick={() => navigate('/vertrag/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Vertrag
        </Button>
      </div>

      {auslaufend > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{auslaufend} Vertrag/Verträge laufen bald aus!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Verträge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockVertraege.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockVertraege.filter((v) => v.status === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auslaufend</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{auslaufend}</span>
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
          <DataTable data={mockVertraege} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
