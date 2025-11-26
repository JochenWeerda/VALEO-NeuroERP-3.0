import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatDate, formatCurrency } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'

// API Client für Opportunities
const apiClient = createApiClient('/api/crm-sales')

// Konfiguration für Opportunities ListReport (wird in Komponente mit i18n erstellt)
const createOpportunitiesConfig = (t: any, entityTypeLabel: string): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.manageOpportunities'),
  subtitleKey: 'crud.subtitles.manageOpportunities',
  type: 'list-report',
  columns: [
    {
      key: 'number',
      label: t('crud.fields.number'),
      labelKey: 'crud.fields.number',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'name',
      label: t('crud.fields.name'),
      labelKey: 'crud.fields.name',
      sortable: true,
      filterable: true
    },
    {
      key: 'customer_id',
      label: t('crud.entities.customer'),
      labelKey: 'crud.entities.customer',
      sortable: true,
      filterable: true,
      render: (value, item) => {
        // TODO: Load customer name from API
        return value ? <span>{value}</span> : '-'
      }
    },
    {
      key: 'stage',
      label: t('crud.fields.stage'),
      labelKey: 'crud.fields.stage',
      sortable: true,
      filterable: true,
      render: (value) => {
        const stageLabel = getStatusLabel(t, value as string, value as string)
        return <Badge variant="outline">{stageLabel}</Badge>
      }
    },
    {
      key: 'amount',
      label: t('crud.fields.amount'),
      labelKey: 'crud.fields.amount',
      sortable: true,
      render: (value, item) => {
        if (!value) return '-'
        const currency = item.currency || 'EUR'
        return formatCurrency(value, currency)
      }
    },
    {
      key: 'probability',
      label: t('crud.fields.probability'),
      labelKey: 'crud.fields.probability',
      sortable: true,
      render: (value) => value ? `${value}%` : '-'
    },
    {
      key: 'expected_revenue',
      label: t('crud.fields.expectedRevenue'),
      labelKey: 'crud.fields.expectedRevenue',
      sortable: true,
      render: (value, item) => {
        if (!value) return '-'
        const currency = item.currency || 'EUR'
        return formatCurrency(value, currency)
      }
    },
    {
      key: 'expected_close_date',
      label: t('crud.fields.expectedCloseDate'),
      labelKey: 'crud.fields.expectedCloseDate',
      sortable: true,
      render: (value) => value ? formatDate(value) : '-'
    },
    {
      key: 'owner_id',
      label: t('crud.fields.owner'),
      labelKey: 'crud.fields.owner',
      sortable: true,
      filterable: true,
      render: (value) => value || '-'
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabel = getStatusLabel(t, value as string, value as string)
        const variants: Record<string, 'secondary' | 'default' | 'outline' | 'destructive'> = {
          'prospecting': 'secondary',
          'qualification': 'default',
          'proposal': 'outline',
          'negotiation': 'outline',
          'closed_won': 'default',
          'closed_lost': 'destructive'
        }
        return <Badge variant={variants[value as string] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'created_at',
      label: t('crud.fields.createdAt'),
      labelKey: 'crud.fields.createdAt',
      sortable: true,
      render: (value) => formatDate(value)
    }
  ],
  filters: [
    {
      name: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      type: 'select',
      options: [
        { value: 'prospecting', label: t('status.prospecting'), labelKey: 'status.prospecting' },
        { value: 'qualification', label: t('status.qualification'), labelKey: 'status.qualification' },
        { value: 'proposal', label: t('status.proposal'), labelKey: 'status.proposal' },
        { value: 'negotiation', label: t('status.negotiation'), labelKey: 'status.negotiation' },
        { value: 'closed_won', label: t('status.closedWon'), labelKey: 'status.closedWon' },
        { value: 'closed_lost', label: t('status.closedLost'), labelKey: 'status.closedLost' }
      ]
    },
    {
      name: 'stage',
      label: t('crud.fields.stage'),
      labelKey: 'crud.fields.stage',
      type: 'select',
      options: [
        { value: 'initial_contact', label: t('crud.stages.initialContact'), labelKey: 'crud.stages.initialContact' },
        { value: 'needs_analysis', label: t('crud.stages.needsAnalysis'), labelKey: 'crud.stages.needsAnalysis' },
        { value: 'value_proposition', label: t('crud.stages.valueProposition'), labelKey: 'crud.stages.valueProposition' },
        { value: 'proposal_price_quote', label: t('crud.stages.proposalPriceQuote'), labelKey: 'crud.stages.proposalPriceQuote' },
        { value: 'negotiation_review', label: t('crud.stages.negotiationReview'), labelKey: 'crud.stages.negotiationReview' }
      ]
    },
    {
      name: 'owner_id',
      label: t('crud.fields.owner'),
      labelKey: 'crud.fields.owner',
      type: 'text'
    }
  ],
  bulkActions: [
    {
      key: 'convertToQuote',
      label: t('crud.actions.convertToQuote'),
      labelKey: 'crud.actions.convertToQuote',
      type: 'primary',
      onClick: () => console.log('Convert to Quote clicked')
    },
    {
      key: 'markAsWon',
      label: t('crud.actions.markAsWon'),
      labelKey: 'crud.actions.markAsWon',
      type: 'default',
      onClick: () => console.log('Mark as Won clicked')
    },
    {
      key: 'markAsLost',
      label: t('crud.actions.markAsLost'),
      labelKey: 'crud.actions.markAsLost',
      type: 'secondary',
      onClick: () => console.log('Mark as Lost clicked')
    }
  ],
  defaultSort: { field: 'expected_close_date', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/crm-sales/opportunities',
    endpoints: {
      list: '/api/crm-sales/opportunities',
      get: '/api/crm-sales/opportunities/{id}',
      create: '/api/crm-sales/opportunities',
      update: '/api/crm-sales/opportunities/{id}',
      delete: '/api/crm-sales/opportunities/{id}'
    }
  },
  permissions: ['crm.read', 'sales.read'],
  actions: []
})

