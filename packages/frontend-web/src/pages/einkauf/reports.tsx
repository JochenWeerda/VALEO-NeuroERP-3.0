import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Download } from 'lucide-react'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { toast } from '@/hooks/use-toast'
import { useEinkaufReports, useEinkaufReportsStandard } from '@/lib/api/einkauf'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'

export default function ProcurementReportsPage(): JSX.Element {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState('open-orders')

  const {
    data: baseData,
    isLoading: isBaseLoading,
    isError: isBaseError,
    error: baseError,
    refetch: refetchBase,
  } = useEinkaufReports()

  const {
    data: standardData,
    isLoading: isStandardLoading,
    isError: isStandardError,
    error: standardError,
    refetch: refetchStandard,
  } = useEinkaufReportsStandard()

  const loading = isBaseLoading || isStandardLoading

  if (isBaseError || isStandardError) {
    return (
      <ErrorState
        error={(baseError || standardError) as Error}
        onRetry={() => {
          void refetchBase()
          void refetchStandard()
        }}
      />
    )
  }

  const openOrders = standardData?.openOrders ?? []
  const spendByCategory = baseData?.spendByCategory ?? []
  const supplierPerformance = standardData?.supplierPerformance ?? baseData?.supplierPerformance ?? []
  const toleranceReports = standardData?.toleranceReports ?? []

  const spendAnalysis = {
    totalSpend: spendByCategory.reduce((sum: number, item: any) => sum + Number(item.amount || item.betrag || 0), 0),
    period: new Date().toISOString().slice(0, 7),
    byCategory: spendByCategory,
  }

  const handleExport = (reportType: string, data: any) => {
    try {
      let csvHeader = ''
      let csvContent = ''

      switch (reportType) {
        case 'open-orders':
          csvHeader = `${t('crud.fields.orderNumber')};${t('crud.entities.supplier')};${t('crud.fields.status')};${t('crud.fields.deliveryDate')};${t('crud.fields.totalAmount')}\n`
          csvContent = data
            .map(
              (order: any) =>
                `"${order.purchaseOrderNumber || ''}";"${order.supplierName || order.supplierId || ''}";"${order.status || ''}";"${order.deliveryDate || ''}";"${order.totalAmount || 0}"`,
            )
            .join('\n')
          break
        case 'spend':
          csvHeader = `${t('crud.fields.category')};${t('crud.fields.amount')};${t('crud.fields.percentage')}\n`
          csvContent = data
            .map((item: any) => `"${item.category || item.kategorie}";"${item.amount || item.betrag || 0}";"${item.percentage || item.anteil || 0}%"`)
            .join('\n')
          break
        case 'performance':
          csvHeader = `${t('crud.entities.supplier')};${t('crud.fields.onTimeDelivery')};${t('crud.fields.quality')};${t('crud.fields.priceCompetitiveness')};${t('crud.fields.service')};${t('crud.fields.overallScore')}\n`
          csvContent = data
            .map(
              (supplier: any) =>
                `"${supplier.supplier || ''}";"${supplier.onTimeDelivery || 0}%";"${supplier.qualityScore || 0}";"${supplier.priceScore || 0}";"${supplier.serviceScore || 0}";"${supplier.overallScore || 0}"`,
            )
            .join('\n')
          break
        case 'tolerance':
          csvHeader = `${t('crud.fields.orderNumber')};${t('crud.fields.type')};${t('crud.fields.deviation')}\n`
          csvContent = data
            .map((item: any) => `"${item.purchaseOrderNumber || ''}";"${item.type || ''}";"${item.deviation || 0}"`)
            .join('\n')
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
      })
    } catch {
      toast({
        variant: 'destructive',
        title: t('crud.messages.exportError'),
      })
    }
  }

  if (loading) {
    return (
      <div className="p-3 md:p-6 space-y-4">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-[400px] w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-3 md:p-6">
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

        <TabsContent value="open-orders">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.fields.openOrdersReport')}</CardTitle>
                <Button variant="outline" size="sm" onClick={() => handleExport('open-orders', openOrders)} disabled={openOrders.length === 0}>
                  <Download className="h-4 w-4 mr-2" />
                  {t('crud.actions.export')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {openOrders.length === 0 ? (
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
                      <TableRow key={order.id || order.purchaseOrderNumber}>
                        <TableCell><code className="text-sm">{order.purchaseOrderNumber || '-'}</code></TableCell>
                        <TableCell>{order.supplierName || order.supplierId || '-'}</TableCell>
                        <TableCell>
                          <Badge variant={order.status === 'STORNIERT' ? 'destructive' : 'default'}>{order.status || '-'}</Badge>
                        </TableCell>
                        <TableCell>{formatDate(order.deliveryDate)}</TableCell>
                        <TableCell className="text-right">{formatNumber(order.totalAmount || 0, 2)} EUR</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="spend">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.fields.spendAnalysisReport')}</CardTitle>
                <Button variant="outline" size="sm" onClick={() => handleExport('spend', spendByCategory)} disabled={spendByCategory.length === 0}>
                  <Download className="h-4 w-4 mr-2" />
                  {t('crud.actions.export')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{formatNumber(spendAnalysis.totalSpend, 0)} EUR</div>
                    <p className="text-sm text-muted-foreground">{t('crud.fields.totalSpend')}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{spendAnalysis.period}</div>
                    <p className="text-sm text-muted-foreground">{t('crud.fields.period')}</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-2xl font-bold">{spendByCategory.length}</div>
                    <p className="text-sm text-muted-foreground">{t('crud.fields.category')}</p>
                  </CardContent>
                </Card>
              </div>
              {spendByCategory.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">{t('crud.messages.noData')}</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.fields.category')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.amount')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.percentage')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {spendByCategory.map((item: any, idx: number) => (
                      <TableRow key={idx}>
                        <TableCell>{item.category || item.kategorie}</TableCell>
                        <TableCell className="text-right">{formatNumber(item.amount || item.betrag || 0, 0)} EUR</TableCell>
                        <TableCell className="text-right">{item.percentage || item.anteil || 0}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.fields.supplierPerformanceReport')}</CardTitle>
                <Button variant="outline" size="sm" onClick={() => handleExport('performance', supplierPerformance)} disabled={supplierPerformance.length === 0}>
                  <Download className="h-4 w-4 mr-2" />
                  {t('crud.actions.export')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {supplierPerformance.length === 0 ? (
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
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {supplierPerformance.map((supplier: any, idx: number) => (
                      <TableRow key={idx}>
                        <TableCell>{supplier.supplier}</TableCell>
                        <TableCell className="text-right">{supplier.onTimeDelivery || 0}%</TableCell>
                        <TableCell className="text-right">{supplier.qualityScore || 0}</TableCell>
                        <TableCell className="text-right">{supplier.priceScore || 0}</TableCell>
                        <TableCell className="text-right">{supplier.serviceScore || 0}</TableCell>
                        <TableCell className="text-right">{supplier.overallScore || 0}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tolerance">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{t('crud.fields.toleranceReports')}</CardTitle>
                <Button variant="outline" size="sm" onClick={() => handleExport('tolerance', toleranceReports)} disabled={toleranceReports.length === 0}>
                  <Download className="h-4 w-4 mr-2" />
                  {t('crud.actions.export')}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {toleranceReports.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">{t('crud.messages.noData')}</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('crud.fields.orderNumber')}</TableHead>
                      <TableHead>{t('crud.fields.type')}</TableHead>
                      <TableHead className="text-right">{t('crud.fields.deviation')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {toleranceReports.map((item: any, idx: number) => (
                      <TableRow key={idx}>
                        <TableCell><code className="text-sm">{item.purchaseOrderNumber || '-'}</code></TableCell>
                        <TableCell><Badge variant="outline">{item.type || '-'}</Badge></TableCell>
                        <TableCell className="text-right">
                          <span className={Number(item.deviation || 0) > 0 ? 'text-red-600' : 'text-green-600'}>
                            {Number(item.deviation || 0) > 0 ? '+' : ''}
                            {formatNumber(Number(item.deviation || 0), 2)}%
                          </span>
                        </TableCell>
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
