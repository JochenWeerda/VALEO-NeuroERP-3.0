import { useState, useEffect, useMemo, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { formatCurrency, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { ListConfig } from '@/components/mask-builder/types'
import { toast } from '@/hooks/use-toast'
import { api } from '@/lib/axios'

// API Client für Debitoren (Liste)
const apiClient = createApiClient('/api/v1/finance')

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
    { key: 'export', label: t('crud.actions.export'), type: 'secondary', onClick: () => {} },
    { key: 'reminder', label: t('crud.actions.paymentReminder'), type: 'secondary', onClick: () => {} },
    { key: 'dunning', label: t('crud.actions.sendDunning'), type: 'danger', onClick: () => {} },
    { key: 'block', label: t('crud.actions.blockPayment'), type: 'danger', onClick: () => {} },
  ],
  defaultSort: { field: 'offenerBetrag', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/finance/debtors',
    endpoints: {
      list: '/api/v1/finance/debtors',
      get: '/api/v1/finance/debtors/{id}',
      create: '/api/v1/finance/debtors',
      update: '/api/v1/finance/debtors/{id}',
      delete: '/api/v1/finance/debtors/{id}'
    }
  },
  permissions: ['finance.read', 'debtor.read'],
  actions: []
})

async function triggerExportDownload(entity: string, format: string, toastFn: (opts: { title: string; description?: string; variant?: 'destructive' }) => void): Promise<void> {
  try {
    const res = await api.post('/api/v1/export/list', { entity, format }, { responseType: 'blob' })
    const blob = res.data as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `export_${entity}_${new Date().toISOString().slice(0, 10)}.${format === 'xlsx' ? 'xlsx' : 'csv'}`
    a.click()
    URL.revokeObjectURL(url)
    toastFn({ title: 'Export erstellt', description: 'Download gestartet.' })
  } catch (e: any) {
    toastFn({ title: 'Export fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
  }
}

export default function DebitorenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const importInputRef = useRef<HTMLInputElement>(null)
  const [data, setData] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const baseConfig = createDebitorenListConfig(t) as ListConfig & {
    bulkActions: NonNullable<ListConfig['bulkActions']>
  }

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
      navigate(`/finance/debitoren/${item.id}`)
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
    } catch (error: any) {
      toast({ variant: 'destructive', title: t('crud.messages.loadDataError'), description: error?.message })
    } finally {
      setLoading(false)
    }
  }

  const debitorenListConfig = useMemo(() => {
    const onExportBulk = async () => {
      await triggerExportDownload('debtors', 'csv', toast)
    }
    const onReminder = async (items: any[]) => {
      if (items.length === 0) { toast({ title: t('crud.list.noSelection') ?? 'Keine Auswahl' }); return }
      toast({ title: 'Zahlungserinnerung', description: `Für ${items.length} Debitoren wird Erinnerung erstellt.` })
    }
    const onDunning = async (items: any[]) => {
      if (items.length === 0) { toast({ title: t('crud.list.noSelection') ?? 'Keine Auswahl' }); return }
      try {
        await api.post('/api/v1/finance/dunning/run', { as_of_date: new Date().toISOString().slice(0, 10) })
        toast({ title: 'Mahnlauf gestartet', description: 'Mahnungen werden erstellt.' })
        loadData()
      } catch (e: any) {
        toast({ title: 'Fehler', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
      }
    }
    const onBlock = async (items: any[]) => {
      if (items.length === 0) { toast({ title: t('crud.list.noSelection') ?? 'Keine Auswahl' }); return }
      try {
        for (const item of items) {
          if (item.id) await api.patch(`/api/v1/finance/debtors/${item.id}`, { is_active: false })
        }
        toast({ title: 'Gesperrt', description: `${items.length} Debitor(en) gesperrt.`, variant: 'destructive' })
        loadData()
      } catch (e: any) {
        toast({ title: 'Fehler', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
      }
    }
    const bulkActions = baseConfig.bulkActions ?? []
    return {
      ...baseConfig,
      bulkActions: bulkActions.length >= 4 ? [
        { ...bulkActions[0], onClick: onExportBulk },
        { ...bulkActions[1], onClick: onReminder },
        { ...bulkActions[2], onClick: onDunning },
        { ...bulkActions[3], onClick: onBlock },
      ] : [],
    }
  }, [t])

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
    if (!confirm(t('crud.messages.confirmDeleteDebtor', { name: item.kunde }))) return
    void withPending(String(item.id), async () => {
      try {
        await apiClient.delete(`/debitoren/${item.id}`)
        loadData()
      } catch {
        toast({ title: t('common.error', { defaultValue: 'Fehler' }), description: t('crud.messages.deleteError', { defaultValue: 'Löschen fehlgeschlagen.' }), variant: 'destructive' })
      }
    })
  }

  const handleExport = async () => {
    await triggerExportDownload('debtors', 'csv', toast)
  }

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await api.post('/api/v1/finance/import/debitoren', form, { headers: { 'Content-Type': 'multipart/form-data' } })
      const { created, updated, errors } = res.data as { created: number; updated: number; errors: string[] }
      toast({ title: 'Import abgeschlossen', description: `${created} neu, ${updated} aktualisiert${errors.length ? `, ${errors.length} Fehler` : ''}.` })
      loadData()
    } catch (e: any) {
      toast({ title: 'Import fehlgeschlagen', description: e.response?.data?.detail ?? e.message, variant: 'destructive' })
    }
    e.target.value = ''
  }

  return (
    <>
      <input ref={importInputRef} type="file" accept=".csv" style={{ display: 'none' }} onChange={handleImportFile} />
      <ListReport
        config={debitorenListConfig}
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
    </>
  )
}
