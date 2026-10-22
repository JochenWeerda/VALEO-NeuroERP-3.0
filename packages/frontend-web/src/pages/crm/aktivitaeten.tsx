import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '@/hooks/useAuth'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { Calendar, Mail, Phone, Plus, Search, Users, Loader2, Filter } from 'lucide-react'
import { queryKeys } from '@/lib/query'
import { crmService, type Activity } from '@/lib/services/crm-service'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'

const EMPTY_ACTIVITIES_RESPONSE: { data: Activity[]; total: number } = {
  data: [],
  total: 0,
}

export type DatePreset = 'all' | 'today' | 'week' | 'overdue'

function startOfLocalDay(value: Date): Date {
  const next = new Date(value)
  next.setHours(0, 0, 0, 0)
  return next
}

function startOfWeekMonday(value: Date): Date {
  const start = startOfLocalDay(value)
  const weekday = start.getDay()
  const offset = weekday === 0 ? -6 : 1 - weekday
  start.setDate(start.getDate() + offset)
  return start
}

export function matchesDatePreset(activity: Pick<Activity, 'date' | 'status'>, preset: DatePreset, now = new Date()): boolean {
  if (preset === 'all') return true
  const due = new Date(activity.date)
  const today = startOfLocalDay(now)
  if (preset === 'today') {
    return startOfLocalDay(due).getTime() === today.getTime()
  }
  if (preset === 'week') {
    const weekStart = startOfWeekMonday(now)
    const weekEnd = new Date(weekStart)
    weekEnd.setDate(weekEnd.getDate() + 7)
    return due >= weekStart && due < weekEnd
  }
  return due < today && activity.status !== 'completed'
}

export default function AktivitaetenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { user } = useAuth()
  const entityType = 'activity'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Aktivität')
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [assignedFilter, setAssignedFilter] = useState<string>('all')
  const [datePreset, setDatePreset] = useState<DatePreset>('all')
  const currentUserTokens = [user?.email, user?.sub, user?.name]
    .filter(Boolean)
    .map((value) => String(value).trim().toLowerCase())

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
    initialData: EMPTY_ACTIVITIES_RESPONSE,
    // Sofort veraltet: Sonst gilt der Platzhalter als frisch geladen und
    // `staleTime` verhindert den Mount-Fetch (Nutzermeldung 17.07.2026).
    initialDataUpdatedAt: 0,
  })

  const activities = activitiesData.data
  const totalActivities = activitiesData.total

  // Filter activities based on status and assignment
  const filteredActivities = activities.filter(activity => {
    if (statusFilter !== 'all' && activity.status !== statusFilter) return false
    if (assignedFilter === 'mine') {
      const assignedToken = String(activity.assignedTo || '').trim().toLowerCase()
      if (!assignedToken || !currentUserTokens.includes(assignedToken)) return false
    }
    if (!matchesDatePreset(activity, datePreset)) return false
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
          type="button"
          onClick={() => navigate(`/crm/aktivitaet/${activity.id}`)}
          className="inline-flex min-h-11 items-center text-left font-medium text-primary underline-offset-4 hover:underline"
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
          <span className={isOverdue ? 'font-semibold text-status-error' : ''}>
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
      <div className="space-y-4 p-3 md:p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-status-error">{t('crud.messages.loadError')}</h1>
          <p className="text-muted-foreground">
            {error instanceof Error ? error.message : t('common.unknownError')}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold">{getListTitle(t, entityTypeLabel)}</h1>
          <p className="text-muted-foreground">
            {isLoading ? t('crud.list.loading', { entityType: entityTypeLabel }) : t('crud.list.total', { count: totalActivities, entityType: entityTypeLabel })}
          </p>
        </div>
        <Button onClick={() => navigate('/crm/aktivitaet/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          {t('crud.actions.new')} {entityTypeLabel}
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.actions.search')} & {t('crud.actions.filter')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3">
            <div className="flex flex-col gap-3 lg:flex-row">
              <div className="relative min-w-0 flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder={t('crud.tooltips.placeholders.searchActivity')}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="min-h-touch pl-10"
                  aria-label="Aktivitäten suchen"
                />
              </div>
              <div className="relative min-w-0 lg:w-40">
                <Filter className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <NativeSelect
                  value={typeFilter}
                  onValueChange={setTypeFilter}
                  options={[
                    { value: 'all', label: t('crud.list.allTypes') },
                    { value: 'meeting', label: t('crud.fields.meeting') },
                    { value: 'call', label: t('crud.fields.call') },
                    { value: 'email', label: t('crud.fields.email') },
                    { value: 'note', label: t('crud.fields.note') },
                  ]}
                  className="min-h-touch pl-9"
                />
              </div>
              <div className="min-w-0 lg:w-40">
                <NativeSelect
                  value={statusFilter}
                  onValueChange={setStatusFilter}
                  options={[
                    { value: 'all', label: t('crud.list.allStatus', { defaultValue: 'Alle Status' }) },
                    { value: 'planned', label: t('status.planned') },
                    { value: 'completed', label: t('status.completed') },
                    { value: 'overdue', label: t('status.overdue') },
                  ]}
                  className="min-h-touch"
                />
              </div>
              <div className="min-w-0 lg:w-40">
                <NativeSelect
                  value={assignedFilter}
                  onValueChange={setAssignedFilter}
                  options={[
                    { value: 'all', label: t('crud.list.all') },
                    { value: 'mine', label: t('crud.list.mineOnly') },
                  ]}
                  className="min-h-touch"
                />
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                variant={datePreset === 'today' ? 'default' : 'outline'}
                className="min-h-touch touch-manipulation"
                aria-pressed={datePreset === 'today'}
                onClick={() => setDatePreset((current) => current === 'today' ? 'all' : 'today')}
              >
                {t('crud.fields.today')}
              </Button>
              <Button
                type="button"
                variant={datePreset === 'week' ? 'default' : 'outline'}
                className="min-h-touch touch-manipulation"
                aria-pressed={datePreset === 'week'}
                onClick={() => setDatePreset((current) => current === 'week' ? 'all' : 'week')}
              >
                {t('crud.fields.thisWeek')}
              </Button>
              <Button
                type="button"
                variant={datePreset === 'overdue' ? 'default' : 'outline'}
                className="min-h-touch touch-manipulation"
                aria-pressed={datePreset === 'overdue'}
                onClick={() => setDatePreset((current) => current === 'overdue' ? 'all' : 'overdue')}
              >
                {t('status.overdue')}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="overflow-x-auto pt-6">
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
            <span className="text-2xl font-bold text-primary">{plannedActivities}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('status.overdue')}</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-error">{overdueActivities}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('status.completed')}</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{completedActivities}</span>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
