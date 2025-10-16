import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
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

export default function AktivitaetenPage(): JSX.Element {
  const navigate = useNavigate()
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
      label: 'Typ',
      render: (activity: Activity) => {
        const icons = {
          meeting: Calendar,
          call: Phone,
          email: Mail,
          note: Users
        }
        const Icon = icons[activity.type] || Users
        return (
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4" />
            <span className="capitalize">
              {activity.type === 'meeting' ? 'Termin' :
               activity.type === 'call' ? 'Anruf' :
               activity.type === 'email' ? 'E-Mail' : 'Notiz'}
            </span>
          </div>
        )
      },
    },
    {
      key: 'title' as const,
      label: 'Titel',
      render: (activity: Activity) => (
        <button
          onClick={() => navigate(`/crm/aktivitaet/${activity.id}`)}
          className="font-medium text-blue-600 hover:underline text-left"
        >
          {activity.title}
        </button>
      ),
    },
    { key: 'customer' as const, label: 'Kunde' },
    { key: 'contactPerson' as const, label: 'Ansprechpartner' },
    {
      key: 'date' as const,
      label: 'Datum',
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
    { key: 'assignedTo' as const, label: 'Zuständig' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (activity: Activity) => (
        <Badge variant={
          activity.status === 'completed' ? 'outline' :
          activity.status === 'overdue' ? 'destructive' : 'secondary'
        }>
          {activity.status === 'completed' ? 'Abgeschlossen' :
           activity.status === 'overdue' ? 'Überfällig' : 'Geplant'}
        </Badge>
      ),
    },
  ]

  if (error) {
    return (
      <div className="space-y-4 p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Fehler beim Laden der Aktivitäten</h1>
          <p className="text-muted-foreground">
            {error instanceof Error ? error.message : 'Unbekannter Fehler'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">CRM-Aktivitäten</h1>
          <p className="text-muted-foreground">
            {isLoading ? 'Lade Aktivitäten...' : `${totalActivities} Termine, Anrufe, E-Mails & Notizen`}
          </p>
        </div>
        <Button onClick={() => navigate('/crm/aktivitaet/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Aktivität
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktivitäten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{totalActivities}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Geplant</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-blue-600">{plannedActivities}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Überfällig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{overdueActivities}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{completedActivities}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            <div className="flex gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Suche nach Titel, Kunde oder Ansprechpartner..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-40">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Typ" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Typen</SelectItem>
                  <SelectItem value="meeting">Termin</SelectItem>
                  <SelectItem value="call">Anruf</SelectItem>
                  <SelectItem value="email">E-Mail</SelectItem>
                  <SelectItem value="note">Notiz</SelectItem>
                </SelectContent>
              </Select>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Status</SelectItem>
                  <SelectItem value="planned">Geplant</SelectItem>
                  <SelectItem value="completed">Abgeschlossen</SelectItem>
                  <SelectItem value="overdue">Überfällig</SelectItem>
                </SelectContent>
              </Select>
              <Select value={assignedFilter} onValueChange={setAssignedFilter}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Zuständig" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle</SelectItem>
                  <SelectItem value="mine">Nur Meine</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                Heute
              </Button>
              <Button variant="outline" size="sm">
                Diese Woche
              </Button>
              <Button variant="outline" size="sm">
                Überfällig
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
              <span className="ml-2">Lade Aktivitäten...</span>
            </div>
          ) : (
            <DataTable data={filteredActivities} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
