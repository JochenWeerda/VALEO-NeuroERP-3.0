import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/hooks/useAuth'
import { CustomerSelectionDialog, type Customer } from '@/components/sales/CustomerSelectionDialog'
import { ArtikelSuchDialog, type Article as LookupArticle } from '@/components/sales/ArtikelSuchDialog'
import {
  cancelKontrakt,
  createKontrakt,
  deleteKontrakt,
  getKontrakt,
  type Kontrakt,
  type KontraktLine,
  updateKontrakt,
} from '@/lib/api/kontrakte'
import DlgAuswahlVerkaufKontrakte from '@/pages/kontrakte/DlgAuswahlVerkaufKontrakte'
import DlgKontraktUmSaetze from '@/pages/kontrakte/DlgKontraktUmSaetze'
import FrmKontraktProtokoll from '@/pages/kontrakte/FrmKontraktProtokoll'

type FormState = Omit<Kontrakt, 'contract_id' | 'rest_quantity'>

function createEmptyLine(position_no: number): KontraktLine {
  return {
    position_no,
    article_id: '',
    qty_contract: 0,
    unit_price: 0,
    discount_pct: 0,
    description1: '',
    description2: '',
    price_unit: 'kg',
    surcharge: 0,
    rebate_type: '',
    is_bio: false,
    is_matif: false,
  }
}

function createEmptyState(): FormState {
  return {
    contract_no: '',
    contract_type: 'VERKAUF',
    branch_id: '',
    clerk_id: '',
    party_id: '',
    debitor_kto: '',
    kreditor_kto: '',
    contract_date: new Date().toISOString(),
    valid_from: '',
    valid_to: '',
    quantity_type: 'GESAMTKONTRAKT',
    total_quantity: 0,
    unit: 'kg',
    allow_overdelivery: false,
    status: 'OFFEN',
    notes: '',
    payment_terms: '',
    conditions_json: {},
    pricing_model: 'fixed',
    min_price: null,
    premium_type: '',
    premium_value: null,
    basis_reference: '',
    pricing_window_from: '',
    pricing_window_to: '',
    lines: [createEmptyLine(1)],
  }
}

