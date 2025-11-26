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
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { Package, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

type PurchaseOrderItem = {
  id: string
  productId: string
  productName: string
  quantityOrdered: number
  quantityReceived: number
  unit: string
  price: number
}

type PurchaseOrder = {
  id: string
  number: string
  supplierId: string
  supplierName: string
  status: string
  items: PurchaseOrderItem[]
}

type GoodsReceiptItem = {
  purchaseOrderItemId: string
  receivedQuantity: number
  acceptedQuantity: number
  rejectedQuantity: number
  condition: 'PERFECT' | 'GOOD' | 'DAMAGED' | 'DEFECTIVE'
}

type GoodsReceiptData = {
  purchaseOrderId: string
  deliveryNoteNumber: string
  receivedDate: string
  receivedBy: string
  receivedLocation: string
  items: GoodsReceiptItem[]
  qualityInspectionStatus: 'PENDING' | 'PASSED' | 'FAILED' | 'CONDITIONAL'
  inspectionNotes?: string
  damageReport?: string
}

export default function WareneingangPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { poId } = useParams<{ poId?: string }>()
  const entityType = 'goodsReceipt'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Wareneingang')

  const [loading, setLoading] = useState(false)
  const [purchaseOrder, setPurchaseOrder] = useState<PurchaseOrder | null>(null)
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([])
  const [selectedPoId, setSelectedPoId] = useState<string>(poId || '')
  const [receiptData, setReceiptData] = useState<GoodsReceiptData>({
    purchaseOrderId: '',
    deliveryNoteNumber: '',
    receivedDate: new Date().toISOString().split('T')[0],
    receivedBy: '',
    receivedLocation: '',
    items: [],
    qualityInspectionStatus: 'PENDING',
  })

  // Lade Bestellungen
  useEffect(() => {
    loadPurchaseOrders()
  }, [])

  // Lade Bestellung wenn ausgewählt
  useEffect(() => {
    if (selectedPoId) {
      loadPurchaseOrder(selectedPoId)
    }
  }, [selectedPoId])

  const loadPurchaseOrders = async () => {
    try {
      // Versuche MCP-API, dann Fallback
      try {
        const response = await fetch('/api/mcp/documents/purchase_order?status=FREIGEGEBEN&limit=100')
        if (response.ok) {
          const result = await response.json()
          if (result.ok && result.data) {
            setPurchaseOrders(result.data.map((po: any) => ({
              id: po.id || po.number,
              number: po.number,
              supplierId: po.supplierId || '',
              supplierName: po.supplierName || po.supplier?.name || '',
              status: po.status,
              items: po.lines?.map((line: any) => ({
                id: line.id || `${po.id}-${line.productId}`,
                productId: line.productId,
                productName: line.productName || line.product?.name || '',
                quantityOrdered: line.qty || line.quantity || 0,
                quantityReceived: line.quantityReceived || 0,
                unit: line.unit || 'Stk',
                price: line.price || 0,
              })) || [],
            })))
            return
          }
        }
      } catch (mcpError) {
        console.warn('MCP-API nicht verfügbar, verwende Fallback:', mcpError)
      }

      // Fallback
      const response = await apiClient.get('/einkauf/bestellungen?status=FREIGEGEBEN')
      if (response.data?.data) {
        setPurchaseOrders(response.data.data)
      }
    } catch (error) {
      console.error('Fehler beim Laden der Bestellungen:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadDataError'),
      })
    }
  }

  const loadPurchaseOrder = async (orderId: string) => {
    setLoading(true)
    try {
      // Versuche MCP-API, dann Fallback
      try {
        const response = await fetch(`/api/mcp/documents/purchase_order/${orderId}`)
        if (response.ok) {
          const result = await response.json()
          if (result.ok && result.data) {
            const po = result.data
            setPurchaseOrder({
              id: po.id || po.number,
              number: po.number,
              supplierId: po.supplierId || '',
              supplierName: po.supplierName || po.supplier?.name || '',
              status: po.status,
              items: po.lines?.map((line: any) => ({
                id: line.id || `${po.id}-${line.productId}`,
                productId: line.productId,
                productName: line.productName || line.product?.name || '',
                quantityOrdered: line.qty || line.quantity || 0,
                quantityReceived: line.quantityReceived || 0,
                unit: line.unit || 'Stk',
                price: line.price || 0,
              })) || [],
            })
            // Initialisiere Receipt Items
            const items: GoodsReceiptItem[] = po.lines?.map((line: any) => ({
              purchaseOrderItemId: line.id || `${po.id}-${line.productId}`,
              receivedQuantity: 0,
              acceptedQuantity: 0,
              rejectedQuantity: 0,
              condition: 'PERFECT' as const,
            })) || []
            setReceiptData(prev => ({
              ...prev,
              purchaseOrderId: orderId,
              items,
            }))
            setLoading(false)
            return
          }
        }
      } catch (mcpError) {
        console.warn('MCP-API nicht verfügbar, verwende Fallback:', mcpError)
      }

      // Fallback
      const response = await apiClient.get(`/einkauf/bestellungen/${orderId}`)
      if (response.data) {
        const po = response.data
        setPurchaseOrder(po)
        const items: GoodsReceiptItem[] = (po.items || []).map((item: any) => ({
          purchaseOrderItemId: item.id,
          receivedQuantity: 0,
          acceptedQuantity: 0,
          rejectedQuantity: 0,
          condition: 'PERFECT' as const,
        }))
        setReceiptData(prev => ({
          ...prev,
          purchaseOrderId: orderId,
          items,
        }))
      }
    } catch (error) {
      console.error('Fehler beim Laden der Bestellung:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadDataError'),
      })
    } finally {
      setLoading(false)
    }
  }

  const updateReceiptItem = (index: number, field: keyof GoodsReceiptItem, value: any) => {
    setReceiptData(prev => {
      const newItems = [...prev.items]
      newItems[index] = { ...newItems[index], [field]: value }
      
      // Auto-berechnen: acceptedQuantity = receivedQuantity - rejectedQuantity
      if (field === 'receivedQuantity' || field === 'rejectedQuantity') {
        const received = field === 'receivedQuantity' ? value : newItems[index].receivedQuantity
        const rejected = field === 'rejectedQuantity' ? value : newItems[index].rejectedQuantity
        newItems[index].acceptedQuantity = Math.max(0, received - rejected)
      }
      
      return { ...prev, items: newItems }
    })
  }

  const handleSubmit = async () => {
    if (!receiptData.purchaseOrderId) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.fields.purchaseOrder') + ' ist erforderlich',
      })
      return
    }

    if (!receiptData.receivedBy || !receiptData.receivedLocation) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: 'Empfänger und Lagerort sind erforderlich',
      })
      return
    }

    const hasItems = receiptData.items.some(item => item.receivedQuantity > 0)
    if (!hasItems) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: 'Mindestens eine Position muss eine Menge > 0 haben',
      })
      return
    }

    setLoading(true)
    try {
      // Rufe Backend-API auf
      const response = await apiClient.post(
        `/api/purchase-workflow/orders/${receiptData.purchaseOrderId}/goods-receipt`,
        {
          deliveryNoteNumber: receiptData.deliveryNoteNumber,
          receivedDate: new Date(receiptData.receivedDate).toISOString(),
          receivedBy: receiptData.receivedBy,
          receivedLocation: receiptData.receivedLocation,
          items: receiptData.items.filter(item => item.receivedQuantity > 0),
          qualityInspectionStatus: receiptData.qualityInspectionStatus,
          inspectionNotes: receiptData.inspectionNotes,
          damageReport: receiptData.damageReport,
        }
      )

      toast({
        title: t('crud.messages.createSuccess', { entityType: entityTypeLabel }),
        description: `Wareneingang für Bestellung ${purchaseOrder?.number} erfolgreich gebucht`,
      })

      navigate('/einkauf/bestellungen')
    } catch (error: any) {
      console.error('Fehler beim Buchen des Wareneingangs:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.createError', { entityType: entityTypeLabel }),
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const getRemainingQuantity = (item: PurchaseOrderItem) => {
    return item.quantityOrdered - item.quantityReceived
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{entityTypeLabel}</h1>
          <p className="text-muted-foreground">{t('crud.actions.create')}</p>
        </div>
        <Button variant="outline" onClick={() => navigate('/einkauf/bestellungen')}>
          {t('common.cancel')}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.detail.basicInfo')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="purchaseOrder">{t('crud.entities.purchaseOrder')} *</Label>
              <Select value={selectedPoId} onValueChange={setSelectedPoId}>
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.fields.selectPurchaseOrder')} />
                </SelectTrigger>
                <SelectContent>
                  {purchaseOrders.map(po => (
                    <SelectItem key={po.id} value={po.id}>
                      {po.number} - {po.supplierName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="deliveryNoteNumber">{t('crud.fields.deliveryNoteNumber')}</Label>
              <Input
                id="deliveryNoteNumber"
                value={receiptData.deliveryNoteNumber}
                onChange={(e) => setReceiptData(prev => ({ ...prev, deliveryNoteNumber: e.target.value }))}
                placeholder="LS-2025-001"
              />
            </div>

            <div>
              <Label htmlFor="receivedDate">{t('crud.fields.receivedDate')} *</Label>
              <Input
                id="receivedDate"
                type="date"
                value={receiptData.receivedDate}
                onChange={(e) => setReceiptData(prev => ({ ...prev, receivedDate: e.target.value }))}
                required
              />
            </div>

            <div>
              <Label htmlFor="receivedBy">{t('crud.fields.receivedBy')} *</Label>
              <Input
                id="receivedBy"
                value={receiptData.receivedBy}
                onChange={(e) => setReceiptData(prev => ({ ...prev, receivedBy: e.target.value }))}
                placeholder="Name des Empfängers"
                required
              />
            </div>

            <div>
              <Label htmlFor="receivedLocation">{t('crud.fields.receivedLocation')} *</Label>
              <Input
                id="receivedLocation"
                value={receiptData.receivedLocation}
                onChange={(e) => setReceiptData(prev => ({ ...prev, receivedLocation: e.target.value }))}
                placeholder="Lagerort"
                required
              />
            </div>

            <div>
              <Label htmlFor="qualityInspectionStatus">{t('crud.fields.qualityInspectionStatus')}</Label>
              <Select
                value={receiptData.qualityInspectionStatus}
                onValueChange={(value: any) => setReceiptData(prev => ({ ...prev, qualityInspectionStatus: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="PENDING">{t('status.pending')}</SelectItem>
                  <SelectItem value="PASSED">{t('status.approved')}</SelectItem>
                  <SelectItem value="FAILED">{t('status.rejected')}</SelectItem>
                  <SelectItem value="CONDITIONAL">{t('status.partial')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {purchaseOrder && (
        <Card>
          <CardHeader>
            <CardTitle>
              {t('crud.fields.items')} - {t('crud.entities.purchaseOrder')} {purchaseOrder.number}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('crud.fields.product')}</TableHead>
                  <TableHead className="text-right">{t('crud.fields.quantityOrdered')}</TableHead>
                  <TableHead className="text-right">{t('crud.fields.quantityReceived')}</TableHead>
                  <TableHead className="text-right">{t('crud.fields.remaining')}</TableHead>
                  <TableHead className="text-right">{t('crud.fields.receivedQuantity')}</TableHead>
                  <TableHead className="text-right">{t('crud.fields.acceptedQuantity')}</TableHead>
                  <TableHead className="text-right">{t('crud.fields.rejectedQuantity')}</TableHead>
                  <TableHead>{t('crud.fields.condition')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {purchaseOrder.items.map((item, index) => {
                  const receiptItem = receiptData.items[index] || {
                    purchaseOrderItemId: item.id,
                    receivedQuantity: 0,
                    acceptedQuantity: 0,
                    rejectedQuantity: 0,
                    condition: 'PERFECT' as const,
                  }
                  const remaining = getRemainingQuantity(item)
                  
                  return (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">{item.productName}</TableCell>
                      <TableCell className="text-right">
                        {item.quantityOrdered} {item.unit}
                      </TableCell>
                      <TableCell className="text-right">
                        {item.quantityReceived} {item.unit}
                      </TableCell>
                      <TableCell className="text-right">
                        <Badge variant={remaining > 0 ? 'default' : 'outline'}>
                          {remaining} {item.unit}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          min="0"
                          max={remaining}
                          step="0.001"
                          value={receiptItem.receivedQuantity}
                          onChange={(e) => updateReceiptItem(index, 'receivedQuantity', Number(e.target.value))}
                          className="w-24"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          min="0"
                          value={receiptItem.acceptedQuantity}
                          onChange={(e) => updateReceiptItem(index, 'acceptedQuantity', Number(e.target.value))}
                          className="w-24"
                          readOnly
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          min="0"
                          value={receiptItem.rejectedQuantity}
                          onChange={(e) => updateReceiptItem(index, 'rejectedQuantity', Number(e.target.value))}
                          className="w-24"
                        />
                      </TableCell>
                      <TableCell>
                        <Select
                          value={receiptItem.condition}
                          onValueChange={(value: any) => updateReceiptItem(index, 'condition', value)}
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="PERFECT">{t('crud.fields.conditionPerfect')}</SelectItem>
                            <SelectItem value="GOOD">{t('crud.fields.conditionGood')}</SelectItem>
                            <SelectItem value="DAMAGED">{t('crud.fields.conditionDamaged')}</SelectItem>
                            <SelectItem value="DEFECTIVE">{t('crud.fields.conditionDefective')}</SelectItem>
                          </SelectContent>
                        </Select>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={() => navigate('/einkauf/bestellungen')} disabled={loading}>
          {t('common.cancel')}
        </Button>
        <Button onClick={handleSubmit} disabled={loading || !purchaseOrder}>
          <Package className="h-4 w-4 mr-2" />
          {loading ? t('common.loading') : t('crud.actions.save')}
        </Button>
      </div>
    </div>
  )
}

