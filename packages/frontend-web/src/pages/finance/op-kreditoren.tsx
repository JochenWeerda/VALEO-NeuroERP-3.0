import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Euro, Search, AlertCircle, CheckCircle2, Clock, Plus, Pencil, Trash2, Layers } from 'lucide-react'
import { Checkbox } from '@/components/ui/checkbox'
import { toast } from 'sonner'
import { useFibuCockpit } from '@/lib/api/fibu'

type OpStatus = 'offen' | 'teilweise' | 'geschlossen' | 'storniert'

type OpenItem = {
  id: string
  konto_name?: string | null
  konto_nr?: string | null
  konto_typ: 'debitoren' | 'kreditoren'
  op_status: OpStatus
  rechnungsnr: string
  rechnungsdatum: string
  faelligkeit: string
  op_betrag: number
  offen: number
  waehrung?: string
}

type OpenItemsResponse = {
  items: OpenItem[]
  summary: {
    count: number
    op_summe: number
    faellig: number
    nicht_faellig: number
  }
}

type OpenItemPayload = {
  konto_nr: string
  konto_name: string
  konto_typ: 'kreditoren'
  op_status: OpStatus
  rechnungsnr: string
  rechnungsdatum: string
  faelligkeit: string
  op_betrag: number
  offen: number
  waehrung: string
}

type SettlementPayload = {
  op_id: string
  payment_amount: number
  payment_date: string
  payment_reference: string
  payment_type: 'payment'
}

const fmt = (n: number, currency = 'EUR') =>
  new Intl.NumberFormat('de-DE', { style: 'currency', currency, maximumFractionDigits: 2 }).format(n || 0)

const defaultForm: OpenItemPayload = {
  konto_nr: '',
  konto_name: '',
  konto_typ: 'kreditoren',
  op_status: 'offen',
  rechnungsnr: '',
  rechnungsdatum: new Date().toISOString().slice(0, 10),
  faelligkeit: new Date().toISOString().slice(0, 10),
  op_betrag: 0,
  offen: 0,
  waehrung: 'EUR',
}

function isEditable(status: OpStatus): boolean {
  return status === 'offen' || status === 'teilweise'
}

function statusBadge(op: OpenItem) {
  if (op.op_status === 'geschlossen') return <Badge variant="secondary">Ausgeglichen</Badge>
  if (op.op_status === 'teilweise') return <Badge variant="outline">Teilweise</Badge>
  if (op.op_status === 'storniert') return <Badge variant="destructive">Storniert</Badge>
  return <Badge>Offen</Badge>
}

