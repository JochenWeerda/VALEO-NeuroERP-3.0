import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
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
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { PackageX, ArrowLeft, CheckCircle, AlertTriangle } from 'lucide-react'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'

type GoodsReceiptItem = {
  id: string
  goodsReceiptId: string
  purchaseOrderItemId: string
  productId: string
  productName: string
  quantityReceived: number
  quantityReturned: number
  unit: string
  price: number
  condition: string
}

type GoodsReceipt = {
  id: string
  number: string
  purchaseOrderId: string
  purchaseOrderNumber: string
  supplierId: string
  supplierName: string
  receivedDate: string
  status: string
  items: GoodsReceiptItem[]
}

type ReturnItem = {
  goodsReceiptItemId: string
  productId: string
  productName: string
  quantityReturned: number
  unit: string
  price: number
  reason: string
  creditMemoRequested: boolean
}

type ReturnData = {
  goodsReceiptId: string
  returnDate: string
  returnReason: string
  returnNotes: string
  items: ReturnItem[]
  creditMemoRequested: boolean
}

export default function RetourenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { grId } = useParams<{ grId?: string }>()
  const entityType = 'goodsReturn'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Retoure')

  const [loading, setLoading] = useState(false)
  const [goodsReceipt, setGoodsReceipt] = useState<GoodsReceipt | null>(null)
  const [goodsReceipts, setGoodsReceipts] = useState<GoodsReceipt[]>([])
  const [selectedGrId, setSelectedGrId] = useState<string>(grId || '')
  const [returnDialogOpen, setReturnDialogOpen] = useState(false)
  const [returnData, setReturnData] = useState<ReturnData>({
    goodsReceiptId: '',
    returnDate: new Date().toISOString().split('T')[0],
    returnReason: '',
    returnNotes: '',
    items: [],
    creditMemoRequested: false,
  })

  // Lade Wareneingänge
  useEffect(() => {
    loadGoodsReceipts()
  }, [])

  // Lade Wareneingang wenn ausgewählt
  useEffect(() => {
    if (selectedGrId) {
      loadGoodsReceipt(selectedGrId)
    }
  }, [selectedGrId])

  const loadGoodsReceipts = async () => {
    try {
      setLoading(true)
      // Mock: In Produktion würde hier die API aufgerufen
      const mockReceipts: GoodsReceipt[] = [
        {
          id: 'gr-001',
          number: 'GR-2025-001',
          purchaseOrderId: 'po-001',
          purchaseOrderNumber: 'PO-2025-001',
          supplierId: 'supplier-001',
          supplierName: 'Lieferant A',
          receivedDate: '2025-01-15',
          status: 'RECEIVED',
          items: [
            {
              id: 'gri-001',
              goodsReceiptId: 'gr-001',
              purchaseOrderItemId: 'poi-001',
              productId: 'prod-001',
              productName: 'Produkt A',
              quantityReceived: 100,
              quantityReturned: 0,
              unit: 'Stk',
              price: 10.50,
              condition: 'GOOD',
            },
          ],
        },
      ]
      setGoodsReceipts(mockReceipts)
    } catch (error) {
      console.error('Fehler beim Laden der Wareneingänge:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: t('crud.messages.loadErrorDescription'),
      })
    } finally {
      setLoading(false)
    }
  }

  const loadGoodsReceipt = async (id: string) => {
    try {
      setLoading(true)
      // Mock: In Produktion würde hier die API aufgerufen
      const mockReceipt = goodsReceipts.find(gr => gr.id === id)
      if (mockReceipt) {
        setGoodsReceipt(mockReceipt)
        setReturnData(prev => ({
          ...prev,
          goodsReceiptId: id,
          items: mockReceipt.items.map(item => ({
            goodsReceiptItemId: item.id,
            productId: item.productId,
            productName: item.productName,
            quantityReturned: 0,
            unit: item.unit,
            price: item.price,
            reason: '',
            creditMemoRequested: false,
          })),
        }))
      }
    } catch (error) {
      console.error('Fehler beim Laden des Wareneingangs:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: t('crud.messages.loadErrorDescription'),
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCreateReturn = () => {
    if (!selectedGrId) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.selectGoodsReceipt'),
      })
      return
    }
    setReturnDialogOpen(true)
  }

  const handleSaveReturn = async () => {
    if (!returnData.returnReason || returnData.returnReason.length < 10) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.reasonMinLength'),
      })
      return
    }

    const hasReturnItems = returnData.items.some(item => item.quantityReturned > 0)
    if (!hasReturnItems) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.selectReturnItems'),
      })
      return
    }

    setLoading(true)
    try {
      // API-Call würde hier erfolgen
      await apiClient.post('/api/einkauf/retouren', {
        goodsReceiptId: returnData.goodsReceiptId,
        returnDate: returnData.returnDate,
        returnReason: returnData.returnReason,
        returnNotes: returnData.returnNotes,
        items: returnData.items.filter(item => item.quantityReturned > 0),
        creditMemoRequested: returnData.creditMemoRequested,
      })

      toast({
        title: t('crud.messages.createSuccess', { entityType: entityTypeLabel }),
      })

      setReturnDialogOpen(false)
      setReturnData({
        goodsReceiptId: '',
        returnDate: new Date().toISOString().split('T')[0],
        returnReason: '',
        returnNotes: '',
        items: [],
        creditMemoRequested: false,
      })
      
      // Reload goods receipts
      loadGoodsReceipts()
      if (selectedGrId) {
        loadGoodsReceipt(selectedGrId)
      }
    } catch (error: any) {
      console.error('Fehler beim Erstellen der Retoure:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.createError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t('crud.entities.goodsReturn')}</h1>
          <p className="text-muted-foreground mt-1">
            {t('crud.descriptions.goodsReturn', { defaultValue: 'Retouren an Lieferanten verwalten' })}
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => navigate('/einkauf/wareneingang')}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          {t('common.back')}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.fields.selectGoodsReceipt')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Label htmlFor="goodsReceipt">{t('crud.fields.goodsReceipt')}</Label>
              <Select value={selectedGrId} onValueChange={setSelectedGrId}>
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.tooltips.placeholders.selectGoodsReceipt')} />
                </SelectTrigger>
                <SelectContent>
                  {goodsReceipts.map(gr => (
                    <SelectItem key={gr.id} value={gr.id}>
                      {gr.number} - {gr.supplierName} ({formatDate(gr.receivedDate)})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {goodsReceipt && (
        <Card>
          <CardHeader>
            <CardTitle>{t('crud.fields.goodsReceiptDetails')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>{t('crud.fields.number')}</Label>
                  <p className="font-medium">{goodsReceipt.number}</p>
                </div>
                <div>
                  <Label>{t('crud.entities.supplier')}</Label>
                  <p className="font-medium">{goodsReceipt.supplierName}</p>
                </div>
                <div>
                  <Label>{t('crud.fields.purchaseOrder')}</Label>
                  <p className="font-medium">{goodsReceipt.purchaseOrderNumber}</p>
                </div>
                <div>
                  <Label>{t('crud.fields.receivedDate')}</Label>
                  <p className="font-medium">{formatDate(goodsReceipt.receivedDate)}</p>
                </div>
              </div>

              <div>
                <Label>{t('crud.fields.items')}</Label>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.fields.product')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.quantityReceived')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.quantityReturned')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.unit')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.price')}</TableHead>
                      <TableHead>{t('crud.fields.condition')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {goodsReceipt.items.map(item => (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{item.productName}</TableCell>
                        <TableCell className="text-right">{formatNumber(item.quantityReceived, 2)}</TableCell>
                        <TableCell className="text-right">
                          <Badge variant={item.quantityReturned > 0 ? 'destructive' : 'outline'}>
                            {formatNumber(item.quantityReturned, 2)}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">{item.unit}</TableCell>
                        <TableCell className="text-right">{formatNumber(item.price, 2)} €</TableCell>
                        <TableCell>
                          <Badge variant="outline">{item.condition}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              <Button
                onClick={handleCreateReturn}
                disabled={loading || goodsReceipt.items.every(item => item.quantityReturned >= item.quantityReceived)}
              >
                <PackageX className="h-4 w-4 mr-2" />
                {t('crud.actions.createReturn')}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Return Dialog */}
      <Dialog open={returnDialogOpen} onOpenChange={setReturnDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('crud.actions.createReturn')}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.createReturn.description')}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="returnDate">{t('crud.fields.returnDate')} *</Label>
                <Input
                  id="returnDate"
                  type="date"
                  value={returnData.returnDate}
                  onChange={(e) => setReturnData(prev => ({ ...prev, returnDate: e.target.value }))}
                  required
                />
              </div>
              <div>
                <Label htmlFor="creditMemoRequested">{t('crud.fields.creditMemoRequested')}</Label>
                <Select
                  value={returnData.creditMemoRequested ? 'yes' : 'no'}
                  onValueChange={(value) => setReturnData(prev => ({ ...prev, creditMemoRequested: value === 'yes' }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="yes">{t('common.yes')}</SelectItem>
                    <SelectItem value="no">{t('common.no')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div>
              <Label htmlFor="returnReason">{t('crud.fields.returnReason')} *</Label>
              <Select
                value={returnData.returnReason}
                onValueChange={(value) => setReturnData(prev => ({ ...prev, returnReason: value }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.tooltips.placeholders.selectReturnReason')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="DEFECTIVE">{t('crud.fields.returnReasonDefective')}</SelectItem>
                  <SelectItem value="WRONG_ITEM">{t('crud.fields.returnReasonWrongItem')}</SelectItem>
                  <SelectItem value="DAMAGED">{t('crud.fields.returnReasonDamaged')}</SelectItem>
                  <SelectItem value="OVER_DELIVERY">{t('crud.fields.returnReasonOverDelivery')}</SelectItem>
                  <SelectItem value="QUALITY_ISSUE">{t('crud.fields.returnReasonQualityIssue')}</SelectItem>
                  <SelectItem value="OTHER">{t('crud.fields.returnReasonOther')}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="returnNotes">{t('crud.fields.returnNotes')}</Label>
              <Textarea
                id="returnNotes"
                value={returnData.returnNotes}
                onChange={(e) => setReturnData(prev => ({ ...prev, returnNotes: e.target.value }))}
                placeholder={t('crud.tooltips.placeholders.returnNotes')}
                rows={3}
              />
            </div>

            <div>
              <Label>{t('crud.fields.returnItems')}</Label>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('crud.fields.product')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.quantityReceived')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.quantityReturned')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.unit')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.price')}</TableHead>
                    <TableHead>{t('crud.fields.itemReason')}</TableHead>
                    <TableHead>{t('crud.fields.creditMemo')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {returnData.items.map((item, index) => {
                    const grItem = goodsReceipt?.items.find(gi => gi.id === item.goodsReceiptItemId)
                    const maxReturnable = (grItem?.quantityReceived || 0) - (grItem?.quantityReturned || 0)
                    
                    return (
                      <TableRow key={item.goodsReceiptItemId}>
                        <TableCell className="font-medium">{item.productName}</TableCell>
                        <TableCell className="text-right">{formatNumber(grItem?.quantityReceived || 0, 2)}</TableCell>
                        <TableCell className="text-right">
                          <Input
                            type="number"
                            min="0"
                            max={maxReturnable}
                            step="0.01"
                            value={item.quantityReturned}
                            onChange={(e) => {
                              const updatedItems = [...returnData.items]
                              updatedItems[index].quantityReturned = Number(e.target.value)
                              setReturnData(prev => ({ ...prev, items: updatedItems }))
                            }}
                            className="w-24"
                          />
                        </TableCell>
                        <TableCell className="text-right">{item.unit}</TableCell>
                        <TableCell className="text-right">{formatNumber(item.price, 2)} €</TableCell>
                        <TableCell>
                          <Input
                            type="text"
                            value={item.reason}
                            onChange={(e) => {
                              const updatedItems = [...returnData.items]
                              updatedItems[index].reason = e.target.value
                              setReturnData(prev => ({ ...prev, items: updatedItems }))
                            }}
                            placeholder={t('crud.tooltips.placeholders.itemReason')}
                            className="w-32"
                          />
                        </TableCell>
                        <TableCell>
                          <Select
                            value={item.creditMemoRequested ? 'yes' : 'no'}
                            onValueChange={(value) => {
                              const updatedItems = [...returnData.items]
                              updatedItems[index].creditMemoRequested = value === 'yes'
                              setReturnData(prev => ({ ...prev, items: updatedItems }))
                            }}
                          >
                            <SelectTrigger className="w-20">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="yes">{t('common.yes')}</SelectItem>
                              <SelectItem value="no">{t('common.no')}</SelectItem>
                            </SelectContent>
                          </Select>
                        </TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            </div>

            {returnData.creditMemoRequested && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-4 w-4 text-blue-600 mt-0.5" />
                  <div className="text-sm text-blue-800">
                    {t('crud.dialogs.createReturn.creditMemoInfo')}
                  </div>
                </div>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setReturnDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleSaveReturn}
              disabled={loading || !returnData.returnReason || returnData.returnReason.length < 10}
            >
              {loading ? t('common.loading') : t('common.save')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

