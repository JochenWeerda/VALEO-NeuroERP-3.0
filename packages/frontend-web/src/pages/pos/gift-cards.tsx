import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, Gift, Plus, Scan } from 'lucide-react'

type GiftCard = {
  id: string
  cardNumber: string
  wert: number
  restguthaben: number
  gueltigBis: string
  ausgestelltAm: string
  kunde?: string
  status: 'aktiv' | 'teilweise-eingeloest' | 'eingeloest' | 'abgelaufen'
}

const mockGiftCards: GiftCard[] = [
  {
    id: '1',
    cardNumber: 'GC-2025-001234',
    wert: 50.00,
    restguthaben: 50.00,
    gueltigBis: '2027-10-11',
    ausgestelltAm: '2025-10-11',
    kunde: 'Maria Schmidt',
    status: 'aktiv',
  },
  {
    id: '2',
    cardNumber: 'GC-2025-001235',
    wert: 100.00,
    restguthaben: 35.50,
    gueltigBis: '2027-09-20',
    ausgestelltAm: '2025-09-20',
    kunde: 'Thomas Weber',
    status: 'teilweise-eingeloest',
  },
  {
    id: '3',
    cardNumber: 'GC-2024-000987',
    wert: 25.00,
    restguthaben: 0,
    gueltigBis: '2026-12-25',
    ausgestelltAm: '2024-12-25',
    status: 'eingeloest',
  },
]

export default function GiftCardsPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [scanMode, setScanMode] = useState(false)

  const columns = [
    {
      key: 'cardNumber' as const,
      label: 'Karten-Nummer',
      render: (gc: GiftCard) => (
        <button onClick={() => navigate(`/pos/gift-card/${gc.id}`)} className="font-mono font-bold text-blue-600 hover:underline">
          {gc.cardNumber}
        </button>
      ),
    },
    {
      key: 'wert' as const,
      label: 'Wert',
      render: (gc: GiftCard) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gc.wert),
    },
    {
      key: 'restguthaben' as const,
      label: 'Restguthaben',
      render: (gc: GiftCard) => (
        <span className={`font-bold ${gc.restguthaben === 0 ? 'text-gray-400' : 'text-green-600'}`}>
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gc.restguthaben)}
        </span>
      ),
    },
    {
      key: 'ausgestelltAm' as const,
      label: 'Ausgestellt',
      render: (gc: GiftCard) => new Date(gc.ausgestelltAm).toLocaleDateString('de-DE'),
    },
    {
      key: 'gueltigBis' as const,
      label: 'Gültig bis',
      render: (gc: GiftCard) => {
        const ablauf = new Date(gc.gueltigBis)
        const bald = ablauf <= new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
        return (
          <span className={bald ? 'font-semibold text-orange-600' : ''}>
            {ablauf.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    { key: 'kunde' as const, label: 'Kunde', render: (gc: GiftCard) => gc.kunde || <span className="text-muted-foreground">–</span> },
    {
      key: 'status' as const,
      label: 'Status',
      render: (gc: GiftCard) => (
        <Badge
          variant={
            gc.status === 'aktiv'
              ? 'outline'
              : gc.status === 'teilweise-eingeloest'
              ? 'secondary'
              : gc.status === 'eingeloest'
              ? 'default'
              : 'destructive'
          }
        >
          {gc.status === 'aktiv'
            ? 'Aktiv'
            : gc.status === 'teilweise-eingeloest'
            ? 'Teilweise eingelöst'
            : gc.status === 'eingeloest'
            ? 'Eingelöst'
            : 'Abgelaufen'}
        </Badge>
      ),
    },
  ]

  const ablaufend = mockGiftCards.filter((gc) => {
    const ablauf = new Date(gc.gueltigBis)
    return ablauf <= new Date(Date.now() + 90 * 24 * 60 * 60 * 1000) && gc.restguthaben > 0
  }).length

  const gesamtWert = mockGiftCards.reduce((sum, gc) => sum + gc.wert, 0)
  const gesamtGuthaben = mockGiftCards.reduce((sum, gc) => sum + gc.restguthaben, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Gift className="h-10 w-10 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Geschenkkarten</h1>
            <p className="text-muted-foreground">Gift Cards Verwaltung</p>
          </div>
        </div>
        <Button onClick={() => navigate('/pos/gift-card-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Geschenkkarte
        </Button>
      </div>

      {ablaufend > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ablaufend} Geschenkkarte(n) laufen in 3 Monaten ab!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
        <div className="flex items-center gap-2">
          <Gift className="h-4 w-4" />
          <p className="font-semibold">Gift Cards als Zahlungsmittel</p>
        </div>
        <p className="mt-1">
          Im POS-Terminal scannen → Automatische Einlösung • Restguthaben bleibt auf Karte • Gültigkeit: 3 Jahre ab Ausstellung
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gift Cards Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockGiftCards.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ausgestellter Wert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtWert)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offenes Guthaben</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtGuthaben)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktive Karten</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockGiftCards.filter((gc) => gc.status === 'aktiv' || gc.status === 'teilweise-eingeloest').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Schnellsuche (für POS)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Scan className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Karten-Nummer scannen oder eingeben..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 font-mono"
                autoFocus={scanMode}
              />
            </div>
            <Button variant="outline" onClick={() => setScanMode(!scanMode)}>
              {scanMode ? 'Scanner Aktiv' : 'Scanner Inaktiv'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockGiftCards} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
