import { useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { useTranslation } from 'react-i18next'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle, Euro, FileDown, Loader2, Search } from 'lucide-react'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { apiClient } from '@/lib/api-client'
import { exportToCSV } from '@/lib/export-utils'
import { useToast } from '@/hooks/use-toast'
import { ErrorState } from '@/components/ErrorState'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type OffenerPosten = {
  id: string
  rechnungsNr: string
  kunde: string
  rechnungsDatum: string
  faelligAm: string
  betrag: number
  offen: number
  tageUeberfaellig: number
  mahnstufe: 0 | 1 | 2 | 3
  status: 'faellig' | 'ueberfaellig' | 'mahnung1' | 'mahnung2' | 'mahnung3' | 'inkasso'
}

interface OpenItemAPI {
  id: string
  konto_nr?: string
  konto_name?: string
  konto_typ: 'debitoren' | 'kreditoren'
  op_status: 'offen' | 'teilweise' | 'geschlossen' | 'storniert'
  rechnungsnr: string
  rechnungsdatum: string
  faelligkeit: string
  valuta?: string
  op_betrag: number
  offen: number
  saldo?: number
  op_text?: string
  kunde_id?: string
  kunde_name?: string
  kredit_limit?: number
  kv_limit?: number
  sperre_grund?: string
  letzte_bewegung_am?: string
}

function deriveStatus(dueDate: string): { tageUeberfaellig: number; mahnstufe: 0 | 1 | 2 | 3; status: OffenerPosten['status'] } {
  const due = new Date(dueDate)
  const today = new Date()
  const diff = Math.floor((today.getTime() - due.getTime()) / (1000 * 60 * 60 * 24))
  if (diff <= 0) return { tageUeberfaellig: 0, mahnstufe: 0, status: 'faellig' }
  if (diff <= 14) return { tageUeberfaellig: diff, mahnstufe: 1, status: 'mahnung1' }
  if (diff <= 30) return { tageUeberfaellig: diff, mahnstufe: 2, status: 'mahnung2' }
  if (diff <= 60) return { tageUeberfaellig: diff, mahnstufe: 3, status: 'mahnung3' }
  return { tageUeberfaellig: diff, mahnstufe: 3, status: 'inkasso' }
}

function mapApiItem(item: OpenItemAPI): OffenerPosten {
  const { tageUeberfaellig, mahnstufe, status } = deriveStatus(item.faelligkeit)
  return {
    id: item.id,
    rechnungsNr: item.rechnungsnr,
    kunde: item.kunde_name ?? item.konto_name ?? '-',
    rechnungsDatum: item.rechnungsdatum,
    faelligAm: item.faelligkeit,
    betrag: item.op_betrag,
    offen: item.offen,
    tageUeberfaellig,
    mahnstufe,
    status,
  }
}

const statusVariantMap: Record<
  OffenerPosten['status'],
  'default' | 'outline' | 'secondary' | 'destructive'
> = {
  faellig: 'default',
  ueberfaellig: 'secondary',
  mahnung1: 'secondary',
  mahnung2: 'destructive',
  mahnung3: 'destructive',
  inkasso: 'destructive',
}


