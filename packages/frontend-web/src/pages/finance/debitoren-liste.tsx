import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'

// API Client für Debitoren
const apiClient = createApiClient('/api/finance')

// Konfiguration für Debitoren ListReport
const debitorenListConfig: ListConfig = {
  title: 'Debitoren-Liste',
  subtitle: 'Übersicht aller Debitoren und offener Forderungen',
  type: 'list-report',
  columns: [
    {
      key: 'kunde',
      label: 'Kunde',
      sortable: true,
      filterable: true,
      render: (value, row) => (
        <div>
          <div className="font-medium">{value}</div>
          <div className="text-sm text-muted-foreground">Kundennr: {row.kundennummer}</div>
        </div>
      )
    },
    {
      key: 'gesamtForderung',
      label: 'Gesamtforderung',
      sortable: true,
      render: (value) => formatCurrency(value || 0)
    },
    {
      key: 'offenerBetrag',
      label: 'Offener Betrag',
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
      label: 'Fälligkeit',
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
      label: 'Mahnstufe',
      sortable: true,
      filterable: true,
      render: (value) => {
        const levels = {
          0: { label: 'Keine', variant: 'secondary' as const },
          1: { label: '1. Mahnung', variant: 'outline' as const },
          2: { label: '2. Mahnung', variant: 'outline' as const },
          3: { label: '3. Mahnung', variant: 'destructive' as const }
        }
        const level = levels[value as keyof typeof levels] || levels[0]
        return <Badge variant={level.variant}>{level.label}</Badge>
      }
    },
    {
      key: 'letzteZahlung',
      label: 'Letzte Zahlung',
      sortable: true,
      render: (value) => value ? new Date(value).toLocaleDateString('de-DE') : '-'
    },
    {
      key: 'zahlungsart',
      label: 'Zahlungsart',
      filterable: true,
      render: (value) => value || 'Rechnung'
    },
    {
      key: 'kreditlimit',
      label: 'Kreditlimit',
      sortable: true,
      render: (value) => value ? formatCurrency(value) : '-'
    },
    {
      key: 'auslastung',
      label: 'Limit-Auslastung',
      sortable: true,
      render: (value) => value ? `${formatNumber(value, 1)}%` : '-'
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statuses = {
          'aktiv': { label: 'Aktiv', variant: 'default' as const },
          'gesperrt': { label: 'Gesperrt', variant: 'destructive' as const },
          'zahlungsziel': { label: 'Zahlungsziel', variant: 'secondary' as const }
        }
        const status = statuses[value as keyof typeof statuses] || statuses.aktiv
        return <Badge variant={status.variant}>{status.label}</Badge>
      }
    }
  ],
  filters: [
    {
      name: 'status',
      label: 'Status',
      type: 'select',
      options: [
        { value: 'aktiv', label: 'Aktiv' },
        { value: 'gesperrt', label: 'Gesperrt' },
        { value: 'zahlungsziel', label: 'Zahlungsziel' }
      ]
    },
    {
      name: 'mahnstufe',
      label: 'Mahnstufe',
      type: 'select',
      options: [
        { value: '0', label: 'Keine Mahnung' },
        { value: '1', label: '1. Mahnung' },
        { value: '2', label: '2. Mahnung' },
        { value: '3', label: '3. Mahnung' }
      ]
    },
    {
      name: 'zahlungsart',
      label: 'Zahlungsart',
      type: 'select',
      options: [
        { value: 'rechnung', label: 'Rechnung' },
        { value: 'vorkasse', label: 'Vorkasse' },
        { value: 'nachnahme', label: 'Nachnahme' },
        { value: 'lastschrift', label: 'Lastschrift' }
      ]
    },
    {
      name: 'offenerBetrag',
      label: 'Offener Betrag von',
      type: 'number',
      min: 0
    },
    {
      name: 'offenerBetrag',
      label: 'Offener Betrag bis',
      type: 'number',
      min: 0
    }
  ],
  bulkActions: [
    {
      key: 'export',
      label: 'Exportieren',
      type: 'secondary',
      onClick: () => console.log('Export clicked')
    },
    {
      key: 'reminder',
      label: 'Zahlungserinnerung',
      type: 'secondary',
      onClick: () => console.log('Reminder clicked')
    },
    {
      key: 'dunning',
      label: 'Mahnung senden',
      type: 'danger',
      onClick: () => console.log('Dunning clicked')
    },
    {
      key: 'block',
      label: 'Zahlung sperren',
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
}

export default function DebitorenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/finance/debitoren/${item.id}`)
    } else if (action === 'delete' && item) {
      if (confirm(`Debitor "${item.kunde}" wirklich löschen?`)) {
        try {
          await apiClient.delete(`/debitoren/${item.id}`)
          loadData() // Liste neu laden
        } catch (error) {
          alert('Fehler beim Löschen')
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
      console.error('Fehler beim Laden der Daten:', error)
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
    alert('Export-Funktion wird implementiert')
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
      onImport={() => alert('Import-Funktion wird implementiert')}
      isLoading={loading}
    />
  )
}