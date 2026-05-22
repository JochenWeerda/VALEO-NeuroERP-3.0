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
import { escapeHtml } from '@/lib/export-utils'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

// Konfiguration für Bestellungen ListReport (wird in Komponente mit i18n erstellt)
type PurchaseRoleFocus = 'all' | 'procurement' | 'goods-receipt' | 'finance' | 'supplier' | 'management'

const purchaseRoleProfiles: Array<{ id: PurchaseRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt Bestellarbeit fuer Einkauf, Wareneingang, Finance, Lieferant und Leitung.',
  },
  {
    id: 'procurement',
    label: 'Einkauf',
    description: 'Fokus auf Entwurf, Freigabe, Liefertermin und Lieferantenkommunikation.',
  },
  {
    id: 'goods-receipt',
    label: 'Wareneingang',
    description: 'Fokus auf bestellte, teilgelieferte und gelieferte Mengen.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Fokus auf Bestellwert, Freigabe und spaeteren Rechnungsabgleich.',
  },
  {
    id: 'supplier',
    label: 'Lieferant',
    description: 'Fokus auf externe Referenz, Incoterms, Liefertermin und Bestellstatus.',
  },
  {
    id: 'management',
    label: 'Leitung',
    description: 'Fokus auf Rueckstand, Wert und Entscheidungsbedarf.',
  },
]

