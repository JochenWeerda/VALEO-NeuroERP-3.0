import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileText, Plus, Search, Shield } from 'lucide-react'

type Sicherheit = {
  id: string
  typ: 'abtretung' | 'sicherungseigentum' | 'buergschaft' | 'pfandrecht'
  kunde: string
  kundennr: string
  gegenstand: string
  wert: number
  datumErstellung: string
  gueltigBis?: string
  status: 'aktiv' | 'abgelaufen' | 'freigegeben'
  kreditlinie: number
  ausgenutzt: number
}

const mockSicherheiten: Sicherheit[] = [
  {
    id: '1',
    typ: 'abtretung',
    kunde: 'Agrar Schmidt GmbH',
    kundennr: 'K-10023',
    gegenstand: 'Forderungsabtretung Ernteerlöse 2025',
    wert: 150000,
    datumErstellung: '2025-01-15',
    gueltigBis: '2025-12-31',
    status: 'aktiv',
    kreditlinie: 200000,
    ausgenutzt: 85000,
  },
  {
    id: '2',
    typ: 'sicherungseigentum',
    kunde: 'Landwirtschaft Müller',
    kundennr: '10045',
    gegenstand: 'Sicherungsübereignung Mähdrescher Claas Lexion 780',
    wert: 450000,
    datumErstellung: '2024-06-20',
    status: 'aktiv',
    kreditlinie: 250000,
    ausgenutzt: 120000,
  },
  {
    id: '3',
    typ: 'buergschaft',
    kunde: 'Hofgut Weber',
    kundennr: 'K-10067',
    gegenstand: 'Bürgschaft Volksbank Rotenburg',
    wert: 100000,
    datumErstellung: '2024-03-10',
    gueltigBis: '2026-03-10',
    status: 'aktiv',
    kreditlinie: 100000,
    ausgenutzt: 45000,
  },
]

export default function SicherheitenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (s: Sicherheit) => {
        const labels = {
          abtretung: 'Abtretung',
          sicherungseigentum: 'Sicherungsübereignung',
          buergschaft: 'Bürgschaft',
          pfandrecht: 'Pfandrecht',
        }
        return <Badge variant="outline">{labels[s.typ]}</Badge>
      },
    },
    {
      key: 'kunde' as const,
      label: 'Kunde',
      render: (s: Sicherheit) => (
        <button onClick={() => navigate(`/verkauf/kunden-stamm/${s.id}`)} className="font-medium text-blue-600 hover:underline">
          {s.kunde}
        </button>
      ),
    },
    { key: 'kundennr' as const, label: 'Kd-Nr', render: (s: Sicherheit) => <span className="font-mono text-sm">{s.kundennr}</span> },
    { key: 'gegenstand' as const, label: 'Gegenstand' },
    {
      key: 'wert' as const,
      label: 'Sicherheitenwert',
      render: (s: Sicherheit) => (
        <span className="font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(s.wert)}</span>
      ),
    },
    {
      key: 'kreditlinie' as const,
      label: 'Kreditlinie',
      render: (s: Sicherheit) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(s.kreditlinie),
    },
    {
      key: 'ausgenutzt' as const,
      label: 'Ausgenutzt',
      render: (s: Sicherheit) => {
        const prozent = (s.ausgenutzt / s.kreditlinie) * 100
        return (
          <div className="space-y-1">
            <div className="font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(s.ausgenutzt)}</div>
            <div className="h-1.5 w-24 bg-gray-200 rounded-full overflow-hidden">
              <div className={`h-full ${prozent > 80 ? 'bg-red-500' : prozent > 60 ? 'bg-orange-500' : 'bg-green-500'}`} style={{ width: `${prozent}%` }} />
            </div>
            <div className="text-xs text-muted-foreground">{prozent.toFixed(0)}%</div>
          </div>
        )
      },
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Sicherheit) => (
        <Badge variant={s.status === 'aktiv' ? 'outline' : s.status === 'abgelaufen' ? 'destructive' : 'secondary'}>
          {s.status === 'aktiv' ? 'Aktiv' : s.status === 'abgelaufen' ? 'Abgelaufen' : 'Freigegeben'}
        </Badge>
      ),
    },
  ]

  const gesamtwert = mockSicherheiten.reduce((sum, s) => sum + s.wert, 0)
  const gesamtKreditlinie = mockSicherheiten.reduce((sum, s) => sum + s.kreditlinie, 0)
  const gesamtAusgenutzt = mockSicherheiten.reduce((sum, s) => sum + s.ausgenutzt, 0)
  const auslastung = (gesamtAusgenutzt / gesamtKreditlinie) * 100

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="h-10 w-10 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Sicherheiten-Verwaltung</h1>
            <p className="text-muted-foreground">Abtretungen, Sicherungsübereignungen & Bürgschaften</p>
          </div>
        </div>
        <Button onClick={() => navigate('/fibu/sicherheit-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Sicherheit
        </Button>
      </div>

      {auslastung > 80 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">Kreditlinie zu {auslastung.toFixed(0)}% ausgelastet!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          <p className="font-semibold">Rechtliche Sicherheiten bei Warenkrediten</p>
        </div>
        <p className="mt-1">
          <strong>Abtretung:</strong> Forderungsabtretung (§§ 398 ff. BGB) • <strong>Sicherungsübereignung:</strong> Eigentum an Sache (§ 930 BGB) • <strong>Bürgschaft:</strong> §§ 765 ff. BGB
        </p>
        <p className="mt-1 text-xs">Automatische Bonitätsprüfung bei Überschreitung 80% der Kreditlinie</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Sicherheiten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockSicherheiten.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Sicherheitenwert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtwert)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kreditlinie Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtKreditlinie)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auslastung</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold ${auslastung > 80 ? 'text-red-600' : auslastung > 60 ? 'text-orange-600' : 'text-green-600'}`}>
                {auslastung.toFixed(0)}%
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Kunde oder Gegenstand..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline">Nur Aktive</Button>
            <Button variant="outline">Nur Überlastet (&gt;80%)</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockSicherheiten} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
