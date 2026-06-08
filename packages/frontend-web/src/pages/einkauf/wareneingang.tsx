import { useState, useEffect } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { NativeSelect } from '@/components/ui/native-select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { Package } from 'lucide-react'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

type GoodsReceiptRoleFocus = 'all' | 'receiving' | 'procurement' | 'quality' | 'warehouse' | 'finance'

const goodsReceiptRoleProfiles: Array<{ id: GoodsReceiptRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt den Wareneingang fuer Annahme, Einkauf, QS, Lager und Finance.',
  },
  {
    id: 'receiving',
    label: 'Wareneingang',
    description: 'Fokus auf Bestellung, Lieferschein, Empfaenger und Buchung.',
  },
  {
    id: 'procurement',
    label: 'Einkauf',
    description: 'Fokus auf Bestellbezug, Lieferant und offene Restmengen.',
  },
  {
    id: 'quality',
    label: 'QS',
    description: 'Fokus auf Pruefstatus, abgelehnte Mengen und Schadensbericht.',
  },
  {
    id: 'warehouse',
    label: 'Lager',
    description: 'Fokus auf Lagerort, angenommene Mengen und Einlagerungsfolge.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Fokus auf Buchungsnachweis und spaeteren Rechnungsabgleich.',
  },
]

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
  const qualityInspectionOptions = [
    { value: 'PENDING', label: t('status.pending') },
    { value: 'PASSED', label: t('status.approved') },
    { value: 'FAILED', label: t('status.rejected') },
    { value: 'CONDITIONAL', label: t('status.partial') },
  ]
  const conditionOptions = [
    { value: 'PERFECT', label: t('crud.fields.conditionPerfect') },
    { value: 'GOOD', label: t('crud.fields.conditionGood') },
    { value: 'DAMAGED', label: t('crud.fields.conditionDamaged') },
    { value: 'DEFECTIVE', label: t('crud.fields.conditionDefective') },
  ]

  const [loading, setLoading] = useState(false)
  const [purchaseOrder, setPurchaseOrder] = useState<PurchaseOrder | null>(null)
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>([])
  const [selectedPoId, setSelectedPoId] = useState<string>(poId || '')
  const [roleFocus, setRoleFocus] = useState<GoodsReceiptRoleFocus>('all')
  const purchaseOrderOptions = purchaseOrders.map((po) => ({ value: po.id, label: `${po.number} - ${po.supplierName}` }))
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
      const rows = (await apiClient.get<any[]>('/api/v1/purchase-orders?status=FREIGEGEBEN&page=1&pageSize=100')) as unknown as any[]
      setPurchaseOrders(rows.map((po: any) => ({
        id: po.id,
        number: po.purchaseOrderNumber || po.number,
        supplierId: po.supplierId || '',
        supplierName: po.subject || po.supplierName || '',
        status: po.status,
        items: (po.items || []).map((line: any) => ({
          id: line.id || `${po.id}-${line.articleId || line.description}`,
          productId: line.articleId || line.productId || '',
          productName: line.description || line.productName || '',
          quantityOrdered: Number(line.quantity || 0),
          quantityReceived: Number(line.quantityReceived || 0),
          unit: line.unit || 'Stk',
          price: Number(line.unitPrice || line.price || 0),
        })),
      })))
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadDataError'),
      })
    }
  }

  const loadPurchaseOrder = async (orderId: string) => {
    setLoading(true)
    try {
      const po: any = await apiClient.get<any>(`/api/v1/purchase-orders/${orderId}`)
      setPurchaseOrder({
        id: po.id,
        number: po.purchaseOrderNumber || po.number,
        supplierId: po.supplierId || '',
        supplierName: po.subject || po.supplierName || '',
        status: po.status,
        items: (po.items || []).map((line: any) => ({
          id: line.id || `${po.id}-${line.articleId || line.description}`,
          productId: line.articleId || line.productId || '',
          productName: line.description || line.productName || '',
          quantityOrdered: Number(line.quantity || 0),
          quantityReceived: Number(line.quantityReceived || 0),
          unit: line.unit || 'Stk',
          price: Number(line.unitPrice || line.price || 0),
        })),
      })
      const items: GoodsReceiptItem[] = (po.items || []).map((item: any) => ({
        purchaseOrderItemId: item.id || `${po.id}-${item.articleId || item.description}`,
        receivedQuantity: 0,
        acceptedQuantity: 0,
        rejectedQuantity: 0,
        condition: 'PERFECT' as const,
      }))
      setReceiptData((prev) => ({
        ...prev,
        purchaseOrderId: orderId,
        items,
      }))
    } catch (error) {
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
        description: `${t('crud.fields.purchaseOrder')} ist erforderlich`,
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
      await apiClient.post('/api/v1/einkauf/goods-receipts', {
        purchaseOrderId: receiptData.purchaseOrderId,
        deliveryNoteNumber: receiptData.deliveryNoteNumber,
        receivedDate: receiptData.receivedDate,
        receivedBy: receiptData.receivedBy,
        receivedLocation: receiptData.receivedLocation,
        items: receiptData.items.filter(item => item.receivedQuantity > 0),
        qualityInspectionStatus: receiptData.qualityInspectionStatus,
        inspectionNotes: receiptData.inspectionNotes,
        damageReport: receiptData.damageReport,
      })

      toast({
        title: t('crud.messages.createSuccess', { entityType: entityTypeLabel }),
        description: `Wareneingang für Bestellung ${purchaseOrder?.number} erfolgreich gebucht`,
      })

      navigate('/einkauf/bestellungen')
    } catch (error: any) {
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

  const totalReceived = receiptData.items.reduce((sum, item) => sum + Number(item.receivedQuantity || 0), 0)
  const totalAccepted = receiptData.items.reduce((sum, item) => sum + Number(item.acceptedQuantity || 0), 0)
  const totalRejected = receiptData.items.reduce((sum, item) => sum + Number(item.rejectedQuantity || 0), 0)
  const hasPurchaseOrder = Boolean(receiptData.purchaseOrderId && purchaseOrder)
  const hasDeliveryNote = Boolean(receiptData.deliveryNoteNumber.trim())
  const hasRequiredHeader = Boolean(receiptData.receivedBy.trim() && receiptData.receivedLocation.trim())
  const hasReceivedItems = totalReceived > 0
  const hasQualityBlocker = receiptData.qualityInspectionStatus === 'FAILED' || totalRejected > 0
  const canPostReceipt = hasPurchaseOrder && hasRequiredHeader && hasReceivedItems && !hasQualityBlocker
  const nextReceiptAction = !hasPurchaseOrder
    ? 'Bestellung auswaehlen.'
    : !hasDeliveryNote
      ? 'Lieferscheinnummer erfassen.'
      : !hasRequiredHeader
        ? 'Empfaenger und Lagerort eintragen.'
        : !hasReceivedItems
          ? 'Gelieferte Mengen erfassen.'
          : hasQualityBlocker
            ? 'QS-Abweichung klaeren, bevor gebucht wird.'
            : 'Wareneingang buchen und Nachweis sichern.'
  const receiptTaskItems: UxTaskItem[] = [
    {
      label: 'Bestellung auswaehlen',
      done: hasPurchaseOrder,
      hint: hasPurchaseOrder ? `Bestellung ${purchaseOrder?.number} von ${purchaseOrder?.supplierName || 'Lieferant'} geladen.` : 'Freigegebene Bestellung auswaehlen.',
    },
    {
      label: 'Lieferschein erfassen',
      done: hasDeliveryNote,
      hint: hasDeliveryNote ? `Lieferschein ${receiptData.deliveryNoteNumber} erfasst.` : 'Lieferscheinnummer als Nachweis eintragen.',
    },
    {
      label: 'Mengen und QS pruefen',
      done: hasReceivedItems && !hasQualityBlocker,
      hint: hasQualityBlocker ? `${totalRejected} abgelehnte Menge oder QS-Fehler klaeren.` : `${totalAccepted} akzeptiert, ${totalRejected} abgelehnt.`,
    },
    {
      label: 'Wareneingang buchen',
      done: canPostReceipt,
      hint: canPostReceipt ? 'Alle Pflichtangaben liegen vor; Buchung ist moeglich.' : 'Vor Buchung offene Pflicht- oder QS-Punkte schliessen.',
    },
  ]
  const receiptCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen/Buchen',
      available: canPostReceipt,
      hint: canPostReceipt ? 'Wareneingang kann gebucht werden.' : 'Buchung erst nach Bestellung, Kopfpflichtfeldern und Mengenpruefung.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Bestellung, Lieferant, Positionen, Restmengen, QS-Status und Lagerort sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Bearbeiten',
      available: true,
      hint: 'Lieferschein, Empfaenger, Lagerort, Mengen, Ablehnungen und Zustand koennen vor Buchung gepflegt werden.',
    },
    {
      key: 'delete',
      label: 'Abbrechen',
      available: true,
      hint: 'Nicht gebuchte Eingaben koennen verworfen werden; gebuchte Korrekturen laufen fachlich ueber Folgebeleg.',
    },
    {
      key: 'approve',
      label: 'QS-Freigabe',
      available: !hasQualityBlocker,
      hint: hasQualityBlocker ? 'QS-Abweichung oder abgelehnte Menge blockiert die Freigabe.' : 'Keine QS-Blockade in der aktuellen Eingabe.',
    },
    {
      key: 'export',
      label: 'Nachweis',
      available: hasDeliveryNote || canPostReceipt,
      hint: 'Lieferschein, Buchung und Positionswerte bilden den Wareneingangsnachweis.',
    },
    {
      key: 'audit',
      label: 'Audit',
      available: true,
      hint: 'Bestellbezug, Empfaenger, Lagerort, QS-Status und Mengen bleiben nachvollziehbar.',
    },
  ]

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
      <RoleFocusBar
        roles={goodsReceiptRoleProfiles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={roleFocus === 'all' ? 5 : 1}
        totalCount={5}
      />
      <ManagementDecisionPanel
        decision={{
          allowed: canPostReceipt,
          allowedLabel: 'Buchbar',
          blockedLabel: 'Noch nicht buchbar',
          summary: canPostReceipt
            ? `Wareneingang ist bereit zur Buchung. ${totalAccepted} akzeptierte Menge wird mit Bestellung ${purchaseOrder?.number} verknuepft.`
            : `Wareneingang ist noch nicht vollstaendig. ${nextReceiptAction}`,
          blockerCount: canPostReceipt ? 0 : 1,
          nextFocus: nextReceiptAction,
          template: {
            label: 'Bestellung oeffnen',
            href: '/einkauf/bestellungen',
          },
        }}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTaskPlan title="Eingangspruefplan" items={receiptTaskItems} />
        <NextActionPanel
          action={nextReceiptAction}
          tone={canPostReceipt ? 'emerald' : hasQualityBlocker ? 'red' : hasPurchaseOrder ? 'amber' : 'blue'}
        />
      </div>
      <CrudCapabilityChecklist capabilities={receiptCrudCapabilities} />

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.detail.basicInfo')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="purchaseOrder">{t('crud.entities.purchaseOrder')} *</Label>
              <NativeSelect
                id="purchaseOrder"
                value={selectedPoId}
                onValueChange={setSelectedPoId}
                options={purchaseOrderOptions}
                placeholder={t('crud.fields.selectPurchaseOrder')}
              />
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
              <NativeSelect
                id="qualityInspectionStatus"
                value={receiptData.qualityInspectionStatus}
                onValueChange={(value) =>
                  setReceiptData((prev) => ({ ...prev, qualityInspectionStatus: value as GoodsReceiptData['qualityInspectionStatus'] }))
                }
                options={qualityInspectionOptions}
              />
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
                        <NativeSelect
                          value={receiptItem.condition}
                          onValueChange={(value) => updateReceiptItem(index, 'condition', value as GoodsReceiptItem['condition'])}
                          options={conditionOptions}
                          className="w-32"
                        />
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