export default function FrmKontraktDetail(): JSX.Element {
  const { id } = useParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const { hasRole } = useAuth()

  const isEdit = Boolean(id)
  const [state, setState] = useState<FormState>(createEmptyState())
  const [showLookupDlg, setShowLookupDlg] = useState(false)
  const [showUmsaetze, setShowUmsaetze] = useState(false)
  const [showCustomerDlg, setShowCustomerDlg] = useState(false)
  const [showArticleDlg, setShowArticleDlg] = useState(false)
  const [activeLineIndex, setActiveLineIndex] = useState<number | null>(null)
  const [selectedCustomerName, setSelectedCustomerName] = useState('')

  const canEdit = hasRole('KONTRAKT_BEARBEITEN') || hasRole('KONTRAKT_ADMIN')
  const canDelete = hasRole('KONTRAKT_LOESCHEN') || hasRole('KONTRAKT_ADMIN')
  const isAdmin = hasRole('KONTRAKT_ADMIN')
  const isDraftEditable = canEdit && (!isEdit || state.status === 'OFFEN')

  const detailQuery = useQuery({
    queryKey: ['kontrakte', 'detail', id],
    queryFn: () => getKontrakt(String(id)),
    enabled: isEdit,
  })

  useEffect(() => {
    if (detailQuery.data) {
      const { contract_id: _contractId, rest_quantity: _rest, ...rest } = detailQuery.data
      setState({
        ...rest,
        contract_date: rest.contract_date || '',
        valid_from: rest.valid_from || '',
        valid_to: rest.valid_to || '',
        pricing_window_from: rest.pricing_window_from || '',
        pricing_window_to: rest.pricing_window_to || '',
      })
    }
  }, [detailQuery.data])

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!state.party_id || !state.contract_type) {
        throw new Error('Pflichtfelder fehlen')
      }
      if (state.lines.length < 1 || state.lines.length > 3) {
        throw new Error('Sammelkontrakt muss zwischen 1 und 3 Artikel-Positionen enthalten')
      }
      const missingArticle = state.lines.find((line) => !line.article_id?.trim())
      if (missingArticle) {
        throw new Error(`Artikel fehlt in Position ${missingArticle.position_no}`)
      }
      if (state.quantity_type === 'GESAMTKONTRAKT') {
        const sumLines = state.lines.reduce((acc, line) => acc + Number(line.qty_contract || 0), 0)
        const total = Number(state.total_quantity || 0)
        if (Math.abs(sumLines - total) > 0.0001) {
          throw new Error(`Gesamt-Menge (${total}) muss Summe der Positionen (${sumLines}) entsprechen`)
        }
      }
      if (isEdit) return updateKontrakt(String(id), state)
      return createKontrakt(state)
    },
    onSuccess: (saved) => {
      toast({ title: 'Gespeichert', description: `Kontrakt ${saved.contract_no}` })
      navigate(`/kontrakte/${saved.contract_id}`)
    },
    onError: (err: any) => {
      toast({ title: 'Fehler', description: err?.message || 'Speichern fehlgeschlagen', variant: 'destructive' })
    },
  })

  const cancelMutation = useMutation({
    mutationFn: async () => cancelKontrakt(String(id), 'Manueller Storno aus FrmKontraktDetail'),
    onSuccess: () => {
      toast({ title: 'Storniert' })
      detailQuery.refetch()
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async () => deleteKontrakt(String(id)),
    onSuccess: () => {
      toast({ title: 'Geloescht' })
      navigate('/kontrakte')
    },
    onError: (err: any) => {
      toast({ title: 'Loeschen fehlgeschlagen', description: err?.message || '', variant: 'destructive' })
    },
  })

  const restMenge = useMemo(() => {
    const total = state.lines.reduce((acc, l) => acc + Number(l.qty_contract || 0), 0)
    return Number(state.total_quantity || total)
  }, [state.lines, state.total_quantity])

  const updateLine = (index: number, patch: Partial<KontraktLine>): void => {
    setState((prev) => {
      const lines = [...prev.lines]
      lines[index] = { ...lines[index], ...patch }
      return { ...prev, lines }
    })
  }

  const moveLine = (index: number, direction: -1 | 1): void => {
    setState((prev) => {
      const target = index + direction
      if (target < 0 || target >= prev.lines.length) return prev
      const lines = [...prev.lines]
      const temp = lines[index]
      lines[index] = lines[target]
      lines[target] = temp
      const normalized = lines.map((line, i) => ({ ...line, position_no: i + 1 }))
      return { ...prev, lines: normalized }
    })
  }

  const removeLine = (index: number): void => {
    setState((prev) => {
      if (prev.lines.length <= 1) return prev
      const lines = prev.lines.filter((_, i) => i !== index).map((line, i) => ({ ...line, position_no: i + 1 }))
      return { ...prev, lines }
    })
  }

  return (
    <div className="space-y-4 p-6">
      <Card>
        <CardHeader>
          <CardTitle>FrmKontraktDetail</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Button disabled={!isDraftEditable || saveMutation.isPending} onClick={() => saveMutation.mutate()}>Speichern</Button>
            <Button variant="outline" disabled={!canDelete || !isEdit || deleteMutation.isPending || !isDraftEditable} onClick={() => deleteMutation.mutate()}>Loeschen</Button>
            <Button variant="outline" disabled={!isEdit} onClick={() => window.print()}>Drucken</Button>
            <Button variant="outline" disabled={!isEdit} onClick={() => setShowUmsaetze(true)}>Umsaetze</Button>
            <Button variant="outline" onClick={() => setShowLookupDlg(true)}>Lookup/Matchcode</Button>
            <Button variant="outline" onClick={() => navigate('/dokumente/ablage')}>Unterlagen/Dateien</Button>
            <Button variant="outline" disabled={!isEdit || !canEdit || cancelMutation.isPending} onClick={() => cancelMutation.mutate()}>Workflow erledigt/stornieren</Button>
          </div>

          <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
            <div className="space-y-1">
              <Label>Kontrakt-Nr.</Label>
              <Input value={state.contract_no || ''} onChange={(e) => setState((s) => ({ ...s, contract_no: e.target.value }))} disabled={!isAdmin && isEdit} />
            </div>
            <div className="space-y-1">
              <Label>Kontrakt-Typ</Label>
              <Select value={state.contract_type} onValueChange={(v: any) => setState((s) => ({ ...s, contract_type: v }))} disabled={!isDraftEditable}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="VERKAUF">VERKAUF</SelectItem>
                  <SelectItem value="ZUKAUF">ZUKAUF</SelectItem>
                  <SelectItem value="EINKAUF">EINKAUF</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>Niederlassung</Label>
              <Input value={state.branch_id || ''} onChange={(e) => setState((s) => ({ ...s, branch_id: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>Bediener</Label>
              <Input value={state.clerk_id || ''} onChange={(e) => setState((s) => ({ ...s, clerk_id: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>Kunde/Lieferant</Label>
              <div className="flex gap-2">
                <Input value={state.party_id} onChange={(e) => setState((s) => ({ ...s, party_id: e.target.value }))} disabled={!isDraftEditable} />
                <Button type="button" variant="outline" disabled={!isDraftEditable} onClick={() => setShowCustomerDlg(true)}>Suchen</Button>
              </div>
              {selectedCustomerName ? <p className="text-xs text-muted-foreground">{selectedCustomerName}</p> : null}
            </div>
            <div className="space-y-1">
              <Label>Kontrakt-Datum</Label>
              <Input type="date" value={(state.contract_date || '').slice(0, 10)} onChange={(e) => setState((s) => ({ ...s, contract_date: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>gueltig von</Label>
              <Input type="date" value={(state.valid_from || '').slice(0, 10)} onChange={(e) => setState((s) => ({ ...s, valid_from: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>gueltig bis</Label>
              <Input type="date" value={(state.valid_to || '').slice(0, 10)} onChange={(e) => setState((s) => ({ ...s, valid_to: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>Mengen-Art</Label>
              <Select value={state.quantity_type} onValueChange={(v: any) => setState((s) => ({ ...s, quantity_type: v }))} disabled={!isDraftEditable}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="GESAMTKONTRAKT">Gesamtkontrakt</SelectItem>
                  <SelectItem value="EINZELMENGEN">Einzelmengen</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label>Gesamt-Menge</Label>
              <Input type="number" value={state.total_quantity} onChange={(e) => setState((s) => ({ ...s, total_quantity: Number(e.target.value) }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>Einheit</Label>
              <Input value={state.unit} onChange={(e) => setState((s) => ({ ...s, unit: e.target.value }))} disabled={!isDraftEditable} />
            </div>
            <div className="space-y-1">
              <Label>Rest-Menge</Label>
              <Input value={restMenge} disabled />
            </div>
            <div className="flex items-center gap-2 pt-6">
              <Checkbox checked={state.allow_overdelivery} onCheckedChange={(v) => setState((s) => ({ ...s, allow_overdelivery: v === true }))} disabled={!isDraftEditable} />
              <Label>Ueberschreiten der Kontraktmenge erlaubt</Label>
            </div>
          </div>

          <Tabs defaultValue={state.contract_type === 'VERKAUF' ? 'kunde' : 'lieferant'}>
            <TabsList className="flex flex-wrap">
              <TabsTrigger value="kunde">KUNDE</TabsTrigger>
              <TabsTrigger value="lieferant">LIEFERANT</TabsTrigger>
              <TabsTrigger value="lieferanschrift">LIEFERANSCHR</TabsTrigger>
              <TabsTrigger value="info">INFO</TabsTrigger>
              <TabsTrigger value="zahlungsbed">ZAHLUNGSBED.</TabsTrigger>
              <TabsTrigger value="texte">TEXTE</TabsTrigger>
              <TabsTrigger value="bedingungen">BEDINGUNGEN</TabsTrigger>
              <TabsTrigger value="unterlagen">UNTERLAGEN/DATEIEN</TabsTrigger>
              <TabsTrigger value="protokoll">PROTOKOLL</TabsTrigger>
            </TabsList>
            <TabsContent value="kunde"><Input value={state.party_id} onChange={(e) => setState((s) => ({ ...s, party_id: e.target.value }))} /></TabsContent>
            <TabsContent value="lieferant"><Input value={state.party_id} onChange={(e) => setState((s) => ({ ...s, party_id: e.target.value }))} /></TabsContent>
            <TabsContent value="lieferanschrift"><Textarea value={state.notes || ''} onChange={(e) => setState((s) => ({ ...s, notes: e.target.value }))} /></TabsContent>
            <TabsContent value="info"><Textarea value={state.notes || ''} onChange={(e) => setState((s) => ({ ...s, notes: e.target.value }))} /></TabsContent>
            <TabsContent value="zahlungsbed"><Textarea value={state.payment_terms || ''} onChange={(e) => setState((s) => ({ ...s, payment_terms: e.target.value }))} /></TabsContent>
            <TabsContent value="texte"><Textarea value={state.notes || ''} onChange={(e) => setState((s) => ({ ...s, notes: e.target.value }))} /></TabsContent>
            <TabsContent value="bedingungen"><Textarea value={JSON.stringify(state.conditions_json || {}, null, 2)} onChange={(e) => { try { setState((s) => ({ ...s, conditions_json: JSON.parse(e.target.value) })) } catch (_error) { /* ignore */ } }} /></TabsContent>
            <TabsContent value="unterlagen"><Button variant="outline" onClick={() => navigate('/dokumente/ablage')}>Unterlagen/Dateien oeffnen</Button></TabsContent>
            <TabsContent value="protokoll">{isEdit ? <FrmKontraktProtokoll contractId={String(id)} /> : <p>Protokoll erst nach dem Speichern verfuegbar.</p>}</TabsContent>
          </Tabs>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Positionen</CardTitle>
              <Button variant="outline" onClick={() => setState((s) => ({ ...s, lines: [...s.lines, createEmptyLine(s.lines.length + 1)] }))} disabled={!isDraftEditable || state.lines.length >= 3}>
                Position hinzufuegen
              </Button>
            </CardHeader>
            <CardContent>
              <div className="max-h-[320px] overflow-auto rounded border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Pos.-Nr</TableHead>
                      <TableHead>Artikel-Nr</TableHead>
                      <TableHead>Bezeichnung-1</TableHead>
                      <TableHead>Bezeichnung-2</TableHead>
                      <TableHead>Menge</TableHead>
                      <TableHead>Rest-Menge</TableHead>
                      <TableHead>Einheit</TableHead>
                      <TableHead>Einh.-Preis</TableHead>
                      <TableHead>Rabatt %</TableHead>
                      <TableHead>Aktionen</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {state.lines.map((line, index) => (
                      <TableRow key={`${line.line_id ?? 'new'}-${index}`}>
                        <TableCell>{line.position_no}</TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Input value={line.article_id} onChange={(e) => updateLine(index, { article_id: e.target.value })} disabled={!isDraftEditable} />
                            <Button type="button" variant="outline" disabled={!isDraftEditable} onClick={() => { setActiveLineIndex(index); setShowArticleDlg(true) }}>Suchen</Button>
                          </div>
                        </TableCell>
                        <TableCell><Input value={line.description1 || ''} onChange={(e) => updateLine(index, { description1: e.target.value })} disabled={!isDraftEditable} /></TableCell>
                        <TableCell><Input value={line.description2 || ''} onChange={(e) => updateLine(index, { description2: e.target.value })} disabled={!isDraftEditable} /></TableCell>
                        <TableCell><Input type="number" value={line.qty_contract} onChange={(e) => updateLine(index, { qty_contract: Number(e.target.value) })} disabled={!isDraftEditable} /></TableCell>
                        <TableCell>{line.qty_remaining ?? line.qty_contract}</TableCell>
                        <TableCell>{state.unit}</TableCell>
                        <TableCell><Input type="number" value={line.unit_price ?? 0} onChange={(e) => updateLine(index, { unit_price: Number(e.target.value) })} disabled={!isDraftEditable} /></TableCell>
                        <TableCell><Input type="number" value={line.discount_pct ?? 0} onChange={(e) => updateLine(index, { discount_pct: Number(e.target.value) })} disabled={!isDraftEditable} /></TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button type="button" variant="outline" disabled={!isDraftEditable || index === 0} onClick={() => moveLine(index, -1)}>?</Button>
                            <Button type="button" variant="outline" disabled={!isDraftEditable || index === state.lines.length - 1} onClick={() => moveLine(index, 1)}>?</Button>
                            <Button type="button" variant="destructive" disabled={!isDraftEditable || state.lines.length <= 1} onClick={() => removeLine(index)}>Loeschen</Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">Sammelkontrakt: 1 bis 3 Artikelpositionen. Bei "Gesamtkontrakt" muss die Summe der Positionsmengen der Gesamt-Menge entsprechen.</p>
            </CardContent>
          </Card>
        </CardContent>
      </Card>

      <DlgAuswahlVerkaufKontrakte
        open={showLookupDlg}
        onOpenChange={setShowLookupDlg}
        onSelect={(item) => {
          if (!state.lines.length) return
          updateLine(0, { article_id: item.article_id, description1: item.bezeichnung })
          toast({ title: 'Lookup uebernommen', description: `${item.contract_no}/${item.position_no}` })
        }}
      />

      <CustomerSelectionDialog
        open={showCustomerDlg}
        onClose={() => setShowCustomerDlg(false)}
        onSelect={(customer: Customer) => {
          setState((s) => ({ ...s, party_id: customer.id }))
          setSelectedCustomerName(customer.name || customer.company_name || customer.id)
          setShowCustomerDlg(false)
          toast({ title: 'Kunde uebernommen', description: `${customer.customerNumber} - ${customer.name}` })
        }}
        title="Kunde/Lieferant auswaehlen"
      />

      <ArtikelSuchDialog
        open={showArticleDlg}
        onClose={() => setShowArticleDlg(false)}
        onSelect={(article: LookupArticle) => {
          if (activeLineIndex === null) return
          updateLine(activeLineIndex, {
            article_id: article.articleNumber || article.id,
            description1: article.description || article.name || '',
            description2: article.description2 || '',
          })
          setShowArticleDlg(false)
          setActiveLineIndex(null)
          toast({ title: 'Artikel uebernommen', description: `${article.articleNumber} - ${article.description}` })
        }}
      />

      {isEdit && (
        <DlgKontraktUmSaetze
          open={showUmsaetze}
          onOpenChange={setShowUmsaetze}
          contractId={String(id)}
          contractNo={state.contract_no}
          validFrom={state.valid_from || null}
          validTo={state.valid_to || null}
          partner={state.party_id}
          quantityType={state.quantity_type}
          done={state.status === 'ERLEDIGT'}
          contractQty={state.total_quantity}
          restQty={detailQuery.data?.rest_quantity}
        />
      )}
    </div>
  )
}
