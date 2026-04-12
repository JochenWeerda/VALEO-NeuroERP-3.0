import { useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { BookOpen, FileDown, Loader2, Search, Undo2 } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { ErrorState } from '@/components/ErrorState'
import { StornoDialog } from '@/components/finance/StornoDialog'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { toast } from 'sonner'

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
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [referenceFilter, setReferenceFilter] = useState('')
  const [stornoOpen, setStornoOpen] = useState(false)
  const [stornoEntry, setStornoEntry] = useState<Buchung | null>(null)
  const [stornoLoading, setStornoLoading] = useState(false)

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['fibu', 'journal-entries', referenceFilter || null],
    queryFn: async () => {
      const params = referenceFilter.trim() ? { reference: referenceFilter.trim() } : {}
      const res = await apiClient.get<unknown>('/api/v1/journal-entries', { params })
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

  const buchungen = data ?? []
  const filteredBuchungen = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase()
    if (!needle) return buchungen
    return buchungen.filter((buchung) =>
      [buchung.belegnr, buchung.sollKonto, buchung.habenKonto, buchung.text]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(needle)),
    )
  }, [buchungen, searchTerm])

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const openStorno = (b: Buchung) => {
    setStornoEntry(b)
    setStornoOpen(true)
  }

  const handleStornoConfirm = async (reason: string) => {
    if (!stornoEntry) return
    setStornoLoading(true)
    try {
      await apiClient.post(`/api/v1/journal-entries/${stornoEntry.id}/reverse`, null, { params: { reason } })
      await queryClient.invalidateQueries({ queryKey: ['fibu', 'journal-entries'] })
      toast.success(t('crud.messages.stornoSuccess'))
      setStornoOpen(false)
      setStornoEntry(null)
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err && typeof (err as { response?: { data?: { detail?: string } } }).response?.data?.detail === 'string'
        ? (err as { response: { data: { detail: string } } }).response.data.detail
        : t('crud.messages.stornoError')
      toast.error(msg)
    } finally {
      setStornoLoading(false)
    }
  }

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
    {
      key: 'actions' as const,
      label: t('crud.fields.actions'),
      render: (b: Buchung) => (
        <Button variant="outline" size="sm" onClick={() => openStorno(b)} className="gap-1">
          <Undo2 className="h-3 w-3" />
          {t('crud.actions.reverse')}
        </Button>
      ),
    },
  ]

  const gesamtBetrag = filteredBuchungen.reduce((sum, b) => sum + b.betrag, 0)
  const stornoFaelle = filteredBuchungen.filter((b) => b.belegart === 'EB').length
  const operationalStatus = normalizeOperationalStatus(
    stornoFaelle > 0 ? 'wartet_auf_mensch' : filteredBuchungen.length > 0 ? 'in_pruefung' : 'offen',
  )
  const contextSections = [
    {
      title: 'Revisionslage',
      items: [
        { label: 'Journalbuchungen', value: `${filteredBuchungen.length}` },
        { label: 'Referenzfilter', value: referenceFilter.trim() || 'Keine Einschraenkung' },
        { label: 'Stornorelevante Saetze', value: `${stornoFaelle}` },
      ],
    },
    {
      title: 'Folgepfad',
      items: [
        { label: 'Periode', value: filteredBuchungen[0]?.datum?.slice(0, 7) || 'Keine Periode aktiv' },
        { label: 'Naechste Aktion', value: stornoFaelle > 0 ? 'Storno- und Referenzpfad pruefen' : 'Export oder Drilldown in Buchungsuebergabe' },
        { label: 'Buchungswert', value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtBetrag) },
      ],
    },
  ]
  const timelineItems = [
    {
      label: referenceFilter.trim() ? 'Journal auf Referenz eingeschraenkt' : 'Gesamtjournal aktiv',
      detail: referenceFilter.trim()
        ? `Aktiver Filter fuer Referenz oder Importlauf: ${referenceFilter.trim()}.`
        : 'Es wird die ungefilterte Journalsicht des aktuellen Arbeitsraums gezeigt.',
    },
    {
      label: stornoFaelle > 0 ? 'Ruecknahmefaehige Saetze vorhanden' : 'Keine akute Ruecknahme markiert',
      detail: stornoFaelle > 0
        ? `${stornoFaelle} Eingangssaetze sollten vor Export und Periodenabschluss geprueft werden.`
        : 'Es liegt kein akuter Storno-Hinweis aus dem aktuellen Ausschnitt vor.',
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div>
        <h1 className="text-3xl font-bold">Buchungsjournal</h1>
        <p className="text-muted-foreground">Alle Buchungssaetze</p>
      </div>

      <OperationalCaseHeader
        title="Buchungsjournal"
        description="Journalsaetze werden als Revisions- und Exportfall gefuehrt, damit Perioden- und Referenzdruck sichtbar bleiben."
        status={operationalStatus}
        owner="Finanzbuchhaltung"
        blocker={stornoFaelle > 0 ? `${stornoFaelle} Saetze sollten vor dem Export rueckgeprueft werden.` : null}
        nextAction={stornoFaelle > 0 ? 'Stornofaehige Saetze klaeren oder ruecknehmen' : 'Buchungsuebergabe und Periodenlage abstimmen'}
        caseLabel="Vorgang: Journal"
        tags={['FIBU', 'Revision', 'L3']}
      />
      <div className="grid gap-4 xl:grid-cols-[minmax(0,2fr)_360px]">
        <OperationalTimeline title="Journalverlauf" items={timelineItems} />
        <OperationalContextPanel title="Journalkontext" sections={contextSections} />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Buchungen Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{filteredBuchungen.length}</span>
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
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Belegnummer, Konto, Text..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <div className="flex items-center gap-2 sm:w-64">
              <label htmlFor="ref-filter" className="shrink-0 text-sm text-muted-foreground">Referenz / Importlauf</label>
              <Input
                id="ref-filter"
                placeholder="z. B. run_id"
                value={referenceFilter}
                onChange={(e) => setReferenceFilter(e.target.value)}
                className="font-mono text-sm"
              />
            </div>
            <Button variant="outline" className="gap-2" onClick={() => navigate('/fibu/schnittstelle-fibu?context=journal')}>
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
            <DataTable data={filteredBuchungen} columns={columns} />
          )}
        </CardContent>
      </Card>

      <StornoDialog
        open={stornoOpen}
        onOpenChange={(open) => { if (!open) { setStornoEntry(null) } setStornoOpen(open) }}
        onConfirm={handleStornoConfirm}
        entryNumber={stornoEntry?.belegnr}
        entryDate={stornoEntry?.datum}
        isLoading={stornoLoading}
      />
    </div>
  )
}
