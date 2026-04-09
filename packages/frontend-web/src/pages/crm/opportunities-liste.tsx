import { useState, useEffect, useMemo, useRef, type ChangeEvent } from 'react'
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
const apiClient = createApiClient('/api/v1/crm')

// Konfiguration für Opportunities ListReport (wird in Komponente mit i18n erstellt)
const createOpportunitiesConfig = (
  t: any,
  entityTypeLabel: string,
  handlers: {
    convertToQuote: (items: any[]) => void
    markAsWon: (items: any[]) => void
    markAsLost: (items: any[]) => void
  },
): ListConfig => ({
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
      render: (value, item: any) => {
        const name = item?.customer_name ?? item?.customer?.name ?? value
        return name ? <span>{name}</span> : '-'
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
      onClick: handlers.convertToQuote,
    },
    {
      key: 'markAsWon',
      label: t('crud.actions.markAsWon'),
      labelKey: 'crud.actions.markAsWon',
      type: 'default',
      onClick: handlers.markAsWon,
    },
    {
      key: 'markAsLost',
      label: t('crud.actions.markAsLost'),
      labelKey: 'crud.actions.markAsLost',
      type: 'secondary',
      onClick: handlers.markAsLost,
    }
  ],
  defaultSort: { field: 'expected_close_date', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/crm/opportunities',
    endpoints: {
      list: '/api/v1/crm/opportunities',
      get: '/api/v1/crm/opportunities/{id}',
      create: '/api/v1/crm/opportunities',
      update: '/api/v1/crm/opportunities/{id}',
      delete: '/api/v1/crm/opportunities/{id}'
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
  const importInputRef = useRef<HTMLInputElement>(null)

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

  const updateSelectedOpportunities = async (
    items: any[],
    payload: Record<string, unknown>,
    successTitle: string,
    successDescription: string,
    errorTitle: string,
  ): Promise<void> => {
    if (!items.length) {
      toast({
        variant: 'destructive',
        title: 'Keine Auswahl',
        description: 'Bitte mindestens eine Opportunity auswaehlen.',
      })
      return
    }

    try {
      await Promise.all(items.map((item) => apiClient.put(`/opportunities/${item.id}`, payload)))
      toast({ title: successTitle, description: successDescription })
      await loadData()
    } catch (error) {
      toast({
        variant: 'destructive',
        title: errorTitle,
        description: 'Der Statuswechsel konnte nicht fuer alle Opportunities abgeschlossen werden.',
      })
    }
  }

  const handleConvertToQuote = (items: any[]) => {
    if (!items.length) {
      toast({
        variant: 'destructive',
        title: 'Keine Auswahl',
        description: 'Bitte mindestens eine Opportunity auswaehlen.',
      })
      return
    }

    const lead = items[0]
    if (items.length === 1) {
      navigate(`/sales/angebot-erstellen?opportunityId=${lead.id}`)
      return
    }

    void updateSelectedOpportunities(
      items,
      { status: 'proposal', stage: 'proposal_price_quote' },
      'Quote-Phase vorbereitet',
      `${items.length} Opportunities wurden in die Angebotsphase ueberfuehrt.`,
      'Konvertierung fehlgeschlagen',
    ).then(() => navigate('/crm/opportunities-kanban'))
  }

  const handleMarkAsWon = (items: any[]) => {
    void updateSelectedOpportunities(
      items,
      { status: 'closed_won', stage: 'closed_won' },
      'Als gewonnen markiert',
      `${items.length} Opportunities wurden abgeschlossen.`,
      'Gewinnstatus fehlgeschlagen',
    )
  }

  const handleMarkAsLost = (items: any[]) => {
    void updateSelectedOpportunities(
      items,
      { status: 'closed_lost', stage: 'closed_lost' },
      'Als verloren markiert',
      `${items.length} Opportunities wurden als verloren gesetzt.`,
      'Verluststatus fehlgeschlagen',
    )
  }

  const handleImportFile = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const raw = await file.text()
      const rows = raw
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean)

      if (rows.length <= 1) {
        toast({ variant: 'destructive', title: 'Import fehlgeschlagen', description: 'Die CSV-Datei enthaelt keine Datenzeilen.' })
        return
      }

      const headers = rows[0].split(';').map((value) => value.replace(/^"|"$/g, '').trim().toLowerCase())
      const dataRows = rows.slice(1)
      let created = 0

      for (const row of dataRows) {
        const values = row.split(';').map((value) => value.replace(/^"|"$/g, '').trim())
        const get = (names: string[]) => {
          const idx = headers.findIndex((header) => names.includes(header))
          return idx >= 0 ? values[idx] ?? '' : ''
        }

        const payload = {
          number: get(['number', 'nummer']) || `OPP-${Date.now()}-${created + 1}`,
          name: get(['name', 'bezeichnung', 'titel']) || 'Importierte Opportunity',
          stage: get(['stage', 'stufe']) || 'initial_contact',
          status: get(['status']) || 'prospecting',
          amount: Number(get(['amount', 'betrag']).replace(',', '.')) || 0,
          probability: Number(get(['probability', 'wahrscheinlichkeit']).replace(',', '.')) || 0,
          expected_revenue: Number(get(['expected_revenue', 'erwarteter_umsatz']).replace(',', '.')) || 0,
          customer_name: get(['customer', 'kunde', 'customer_name']) || undefined,
          owner_id: get(['owner', 'owner_id']) || undefined,
        }
        await apiClient.post('/opportunities', payload)
        created += 1
      }

      toast({ title: 'Import abgeschlossen', description: `${created} Opportunities angelegt.` })
      await loadData()
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: 'Import fehlgeschlagen',
        description: error.response?.data?.detail ?? error.message,
      })
    } finally {
      event.target.value = ''
    }
  }

  const opportunitiesConfig = useMemo(
    () =>
      createOpportunitiesConfig(t, entityTypeLabel, {
        convertToQuote: handleConvertToQuote,
        markAsWon: handleMarkAsWon,
        markAsLost: handleMarkAsLost,
      }),
    [t, entityTypeLabel],
  )

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
    <>
      <input ref={importInputRef} type="file" accept=".csv" className="hidden" onChange={handleImportFile} />
      <ListReport
        config={opportunitiesConfig}
        data={data}
        total={total}
        onCreate={handleCreate}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onExport={handleExport}
        onImport={() => importInputRef.current?.click()}
        isLoading={loading}
      />
    </>
  )
}
