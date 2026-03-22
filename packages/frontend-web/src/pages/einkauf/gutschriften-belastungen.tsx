import { useState, useEffect } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { NativeSelect } from '@/components/ui/native-select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/axios'
import { Plus, ArrowLeft, XCircle } from 'lucide-react'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'

type APInvoice = {
  id: string
  number: string
  supplierId: string
  supplierName: string
  invoiceDate: string
  dueDate: string
  netAmount: number
  taxAmount: number
  grossAmount: number
  status: string
  openAmount: number
}

type CreditMemo = {
  id: string
  number: string
  supplierId: string
  supplierName: string
  invoiceId?: string
  invoiceNumber?: string
  memoDate: string
  netAmount: number
  taxAmount: number
  grossAmount: number
  status: string
  reason: string
  notes?: string
  settled: boolean
  settledInvoiceIds?: string[]
}

type DebitMemo = {
  id: string
  number: string
  supplierId: string
  supplierName: string
  invoiceId?: string
  invoiceNumber?: string
  memoDate: string
  netAmount: number
  taxAmount: number
  grossAmount: number
  status: string
  reason: string
  notes?: string
  settled: boolean
  settledInvoiceIds?: string[]
}

type MemoItem = {
  productId?: string
  productName: string
  quantity: number
  unit: string
  unitPrice: number
  netAmount: number
  taxRate: number
  taxAmount: number
  grossAmount: number
  reason: string
}

type MemoData = {
  supplierId: string
  invoiceId?: string
  settlementId?: string
  memoDate: string
  reason: string
  notes: string
  items: MemoItem[]
  settlementInvoiceIds: string[]
}

type SettlementCorrectionDraft = {
  settlement_id: string
  settlement_number: string
  memo_type: 'credit' | 'debit'
  supplier_id: string
  supplier_name?: string | null
  posted_journal_ref?: string | null
  suggested_reason: string
  suggested_notes: string
  suggested_route: string
  items: MemoItem[]
}

