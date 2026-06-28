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
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { summarizeProcurementMatch } from '@/lib/domain-depth'
import { CheckCircle, XCircle, AlertTriangle, FileCheck, Receipt } from 'lucide-react'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

type MatchItem = {
  purchaseOrderItemId: string
  receiptItemId?: string
  invoiceItemId: string
  productName: string
  poQuantity: number
  poPrice: number
  poTotal: number
  grQuantity?: number
  grAccepted?: number
  grRejected?: number
  ivQuantity: number
  ivPrice: number
  ivTotal: number
  quantityMatch: boolean
  priceMatch: boolean
  qualityMatch: boolean
  exceptions: string[]
  varianceAmount: number
}

type MatchResult = {
  matchId?: string
  purchaseOrderId: string
  receiptId?: string
  invoiceId: string
  matchType: 'two_way' | 'three_way'
  overallStatus: 'matched' | 'partial_match' | 'exceptions' | 'no_match'
  quantityMatch: 'matched' | 'over_invoice' | 'under_invoice' | 'no_receipt'
  priceMatch: 'matched' | 'price_variance' | 'no_match'
  qualityMatch: 'matched' | 'quality_issues' | 'no_receipt'
  itemMatches: MatchItem[]
  totalVariance: number
  variancePercentage: number
  exceptionsCount: number
  autoApprovalEligible: boolean
}

type ToleranceConfig = {
  quantity: number // Prozent
  price: number // Prozent
  date: number // Tage
}

