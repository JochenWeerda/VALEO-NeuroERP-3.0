import { Suspense, lazy, useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatCurrency } from '@/components/mask-builder/utils/formatting'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { Label } from '@/components/ui/label'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { ArrowLeft, RefreshCw, TrendingUp, DollarSign, Download, Filter } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const OpportunitiesForecastCharts = lazy(() =>
  import('@/pages/crm/charts/OpportunitiesForecastCharts').then((module) => ({ default: module.default })),
)

const apiClient = createApiClient('/api/crm-sales')

interface ForecastData {
  period: string
  stage: string | null
  owner_id: string | null
  count: number
  total_amount: number
  total_expected_revenue: number
}

const CHART_COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#ff7300']

export default function OpportunitiesForecastPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [forecastData, setForecastData] = useState<ForecastData[]>([])
  const [loading, setLoading] = useState(true)
  const [filterPeriod, setFilterPeriod] = useState<string>('all')
  const [filterOwner, setFilterOwner] = useState<string>('')
  const [filterStage, setFilterStage] = useState<string>('all')
  const [viewMode, setViewMode] = useState<'period' | 'stage' | 'owner'>('period')
  const entityType = 'opportunity'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Opportunity')

  useEffect(() => {
    void loadForecastData()
  }, [filterPeriod, filterOwner, filterStage])

  const loadForecastData = async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (filterPeriod !== 'all') params.period = filterPeriod
      if (filterOwner) params.owner_id = filterOwner
      if (filterStage !== 'all') params.stage = filterStage

      const response = await apiClient.get('/opportunities/forecast', { params })
      if (response.success) {
        setForecastData(response.data || [])
      }
    } catch (error) {
      console.error('Fehler beim Laden der Forecast-Daten:', error)
      toast({ variant: 'destructive', title: t('crud.messages.loadError') })
    } finally {
      setLoading(false)
    }
  }

  const chartData = useMemo(() => {
    if (viewMode === 'period') {
      const grouped = forecastData.reduce((acc, item) => {
        const key = item.period
        if (!acc[key]) acc[key] = { period: key, count: 0, total_amount: 0, total_expected_revenue: 0 }
        acc[key].count += item.count
        acc[key].total_amount += item.total_amount
        acc[key].total_expected_revenue += item.total_expected_revenue
        return acc
      }, {} as Record<string, any>)
      return Object.values(grouped).sort((a: any, b: any) => a.period.localeCompare(b.period))
    }

    if (viewMode === 'stage') {
      const grouped = forecastData.reduce((acc, item) => {
        const key = item.stage || 'unknown'
        if (!acc[key]) acc[key] = { stage: key, count: 0, total_amount: 0, total_expected_revenue: 0 }
        acc[key].count += item.count
        acc[key].total_amount += item.total_amount
        acc[key].total_expected_revenue += item.total_expected_revenue
        return acc
      }, {} as Record<string, any>)
      return Object.values(grouped)
    }

    const grouped = forecastData.reduce((acc, item) => {
      const key = item.owner_id || 'unassigned'
      if (!acc[key]) acc[key] = { owner: key, count: 0, total_amount: 0, total_expected_revenue: 0 }
      acc[key].count += item.count
      acc[key].total_amount += item.total_amount
      acc[key].total_expected_revenue += item.total_expected_revenue
      return acc
    }, {} as Record<string, any>)
    return Object.values(grouped).sort((a: any, b: any) => b.total_expected_revenue - a.total_expected_revenue)
  }, [forecastData, viewMode])

  const totals = useMemo(() => {
    return forecastData.reduce(
      (acc, item) => ({
        count: acc.count + item.count,
        total_amount: acc.total_amount + item.total_amount,
        total_expected_revenue: acc.total_expected_revenue + item.total_expected_revenue,
      }),
      { count: 0, total_amount: 0, total_expected_revenue: 0 },
    )
  }, [forecastData])

  const stageDistributionData = useMemo(() => {
    const grouped = forecastData.reduce((acc, item) => {
      const key = item.stage || 'unknown'
      if (!acc[key]) acc[key] = { name: key, value: 0 }
      acc[key].value += item.total_expected_revenue
      return acc
    }, {} as Record<string, any>)

    return Object.values(grouped).map((item: any) => ({
      ...item,
      name: item.name === 'unknown' ? t('crud.forecast.unknown') : getStatusLabel(t, item.name, item.name),
    }))
  }, [forecastData, t])

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.period')};${t('crud.fields.stage')};${t('crud.fields.owner')};${t('crud.fields.count')};${t('crud.fields.totalAmount')};${t('crud.fields.expectedRevenue')}\n`
      const csvContent = forecastData.map((item) => `"${item.period || ''}";"${item.stage || ''}";"${item.owner_id || ''}";"${item.count}";"${item.total_amount}";"${item.total_expected_revenue}"`).join('\n')
      const blob = new Blob([csvHeader + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `forecast-report-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      toast({ title: t('crud.messages.exportSuccess'), description: t('crud.messages.exportedItems', { count: forecastData.length, entityType: t('crud.forecast.report') }) })
    } catch {
      toast({ variant: 'destructive', title: t('crud.messages.exportError') })
    }
  }

  const periodOptions = useMemo(() => {
    const options = []
    const now = new Date()
    for (let i = 0; i < 12; i += 1) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
      const period = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      options.push({ value: period, label: date.toLocaleDateString('de-DE', { year: 'numeric', month: 'long' }) })
    }
    return options
  }, [])
  const filterPeriodOptions = [{ value: 'all', label: t('crud.forecast.allPeriods') }, ...periodOptions]
  const filterStageOptions = [
    { value: 'all', label: t('crud.forecast.allStages') },
    { value: 'initial_contact', label: t('crud.stages.initialContact') },
    { value: 'needs_analysis', label: t('crud.stages.needsAnalysis') },
    { value: 'value_proposition', label: t('crud.stages.valueProposition') },
    { value: 'proposal_price_quote', label: t('crud.stages.proposalPriceQuote') },
    { value: 'negotiation_review', label: t('crud.stages.negotiationReview') },
  ]
  const viewModeOptions = [
    { value: 'period', label: t('crud.forecast.byPeriod') },
    { value: 'stage', label: t('crud.forecast.byStage') },
    { value: 'owner', label: t('crud.forecast.byOwner') },
  ]

  if (loading) {
    return <div className="flex items-center justify-center p-8"><div className="text-center"><RefreshCw className="mx-auto mb-2 h-8 w-8 animate-spin" /><p>{t('crud.messages.loading')}</p></div></div>
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={() => navigate('/crm/opportunities')} className="mb-2"><ArrowLeft className="mr-2 h-4 w-4" />{t('crud.actions.back')}</Button>
          <h1 className="text-3xl font-bold">{t('crud.forecast.title', { entityType: entityTypeLabel })}</h1>
          <p className="text-muted-foreground">{t('crud.forecast.description')}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => void loadForecastData()}><RefreshCw className="mr-2 h-4 w-4" />{t('crud.actions.refresh')}</Button>
          <Button variant="outline" onClick={handleExport}><Download className="mr-2 h-4 w-4" />{t('crud.actions.export')}</Button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <Card><CardContent className="pt-4"><div className="flex items-center justify-between"><div><p className="text-sm text-muted-foreground">{t('crud.forecast.totalOpportunities')}</p><p className="text-2xl font-bold">{totals.count}</p></div><TrendingUp className="h-8 w-8 text-muted-foreground" /></div></CardContent></Card>
        <Card><CardContent className="pt-4"><div className="flex items-center justify-between"><div><p className="text-sm text-muted-foreground">{t('crud.forecast.totalAmount')}</p><p className="text-2xl font-bold">{formatCurrency(totals.total_amount, 'EUR')}</p></div><DollarSign className="h-8 w-8 text-muted-foreground" /></div></CardContent></Card>
        <Card><CardContent className="pt-4"><div className="flex items-center justify-between"><div><p className="text-sm text-muted-foreground">{t('crud.forecast.totalExpectedRevenue')}</p><p className="text-2xl font-bold">{formatCurrency(totals.total_expected_revenue, 'EUR')}</p></div><TrendingUp className="h-8 w-8 text-muted-foreground" /></div></CardContent></Card>
        <Card><CardContent className="pt-4"><div className="flex items-center justify-between"><div><p className="text-sm text-muted-foreground">{t('crud.forecast.avgDealSize')}</p><p className="text-2xl font-bold">{totals.count > 0 ? formatCurrency(totals.total_amount / totals.count, 'EUR') : formatCurrency(0, 'EUR')}</p></div><DollarSign className="h-8 w-8 text-muted-foreground" /></div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Filter className="h-5 w-5" />{t('crud.actions.filter')}</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <Label>{t('crud.fields.period')}</Label>
              <NativeSelect value={filterPeriod} onValueChange={setFilterPeriod} options={filterPeriodOptions} placeholder={t('crud.forecast.allPeriods')} />
            </div>
            <div>
              <Label>{t('crud.fields.owner')}</Label>
              <Input placeholder={t('crud.tooltips.placeholders.owner')} value={filterOwner} onChange={(e) => setFilterOwner(e.target.value)} />
            </div>
            <div>
              <Label>{t('crud.fields.stage')}</Label>
              <NativeSelect value={filterStage} onValueChange={setFilterStage} options={filterStageOptions} placeholder={t('crud.forecast.allStages')} />
            </div>
            <div>
              <Label>{t('crud.forecast.viewMode')}</Label>
              <NativeSelect value={viewMode} onValueChange={(value) => setViewMode(value as 'period' | 'stage' | 'owner')} options={viewModeOptions} />
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-4">
        <Suspense fallback={<><Card><CardContent className="p-6"><div className="h-[300px] animate-pulse rounded bg-muted" /></CardContent></Card><Card><CardContent className="p-6"><div className="h-[300px] animate-pulse rounded bg-muted" /></CardContent></Card><Card><CardContent className="p-6"><div className="h-[300px] animate-pulse rounded bg-muted" /></CardContent></Card><Card><CardContent className="p-6"><div className="h-[300px] animate-pulse rounded bg-muted" /></CardContent></Card></>}>
          <OpportunitiesForecastCharts chartData={chartData} stageDistributionData={stageDistributionData} viewMode={viewMode} colors={CHART_COLORS} />
        </Suspense>
      </div>

      <Card>
        <CardHeader><CardTitle>{t('crud.forecast.detailedData')}</CardTitle></CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50"><tr><th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">{t('crud.fields.period')}</th><th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">{t('crud.fields.stage')}</th><th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">{t('crud.fields.owner')}</th><th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">{t('crud.fields.count')}</th><th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">{t('crud.fields.totalAmount')}</th><th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">{t('crud.fields.expectedRevenue')}</th></tr></thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {forecastData.length === 0 ? (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">{t('crud.messages.noData')}</td></tr>
                ) : (
                  forecastData.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="whitespace-nowrap px-4 py-3 text-sm">{item.period || '-'}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm">{item.stage ? <Badge variant="outline">{getStatusLabel(t, item.stage, item.stage)}</Badge> : '-'}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-sm">{item.owner_id || '-'}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-right text-sm">{item.count}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-right text-sm font-medium">{formatCurrency(item.total_amount, 'EUR')}</td>
                      <td className="whitespace-nowrap px-4 py-3 text-right text-sm font-medium">{formatCurrency(item.total_expected_revenue, 'EUR')}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
