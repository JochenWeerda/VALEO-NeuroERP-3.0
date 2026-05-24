import { useState, useEffect, useMemo, useRef, type ChangeEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { apiClient } from '@/lib/api-client'
import { formatDate, formatCurrency } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

// API Client für Opportunities

type CrmRoleFocus = 'all' | 'sales' | 'inside-sales' | 'management' | 'finance' | 'customer-success'

const crmRoleProfiles: Array<{ id: CrmRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt die Pipeline fuer Vertrieb, Inside Sales, Leitung, Finance und Customer Success.',
  },
  {
    id: 'sales',
    label: 'Vertrieb',
    description: 'Fokus auf Deal-Lage, Abschlusswahrscheinlichkeit und naechstes Kundengespraech.',
  },
  {
    id: 'inside-sales',
    label: 'Inside Sales',
    description: 'Fokus auf Datenqualitaet, Follow-up, Angebotserstellung und Wiedervorlage.',
  },
  {
    id: 'management',
    label: 'Leitung',
    description: 'Fokus auf Pipeline-Wert, erwarteten Umsatz und Abschlussrisiko.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Fokus auf erwarteten Umsatz, Angebotspfad und spaetere Auftrag-/Faktura-Uebergabe.',
  },
  {
    id: 'customer-success',
    label: 'Customer Success',
    description: 'Fokus auf gewonnene Deals, Uebergabe und naechste Kundenbetreuung.',
  },
]

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
  const [roleFocus, setRoleFocus] = useState<CrmRoleFocus>('all')
  const entityType = 'opportunity'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Opportunity')
  const importInputRef = useRef<HTMLInputElement>(null)

  const [pendingRows, setPendingRows] = useState<Set<string>>(new Set())

  async function withPending(key: string, fn: () => Promise<void>) {
    if (pendingRows.has(key)) return
    setPendingRows(prev => new Set(prev).add(key))
    try { await fn() } finally {
      setPendingRows(prev => { const s = new Set(prev); s.delete(key); return s })
    }
  }

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/crm/opportunity/${item.id}`)
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/api/v1/crm/opportunities')
      if (response.data) {
        setData((response.data as any).items || [])
        setTotal((response.data as any).total || 0)
      }
    } catch (error) {
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
      await Promise.all(items.map((item) => apiClient.put(`/api/v1/crm/opportunities/${item.id}`, payload)))
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
        await apiClient.post('/api/v1/crm/opportunities', payload)
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
    if (!confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) return
    void withPending(String(item.id), async () => {
      try {
        await apiClient.delete(`/api/v1/crm/opportunities/${item.id}`)
        loadData()
      } catch {
        toast({ variant: 'destructive', title: t('crud.messages.deleteError', { entityType: entityTypeLabel }) })
      }
    })
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

  const visibleTotal = data.length
  const proposalCount = data.filter((item) => item.status === 'proposal' || item.stage === 'proposal_price_quote').length
  const negotiationCount = data.filter((item) => item.status === 'negotiation' || item.stage === 'negotiation_review').length
  const wonCount = data.filter((item) => item.status === 'closed_won').length
  const lostCount = data.filter((item) => item.status === 'closed_lost').length
  const activeCount = data.filter((item) => !['closed_won', 'closed_lost'].includes(String(item.status || ''))).length
  const expectedRevenue = data.reduce((sum, item) => sum + Number(item.expected_revenue || 0), 0)
  const missingOwnerCount = data.filter((item) => !item.owner_id).length
  const nextPipelineAction = proposalCount > 0
    ? 'Opportunities in der Angebotsphase nachfassen oder in ein Angebot ueberfuehren.'
    : negotiationCount > 0
      ? 'Verhandlungsergebnis entscheiden: gewonnen, verloren oder naechster Termin.'
      : activeCount > 0
        ? 'Aktive Opportunities qualifizieren und naechsten Kundenschritt setzen.'
        : 'Neue Opportunity anlegen oder Import starten.'
  const pipelineTaskItems: UxTaskItem[] = [
    {
      label: 'Opportunity erfassen',
      done: visibleTotal > 0,
      hint: visibleTotal > 0 ? `${visibleTotal} Opportunities in der aktuellen Sicht.` : 'Neue Opportunity anlegen oder CSV importieren.',
    },
    {
      label: 'Qualifizieren und Owner klaeren',
      done: activeCount > 0 && missingOwnerCount === 0,
      hint: missingOwnerCount > 0 ? `${missingOwnerCount} Opportunities brauchen einen Owner.` : 'Aktive Opportunities sind einem Owner zugeordnet.',
    },
    {
      label: 'Angebot vorbereiten',
      done: proposalCount > 0,
      hint: proposalCount > 0 ? `${proposalCount} Opportunities stehen in der Angebotsphase.` : 'Qualifizierte Chancen in Angebot ueberfuehren.',
    },
    {
      label: 'Entscheiden und nachfassen',
      done: wonCount + lostCount > 0,
      hint: negotiationCount > 0 ? `${negotiationCount} Opportunities sind in Verhandlung.` : 'Gewonnene, verlorene und offene Deals regelmaessig nachhalten.',
    },
  ]
  const pipelineCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen',
      available: true,
      hint: 'Neue Opportunities koennen direkt aus der Liste angelegt werden.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Kunde, Stage, Betrag, Wahrscheinlichkeit, Owner und Status sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Bearbeiten',
      available: visibleTotal > 0,
      hint: 'Opportunities koennen geoeffnet und im Detail bearbeitet werden.',
    },
    {
      key: 'delete',
      label: 'Loeschen',
      available: visibleTotal > 0,
      hint: 'Einzelne Opportunities koennen geloescht werden, solange die Rolle berechtigt ist.',
    },
    {
      key: 'approve',
      label: 'Pipeline-Aktion',
      available: activeCount > 0,
      hint: 'Bulk-Aktionen ueberfuehren in Angebot, markieren gewonnen oder markieren verloren.',
    },
    {
      key: 'export',
      label: 'Export/Import',
      available: true,
      hint: 'CSV-Export und CSV-Import sind an der Liste angebunden.',
    },
    {
      key: 'audit',
      label: 'Follow-up',
      available: true,
      hint: 'Stage, Status, Owner und erwarteter Abschluss bilden die Nachfassspur.',
    },
  ]

  return (
    <div className="space-y-6">
      <input ref={importInputRef} type="file" accept=".csv" className="hidden" onChange={handleImportFile} />
      <RoleFocusBar
        roles={crmRoleProfiles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={roleFocus === 'all' ? 5 : 1}
        totalCount={5}
      />
      <ManagementDecisionPanel
        decision={{
          allowed: visibleTotal > 0,
          allowedLabel: 'Pipeline handlungsfaehig',
          blockedLabel: 'Pipeline leer',
          summary: visibleTotal > 0
            ? `Die Pipeline enthaelt ${visibleTotal} Opportunities mit ${formatCurrency(expectedRevenue, 'EUR')} erwartetem Umsatz. ${nextPipelineAction}`
            : 'In der aktuellen Sicht gibt es keine Opportunities. Legen Sie eine neue Chance an oder importieren Sie eine CSV-Datei.',
          blockerCount: visibleTotal === 0 ? 1 : missingOwnerCount,
          nextFocus: nextPipelineAction,
          template: {
            label: 'Opportunity anlegen',
            href: '/crm/opportunity/new',
          },
        }}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTaskPlan title="Pipeline-Follow-up-Plan" items={pipelineTaskItems} />
        <NextActionPanel
          action={nextPipelineAction}
          tone={proposalCount > 0 || negotiationCount > 0 ? 'amber' : visibleTotal > 0 ? 'blue' : 'red'}
        />
      </div>
      <CrudCapabilityChecklist capabilities={pipelineCrudCapabilities} />
      <ListReport
        config={opportunitiesConfig}
        data={data}
        total={total}
        onCreate={handleCreate}
        onEdit={handleEdit}
        onDelete={handleDelete}
        pendingRows={pendingRows}
        onExport={handleExport}
        onImport={() => importInputRef.current?.click()}
        isLoading={loading}
      />
    </div>
  )
}
