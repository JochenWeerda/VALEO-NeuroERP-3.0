import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, Search, Truck } from 'lucide-react'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { useLieferungen, type Lieferung, type LieferungStatus } from '@/lib/api/sales'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

const statusVariantMap: Record<LieferungStatus, 'default' | 'outline' | 'secondary' | 'destructive'> = {
  geplant: 'default',
  unterwegs: 'secondary',
  zugestellt: 'outline',
  storniert: 'destructive',
}

type DeliveryListRoleFocus = 'all' | 'shipping' | 'sales' | 'logistics' | 'billing' | 'management'

const deliveryListRoleProfiles: Array<{ id: DeliveryListRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle Rollen', description: 'Zeigt Lieferungen fuer Versand, Vertrieb, Logistik, Faktura und Leitung.' },
  { id: 'shipping', label: 'Versand', description: 'Fokus auf geplante und unterwegs befindliche Lieferungen.' },
  { id: 'sales', label: 'Vertrieb', description: 'Fokus auf Kunde, Auftragsbezug und Lieferstatus.' },
  { id: 'logistics', label: 'Logistik', description: 'Fokus auf Tour-/Auslieferdruck und Zustellung.' },
  { id: 'billing', label: 'Faktura', description: 'Fokus auf zugestellte Lieferungen und Rechnungsfolge.' },
  { id: 'management', label: 'Leitung', description: 'Fokus auf Stopper, offene Lieferungen und naechste Aktion.' },
]

