import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, CheckCircle, FileDown, Search, XCircle } from 'lucide-react'

type TSETransaction = {
  id: string
  datum: string
  bonnummer: string
  tseTransactionNumber: number
  tseSignature: string
  betrag: number
  zahlungsart: 'bar' | 'ec' | 'paypal' | 'b2b'
  fibuStatus: 'offen' | 'gebucht' | 'exportiert'
  fibuDatum?: string
  fibuBelegnr?: string
}

const mockTSETransaktionen: TSETransaction[] = [
  {
    id: '1',
    datum: '2025-10-11 09:15:23',
    bonnummer: 'BON-2025-00123',
    tseTransactionNumber: 7843,
    tseSignature: 'TSE_SIG_1728640523',
    betrag: 45.97,
    zahlungsart: 'bar',
    fibuStatus: 'gebucht',
    fibuDatum: '2025-10-11',
    fibuBelegnr: 'KA-2025-10-11',
  },
  {
    id: '2',
    datum: '2025-10-11 10:42:11',
    bonnummer: 'BON-2025-00124',
    tseTransactionNumber: 7844,
    tseSignature: 'TSE_SIG_1728645731',
    betrag: 128.50,
    zahlungsart: 'ec',
    fibuStatus: 'gebucht',
    fibuDatum: '2025-10-11',
    fibuBelegnr: 'KA-2025-10-11',
  },
  {
    id: '3',
    datum: '2025-10-11 14:20:45',
    bonnummer: 'BON-2025-00125',
    tseTransactionNumber: 7845,
    tseSignature: 'TSE_SIG_1728659245',
    betrag: 89.99,
    zahlungsart: 'bar',
    fibuStatus: 'offen',
  },
]

export default function TSEJournalPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'datum' as const,
      label: 'Datum/Zeit',
      render: (t: TSETransaction) => (
        <div>
          <div className="font-semibold">{new Date(t.datum).toLocaleDateString('de-DE')}</div>
          <div className="text-xs text-muted-foreground">{new Date(t.datum).toLocaleTimeString('de-DE')}</div>
        </div>
      ),
    },
    { key: 'bonnummer' as const, label: 'Bon-Nr', render: (t: TSETransaction) => <span className="font-mono text-sm">{t.bonnummer}</span> },
    {
      key: 'tseTransactionNumber' as const,
      label: 'TSE-Nr',
      render: (t: TSETransaction) => <span className="font-mono font-bold">{t.tseTransactionNumber}</span>,
    },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (t: TSETransaction) => (
        <span className="font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(t.betrag)}</span>
      ),
    },
    {
      key: 'zahlungsart' as const,
      label: 'Zahlungsart',
      render: (t: TSETransaction) => {
        const labels = { bar: 'Bar', ec: 'EC-Karte', paypal: 'PayPal', b2b: 'B2B-Beleg' }
        return <Badge variant="outline">{labels[t.zahlungsart]}</Badge>
      },
    },
    {
      key: 'fibuStatus' as const,
      label: 'Fibu-Status',
      render: (t: TSETransaction) => (
        <div className="flex items-center gap-2">
          {t.fibuStatus === 'gebucht' ? (
            <CheckCircle className="h-4 w-4 text-green-600" />
          ) : t.fibuStatus === 'exportiert' ? (
            <FileDown className="h-4 w-4 text-blue-600" />
          ) : (
            <XCircle className="h-4 w-4 text-orange-600" />
          )}
          <Badge variant={t.fibuStatus === 'gebucht' ? 'outline' : t.fibuStatus === 'exportiert' ? 'secondary' : 'default'}>
            {t.fibuStatus === 'gebucht' ? 'Gebucht' : t.fibuStatus === 'exportiert' ? 'Exportiert' : 'Offen'}
          </Badge>
        </div>
      ),
    },
    {
      key: 'fibuDatum' as const,
      label: 'Fibu-Datum',
      render: (t: TSETransaction) =>
        t.fibuDatum ? (
          <div>
            <div className="font-semibold">{new Date(t.fibuDatum).toLocaleDateString('de-DE')}</div>
            <div className="text-xs text-muted-foreground font-mono">{t.fibuBelegnr}</div>
          </div>
        ) : (
          <span className="text-muted-foreground">–</span>
        ),
    },
  ]

  const offen = mockTSETransaktionen.filter((t) => t.fibuStatus === 'offen').length
  const gesamtBetrag = mockTSETransaktionen.reduce((sum, t) => sum + t.betrag, 0)
  const offenerBetrag = mockTSETransaktionen.filter((t) => t.fibuStatus === 'offen').reduce((sum, t) => sum + t.betrag, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">TSE-Journal</h1>
          <p className="text-muted-foreground">Kassensicherungsverordnung - Transaktionsprotokoll</p>
        </div>
        <Button onClick={() => navigate('/pos/tagesabschluss')} className="gap-2">
          Tagesabschluss
        </Button>
      </div>

      {offen > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{offen} Transaktion(en) noch nicht in Fibu gebucht!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
        <p className="font-semibold">🔐 TSE-Pflicht (KassenSichV)</p>
        <p className="mt-1">
          Alle Kassentransaktionen mit zertifizierter TSE signiert • Unveränderbar • 10 Jahre Aufbewahrungspflicht •
          DSFinV-K Export für DATEV/Finanzamt
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Transaktionen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockTSETransaktionen.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Umsatz Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtBetrag)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Noch nicht gebucht</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{offen}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offener Betrag</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(offenerBetrag)}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Export</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Bon-Nr oder TSE-Nr..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              DSFinV-K Export
            </Button>
            <Button variant="outline">Nur Offene</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockTSETransaktionen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
