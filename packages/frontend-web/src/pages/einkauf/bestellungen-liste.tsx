import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ListReport } from '@/components/mask-builder'
import { useMaskActions } from '@/components/mask-builder/hooks'
import { formatDate, formatNumber } from '@/components/mask-builder/utils/formatting'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ListConfig } from '@/components/mask-builder/types'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { usePurchaseOrders, useApprovePurchaseOrder, useCancelPurchaseOrder, INCOTERM_OPTIONS } from '@/lib/api/purchase-orders'
import { apiClient } from '@/lib/api-client'

// Konfiguration für Bestellungen ListReport (wird in Komponente mit i18n erstellt)
const createBestellungenConfig = (
  t: any,
  entityTypeLabel: string,
  onBulkPrint?: () => void,
  onBulkApprove?: (items: any[]) => void,
  onBulkCancel?: (items: any[]) => void,
): ListConfig => ({
  title: entityTypeLabel,
  titleKey: 'crud.list.title',
  subtitle: t('crud.subtitles.managePurchaseOrders'),
  subtitleKey: 'crud.subtitles.managePurchaseOrders',
  type: 'list-report',
  columns: [
    {
      key: 'purchaseOrderNumber',
      label: t('crud.fields.orderNumber'),
      labelKey: 'crud.fields.orderNumber',
      sortable: true,
      render: (value) => <code className="text-sm font-mono">{value}</code>
    },
    {
      key: 'subject',
      label: t('crud.entities.supplier'),
      labelKey: 'crud.entities.supplier',
      sortable: true,
      filterable: true
    },
    {
      key: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      sortable: true,
      filterable: true,
      render: (value) => {
        const statusLabel = getStatusLabel(t, value as string, value as string)
        const variants: Record<string, 'secondary' | 'default' | 'outline' | 'destructive'> = {
          'ENTWURF': 'secondary',
          'FREIGEGEBEN': 'default',
          'BESTELLT': 'default',
          'TEILGELIEFERT': 'secondary',
          'GELIEFERT': 'outline',
          'STORNIERT': 'destructive'
        }
        return <Badge variant={variants[value as string] || 'secondary'}>{statusLabel}</Badge>
      }
    },
    {
      key: 'incoterms',
      label: 'Incoterms',
      labelKey: 'crud.fields.incoterms',
      sortable: true,
      render: (value) => {
        if (!value) return <span className="text-muted-foreground">–</span>
        const option = INCOTERM_OPTIONS.find(o => o.value === value)
        return <span title={option?.label}>{value as string}</span>
      }
    },
    {
      key: 'deliveryDate',
      label: t('crud.fields.deliveryDate'),
      labelKey: 'crud.fields.deliveryDate',
      sortable: true,
      render: (value) => formatDate(value)
    },
    {
      key: 'totalAmount',
      label: t('crud.fields.totalAmount'),
      labelKey: 'crud.fields.totalAmount',
      sortable: true,
      render: (value) => `${formatNumber(value, 2)} €`
    },
    {
      key: 'externalReference',
      label: 'Ext. Referenz',
      labelKey: 'crud.fields.externalReference',
      sortable: true,
      render: (value) => value ? <span className="text-xs font-mono">{value as string}</span> : <span className="text-muted-foreground">–</span>
    },
  ],
  filters: [
    {
      name: 'status',
      label: t('crud.fields.status'),
      labelKey: 'crud.fields.status',
      type: 'select',
      options: [
        { value: 'ENTWURF', label: t('status.draft'), labelKey: 'status.draft' },
        { value: 'FREIGEGEBEN', label: t('status.approved'), labelKey: 'status.approved' },
        { value: 'BESTELLT', label: 'Bestellt', labelKey: 'status.ordered' },
        { value: 'TEILGELIEFERT', label: t('status.partial'), labelKey: 'status.partial' },
        { value: 'GELIEFERT', label: 'Geliefert', labelKey: 'status.delivered' },
        { value: 'STORNIERT', label: t('status.cancelled'), labelKey: 'status.cancelled' }
      ]
    },
    {
      name: 'search',
      label: t('crud.entities.supplier'),
      labelKey: 'crud.entities.supplier',
      type: 'text'
    }
  ],
  bulkActions: [
    {
      key: 'freigeben',
      label: t('crud.actions.approve'),
      labelKey: 'crud.actions.approve',
      type: 'primary',
      onClick: (items) => { onBulkApprove?.(items ?? []) }
    },
    {
      key: 'stornieren',
      label: t('crud.actions.cancel'),
      labelKey: 'crud.actions.cancel',
      type: 'danger',
      onClick: (items) => { onBulkCancel?.(items ?? []) }
    },
    {
      key: 'drucken',
      label: t('crud.actions.print'),
      labelKey: 'crud.actions.print',
      type: 'secondary',
      onClick: (items) => { onBulkPrint?.(items ?? []) }
    }
  ],
  defaultSort: { field: 'createdAt', direction: 'desc' },
  pageSize: 25,
  api: {
    baseUrl: '/api/v1/purchase-orders',
    endpoints: {
      list: '/api/v1/purchase-orders',
      get: '/api/v1/purchase-orders/{id}',
      create: '/api/v1/purchase-orders',
      update: '/api/v1/purchase-orders/{id}',
      delete: '/api/v1/purchase-orders/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write'],
  actions: []
})

export default function BestellungenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entityType = 'purchaseOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bestellung')
  const handleBulkPrint = (items: any[]) => {
    if (!items?.length) {
      toast({ title: t('crud.actions.print'), description: 'Bitte Bestellungen auswählen.', variant: 'destructive' })
      return
    }
    const rows = items.map((o: any) =>
      `<tr><td>${o.purchaseOrderNumber ?? o.id}</td><td>${o.supplier ?? o.subject ?? ''}</td><td>${o.status ?? ''}</td><td>${o.deliveryDate ? new Date(o.deliveryDate).toLocaleDateString('de-DE') : ''}</td><td>${o.totalAmount != null ? Number(o.totalAmount).toFixed(2) : ''} €</td></tr>`
    ).join('')
    const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>Bestellungen</title></head><body><h1>Bestellungen (${items.length})</h1><table border="1" cellpadding="4"><thead><tr><th>Bestellnr.</th><th>Lieferant</th><th>Status</th><th>Lieferdatum</th><th>Betrag</th></tr></thead><tbody>${rows}</tbody></table><p style="margin-top:1em">Erstellt: ${new Date().toLocaleString('de-DE')}</p></body></html>`
    const w = window.open('', '_blank')
    if (w) {
      w.document.write(html)
      w.document.close()
      w.focus()
      w.print()
      w.close()
      toast({ title: t('crud.actions.print'), description: `${items.length} Bestellung(en) zum Drucken geöffnet.` })
    } else {
      toast({ title: t('crud.actions.print'), description: 'Pop-up blockiert. Bitte Pop-ups erlauben und erneut versuchen.', variant: 'destructive' })
    }
  }
  const handleBulkApprove = async (items: any[]) => {
    if (items.length === 0) return
    for (const item of items) {
      try {
        await approveMutation.mutateAsync(item.id)
        toast({ title: 'Bestellung freigegeben', description: item.purchaseOrderNumber })
      } catch {
        toast({ variant: 'destructive', title: t('crud.messages.updateError', { entityType: entityTypeLabel }), description: item.purchaseOrderNumber })
      }
    }
    if (items.length > 1) toast({ title: 'Bulk-Freigabe', description: `${items.length} Bestellungen freigegeben.` })
  }
  const handleBulkCancel = async (items: any[]) => {
    if (items.length === 0) return
    const reason = prompt(`Stornierungsgrund für ${items.length} Bestellung(en):`)
    if (!reason) return
    for (const item of items) {
      try {
        await cancelMutation.mutateAsync({ id: item.id, reason })
        toast({ title: 'Bestellung storniert', description: item.purchaseOrderNumber })
      } catch {
        toast({ variant: 'destructive', title: t('crud.messages.updateError', { entityType: entityTypeLabel }), description: item.purchaseOrderNumber })
      }
    }
    if (items.length > 1) toast({ title: 'Bulk-Storno', description: `${items.length} Bestellungen storniert.` })
  }
  const bestellungenConfig = createBestellungenConfig(t, entityTypeLabel, handleBulkPrint, handleBulkApprove, handleBulkCancel)

  const { data: orders, isLoading, refetch } = usePurchaseOrders()
  const approveMutation = useApprovePurchaseOrder()
  const cancelMutation = useCancelPurchaseOrder()

  const data = orders ?? []

  const { handleAction } = useMaskActions(async (action: string, item: any) => {
    if (action === 'edit' && item) {
      navigate(`/einkauf/bestellungen/${item.id}`)
    } else if (action === 'freigeben' && item) {
      try {
        await approveMutation.mutateAsync(item.id)
        toast({ title: 'Bestellung freigegeben' })
      } catch {
        toast({ variant: 'destructive', title: t('crud.messages.updateError', { entityType: entityTypeLabel }) })
      }
    } else if (action === 'stornieren' && item) {
      const reason = prompt('Stornierungsgrund:')
      if (reason) {
        try {
          await cancelMutation.mutateAsync({ id: item.id, reason })
          toast({ title: 'Bestellung storniert' })
        } catch {
          toast({ variant: 'destructive', title: t('crud.messages.updateError', { entityType: entityTypeLabel }) })
        }
      }
    }
  })

  const handleCreate = () => {
    navigate('/einkauf/bestellungen/neu')
  }

  const handleEdit = (item: any) => {
    handleAction('edit', item)
  }

  const [importOpen, setImportOpen] = useState(false)
  const [importFile, setImportFile] = useState<File | null>(null)
  const [importSubmitting, setImportSubmitting] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleImportClick = () => setImportOpen(true)

  const handleImportSubmit = async () => {
    if (!importFile) {
      toast({ variant: 'destructive', title: t('crud.messages.importInfo'), description: 'Bitte eine Datei wählen.' })
      return
    }
    setImportSubmitting(true)
    try {
      const formData = new FormData()
      formData.append('file', importFile)
      const res = await apiClient.post<{ received: number; message?: string }>(
        '/api/v1/einkauf/bestellungen/import',
        formData,
      )
      const received = res?.data?.received ?? 0
      toast({
        title: t('crud.messages.importInfo'),
        description: res?.data?.message ?? `${received} Zeilen empfangen. Import in Verarbeitung.`,
      })
      setImportOpen(false)
      setImportFile(null)
      refetch()
    } catch (err: any) {
      toast({
        variant: 'destructive',
        title: 'Import fehlgeschlagen',
        description: err?.response?.data?.detail ?? err?.message ?? String(err),
      })
    } finally {
      setImportSubmitting(false)
    }
  }

  const handleExport = () => {
    try {
      const csvHeader = `Bestellnr.;Betreff;Status;Incoterms;Liefertermin;Gesamtbetrag;Ext. Referenz\n`
      const csvContent = data.map((po) =>
        `"${po.purchaseOrderNumber}";"${po.subject}";"${po.status}";"${po.incoterms ?? ''}";"${po.deliveryDate}";"${po.totalAmount}";"${po.externalReference ?? ''}"`
      ).join('\n')

      const blob = new Blob([csvHeader + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `Bestellungen-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: t('crud.messages.exportSuccess'),
        description: t('crud.messages.exportedItems', { count: data.length, entityType: entityTypeLabel }),
      })
    } catch {
      toast({ variant: 'destructive', title: t('crud.messages.exportError') })
    }
  }

  return (
    <>
      <ListReport
        config={bestellungenConfig}
        data={data}
        total={data.length}
        onCreate={handleCreate}
        onEdit={handleEdit}
        onExport={handleExport}
        onImport={handleImportClick}
        isLoading={isLoading}
      />
      <Dialog open={importOpen} onOpenChange={setImportOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>{t('crud.messages.importInfo')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>CSV/Excel (Bestellungen)</Label>
              <Input
                type="file"
                accept=".csv,.xlsx,.xls"
                ref={fileInputRef}
                onChange={(e) => setImportFile(e.target.files?.[0] ?? null)}
                className="mt-1"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setImportOpen(false)}>Abbrechen</Button>
            <Button onClick={handleImportSubmit} disabled={importSubmitting || !importFile}>
              {importSubmitting ? 'Importiere…' : 'Import starten'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}


