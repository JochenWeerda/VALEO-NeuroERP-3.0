import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Upload, Download, Plus, FileSpreadsheet, FileText, X, CheckCircle, AlertTriangle } from 'lucide-react'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'

type Bid = {
  id: string
  rfqId: string
  supplierId: string
  supplierName: string
  items: Array<{
    rfqItemId: string
    quantity: number
    unitPrice: number
    totalPrice: number
    currency: string
    deliveryDate: string
    leadTime: number
    notes?: string
  }>
  totalValue: number
  currency: string
  submittedBy: string
  submittedAt: string
  status: 'SUBMITTED' | 'UNDER_REVIEW' | 'ACCEPTED' | 'REJECTED'
  evaluationScore?: number
  evaluationNotes?: string
  attachments?: string[]
}

export default function RfqBidsPage(): JSX.Element {
  const { t } = useTranslation()
  const { rfqId } = useParams<{ rfqId: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [rfq, setRfq] = useState<any>(null)
  const [bids, setBids] = useState<Bid[]>([])
  const [selectedBid, setSelectedBid] = useState<Bid | null>(null)
  const [bidDialogOpen, setBidDialogOpen] = useState(false)
  const [importDialogOpen, setImportDialogOpen] = useState(false)
  const [comparisonDialogOpen, setComparisonDialogOpen] = useState(false)
  const [awardDialogOpen, setAwardDialogOpen] = useState(false)
  const [selectedBidForAward, setSelectedBidForAward] = useState<Bid | null>(null)
  const [awardDecision, setAwardDecision] = useState({
    selectedBidId: '',
    decisionReason: '',
    evaluationCriteria: {
      price: 0,
      leadTime: 0,
      quality: 0,
      service: 0,
      total: 0,
    },
  })
  const [newBid, setNewBid] = useState({
    supplierId: '',
    supplierName: '',
    items: [] as Array<{
      rfqItemId: string
      quantity: number
      unitPrice: number
      deliveryDate: string
      leadTime: number
      notes: string
    }>,
    totalValue: 0,
    currency: 'EUR',
    paymentTerms: '',
    deliveryTerms: '',
    notes: '',
  })
  const [availableSuppliers, setAvailableSuppliers] = useState<any[]>([])

  useEffect(() => {
    if (rfqId) {
      loadRfq()
      loadBids()
      loadSuppliers()
    }
  }, [rfqId])

  const loadRfq = async () => {
    try {
      const response = await apiClient.get(`/api/einkauf/anfragen/${rfqId}`)
      setRfq(response.data)
    } catch (error: any) {
      console.error('Fehler beim Laden der RFQ:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: error.message,
      })
    }
  }

  const loadBids = async () => {
    setLoading(true)
    try {
      // Mock data for now - would come from backend
      const mockBids: Bid[] = [
        {
          id: 'bid-1',
          rfqId: rfqId || '',
          supplierId: 'supplier-1',
          supplierName: 'Müller Landhandel GmbH',
          items: [
            {
              rfqItemId: 'item-1',
              quantity: 100,
              unitPrice: 250.00,
              totalPrice: 25000.00,
              currency: 'EUR',
              deliveryDate: '2025-03-15',
              leadTime: 30,
              notes: 'Verfügbar ab März',
            },
          ],
          totalValue: 25000.00,
          currency: 'EUR',
          submittedBy: 'Max Mustermann',
          submittedAt: '2025-01-28T10:00:00Z',
          status: 'SUBMITTED',
        },
        {
          id: 'bid-2',
          rfqId: rfqId || '',
          supplierId: 'supplier-2',
          supplierName: 'Schmidt Agrar KG',
          items: [
            {
              rfqItemId: 'item-1',
              quantity: 100,
              unitPrice: 245.00,
              totalPrice: 24500.00,
              currency: 'EUR',
              deliveryDate: '2025-03-20',
              leadTime: 35,
              notes: 'Bulk-Discount bei 100+ t',
            },
          ],
          totalValue: 24500.00,
          currency: 'EUR',
          submittedBy: 'Anna Schmidt',
          submittedAt: '2025-01-28T14:30:00Z',
          status: 'SUBMITTED',
        },
      ]
      setBids(mockBids)
    } catch (error: any) {
      console.error('Fehler beim Laden der Bids:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const loadSuppliers = async () => {
    try {
      const response = await apiClient.get('/api/partners?type=supplier')
      const suppliers = (response as any).data?.data || (response as any).data || []
      setAvailableSuppliers(suppliers)
    } catch (error) {
      console.error('Fehler beim Laden der Lieferanten:', error)
    }
  }

  const handleAddBid = () => {
    setNewBid({
      supplierId: '',
      supplierName: '',
      items: rfq?.items?.map((item: any) => ({
        rfqItemId: item.id || item.anfrageNummer,
        quantity: item.menge || 0,
        unitPrice: 0,
        deliveryDate: '',
        leadTime: 0,
        notes: '',
      })) || [],
      totalValue: 0,
      currency: 'EUR',
      paymentTerms: '',
      deliveryTerms: '',
      notes: '',
    })
    setBidDialogOpen(true)
  }

  const handleSaveBid = () => {
    if (!newBid.supplierId) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.fillRequiredFields'),
      })
      return
    }

    // Calculate total value
    const totalValue = newBid.items.reduce((sum, item) => {
      const itemTotal = item.quantity * item.unitPrice
      return sum + itemTotal
    }, 0)

    const bid: Bid = {
      id: `bid-${Date.now()}`,
      rfqId: rfqId || '',
      supplierId: newBid.supplierId,
      supplierName: newBid.supplierName,
      items: newBid.items.map(item => ({
        ...item,
        totalPrice: item.quantity * item.unitPrice,
        currency: newBid.currency,
      })),
      totalValue,
      currency: newBid.currency,
      submittedBy: 'Current User', // Would come from auth
      submittedAt: new Date().toISOString(),
      status: 'SUBMITTED',
    }

    setBids([...bids, bid])
    setBidDialogOpen(false)
    toast({
      title: t('crud.messages.createSuccess', { entityType: t('crud.fields.bid') }),
    })
  }

  const handleImportBids = async (file: File) => {
    try {
      // Mock import - would parse CSV/Excel
      toast({
        title: t('crud.messages.importInfo'),
        description: t('crud.messages.importComingSoon'),
      })
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.importError'),
        description: error.message,
      })
    }
  }

  const handleCompareBids = () => {
    if (bids.length < 2) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.minimumTwoBidsRequired'),
      })
      return
    }
    setComparisonDialogOpen(true)
  }

  const handleAwardBid = (bid: Bid) => {
    setSelectedBidForAward(bid)
    setAwardDecision({
      selectedBidId: bid.id,
      decisionReason: '',
      evaluationCriteria: {
        price: 0,
        leadTime: 0,
        quality: 0,
        service: 0,
        total: 0,
      },
    })
    setAwardDialogOpen(true)
  }

  const handleSaveAward = () => {
    if (!awardDecision.decisionReason || awardDecision.decisionReason.length < 10) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.messages.reasonMinLength'),
      })
      return
    }

    // Calculate total score
    const totalScore = (
      awardDecision.evaluationCriteria.price +
      awardDecision.evaluationCriteria.leadTime +
      awardDecision.evaluationCriteria.quality +
      awardDecision.evaluationCriteria.service
    ) / 4

    // Update bid status
    const updatedBids = bids.map(bid => {
      if (bid.id === awardDecision.selectedBidId) {
        return {
          ...bid,
          status: 'ACCEPTED' as const,
          evaluationScore: totalScore,
          evaluationNotes: awardDecision.decisionReason,
        }
      } else {
        return {
          ...bid,
          status: 'REJECTED' as const,
        }
      }
    })

    setBids(updatedBids)
    setAwardDialogOpen(false)
    setSelectedBidForAward(null)

    toast({
      title: t('crud.messages.awardSuccess'),
      description: t('crud.messages.bidAwarded', { supplier: selectedBidForAward?.supplierName }),
    })
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t('crud.fields.bids')} - {rfq?.anfrageNummer || rfqId}</h1>
          <p className="text-muted-foreground mt-1">{t('crud.subtitles.manageBids')}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setImportDialogOpen(true)}
            disabled={loading}
          >
            <Upload className="h-4 w-4 mr-2" />
            {t('crud.actions.import')}
          </Button>
          <Button
            variant="outline"
            onClick={handleCompareBids}
            disabled={loading || bids.length < 2}
          >
            <FileText className="h-4 w-4 mr-2" />
            {t('crud.actions.compare')}
          </Button>
          <Button
            onClick={handleAddBid}
            disabled={loading}
          >
            <Plus className="h-4 w-4 mr-2" />
            {t('crud.actions.addBid')}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="bids">
        <TabsList>
          <TabsTrigger value="bids">{t('crud.fields.bids')} ({bids.length})</TabsTrigger>
          <TabsTrigger value="summary">{t('crud.fields.summary')}</TabsTrigger>
        </TabsList>

        <TabsContent value="bids">
          <Card>
            <CardHeader>
              <CardTitle>{t('crud.fields.bids')}</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">{t('common.loading')}</div>
              ) : bids.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <p>{t('crud.messages.noBids')}</p>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={handleAddBid}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    {t('crud.actions.addBid')}
                  </Button>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.entities.supplier')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.totalValue')}</TableHead>
                      <TableHead>{t('crud.fields.currency')}</TableHead>
                      <TableHead>{t('crud.fields.deliveryDate')}</TableHead>
                      <TableHead>{t('crud.fields.leadTime')}</TableHead>
                      <TableHead>{t('crud.fields.status')}</TableHead>
                      <TableHead>{t('crud.fields.submittedAt')}</TableHead>
                      <TableHead>{t('crud.fields.actions')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {bids.map((bid) => (
                      <TableRow key={bid.id}>
                        <TableCell className="font-medium">{bid.supplierName}</TableCell>
                        <TableCell className="text-right">{formatNumber(bid.totalValue, 2)} {bid.currency}</TableCell>
                        <TableCell>{bid.currency}</TableCell>
                        <TableCell>
                          {bid.items[0]?.deliveryDate ? formatDate(bid.items[0].deliveryDate) : '-'}
                        </TableCell>
                        <TableCell>{bid.items[0]?.leadTime ? `${bid.items[0].leadTime} ${t('crud.fields.days')}` : '-'}</TableCell>
                        <TableCell>
                          <Badge variant={
                            bid.status === 'ACCEPTED' ? 'default' :
                            bid.status === 'REJECTED' ? 'destructive' :
                            bid.status === 'UNDER_REVIEW' ? 'secondary' :
                            'outline'
                          }>
                            {bid.status === 'ACCEPTED' ? t('crud.fields.accepted') :
                             bid.status === 'REJECTED' ? t('crud.fields.rejected') :
                             bid.status === 'UNDER_REVIEW' ? t('crud.fields.underReview') :
                             t('crud.fields.submitted')}
                          </Badge>
                        </TableCell>
                        <TableCell>{formatDate(bid.submittedAt)}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => {
                                setSelectedBid(bid)
                                setBidDialogOpen(true)
                              }}
                            >
                              {t('crud.actions.view')}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="summary">
          <Card>
            <CardHeader>
              <CardTitle>{t('crud.fields.bidSummary')}</CardTitle>
            </CardHeader>
            <CardContent>
              {bids.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">{t('crud.messages.noBids')}</div>
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-4 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold">{bids.length}</div>
                        <p className="text-sm text-muted-foreground">{t('crud.fields.totalBids')}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold">
                          {formatNumber(
                            bids.reduce((sum, bid) => sum + bid.totalValue, 0) / bids.length,
                            2
                          )} {bids[0]?.currency || 'EUR'}
                        </div>
                        <p className="text-sm text-muted-foreground">{t('crud.fields.averageBidValue')}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-green-600">
                          {formatNumber(
                            Math.min(...bids.map(bid => bid.totalValue)),
                            2
                          )} {bids[0]?.currency || 'EUR'}
                        </div>
                        <p className="text-sm text-muted-foreground">{t('crud.fields.lowestBid')}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-red-600">
                          {formatNumber(
                            Math.max(...bids.map(bid => bid.totalValue)),
                            2
                          )} {bids[0]?.currency || 'EUR'}
                        </div>
                        <p className="text-sm text-muted-foreground">{t('crud.fields.highestBid')}</p>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Add/Edit Bid Dialog */}
      <Dialog open={bidDialogOpen} onOpenChange={setBidDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedBid ? t('crud.actions.editBid') : t('crud.actions.addBid')}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.bid.description')}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="supplier">{t('crud.entities.supplier')} *</Label>
              <Select
                value={newBid.supplierId}
                onValueChange={(value) => {
                  const supplier = availableSuppliers.find(s => s.id === value)
                  setNewBid(prev => ({
                    ...prev,
                    supplierId: value,
                    supplierName: supplier?.name || '',
                  }))
                }}
                disabled={!!selectedBid}
              >
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.tooltips.placeholders.selectSupplier')} />
                </SelectTrigger>
                <SelectContent>
                  {availableSuppliers.map((supplier) => (
                    <SelectItem key={supplier.id} value={supplier.id}>
                      {supplier.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>{t('crud.fields.items')}</Label>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('crud.fields.product')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.quantity')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.unitPrice')}</TableHead>
                    <TableHead className="text-right">{t('crud.fields.totalPrice')}</TableHead>
                    <TableHead>{t('crud.fields.deliveryDate')}</TableHead>
                    <TableHead>{t('crud.fields.leadTime')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {newBid.items.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>{rfq?.artikel || '-'}</TableCell>
                      <TableCell className="text-right">
                        <Input
                          type="number"
                          value={item.quantity}
                          onChange={(e) => {
                            const updatedItems = [...newBid.items]
                            updatedItems[index].quantity = Number(e.target.value)
                            setNewBid(prev => ({ ...prev, items: updatedItems }))
                          }}
                          className="w-20"
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        <Input
                          type="number"
                          step="0.01"
                          value={item.unitPrice}
                          onChange={(e) => {
                            const updatedItems = [...newBid.items]
                            updatedItems[index].unitPrice = Number(e.target.value)
                            setNewBid(prev => ({ ...prev, items: updatedItems }))
                          }}
                          className="w-24"
                        />
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {formatNumber(item.quantity * item.unitPrice, 2)} {newBid.currency}
                      </TableCell>
                      <TableCell>
                        <Input
                          type="date"
                          value={item.deliveryDate}
                          onChange={(e) => {
                            const updatedItems = [...newBid.items]
                            updatedItems[index].deliveryDate = e.target.value
                            setNewBid(prev => ({ ...prev, items: updatedItems }))
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={item.leadTime}
                          onChange={(e) => {
                            const updatedItems = [...newBid.items]
                            updatedItems[index].leadTime = Number(e.target.value)
                            setNewBid(prev => ({ ...prev, items: updatedItems }))
                          }}
                          className="w-20"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            <div>
              <Label htmlFor="notes">{t('crud.fields.notes')}</Label>
              <Textarea
                id="notes"
                value={newBid.notes}
                onChange={(e) => setNewBid(prev => ({ ...prev, notes: e.target.value }))}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setBidDialogOpen(false)
              setSelectedBid(null)
            }}>
              {t('common.cancel')}
            </Button>
            <Button onClick={handleSaveBid} disabled={!newBid.supplierId}>
              {t('common.save')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Import Dialog */}
      <Dialog open={importDialogOpen} onOpenChange={setImportDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('crud.actions.importBids')}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.importBids.description')}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="importFile">{t('crud.fields.file')}</Label>
              <Input
                id="importFile"
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    handleImportBids(file)
                  }
                }}
              />
              <p className="text-sm text-muted-foreground mt-1">
                {t('crud.dialogs.importBids.supportedFormats')}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setImportDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Comparison Dialog */}
      <Dialog open={comparisonDialogOpen} onOpenChange={setComparisonDialogOpen}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('crud.actions.compareBids')}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.compareBids.description')}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Tabs defaultValue="matrix">
              <TabsList>
                <TabsTrigger value="matrix">{t('crud.fields.comparisonMatrix')}</TabsTrigger>
                <TabsTrigger value="criteria">{t('crud.fields.multiCriteriaComparison')}</TabsTrigger>
              </TabsList>

              <TabsContent value="matrix">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.entities.supplier')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.totalValue')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.unitPrice')}</TableHead>
                      <TableHead>{t('crud.fields.deliveryDate')}</TableHead>
                      <TableHead>{t('crud.fields.leadTime')}</TableHead>
                      <TableHead>{t('crud.fields.paymentTerms')}</TableHead>
                      <TableHead>{t('crud.fields.evaluationScore')}</TableHead>
                      <TableHead>{t('crud.fields.actions')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {bids.map((bid) => {
                      const isLowestPrice = bid.totalValue === Math.min(...bids.map(b => b.totalValue))
                      const isShortestLeadTime = bid.items[0]?.leadTime === Math.min(...bids.map(b => b.items[0]?.leadTime || Infinity))
                      
                      return (
                        <TableRow key={bid.id}>
                          <TableCell className="font-medium">{bid.supplierName}</TableCell>
                          <TableCell className={`text-right ${isLowestPrice ? 'font-bold text-green-600' : ''}`}>
                            {formatNumber(bid.totalValue, 2)} {bid.currency}
                            {isLowestPrice && <Badge variant="outline" className="ml-2">{t('crud.fields.bestPrice')}</Badge>}
                          </TableCell>
                          <TableCell className="text-right">
                            {bid.items[0] ? formatNumber(bid.items[0].unitPrice, 2) : '-'} {bid.currency}
                          </TableCell>
                          <TableCell>
                            {bid.items[0]?.deliveryDate ? formatDate(bid.items[0].deliveryDate) : '-'}
                          </TableCell>
                          <TableCell className={isShortestLeadTime ? 'font-bold text-green-600' : ''}>
                            {bid.items[0]?.leadTime ? `${bid.items[0].leadTime} ${t('crud.fields.days')}` : '-'}
                            {isShortestLeadTime && <Badge variant="outline" className="ml-2">{t('crud.fields.fastestDelivery')}</Badge>}
                          </TableCell>
                          <TableCell>{newBid.paymentTerms || '-'}</TableCell>
                          <TableCell>
                            {bid.evaluationScore ? (
                              <Badge variant="default">{bid.evaluationScore.toFixed(1)} / 5.0</Badge>
                            ) : (
                              <span className="text-muted-foreground">-</span>
                            )}
                          </TableCell>
                          <TableCell>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setComparisonDialogOpen(false)
                                handleAwardBid(bid)
                              }}
                              disabled={bid.status === 'ACCEPTED' || bid.status === 'REJECTED'}
                            >
                              {t('crud.actions.awardBid')}
                            </Button>
                          </TableCell>
                        </TableRow>
                      )
                    })}
                  </TableBody>
                </Table>
              </TabsContent>

              <TabsContent value="criteria">
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <Card>
                      <CardHeader>
                        <CardTitle>{t('crud.fields.priceComparison')}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {bids
                            .sort((a, b) => a.totalValue - b.totalValue)
                            .map((bid, index) => (
                              <div key={bid.id} className="flex items-center justify-between p-2 border rounded">
                                <span className={index === 0 ? 'font-bold text-green-600' : ''}>
                                  {bid.supplierName}
                                </span>
                                <span className={index === 0 ? 'font-bold text-green-600' : ''}>
                                  {formatNumber(bid.totalValue, 2)} {bid.currency}
                                </span>
                              </div>
                            ))}
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle>{t('crud.fields.leadTimeComparison')}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {bids
                            .sort((a, b) => (a.items[0]?.leadTime || Infinity) - (b.items[0]?.leadTime || Infinity))
                            .map((bid, index) => (
                              <div key={bid.id} className="flex items-center justify-between p-2 border rounded">
                                <span className={index === 0 ? 'font-bold text-green-600' : ''}>
                                  {bid.supplierName}
                                </span>
                                <span className={index === 0 ? 'font-bold text-green-600' : ''}>
                                  {bid.items[0]?.leadTime ? `${bid.items[0].leadTime} ${t('crud.fields.days')}` : '-'}
                                </span>
                              </div>
                            ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  <Card>
                    <CardHeader>
                      <CardTitle>{t('crud.fields.weightedScoreComparison')}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>{t('crud.entities.supplier')}</TableHead>
                            <TableHead className="text-right">{t('crud.fields.price')} (40%)</TableHead>
                            <TableHead className="text-right">{t('crud.fields.leadTime')} (30%)</TableHead>
                            <TableHead className="text-right">{t('crud.fields.quality')} (20%)</TableHead>
                            <TableHead className="text-right">{t('crud.fields.service')} (10%)</TableHead>
                            <TableHead className="text-right font-bold">{t('crud.fields.totalScore')}</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {bids.map((bid) => {
                            // Mock scores - would come from evaluation
                            const priceScore = 5 - ((bid.totalValue - Math.min(...bids.map(b => b.totalValue))) / Math.max(...bids.map(b => b.totalValue)) * 5)
                            const leadTimeScore = bid.items[0]?.leadTime ? 5 - ((bid.items[0].leadTime - Math.min(...bids.map(b => b.items[0]?.leadTime || Infinity))) / Math.max(...bids.map(b => b.items[0]?.leadTime || 1)) * 5) : 0
                            const qualityScore = bid.evaluationScore || 3.5
                            const serviceScore = 4.0
                            const totalScore = (priceScore * 0.4) + (leadTimeScore * 0.3) + (qualityScore * 0.2) + (serviceScore * 0.1)

                            return (
                              <TableRow key={bid.id}>
                                <TableCell className="font-medium">{bid.supplierName}</TableCell>
                                <TableCell className="text-right">{priceScore.toFixed(1)}</TableCell>
                                <TableCell className="text-right">{leadTimeScore.toFixed(1)}</TableCell>
                                <TableCell className="text-right">{qualityScore.toFixed(1)}</TableCell>
                                <TableCell className="text-right">{serviceScore.toFixed(1)}</TableCell>
                                <TableCell className="text-right font-bold">
                                  <Badge variant={totalScore >= 4 ? 'default' : totalScore >= 3 ? 'secondary' : 'outline'}>
                                    {totalScore.toFixed(2)} / 5.0
                                  </Badge>
                                </TableCell>
                              </TableRow>
                            )
                          })}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setComparisonDialogOpen(false)}>
              {t('common.close')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Award Dialog */}
      <Dialog open={awardDialogOpen} onOpenChange={setAwardDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>{t('crud.actions.awardBid')}</DialogTitle>
            <DialogDescription>
              {t('crud.dialogs.awardBid.description', { supplier: selectedBidForAward?.supplierName })}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {selectedBidForAward && (
              <Card>
                <CardHeader>
                  <CardTitle>{t('crud.fields.selectedBid')}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="font-medium">{t('crud.entities.supplier')}:</span>
                      <span>{selectedBidForAward.supplierName}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">{t('crud.fields.totalValue')}:</span>
                      <span>{formatNumber(selectedBidForAward.totalValue, 2)} {selectedBidForAward.currency}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">{t('crud.fields.deliveryDate')}:</span>
                      <span>{selectedBidForAward.items[0]?.deliveryDate ? formatDate(selectedBidForAward.items[0].deliveryDate) : '-'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="font-medium">{t('crud.fields.leadTime')}:</span>
                      <span>{selectedBidForAward.items[0]?.leadTime ? `${selectedBidForAward.items[0].leadTime} ${t('crud.fields.days')}` : '-'}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            <div>
              <Label>{t('crud.fields.evaluationCriteria')}</Label>
              <div className="grid grid-cols-2 gap-4 mt-2">
                <div>
                  <Label htmlFor="priceScore">{t('crud.fields.price')} (1-5)</Label>
                  <Input
                    id="priceScore"
                    type="number"
                    min="1"
                    max="5"
                    step="0.1"
                    value={awardDecision.evaluationCriteria.price}
                    onChange={(e) => setAwardDecision(prev => ({
                      ...prev,
                      evaluationCriteria: {
                        ...prev.evaluationCriteria,
                        price: Number(e.target.value),
                      },
                    }))}
                  />
                </div>
                <div>
                  <Label htmlFor="leadTimeScore">{t('crud.fields.leadTime')} (1-5)</Label>
                  <Input
                    id="leadTimeScore"
                    type="number"
                    min="1"
                    max="5"
                    step="0.1"
                    value={awardDecision.evaluationCriteria.leadTime}
                    onChange={(e) => setAwardDecision(prev => ({
                      ...prev,
                      evaluationCriteria: {
                        ...prev.evaluationCriteria,
                        leadTime: Number(e.target.value),
                      },
                    }))}
                  />
                </div>
                <div>
                  <Label htmlFor="qualityScore">{t('crud.fields.quality')} (1-5)</Label>
                  <Input
                    id="qualityScore"
                    type="number"
                    min="1"
                    max="5"
                    step="0.1"
                    value={awardDecision.evaluationCriteria.quality}
                    onChange={(e) => setAwardDecision(prev => ({
                      ...prev,
                      evaluationCriteria: {
                        ...prev.evaluationCriteria,
                        quality: Number(e.target.value),
                      },
                    }))}
                  />
                </div>
                <div>
                  <Label htmlFor="serviceScore">{t('crud.fields.service')} (1-5)</Label>
                  <Input
                    id="serviceScore"
                    type="number"
                    min="1"
                    max="5"
                    step="0.1"
                    value={awardDecision.evaluationCriteria.service}
                    onChange={(e) => setAwardDecision(prev => ({
                      ...prev,
                      evaluationCriteria: {
                        ...prev.evaluationCriteria,
                        service: Number(e.target.value),
                      },
                    }))}
                  />
                </div>
              </div>
              <div className="mt-2 p-2 bg-muted rounded">
                <div className="flex justify-between">
                  <span className="font-medium">{t('crud.fields.totalScore')}:</span>
                  <span className="font-bold">
                    {((awardDecision.evaluationCriteria.price +
                      awardDecision.evaluationCriteria.leadTime +
                      awardDecision.evaluationCriteria.quality +
                      awardDecision.evaluationCriteria.service) / 4).toFixed(1)} / 5.0
                  </span>
                </div>
              </div>
            </div>

            <div>
              <Label htmlFor="decisionReason">{t('crud.fields.decisionReason')} *</Label>
              <Textarea
                id="decisionReason"
                value={awardDecision.decisionReason}
                onChange={(e) => setAwardDecision(prev => ({ ...prev, decisionReason: e.target.value }))}
                placeholder={t('crud.tooltips.placeholders.decisionReason')}
                rows={4}
                required
                minLength={10}
              />
              <p className="text-sm text-muted-foreground mt-1">
                {t('crud.messages.reasonMinLength')}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => {
              setAwardDialogOpen(false)
              setSelectedBidForAward(null)
            }}>
              {t('common.cancel')}
            </Button>
            <Button
              onClick={handleSaveAward}
              disabled={!awardDecision.decisionReason || awardDecision.decisionReason.length < 10}
            >
              {t('crud.actions.awardBid')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