export default function OffenePostenPage(): JSX.Element {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<OffenerPosten['status'] | 'alle'>('alle')
  const [editingId, setEditingId] = useState<string | null>(null)

  const handleExport = (): void => {
    try {
      exportToCSV(
        filteredPosten,
        `offene-posten-${new Date().toISOString().slice(0, 10)}.csv`,
        [
          { key: 'rechnungsNr', label: 'Rechnungs-Nr' },
          { key: 'kunde', label: 'Kunde' },
          { key: 'rechnungsDatum', label: 'Rechnungsdatum' },
          { key: 'faelligAm', label: 'Fällig am' },
          { key: 'betrag', label: 'Betrag' },
          { key: 'offen', label: 'Offen' },
          { key: 'status', label: 'Status' },
        ]
      )
      toast({ title: 'Export', description: `${filteredPosten.length} offene Posten exportiert.` })
    } catch (e) {
      toast({ title: 'Export fehlgeschlagen', description: String(e), variant: 'destructive' })
    }
  }
  const [form, setForm] = useState({
    rechnungsnr: '',
    konto_nr: '',
    konto_name: '',
    kunde_name: '',
    rechnungsdatum: new Date().toISOString().slice(0, 10),
    faelligkeit: new Date().toISOString().slice(0, 10),
    op_betrag: 0,
    offen: 0,
    op_text: '',
  })

  const { data: allePosten = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ['fibu', 'open-items'],
    queryFn: async () => {
      const res = await apiClient.get<{ items: OpenItemAPI[] }>('/api/v1/finance/open-items')
      if (!res.data?.items) {
        throw new Error('Ungültige Antwort für offene Posten')
      }
      return res.data.items.map(mapApiItem)
    },
    staleTime: 2 * 60 * 1000,
  })

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        konto_nr: form.konto_nr || null,
        konto_name: form.konto_name || null,
        konto_typ: 'debitoren',
        op_status: 'offen',
        rechnungsnr: form.rechnungsnr,
        rechnungsdatum: form.rechnungsdatum,
        faelligkeit: form.faelligkeit,
        valuta: form.rechnungsdatum,
        op_betrag: Number(form.op_betrag || 0),
        saldo: 0,
        offen: Number(form.offen || form.op_betrag || 0),
        op_text: form.op_text || null,
        waehrung: 'EUR',
        kunde_id: null,
        kunde_name: form.kunde_name || null,
        lieferant_id: null,
        lieferant_name: null,
        skonto_prozent: null,
        skonto_bis: null,
        mahn_stufe: 0,
        zahlbar: true,
        letzte_bewegung_am: null,
        kredit_limit: null,
        kv_limit: null,
        sperre_grund: null,
      }
      if (editingId) {
        await apiClient.put(`/api/v1/finance/open-items/${editingId}`, payload)
      } else {
        await apiClient.post('/api/v1/finance/open-items', payload)
      }
    },
    onSuccess: () => {
      setEditingId(null)
      setForm({
        rechnungsnr: '',
        konto_nr: '',
        konto_name: '',
        kunde_name: '',
        rechnungsdatum: new Date().toISOString().slice(0, 10),
        faelligkeit: new Date().toISOString().slice(0, 10),
        op_betrag: 0,
        offen: 0,
        op_text: '',
      })
      void refetch()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/v1/finance/open-items/${id}`)
    },
    onSuccess: () => {
      void refetch()
    },
  })

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const filteredPosten = allePosten.filter((posten) => {
    const matchesSearch =
      posten.rechnungsNr.toLowerCase().includes(searchTerm.toLowerCase()) ||
      posten.kunde.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || posten.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const gesamtOffen = filteredPosten.reduce((sum, p) => sum + p.offen, 0)
  const ueberfaellig = filteredPosten.filter((p) => p.tageUeberfaellig > 0)
  const operationalStatus = normalizeOperationalStatus(
    ueberfaellig.length > 0 ? (ueberfaellig.some((item) => item.tageUeberfaellig > 30) ? 'eskaliert' : 'wartet_auf_mensch') : 'in_pruefung'
  )
  const contextSections = [
    {
      title: 'Vorgang',
      items: [
        { label: 'Posten gesamt', value: String(allePosten.length) },
        { label: 'Gefiltert', value: String(filteredPosten.length) },
        { label: 'Ueberfaellig', value: String(ueberfaellig.length) },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        {
          label: 'Gesamt offen',
          value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtOffen),
        },
        {
          label: 'Kritisch ueberfaellig',
          value: `${ueberfaellig.filter((item) => item.tageUeberfaellig > 30).length} Posten`,
        },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: ueberfaellig.length > 0 ? 'Mahnlauf oder Bearbeitung starten' : 'Offene Posten pruefen' },
        { label: 'Blocker', value: editingId ? 'Datensatz wird bearbeitet' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'OP-Liste geladen', detail: `${allePosten.length} Posten verfuegbar` },
    ueberfaellig.length > 0 ? { label: 'Mahnfaellige Posten erkannt', detail: `${ueberfaellig.length} Position(en)` } : null,
    editingId ? { label: 'Bearbeitung aktiv', detail: `Posten ${editingId} wird angepasst` } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  const columns = [
    {
      key: 'rechnungsNr' as const,
      label: 'Rechnung',
      render: (posten: OffenerPosten) => (
        <button
          onClick={() => navigate(`/sales/invoice-editor?id=${posten.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {posten.rechnungsNr}
        </button>
      ),
    },
    {
      key: 'kunde' as const,
      label: 'Kunde',
    },
    {
      key: 'rechnungsDatum' as const,
      label: 'Rechnungsdatum',
      render: (posten: OffenerPosten) => new Date(posten.rechnungsDatum).toLocaleDateString('de-DE'),
    },
    {
      key: 'faelligAm' as const,
      label: 'Fällig am',
      render: (posten: OffenerPosten) => {
        const faellig = new Date(posten.faelligAm)
        const heute = new Date()
        const isUeberfaellig = faellig < heute
        return (
          <span className={isUeberfaellig ? 'font-semibold text-red-600' : ''}>
            {faellig.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'offen' as const,
      label: 'Offener Betrag',
      render: (posten: OffenerPosten) => (
        <span className="font-semibold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(posten.offen)}
        </span>
      ),
    },
    {
      key: 'tageUeberfaellig' as const,
      label: 'Tage überfällig',
      render: (posten: OffenerPosten) =>
        posten.tageUeberfaellig > 0 ? (
          <span className="flex items-center gap-1 text-red-600">
            <AlertCircle className="h-4 w-4" />
            {posten.tageUeberfaellig} Tage
          </span>
        ) : (
          <span className="text-muted-foreground">-</span>
        ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (posten: OffenerPosten) => (
        <Badge variant={statusVariantMap[posten.status]}>{getStatusLabel(t, posten.status, posten.status)}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <OperationalCaseHeader
        title="Offene Posten"
        description="Forderungsmanagement mit Fokus auf Faelligkeit, Mahnstufe und naechste Eskalation."
        status={operationalStatus}
        owner="Debitorenmanagement"
        blocker={ueberfaellig.length > 0 ? 'Es liegen ueberfaellige Forderungen vor.' : null}
        nextAction={ueberfaellig.length > 0 ? 'Mahnlauf anstossen oder Posten klaeren' : 'Offene Posten periodisch pruefen'}
        caseLabel="OP-Management"
        tags={['FIBU', 'Mahnwesen']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Aktuelle Lage" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Offene Posten</h1>
          <p className="text-muted-foreground">Forderungsmanagement & Mahnwesen</p>
        </div>
        <Button variant="outline" className="gap-2">
          <FileDown className="h-4 w-4" />
          Mahnlauf starten
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-muted-foreground" />
              <span className="text-2xl font-bold">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                  gesamtOffen
                )}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Überfällige Posten</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <span className="text-2xl font-bold text-red-600">{ueberfaellig.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ø Überfällig</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {ueberfaellig.length > 0
                ? Math.round(
                    ueberfaellig.reduce((sum, p) => sum + p.tageUeberfaellig, 0) / ueberfaellig.length
                  )
                : 0}{' '}
              Tage
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filter & Suche</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-3 md:grid-cols-5">
            <Input placeholder="Rechnungs-Nr." value={form.rechnungsnr} onChange={(e) => setForm((p) => ({ ...p, rechnungsnr: e.target.value }))} />
            <Input placeholder="Konto-Nr." value={form.konto_nr} onChange={(e) => setForm((p) => ({ ...p, konto_nr: e.target.value }))} />
            <Input placeholder="Konto/Kunde Name" value={form.konto_name} onChange={(e) => setForm((p) => ({ ...p, konto_name: e.target.value, kunde_name: e.target.value }))} />
            <Input type="date" value={form.rechnungsdatum} onChange={(e) => setForm((p) => ({ ...p, rechnungsdatum: e.target.value }))} />
            <Input type="date" value={form.faelligkeit} onChange={(e) => setForm((p) => ({ ...p, faelligkeit: e.target.value }))} />
            <Input type="number" placeholder="OP-Betrag" value={form.op_betrag} onChange={(e) => setForm((p) => ({ ...p, op_betrag: Number(e.target.value || 0) }))} />
            <Input type="number" placeholder="Offen" value={form.offen} onChange={(e) => setForm((p) => ({ ...p, offen: Number(e.target.value || 0) }))} />
            <Input placeholder="OP-Text" value={form.op_text} onChange={(e) => setForm((p) => ({ ...p, op_text: e.target.value }))} />
            <div className="flex gap-2">
              <Button onClick={() => void saveMutation.mutateAsync()} disabled={saveMutation.isPending || !form.rechnungsnr}>
                {editingId ? 'Aktualisieren' : 'Neu'}
              </Button>
              {editingId && <Button variant="outline" onClick={() => setEditingId(null)}>Abbrechen</Button>}
            </div>
          </div>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Suche nach Rechnung oder Kunde..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as OffenerPosten['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">Alle Status</option>
              <option value="faellig">Fällig</option>
              <option value="ueberfaellig">Überfällig</option>
              <option value="mahnung1">Mahnung 1</option>
              <option value="mahnung2">Mahnung 2</option>
              <option value="mahnung3">Mahnung 3</option>
              <option value="inkasso">Inkasso</option>
            </select>
            <Button variant="outline" className="gap-2" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-sm text-muted-foreground">Lade offene Posten...</span>
            </div>
          ) : (
            <>
                      <DataTable data={filteredPosten} columns={columns} />
              <div className="mt-2 space-y-2">
                {filteredPosten.map((posten) => (
                  <div key={`crud-${posten.id}`} className="flex items-center gap-2 text-xs">
                    <span>{posten.rechnungsNr}</span>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        const src = allePosten.find((x) => x.id === posten.id)
                        if (!src) return
                        setEditingId(src.id)
                        setForm({
                          rechnungsnr: src.rechnungsNr,
                          konto_nr: '',
                          konto_name: src.kunde,
                          kunde_name: src.kunde,
                          rechnungsdatum: src.rechnungsDatum.slice(0, 10),
                          faelligkeit: src.faelligAm.slice(0, 10),
                          op_betrag: src.betrag,
                          offen: src.offen,
                          op_text: '',
                        })
                      }}
                    >
                      Bearbeiten
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => deleteMutation.mutate(posten.id)} disabled={deleteMutation.isPending}>Loeschen</Button>
                  </div>
                ))}
              </div>
              <div className="mt-4 text-sm text-muted-foreground">
                {filteredPosten.length} von {allePosten.length} offene(n) Posten angezeigt
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
