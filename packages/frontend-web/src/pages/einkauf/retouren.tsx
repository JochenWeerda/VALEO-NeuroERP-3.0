import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { NativeSelect } from '@/components/ui/native-select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { Skeleton } from '@/components/ui/skeleton'
import { PackageX, ArrowLeft, AlertTriangle } from 'lucide-react'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { ErrorState } from '@/components/ErrorState'
import { useEinkaufRetouren, useUpdateEinkaufRetoure } from '@/lib/api/einkauf'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

type ReturnRoleFocus = 'all' | 'procurement' | 'goods-receipt' | 'finance' | 'quality' | 'management'

const returnRoleProfiles: Array<{ id: ReturnRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle Rollen', description: 'Zeigt Retouren fuer Einkauf, Wareneingang, Finance, QS und Leitung.' },
  { id: 'procurement', label: 'Einkauf', description: 'Fokus auf Lieferant, Wareneingang, Grund und Lieferantenklaerung.' },
  { id: 'goods-receipt', label: 'Wareneingang', description: 'Fokus auf Positionen, Mengen und Ruecksendung.' },
  { id: 'finance', label: 'Finance', description: 'Fokus auf Gutschriftanforderung und Wert der Retoure.' },
  { id: 'quality', label: 'QS', description: 'Fokus auf Defekt, Schaden, Qualitaetsproblem und Notizen.' },
  { id: 'management', label: 'Leitung', description: 'Fokus auf Stopper, Status und naechste Aktion.' },
]

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
  const [selectedGrId, setSelectedGrId] = useState<string>(grId || '')
  const [returnDialogOpen, setReturnDialogOpen] = useState(false)
  const [roleFocus, setRoleFocus] = useState<ReturnRoleFocus>('all')
  const [returnData, setReturnData] = useState<ReturnData>({
    goodsReceiptId: '',
    returnDate: new Date().toISOString().split('T')[0],
    returnReason: '',
    returnNotes: '',
    items: [],
    creditMemoRequested: false,
  })

  const { data: goodsReceipts = [], isLoading: grLoading, isError: grError, error: grErrorObj, refetch: refetchReceipts } = useQuery({
    queryKey: ['einkauf', 'goods-receipts'],
    queryFn: async () => (await apiClient.get<GoodsReceipt[]>('/api/v1/einkauf/goods-receipts')).data,
    staleTime: 2 * 60 * 1000,
  })

  const {
    data: retouren = [],
    isLoading: retourenLoading,
    isError: retourenError,
    error: retourenErrorObj,
    refetch: refetchRetouren,
  } = useEinkaufRetouren()
  const updateRetoure = useUpdateEinkaufRetoure()


  // Lade Wareneingang wenn ausgewählt
  useEffect(() => {
    if (selectedGrId) {
      const receipt = goodsReceipts.find(gr => gr.id === selectedGrId)
      if (receipt) {
        setGoodsReceipt(receipt)
        setReturnData(prev => ({
          ...prev,
          goodsReceiptId: selectedGrId,
          items: receipt.items.map(item => ({
            goodsReceiptItemId: item.id, productId: item.productId, productName: item.productName,
            quantityReturned: 0, unit: item.unit, price: item.price, reason: '', creditMemoRequested: false,
          })),
        }))
      }
    }
  }, [selectedGrId, goodsReceipts])

  if (grError) {
    return <ErrorState error={grErrorObj as Error} onRetry={() => { void refetchReceipts() }} />
  }

  if (retourenError) {
    return <ErrorState error={retourenErrorObj as Error} onRetry={() => { void refetchRetouren() }} />
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

  const hasGoodsReceipt = Boolean(goodsReceipt)
  const returnableItems = goodsReceipt?.items.filter(item => item.quantityReturned < item.quantityReceived) ?? []
  const selectedReturnItems = returnData.items.filter(item => item.quantityReturned > 0)
  const openReturns = retouren.filter((retoure) => retoure.status !== 'abgeschlossen' && retoure.status !== 'storniert').length
  const hasReturnReason = Boolean(returnData.returnReason)
  const hasReturnItems = selectedReturnItems.length > 0
  const canCreateReturn = hasGoodsReceipt && hasReturnReason && hasReturnItems
  const nextReturnAction = !hasGoodsReceipt
    ? 'Wareneingang auswaehlen.'
    : returnableItems.length === 0
      ? 'Wareneingang ist vollstaendig retourniert; anderen Wareneingang waehlen.'
      : !hasReturnReason
        ? 'Retourengrund im Dialog auswaehlen.'
        : !hasReturnItems
          ? 'Ruecksendemenge fuer mindestens eine Position erfassen.'
          : returnData.creditMemoRequested
            ? 'Retoure speichern und Gutschrift beim Lieferanten nachhalten.'
            : 'Retoure speichern und Status nachhalten.'
  const returnTaskItems: UxTaskItem[] = [
    {
      label: 'Wareneingang klaeren',
      done: hasGoodsReceipt,
      hint: hasGoodsReceipt ? `${goodsReceipt?.number} von ${goodsReceipt?.supplierName}.` : 'Wareneingang ist Pflicht fuer eine belastbare Retoure.',
    },
    {
      label: 'Ruecksendemengen pruefen',
      done: hasReturnItems,
      hint: hasReturnItems ? `${selectedReturnItems.length} Positionen fuer Ruecksendung markiert.` : `${returnableItems.length} Positionen waeren aktuell retournierbar.`,
    },
    {
      label: 'Grund und QS-Nachweis sichern',
      done: hasReturnReason,
      hint: hasReturnReason ? `Grund: ${returnData.returnReason}.` : 'Grund auswaehlen und bei Bedarf Positionsgrund ergaenzen.',
    },
    {
      label: 'Gutschrift und Status nachhalten',
      done: openReturns === 0 && retouren.length > 0,
      hint: openReturns > 0 ? `${openReturns} Retouren sind noch offen oder in Pruefung.` : 'Keine offene Retoure im aktuellen Bestand.',
    },
  ]
  const returnCrudCapabilities = [
    { key: 'create', label: 'Retoure anlegen', available: canCreateReturn, hint: canCreateReturn ? 'Retoure kann gespeichert werden.' : 'Wareneingang, Grund und Ruecksendemenge fehlen noch.' },
    { key: 'read', label: 'Lesen', available: true, hint: 'Wareneingaenge, Positionen, Retourenliste und Status sind sichtbar.' },
    { key: 'update', label: 'Status pflegen', available: retouren.length > 0, hint: retouren.length > 0 ? 'Retourenstatus kann in der Liste aktualisiert werden.' : 'Keine Retoure fuer Statuspflege vorhanden.' },
    { key: 'approve', label: 'Gutschrift anfordern', available: returnData.creditMemoRequested || retouren.length > 0, hint: returnData.creditMemoRequested ? 'Gutschrift ist fuer diese Retoure angefordert.' : 'Gutschrift kann im Retourendialog markiert werden.' },
    { key: 'evidence', label: 'Nachweis', available: hasGoodsReceipt || retouren.length > 0, hint: 'Wareneingang, Position, Grund, Status und Gutschriftanforderung bilden den Nachweis.' },
    { key: 'audit', label: 'Pruefspur', available: true, hint: 'Anlage, Statuswechsel und Wareneingangsbezug laufen ueber bestehende API-Aktionen.' },
  ]

  const handleSaveReturn = async () => {
    if (!returnData.returnReason) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.tooltips.placeholders.selectReturnReason'),
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
      await apiClient.post('/api/v1/einkauf/retouren', {
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
      
      await refetchReceipts()
      await refetchRetouren()
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
    <div className="space-y-6 p-3 md:p-6">
      {grLoading && (
        <div className="space-y-4"><Skeleton className="h-8 w-64" /><Skeleton className="h-[200px] w-full" /></div>
      )}
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

      <div className="space-y-4">
        <RoleFocusBar roles={returnRoleProfiles} value={roleFocus} onChange={setRoleFocus} visibleCount={roleFocus === 'all' ? 5 : 1} totalCount={5} />
        <ManagementDecisionPanel
          decision={{
            allowed: canCreateReturn || openReturns === 0,
            allowedLabel: 'Freigabefaehig',
            blockedLabel: 'Klaerungsbedarf',
            summary: canCreateReturn ? `Retoure ist vorbereitet: ${selectedReturnItems.length} Positionen, Gutschrift ${returnData.creditMemoRequested ? 'ja' : 'nein'}.` : `Vor der Retoure ist noch etwas offen: ${nextReturnAction}`,
            blockerCount: [!hasGoodsReceipt, returnableItems.length === 0, !hasReturnReason, !hasReturnItems].filter(Boolean).length,
            nextFocus: nextReturnAction,
            template: { label: 'Wareneingang oeffnen', href: '/einkauf/wareneingang' },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan title="Retouren-Freigabeplan" items={returnTaskItems} />
          <div className="space-y-3">
            <NextActionPanel action={nextReturnAction} tone={canCreateReturn ? 'emerald' : hasGoodsReceipt ? 'amber' : 'blue'} />
            <EvidenceTemplateLink link={{ label: 'Gutschriften/Belastungen pruefen', href: '/einkauf/gutschriften-belastungen' }} />
          </div>
        </div>
        <CrudCapabilityChecklist capabilities={returnCrudCapabilities} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.fields.selectGoodsReceipt')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Label htmlFor="goodsReceipt">{t('crud.fields.goodsReceipt')}</Label>
              <NativeSelect
                value={selectedGrId}
                onValueChange={setSelectedGrId}
                options={goodsReceipts.map((gr) => ({
                  value: gr.id,
                  label: `${gr.number} - ${gr.supplierName} (${formatDate(gr.receivedDate)})`,
                }))}
                placeholder={t('crud.tooltips.placeholders.selectGoodsReceipt')}
              />
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

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.entities.goodsReturn')}</CardTitle>
        </CardHeader>
        <CardContent>
          {retourenLoading ? (
            <div className="text-sm text-muted-foreground">{t('common.loading')}</div>
          ) : retouren.length === 0 ? (
            <div className="text-sm text-muted-foreground">{t('crud.messages.noData')}</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('crud.fields.number')}</TableHead>
                  <TableHead>{t('crud.entities.supplier')}</TableHead>
                  <TableHead>{t('crud.fields.reason')}</TableHead>
                  <TableHead>{t('crud.fields.date')}</TableHead>
                  <TableHead>{t('crud.fields.status')}</TableHead>
                  <TableHead className="text-right">{t('crud.actions.update')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {retouren.map((retoure) => (
                  <TableRow key={retoure.id}>
                    <TableCell><code className="text-sm">{retoure.nummer}</code></TableCell>
                    <TableCell>{retoure.lieferant || '-'}</TableCell>
                    <TableCell>{retoure.grund || '-'}</TableCell>
                    <TableCell>{retoure.datum ? formatDate(retoure.datum) : '-'}</TableCell>
                    <TableCell>
                      <Badge variant={retoure.status === 'abgeschlossen' ? 'default' : 'secondary'}>{retoure.status}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <NativeSelect
                        value={retoure.status}
                        onValueChange={(status) => {
                          void updateRetoure.mutateAsync({ id: retoure.id, status })
                        }}
                        options={[
                          { value: 'offen', label: 'offen' },
                          { value: 'in_pruefung', label: 'in_pruefung' },
                          { value: 'abgeschlossen', label: 'abgeschlossen' },
                          { value: 'storniert', label: 'storniert' },
                        ]}
                        className="ml-auto w-[170px]"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

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
                <NativeSelect
                  value={returnData.creditMemoRequested ? 'yes' : 'no'}
                  onValueChange={(value) => setReturnData(prev => ({ ...prev, creditMemoRequested: value === 'yes' }))}
                  options={[
                    { value: 'yes', label: t('common.yes') },
                    { value: 'no', label: t('common.no') },
                  ]}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="returnReason">{t('crud.fields.returnReason')} *</Label>
              <NativeSelect
                value={returnData.returnReason}
                onValueChange={(value) => setReturnData(prev => ({ ...prev, returnReason: value }))}
                options={[
                  { value: 'DEFECTIVE', label: t('crud.fields.returnReasonDefective') },
                  { value: 'WRONG_ITEM', label: t('crud.fields.returnReasonWrongItem') },
                  { value: 'DAMAGED', label: t('crud.fields.returnReasonDamaged') },
                  { value: 'OVER_DELIVERY', label: t('crud.fields.returnReasonOverDelivery') },
                  { value: 'QUALITY_ISSUE', label: t('crud.fields.returnReasonQualityIssue') },
                  { value: 'OTHER', label: t('crud.fields.returnReasonOther') },
                ]}
                placeholder={t('crud.tooltips.placeholders.selectReturnReason')}
              />
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
                          <NativeSelect
                            value={item.creditMemoRequested ? 'yes' : 'no'}
                            onValueChange={(value) => {
                              const updatedItems = [...returnData.items]
                              updatedItems[index].creditMemoRequested = value === 'yes'
                              setReturnData(prev => ({ ...prev, items: updatedItems }))
                            }}
                            options={[
                              { value: 'yes', label: t('common.yes') },
                              { value: 'no', label: t('common.no') },
                            ]}
                            className="w-20"
                          />
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

