import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatCurrency } from '@/components/mask-builder/utils/formatting'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { 
  ArrowLeft, 
  Filter, 
  RefreshCw, 
  TrendingUp, 
  DollarSign,
  Calendar,
  User,
  Target
} from 'lucide-react'

// API Client
const apiClient = createApiClient('/api/crm-sales')

interface Opportunity {
  id: string
  number: string
  name: string
  amount: number | null
  currency: string
  probability: number | null
  expected_revenue: number | null
  expected_close_date: string | null
  stage: string
  status: string
  customer_id: string | null
  owner_id: string | null
  assigned_to: string | null
}

interface StageColumn {
  key: string
  label: string
  opportunities: Opportunity[]
  totalAmount: number
  totalExpectedRevenue: number
  count: number
}

export default function OpportunitiesKanbanPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [stages, setStages] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filterOwner, setFilterOwner] = useState<string>('')
  const [filterStatus, setFilterStatus] = useState<string>('')
  const [draggedOpportunity, setDraggedOpportunity] = useState<Opportunity | null>(null)
  const entityType = 'opportunity'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Opportunity')

  // Load opportunities and stages
  useEffect(() => {
    loadData()
  }, [filterOwner, filterStatus])

  const loadData = async () => {
    setLoading(true)
    try {
      // Load opportunities
      const oppsResponse = await apiClient.get('/opportunities', {
        params: {
          ...(filterOwner && { owner_id: filterOwner }),
          ...(filterStatus && { status: filterStatus })
        }
      })
      
      if (oppsResponse.success) {
        const data = oppsResponse.data as any
        setOpportunities((data.items || data) as Opportunity[])
      }

      // Load stages
      const stagesResponse = await apiClient.get('/opportunities/stages')
      if (stagesResponse.success) {
        setStages(stagesResponse.data || [])
      }
    } catch (error) {
      console.error('Fehler beim Laden der Daten:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.loadError')
      })
    } finally {
      setLoading(false)
    }
  }

  // Group opportunities by stage
  const stageColumns = useMemo(() => {
    const columns: StageColumn[] = []
    
    // Get default stages if API stages not loaded yet
    const defaultStages = [
      { stage_key: 'initial_contact', name: t('crud.stages.initialContact'), order: 1 },
      { stage_key: 'needs_analysis', name: t('crud.stages.needsAnalysis'), order: 2 },
      { stage_key: 'value_proposition', name: t('crud.stages.valueProposition'), order: 3 },
      { stage_key: 'identify_decision_makers', name: t('crud.stages.identifyDecisionMakers'), order: 4 },
      { stage_key: 'proposal_price_quote', name: t('crud.stages.proposalPriceQuote'), order: 5 },
      { stage_key: 'negotiation_review', name: t('crud.stages.negotiationReview'), order: 6 },
      { stage_key: 'closed_won', name: t('crud.stages.closedWon'), order: 7 },
      { stage_key: 'closed_lost', name: t('crud.stages.closedLost'), order: 8 }
    ]
    
    const stagesToUse = stages.length > 0 ? stages : defaultStages
    
    stagesToUse
      .sort((a, b) => (a.order || 0) - (b.order || 0))
      .forEach((stage) => {
        const stageKey = stage.stage_key || stage.key || stage
        const stageOpps = opportunities.filter(opp => opp.stage === stageKey)
        
        const totalAmount = stageOpps.reduce((sum, opp) => sum + (opp.amount || 0), 0)
        const totalExpectedRevenue = stageOpps.reduce((sum, opp) => sum + (opp.expected_revenue || 0), 0)
        
        columns.push({
          key: stageKey,
          label: stage.name || stage.label || getStatusLabel(t, stageKey, stageKey),
          opportunities: stageOpps,
          totalAmount,
          totalExpectedRevenue,
          count: stageOpps.length
        })
      })
    
    return columns
  }, [opportunities, stages, t])

  // Handle drag start
  const handleDragStart = (e: React.DragEvent, opportunity: Opportunity) => {
    setDraggedOpportunity(opportunity)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', opportunity.id)
  }

  // Handle drag over
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  // Handle drop
  const handleDrop = async (e: React.DragEvent, targetStage: string) => {
    e.preventDefault()
    
    if (!draggedOpportunity) return
    
    // Don't update if dropped on same stage
    if (draggedOpportunity.stage === targetStage) {
      setDraggedOpportunity(null)
      return
    }

    try {
      // Optimistic update
      const updatedOpportunities = opportunities.map(opp =>
        opp.id === draggedOpportunity.id
          ? { ...opp, stage: targetStage }
          : opp
      )
      setOpportunities(updatedOpportunities)

      // Update via API
      await apiClient.put(`/opportunities/${draggedOpportunity.id}`, {
        stage: targetStage
      }, {
        params: {
          changed_by: 'current_user' // TODO: Get from auth context
        }
      })

      toast({
        title: t('crud.messages.updateSuccess', { entityType: entityTypeLabel }),
        description: t('crud.messages.stageChanged', { 
          stage: getStatusLabel(t, targetStage, targetStage)
        })
      })

      // Reload to get fresh data
      await loadData()
    } catch (error) {
      // Revert on error
      setOpportunities(opportunities)
      toast({
        variant: 'destructive',
        title: t('crud.messages.updateError', { entityType: entityTypeLabel })
      })
    } finally {
      setDraggedOpportunity(null)
    }
  }

  // Handle drag end
  const handleDragEnd = () => {
    setDraggedOpportunity(null)
  }

  // Get status badge variant
  const getStatusVariant = (status: string): 'secondary' | 'default' | 'outline' | 'destructive' => {
    const variants: Record<string, 'secondary' | 'default' | 'outline' | 'destructive'> = {
      'prospecting': 'secondary',
      'qualification': 'default',
      'proposal': 'outline',
      'negotiation': 'outline',
      'closed_won': 'default',
      'closed_lost': 'destructive'
    }
    return variants[status] || 'secondary'
  }

  // Calculate totals
  const totalAmount = opportunities.reduce((sum, opp) => sum + (opp.amount || 0), 0)
  const totalExpectedRevenue = opportunities.reduce((sum, opp) => sum + (opp.expected_revenue || 0), 0)
  const totalCount = opportunities.length

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
          <h1 className="text-3xl font-bold">{t('crud.kanban.pipeline', { entityType: entityTypeLabel })}</h1>
          <p className="text-muted-foreground">{t('crud.kanban.description')}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={loadData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            {t('crud.actions.refresh')}
          </Button>
          <Button onClick={() => navigate('/crm/opportunity/new')}>
            {t('crud.actions.create', { entityType: entityTypeLabel })}
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{t('crud.kanban.totalOpportunities')}</p>
                <p className="text-2xl font-bold">{totalCount}</p>
              </div>
              <Target className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{t('crud.kanban.totalAmount')}</p>
                <p className="text-2xl font-bold">{formatCurrency(totalAmount, 'EUR')}</p>
              </div>
              <DollarSign className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{t('crud.kanban.totalExpectedRevenue')}</p>
                <p className="text-2xl font-bold">{formatCurrency(totalExpectedRevenue, 'EUR')}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{t('crud.kanban.avgProbability')}</p>
                <p className="text-2xl font-bold">
                  {opportunities.length > 0
                    ? `${Math.round(
                        opportunities.reduce((sum, opp) => sum + (opp.probability || 0), 0) /
                          opportunities.length
                      )}%`
                    : '0%'}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-muted-foreground" />
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
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">{t('crud.fields.owner')}</label>
              <Input
                placeholder={t('crud.tooltips.placeholders.owner')}
                value={filterOwner}
                onChange={(e) => setFilterOwner(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">{t('crud.fields.status')}</label>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.actions.filter')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">{t('common.all')}</SelectItem>
                  <SelectItem value="prospecting">{t('status.prospecting')}</SelectItem>
                  <SelectItem value="qualification">{t('status.qualification')}</SelectItem>
                  <SelectItem value="proposal">{t('status.proposal')}</SelectItem>
                  <SelectItem value="negotiation">{t('status.negotiation')}</SelectItem>
                  <SelectItem value="closed_won">{t('status.closedWon')}</SelectItem>
                  <SelectItem value="closed_lost">{t('status.closedLost')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Kanban Board */}
      <div className="flex gap-4 overflow-x-auto pb-4" style={{ minHeight: '600px' }}>
        {stageColumns.map((column) => (
          <div
            key={column.key}
            className="flex-shrink-0 w-80"
            onDragOver={handleDragOver}
            onDrop={(e) => handleDrop(e, column.key)}
          >
            <Card className="h-full">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center justify-between">
                  <span>{column.label}</span>
                  <Badge variant="outline">{column.count}</Badge>
                </CardTitle>
                <div className="text-sm text-muted-foreground space-y-1 mt-2">
                  <div className="flex items-center justify-between">
                    <span>{t('crud.fields.amount')}:</span>
                    <span className="font-medium">{formatCurrency(column.totalAmount, 'EUR')}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>{t('crud.fields.expectedRevenue')}:</span>
                    <span className="font-medium">{formatCurrency(column.totalExpectedRevenue, 'EUR')}</span>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-2 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 400px)' }}>
                {column.opportunities.map((opportunity) => (
                  <Card
                    key={opportunity.id}
                    className="cursor-move hover:shadow-md transition-shadow"
                    draggable
                    onDragStart={(e) => handleDragStart(e, opportunity)}
                    onDragEnd={handleDragEnd}
                    onClick={() => navigate(`/crm/opportunity/${opportunity.id}`)}
                  >
                    <CardContent className="pt-4">
                      <div className="space-y-2">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-medium text-sm">{opportunity.name}</p>
                            <p className="text-xs text-muted-foreground font-mono">{opportunity.number}</p>
                          </div>
                          <Badge variant={getStatusVariant(opportunity.status)} className="text-xs">
                            {getStatusLabel(t, opportunity.status, opportunity.status)}
                          </Badge>
                        </div>
                        
                        {opportunity.amount && (
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">{t('crud.fields.amount')}:</span>
                            <span className="font-medium">
                              {formatCurrency(opportunity.amount, opportunity.currency || 'EUR')}
                            </span>
                          </div>
                        )}
                        
                        {opportunity.probability !== null && (
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-muted-foreground">{t('crud.fields.probability')}:</span>
                            <span className="font-medium">{opportunity.probability}%</span>
                          </div>
                        )}
                        
                        {opportunity.expected_close_date && (
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Calendar className="h-3 w-3" />
                            {formatDate(opportunity.expected_close_date)}
                          </div>
                        )}
                        
                        {opportunity.owner_id && (
                          <div className="flex items-center gap-1 text-xs text-muted-foreground">
                            <User className="h-3 w-3" />
                            {opportunity.owner_id}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
                
                {column.opportunities.length === 0 && (
                  <div className="text-center text-muted-foreground py-8 text-sm">
                    {t('crud.kanban.noOpportunitiesInStage')}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        ))}
      </div>
    </div>
  )
}

