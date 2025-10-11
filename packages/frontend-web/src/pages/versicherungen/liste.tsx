import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, Plus, Search, Shield } from 'lucide-react'

type Versicherung = {
  id: string
  art: string
  versicherer: string
  vertragsnummer: string
  praemie: number
  ablauf: string
  status: 'aktiv' | 'kuendigung'
}

const mockVersicherungen: Versicherung[] = [
  { id: '1', art: 'Betriebshaftpflicht', versicherer: 'R+V Versicherung', vertragsnummer: 'RV-2024-1234', praemie: 3200, ablauf: '2025-12-31', status: 'aktiv' },
  { id: '2', art: 'Hagelversicherung', versicherer: 'Vereinigte Hagel', vertragsnummer: 'VH-2024-5678', praemie: 8500, ablauf: '2025-06-30', status: 'aktiv' },
]

export default function VersicherungenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const ablaufBald = mockVersicherungen.filter((v) => new Date(v.ablauf) < new Date(Date.now() + 60 * 24 * 60 * 60 * 1000)).length

  const columns = [
    {
      key: 'art' as const,
      label: 'Art',
      render: (v: Versicherung) => (
        <button onClick={() => navigate(`/versicherungen/${v.id}`)} className="font-medium text-blue-600 hover:underline">
          {v.art}
        </button>
      ),
    },
    { key: 'versicherer' as const, label: 'Versicherer' },
    { key: 'vertragsnummer' as const, label: 'Vertragsnummer', render: (v: Versicherung) => <span className="font-mono text-sm">{v.vertragsnummer}</span> },
    {
      key: 'praemie' as const,
      label: 'Prämie (jährl.)',
      render: (v: Versicherung) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(v.praemie),
    },
    {
      key: 'ablauf' as const,
      label: 'Ablauf',
      render: (v: Versicherung) => {
        const datum = new Date(v.ablauf)
        const bald = datum < new Date(Date.now() + 60 * 24 * 60 * 60 * 1000)
        return (
          <span className={bald ? 'font-semibold text-orange-600' : ''}>
            {datum.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (v: Versicherung) => (
        <Badge variant={v.status === 'aktiv' ? 'outline' : 'secondary'}>
          {v.status === 'aktiv' ? 'Aktiv' : 'Kündigung'}
        </Badge>
      ),
    },
  ]

  const gesamtPraemie = mockVersicherungen.reduce((sum, v) => sum + v.praemie, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Versicherungen</h1>
          <p className="text-muted-foreground">Versicherungs-Verwaltung</p>
        </div>
        <Button onClick={() => navigate('/versicherungen/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Versicherung
        </Button>
      </div>

      {ablaufBald > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ablaufBald} Versicherung(en) läuft/laufen in den nächsten 60 Tagen ab!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Versicherungen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockVersicherungen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt-Prämie (jährl.)</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtPraemie)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ablauf in 60 Tagen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{ablaufBald}</span>
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
          <DataTable data={mockVersicherungen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