export default function OpportunitiesListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const entityType = 'opportunity'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Opportunity')
  const opportunitiesConfig = createOpportunitiesConfig(t, entityTypeLabel)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/crm/opportunity/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await apiClient.delete(`/opportunities/${item.id}`)
          loadData() // Liste neu laden
        } catch (error) {
          toast({
            variant: 'destructive',
            title: t('crud.messages.deleteError', { entityType: entityTypeLabel })
          })
        }
      }
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/opportunities')
      if (response.success) {
        setData((response.data as any).items || [])
        setTotal((response.data as any).total || 0)
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

  useEffect(() => {
    loadData()
  }, [])

  const handleCreate = () => {
    navigate('/crm/opportunity/new')
  }

  const handleEdit = (item: any) => {
    handleAction('edit', item)
  }

  const handleDelete = (item: any) => {
    handleAction('delete', item)
  }

  const handleExport = () => {
    try {
      const csvHeader = `${t('crud.fields.number')};${t('crud.fields.name')};${t('crud.fields.stage')};${t('crud.fields.amount')};${t('crud.fields.probability')};${t('crud.fields.status')}\n`
      const csvContent = data.map((opp: any) =>
        `"${opp.number}";"${opp.name}";"${opp.stage}";"${opp.amount || 0}";"${opp.probability || 0}";"${opp.status}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `opportunities-liste-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: t('crud.messages.exportSuccess'),
        description: t('crud.messages.exportedItems', { count: data.length, entityType: entityTypeLabel }),
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
    <ListReport
      config={opportunitiesConfig}
      data={data}
      total={total}
      onCreate={handleCreate}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onExport={handleExport}
      onImport={() => {
        toast({
          title: t('crud.messages.importInfo'),
          description: t('crud.messages.importComingSoon'),
        })
      }}
      isLoading={loading}
    />
  )
}
