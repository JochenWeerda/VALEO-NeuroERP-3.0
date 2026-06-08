import { Suspense, lazy, useEffect, useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { NativeSelect } from '@/components/ui/native-select'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { ArrowLeft, TrendingUp, Mail, Target, BarChart3, Info } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { formatDate, formatCurrency } from '@/components/mask-builder/utils/formatting'
import { toast } from '@/hooks/use-toast'
import { useTenant } from '@/hooks/useTenant'
import { DataTable } from '@/components/ui/data-table'

const CampaignPerformanceCharts = lazy(() =>
  import('@/pages/crm/charts/CampaignPerformanceCharts').then((module) => ({ default: module.default })),
)


interface CampaignSummary {
  id: string
  name: string
  type?: string
  sent_count?: number
  open_count?: number
  click_count?: number
  conversion_count?: number
  spent?: number
}

interface CampaignPerformancePoint {
  date: string
  sent_count?: number
  open_count?: number
  click_count?: number
  conversion_count?: number
}

export default function CampaignPerformanceDashboardPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { tenantId } = useTenant()
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('30d')
  const [campaigns, setCampaigns] = useState<CampaignSummary[]>([])
  const [performance, setPerformance] = useState<CampaignPerformancePoint[]>([])
  const [summary, setSummary] = useState<{
    totalCampaigns: number
    totalSent: number
    totalOpened: number
    totalClicked: number
    totalConverted: number
    totalSpent: number
    avgOpenRate: number
    avgClickRate: number
    avgConversionRate: number
  } | null>(null)

  useEffect(() => {
    void loadData()
  }, [timeRange])

  const loadData = async () => {
    setLoading(true)
    try {
      const [campaignsRes, performanceRes] = await Promise.all([
        apiClient.get<CampaignSummary[] | { items?: CampaignSummary[] }>('/api/v1/crm/campaigns', { params: { tenant_id: tenantId, state: 'completed' } }),
        apiClient.get<CampaignSummary[] | { items?: CampaignSummary[] }>('/api/v1/crm/campaigns', { params: { tenant_id: tenantId, state: 'active' } }),
      ])

      const items: CampaignSummary[] = Array.isArray(campaignsRes.data) ? campaignsRes.data : ((campaignsRes.data as { items?: CampaignSummary[] }).items ?? [])
      setCampaigns(items)

      const totalSent = items.reduce((sum, campaign) => sum + (campaign.sent_count || 0), 0)
      const totalOpened = items.reduce((sum, campaign) => sum + (campaign.open_count || 0), 0)
      const totalClicked = items.reduce((sum, campaign) => sum + (campaign.click_count || 0), 0)
      const totalConverted = items.reduce((sum, campaign) => sum + (campaign.conversion_count || 0), 0)
      const totalSpent = items.reduce((sum, campaign) => sum + (campaign.spent || 0), 0)

      setSummary({
        totalCampaigns: items.length,
        totalSent,
        totalOpened,
        totalClicked,
        totalConverted,
        totalSpent,
        avgOpenRate: totalSent > 0 ? (totalOpened / totalSent) * 100 : 0,
        avgClickRate: totalSent > 0 ? (totalClicked / totalSent) * 100 : 0,
        avgConversionRate: totalSent > 0 ? (totalConverted / totalSent) * 100 : 0,
      })

      const perfRaw = performanceRes.data as unknown
      const perfItems: CampaignPerformancePoint[] = Array.isArray(perfRaw) ? (perfRaw as CampaignPerformancePoint[]) : ((perfRaw as { items?: CampaignPerformancePoint[] }).items ?? [])
      setPerformance(perfItems)
    } catch {
      toast({ variant: 'destructive', title: t('crud.messages.loadError') })
    } finally {
      setLoading(false)
    }
  }

  const chartData = performance.map((perf) => ({
    date: formatDate(perf.date),
    sent: perf.sent_count || 0,
    opened: perf.open_count || 0,
    clicked: perf.click_count || 0,
    converted: perf.conversion_count || 0,
  }))

  const campaignChartData = campaigns.slice(0, 10).map((campaign) => ({
    name: campaign.name?.substring(0, 20) || '-',
    sent: campaign.sent_count || 0,
    opened: campaign.open_count || 0,
    clicked: campaign.click_count || 0,
    converted: campaign.conversion_count || 0,
  }))

  const typeDistribution = campaigns.reduce((acc, campaign) => {
    const type = campaign.type || 'unknown'
    acc[type] = (acc[type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const typeChartData = Object.entries(typeDistribution).map(([type, count]) => ({
    name: t(`crud.campaigns.types.${type}`) || type,
    value: Number(count),
  }))

  const topCampaigns = [...campaigns].sort((a, b) => (b.conversion_count || 0) - (a.conversion_count || 0)).slice(0, 5)
  const timeRangeOptions = [
    { value: '7d', label: t('crud.campaigns.timeRange.7d') },
    { value: '30d', label: t('crud.campaigns.timeRange.30d') },
    { value: '90d', label: t('crud.campaigns.timeRange.90d') },
    { value: '1y', label: t('crud.campaigns.timeRange.1y') },
  ]

  const campaignColumns = [
    {
      key: 'name' as const,
      label: t('crud.fields.name'),
      render: (campaign: any) => <Button variant="link" className="h-auto p-0" onClick={() => navigate(`/crm/campaign/${campaign.id}`)}>{campaign.name}</Button>,
    },
    {
      key: 'type' as const,
      label: t('crud.fields.type'),
      render: (campaign: any) => {
        const typeLabels: Record<string, string> = {
          email: t('crud.campaigns.types.email'),
          sms: t('crud.campaigns.types.sms'),
          push: t('crud.campaigns.types.push'),
          social: t('crud.campaigns.types.social'),
        }
        return <Badge variant="outline">{typeLabels[campaign.type] || campaign.type}</Badge>
      },
    },
    { key: 'sent_count' as const, label: t('crud.fields.sentCount'), render: (campaign: any) => (campaign.sent_count || 0).toLocaleString() },
    { key: 'open_rate' as const, label: t('crud.fields.openRate'), render: (campaign: any) => `${campaign.sent_count > 0 ? (((campaign.open_count || 0) / campaign.sent_count) * 100).toFixed(1) : '0.0'}%` },
    { key: 'click_rate' as const, label: t('crud.fields.clickRate'), render: (campaign: any) => `${campaign.sent_count > 0 ? (((campaign.click_count || 0) / campaign.sent_count) * 100).toFixed(1) : '0.0'}%` },
    { key: 'conversion_rate' as const, label: t('crud.fields.conversionRate'), render: (campaign: any) => `${campaign.sent_count > 0 ? (((campaign.conversion_count || 0) / campaign.sent_count) * 100).toFixed(1) : '0.0'}%` },
    { key: 'spent' as const, label: t('crud.fields.spent'), render: (campaign: any) => formatCurrency(campaign.spent || 0) },
  ]

  const hasData = campaigns.length > 0 || (summary && summary.totalCampaigns > 0)

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={() => navigate('/crm/campaigns')} className="mb-2">
            <ArrowLeft className="mr-2 h-4 w-4" />
            {t('crud.actions.back')}
          </Button>
          <h1 className="text-3xl font-bold">{t('crud.campaigns.performanceDashboard')}</h1>
          <p className="text-muted-foreground">{t('crud.campaigns.performanceDashboardDescription')}</p>
        </div>
        <div className="flex items-center gap-2">
          <NativeSelect className="w-40" value={timeRange} onValueChange={setTimeRange} options={timeRangeOptions} />
        </div>
      </div>

      {!loading && !hasData && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>{t('crud.campaigns.noDataTitle')}</AlertTitle>
          <AlertDescription>{t('crud.campaigns.noDataDescription')}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">{t('crud.campaigns.summary.totalCampaigns')}</CardTitle><BarChart3 className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent>{loading ? <Skeleton className="h-8 w-20" /> : <div className="text-2xl font-bold">{summary?.totalCampaigns || 0}</div>}</CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">{t('crud.fields.sentCount')}</CardTitle><Mail className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent>{loading ? <Skeleton className="h-8 w-24" /> : <div className="text-2xl font-bold">{(summary?.totalSent || 0).toLocaleString()}</div>}</CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">{t('crud.fields.avgOpenRate')}</CardTitle><TrendingUp className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent>{loading ? <Skeleton className="h-8 w-16" /> : <div className="text-2xl font-bold">{(summary?.avgOpenRate || 0).toFixed(1)}%</div>}</CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">{t('crud.fields.avgConversionRate')}</CardTitle><Target className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent>{loading ? <Skeleton className="h-8 w-16" /> : <div className="text-2xl font-bold">{(summary?.avgConversionRate || 0).toFixed(1)}%</div>}</CardContent></Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Suspense fallback={<><Card><CardContent className="p-6"><Skeleton className="h-[300px] w-full" /></CardContent></Card><Card><CardContent className="p-6"><Skeleton className="h-[300px] w-full" /></CardContent></Card><Card><CardContent className="p-6"><Skeleton className="h-[300px] w-full" /></CardContent></Card></>}>
          <CampaignPerformanceCharts loading={loading} chartData={chartData} campaignChartData={campaignChartData} typeChartData={typeChartData} />
        </Suspense>

        <Card>
          <CardHeader>
            <CardTitle>{t('crud.campaigns.summaryMetrics')}</CardTitle>
            <CardDescription>{t('crud.campaigns.summaryMetricsDescription')}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div><div className="text-sm text-muted-foreground">{t('crud.fields.totalOpened')}</div>{loading ? <Skeleton className="mt-1 h-8 w-20" /> : <div className="text-2xl font-bold">{(summary?.totalOpened || 0).toLocaleString()}</div>}</div>
              <div><div className="text-sm text-muted-foreground">{t('crud.fields.totalClicked')}</div>{loading ? <Skeleton className="mt-1 h-8 w-20" /> : <div className="text-2xl font-bold">{(summary?.totalClicked || 0).toLocaleString()}</div>}</div>
              <div><div className="text-sm text-muted-foreground">{t('crud.fields.totalConverted')}</div>{loading ? <Skeleton className="mt-1 h-8 w-20" /> : <div className="text-2xl font-bold">{(summary?.totalConverted || 0).toLocaleString()}</div>}</div>
              <div><div className="text-sm text-muted-foreground">{t('crud.fields.totalSpent')}</div>{loading ? <Skeleton className="mt-1 h-8 w-24" /> : <div className="text-2xl font-bold">{formatCurrency(summary?.totalSpent || 0)}</div>}</div>
            </div>
            <div className="border-t pt-4"><div className="mb-2 text-sm text-muted-foreground">{t('crud.fields.avgClickRate')}</div>{loading ? <Skeleton className="h-8 w-16" /> : <div className="text-2xl font-bold">{(summary?.avgClickRate || 0).toFixed(1)}%</div>}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>{t('crud.campaigns.topCampaigns')}</CardTitle><CardDescription>{t('crud.campaigns.topCampaignsDescription')}</CardDescription></CardHeader>
        <CardContent>
          {loading ? <div className="space-y-3">{[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</div> : topCampaigns.length > 0 ? <DataTable data={topCampaigns} columns={campaignColumns} /> : <div className="py-8 text-center text-muted-foreground"><Target className="mx-auto mb-2 h-12 w-12 opacity-50" /><p>{t('crud.campaigns.noTopCampaigns')}</p></div>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>{t('crud.campaigns.allCampaigns')}</CardTitle><CardDescription>{t('crud.campaigns.allCampaignsDescription')}</CardDescription></CardHeader>
        <CardContent>
          {loading ? <div className="space-y-3">{[...Array(10)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</div> : campaigns.length > 0 ? <DataTable data={campaigns} columns={campaignColumns} /> : <div className="py-8 text-center text-muted-foreground"><Mail className="mx-auto mb-2 h-12 w-12 opacity-50" /><p>{t('crud.campaigns.noCampaigns')}</p><Button variant="outline" className="mt-4" onClick={() => navigate('/crm/campaigns/new')}>{t('crud.campaigns.createFirst')}</Button></div>}
        </CardContent>
      </Card>
    </div>
  )
}
