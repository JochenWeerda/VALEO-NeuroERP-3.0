import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Download, TrendingUp, AlertTriangle, BarChart3 } from 'lucide-react'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

export default function ProcurementReportsPage(): JSX.Element {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('open-orders')

  // Report Data
  const [openOrders, setOpenOrders] = useState<any[]>([])
  const [spendAnalysis, setSpendAnalysis] = useState<any>(null)
  const [supplierPerformance, setSupplierPerformance] = useState<any[]>([])
  const [toleranceReports, setToleranceReports] = useState<any[]>([])

  // Load Open Orders Report
  useEffect(() => {
    if (activeTab === 'open-orders') {
      loadOpenOrders()
    }
  }, [activeTab])

  // Load Spend Analysis
  useEffect(() => {
    if (activeTab === 'spend') {
      loadSpendAnalysis()
    }
  }, [activeTab])

  // Load Supplier Performance
  useEffect(() => {
    if (activeTab === 'performance') {
      loadSupplierPerformance()
    }
  }, [activeTab])

  // Load Tolerance Reports
  useEffect(() => {
    if (activeTab === 'tolerance') {
      loadToleranceReports()
    }
  }, [activeTab])

  const loadOpenOrders = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/api/mcp/documents/purchase_order?status=ENTWURF,FREIGEGEBEN,TEILGELIEFERT')
      const orders = response.data?.data || response.data || []
      setOpenOrders(orders)
    } catch (error: any) {
      console.error('Fehler beim Laden der offenen Bestellungen:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const loadSpendAnalysis = async () => {
    setLoading(true)
    try {
      // Mock data for now - would come from backend
      const mockSpend = {
        totalSpend: 1250000,
        period: '2025-01',
        byCategory: [
          { category: 'Saatgut', amount: 450000, percentage: 36 },
          { category: 'Düngemittel', amount: 380000, percentage: 30.4 },
          { category: 'Landtechnik', amount: 320000, percentage: 25.6 },
          { category: 'Sonstiges', amount: 100000, percentage: 8 },
        ],
        bySupplier: [
          { supplier: 'Müller Landhandel GmbH', amount: 280000, percentage: 22.4 },
          { supplier: 'Schmidt Agrar KG', amount: 195000, percentage: 15.6 },
          { supplier: 'Weber Saatgut AG', amount: 175000, percentage: 14 },
        ],
        trend: '+12.5%',
      }
      setSpendAnalysis(mockSpend)
    } catch (error: any) {
      console.error('Fehler beim Laden der Spend-Analyse:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const loadSupplierPerformance = async () => {
    setLoading(true)
    try {
      // Mock data for now - would come from backend
      const mockPerformance = [
        {
          supplier: 'Müller Landhandel GmbH',
          onTimeDelivery: 95.2,
          qualityScore: 4.5,
          priceScore: 4.2,
          serviceScore: 4.3,
          overallScore: 4.3,
          totalOrders: 45,
          totalSpend: 280000,
        },
        {
          supplier: 'Schmidt Agrar KG',
          onTimeDelivery: 88.7,
          qualityScore: 4.2,
          priceScore: 4.5,
          serviceScore: 4.0,
          overallScore: 4.2,
          totalOrders: 32,
          totalSpend: 195000,
        },
        {
          supplier: 'Weber Saatgut AG',
          onTimeDelivery: 92.1,
          qualityScore: 4.8,
          priceScore: 3.9,
          serviceScore: 4.4,
          overallScore: 4.3,
          totalOrders: 28,
          totalSpend: 175000,
        },
      ]
      setSupplierPerformance(mockPerformance)
    } catch (error: any) {
      console.error('Fehler beim Laden der Lieferantenperformance:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const loadToleranceReports = async () => {
    setLoading(true)
    try {
      // Mock data for now - would come from backend
      const mockTolerances = [
        {
          invoiceNumber: 'RE-2025-001',
          poNumber: 'PO-2025-045',
          supplier: 'Müller Landhandel GmbH',
          type: 'price',
          expected: 1250.00,
          actual: 1280.50,
          deviation: 30.50,
          percentage: 2.44,
          status: 'approved',
          reason: 'Preisanpassung vereinbart',
        },
        {
          invoiceNumber: 'RE-2025-002',
          poNumber: 'PO-2025-032',
          supplier: 'Schmidt Agrar KG',
          type: 'quantity',
          expected: 100,
          actual: 98,
          deviation: -2,
          percentage: -2.0,
          status: 'pending',
          reason: '',
        },
        {
          invoiceNumber: 'RE-2025-003',
          poNumber: 'PO-2025-028',
          supplier: 'Weber Saatgut AG',
          type: 'quality',
          expected: 'PERFECT',
          actual: 'GOOD',
          deviation: 'Qualitätsabweichung',
          percentage: 0,
          status: 'exception',
          reason: 'Leichte Qualitätsminderung',
        },
      ]
      setToleranceReports(mockTolerances)
    } catch (error: any) {
      console.error('Fehler beim Laden der Toleranzreports:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleExport = (reportType: string, data: any) => {
    try {
      let csvHeader = ''
      let csvContent = ''

      switch (reportType) {
        case 'open-orders':
          csvHeader = `${t('crud.fields.orderNumber')};${t('crud.entities.supplier')};${t('crud.fields.status')};${t('crud.fields.deliveryDate')};${t('crud.fields.totalAmount')}\n`
          csvContent = data.map((order: any) =>
            `"${order.nummer || order.number}";"${order.lieferant || order.supplier}";"${order.status}";"${order.liefertermin || order.deliveryDate}";"${order.gesamtbetrag || order.totalAmount}"`
          ).join('\n')
          break
        case 'spend':
          csvHeader = `${t('crud.fields.category')};${t('crud.fields.amount')};${t('crud.fields.percentage')}\n`
          csvContent = data.byCategory.map((item: any) =>
            `"${item.category}";"${item.amount}";"${item.percentage}%"`
          ).join('\n')
          break
        case 'performance':
          csvHeader = `${t('crud.entities.supplier')};${t('crud.fields.onTimeDelivery')};${t('crud.fields.quality')};${t('crud.fields.priceCompetitiveness')};${t('crud.fields.service')};${t('crud.fields.overallScore')}\n`
          csvContent = data.map((supplier: any) =>
            `"${supplier.supplier}";"${supplier.onTimeDelivery}%";"${supplier.qualityScore}";"${supplier.priceScore}";"${supplier.serviceScore}";"${supplier.overallScore}"`
          ).join('\n')
          break
        case 'tolerance':
          csvHeader = `${t('crud.fields.invoiceNumber')};${t('crud.fields.orderNumber')};${t('crud.entities.supplier')};${t('crud.fields.type')};${t('crud.fields.deviation')};${t('crud.fields.status')}\n`
          csvContent = data.map((item: any) =>
            `"${item.invoiceNumber}";"${item.poNumber}";"${item.supplier}";"${item.type}";"${item.deviation}";"${item.status}"`
          ).join('\n')
          break
      }

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `procurement-${reportType}-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      toast({
        title: t('crud.messages.exportSuccess'),
        description: t('crud.messages.exportedItems', { count: Array.isArray(data) ? data.length : 1, entityType: t('crud.fields.report') }),
      })
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.exportError'),
        description: t('crud.messages.exportFailed'),
      })
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{t('crud.fields.procurementReports')}</h1>
          <p className="text-muted-foreground mt-1">{t('crud.subtitles.procurementReports')}</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="open-orders">{t('crud.fields.openOrders')}</TabsTrigger>
          <TabsTrigger value="spend">{t('crud.fields.spendAnalysis')}</TabsTrigger>
          <TabsTrigger value="performance">{t('crud.fields.supplierPerformance')}</TabsTrigger>
          <TabsTrigger value="tolerance">{t('crud.fields.toleranceReports')}</TabsTrigger>
        </TabsList>

        {/* Open Orders Report */}
        <TabsContent value="open-orders">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.fields.openOrdersReport')}</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport('open-orders', openOrders)}
                  disabled={loading || openOrders.length === 0}
                >
                  <Download className="h-4 w-4 mr-2" />
                  {t('crud.actions.export')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">{t('common.loading')}</div>
              ) : openOrders.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">{t('crud.messages.noData')}</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.fields.orderNumber')}</TableHead>
                      <TableHead>{t('crud.entities.supplier')}</TableHead>
                      <TableHead>{t('crud.fields.status')}</TableHead>
                      <TableHead>{t('crud.fields.deliveryDate')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.totalAmount')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {openOrders.map((order: any) => (
                      <TableRow key={order.id || order.number}>
                        <TableCell><code className="text-sm">{order.nummer || order.number}</code></TableCell>
                        <TableCell>{order.lieferant || order.supplier}</TableCell>
                        <TableCell>
                          <Badge variant={order.status === 'STORNIERT' ? 'destructive' : 'default'}>
                            {order.status}
                          </Badge>
                        </TableCell>
                        <TableCell>{formatDate(order.liefertermin || order.deliveryDate)}</TableCell>
                        <TableCell className="text-right">{formatNumber(order.gesamtbetrag || order.totalAmount, 2)} €</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Spend Analysis Report */}
        <TabsContent value="spend">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.fields.spendAnalysisReport')}</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport('spend', spendAnalysis)}
                  disabled={loading || !spendAnalysis}
                >
                  <Download className="h-4 w-4 mr-2" />
                  {t('crud.actions.export')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">{t('common.loading')}</div>
              ) : !spendAnalysis ? (
                <div className="text-center py-8 text-muted-foreground">{t('crud.messages.noData')}</div>
              ) : (
                <div className="space-y-6">
                  <div className="grid grid-cols-3 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold">{formatNumber(spendAnalysis.totalSpend, 0)} €</div>
                        <p className="text-sm text-muted-foreground">{t('crud.fields.totalSpend')}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-green-600">{spendAnalysis.trend}</div>
                        <p className="text-sm text-muted-foreground">{t('crud.fields.trend')}</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold">{spendAnalysis.period}</div>
                        <p className="text-sm text-muted-foreground">{t('crud.fields.period')}</p>
                      </CardContent>
                    </Card>
                  </div>

                  <div>
                    <h3 className="text-lg font-semibold mb-4">{t('crud.fields.spendByCategory')}</h3>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>{t('crud.fields.category')}</TableHead>
                          <TableHead className="text-right">{t('crud.fields.amount')}</TableHead>
                          <TableHead className="text-right">{t('crud.fields.percentage')}</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {spendAnalysis.byCategory.map((item: any, index: number) => (
                          <TableRow key={index}>
                            <TableCell>{item.category}</TableCell>
                            <TableCell className="text-right">{formatNumber(item.amount, 0)} €</TableCell>
                            <TableCell className="text-right">{item.percentage}%</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Supplier Performance Report */}
        <TabsContent value="performance">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.fields.supplierPerformanceReport')}</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport('performance', supplierPerformance)}
                  disabled={loading || supplierPerformance.length === 0}
                >
                  <Download className="h-4 w-4 mr-2" />
                  {t('crud.actions.export')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">{t('common.loading')}</div>
              ) : supplierPerformance.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">{t('crud.messages.noData')}</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.entities.supplier')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.onTimeDelivery')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.quality')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.priceCompetitiveness')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.service')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.overallScore')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.totalOrders')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {supplierPerformance.map((supplier: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell>{supplier.supplier}</TableCell>
                        <TableCell className="text-right">{supplier.onTimeDelivery}%</TableCell>
                        <TableCell className="text-right">{supplier.qualityScore} / 5.0</TableCell>
                        <TableCell className="text-right">{supplier.priceScore} / 5.0</TableCell>
                        <TableCell className="text-right">{supplier.serviceScore} / 5.0</TableCell>
                        <TableCell className="text-right">
                          <Badge variant={supplier.overallScore >= 4 ? 'default' : supplier.overallScore >= 3 ? 'secondary' : 'destructive'}>
                            {supplier.overallScore} / 5.0
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">{supplier.totalOrders}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tolerance Reports */}
        <TabsContent value="tolerance">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.fields.toleranceReports')}</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleExport('tolerance', toleranceReports)}
                  disabled={loading || toleranceReports.length === 0}
                >
                  <Download className="h-4 w-4 mr-2" />
                  {t('crud.actions.export')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">{t('common.loading')}</div>
              ) : toleranceReports.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">{t('crud.messages.noData')}</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.fields.invoiceNumber')}</TableHead>
                      <TableHead>{t('crud.fields.orderNumber')}</TableHead>
                      <TableHead>{t('crud.entities.supplier')}</TableHead>
                      <TableHead>{t('crud.fields.type')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.deviation')}</TableHead>
                      <TableHead>{t('crud.fields.status')}</TableHead>
                      <TableHead>{t('crud.fields.reason')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {toleranceReports.map((item: any, index: number) => (
                      <TableRow key={index}>
                        <TableCell><code className="text-sm">{item.invoiceNumber}</code></TableCell>
                        <TableCell><code className="text-sm">{item.poNumber}</code></TableCell>
                        <TableCell>{item.supplier}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{item.type}</Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          {typeof item.deviation === 'number' ? (
                            <span className={item.deviation > 0 ? 'text-red-600' : 'text-green-600'}>
                              {item.deviation > 0 ? '+' : ''}{formatNumber(item.deviation, 2)} {item.type === 'price' ? '€' : ''}
                              {item.percentage !== 0 && ` (${item.percentage > 0 ? '+' : ''}${item.percentage}%)`}
                            </span>
                          ) : (
                            <span>{item.deviation}</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge variant={item.status === 'approved' ? 'default' : item.status === 'exception' ? 'destructive' : 'secondary'}>
                            {item.status === 'approved' ? t('crud.fields.approved') : item.status === 'exception' ? t('crud.fields.exception') : t('crud.fields.pending')}
                          </Badge>
                        </TableCell>
                        <TableCell className="max-w-xs truncate">{item.reason || '-'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

