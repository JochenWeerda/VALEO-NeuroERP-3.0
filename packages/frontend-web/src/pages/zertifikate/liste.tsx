import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, Award, FileDown, Plus, Search } from 'lucide-react'

type Zertifikat = {
  id: string
  art: string
  standard: string
  nummer: string
  gueltigBis: string
  audit: string
  status: 'gueltig' | 'ablaufend' | 'abgelaufen'
}

const mockZertifikate: Zertifikat[] = [
  { id: '1', art: 'Bio-Zertifikat', standard: 'EU-Bio-Verordnung', nummer: 'BIO-2024-1234', gueltigBis: '2026-03-31', audit: '2025-02-15', status: 'gueltig' },
  { id: '2', art: 'QS-Zertifikat', standard: 'QS Qualität & Sicherheit', nummer: 'QS-2024-5678', gueltigBis: '2025-12-31', audit: '2025-11-01', status: 'gueltig' },
]

export default function ZertifikateListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const ablaufend = mockZertifikate.filter((z) => new Date(z.gueltigBis) < new Date(Date.now() + 90 * 24 * 60 * 60 * 1000) && z.status === 'gueltig').length

  const columns = [
    {
      key: 'art' as const,
      label: 'Zertifikat',
      render: (z: Zertifikat) => (
        <button onClick={() => navigate(`/zertifikate/${z.id}`)} className="font-medium text-blue-600 hover:underline">
          {z.art}
        </button>
      ),
    },
    { key: 'standard' as const, label: 'Standard' },
    { key: 'nummer' as const, label: 'Nummer', render: (z: Zertifikat) => <span className="font-mono text-sm">{z.nummer}</span> },
    {
      key: 'gueltigBis' as const,
      label: 'Gültig bis',
      render: (z: Zertifikat) => {
        const datum = new Date(z.gueltigBis)
        const ablaufend = datum < new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
        return (
          <span className={ablaufend ? 'font-semibold text-orange-600' : ''}>
            {datum.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    { key: 'audit' as const, label: 'Nächstes Audit', render: (z: Zertifikat) => new Date(z.audit).toLocaleDateString('de-DE') },
    {
      key: 'status' as const,
      label: 'Status',
      render: (z: Zertifikat) => (
        <Badge variant={z.status === 'gueltig' ? 'outline' : z.status === 'ablaufend' ? 'secondary' : 'destructive'}>
          {z.status === 'gueltig' ? 'Gültig' : z.status === 'ablaufend' ? 'Läuft ab' : 'Abgelaufen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Zertifikate</h1>
          <p className="text-muted-foreground">Zertifikat-Verwaltung</p>
        </div>
        <Button onClick={() => navigate('/zertifikate/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues Zertifikat
        </Button>
      </div>

      {ablaufend > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ablaufend} Zertifikat(e) läuft/laufen in den nächsten 90 Tagen ab!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Zertifikate Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Award className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockZertifikate.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gültig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockZertifikate.filter((z) => z.status === 'gueltig').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ablauf in 90 Tagen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{ablaufend}</span>
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
          <DataTable data={mockZertifikate} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
