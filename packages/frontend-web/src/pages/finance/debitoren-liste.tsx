import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Debitoren
const apiClient = createApiClient('/api/finance')

// Konfiguration für Debitoren ListReport (wird in Komponente mit i18n erstellt)
const createDebitorenListConfig = (t: any): ListConfig => ({
  title: t('crud.fields.debtorsList'),
  subtitle: t('crud.fields.debtorsListSubtitle'),
  type: 'list-report',
  columns: [
    {
      key: 'kunde',
      label: t('crud.fields.customer'),
      sortable: true,
      filterable: true,
      render: (value, row) => (
        <div>
          <div className="font-medium">{value}</div>
          <div className="text-sm text-muted-foreground">{t('crud.fields.customerNumber')}: {row.kundennummer}</div>
        </div>
      )
    },
    {
      key: 'gesamtForderung',
      label: t('crud.fields.totalClaim'),
      sortable: true,
      render: (value) => formatCurrency(value || 0)
    },
    {
      key: 'offenerBetrag',
      label: t('crud.fields.openAmount'),
      sortable: true,
      render: (value, row) => {
        const overdue = row.mahnstufe > 0
        return (
          <span className={overdue ? 'text-red-600 font-semibold' : ''}>
            {formatCurrency(value || 0)}
          </span>
        )
      }
    },
    {
      key: 'faelligkeit',
      label: t('crud.fields.dueDate'),
      sortable: true,
      render: (value) => {
        if (!value) return '-'
        const date = new Date(value)
        const today = new Date()
        const daysUntil = Math.ceil((date.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

        let color = 'text-gray-600'
        if (daysUntil < 0) color = 'text-red-600'
        else if (daysUntil <= 7) color = 'text-orange-600'
        else if (daysUntil <= 30) color = 'text-blue-600'

        return <span className={color}>{date.toLocaleDateString('de-DE')}</span>
      }
    },
    {
      key: 'mahnstufe',
      label: t('crud.fields.dunningLevel'),
      sortable: true,
      filterable: true,
      render: (value) => {
        const levels = {
          0: { label: t('crud.fields.noDunning'), variant: 'secondary' as const },
          1: { label: t('dunningLevels.1'), variant: 'outline' as const },
          2: { label: t('dunningLevels.2'), variant: 'outline' as const },
          3: { label: t('dunningLevels.3'), variant: 'destructive' as const }
        }
        const level = levels[value as keyof typeof levels] || levels[0]
        return <Badge variant={level.variant}>{level.label}</Badge>
      }
    },
    {
      key: 'letzteZahlung',
      label: t('crud.fields.lastPayment'),
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString('de-DE') : '-'
    },
    {
      key: 'zahlungsart',
      label: t('crud.fields.paymentMethod'),
      filterable: true,
      render: (value) => value || t('crud.fields.invoice')
    },
    {
      key: 'kreditlimit',
      label: t('crud.fields.creditLimit'),
      sortable: true,
      render: (value) => value ? formatCurrency(value) : '-'
    },
    {
      key: 'auslastung',
      label: t('crud.fields.limitUtilization'),
      sortable: true,
      render: (value) => value ? `${formatNumber(value, 1)}%` : '-'
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      sortable: true,
      filterable: true,
      render: (value) => {
        const statuses = {
          'aktiv': { label: t('status.active'), variant: 'default' as const },
          'gesperrt': { label: t('status.locked'), variant: 'destructive' as const },
          'zahlungsziel': { label: t('crud.fields.paymentTerms'), variant: 'secondary' as const }
        }
        const status = statuses[value as keyof typeof statuses] || statuses.aktiv
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    }
  ],
  filters: [
    {
      name: 'status',
      label: t('crud.fields.status'),
      type: 'select',
      options: [
        { value: 'aktiv', label: t('status.active') },
        { value: 'gesperrt', label: t('status.locked') },
        { value: 'zahlungsziel', label: t('crud.fields.paymentTerms') }
      ]
    },
    {
      name: 'mahnstufe',
      label: t('crud.fields.dunningLevel'),
      type: 'select',
      options: [
        { value: '0', label: t('crud.fields.noDunning') },
        { value: '1', label: t('dunningLevels.1') },
        { value: '2', label: t('dunningLevels.2') },
        { value: '3', label: t('dunningLevels.3') }
      ]
    },
    {
      name: 'zahlungsart',
      label: t('crud.fields.paymentMethod'),
      type: 'select',
      options: [
        { value: 'rechnung', label: t('crud.fields.invoice') },
        { value: 'vorkasse', label: t('paymentTerms.prepay') },
        { value: 'nachnahme', label: t('crud.fields.cashOnDelivery') },
        { value: 'lastschrift', label: t('crud.fields.directDebit') }
      ]
    },
    {
      name: 'offenerBetrag',
      label: t('crud.fields.openAmountFrom'),
      type: 'number',
      min: 0
    },
    {
      name: 'offenerBetrag',
      label: t('crud.fields.openAmountTo'),
      type: 'number',
      min: 0
    }
  ],
  bulkActions: [
    {
      key: 'export',
      label: t('crud.actions.export'),
      type: 'secondary',
      onClick: () => console.log('Export clicked')
    },
    {
      key: 'reminder',
      label: t('crud.actions.paymentReminder'),
      type: 'secondary',
      onClick: () => console.log('Reminder clicked')
    },
    {
      key: 'dunning',
      label: t('crud.actions.sendDunning'),
      type: 'danger',
      onClick: () => console.log('Dunning clicked')
    },
    {
      key: 'block',
      label: t('crud.actions.blockPayment'),
      type: 'danger',
      onClick: () => console.log('Block clicked')
    }
  ],
  defaultSort: { field: 'offenerBetrag', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/finance/debitoren',
    endpoints: {
      list: '/api/finance/debitoren',
      get: '/api/finance/debitoren/{id}',
      create: '/api/finance/debitoren',
      update: '/api/finance/debitoren/{id}',
      delete: '/api/finance/debitoren/{id}'
    }
  },
  permissions: ['finance.read', 'debtor.read'],
  actions: []
})

export default function DebitorenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const debitorenListConfig = createDebitorenListConfig(t)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/finance/debitoren/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(t('crud.messages.confirmDeleteDebtor', { name: item.kunde }))) {
        try {
          await apiClient.delete(`/debitoren/${item.id}`)
          loadData() // Liste neu laden
        } catch (error) {
          alert(t('crud.messages.deleteError'))
        }
      }
    }
  })

  const loadData = async () => {
    setLoading(true)
    try {
      const response = await apiClient.get('/debitoren')
      if (response.success) {
        setData((response.data as any).data || [])
        setTotal((response.data as any).total || 0)
      }
    } catch (error) {
      console.error(t('crud.messages.loadDataError'), error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleCreate = () => {
    navigate('/finance/debitoren/new')
  }

  const handleEdit = (item: any) => {
    handleAction('edit', item)
  }

  const handleDelete = (item: any) => {
    handleAction('delete', item)
  }

  const handleExport = () => {
    alert(t('crud.messages.exportFunctionInfo'))
  }

  return (
    <ListReport
      config={debitorenListConfig}
      data={data}
      total={total}
      onCreate={handleCreate}
      onEdit={handleEdit}
      onDelete={handleDelete}
      onExport={handleExport}
      onImport={() => alert(t('crud.messages.importFunctionInfo'))}
      isLoading={loading}
    />
  )
}