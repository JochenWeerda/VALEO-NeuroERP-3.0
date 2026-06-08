import { useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { useTSEJournal, type TSEEintrag } from '@/lib/api/pos'
import { useToast } from '@/hooks/use-toast'
import { api } from '@/lib/axios'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, CheckCircle, FileDown, Search, XCircle } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

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

export default function TSEJournalPage(): JSX.Element {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [nurOffene, setNurOffene] = useState(false)
  const { data: apiTse = [], isError, error, refetch } = useTSEJournal()
  const tseTransaktionen: TSETransaction[] = apiTse.map((t: TSEEintrag) => ({
    id: t.id,
    datum: t.zeitstempel,
    bonnummer: t.transaktionsNr,
    tseTransactionNumber: Number(t.transaktionsNr.replace(/\D/g, '')) || 0,
    tseSignature: t.signatur,
    betrag: t.betrag,
    zahlungsart: 'bar',
    fibuStatus: t.status === 'ok' ? 'gebucht' : 'offen',
    fibuDatum: t.status === 'ok' ? t.zeitstempel.slice(0, 10) : undefined,
    fibuBelegnr: t.status === 'ok' ? t.transaktionsNr : undefined,
  }))

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

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

  const offen = tseTransaktionen.filter((t) => t.fibuStatus === 'offen').length
  const gesamtBetrag = tseTransaktionen.reduce((sum, t) => sum + t.betrag, 0)
  const offenerBetrag = tseTransaktionen.filter((t) => t.fibuStatus === 'offen').reduce((sum, t) => sum + t.betrag, 0)

  const displayedData = nurOffene ? tseTransaktionen.filter((t) => t.fibuStatus === 'offen') : tseTransaktionen
  const filteredBySearch =
    searchTerm.trim() === ''
      ? displayedData
      : displayedData.filter(
          (t) =>
            t.bonnummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
            String(t.tseTransactionNumber).includes(searchTerm)
        )

  const handleDSFinVExport = async () => {
    try {
      const res = await api.get('/api/v1/pos/tse-journal/export/dsfinvk', { responseType: 'blob' })
      const blob = res.data as Blob
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `DSFinV-K_${new Date().toISOString().slice(0, 10)}.csv`
      a.click()
      URL.revokeObjectURL(url)
      toast({ title: 'DSFinV-K Export', description: 'Download gestartet.' })
    } catch {
      // Fallback: CSV aus aktuellen Transaktionen (DSFinV-K Format Platzhalter)
      const header = 'Datum;Bon-Nr;TSE-Nr;Betrag;Zahlungsart;Fibu-Status;Fibu-Datum;Belegnr\n'
      const rows = displayedData.map((t) =>
        [t.datum, t.bonnummer, t.tseTransactionNumber, t.betrag.toFixed(2), t.zahlungsart, t.fibuStatus, t.fibuDatum ?? '', t.fibuBelegnr ?? ''].join(';')
      )
      const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `DSFinV-K_${new Date().toISOString().slice(0, 10)}.csv`
      a.click()
      URL.revokeObjectURL(url)
      toast({ title: 'DSFinV-K Export', description: 'CSV-Download (aktuelle Ansicht).' })
    }
  }

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
        <p className="mt-1 text-xs font-medium">POS-Umsätze werden als B2C-Endpreise inkl. gesetzl. MwSt. protokolliert.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Transaktionen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{tseTransaktionen.length}</span>
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
            <Button variant="outline" className="gap-2" onClick={handleDSFinVExport}>
              <FileDown className="h-4 w-4" />
              DSFinV-K Export
            </Button>
            <Button variant="outline" onClick={() => setNurOffene((v) => !v)}>
              {nurOffene ? 'Alle anzeigen' : 'Nur Offene'}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredBySearch} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
