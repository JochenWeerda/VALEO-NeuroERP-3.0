import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Calendar, Mail, Phone, Plus, Search, Users, Loader2, Filter } from 'lucide-react'
import { queryKeys } from '@/lib/query'
import { crmService, type Activity } from '@/lib/services/crm-service'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'

export default function AktivitaetenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entityType = 'activity'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Aktivität')
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [assignedFilter, setAssignedFilter] = useState<string>('all')

  const { data: activitiesData, isLoading, error } = useQuery({
    queryKey: queryKeys.crm.activities.listFiltered({
      search: searchTerm || undefined,
      type: typeFilter !== 'all' ? typeFilter : undefined,
      status: statusFilter !== 'all' ? statusFilter : undefined,
    }),
    queryFn: () => crmService.getActivities({
      search: searchTerm || undefined,
      type: typeFilter !== 'all' ? typeFilter : undefined,
    }),
  })

  const activities = activitiesData?.data || []
  const totalActivities = activitiesData?.total || 0

  // Filter activities based on status and assignment
  const filteredActivities = activities.filter(activity => {
    if (statusFilter !== 'all' && activity.status !== statusFilter) return false
    if (assignedFilter === 'mine' && activity.assignedTo !== 'current-user') return false // TODO: Get current user
    return true
  })

  const plannedActivities = filteredActivities.filter(a => a.status === 'planned').length
  const overdueActivities = filteredActivities.filter(a => {
    const dueDate = new Date(a.date)
    const today = new Date()
    return dueDate < today && a.status !== 'completed'
  }).length
  const completedActivities = filteredActivities.filter(a => a.status === 'completed').length

  const columns = [
    {
      key: 'type' as const,
      label: t('crud.fields.type'),
      render: (activity: Activity) => {
        const icons = {
          meeting: Calendar,
          call: Phone,
          email: Mail,
          note: Users
        }
        const Icon = icons[activity.type] || Users
        const typeLabels: Record<string, string> = {
          meeting: t('crud.fields.meeting'),
          call: t('crud.fields.call'),
          email: t('crud.fields.email'),
          note: t('crud.fields.note')
        }
        return (
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4" />
            <span className="capitalize">
              {typeLabels[activity.type] || activity.type}
            </span>
          </div>
        )
      },
    },
    {
      key: 'title' as const,
      label: t('crud.fields.title'),
      render: (activity: Activity) => (
        <button
          onClick={() => navigate(`/crm/aktivitaet/${activity.id}`)}
          className="font-medium text-blue-600 hover:underline text-left"
        >
          {activity.title}
        </button>
      ),
    },
    { key: 'customer' as const, label: t('crud.entities.customer') },
    { key: 'contactPerson' as const, label: t('crud.fields.contactPerson') },
    {
      key: 'date' as const,
      label: t('crud.fields.date'),
      render: (activity: Activity) => {
        const dueDate = new Date(activity.date)
        const today = new Date()
        const isOverdue = dueDate < today && activity.status !== 'completed'
        return (
          <span className={isOverdue ? 'font-semibold text-red-600' : ''}>
            {dueDate.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    { key: 'assignedTo' as const, label: t('crud.fields.assignedTo') },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (activity: Activity) => (
        <Badge variant={
          activity.status === 'completed' ? 'outline' :
          activity.status === 'overdue' ? 'destructive' : 'secondary'
        }>
          {getStatusLabel(t, activity.status, activity.status)}
        </Badge>
      ),
    },
  ]

  if (error) {
    return (
      <div className="space-y-4 p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">{t('crud.messages.loadError')}</h1>
          <p className="text-muted-foreground">
            {error instanceof Error ? error.message : t('common.unknownError')}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{getListTitle(t, entityTypeLabel)}</h1>
          <p className="text-muted-foreground">
            {isLoading ? t('crud.list.loading', { entityType: entityTypeLabel }) : t('crud.list.total', { count: totalActivities, entityType: entityTypeLabel })}
          </p>
        </div>
        <Button onClick={() => navigate('/crm/aktivitaet/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          {t('crud.actions.new')} {entityTypeLabel}
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.fields.totalActivities')}</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{totalActivities}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('status.planned')}</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-blue-600">{plannedActivities}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('status.overdue')}</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{overdueActivities}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('status.completed')}</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{completedActivities}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.actions.search')} & {t('crud.actions.filter')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            <div className="flex gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder={t('crud.tooltips.placeholders.searchActivity')}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-40">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder={t('crud.fields.type')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('crud.list.allTypes')}</SelectItem>
                  <SelectItem value="meeting">{t('crud.fields.meeting')}</SelectItem>
                  <SelectItem value="call">{t('crud.fields.call')}</SelectItem>
                  <SelectItem value="email">{t('crud.fields.email')}</SelectItem>
                  <SelectItem value="note">{t('crud.fields.note')}</SelectItem>
                </SelectContent>
              </Select>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder={t('crud.fields.status')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('crud.list.allStatus', { defaultValue: 'Alle Status' })}</SelectItem>
                  <SelectItem value="planned">{t('status.planned')}</SelectItem>
                  <SelectItem value="completed">{t('status.completed')}</SelectItem>
                  <SelectItem value="overdue">{t('status.overdue')}</SelectItem>
                </SelectContent>
              </Select>
              <Select value={assignedFilter} onValueChange={setAssignedFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder={t('crud.fields.assignedTo')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t('crud.list.all')}</SelectItem>
                  <SelectItem value="mine">{t('crud.list.mineOnly')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                {t('crud.fields.today')}
              </Button>
              <Button variant="outline" size="sm">
                {t('crud.fields.thisWeek')}
              </Button>
              <Button variant="outline" size="sm">
                {t('status.overdue')}
              </Button>
            </div>
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
            <DataTable data={filteredActivities} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
