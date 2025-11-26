import { useState, useEffect } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { FileText, Plus, ArrowLeft, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
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
  memoDate: string
  reason: string
  notes: string
  items: MemoItem[]
  settlementInvoiceIds: string[]
}

export default function GutschriftenBelastungenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { type } = useParams<{ type?: string }>()
  const [searchParams] = useSearchParams()
  const invoiceId = searchParams.get('invoiceId')
  
  const [activeTab, setActiveTab] = useState<'credit' | 'debit'>(type === 'debit' ? 'debit' : 'credit')
  const [loading, setLoading] = useState(false)
  const [creditMemos, setCreditMemos] = useState<CreditMemo[]>([])
  const [debitMemos, setDebitMemos] = useState<DebitMemo[]>([])
  const [openInvoices, setOpenInvoices] = useState<APInvoice[]>([])
  const [selectedInvoice, setSelectedInvoice] = useState<APInvoice | null>(null)
  const [memoDialogOpen, setMemoDialogOpen] = useState(false)
  const [settlementDialogOpen, setSettlementDialogOpen] = useState(false)
  const [selectedMemo, setSelectedMemo] = useState<CreditMemo | DebitMemo | null>(null)
  const [memoData, setMemoData] = useState<MemoData>({
    supplierId: '',
    invoiceId: invoiceId || '',
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
    if (invoiceId) {
      const invoice = openInvoices.find(inv => inv.id === invoiceId)
      if (invoice) {
        setSelectedInvoice(invoice)
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
      const response = await apiClient.get('/api/v1/einkauf/credit-memos')
      if (response.data) {
        setCreditMemos(response.data)
      }
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
      const response = await apiClient.get('/api/v1/einkauf/debit-memos')
      if (response.data) {
        setDebitMemos(response.data)
      }
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
      const response = await apiClient.get('/api/v1/ap/invoices?status=APPROVED')
      if (response.data) {
        // Transform API response to match our type
        const invoices: APInvoice[] = response.data.map((inv: any) => ({
          id: inv.id || inv.number,
          number: inv.number,
          supplierId: inv.customerId || inv.supplierId, // AP invoices use customerId for supplier
          supplierName: inv.customerName || inv.supplierName || '',
          invoiceDate: inv.date || inv.invoiceDate,
          dueDate: inv.dueDate,
          netAmount: inv.subtotalNet || inv.netAmount || 0,
          taxAmount: inv.totalTax || inv.taxAmount || 0,
          grossAmount: inv.totalGross || inv.grossAmount || 0,
          status: inv.status,
          openAmount: inv.totalGross || inv.grossAmount || 0, // TODO: Calculate from open items
        }))
        setOpenInvoices(invoices)
      }
    } catch (error) {
      console.error('Fehler beim Laden der offenen Rechnungen:', error)
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

  const entityType = activeTab === 'credit' ? 'creditMemo' : 'debitMemo'
  const entityTypeLabel = getEntityTypeLabel(
    t,
    entityType,
    activeTab === 'credit' ? 'Gutschrift' : 'Belastung'
  )

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
                <Select
                  value={memoData.supplierId}
                  onValueChange={(value) => setMemoData(prev => ({ ...prev, supplierId: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={t('crud.tooltips.placeholders.selectSupplier')} />
                  </SelectTrigger>
                  <SelectContent>
                    {Array.from(new Set(openInvoices.map(inv => inv.supplierId))).map(supplierId => {
                      const supplier = openInvoices.find(inv => inv.supplierId === supplierId)
                      return (
                        <SelectItem key={supplierId} value={supplierId}>
                          {supplier?.supplierName || supplierId}
                        </SelectItem>
                      )
                    })}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="invoiceId">{t('crud.fields.invoiceNumber')}</Label>
                <Select
                  value={memoData.invoiceId}
                  onValueChange={(value) => setMemoData(prev => ({ ...prev, invoiceId: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={t('crud.tooltips.placeholders.selectInvoice')} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">-</SelectItem>
                    {openInvoices
                      .filter(inv => inv.supplierId === memoData.supplierId)
                      .map(inv => (
                        <SelectItem key={inv.id} value={inv.id}>
                          {inv.number} ({formatNumber(inv.openAmount, 2)} €)
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
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

