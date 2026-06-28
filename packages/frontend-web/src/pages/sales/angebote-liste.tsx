import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from '@/app/routing/typed-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { FileDown, FileText, Plus, Search } from 'lucide-react'
import { useListActions } from '@/hooks/useListActions'
import { formatDateForExport, formatCurrencyForExport } from '@/lib/export-utils'
import { getEntityTypeLabel, getListTitle, getStatusLabel } from '@/features/crud/utils/i18n-helpers'
import { AdvancedFilters, FilterConfig } from '@/components/list/AdvancedFilters'
import { CSVImport } from '@/components/list/CSVImport'
import { useToast } from '@/hooks/use-toast'
import { saveDocument } from '@/lib/document-api'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useAngebote, type Angebot, type AngebotStatus } from '@/lib/api/sales'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

const statusVariantMap: Record<AngebotStatus, 'default' | 'outline' | 'secondary' | 'destructive'> = {
  offen: 'default',
  angenommen: 'outline',
  abgelehnt: 'destructive',
  abgelaufen: 'secondary',
}

type OfferRoleFocus = 'all' | 'sales' | 'inside-sales' | 'order-desk' | 'finance' | 'management'

const offerRoleProfiles: Array<{ id: OfferRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt die Angebotsarbeit fuer Vertrieb, Inside Sales, Auftragsabwicklung, Finance und Leitung.',
  },
  {
    id: 'sales',
    label: 'Vertrieb',
    description: 'Fokus auf Kunde, Angebotswert, Nachfassen und Abschlusschance.',
  },
  {
    id: 'inside-sales',
    label: 'Inside Sales',
    description: 'Fokus auf offene Angebote, Gueltigkeit, Datenpflege und Wiedervorlage.',
  },
  {
    id: 'order-desk',
    label: 'Auftragsabwicklung',
    description: 'Fokus auf angenommene Angebote und Uebernahme in den Auftrag.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Fokus auf Angebotswert, spaetere Faktura und Export.',
  },
  {
    id: 'management',
    label: 'Leitung',
    description: 'Fokus auf Angebotsvolumen, Ablaufdruck und Entscheidungsbedarf.',
  },
]