const createBestellungenConfig = (
  t: any,
  entityTypeLabel: string,
  onBulkPrint?: (items: any[]) => void,
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
        { value: 'BESTELLT', label: 'Bestellt' },
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
  const [roleFocus, setRoleFocus] = useState<PurchaseRoleFocus>('all')
  const handleBulkPrint = (items: any[]) => {
    if (!items?.length) {
      toast({ title: t('crud.actions.print'), description: 'Bitte Bestellungen auswählen.', variant: 'destructive' })
      return
    }
    const rows = items.map((o: any) =>
      `<tr><td>${escapeHtml(o.purchaseOrderNumber ?? o.id)}</td><td>${escapeHtml(o.supplier ?? o.subject ?? '')}</td><td>${escapeHtml(o.status ?? '')}</td><td>${escapeHtml(o.deliveryDate ? new Date(o.deliveryDate).toLocaleDateString('de-DE') : '')}</td><td>${escapeHtml(o.totalAmount != null ? `${Number(o.totalAmount).toFixed(2)} EUR` : '')}</td></tr>`
    ).join('')
    const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>Bestellungen</title></head><body><h1>Bestellungen (${items.length})</h1><table border="1" cellpadding="4"><thead><tr><th>Bestellnr.</th><th>Lieferant</th><th>Status</th><th>Lieferdatum</th><th>Betrag</th></tr></thead><tbody>${rows}</tbody></table><p style="margin-top:1em">Erstellt: ${escapeHtml(new Date().toLocaleString('de-DE'))}</p></body></html>`
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
  const draftCount = data.filter((order: any) => order.status === 'ENTWURF').length
  const approvedCount = data.filter((order: any) => order.status === 'FREIGEGEBEN').length
  const orderedCount = data.filter((order: any) => order.status === 'BESTELLT').length
  const partialCount = data.filter((order: any) => order.status === 'TEILGELIEFERT').length
  const deliveredCount = data.filter((order: any) => order.status === 'GELIEFERT').length
  const cancelledCount = data.filter((order: any) => order.status === 'STORNIERT').length
  const totalAmount = data.reduce((sum: number, order: any) => sum + Number(order.totalAmount || 0), 0)
  const today = new Date().toISOString().split('T')[0]
  const overdueCount = data.filter((order: any) =>
    order.deliveryDate && new Date(order.deliveryDate).toISOString().split('T')[0] < today && !['GELIEFERT', 'STORNIERT'].includes(String(order.status)),
  ).length
  const activeCount = data.length - cancelledCount
  const nextPurchaseAction = overdueCount > 0
    ? 'Ueberfaellige Liefertermine mit Lieferant und Wareneingang klaeren.'
    : draftCount > 0
      ? 'Entwuerfe pruefen und freigeben.'
      : approvedCount > 0
        ? 'Freigegebene Bestellungen an Lieferanten senden oder drucken.'
        : orderedCount + partialCount > 0
          ? 'Bestellte und teilgelieferte Positionen im Wareneingang nachhalten.'
          : 'Neue Bestellung anlegen oder Import starten.'
  const purchaseTaskItems: UxTaskItem[] = [
    {
      label: 'Bestellung erfassen',
      done: data.length > 0,
      hint: data.length > 0 ? `${data.length} Bestellungen in der aktuellen Sicht.` : 'Neue Bestellung anlegen oder Import starten.',
    },
    {
      label: 'Freigeben',
      done: draftCount === 0 && data.length > 0,
      hint: draftCount > 0 ? `${draftCount} Entwuerfe warten auf Freigabe.` : 'Keine offenen Entwuerfe in der Sicht.',
    },
    {
      label: 'Bestellen und Liefern',
      done: orderedCount + partialCount + deliveredCount > 0,
      hint: orderedCount + partialCount > 0 ? `${orderedCount + partialCount} Bestellungen brauchen Liefernachlauf.` : 'Keine bestellte, offene Lieferung in der Sicht.',
    },
    {
      label: 'Nachweis und Export sichern',
      done: deliveredCount > 0,
      hint: deliveredCount > 0 ? `${deliveredCount} Bestellungen sind geliefert.` : 'Druck, Export oder Liefernachweis nach Freigabe sichern.',
    },
  ]
  const purchaseCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen',
      available: true,
      hint: 'Neue Bestellungen koennen direkt aus der Liste angelegt werden.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Bestellnummer, Lieferant, Status, Incoterms, Liefertermin und Betrag sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Bearbeiten',
      available: data.length > 0,
      hint: 'Bestellungen koennen aus der Liste geoeffnet und bearbeitet werden.',
    },
    {
      key: 'delete',
      label: 'Storno',
      available: activeCount > 0,
      hint: 'Storno ist als gefuehrte Bulk-Aktion vorhanden; direktes Loeschen ist kein Standardpfad.',
    },
    {
      key: 'approve',
      label: 'Freigeben',
      available: draftCount > 0 || approvedCount > 0,
      hint: 'Bulk-Freigabe und Druck der freigegebenen Bestellungen sind angebunden.',
    },
    {
      key: 'export',
      label: 'Export/Import',
      available: true,
      hint: 'CSV/Excel-Import, CSV-Export und Druck sind an der Liste verfuegbar.',
    },
    {
      key: 'audit',
      label: 'Nachverfolgung',
      available: true,
      hint: 'Status, Liefertermin, externe Referenz und Betrag bilden die Bestellspur.',
    },
  ]

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
      const received = res?.received ?? 0
      toast({
        title: t('crud.messages.importInfo'),
        description: res?.message ?? `${received} Zeilen empfangen. Import in Verarbeitung.`,
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
    <div className="space-y-6">
      <RoleFocusBar
        roles={purchaseRoleProfiles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={roleFocus === 'all' ? 5 : 1}
        totalCount={5}
      />
      <ManagementDecisionPanel
        decision={{
          allowed: data.length > 0 && overdueCount === 0,
          allowedLabel: 'Bestellarbeit stabil',
          blockedLabel: data.length === 0 ? 'Keine Bestellung' : 'Liefertermin pruefen',
          summary: data.length > 0
            ? `Die aktuelle Sicht enthaelt ${data.length} Bestellungen mit ${formatNumber(totalAmount, 2)} EUR Bestellwert. ${nextPurchaseAction}`
            : 'In der aktuellen Sicht gibt es keine Bestellungen. Legen Sie eine neue Bestellung an oder starten Sie den Import.',
          blockerCount: data.length === 0 ? 1 : overdueCount,
          nextFocus: nextPurchaseAction,
          template: {
            label: 'Bestellung anlegen',
            href: '/einkauf/bestellungen/neu',
          },
        }}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTaskPlan title="Bestell-Follow-up-Plan" items={purchaseTaskItems} />
        <NextActionPanel
          action={nextPurchaseAction}
          tone={overdueCount > 0 ? 'red' : draftCount + approvedCount + orderedCount + partialCount > 0 ? 'amber' : data.length > 0 ? 'blue' : 'red'}
        />
      </div>
      <CrudCapabilityChecklist capabilities={purchaseCrudCapabilities} />
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
    </div>
  )
}


