import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Target, Loader2 } from 'lucide-react'
import { queryKeys } from '@/lib/query'
import { apiClient } from '@/lib/api-client'
import { toast } from '@/hooks/use-toast'
import { useConvertLead } from '@/lib/api/lead-gen'
import { type Lead } from '@/lib/services/crm-service'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'

const EMPTY_LEADS_RESPONSE: { data: Lead[]; total: number } = {
  data: [],
  total: 0,
}

export default function LeadsPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const entityType = 'lead'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Lead')

  const convertLead = useConvertLead()
  const { data: leadsData, isLoading, error, refetch } = useQuery({
    queryKey: queryKeys.crm.leads.listFiltered({ search: searchTerm || undefined }),
    queryFn: async () => {
      // Echte uebernommene Leads aus public.crm_leads (Lead-Generierung-Funnel).
      const res = await apiClient.get<{ data: Lead[]; total: number }>(
        '/api/v1/crm/lead-generierung/leads',
        { params: searchTerm ? { search: searchTerm } : {} },
      )
      return res.data ?? EMPTY_LEADS_RESPONSE
    },
    initialData: EMPTY_LEADS_RESPONSE,
    initialDataUpdatedAt: 0, // initialData sofort als veraltet -> Fetch beim Mount
  })

  const leads = leadsData.data
  const totalLeads = leadsData.total
  const totalPotential = leads.reduce((sum, lead) => sum + lead.potential, 0)
  const qualifiedLeads = leads.filter(lead => lead.status === 'qualified').length
  const highPriorityLeads = leads.filter(lead => lead.priority === 'high').length

  const handleConvert = (lead: Lead) => {
    convertLead.mutate(lead.id, {
      onSuccess: (r) => {
        toast({ title: 'Lead konvertiert', description: `${lead.company} → Kunde ${r.kunden_nr}.` })
        void refetch()
      },
      onError: (e: unknown) => toast({ variant: 'destructive', title: 'Konversion fehlgeschlagen', description: e instanceof Error ? e.message : 'Fehler' }),
    })
  }

  const columns = [
    {
      key: 'company' as const,
      label: t('crud.fields.company'),
      render: (lead: Lead) => (
        <div>
          <button
            onClick={() => navigate(`/crm/lead/${lead.id}`)}
            className="font-medium text-blue-600 hover:underline"
          >
            {lead.company}
          </button>
          <div className="text-sm text-muted-foreground">{lead.contactPerson}</div>
        </div>
      ),
    },
    { key: 'source' as const, label: t('crud.fields.source') },
    {
      key: 'potential' as const,
      label: t('crud.fields.potential'),
      render: (lead: Lead) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(lead.potential),
    },
    {
      key: 'priority' as const,
      label: t('crud.fields.priority'),
      render: (lead: Lead) => {
        const priorityLabel = getStatusLabel(t, lead.priority, lead.priority)
        return (
          <Badge variant={lead.priority === 'high' ? 'destructive' : lead.priority === 'medium' ? 'secondary' : 'outline'}>
            {priorityLabel}
          </Badge>
        )
      },
    },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (lead: Lead) => {
        const statusLabel = getStatusLabel(t, lead.status, lead.status)
        return (
          <Badge variant={lead.status === 'qualified' ? 'default' : 'outline'}>
            {statusLabel}
          </Badge>
        )
      },
    },
    {
      key: 'aktion' as const,
      label: 'Aktion',
      render: (lead: Lead) => (
        <Button
          size="sm"
          variant="outline"
          onClick={() => handleConvert(lead)}
          disabled={convertLead.isPending}
        >
          → Kunde
        </Button>
      ),
    },
  ]

  if (error) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-status-error">{t('crud.messages.loadError')}</h1>
          <p className="text-muted-foreground">
            {error instanceof Error ? error.message : t('crud.messages.unknownError')}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{getListTitle(t, entityTypeLabel)}</h1>
          <p className="text-muted-foreground">
            {isLoading ? t('crud.list.loading', { entityType: entityTypeLabel }) : t('crud.list.total', { count: totalLeads, entityType: entityTypeLabel })}
          </p>
        </div>
        <Button onClick={() => navigate('/crm/lead/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          {t('crud.actions.new')} {entityTypeLabel}
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.list.total')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{totalLeads}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.fields.totalPotential')}</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(totalPotential)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.fields.qualified')}</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{qualifiedLeads}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.fields.highPriority')}</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-error">{highPriorityLeads}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('common.search')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder={t('crud.list.searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              {t('crud.actions.export')}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">{t('crud.list.loading', { entityType: entityTypeLabel })}</span>
            </div>
          ) : (
            <DataTable data={leads} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
