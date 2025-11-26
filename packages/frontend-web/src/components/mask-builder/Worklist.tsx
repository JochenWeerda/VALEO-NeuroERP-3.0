import React, { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { AlertTriangle, CheckCircle, Clock, Filter, Search, XCircle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { WorklistConfig, WorklistItem } from './types'

interface WorklistProps {
  config: WorklistConfig
  items: WorklistItem[]
  onAction: (_item: WorklistItem, _action: string) => void
  isLoading?: boolean
}

const Worklist: React.FC<WorklistProps> = ({
  config,
  items,
  onAction,
  isLoading: _isLoading = false
}) => {
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [groupBy, setGroupBy] = useState<string>(config.groupBy || '')

  // Filter items
  const filteredItems = items.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter
    const matchesPriority = priorityFilter === 'all' || item.priority === priorityFilter

    return matchesSearch && matchesStatus && matchesPriority
  })

  // Group items if groupBy is specified
  const groupedItems = groupBy ? filteredItems.reduce((groups, item) => {
    const key = item[groupBy as keyof WorklistItem] as string || 'Unbekannt'
    if (!groups[key]) groups[key] = []
    groups[key].push(item)
    return groups
  }, {} as Record<string, WorklistItem[]>) : { 'Alle': filteredItems }

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { variant: 'secondary' as const, icon: Clock, text: 'Ausstehend' },
      'in-progress': { variant: 'default' as const, icon: AlertTriangle, text: 'In Bearbeitung' },
      completed: { variant: 'outline' as const, icon: CheckCircle, text: 'Abgeschlossen' },
      overdue: { variant: 'destructive' as const, icon: XCircle, text: 'Überfällig' }
    }
    const config = statusConfig[status as keyof typeof statusConfig]
    const Icon = config.icon

    return (
      <Badge variant={config.variant} className="gap-1">
        <Icon className="h-3 w-3" />
        {config.text}
      </Badge>
    )
  }

  const getPriorityBadge = (priority: string) => {
    const priorityConfig = {
      low: { variant: 'outline' as const, text: 'Niedrig' },
      medium: { variant: 'secondary' as const, text: 'Mittel' },
      high: { variant: 'default' as const, text: 'Hoch' },
      urgent: { variant: 'destructive' as const, text: 'Dringend' }
    }
    const config = priorityConfig[priority as keyof typeof priorityConfig]

    return <Badge variant={config.variant}>{config.text}</Badge>
  }

  const handleAction = (item: WorklistItem, actionKey: string) => {
    const action = config.actions.find(a => a.key === actionKey)
    if (!action) return

    if (action.condition(item)) {
      onAction(item, actionKey)
    } else {
      toast({
        title: "Aktion nicht verfügbar",
        description: "Diese Aktion kann für dieses Element nicht ausgeführt werden.",
        variant: "destructive",
      })
    }
  }

  const renderItem = (item: WorklistItem) => (
    <Card key={item.id} className="mb-4">
      <CardContent className="pt-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="font-medium">{item.title}</h3>
              {getStatusBadge(item.status)}
              {getPriorityBadge(item.priority)}
            </div>

            {item.description && (
              <p className="text-sm text-muted-foreground mb-2">{item.description}</p>
            )}

            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              {item.assignedTo && (
                <span>Zugewiesen an: {item.assignedTo}</span>
              )}
              {item.dueDate && (
                <span>
                  Fällig: {new Date(item.dueDate).toLocaleDateString('de-DE')}
                  {new Date(item.dueDate) < new Date() && item.status !== 'completed' && (
                    <span className="text-red-600 ml-1">(Überfällig)</span>
                  )}
                </span>
              )}
            </div>

            {item.metadata && (
              <div className="mt-2 flex flex-wrap gap-1">
                {Object.entries(item.metadata).map(([key, value]) => (
                  <Badge key={key} variant="outline" className="text-xs">
                    {key}: {String(value)}
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <div className="flex gap-1 ml-4">
            {config.actions
              .filter(action => action.condition(item))
              .map(action => (
                <Button
                  key={action.key}
                  variant={action.type === 'primary' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleAction(item, action.key)}
                  className="gap-1"
                >
                  {action.icon && <span className="text-sm">{action.icon}</span>}
                  {action.label}
                </Button>
              ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{config.title}</h1>
          {config.subtitle && (
            <p className="text-muted-foreground">{config.subtitle}</p>
          )}
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Suche & Filter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {/* Search */}
            <div>
              <Label>Suche</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Titel oder Beschreibung..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <Label>Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Status</SelectItem>
                  <SelectItem value="pending">Ausstehend</SelectItem>
                  <SelectItem value="in-progress">In Bearbeitung</SelectItem>
                  <SelectItem value="completed">Abgeschlossen</SelectItem>
                  <SelectItem value="overdue">Überfällig</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Priority Filter */}
            <div>
              <Label>Priorität</Label>
              <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alle Prioritäten</SelectItem>
                  <SelectItem value="low">Niedrig</SelectItem>
                  <SelectItem value="medium">Mittel</SelectItem>
                  <SelectItem value="high">Hoch</SelectItem>
                  <SelectItem value="urgent">Dringend</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Group By */}
            {config.groupBy && (
              <div>
                <Label>Gruppieren nach</Label>
                <Select value={groupBy} onValueChange={setGroupBy}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Nicht gruppieren</SelectItem>
                    <SelectItem value={config.groupBy}>{config.groupBy}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Worklist Items */}
      <div className="space-y-6">
        {Object.entries(groupedItems).map(([groupName, groupItems]) => (
          <div key={groupName}>
            {groupBy && (
              <h2 className="text-xl font-semibold mb-4">{groupName}</h2>
            )}

            {groupItems.length === 0 ? (
              <Card>
                <CardContent className="pt-6 text-center text-muted-foreground">
                  Keine Elemente gefunden
                </CardContent>
              </Card>
            ) : (
              groupItems.map(renderItem)
            )}
          </div>
        ))}
      </div>

      {/* Summary */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {items.filter(i => i.status === 'pending').length}
              </div>
              <div className="text-sm text-muted-foreground">Ausstehend</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {items.filter(i => i.status === 'in-progress').length}
              </div>
              <div className="text-sm text-muted-foreground">In Bearbeitung</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {items.filter(i => i.status === 'completed').length}
              </div>
              <div className="text-sm text-muted-foreground">Abgeschlossen</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {items.filter(i => i.status === 'overdue').length}
              </div>
              <div className="text-sm text-muted-foreground">Überfällig</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Worklist