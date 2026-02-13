import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { BookOpen, FileDown, Loader2, Search } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { ErrorState } from '@/components/ErrorState'

type Buchung = {
  id: string
  belegnr: string
  datum: string
  sollKonto: string
  habenKonto: string
  betrag: number
  text: string
  belegart: string
}

interface JournalEntryAPI {
  id: string
  account_id: string
  description: string
  amount: number
  currency: string
  period: string
  document_id?: string
  posted_at: string
  created_by: string
}

function mapApiEntry(e: JournalEntryAPI): Buchung {
  return {
    id: e.id,
    belegnr: e.document_id || e.id,
    datum: e.posted_at?.split('T')[0] || '',
    sollKonto: e.account_id,
    habenKonto: '-',
    betrag: Math.abs(e.amount),
    text: e.description,
    belegart: e.amount >= 0 ? 'ER' : 'EB',
  }
}

export default function BuchungsjournalPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['fibu', 'journal-entries'],
    queryFn: async () => {
      const res = await apiClient.get<unknown>('/api/v1/journal-entries')
      const payload = res.data as { items?: JournalEntryAPI[] } | JournalEntryAPI[]

      if (Array.isArray(payload)) {
        return payload.map(mapApiEntry)
      }

      if (payload && typeof payload === 'object' && Array.isArray(payload.items)) {
        return payload.items.map(mapApiEntry)
      }

      throw new Error('Ungueltige Antwort fuer Journal Entries')
    },
    staleTime: 2 * 60 * 1000,
  })

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const buchungen = data ?? []

  const columns = [
    { key: 'datum' as const, label: 'Datum', render: (b: Buchung) => new Date(b.datum).toLocaleDateString('de-DE') },
    { key: 'belegnr' as const, label: 'Belegnummer', render: (b: Buchung) => <span className="font-mono font-bold">{b.belegnr}</span> },
    {
      key: 'belegart' as const,
      label: 'Art',
      render: (b: Buchung) => (
        <Badge variant="outline">
          {b.belegart === 'ER' ? 'Erloes' : b.belegart === 'EB' ? 'Eingang' : b.belegart === 'ZE' ? 'Zahlung' : b.belegart}
        </Badge>
      ),
    },
    { key: 'sollKonto' as const, label: 'Soll', render: (b: Buchung) => <span className="font-mono">{b.sollKonto}</span> },
    { key: 'habenKonto' as const, label: 'Haben', render: (b: Buchung) => <span className="font-mono">{b.habenKonto}</span> },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (b: Buchung) => (
        <span className="font-bold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(b.betrag)}
        </span>
      ),
    },
    { key: 'text' as const, label: 'Buchungstext' },
  ]

  const gesamtBetrag = buchungen.reduce((sum, b) => sum + b.betrag, 0)

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Buchungsjournal</h1>
        <p className="text-muted-foreground">Alle Buchungssaetze</p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Buchungen Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{buchungen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Summe Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtBetrag)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Periode</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">02/2026</span>
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
              <Input placeholder="Suche Belegnummer, Konto, Text..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              DATEV Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-sm text-muted-foreground">Lade Buchungen...</span>
            </div>
          ) : (
            <DataTable data={buchungen} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
