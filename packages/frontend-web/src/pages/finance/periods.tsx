/**
 * Accounting Period Management
 * FIBU-GL-05: Periodensteuerung
 * Verwaltung von Buchungsperioden (Öffnen/Sperren)
 */

import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Calendar, Lock, Unlock, Plus, AlertCircle } from 'lucide-react'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import { useToast } from '@/hooks/use-toast'

type AccountingPeriod = {
  id: string
  tenant_id: string
  period: string  // YYYY-MM
  status: 'OPEN' | 'CLOSED' | 'ADJUSTING'
  start_date: string
  end_date: string
  closed_at?: string
  closed_by?: string
  metadata: Record<string, any>
}

export default function PeriodsPage(): JSX.Element {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [periods, setPeriods] = useState<AccountingPeriod[]>([])
  const [loading, setLoading] = useState(true)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isCloseDialogOpen, setIsCloseDialogOpen] = useState(false)
  const [selectedPeriod, setSelectedPeriod] = useState<AccountingPeriod | null>(null)
  const [newPeriod, setNewPeriod] = useState({
    tenant_id: 'default',
    period: '',
    start_date: '',
    end_date: '',
    status: 'OPEN' as const
  })
  const [closeBy, setCloseBy] = useState('')

  useEffect(() => {
    fetchPeriods()
  }, [])

  async function fetchPeriods(): Promise<void> {
    setLoading(true)
    try {
      const response = await fetch('/api/v1/finance/periods?limit=100')
      if (!response.ok) {
        throw new Error('Failed to fetch periods')
      }
      const data: AccountingPeriod[] = await response.json()
      setPeriods(data)
    } catch (error) {
      console.error('Error fetching periods:', error)
      toast({
        title: t('common.error'),
        description: t('crud.feedback.fetchError', { entityType: 'Perioden' }),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  async function createPeriod(): Promise<void> {
    try {
      const response = await fetch('/api/v1/finance/periods', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPeriod),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to create period')
      }

      toast({
        title: t('common.success'),
        description: t('crud.feedback.createSuccess', { entityType: 'Periode' }),
      })
      setIsCreateDialogOpen(false)
      setNewPeriod({ tenant_id: 'default', period: '', start_date: '', end_date: '', status: 'OPEN' })
      await fetchPeriods()
    } catch (error: any) {
      console.error('Error creating period:', error)
      toast({
        title: t('common.error'),
        description: error.message || t('crud.feedback.createError', { entityType: 'Periode' }),
        variant: 'destructive',
      })
    }
  }

  async function closePeriod(): Promise<void> {
    if (!selectedPeriod || !closeBy) return

    try {
      const response = await fetch(`/api/v1/finance/periods/${selectedPeriod.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'CLOSED',
          closed_by: closeBy,
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to close period')
      }

      toast({
        title: t('common.success'),
        description: t('finance.periods.periodClosed', { period: selectedPeriod.period }),
      })
      setIsCloseDialogOpen(false)
      setSelectedPeriod(null)
      setCloseBy('')
      await fetchPeriods()
    } catch (error: any) {
      console.error('Error closing period:', error)
      toast({
        title: t('common.error'),
        description: error.message || t('finance.periods.closeError'),
        variant: 'destructive',
      })
    }
  }

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'OPEN':
        return 'bg-green-100 text-green-800'
      case 'CLOSED':
        return 'bg-red-100 text-red-800'
      case 'ADJUSTING':
        return 'bg-yellow-100 text-yellow-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusLabel = (status: string): string => {
    switch (status) {
      case 'OPEN':
        return t('finance.periods.status.open')
      case 'CLOSED':
        return t('finance.periods.status.closed')
      case 'ADJUSTING':
        return t('finance.periods.status.adjusting')
      default:
        return status
    }
  }

  const columns = [
    {
      accessorKey: 'period',
      header: t('finance.periods.period'),
      cell: ({ row }: { row: { original: AccountingPeriod } }) => (
        <div className="font-medium">{row.original.period}</div>
      ),
    },
    {
      accessorKey: 'start_date',
      header: t('finance.periods.startDate'),
      cell: ({ row }: { row: { original: AccountingPeriod } }) => (
        <div className="text-sm">
          {format(new Date(row.original.start_date), 'dd.MM.yyyy', { locale: de })}
        </div>
      ),
    },
    {
      accessorKey: 'end_date',
      header: t('finance.periods.endDate'),
      cell: ({ row }: { row: { original: AccountingPeriod } }) => (
        <div className="text-sm">
          {format(new Date(row.original.end_date), 'dd.MM.yyyy', { locale: de })}
        </div>
      ),
    },
    {
      accessorKey: 'status',
      header: t('crud.fields.status'),
      cell: ({ row }: { row: { original: AccountingPeriod } }) => (
        <Badge className={getStatusColor(row.original.status)}>
          {getStatusLabel(row.original.status)}
        </Badge>
      ),
    },
    {
      accessorKey: 'closed_by',
      header: t('finance.periods.closedBy'),
      cell: ({ row }: { row: { original: AccountingPeriod } }) => (
        <div className="text-sm">
          {row.original.closed_by || '-'}
          {row.original.closed_at && (
            <div className="text-xs text-muted-foreground">
              {format(new Date(row.original.closed_at), 'dd.MM.yyyy HH:mm', { locale: de })}
            </div>
          )}
        </div>
      ),
    },
    {
      id: 'actions',
      header: t('crud.fields.actions'),
      cell: ({ row }: { row: { original: AccountingPeriod } }) => (
        <div className="flex items-center space-x-2">
          {row.original.status === 'OPEN' && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSelectedPeriod(row.original)
                setIsCloseDialogOpen(true)
              }}
            >
              <Lock className="h-4 w-4 mr-1" />
              {t('finance.periods.close')}
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">{t('finance.periods.title')}</h2>
          <p className="text-muted-foreground">{t('finance.periods.description')}</p>
        </div>
        <div className="flex items-center space-x-2">
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                {t('finance.periods.createPeriod')}
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{t('finance.periods.createPeriod')}</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label>{t('finance.periods.period')} (YYYY-MM)</Label>
                  <Input
                    value={newPeriod.period}
                    onChange={(e) => setNewPeriod({ ...newPeriod, period: e.target.value })}
                    placeholder="2025-01"
                  />
                </div>
                <div>
                  <Label>{t('finance.periods.startDate')}</Label>
                  <Input
                    type="date"
                    value={newPeriod.start_date}
                    onChange={(e) => setNewPeriod({ ...newPeriod, start_date: e.target.value })}
                  />
                </div>
                <div>
                  <Label>{t('finance.periods.endDate')}</Label>
                  <Input
                    type="date"
                    value={newPeriod.end_date}
                    onChange={(e) => setNewPeriod({ ...newPeriod, end_date: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  {t('common.cancel')}
                </Button>
                <Button onClick={createPeriod}>{t('common.create')}</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Info Card */}
      <Card className="border-yellow-200 bg-yellow-50">
        <CardContent className="pt-6">
          <div className="flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-yellow-800">{t('finance.periods.infoTitle')}</p>
              <p className="text-sm text-yellow-700 mt-1">{t('finance.periods.infoDescription')}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Periods Table */}
      <Card>
        <CardHeader>
          <CardTitle>{t('finance.periods.periodsList')}</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={periods} loading={loading} />
        </CardContent>
      </Card>

      {/* Close Period Dialog */}
      <Dialog open={isCloseDialogOpen} onOpenChange={setIsCloseDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t('finance.periods.closePeriod')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {selectedPeriod && (
              <div>
                <p className="text-sm text-muted-foreground mb-2">
                  {t('finance.periods.closeConfirm', { period: selectedPeriod.period })}
                </p>
                <Label>{t('finance.periods.closedBy')}</Label>
                <Input
                  value={closeBy}
                  onChange={(e) => setCloseBy(e.target.value)}
                  placeholder={t('finance.periods.closedByPlaceholder')}
                />
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCloseDialogOpen(false)}>
              {t('common.cancel')}
            </Button>
            <Button onClick={closePeriod} disabled={!closeBy}>
              <Lock className="h-4 w-4 mr-2" />
              {t('finance.periods.close')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