export default function OpKreditorenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { data: fibuCockpit } = useFibuCockpit()
  const [search, setSearch] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [settleOpen, setSettleOpen] = useState(false)
  const [formData, setFormData] = useState<OpenItemPayload>(defaultForm)
  const [selectedItem, setSelectedItem] = useState<OpenItem | null>(null)
  const [settleAmount, setSettleAmount] = useState<number>(0)
  const [settleDate, setSettleDate] = useState<string>(new Date().toISOString().slice(0, 10))
  const [settleReference, setSettleReference] = useState<string>('')
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [batchSettleOpen, setBatchSettleOpen] = useState(false)
  const [batchSettleDate, setBatchSettleDate] = useState<string>(new Date().toISOString().slice(0, 10))

  const { data, isLoading, isError } = useQuery({
    queryKey: ['finance', 'open-items', 'kreditoren'],
    queryFn: async () =>
      (
        await apiClient.get<OpenItemsResponse>('/api/v1/finance/open-items', {
          params: { konto_typ: 'kreditoren', limit: 1000 },
        })
      ).data,
    staleTime: 2 * 60 * 1000,
  })

  const createMutation = useMutation({
    mutationFn: async (payload: OpenItemPayload) =>
      apiClient.post('/api/v1/finance/open-items', payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['finance', 'open-items', 'kreditoren'] })
      toast.success('Offener Posten wurde angelegt.')
      setCreateOpen(false)
      setFormData(defaultForm)
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail ?? 'Anlage fehlgeschlagen')
    },
  })

  const updateMutation = useMutation({
    mutationFn: async (payload: { id: string; body: OpenItemPayload }) =>
      apiClient.put(`/api/v1/finance/open-items/${payload.id}`, payload.body),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['finance', 'open-items', 'kreditoren'] })
      toast.success('Offener Posten wurde aktualisiert.')
      setEditOpen(false)
      setSelectedItem(null)
      setFormData(defaultForm)
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail ?? 'Aktualisierung fehlgeschlagen')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => apiClient.delete(`/api/v1/finance/open-items/${id}`),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['finance', 'open-items', 'kreditoren'] })
      toast.success('Offener Posten wurde gelöscht.')
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail ?? 'Löschen fehlgeschlagen')
    },
  })

  const settleMutation = useMutation({
    mutationFn: async (payload: { id: string; body: SettlementPayload }) =>
      apiClient.post(`/api/v1/finance/open-items/${payload.id}/settle`, payload.body),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['finance', 'open-items', 'kreditoren'] })
      toast.success('Ausgleich wurde gebucht.')
      setSettleOpen(false)
      setSelectedItem(null)
      setSettleReference('')
      setSettleAmount(0)
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail ?? 'Ausgleich fehlgeschlagen')
    },
  })

  const batchSettleMutation = useMutation({
    mutationFn: async (payload: { items: SettlementPayload[] }) =>
      apiClient.post<{ success_count: number; error_count: number; errors: { op_id: string; detail: string }[] }>(
        '/api/v1/finance/open-items/batch-settle',
        { items: payload.items },
      ),
    onSuccess: async (res) => {
      await queryClient.invalidateQueries({ queryKey: ['finance', 'open-items', 'kreditoren'] })
      setSelectedIds(new Set())
      setBatchSettleOpen(false)
      if (res.data.error_count > 0) {
        toast.warning(`${res.data.success_count} ausgeglichen, ${res.data.error_count} Fehler.`)
      } else {
        toast.success(`Sammelausgleich: ${res.data.success_count} Posten ausgeglichen.`)
      }
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail ?? 'Sammelausgleich fehlgeschlagen')
    },
  })

  const items = data?.items ?? []
  const filtered = useMemo(
    () =>
      items.filter((op) => {
        const name = op.konto_name ?? ''
        return (
          name.toLowerCase().includes(search.toLowerCase()) ||
          op.rechnungsnr.toLowerCase().includes(search.toLowerCase())
        )
      }),
    [items, search],
  )

  const summary = data?.summary
  const sumOffen = summary?.op_summe ?? 0
  const sumUeberfaellig = summary?.faellig ?? 0
  const sumGesamt = items.reduce((s, op) => s + Number(op.op_betrag ?? 0), 0)

  const onSubmitCreate = () => {
    if (!formData.rechnungsnr || !formData.konto_name || formData.op_betrag <= 0) {
      toast.error('Bitte Pflichtfelder ausfüllen (Lieferant, Rechnungs-Nr., Betrag).')
      return
    }
    const payload = {
      ...formData,
      op_betrag: Number(formData.op_betrag),
      offen: Number(formData.offen || formData.op_betrag),
    }
    createMutation.mutate(payload)
  }

  const onSubmitEdit = () => {
    if (!selectedItem) return
    if (!formData.rechnungsnr || !formData.konto_name || formData.op_betrag <= 0) {
      toast.error('Bitte Pflichtfelder ausfüllen (Lieferant, Rechnungs-Nr., Betrag).')
      return
    }
    updateMutation.mutate({
      id: selectedItem.id,
      body: {
        ...formData,
        op_betrag: Number(formData.op_betrag),
        offen: Number(formData.offen),
      },
    })
  }

  const openEdit = (item: OpenItem) => {
    setSelectedItem(item)
    setFormData({
      konto_nr: item.konto_nr ?? '',
      konto_name: item.konto_name ?? '',
      konto_typ: 'kreditoren',
      op_status: item.op_status,
      rechnungsnr: item.rechnungsnr,
      rechnungsdatum: item.rechnungsdatum?.slice(0, 10),
      faelligkeit: item.faelligkeit?.slice(0, 10),
      op_betrag: Number(item.op_betrag),
      offen: Number(item.offen),
      waehrung: item.waehrung ?? 'EUR',
    })
    setEditOpen(true)
  }

  const openSettle = (item: OpenItem) => {
    setSelectedItem(item)
    setSettleAmount(Number(item.offen))
    setSettleDate(new Date().toISOString().slice(0, 10))
    setSettleReference(`AP-${item.rechnungsnr}`)
    setSettleOpen(true)
  }

  const submitSettle = () => {
    if (!selectedItem) return
    if (settleAmount <= 0 || settleAmount > Number(selectedItem.offen)) {
      toast.error('Ausgleichsbetrag ist ungültig.')
      return
    }
    settleMutation.mutate({
      id: selectedItem.id,
      body: {
        op_id: selectedItem.id,
        payment_amount: settleAmount,
        payment_date: settleDate,
        payment_reference: settleReference || `AP-${selectedItem.rechnungsnr}`,
        payment_type: 'payment',
      },
    })
  }

  const editableFiltered = useMemo(
    () => filtered.filter((op) => isEditable(op.op_status)),
    [filtered],
  )
  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }
  const toggleSelectAll = () => {
    if (selectedIds.size >= editableFiltered.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(editableFiltered.map((op) => op.id)))
    }
  }
  const selectedItems = useMemo(
    () => filtered.filter((op) => selectedIds.has(op.id) && isEditable(op.op_status)),
    [filtered, selectedIds],
  )
  const submitBatchSettle = () => {
    if (selectedItems.length === 0) return
    batchSettleMutation.mutate({
      items: selectedItems.map((op) => ({
        op_id: op.id,
        payment_amount: Number(op.offen),
        payment_date: batchSettleDate,
        payment_reference: `AP-${op.rechnungsnr}`,
        payment_type: 'payment' as const,
      })),
    })
  }

  return (
    <div className="space-y-6 p-6">
      <Card className="border-primary/20">
        <CardHeader className="pb-2">
          <CardTitle className="text-base">FIBU-Kernlage Kreditoren</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-4">
          <div><div className="text-xs text-muted-foreground">Zahlbare OP</div><div className="text-2xl font-semibold">{fibuCockpit.creditor.payable_items}</div></div>
          <div><div className="text-xs text-muted-foreground">Offener Betrag</div><div className="text-2xl font-semibold">{fmt(fibuCockpit.creditor.open_amount)}</div></div>
          <div><div className="text-xs text-muted-foreground">Überfällig</div><div className="text-2xl font-semibold">{fmt(fibuCockpit.creditor.overdue_amount)}</div></div>
          <div><div className="text-xs text-muted-foreground">Jahreswechsel</div><div className="text-sm font-semibold">{fibuCockpit.annual_close.ready_for_year_close ? 'stabil' : 'offene Klärungen'}</div></div>
        </CardContent>
      </Card>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Offene Posten - Kreditoren</h1>
          <p className="text-muted-foreground">Verbindlichkeiten, Fälligkeiten und Ausgleich verwalten</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            disabled={selectedIds.size === 0}
            onClick={() => setBatchSettleOpen(true)}
          >
            <Layers className="mr-2 h-4 w-4" />
            Sammelausgleich {selectedIds.size > 0 ? `(${selectedIds.size})` : ''}
          </Button>
          <Button
            onClick={() => {
              setFormData(defaultForm)
              setCreateOpen(true)
            }}
          >
            <Plus className="mr-2 h-4 w-4" />
            Neuer OP
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Euro className="h-4 w-4 text-blue-600" />
              Gesamt offen
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{fmt(sumOffen)}</span>
            <p className="text-xs text-muted-foreground mt-1">{summary?.count ?? 0} Positionen</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-600" />
              Überfällig
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{fmt(sumUeberfaellig)}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              Rechnungsbetrag Gesamt
            </CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{fmt(sumGesamt)}</span>
          </CardContent>
        </Card>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          className="pl-9"
          placeholder="Lieferant oder Rechnungsnummer suchen..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Offene Posten ({filtered.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground text-sm">Lade offene Posten...</p>}
          {isError && <p className="text-red-600 text-sm">Fehler beim Laden der offenen Posten.</p>}
          {!isLoading && !isError && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="py-2 pr-2 w-10">
                      <Checkbox
                        checked={editableFiltered.length > 0 && selectedIds.size === editableFiltered.length}
                        onCheckedChange={toggleSelectAll}
                        aria-label="Alle auswählen"
                      />
                    </th>
                    <th className="py-2 pr-4 font-medium">Lieferant</th>
                    <th className="py-2 pr-4 font-medium">Rechnungs-Nr.</th>
                    <th className="py-2 pr-4 font-medium">Fällig am</th>
                    <th className="py-2 pr-4 font-medium text-right">Betrag</th>
                    <th className="py-2 pr-4 font-medium text-right">Offen</th>
                    <th className="py-2 pr-4 font-medium">Status</th>
                    <th className="py-2 font-medium text-right">Aktionen</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.length === 0 && (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-muted-foreground">
                        Keine offenen Posten gefunden.
                      </td>
                    </tr>
                  )}
                  {filtered.map((op) => (
                    <tr key={op.id} className="border-b hover:bg-muted/50 transition-colors">
                      <td className="py-2 pr-2">
                        {isEditable(op.op_status) ? (
                          <Checkbox
                            checked={selectedIds.has(op.id)}
                            onCheckedChange={() => toggleSelect(op.id)}
                            aria-label={`${op.rechnungsnr} auswählen`}
                          />
                        ) : null}
                      </td>
                      <td className="py-2 pr-4 font-medium">{op.konto_name ?? '-'}</td>
                      <td className="py-2 pr-4 font-mono text-xs">{op.rechnungsnr}</td>
                      <td className="py-2 pr-4">
                        {op.faelligkeit ? new Date(op.faelligkeit).toLocaleDateString('de-DE') : '-'}
                      </td>
                      <td className="py-2 pr-4 text-right">{fmt(Number(op.op_betrag), op.waehrung ?? 'EUR')}</td>
                      <td className="py-2 pr-4 text-right font-semibold">{fmt(Number(op.offen), op.waehrung ?? 'EUR')}</td>
                      <td className="py-2 pr-4">{statusBadge(op)}</td>
                      <td className="py-2 text-right">
                        <div className="inline-flex items-center gap-1">
                          <Button
                            variant="outline"
                            size="sm"
                            disabled={!isEditable(op.op_status)}
                            onClick={() => openSettle(op)}
                          >
                            Ausgleich
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            disabled={!isEditable(op.op_status)}
                            onClick={() => openEdit(op)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            disabled={!isEditable(op.op_status)}
                            onClick={() => deleteMutation.mutate(op.id)}
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Neuen offenen Posten anlegen</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            <Label>Lieferant</Label>
            <Input value={formData.konto_name} onChange={(e) => setFormData((p) => ({ ...p, konto_name: e.target.value }))} />
            <Label>Rechnungs-Nr.</Label>
            <Input value={formData.rechnungsnr} onChange={(e) => setFormData((p) => ({ ...p, rechnungsnr: e.target.value }))} />
            <Label>Rechnungsdatum</Label>
            <Input type="date" value={formData.rechnungsdatum} onChange={(e) => setFormData((p) => ({ ...p, rechnungsdatum: e.target.value }))} />
            <Label>Fälligkeit</Label>
            <Input type="date" value={formData.faelligkeit} onChange={(e) => setFormData((p) => ({ ...p, faelligkeit: e.target.value }))} />
            <Label>Betrag</Label>
            <Input
              type="number"
              step="0.01"
              value={formData.op_betrag}
              onChange={(e) => {
                const amount = Number(e.target.value || 0)
                setFormData((p) => ({ ...p, op_betrag: amount, offen: amount }))
              }}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>Abbrechen</Button>
            <Button onClick={onSubmitCreate} disabled={createMutation.isPending}>Speichern</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Offenen Posten bearbeiten</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            <Label>Lieferant</Label>
            <Input value={formData.konto_name} onChange={(e) => setFormData((p) => ({ ...p, konto_name: e.target.value }))} />
            <Label>Rechnungs-Nr.</Label>
            <Input value={formData.rechnungsnr} onChange={(e) => setFormData((p) => ({ ...p, rechnungsnr: e.target.value }))} />
            <Label>Fälligkeit</Label>
            <Input type="date" value={formData.faelligkeit} onChange={(e) => setFormData((p) => ({ ...p, faelligkeit: e.target.value }))} />
            <Label>Offener Betrag</Label>
            <Input
              type="number"
              step="0.01"
              value={formData.offen}
              onChange={(e) => setFormData((p) => ({ ...p, offen: Number(e.target.value || 0) }))}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)}>Abbrechen</Button>
            <Button onClick={onSubmitEdit} disabled={updateMutation.isPending}>Aktualisieren</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={settleOpen} onOpenChange={setSettleOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ausgleich buchen</DialogTitle>
          </DialogHeader>
          <div className="grid gap-3">
            <p className="text-sm text-muted-foreground">
              {selectedItem ? `Rechnung ${selectedItem.rechnungsnr} | Offen ${fmt(Number(selectedItem.offen))}` : ''}
            </p>
            <Label>Ausgleichsbetrag</Label>
            <Input type="number" step="0.01" value={settleAmount} onChange={(e) => setSettleAmount(Number(e.target.value || 0))} />
            <Label>Datum</Label>
            <Input type="date" value={settleDate} onChange={(e) => setSettleDate(e.target.value)} />
            <Label>Referenz</Label>
            <Input value={settleReference} onChange={(e) => setSettleReference(e.target.value)} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSettleOpen(false)}>Abbrechen</Button>
            <Button onClick={submitSettle} disabled={settleMutation.isPending}>Buchen</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={batchSettleOpen} onOpenChange={setBatchSettleOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Sammelausgleich</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            {selectedItems.length} Posten werden jeweils mit dem vollen offenen Betrag ausgeglichen.
          </p>
          <div className="max-h-48 overflow-y-auto border rounded p-2 space-y-1">
            {selectedItems.map((op) => (
              <div key={op.id} className="flex justify-between text-sm">
                <span>{op.konto_name ?? '-'} · {op.rechnungsnr}</span>
                <span className="font-medium">{fmt(Number(op.offen))}</span>
              </div>
            ))}
          </div>
          <Label>Buchungsdatum (für alle)</Label>
          <Input type="date" value={batchSettleDate} onChange={(e) => setBatchSettleDate(e.target.value)} />
          <DialogFooter>
            <Button variant="outline" onClick={() => setBatchSettleOpen(false)}>Abbrechen</Button>
            <Button onClick={submitBatchSettle} disabled={batchSettleMutation.isPending}>
              Alle ausgleichen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