export default function GutschriftenBelastungenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { type } = useParams<{ type?: string }>()
  const [searchParams] = useSearchParams()
  const invoiceId = searchParams.get('invoiceId')
  const settlementId = searchParams.get('settlementId')
  
  const [activeTab, setActiveTab] = useState<'credit' | 'debit'>(type === 'debit' ? 'debit' : 'credit')
  const [loading, setLoading] = useState(false)
  const [creditMemos, setCreditMemos] = useState<CreditMemo[]>([])
  const [debitMemos, setDebitMemos] = useState<DebitMemo[]>([])
  const [openInvoices, setOpenInvoices] = useState<APInvoice[]>([])
  const [memoDialogOpen, setMemoDialogOpen] = useState(false)
  const [settlementDialogOpen, setSettlementDialogOpen] = useState(false)
  const [selectedMemo, setSelectedMemo] = useState<CreditMemo | DebitMemo | null>(null)
  const [settlementDraft, setSettlementDraft] = useState<SettlementCorrectionDraft | null>(null)
  const [memoData, setMemoData] = useState<MemoData>({
    supplierId: '',
    invoiceId: invoiceId || '',
    settlementId: settlementId || '',
    memoDate: new Date().toISOString().split('T')[0],
    reason: '',
    notes: '',
    items: [],
    settlementInvoiceIds: [],
  })

  useEffect(() => {
    loadCreditMemos()
    loadDebitMemos()
    loadOpenInvoices()
  }, [])

  useEffect(() => {
    if (!settlementId) return
    void loadSettlementCorrectionDraft(settlementId, activeTab)
  }, [settlementId, activeTab])

  useEffect(() => {
    if (invoiceId) {
      const invoice = openInvoices.find(inv => inv.id === invoiceId)
      if (invoice) {
        setMemoData(prev => ({
          ...prev,
          supplierId: invoice.supplierId,
          invoiceId: invoice.id,
        }))
      }
    }
  }, [invoiceId, openInvoices])

  const loadCreditMemos = async () => {
    try {
      setLoading(true)
      const response = (await apiClient.get<CreditMemo[]>('/api/v1/einkauf/credit-memos')) as unknown as CreditMemo[]
      setCreditMemos(response ?? [])
    } catch (error) {
      console.error('Fehler beim Laden der Gutschriften:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: t('crud.messages.loadErrorDescription'),
      })
    } finally {
      setLoading(false)
    }
  }

  const loadDebitMemos = async () => {
    try {
      setLoading(true)
      const response = (await apiClient.get<DebitMemo[]>('/api/v1/einkauf/debit-memos')) as unknown as DebitMemo[]
      setDebitMemos(response ?? [])
    } catch (error) {
      console.error('Fehler beim Laden der Belastungen:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: t('crud.messages.loadErrorDescription'),
      })
    } finally {
      setLoading(false)
    }
  }

  const loadOpenInvoices = async () => {
    try {
      const response = (await apiClient.get<APInvoice[]>('/api/v1/ap/invoices?status=APPROVED')) as unknown as APInvoice[]
      const rawList = Array.isArray(response) ? response : []
      let openItemsMap: Record<string, number> = {}
      try {
        const opRes = (await apiClient.get<{ items?: Array<{ rechnungsnr?: string; offen?: number }> }>(
          '/api/v1/finance/open-items?konto_typ=kreditoren&limit=500'
        )) as unknown as { items?: Array<{ rechnungsnr?: string; offen?: number }> }
        const items = opRes?.items ?? []
        items.forEach((op: { rechnungsnr?: string; offen?: number }) => {
          if (op.rechnungsnr != null) openItemsMap[op.rechnungsnr] = Number(op.offen ?? 0)
        })
      } catch {
        // Fallback: openAmount bleibt aus Rechnung
      }
      const invoices: APInvoice[] = rawList.map((inv: any) => {
        const nr = inv.number ?? inv.id ?? ''
        const openFromOp = openItemsMap[nr]
        return {
          id: inv.id || inv.number,
          number: nr,
          supplierId: inv.customerId || inv.supplierId,
          supplierName: inv.customerName || inv.supplierName || '',
          invoiceDate: inv.date || inv.invoiceDate,
          dueDate: inv.dueDate,
          netAmount: inv.subtotalNet || inv.netAmount || 0,
          taxAmount: inv.totalTax || inv.taxAmount || 0,
          grossAmount: inv.totalGross || inv.grossAmount || 0,
          status: inv.status,
          openAmount: openFromOp !== undefined ? openFromOp : (inv.openAmount ?? inv.open_amount ?? inv.totalGross ?? inv.grossAmount ?? 0),
        }
      })
      setOpenInvoices(invoices)
    } catch (error) {
      console.error('Fehler beim Laden der offenen Rechnungen:', error)
    }
  }

  const loadSettlementCorrectionDraft = async (targetSettlementId: string, memoType: 'credit' | 'debit') => {
    try {
      const response = (await apiClient.get<SettlementCorrectionDraft>(
        `/api/v1/agrar/settlements/${targetSettlementId}/correction-draft?memo_type=${memoType}`
      )) as unknown as SettlementCorrectionDraft
      setSettlementDraft(response)
      setMemoData((prev) => ({
        ...prev,
        supplierId: response.supplier_id,
        invoiceId: '',
        settlementId: response.settlement_id,
        reason: response.suggested_reason,
        notes: response.suggested_notes,
        items: response.items,
      }))
    } catch (error) {
      console.error('Fehler beim Laden des Settlement-Korrekturentwurfs:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: 'Settlement-Korrekturentwurf konnte nicht geladen werden.',
      })
    }
  }

  const handleCreateMemo = () => {
    if (!memoData.supplierId) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.selectSupplier'),
      })
      return
    }
    setMemoDialogOpen(true)
  }

  const handleSaveMemo = async () => {
    if (!memoData.reason || memoData.reason.length < 10) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.reasonMinLength'),
      })
      return
    }

    if (memoData.items.length === 0) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.addAtLeastOneItem'),
      })
      return
    }

    setLoading(true)
    try {
      const endpoint = activeTab === 'credit' 
        ? '/api/v1/einkauf/credit-memos'
        : '/api/v1/einkauf/debit-memos'
      
      // Transform items to match API schema
      const items = memoData.items.map(item => ({
        productId: item.productId,
        productName: item.productName,
        quantity: item.quantity,
        unit: item.unit,
        unitPrice: item.unitPrice,
        netAmount: item.netAmount,
        taxRate: item.taxRate,
        taxAmount: item.taxAmount,
        grossAmount: item.grossAmount,
        reason: item.reason,
      }))
      
      await apiClient.post(endpoint, {
        supplierId: memoData.supplierId,
        invoiceId: memoData.invoiceId || undefined,
        settlementId: memoData.settlementId || undefined,
        correctionMode: settlementDraft ? (activeTab === 'credit' ? 'CREDIT_NOTE' : 'DEBIT_MEMO') : undefined,
        memoDate: memoData.memoDate,
        reason: memoData.reason,
        notes: memoData.notes || undefined,
        items: items,
      })

      toast({
        title: t('crud.messages.createSuccess', { 
          entityType: activeTab === 'credit' 
            ? t('crud.entities.creditMemo')
            : t('crud.entities.debitMemo')
        }),
      })

      setMemoDialogOpen(false)
      setMemoData({
        supplierId: '',
        invoiceId: '',
        settlementId: '',
        memoDate: new Date().toISOString().split('T')[0],
        reason: '',
        notes: '',
        items: [],
        settlementInvoiceIds: [],
      })
      
      if (activeTab === 'credit') {
        loadCreditMemos()
      } else {
        loadDebitMemos()
      }
    } catch (error: any) {
      console.error('Fehler beim Erstellen des Memos:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.createError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSettle = (memo: CreditMemo | DebitMemo) => {
    setSelectedMemo(memo)
    setSettlementDialogOpen(true)
  }

  const handleSaveSettlement = async () => {
    if (!selectedMemo) return

    if (memoData.settlementInvoiceIds.length === 0) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.selectInvoicesForSettlement'),
      })
      return
    }

    setLoading(true)
    try {
      const endpoint = activeTab === 'credit'
        ? `/api/v1/einkauf/credit-memos/${selectedMemo.id}/settle`
        : `/api/v1/einkauf/debit-memos/${selectedMemo.id}/settle`
      
      await apiClient.post(endpoint, {
        invoiceIds: memoData.settlementInvoiceIds,
      })

      toast({
        title: t('crud.messages.settlementSuccess'),
      })

      setSettlementDialogOpen(false)
      setSelectedMemo(null)
      setMemoData(prev => ({ ...prev, settlementInvoiceIds: [] }))
      
      if (activeTab === 'credit') {
        loadCreditMemos()
      } else {
        loadDebitMemos()
      }
      loadOpenInvoices()
    } catch (error: any) {
      console.error('Fehler beim Verrechnen:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.settlementError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const addMemoItem = () => {
    setMemoData(prev => ({
      ...prev,
      items: [
        ...prev.items,
        {
          productName: '',
          quantity: 1,
          unit: 'Stk',
          unitPrice: 0,
          netAmount: 0,
          taxRate: 19,
          taxAmount: 0,
          grossAmount: 0,
          reason: '',
        },
      ],
    }))
  }

  const updateMemoItem = (index: number, field: keyof MemoItem, value: any) => {
    const updatedItems = [...memoData.items]
    updatedItems[index] = { ...updatedItems[index], [field]: value }
    
    // Recalculate amounts
    if (field === 'quantity' || field === 'unitPrice' || field === 'taxRate') {
      const item = updatedItems[index]
      item.netAmount = item.quantity * item.unitPrice
      item.taxAmount = item.netAmount * (item.taxRate / 100)
      item.grossAmount = item.netAmount + item.taxAmount
    }
    
    setMemoData(prev => ({ ...prev, items: updatedItems }))
  }

  const removeMemoItem = (index: number) => {
    setMemoData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
    }))
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            {t('crud.entities.creditMemo')} / {t('crud.entities.debitMemo')}
          </h1>
          <p className="text-muted-foreground mt-1">
            {t('crud.descriptions.creditDebitMemo', { defaultValue: 'Gutschriften und Belastungen verwalten' })}
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => navigate('/einkauf/rechnungseingaenge-liste')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          {t('common.back')}
        </Button>
      </div>

      {settlementDraft ? (
        <Card>
          <CardHeader>
            <CardTitle>Settlement-Korrekturbezug</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="font-medium">{settlementDraft.settlement_number}</div>
            <div className="text-muted-foreground">
              Settlement-ID: {settlementDraft.settlement_id}
            </div>
            <div className="text-muted-foreground">
              Journal: {settlementDraft.posted_journal_ref || '-'}
            </div>
            <div className="text-muted-foreground">
              Lieferant: {settlementDraft.supplier_name || settlementDraft.supplier_id}
            </div>
          </CardContent>
        </Card>
      ) : null}

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'credit' | 'debit')}>
        <TabsList>
          <TabsTrigger value="credit">
            {t('crud.entities.creditMemo')} ({creditMemos.length})
          </TabsTrigger>
          <TabsTrigger value="debit">
            {t('crud.entities.debitMemo')} ({debitMemos.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="credit">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.entities.creditMemo')}</CardTitle>
                <Button onClick={handleCreateMemo}>
                  <Plus className="h-4 w-4 mr-2" />
                  {t('crud.actions.createCreditMemo')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('crud.fields.number')}</TableHead>
                    <TableHead>{t('crud.entities.supplier')}</TableHead>
                    <TableHead>{t('crud.fields.invoiceNumber')}</TableHead>
                    <TableHead>{t('crud.fields.date')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.grossAmount')}</TableHead>
                    <TableHead>{t('crud.fields.reason')}</TableHead>
                    <TableHead>{t('crud.fields.status')}</TableHead>
                    <TableHead>{t('crud.actions.actions')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {creditMemos.map(memo => (
                    <TableRow key={memo.id}>
                      <TableCell className="font-medium">{memo.number}</TableCell>
                      <TableCell>{memo.supplierName}</TableCell>
                      <TableCell>{memo.invoiceNumber || '-'}</TableCell>
                      <TableCell>{formatDate(memo.memoDate)}</TableCell>
                      <TableCell className="text-right">{formatNumber(memo.grossAmount, 2)} €</TableCell>
                      <TableCell>{memo.reason}</TableCell>
                      <TableCell>
                        <Badge variant={memo.settled ? 'default' : 'outline'}>
                          {memo.settled ? t('crud.fields.settled') : t('crud.fields.open')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {!memo.settled && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSettle(memo)}
                          >
                            {t('crud.actions.settle')}
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="debit">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.entities.debitMemo')}</CardTitle>
                <Button onClick={handleCreateMemo}>
                  <Plus className="h-4 w-4 mr-2" />
                  {t('crud.actions.createDebitMemo')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('crud.fields.number')}</TableHead>
                    <TableHead>{t('crud.entities.supplier')}</TableHead>
                    <TableHead>{t('crud.fields.invoiceNumber')}</TableHead>
                    <TableHead>{t('crud.fields.date')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.grossAmount')}</TableHead>
                    <TableHead>{t('crud.fields.reason')}</TableHead>
                    <TableHead>{t('crud.fields.status')}</TableHead>
                    <TableHead>{t('crud.actions.actions')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {debitMemos.map(memo => (
                    <TableRow key={memo.id}>
                      <TableCell className="font-medium">{memo.number}</TableCell>
                      <TableCell>{memo.supplierName}</TableCell>
                      <TableCell>{memo.invoiceNumber || '-'}</TableCell>
                      <TableCell>{formatDate(memo.memoDate)}</TableCell>
                      <TableCell className="text-right">{formatNumber(memo.grossAmount, 2)} €</TableCell>
                      <TableCell>{memo.reason}</TableCell>
                      <TableCell>
                        <Badge variant={memo.settled ? 'default' : 'outline'}>
                          {memo.settled ? t('crud.fields.settled') : t('crud.fields.open')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {!memo.settled && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleSettle(memo)}
                          >
                            {t('crud.actions.settle')}
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Create Memo Dialog */}
      <Dialog open={memoDialogOpen} onOpenChange={setMemoDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {activeTab === 'credit' 
                ? t('crud.actions.createCreditMemo')
                : t('crud.actions.createDebitMemo')}
            </DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.createMemo.description')}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="supplierId">{t('crud.entities.supplier')} *</Label>
                <NativeSelect
                  value={memoData.supplierId}
                  onValueChange={(value) => setMemoData(prev => ({ ...prev, supplierId: value }))}
                  placeholder={t('crud.tooltips.placeholders.selectSupplier')}
                  options={Array.from(new Set(openInvoices.map((inv) => inv.supplierId))).map((supplierId) => {
                    const supplier = openInvoices.find((inv) => inv.supplierId === supplierId)
                    return {
                      value: supplierId,
                      label: supplier?.supplierName || supplierId,
                    }
                  })}
                />
              </div>
              <div>
                <Label htmlFor="invoiceId">{t('crud.fields.invoiceNumber')}</Label>
                <NativeSelect
                  value={memoData.invoiceId ?? ''}
                  onValueChange={(value) => setMemoData(prev => ({ ...prev, invoiceId: value }))}
                  placeholder={t('crud.tooltips.placeholders.selectInvoice')}
                  options={[
                    { value: '', label: '-' },
                    ...openInvoices
                      .filter((inv) => inv.supplierId === memoData.supplierId)
                      .map((inv) => ({
                        value: inv.id,
                        label: `${inv.number} (${formatNumber(inv.openAmount, 2)} EUR)`,
                      })),
                  ]}
                />
              </div>
              <div>
                <Label htmlFor="memoDate">{t('crud.fields.date')} *</Label>
                <Input
                  id="memoDate"
                  type="date"
                  value={memoData.memoDate}
                  onChange={(e) => setMemoData(prev => ({ ...prev, memoDate: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div>
              <Label htmlFor="reason">{t('crud.fields.reason')} *</Label>
              <Input
                id="reason"
                value={memoData.reason}
                onChange={(e) => setMemoData(prev => ({ ...prev, reason: e.target.value }))}
                placeholder={t('crud.tooltips.placeholders.reason')}
                required
              />
            </div>

            <div>
              <Label htmlFor="notes">{t('crud.fields.notes')}</Label>
              <Textarea
                id="notes"
                value={memoData.notes}
                onChange={(e) => setMemoData(prev => ({ ...prev, notes: e.target.value }))}
                placeholder={t('crud.tooltips.placeholders.notes')}
                rows={3}
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <Label>{t('crud.fields.items')} *</Label>
                <Button type="button" variant="outline" size="sm" onClick={addMemoItem}>
                  <Plus className="h-4 w-4 mr-2" />
                  {t('crud.actions.addItem')}
                </Button>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('crud.fields.product')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.quantity')}</TableHead>
                    <TableHead>{t('crud.fields.unit')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.unitPrice')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.taxRate')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.netAmount')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.grossAmount')}</TableHead>
                    <TableHead>{t('crud.fields.itemReason')}</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {memoData.items.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Input
                          value={item.productName}
                          onChange={(e) => updateMemoItem(index, 'productName', e.target.value)}
                          placeholder={t('crud.tooltips.placeholders.productName')}
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        <Input
                          type="number"
                          min="0"
                          step="0.01"
                          value={item.quantity}
                          onChange={(e) => updateMemoItem(index, 'quantity', Number(e.target.value))}
                          className="w-20"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          value={item.unit}
                          onChange={(e) => updateMemoItem(index, 'unit', e.target.value)}
                          className="w-16"
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        <Input
                          type="number"
                          min="0"
                          step="0.01"
                          value={item.unitPrice}
                          onChange={(e) => updateMemoItem(index, 'unitPrice', Number(e.target.value))}
                          className="w-24"
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        <Input
                          type="number"
                          min="0"
                          max="100"
                          step="0.1"
                          value={item.taxRate}
                          onChange={(e) => updateMemoItem(index, 'taxRate', Number(e.target.value))}
                          className="w-20"
                        />
                      </TableCell>
                      <TableCell className="text-right">{formatNumber(item.netAmount, 2)} €</TableCell>
                      <TableCell className="text-right">{formatNumber(item.grossAmount, 2)} €</TableCell>
                      <TableCell>
                        <Input
                          value={item.reason}
                          onChange={(e) => updateMemoItem(index, 'reason', e.target.value)}
                          placeholder={t('crud.tooltips.placeholders.itemReason')}
                          className="w-32"
                        />
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeMemoItem(index)}
                        >
                          <XCircle className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setMemoDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleSaveMemo}
              disabled={loading || !memoData.reason || memoData.reason.length < 10 || memoData.items.length === 0}
            >
              {loading ? t('common.loading') : t('common.save')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Settlement Dialog */}
      <Dialog open={settlementDialogOpen} onOpenChange={setSettlementDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{t('crud.actions.settle')}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.settle.description')}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {selectedMemo && (
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="font-medium">{selectedMemo.number}</p>
                <p className="text-sm text-muted-foreground">
                  {t('crud.fields.grossAmount')}: {formatNumber(selectedMemo.grossAmount, 2)} €
                </p>
              </div>
            )}
            <div>
              <Label>{t('crud.fields.selectInvoicesForSettlement')}</Label>
              <div className="space-y-2 mt-2 max-h-60 overflow-y-auto">
                {openInvoices
                  .filter(inv => inv.supplierId === (selectedMemo?.supplierId || ''))
                  .map(inv => (
                    <div key={inv.id} className="flex items-center space-x-2 p-2 border rounded">
                      <input
                        type="checkbox"
                        checked={memoData.settlementInvoiceIds.includes(inv.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setMemoData(prev => ({
                              ...prev,
                              settlementInvoiceIds: [...prev.settlementInvoiceIds, inv.id],
                            }))
                          } else {
                            setMemoData(prev => ({
                              ...prev,
                              settlementInvoiceIds: prev.settlementInvoiceIds.filter(id => id !== inv.id),
                            }))
                          }
                        }}
                      />
                      <div className="flex-1">
                        <p className="font-medium">{inv.number}</p>
                        <p className="text-sm text-muted-foreground">
                          {formatDate(inv.invoiceDate)} - {formatNumber(inv.openAmount, 2)} €
                        </p>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSettlementDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleSaveSettlement}
              disabled={loading || memoData.settlementInvoiceIds.length === 0}
            >
              {loading ? t('common.loading') : t('common.save')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