export default function AngeboteListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<AngebotStatus | 'alle'>('alle')
  const [showImport, setShowImport] = useState(false)
  const [filterValues, setFilterValues] = useState<Record<string, any>>({})
  const [roleFocus, setRoleFocus] = useState<OfferRoleFocus>('all')

  const entityType = 'offer'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Angebot')

  const { data: angebote = [] } = useAngebote()

  // Filter-Konfiguration für AdvancedFilters
  const filterConfig: FilterConfig[] = [
    {
      key: 'status',
      label: t('crud.fields.status'),
      type: 'select',
      options: [
        { value: 'offen', label: getStatusLabel(t, 'offen', 'Offen') },
        { value: 'angenommen', label: getStatusLabel(t, 'angenommen', 'Angenommen') },
        { value: 'abgelehnt', label: getStatusLabel(t, 'abgelehnt', 'Abgelehnt') },
        { value: 'abgelaufen', label: getStatusLabel(t, 'abgelaufen', 'Abgelaufen') },
      ],
    },
    {
      key: 'datum',
      label: t('crud.fields.date'),
      type: 'date',
    },
    {
      key: 'kunde',
      label: t('crud.entities.customer'),
      type: 'text',
    },
  ]

  const filteredAngebote = angebote.filter((angebot) => {
    const matchesSearch =
      angebot.nummer.toLowerCase().includes(searchTerm.toLowerCase()) ||
      angebot.kunde.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'alle' || angebot.status === statusFilter
    
    // Erweiterte Filter
    if (filterValues.status && angebot.status !== filterValues.status) return false
    if (filterValues.kunde && !angebot.kunde.toLowerCase().includes(filterValues.kunde.toLowerCase())) return false
    if (filterValues.datum) {
      const angebotDate = new Date(angebot.datum).toISOString().split('T')[0]
      if (angebotDate !== filterValues.datum) return false
    }
    
    return matchesSearch && matchesStatus
  })

  const handleImport = async (importData: Record<string, unknown>[]) => {
    try {
      for (const row of importData) {
        // Transformiere CSV-Daten in Dokument-Format
        const doc = {
          number: row.Angebotsnummer || row.number || `ANG-${Date.now()}`,
          date: row.Datum || row.date || new Date().toISOString().split('T')[0],
          customerId: row.Kunde || row.customerId || '',
          status: 'ENTWURF',
          validUntil: row['Gültig bis'] || row.validUntil || '',
          lines: [],
          subtotalNet: 0,
          totalTax: 0,
          totalGross: parseFloat(row.Betrag?.replace(/[^\d,.-]/g, '').replace(',', '.')) || 0,
        }
        await saveDocument('sales_offer', doc)
      }
      toast({
        title: t('crud.messages.importSuccess'),
        description: `${importData.length} Angebote wurden importiert.`,
      })
      // Daten neu laden
      window.location.reload()
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.importError'),
        description: getAxiosErrorMessage(error),
      })
    }
  }

  const exportData = filteredAngebote.map(a => ({
    Angebotsnummer: a.nummer,
    Datum: formatDateForExport(a.datum),
    Kunde: a.kunde,
    Betrag: formatCurrencyForExport(a.betrag),
    'Gültig bis': formatDateForExport(a.gueltigBis),
    Status: getStatusLabel(t, a.status, a.status),
  }))

  const { handleExport, handlePrint } = useListActions({
    data: exportData,
    entityName: 'angebote',
  })

  const total = filteredAngebote.length
  const openCount = filteredAngebote.filter((angebot) => angebot.status === 'offen').length
  const acceptedCount = filteredAngebote.filter((angebot) => angebot.status === 'angenommen').length
  const rejectedCount = filteredAngebote.filter((angebot) => angebot.status === 'abgelehnt').length
  const expiredCount = filteredAngebote.filter((angebot) => angebot.status === 'abgelaufen').length
  const totalAmount = filteredAngebote.reduce((sum, angebot) => sum + Number(angebot.betrag || 0), 0)
  const today = new Date().toISOString().split('T')[0]
  const expiringCount = filteredAngebote.filter((angebot) => {
    if (!angebot.gueltigBis || angebot.status !== 'offen') return false
    const validUntil = new Date(angebot.gueltigBis).toISOString().split('T')[0]
    return validUntil <= today
  }).length
  const nextOfferAction = expiringCount > 0
    ? 'Abgelaufene oder heute faellige Angebote nachfassen.'
    : acceptedCount > 0
      ? 'Angenommene Angebote in Auftraege ueberfuehren.'
      : openCount > 0
        ? 'Offene Angebote nachfassen und Entscheidung sichern.'
        : 'Neues Angebot anlegen oder Import starten.'
  const offerTaskItems: UxTaskItem[] = [
    {
      label: 'Angebot erfassen',
      done: total > 0,
      hint: total > 0 ? `${total} Angebote in der aktuellen Sicht.` : 'Neues Angebot anlegen oder Import starten.',
    },
    {
      label: 'Nachfassen',
      done: openCount > 0 && expiringCount === 0,
      hint: expiringCount > 0 ? `${expiringCount} offene Angebote sind faellig oder abgelaufen.` : `${openCount} offene Angebote nachhalten.`,
    },
    {
      label: 'Entscheidung sichern',
      done: acceptedCount + rejectedCount + expiredCount > 0,
      hint: acceptedCount > 0 ? `${acceptedCount} angenommene Angebote brauchen Folgeauftrag.` : 'Annahme, Ablehnung oder Ablauf im Status festhalten.',
    },
    {
      label: 'In Auftrag ueberfuehren',
      done: acceptedCount > 0,
      hint: acceptedCount > 0 ? `${acceptedCount} Angebote koennen in Auftraege ueberfuehrt werden.` : 'Noch kein angenommenes Angebot in der Sicht.',
    },
  ]
  const offerCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen',
      available: true,
      hint: 'Neue Angebote koennen direkt aus der Liste angelegt werden.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Angebotsnummer, Kunde, Betrag, Gueltigkeit und Status sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Bearbeiten',
      available: total > 0,
      hint: 'Angebote koennen aus der Liste geoeffnet und bearbeitet werden.',
    },
    {
      key: 'delete',
      label: 'Loeschen/Storno',
      available: total > 0,
      hint: 'Angebote koennen fachlich abgelehnt, abgelaufen oder geloescht werden.',
    },
    {
      key: 'approve',
      label: 'Conversion',
      available: acceptedCount > 0 || openCount > 0,
      hint: 'Offene Angebote werden nachgefasst; angenommene Angebote fuehren in den Auftrag.',
    },
    {
      key: 'export',
      label: 'Export/Import',
      available: true,
      hint: 'CSV-Export, Druck und CSV-Import sind angebunden.',
    },
    {
      key: 'audit',
      label: 'Follow-up',
      available: true,
      hint: 'Status, Gueltigkeit, Kunde und Betrag bilden die Nachfassspur.',
    },
  ]

  const columns = [
    {
      key: 'nummer' as const,
      label: t('crud.fields.number'),
      render: (angebot: Angebot) => (
        <button
          onClick={() => navigate(`/sales/angebot/${angebot.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {angebot.nummer}
        </button>
      ),
    },
    {
      key: 'datum' as const,
      label: t('crud.fields.date'),
      render: (angebot: Angebot) => new Date(angebot.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'kunde' as const,
      label: t('crud.entities.customer'),
    },
    {
      key: 'betrag' as const,
      label: t('crud.fields.total'),
      render: (angebot: Angebot) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(angebot.betrag),
    },
    {
      key: 'gueltigBis' as const,
      label: t('crud.fields.validUntil'),
      render: (angebot: Angebot) => new Date(angebot.gueltigBis).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: t('crud.fields.status'),
      render: (angebot: Angebot) => (
        <Badge variant={statusVariantMap[angebot.status]}>{getStatusLabel(t, angebot.status, angebot.status)}</Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{getListTitle(t, entityTypeLabel)}</h1>
          <p className="text-muted-foreground">{t('crud.list.overview', { entityType: entityTypeLabel })}</p>
        </div>
        <Button onClick={() => navigate('/sales/angebot/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          {t('crud.actions.new')} {entityTypeLabel}
        </Button>
      </div>
      <RoleFocusBar
        roles={offerRoleProfiles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={roleFocus === 'all' ? 5 : 1}
        totalCount={5}
      />
      <ManagementDecisionPanel
        decision={{
          allowed: total > 0 && expiringCount === 0,
          allowedLabel: 'Angebotsarbeit stabil',
          blockedLabel: total === 0 ? 'Keine Angebote' : 'Nachfassen faellig',
          summary: total > 0
            ? `Die aktuelle Sicht enthaelt ${total} Angebote mit ${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(totalAmount)} Angebotswert. ${nextOfferAction}`
            : 'In der aktuellen Sicht gibt es keine Angebote. Legen Sie ein neues Angebot an oder starten Sie den Import.',
          blockerCount: total === 0 ? 1 : expiringCount,
          nextFocus: nextOfferAction,
          template: {
            label: 'Angebot anlegen',
            href: '/sales/angebot/neu',
          },
        }}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTaskPlan title="Angebots-Follow-up-Plan" items={offerTaskItems} />
        <NextActionPanel
          action={nextOfferAction}
          tone={expiringCount > 0 ? 'red' : openCount + acceptedCount > 0 ? 'amber' : total > 0 ? 'blue' : 'red'}
        />
      </div>
      <CrudCapabilityChecklist capabilities={offerCrudCapabilities} />

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
              onChange={(e) => setStatusFilter(e.target.value as Angebot['status'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">{t('crud.list.allStatus', { defaultValue: 'Alle Status' })}</option>
              <option value="offen">{getStatusLabel(t, 'offen', 'Offen')}</option>
              <option value="angenommen">{getStatusLabel(t, 'angenommen', 'Angenommen')}</option>
              <option value="abgelehnt">{getStatusLabel(t, 'abgelehnt', 'Abgelehnt')}</option>
              <option value="abgelaufen">{getStatusLabel(t, 'abgelaufen', 'Abgelaufen')}</option>
            </select>
            <AdvancedFilters
              filters={filterConfig}
              values={filterValues}
              onChange={setFilterValues}
              onReset={() => setFilterValues({})}
            />
            <Button variant="outline" className="gap-2" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              {t('crud.print.export')}
            </Button>
            <Button variant="outline" className="gap-2" onClick={handlePrint}>
              <FileText className="h-4 w-4" />
              {t('crud.actions.print')}
            </Button>
            <Button variant="outline" className="gap-2" onClick={() => setShowImport(!showImport)}>
              <FileText className="h-4 w-4" />
              {t('crud.actions.import')}
            </Button>
          </div>
        </CardContent>
      </Card>

      {showImport && (
        <Card>
          <CardContent className="pt-6">
            <CSVImport
              onImport={handleImport}
              expectedColumns={['Angebotsnummer', 'Datum', 'Kunde', 'Betrag', 'Gültig bis', 'Status']}
              entityName="Angebote"
            />
          </CardContent>
        </Card>
      )}

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredAngebote} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {t('crud.list.showing', { count: filteredAngebote.length, total: angebote.length, entityType: entityTypeLabel })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
