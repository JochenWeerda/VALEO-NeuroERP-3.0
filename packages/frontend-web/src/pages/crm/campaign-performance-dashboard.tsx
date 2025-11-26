import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ArrowLeft, TrendingUp, TrendingDown, Mail, MousePointerClick, Target, BarChart3, Users, Calendar } from 'lucide-react'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatCurrency } from '@/components/mask-builder/utils/formatting'
import { toast } from '@/hooks/use-toast'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { DataTable } from '@/components/ui/data-table'

// API Client
const apiClient = createApiClient('/api/crm-marketing')

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']

export default function CampaignPerformanceDashboardPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('30d')
  const [campaigns, setCampaigns] = useState<any[]>([])
  const [performance, setPerformance] = useState<any[]>([])
  const [summary, setSummary] = useState<any>(null)

  useEffect(() => {
    loadData()
  }, [timeRange])

  const loadData = async () => {
    setLoading(true)
    try {
      const [campaignsRes, performanceRes] = await Promise.all([
        apiClient.get('/campaigns', {
          params: {
            tenant_id: '00000000-0000-0000-0000-000000000001',
            status: 'completed'
          }
        }),
        apiClient.get('/campaigns/performance', {
          params: {
            tenant_id: '00000000-0000-0000-0000-000000000001',
            time_range: timeRange
          }
        })
      ])

      if (campaignsRes.success || Array.isArray(campaignsRes)) {
        const items = Array.isArray(campaignsRes) ? campaignsRes : (campaignsRes.data || [])
        setCampaigns(items)
        
        // Calculate summary
        const totalSent = items.reduce((sum, c) => sum + (c.sent_count || 0), 0)
        const totalOpened = items.reduce((sum, c) => sum + (c.open_count || 0), 0)
        const totalClicked = items.reduce((sum, c) => sum + (c.click_count || 0), 0)
        const totalConverted = items.reduce((sum, c) => sum + (c.conversion_count || 0), 0)
        const totalSpent = items.reduce((sum, c) => sum + (c.spent || 0), 0)
        
        setSummary({
          totalCampaigns: items.length,
          totalSent,
          totalOpened,
          totalClicked,
          totalConverted,
          totalSpent,
          avgOpenRate: totalSent > 0 ? (totalOpened / totalSent * 100) : 0,
          avgClickRate: totalSent > 0 ? (totalClicked / totalSent * 100) : 0,
          avgConversionRate: totalSent > 0 ? (totalConverted / totalSent * 100) : 0
        })
      }

      if (performanceRes.success || Array.isArray(performanceRes)) {
        const perf = Array.isArray(performanceRes) ? performanceRes : (performanceRes.data || [])
        setPerformance(perf)
      }
    } catch (error) {
      console.error('Fehler beim Laden der Performance-Daten:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError')
      })
    } finally {
      setLoading(false)
    }
  }

  const chartData = performance.map((perf) => ({
    date: formatDate(perf.date),
    sent: perf.sent_count || 0,
    opened: perf.open_count || 0,
    clicked: perf.click_count || 0,
    converted: perf.conversion_count || 0
  }))

  const campaignChartData = campaigns.slice(0, 10).map((campaign) => ({
    name: campaign.name?.substring(0, 20) || '-',
    sent: campaign.sent_count || 0,
    opened: campaign.open_count || 0,
    clicked: campaign.click_count || 0,
    converted: campaign.conversion_count || 0
  }))

  const typeDistribution = campaigns.reduce((acc, campaign) => {
    const type = campaign.type || 'unknown'
    acc[type] = (acc[type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const typeChartData = Object.entries(typeDistribution).map(([type, count]) => ({
    name: t(`crud.campaigns.types.${type}`) || type,
    value: count
  }))

  const topCampaigns = [...campaigns]
    .sort((a, b) => (b.conversion_count || 0) - (a.conversion_count || 0))
    .slice(0, 5)

  const campaignColumns = [
    {
      key: 'name' as const,
      label: t('crud.fields.name'),
      render: (campaign: any) => (
        <Button
          variant="link"
          className="p-0 h-auto"
          onClick={() => navigate(`/crm/campaign/${campaign.id}`)}
        >
          {campaign.name}
        </Button>
      )
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
      }
    },
    {
      key: 'sent_count' as const,
      label: t('crud.fields.sentCount'),
      render: (campaign: any) => (campaign.sent_count || 0).toLocaleString()
    },
    {
      key: 'open_rate' as const,
      label: t('crud.fields.openRate'),
      render: (campaign: any) => {
        const rate = campaign.sent_count > 0 
          ? ((campaign.open_count || 0) / campaign.sent_count * 100).toFixed(1)
          : '0.0'
        return `${rate}%`
      }
    },
    {
      key: 'click_rate' as const,
      label: t('crud.fields.clickRate'),
      render: (campaign: any) => {
        const rate = campaign.sent_count > 0 
          ? ((campaign.click_count || 0) / campaign.sent_count * 100).toFixed(1)
          : '0.0'
        return `${rate}%`
      }
    },
    {
      key: 'conversion_rate' as const,
      label: t('crud.fields.conversionRate'),
      render: (campaign: any) => {
        const rate = campaign.sent_count > 0 
          ? ((campaign.conversion_count || 0) / campaign.sent_count * 100).toFixed(1)
          : '0.0'
        return `${rate}%`
      }
    },
    {
      key: 'spent' as const,
      label: t('crud.fields.spent'),
      render: (campaign: any) => formatCurrency(campaign.spent || 0)
    }
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <p>{t('crud.messages.loading')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={() => navigate('/crm/campaigns')} className="mb-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('crud.actions.back')}
          </Button>
          <h1 className="text-3xl font-bold">{t('crud.campaigns.performanceDashboard')}</h1>
          <p className="text-muted-foreground">{t('crud.campaigns.performanceDashboardDescription')}</p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">{t('crud.campaigns.timeRange.7d')}</SelectItem>
              <SelectItem value="30d">{t('crud.campaigns.timeRange.30d')}</SelectItem>
              <SelectItem value="90d">{t('crud.campaigns.timeRange.90d')}</SelectItem>
              <SelectItem value="1y">{t('crud.campaigns.timeRange.1y')}</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('crud.campaigns.summary.totalCampaigns')}</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.totalCampaigns}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('crud.fields.sentCount')}</CardTitle>
              <Mail className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.totalSent.toLocaleString()}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('crud.fields.avgOpenRate')}</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.avgOpenRate.toFixed(1)}%</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('crud.fields.avgConversionRate')}</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.avgConversionRate.toFixed(1)}%</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {chartData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>{t('crud.campaigns.performanceChart')}</CardTitle>
              <CardDescription>{t('crud.campaigns.performanceChartDescription')}</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="sent" stroke="#8884d8" name={t('crud.fields.sentCount')} />
                  <Line type="monotone" dataKey="opened" stroke="#82ca9d" name={t('crud.fields.openCount')} />
                  <Line type="monotone" dataKey="clicked" stroke="#ffc658" name={t('crud.fields.clickCount')} />
                  <Line type="monotone" dataKey="converted" stroke="#ff7300" name={t('crud.fields.conversionCount')} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {campaignChartData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>{t('crud.campaigns.campaignComparison')}</CardTitle>
              <CardDescription>{t('crud.campaigns.campaignComparisonDescription')}</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={campaignChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="sent" fill="#8884d8" name={t('crud.fields.sentCount')} />
                  <Bar dataKey="opened" fill="#82ca9d" name={t('crud.fields.openCount')} />
                  <Bar dataKey="clicked" fill="#ffc658" name={t('crud.fields.clickCount')} />
                  <Bar dataKey="converted" fill="#ff7300" name={t('crud.fields.conversionCount')} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {typeChartData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>{t('crud.campaigns.typeDistribution')}</CardTitle>
              <CardDescription>{t('crud.campaigns.typeDistributionDescription')}</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={typeChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {typeChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {summary && (
          <Card>
            <CardHeader>
              <CardTitle>{t('crud.campaigns.summaryMetrics')}</CardTitle>
              <CardDescription>{t('crud.campaigns.summaryMetricsDescription')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">{t('crud.fields.totalOpened')}</div>
                  <div className="text-2xl font-bold">{summary.totalOpened.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">{t('crud.fields.totalClicked')}</div>
                  <div className="text-2xl font-bold">{summary.totalClicked.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">{t('crud.fields.totalConverted')}</div>
                  <div className="text-2xl font-bold">{summary.totalConverted.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">{t('crud.fields.totalSpent')}</div>
                  <div className="text-2xl font-bold">{formatCurrency(summary.totalSpent)}</div>
                </div>
              </div>
              <div className="pt-4 border-t">
                <div className="text-sm text-muted-foreground mb-2">{t('crud.fields.avgClickRate')}</div>
                <div className="text-2xl font-bold">{summary.avgClickRate.toFixed(1)}%</div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Top Campaigns */}
      {topCampaigns.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{t('crud.campaigns.topCampaigns')}</CardTitle>
            <CardDescription>{t('crud.campaigns.topCampaignsDescription')}</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable
              data={topCampaigns}
              columns={campaignColumns}
            />
          </CardContent>
        </Card>
      )}

      {/* All Campaigns */}
      {campaigns.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{t('crud.campaigns.allCampaigns')}</CardTitle>
            <CardDescription>{t('crud.campaigns.allCampaignsDescription')}</CardDescription>
          </CardHeader>
          <CardContent>
            <DataTable
              data={campaigns}
              columns={campaignColumns}
            />
          </CardContent>
        </Card>
      )}
    </div>
  )
}