export default function RechnungAbgleichPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { invoiceId } = useParams<{ invoiceId?: string }>()
  const entityType = 'invoiceReceipt'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Rechnungseingang')

  const [loading, setLoading] = useState(false)
  const [matching, setMatching] = useState(false)
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<string>(invoiceId || '')
  const [invoices, setInvoices] = useState<Record<string, unknown>[]>([])
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null)
  const [toleranceConfig, setToleranceConfig] = useState<ToleranceConfig>({
    quantity: 5,
    price: 2,
    date: 7,
  })
  const [exceptionDialogOpen, setExceptionDialogOpen] = useState(false)
  const [selectedException, setSelectedException] = useState<MatchItem | null>(null)
  const [exceptionReason, setExceptionReason] = useState('')
  const [blocked, setBlocked] = useState(false)

  useEffect(() => {
    loadInvoices()
  }, [])

  useEffect(() => {
    if (selectedInvoiceId) {
      performMatch()
    }
  }, [selectedInvoiceId, toleranceConfig])

  const loadInvoices = async () => {
    try {
      const response = (await apiClient.get<Record<string, unknown>[]>('/api/v1/einkauf/rechnungseingaenge')) as unknown as Record<string, unknown>[]
      const rows = Array.isArray(response) ? response : []
      const normalized = rows.map(inv => ({
        id: inv.id,
        rechnungsNummer: inv.rechnungsNummer || inv.rechnungs_nummer || inv.rechnungsnr || '',
        lieferantName: inv.lieferantName || inv.lieferant_name || inv.lieferant || '',
        status: String(inv.status || '').toUpperCase(),
      }))
      setInvoices(normalized.filter(x => ['ERFASST', 'GEPRUEFT'].includes(x.status)))
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadDataError'),
      })
    }
  }

  const performMatch = async () => {
    if (!selectedInvoiceId) return

    setMatching(true)
    try {
      // Lade Rechnung
      const invoice = await apiClient.get<Record<string, unknown>>(`/api/v1/einkauf/rechnungseingaenge/${selectedInvoiceId}`)
      const invoiceBestellungId = invoice.bestellungId || invoice.bestellung_id || invoice.bestellung
      const invoiceWareneingangId = invoice.wareneingangId || invoice.wareneingang_id || invoice.wareneingang

      if (!invoiceBestellungId) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.validationError'),
          description: 'Rechnung ist nicht mit einer Bestellung verknüpft',
        })
        setMatching(false)
        return
      }

      const purchaseOrder = await apiClient.get<Record<string, unknown>>(`/api/v1/purchase-orders/${String(invoiceBestellungId ?? '')}`)

      // Lade Wareneingang (falls vorhanden)
      let goodsReceipt = null
      if (invoiceWareneingangId) {
        try {
          goodsReceipt = await apiClient.get<Record<string, unknown>>(`/api/purchase-workflow/orders/${String(invoiceBestellungId ?? '')}/goods-receipt/${String(invoiceWareneingangId ?? '')}`)
        } catch {
          // Wareneingang optional — Abgleich läuft auch ohne WE-Daten
        }
      }

      // Führe Abgleich durch (Frontend-Logik)
      const match = performFrontendMatch(purchaseOrder, goodsReceipt, invoice, toleranceConfig)
      setMatchResult(match)

      // Prüfe Blockierung
      const hasBlockingExceptions = match.itemMatches.some(
        item => item.exceptions.length > 0 && Math.abs(item.varianceAmount) > (purchaseOrder.totalAmount * toleranceConfig.price / 100)
      )
      setBlocked(hasBlockingExceptions && match.overallStatus !== 'matched')
    } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadDataError'),
        description: error.message,
      })
    } finally {
      setMatching(false)
    }
  }

  const performFrontendMatch = (
    po: Record<string, unknown>,
    gr: Record<string, unknown> | null,
    invoice: Record<string, unknown>,
    config: ToleranceConfig
  ): MatchResult => {
    const itemMatches: MatchItem[] = []
    let totalVariance = 0
    let exceptionsCount = 0

    const poItems = po.lines || po.items || []
    const grItems = gr?.items || []
    const ivItems = invoice.positionen || invoice.items || []

    for (const poItem of poItems) {
      const grItem = grItems.find(gi => gi.purchaseOrderItemId === poItem.id)
      const ivItem = ivItems.find(ii => {
        const iiArticleId = ii.artikelId || ii.artikel_id || ii.articleId || ii.productId
        const poArticleId = poItem.productId || poItem.articleId || poItem.artikelId
        return iiArticleId && poArticleId ? String(iiArticleId) === String(poArticleId) : false
      })

      if (!ivItem) {
        itemMatches.push({
          purchaseOrderItemId: poItem.id,
          invoiceItemId: '',
          productName: poItem.productName || poItem.product?.name || '',
          poQuantity: poItem.qty || poItem.quantity || 0,
          poPrice: poItem.price || 0,
          poTotal: (poItem.qty || poItem.quantity || 0) * (poItem.price || 0),
          grQuantity: grItem?.receivedQuantity || 0,
          grAccepted: grItem?.acceptedQuantity || 0,
          grRejected: grItem?.rejectedQuantity || 0,
          ivQuantity: 0,
          ivPrice: 0,
          ivTotal: 0,
          quantityMatch: false,
          priceMatch: false,
          qualityMatch: !!grItem,
          exceptions: ['Rechnungsposition nicht gefunden'],
          varianceAmount: (poItem.qty || poItem.quantity || 0) * (poItem.price || 0),
        })
        exceptionsCount++
        totalVariance += Math.abs((poItem.qty || poItem.quantity || 0) * (poItem.price || 0))
        continue
      }

      const poQty = poItem.qty || poItem.quantity || 0
      const poPrice = poItem.price || 0
      const poTotal = poQty * poPrice
      const ivQty = Number(ivItem.menge || ivItem.quantity || 0)
      const ivPrice = Number(ivItem.preis || ivItem.unitPrice || ivItem.einzelpreis || 0)
      const ivTotal = ivQty * ivPrice
      const grQty = grItem?.receivedQuantity || 0
      const grAccepted = grItem?.acceptedQuantity || 0
      const grRejected = grItem?.rejectedQuantity || 0

      // Mengen-Abgleich
      const qtyDiff = Math.abs(ivQty - (grAccepted || poQty))
      const qtyTolerance = (grAccepted || poQty) * (config.quantity / 100)
      const quantityMatch = qtyDiff <= qtyTolerance

      // Preis-Abgleich
      const priceDiff = Math.abs(ivPrice - poPrice)
      const priceTolerance = poPrice * (config.price / 100)
      const priceMatch = priceDiff <= priceTolerance

      // Qualität (nur wenn GR vorhanden)
      const qualityMatch = !grItem || (grItem.rejectedQuantity || 0) === 0

      const exceptions: string[] = []
      if (!quantityMatch) {
        exceptions.push(`Mengenabweichung: ${qtyDiff.toFixed(2)} (Toleranz: ${qtyTolerance.toFixed(2)})`)
      }
      if (!priceMatch) {
        exceptions.push(`Preisabweichung: ${priceDiff.toFixed(2)}€ (Toleranz: ${priceTolerance.toFixed(2)}€)`)
      }
      if (!qualityMatch) {
        exceptions.push(`Qualitätsprobleme: ${grRejected} abgelehnt`)
      }

      const varianceAmount = ivTotal - poTotal
      totalVariance += Math.abs(varianceAmount)
      if (exceptions.length > 0) exceptionsCount++

      itemMatches.push({
        purchaseOrderItemId: poItem.id,
        receiptItemId: grItem?.id,
        invoiceItemId: ivItem.id || '',
        productName: poItem.productName || poItem.product?.name || '',
        poQuantity: poQty,
        poPrice: poPrice,
        poTotal: poTotal,
        grQuantity: grQty,
        grAccepted: grAccepted,
        grRejected: grRejected,
        ivQuantity: ivQty,
        ivPrice: ivPrice,
        ivTotal: ivTotal,
        quantityMatch,
        priceMatch,
        qualityMatch,
        exceptions,
        varianceAmount,
      })
    }

    const poTotal = poItems.reduce((sum, item) => {
      const qty = item.qty || item.quantity || 0
      const price = item.price || 0
      return sum + (qty * price)
    }, 0)

    const variancePercentage = poTotal > 0 ? (totalVariance / poTotal) * 100 : 0

    const quantityMatch: MatchResult['quantityMatch'] = 
      itemMatches.every(m => m.quantityMatch) ? 'matched' :
      itemMatches.some(m => m.ivQuantity > (m.grAccepted || m.poQuantity)) ? 'over_invoice' :
      itemMatches.some(m => m.ivQuantity < (m.grAccepted || m.poQuantity)) ? 'under_invoice' :
      'no_receipt'

    const priceMatch: MatchResult['priceMatch'] = 
      itemMatches.every(m => m.priceMatch) ? 'matched' : 'price_variance'

    const qualityMatch: MatchResult['qualityMatch'] = 
      itemMatches.every(m => m.qualityMatch) ? 'matched' :
      itemMatches.some(m => !m.qualityMatch) ? 'quality_issues' : 'no_receipt'

    const overallStatus: MatchResult['overallStatus'] = 
      exceptionsCount === 0 ? 'matched' :
      exceptionsCount < itemMatches.length ? 'partial_match' :
      itemMatches.length === 0 ? 'no_match' : 'exceptions'

    const autoApprovalEligible = 
      overallStatus === 'matched' || 
      (overallStatus === 'partial_match' && variancePercentage <= 5)

    return {
      purchaseOrderId: po.id || po.number,
      receiptId: gr?.id,
      invoiceId: invoice.id || invoice.rechnungsNummer,
      matchType: gr ? 'three_way' : 'two_way',
      overallStatus,
      quantityMatch,
      priceMatch,
      qualityMatch,
      itemMatches,
      totalVariance,
      variancePercentage,
      exceptionsCount,
      autoApprovalEligible,
    }
  }

  const handleApprove = async () => {
    if (!matchResult || !selectedInvoiceId) return

    if (blocked && !exceptionReason) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: 'Begründung für Abweichungen ist erforderlich',
      })
      return
    }

    setLoading(true)
    try {
      // Update Rechnung Status
      await apiClient.put<Record<string, unknown>>(`/api/v1/einkauf/rechnungseingaenge/${selectedInvoiceId}`, {
        status: 'FREIGEGEBEN',
        abgleichErgebnis: matchResult,
        abweichungsBegruendung: exceptionReason || undefined,
      })

      toast({
        title: t('crud.messages.approveSuccess', { entityType: entityTypeLabel }),
        description: 'Rechnung wurde freigegeben',
      })

      navigate('/einkauf/rechnungseingaenge-liste')
    } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      toast({
        variant: 'destructive',
        title: t('crud.messages.approveError', { entityType: entityTypeLabel }),
        description: error.response?.data?.detail || error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleException = (item: MatchItem) => {
    setSelectedException(item)
    setExceptionDialogOpen(true)
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'matched':
        return <Badge variant="outline" className="bg-green-50 text-green-700"><CheckCircle className="h-3 w-3 mr-1" />{t('status.approved')}</Badge>
      case 'partial_match':
        return <Badge variant="outline" className="bg-yellow-50 text-yellow-700"><AlertTriangle className="h-3 w-3 mr-1" />{t('status.partial')}</Badge>
      case 'exceptions':
        return <Badge variant="destructive"><XCircle className="h-3 w-3 mr-1" />{t('status.rejected')}</Badge>
      default:
        return <Badge variant="outline">{t('status.unknown')}</Badge>
    }
  }

  const matchOps = matchResult
    ? summarizeProcurementMatch({
        exceptionsCount: matchResult.exceptionsCount,
        variancePercentage: matchResult.variancePercentage,
        autoApprovalEligible: matchResult.autoApprovalEligible,
        hasGoodsReceipt: matchResult.matchType === 'three_way',
      })
    : null

  const operationalStatus = matchResult
    ? normalizeOperationalStatus(
        blocked || matchOps?.exceptionPressure === 'hoch'
          ? 'eskaliert'
          : matchResult.overallStatus === 'matched'
            ? 'abgeschlossen'
            : matchResult.overallStatus === 'partial_match'
              ? 'wartet_auf_mensch'
              : 'in_pruefung',
      )
    : normalizeOperationalStatus(selectedInvoiceId ? 'in_pruefung' : 'offen')

  const contextSections = matchResult
    ? [
        {
          title: 'Abgleich',
          items: [
            { label: 'Match-Typ', value: matchResult.matchType === 'three_way' ? '3-Wege' : '2-Wege' },
            { label: 'Ausnahmen', value: String(matchResult.exceptionsCount) },
            { label: 'Varianz', value: `${matchResult.variancePercentage.toFixed(2)}%` },
          ],
        },
        {
          title: 'Folgefall',
          items: [
            { label: 'Freigabefaehig', value: matchResult.autoApprovalEligible ? 'ja' : 'nein' },
            { label: 'Lieferbezug', value: matchResult.matchType === 'three_way' ? 'Wareneingang vorhanden' : 'Wareneingang offen' },
            { label: 'Naechster Schritt', value: matchOps?.nextAction ?? 'Abgleich pruefen' },
          ],
        },
        {
          title: 'Governance',
          items: [
            { label: 'Blockiert', value: blocked ? 'ja' : 'nein' },
            { label: 'Begruendung', value: exceptionReason ? 'erfasst' : 'offen' },
            { label: 'Status', value: matchResult.overallStatus },
          ],
        },
      ]
    : []

  const timelineItems = matchResult
    ? [
        {
          label: 'Abgleich gerechnet',
          detail: `${matchResult.itemMatches.length} Positionen mit ${matchResult.exceptionsCount} Ausnahmefaellen.`,
        },
        {
          label: matchResult.matchType === 'three_way' ? 'Wareneingang einbezogen' : 'Ohne Wareneingang',
          detail: matchResult.matchType === 'three_way' ? 'Mengen- und Qualitaetsbezug wurde gegen den Wareneingang geprueft.' : 'Es liegt nur ein 2-Wege-Abgleich gegen Bestellung und Rechnung vor.',
        },
        {
          label: blocked ? 'Freigabe blockiert' : 'Freigabepfad offen',
          detail: blocked ? 'Die aktuelle Varianz verlangt Begruendung oder Nachforderung vor der Freigabe.' : 'Die Rechnung kann kontrolliert in den Freigabefall uebergehen.',
        },
      ]
    : []

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t('crud.fields.reconciliation')}</h1>
          <p className="text-muted-foreground">2/3-Wege-Abgleich: Bestellung - Wareneingang - Rechnung</p>
        </div>
        <Button variant="outline" onClick={() => navigate('/einkauf/rechnungseingaenge-liste')}>
          {t('common.cancel')}
        </Button>
      </div>

      <OperationalCaseHeader
        title="Beschaffungsfall abstimmen"
        description="Der Abgleich fuehrt Bestellung, Wareneingang und Rechnung als einen Freigabe- und Ausnahmefall zusammen."
        status={operationalStatus}
        owner="Einkauf / Kreditoren"
        blocker={blocked ? 'Varianz oder fehlender Nachweis blockiert die direkte Freigabe.' : null}
        nextAction={matchOps?.nextAction ?? 'Rechnung auswaehlen und Abgleich starten'}
        caseLabel={selectedInvoiceId ? `Rechnung ${selectedInvoiceId}` : 'Kein Rechnungsfall gewaehlt'}
        tags={['Beschaffung', 'Abgleich', 'Freigabe']}
      />

      {matchResult ? (
        <div className="grid gap-4 lg:grid-cols-[1.25fr_1fr]">
          <OperationalTimeline title="Abgleichsverlauf" items={timelineItems} />
          <OperationalContextPanel title="Ausnahme- und Freigabekontext" sections={contextSections} />
        </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.detail.basicInfo')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="invoice">{t('crud.entities.invoiceReceipt')} *</Label>
              <NativeSelect
                value={selectedInvoiceId}
                onValueChange={setSelectedInvoiceId}
                options={invoices.map((inv) => ({
                  value: inv.id,
                  label: `${String(inv.rechnungsNummer ?? '')} - ${String(inv.lieferantName ?? '')}`,
                }))}
                placeholder={t('crud.fields.selectInvoice')}
              />
            </div>

            <div className="flex items-end gap-2">
              <Button onClick={performMatch} disabled={!selectedInvoiceId || matching}>
                <FileCheck className="h-4 w-4 mr-2" />
                {matching ? t('common.loading') : t('crud.actions.review')}
              </Button>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <Label>{t('crud.fields.toleranceQuantity')} (%)</Label>
              <Input
                type="number"
                min="0"
                max="100"
                step="0.1"
                value={toleranceConfig.quantity}
                onChange={(e) => setToleranceConfig(prev => ({ ...prev, quantity: Number(e.target.value) }))}
              />
            </div>
            <div>
              <Label>{t('crud.fields.tolerancePrice')} (%)</Label>
              <Input
                type="number"
                min="0"
                max="100"
                step="0.1"
                value={toleranceConfig.price}
                onChange={(e) => setToleranceConfig(prev => ({ ...prev, price: Number(e.target.value) }))}
              />
            </div>
            <div>
              <Label>{t('crud.fields.toleranceDate')} ({t('crud.fields.days')})</Label>
              <Input
                type="number"
                min="0"
                value={toleranceConfig.date}
                onChange={(e) => setToleranceConfig(prev => ({ ...prev, date: Number(e.target.value) }))}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {matchResult && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {t('crud.fields.reconciliationResult')}
                {getStatusBadge(matchResult.overallStatus)}
              </CardTitle>
            </CardHeader>
          <CardContent>
              <div className="mb-4 grid gap-4 md:grid-cols-3">
                <div className="rounded-lg border p-3">
                  <div className="text-sm text-muted-foreground">Ausnahmedruck</div>
                  <div className="mt-2 text-lg font-semibold">{matchOps?.exceptionPressure ?? 'niedrig'}</div>
                </div>
                <div className="rounded-lg border p-3">
                  <div className="text-sm text-muted-foreground">Freigabepfad</div>
                  <div className="mt-2 text-lg font-semibold">{matchResult.autoApprovalEligible ? 'kontrolliert offen' : 'manuelle Klaerung'}</div>
                </div>
                <div className="rounded-lg border p-3">
                  <div className="text-sm text-muted-foreground">Naechste Aktion</div>
                  <div className="mt-2 text-sm font-semibold">{matchOps?.nextAction}</div>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-4 mb-4">
                <div>
                  <div className="text-sm text-muted-foreground">{t('crud.fields.matchType')}</div>
                  <div className="font-semibold">
                    {matchResult.matchType === 'three_way' ? '3-Wege' : '2-Wege'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">{t('crud.fields.totalVariance')}</div>
                  <div className="font-semibold">
                    {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(matchResult.totalVariance)}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">{t('crud.fields.variancePercentage')}</div>
                  <div className="font-semibold">{matchResult.variancePercentage.toFixed(2)}%</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">{t('crud.fields.exceptionsCount')}</div>
                  <div className="font-semibold">{matchResult.exceptionsCount}</div>
                </div>
              </div>

              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('crud.fields.product')}</TableHead>
                    <TableHead className="text-right">{t('crud.entities.purchaseOrder')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.goodsReceipt')}</TableHead>
                    <TableHead className="text-right">{t('crud.entities.invoiceReceipt')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.variance')}</TableHead>
                    <TableHead>{t('crud.fields.status')}</TableHead>
                    <TableHead>{t('crud.fields.actions')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {matchResult.itemMatches.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{item.productName}</TableCell>
                      <TableCell className="text-right">
                        <div>{item.poQuantity} × {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(item.poPrice)}</div>
                        <div className="text-sm text-muted-foreground">
                          = {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(item.poTotal)}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        {item.grAccepted !== undefined ? (
                          <>
                            <div>{item.grAccepted} {item.grRejected ? `(-${item.grRejected})` : ''}</div>
                            {item.grQuantity !== item.grAccepted && (
                              <div className="text-sm text-muted-foreground">von {item.grQuantity}</div>
                            )}
                          </>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <div>{item.ivQuantity} × {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(item.ivPrice)}</div>
                        <div className="text-sm text-muted-foreground">
                          = {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(item.ivTotal)}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        <span className={item.varianceAmount !== 0 ? 'font-semibold' : ''}>
                          {item.varianceAmount > 0 ? '+' : ''}
                          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(item.varianceAmount)}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-col gap-1">
                          {item.quantityMatch ? (
                            <Badge variant="outline" className="bg-green-50 text-green-700 w-fit">
                              <CheckCircle className="h-3 w-3 mr-1" />{t('crud.fields.quantity')}
                            </Badge>
                          ) : (
                            <Badge variant="destructive" className="w-fit">
                              <XCircle className="h-3 w-3 mr-1" />{t('crud.fields.quantity')}
                            </Badge>
                          )}
                          {item.priceMatch ? (
                            <Badge variant="outline" className="bg-green-50 text-green-700 w-fit">
                              <CheckCircle className="h-3 w-3 mr-1" />{t('crud.fields.price')}
                            </Badge>
                          ) : (
                            <Badge variant="destructive" className="w-fit">
                              <XCircle className="h-3 w-3 mr-1" />{t('crud.fields.price')}
                            </Badge>
                          )}
                          {item.qualityMatch ? (
                            <Badge variant="outline" className="bg-green-50 text-green-700 w-fit">
                              <CheckCircle className="h-3 w-3 mr-1" />{t('crud.fields.quality')}
                            </Badge>
                          ) : (
                            <Badge variant="destructive" className="w-fit">
                              <XCircle className="h-3 w-3 mr-1" />{t('crud.fields.quality')}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        {item.exceptions.length > 0 && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleException(item)}
                          >
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            {t('crud.fields.deviations')}
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button variant="outline" onClick={() => navigate('/einkauf/rechnungseingaenge-liste')} disabled={loading}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleApprove}
              disabled={loading || (blocked && !exceptionReason)}
              variant={blocked ? 'destructive' : 'default'}
            >
              <Receipt className="h-4 w-4 mr-2" />
              {loading ? t('common.loading') : t('crud.actions.approve')}
            </Button>
          </div>
        </>
      )}

      <Dialog open={exceptionDialogOpen} onOpenChange={setExceptionDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.fields.deviations')}</DialogTitle>
            <DialogDescription>
              {selectedException?.productName}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{t('crud.fields.exceptions')}</Label>
              <ul className="list-disc list-inside space-y-1 mt-2">
                {selectedException?.exceptions.map((exc, idx) => (
                  <li key={idx} className="text-sm text-muted-foreground">{exc}</li>
                ))}
              </ul>
            </div>
            {blocked && (
              <div>
                <Label htmlFor="exceptionReason">{t('crud.fields.reason')} *</Label>
                <Textarea
                  id="exceptionReason"
                  value={exceptionReason}
                  onChange={(e) => setExceptionReason(e.target.value)}
                  placeholder={t('crud.tooltips.placeholders.reason')}
                  required
                  minLength={10}
                />
                <p className="text-sm text-muted-foreground mt-1">
                  {t('crud.messages.reasonMinLength')}
                </p>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setExceptionDialogOpen(false)}>
              {t('common.close')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

