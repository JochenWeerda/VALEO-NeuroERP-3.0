import { useState, useEffect, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatCurrency } from '@/components/mask-builder/utils/formatting'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { 
  ArrowLeft, 
  RefreshCw, 
  TrendingUp, 
  DollarSign,
  Calendar,
  User,
  Download,
  Filter
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'

// API Client
const apiClient = createApiClient('/api/crm-sales')

interface ForecastData {
  period: string
  stage: string | null
  owner_id: string | null
  count: number
  total_amount: number
  total_expected_revenue: number
}

export default function OpportunitiesForecastPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [forecastData, setForecastData] = useState<ForecastData[]>([])
  const [loading, setLoading] = useState(true)
  const [filterPeriod, setFilterPeriod] = useState<string>('')
  const [filterOwner, setFilterOwner] = useState<string>('')
  const [filterStage, setFilterStage] = useState<string>('')
  const [viewMode, setViewMode] = useState<'period' | 'stage' | 'owner'>('period')
  const entityType = 'opportunity'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Opportunity')

  // Load forecast data
  useEffect(() => {
    loadForecastData()
  }, [filterPeriod, filterOwner, filterStage])

  const loadForecastData = async () => {
    setLoading(true)
    try {
      const params: any = {}
      if (filterPeriod) params.period = filterPeriod
      if (filterOwner) params.owner_id = filterOwner
      if (filterStage) params.stage = filterStage

      const response = await apiClient.get('/opportunities/forecast', { params })
      
      if (response.success) {
        setForecastData(response.data || [])
      }
    } catch (error) {
      console.error('Fehler beim Laden der Forecast-Daten:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError')
      })
    } finally {
      setLoading(false)
    }
  }

  // Prepare chart data based on view mode
  const chartData = useMemo(() => {
    if (viewMode === 'period') {
      // Group by period
      const grouped = forecastData.reduce((acc, item) => {
        const key = item.period
        if (!acc[key]) {
          acc[key] = {
            period: key,
            count: 0,
            total_amount: 0,
            total_expected_revenue: 0
          }
        }
        acc[key].count += item.count
        acc[key].total_amount += item.total_amount
        acc[key].total_expected_revenue += item.total_expected_revenue
        return acc
      }, {} as Record<string, any>)
      
      return Object.values(grouped).sort((a: any, b: any) => 
        a.period.localeCompare(b.period)
      )
    } else if (viewMode === 'stage') {
      // Group by stage
      const grouped = forecastData.reduce((acc, item) => {
        const key = item.stage || 'unknown'
        if (!acc[key]) {
          acc[key] = {
            stage: key,
            count: 0,
            total_amount: 0,
            total_expected_revenue: 0
          }
        }
        acc[key].count += item.count
        acc[key].total_amount += item.total_amount
        acc[key].total_expected_revenue += item.total_expected_revenue
        return acc
      }, {} as Record<string, any>)
      
      return Object.values(grouped)
    } else {
      // Group by owner
      const grouped = forecastData.reduce((acc, item) => {
        const key = item.owner_id || 'unassigned'
        if (!acc[key]) {
          acc[key] = {
            owner: key,
            count: 0,
            total_amount: 0,
            total_expected_revenue: 0
          }
        }
        acc[key].count += item.count
        acc[key].total_amount += item.total_amount
        acc[key].total_expected_revenue += item.total_expected_revenue
        return acc
      }, {} as Record<string, any>)
      
      return Object.values(grouped).sort((a: any, b: any) => 
        b.total_expected_revenue - a.total_expected_revenue
      )
    }
  }, [forecastData, viewMode])

  // Calculate totals
  const totals = useMemo(() => {
    return forecastData.reduce((acc, item) => ({
      count: acc.count + item.count,
      total_amount: acc.total_amount + item.total_amount,
      total_expected_revenue: acc.total_expected_revenue + item.total_expected_revenue
    }), { count: 0, total_amount: 0, total_expected_revenue: 0 })
  }, [forecastData])

  // Pie chart data for stage distribution
  const stageDistributionData = useMemo(() => {
    const grouped = forecastData.reduce((acc, item) => {
      const key = item.stage || 'unknown'
      if (!acc[key]) {
        acc[key] = { name: key, value: 0 }
      }
      acc[key].value += item.total_expected_revenue
      return acc
    }, {} as Record<string, any>)
    
    return Object.values(grouped).map((item: any) => ({
      ...item,
      name: item.name === 'unknown' 
        ? t('crud.forecast.unknown') 
        : getStatusLabel(t, item.name, item.name)
    }))
  }, [forecastData, t])

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#ff7300']

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.period')};${t('crud.fields.stage')};${t('crud.fields.owner')};${t('crud.fields.count')};${t('crud.fields.totalAmount')};${t('crud.fields.expectedRevenue')}\n`
      const csvContent = forecastData.map((item: any) =>
        `"${item.period || ''}";"${item.stage || ''}";"${item.owner_id || ''}";"${item.count}";"${item.total_amount}";"${item.total_expected_revenue}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `forecast-report-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: t('crud.messages.exportSuccess'),
        description: t('crud.messages.exportedItems', { count: forecastData.length, entityType: t('crud.forecast.report') }),
      })
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.exportError'),
      })
    }
  }

  // Generate period options (last 12 months)
  const periodOptions = useMemo(() => {
    const options = []
    const now = new Date()
    for (let i = 0; i < 12; i++) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
      const period = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      options.push({
        value: period,
        label: date.toLocaleDateString('de-DE', { year: 'numeric', month: 'long' })
      })
    }
    return options
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2" />
          <p>{t('crud.messages.loading')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={() => navigate('/crm/opportunities')} className="mb-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('crud.actions.back')}
          </Button>
          <h1 className="text-3xl font-bold">{t('crud.forecast.title', { entityType: entityTypeLabel })}</h1>
          <p className="text-muted-foreground">{t('crud.forecast.description')}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadForecastData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            {t('crud.actions.refresh')}
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            {t('crud.actions.export')}
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{t('crud.forecast.totalOpportunities')}</p>
                <p className="text-2xl font-bold">{totals.count}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{t('crud.forecast.totalAmount')}</p>
                <p className="text-2xl font-bold">{formatCurrency(totals.total_amount, 'EUR')}</p>
              </div>
              <DollarSign className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{t('crud.forecast.totalExpectedRevenue')}</p>
                <p className="text-2xl font-bold">{formatCurrency(totals.total_expected_revenue, 'EUR')}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{t('crud.forecast.avgDealSize')}</p>
                <p className="text-2xl font-bold">
                  {totals.count > 0 
                    ? formatCurrency(totals.total_amount / totals.count, 'EUR')
                    : formatCurrency(0, 'EUR')
                  }
                </p>
              </div>
              <DollarSign className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            {t('crud.actions.filter')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <Label>{t('crud.fields.period')}</Label>
              <Select value={filterPeriod} onValueChange={setFilterPeriod}>
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.forecast.allPeriods')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">{t('crud.forecast.allPeriods')}</SelectItem>
                  {periodOptions.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>{t('crud.fields.owner')}</Label>
              <Input
                placeholder={t('crud.tooltips.placeholders.owner')}
                value={filterOwner}
                onChange={(e) => setFilterOwner(e.target.value)}
              />
            </div>
            <div>
              <Label>{t('crud.fields.stage')}</Label>
              <Select value={filterStage} onValueChange={setFilterStage}>
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.forecast.allStages')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">{t('crud.forecast.allStages')}</SelectItem>
                  <SelectItem value="initial_contact">{t('crud.stages.initialContact')}</SelectItem>
                  <SelectItem value="needs_analysis">{t('crud.stages.needsAnalysis')}</SelectItem>
                  <SelectItem value="value_proposition">{t('crud.stages.valueProposition')}</SelectItem>
                  <SelectItem value="proposal_price_quote">{t('crud.stages.proposalPriceQuote')}</SelectItem>
                  <SelectItem value="negotiation_review">{t('crud.stages.negotiationReview')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>{t('crud.forecast.viewMode')}</Label>
              <Select value={viewMode} onValueChange={(value: any) => setViewMode(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="period">{t('crud.forecast.byPeriod')}</SelectItem>
                  <SelectItem value="stage">{t('crud.forecast.byStage')}</SelectItem>
                  <SelectItem value="owner">{t('crud.forecast.byOwner')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-4">
        {/* Expected Revenue Chart */}
        <Card>
          <CardHeader>
            <CardTitle>{t('crud.forecast.expectedRevenueChart')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              {viewMode === 'period' ? (
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey={viewMode === 'period' ? 'period' : viewMode === 'stage' ? 'stage' : 'owner'}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    formatter={(value: number) => formatCurrency(value, 'EUR')}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="total_expected_revenue" 
                    stroke="#0088FE" 
                    strokeWidth={2}
                    name={t('crud.fields.expectedRevenue')}
                  />
                </LineChart>
              ) : (
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey={viewMode === 'stage' ? 'stage' : 'owner'}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    formatter={(value: number) => formatCurrency(value, 'EUR')}
                  />
                  <Legend />
                  <Bar 
                    dataKey="total_expected_revenue" 
                    fill="#0088FE"
                    name={t('crud.fields.expectedRevenue')}
                  />
                </BarChart>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Total Amount Chart */}
        <Card>
          <CardHeader>
            <CardTitle>{t('crud.forecast.totalAmountChart')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              {viewMode === 'period' ? (
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="period"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    formatter={(value: number) => formatCurrency(value, 'EUR')}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="total_amount" 
                    stroke="#00C49F" 
                    strokeWidth={2}
                    name={t('crud.fields.totalAmount')}
                  />
                </LineChart>
              ) : (
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey={viewMode === 'stage' ? 'stage' : 'owner'}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    formatter={(value: number) => formatCurrency(value, 'EUR')}
                  />
                  <Legend />
                  <Bar 
                    dataKey="total_amount" 
                    fill="#00C49F"
                    name={t('crud.fields.totalAmount')}
                  />
                </BarChart>
              )}
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Stage Distribution Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>{t('crud.forecast.stageDistribution')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stageDistributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {stageDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => formatCurrency(value, 'EUR')} />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Opportunity Count Chart */}
        <Card>
          <CardHeader>
            <CardTitle>{t('crud.forecast.opportunityCountChart')}</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey={viewMode === 'period' ? 'period' : viewMode === 'stage' ? 'stage' : 'owner'}
                  tick={{ fontSize: 12 }}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Bar 
                  dataKey="count" 
                  fill="#FFBB28"
                  name={t('crud.forecast.opportunityCount')}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>{t('crud.forecast.detailedData')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('crud.fields.period')}
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('crud.fields.stage')}
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('crud.fields.owner')}
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('crud.fields.count')}
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('crud.fields.totalAmount')}
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('crud.fields.expectedRevenue')}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {forecastData.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground">
                      {t('crud.messages.noData')}
                    </td>
                  </tr>
                ) : (
                  forecastData.map((item, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        {item.period || '-'}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        {item.stage ? (
                          <Badge variant="outline">
                            {getStatusLabel(t, item.stage, item.stage)}
                          </Badge>
                        ) : '-'}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        {item.owner_id || '-'}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-right">
                        {item.count}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-medium">
                        {formatCurrency(item.total_amount, 'EUR')}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-medium">
                        {formatCurrency(item.total_expected_revenue, 'EUR')}
                      </td>
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


