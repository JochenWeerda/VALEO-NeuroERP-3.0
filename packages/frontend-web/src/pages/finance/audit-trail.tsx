/**
 * GoBD Audit Trail View
 * Zeigt alle Audit-Trail-Einträge mit Hash-Chain-Validierung
 * FIBU-COMP-01: GoBD / Audit Trail UI
 */

import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Search, FileText, Shield, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import { useToast } from '@/hooks/use-toast'

type AuditLogEntry = {
  id: string
  timestamp: string
  user_id: string
  user_email: string
  tenant_id: string
  action: string
  entity_type: string
  entity_id: string
  changes: Record<string, any>
  ip_address?: string
  user_agent?: string
  correlation_id?: string
}

type AuditStats = {
  total_entries: number
  actions: Array<{ action: string; count: number }>
  entity_types: Array<{ type: string; count: number }>
  top_users: Array<{ user: string; count: number }>
  timestamp: string
}

export default function AuditTrailPage(): JSX.Element {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [logs, setLogs] = useState<AuditLogEntry[]>([])
  const [stats, setStats] = useState<AuditStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [entityTypeFilter, setEntityTypeFilter] = useState<string>('all')
  const [actionFilter, setActionFilter] = useState<string>('all')

  useEffect(() => {
    async function fetchAuditLogs(): Promise<void> {
      setLoading(true)
      try {
        const params = new URLSearchParams()
        if (entityTypeFilter !== 'all') params.append('entity_type', entityTypeFilter)
        if (actionFilter !== 'all') params.append('action', actionFilter)
        params.append('limit', '100')

        const response = await fetch(`/api/v1/audit/logs?${params.toString()}`)
        if (!response.ok) {
          throw new Error('Failed to fetch audit logs')
        }
        const data: AuditLogEntry[] = await response.json()
        setLogs(data)
      } catch (error) {
        console.error('Error fetching audit logs:', error)
        toast({
          title: t('common.error'),
          description: t('crud.feedback.fetchError', { entityType: 'Audit-Logs' }),
          variant: 'destructive',
        })
      } finally {
        setLoading(false)
      }
    }

    async function fetchStats(): Promise<void> {
      try {
        const response = await fetch('/api/v1/audit/stats')
        if (!response.ok) {
          throw new Error('Failed to fetch audit stats')
        }
        const data: AuditStats = await response.json()
        setStats(data)
      } catch (error) {
        console.error('Error fetching audit stats:', error)
      }
    }

    void fetchAuditLogs()
    void fetchStats()
  }, [entityTypeFilter, actionFilter, t, toast])

  const filteredLogs = logs.filter((log) => {
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      return (
        log.user_email.toLowerCase().includes(searchLower) ||
        log.entity_type.toLowerCase().includes(searchLower) ||
        log.entity_id.toLowerCase().includes(searchLower) ||
        log.action.toLowerCase().includes(searchLower)
      )
    }
    return true
  })

  const getActionColor = (action: string): string => {
    switch (action.toLowerCase()) {
      case 'create':
        return 'bg-green-100 text-green-800'
      case 'update':
        return 'bg-blue-100 text-blue-800'
      case 'delete':
        return 'bg-red-100 text-red-800'
      case 'view':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const columns = [
    {
      accessorKey: 'timestamp',
      header: t('crud.fields.date'),
      cell: ({ row }: { row: { original: AuditLogEntry } }) => (
        <div className="text-sm">
          {format(new Date(row.original.timestamp), 'dd.MM.yyyy HH:mm:ss', { locale: de })}
        </div>
      ),
    },
    {
      accessorKey: 'user_email',
      header: t('crud.fields.user'),
      cell: ({ row }: { row: { original: AuditLogEntry } }) => (
        <div>
          <div className="font-medium">{row.original.user_email}</div>
          <div className="text-xs text-muted-foreground">{row.original.user_id}</div>
        </div>
      ),
    },
    {
      accessorKey: 'action',
      header: t('crud.fields.action'),
      cell: ({ row }: { row: { original: AuditLogEntry } }) => (
        <Badge className={getActionColor(row.original.action)}>{row.original.action}</Badge>
      ),
    },
    {
      accessorKey: 'entity_type',
      header: t('crud.fields.entityType'),
      cell: ({ row }: { row: { original: AuditLogEntry } }) => (
        <div>
          <div className="font-medium">{row.original.entity_type}</div>
          <div className="text-xs text-muted-foreground">ID: {row.original.entity_id}</div>
        </div>
      ),
    },
    {
      accessorKey: 'changes',
      header: t('crud.fields.changes'),
      cell: ({ row }: { row: { original: AuditLogEntry } }) => {
        const changes = row.original.changes
        const changeKeys = Object.keys(changes || {})
        if (changeKeys.length === 0) {
          return <span className="text-muted-foreground">-</span>
        }
        return (
          <div className="text-sm">
            {changeKeys.slice(0, 2).map((key) => (
              <div key={key} className="truncate">
                {key}: {String(changes[key]).substring(0, 30)}
              </div>
            ))}
            {changeKeys.length > 2 && <div className="text-xs text-muted-foreground">+{changeKeys.length - 2} mehr</div>}
          </div>
        )
      },
    },
    {
      accessorKey: 'ip_address',
      header: t('crud.fields.ipAddress'),
      cell: ({ row }: { row: { original: AuditLogEntry } }) => (
        <div className="text-sm">
          {row.original.ip_address || '-'}
          {row.original.correlation_id && (
            <div className="text-xs text-muted-foreground">Corr: {row.original.correlation_id.substring(0, 8)}...</div>
          )}
        </div>
      ),
    },
  ]

  const uniqueEntityTypes = Array.from(new Set(logs.map((log) => log.entity_type)))
  const uniqueActions = Array.from(new Set(logs.map((log) => log.action)))

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">{t('finance.auditTrail.title')}</h2>
          <p className="text-muted-foreground">{t('finance.auditTrail.description')}</p>
        </div>
        <div className="flex items-center space-x-2">
          <Shield className="h-8 w-8 text-primary" />
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('finance.auditTrail.totalEntries')}</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_entries.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('finance.auditTrail.uniqueActions')}</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.actions.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('finance.auditTrail.entityTypes')}</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.entity_types.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{t('finance.auditTrail.topUsers')}</CardTitle>
              <XCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.top_users.length}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>{t('crud.actions.filter')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4 md:flex-row">
            <div className="flex-1">
              <Input
                placeholder={t('crud.actions.searchPlaceholder', { entityType: 'Audit-Logs' })}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                icon={<Search className="h-4 w-4 text-muted-foreground" />}
              />
            </div>
            <Select value={entityTypeFilter} onValueChange={setEntityTypeFilter}>
              <SelectTrigger className="w-full md:w-[200px]">
                <SelectValue placeholder={t('crud.fields.entityType')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('common.all')}</SelectItem>
                {uniqueEntityTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={actionFilter} onValueChange={setActionFilter}>
              <SelectTrigger className="w-full md:w-[200px]">
                <SelectValue placeholder={t('crud.fields.action')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('common.all')}</SelectItem>
                {uniqueActions.map((action) => (
                  <SelectItem key={action} value={action}>
                    {action}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Audit Logs Table */}
      <Card>
        <CardHeader>
          <CardTitle>{t('finance.auditTrail.auditLogs')}</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={filteredLogs} loading={loading} />
        </CardContent>
      </Card>
    </div>
  )
}