export default function LieferungenListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const entityType = 'delivery'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Lieferung')
  const pageTitle = getListTitle(t, entityTypeLabel)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<LieferungStatus | 'alle'>('alle')
  const [roleFocus, setRoleFocus] = useState<DeliveryListRoleFocus>('all')

  const { data: lieferungen = [] } = useLieferungen()

  const filteredLieferungen = lieferungen.filter((lieferung) => {
    const matchesSearch =
      lieferung.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lieferung.kunde.toLowerCase().includes(searchTerm.toLowerCase()) ||
      lieferung.auftragsNr.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || lieferung.status === statusFilter
    return matchesSearch && matchesStatus
  })
  const plannedCount = filteredLieferungen.filter((lieferung) => lieferung.status === 'geplant').length
  const transitCount = filteredLieferungen.filter((lieferung) => lieferung.status === 'unterwegs').length
  const deliveredCount = filteredLieferungen.filter((lieferung) => lieferung.status === 'zugestellt').length
  const cancelledCount = filteredLieferungen.filter((lieferung) => lieferung.status === 'storniert').length
  const deliveryListReady = filteredLieferungen.length > 0 && cancelledCount === 0
  const deliveryListNextAction = transitCount > 0
    ? 'Lieferungen unterwegs nachhalten und Zustellung bestaetigen.'
    : plannedCount > 0
      ? 'Geplante Lieferungen disponieren oder starten.'
      : deliveredCount > 0
        ? 'Zugestellte Lieferungen fuer Faktura pruefen.'
        : filteredLieferungen.length === 0
          ? 'Filter anpassen oder neuen Lieferschein anlegen.'
          : 'Stornierte Lieferungen pruefen.'
  const deliveryListTaskItems: UxTaskItem[] = [
    { label: 'Lieferbestand pruefen', done: filteredLieferungen.length > 0, hint: `${filteredLieferungen.length} Lieferungen in der aktuellen Sicht.` },
    { label: 'Versand priorisieren', done: plannedCount === 0, hint: plannedCount > 0 ? `${plannedCount} Lieferungen sind geplant.` : 'Keine geplante Lieferung in der Sicht.' },
    { label: 'Zustellung nachhalten', done: transitCount === 0, hint: transitCount > 0 ? `${transitCount} Lieferungen sind unterwegs.` : 'Keine Lieferung unterwegs.' },
    { label: 'Faktura vorbereiten', done: deliveredCount > 0, hint: deliveredCount > 0 ? `${deliveredCount} Lieferungen sind zugestellt.` : 'Noch keine zugestellte Lieferung fuer Faktura.' },
  ]
  const deliveryListCrudCapabilities = [
    { key: 'create', label: 'Anlegen', available: true, hint: 'Neue Lieferung kann aus der Liste angelegt werden.' },
    { key: 'read', label: 'Lesen', available: true, hint: 'Liefernummer, Datum, Kunde, Auftrag, Menge und Status sind sichtbar.' },
    { key: 'update', label: 'Bearbeiten', available: filteredLieferungen.length > 0, hint: 'Lieferungen koennen im Editor geoeffnet werden.' },
    { key: 'filter', label: 'Suchen/Filtern', available: true, hint: 'Suche und Statusfilter grenzen die Liste ein.' },
    { key: 'export', label: 'Export/Nachweis', available: filteredLieferungen.length > 0, hint: 'Exportaktion ist vorbereitet; Nachweis basiert auf Liefernummer und Auftragsbezug.' },
    { key: 'audit', label: 'Pruefspur', available: true, hint: 'Status, Auftrag, Kunde und Lieferung bilden die operative Pruefspur.' },
  ]

  const columns = [
    {
      key: 'nummer' as const,
      label: t('crud.fields.number'),
      render: (lieferung: Lieferung) => (
        <button
          onClick={() => navigate(`/sales/delivery-editor?id=${lieferung.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {lieferung.nummer}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: t('crud.fields.deliveryDate'),
      render: (lieferung: Lieferung) => new Date(lieferung.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kunde' as const,
      label: t('crud.entities.customer'),
    },
    {
      key: 'auftragsNr' as const,
      label: t('crud.entities.salesOrder'),
      render: (lieferung: Lieferung) => (
        <button
          onClick={() => navigate(`/sales/order-editor?id=${lieferung.auftragsNr}`)}
          className="text-sm text-blue-600 hover:underline"
        >
          {lieferung.auftragsNr}
        </button>
      ),
    },
    {
      key: 'menge' as const,
      label: t('crud.fields.items'),
    },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (lieferung: Lieferung) => (
        <Badge variant={statusVariantMap[lieferung.status]}>{getStatusLabel(t, lieferung.status, lieferung.status)}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{pageTitle}</h1>
          <p className="text-muted-foreground">{t('crud.list.overview', { entityType: entityTypeLabel })}</p>
        </div>
        <Button onClick={() => navigate('/sales/delivery-editor')} className="gap-2">
          <Truck className="h-4 w-4" />
          {t('crud.actions.new')} {entityTypeLabel}
        </Button>
      </div>

      <div className="space-y-4">
        <RoleFocusBar roles={deliveryListRoleProfiles} value={roleFocus} onChange={setRoleFocus} visibleCount={roleFocus === 'all' ? 5 : 1} totalCount={5} />
        <ManagementDecisionPanel
          decision={{
            allowed: deliveryListReady,
            allowedLabel: 'Liefersteuerung arbeitsfaehig',
            blockedLabel: 'Klaerungsbedarf',
            summary: deliveryListReady ? `${filteredLieferungen.length} Lieferungen sichtbar, ${transitCount} unterwegs, ${deliveredCount} zugestellt.` : `Vor der Lieferentscheidung ist noch etwas offen: ${deliveryListNextAction}`,
            blockerCount: [filteredLieferungen.length === 0, cancelledCount > 0].filter(Boolean).length,
            nextFocus: deliveryListNextAction,
            template: { label: 'Rechnungsliste oeffnen', href: '/sales/rechnungen' },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan title="Liefer-Prioritaetsplan" items={deliveryListTaskItems} />
          <div className="space-y-3">
            <NextActionPanel action={deliveryListNextAction} tone={deliveryListReady ? 'emerald' : transitCount > 0 || plannedCount > 0 ? 'amber' : 'blue'} />
            <EvidenceTemplateLink link={{ label: 'Auftragsliste pruefen', href: '/sales/auftraege' }} />
          </div>
        </div>
        <CrudCapabilityChecklist capabilities={deliveryListCrudCapabilities} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('crud.actions.filter')} & {t('crud.actions.search')}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder={`${t('crud.actions.search')  }...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as Lieferung['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">{t('crud.list.allStatus', { defaultValue: 'Alle Status' })}</option>
              <option value="geplant">{t('status.planned')}</option>
              <option value="unterwegs">{t('status.inTransit')}</option>
              <option value="zugestellt">{t('status.delivered')}</option>
              <option value="storniert">{t('status.cancelled')}</option>
            </select>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              {t('crud.actions.export')}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredLieferungen} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {t('crud.list.showing', { count: filteredLieferungen.length, total: lieferungen.length, entityType: entityTypeLabel })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
