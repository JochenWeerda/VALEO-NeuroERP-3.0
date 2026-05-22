import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { summarizeProcurementMatch } from '@/lib/domain-depth'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const createAuftragsbestaetigungConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.tooltips.fields.orderConfirmation'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'bestellungId',
          label: t('crud.entities.purchaseOrder'),
          type: 'lookup',
          required: true,
          endpoint: '/api/v1/purchase-orders?status=FREIGEGEBEN',
          displayField: 'purchaseOrderNumber',
          valueField: 'id'
        },
        { name: 'bestaetigungsNummer', label: t('crud.fields.confirmationNumber'), type: 'text', required: true },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'OFFEN', label: t('status.pending') },
            { value: 'GEPRUEFT', label: t('status.reviewed') },
            { value: 'BESTAETIGT', label: t('status.confirmed') }
          ]
        }
      ]
    },
    {
      key: 'termine',
      label: t('crud.fields.dateConfirmations'),
      fields: [
        {
          name: 'bestaetigteTermine',
          label: t('crud.fields.dateDeviations'),
          type: 'table',
          columns: [
            { key: 'positionId', label: t('crud.fields.item'), type: 'text', required: true },
            { key: 'bestaetigterTermin', label: t('crud.fields.confirmedDate'), type: 'date', required: true },
            { key: 'abweichung', label: t('crud.fields.deviation'), type: 'text' }
          ] as any,
          helpText: t('crud.tooltips.fields.dateDeviations')
        }
      ]
    },
    {
      key: 'preise',
      label: t('crud.fields.priceDeviations'),
      fields: [
        {
          name: 'preisabweichungen',
          label: t('crud.fields.priceChanges'),
          type: 'table',
          columns: [
            { key: 'positionId', label: t('crud.fields.item'), type: 'text', required: true },
            { key: 'urspruenglicherPreis', label: t('crud.fields.originalPrice'), type: 'number', required: true },
            { key: 'neuerPreis', label: t('crud.fields.newPrice'), type: 'number', required: true },
            { key: 'begruendung', label: t('crud.fields.reason'), type: 'text' }
          ] as any,
          helpText: t('crud.tooltips.fields.priceDeviations')
        }
      ]
    },
    {
      key: 'belege',
      label: t('crud.detail.additionalInfo'),
      fields: [
        {
          name: 'bemerkungen',
          label: t('crud.fields.notes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.confirmationNotes')
        }
      ]
    }
  ],
  actions: [
    { key: 'pruefen', label: t('crud.actions.review'), type: 'secondary' },
    { key: 'bestaetigen', label: t('crud.actions.confirm'), type: 'primary' }
  ],
  api: {
    baseUrl: '/api/v1/einkauf/auftragsbestaetigungen',
    endpoints: {
      list: '/api/v1/einkauf/auftragsbestaetigungen',
      get: '/api/v1/einkauf/auftragsbestaetigungen/{id}',
      create: '/api/v1/einkauf/auftragsbestaetigungen',
      update: '/api/v1/einkauf/auftragsbestaetigungen/{id}',
      delete: '/api/v1/einkauf/auftragsbestaetigungen/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write']
})

export default function AuftragsbestaetigungPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'orderConfirmation'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Auftragsbestaetigung')
  const auftragsbestaetigungConfig = createAuftragsbestaetigungConfig(t, entityTypeLabel)

  const { data, saveData } = useMaskData({
    apiUrl: auftragsbestaetigungConfig.api.baseUrl,
    id: id || undefined
  })
  const confirmationOps = summarizeProcurementMatch({
    exceptionsCount:
      (Array.isArray(data?.bestaetigteTermine) ? data.bestaetigteTermine.length : 0) +
      (Array.isArray(data?.preisabweichungen) ? data.preisabweichungen.length : 0),
    variancePercentage: data?.status === 'BESTAETIGT' ? 0 : data?.status === 'GEPRUEFT' ? 4 : 9,
    autoApprovalEligible: data?.status === 'GEPRUEFT' || data?.status === 'BESTAETIGT',
    hasGoodsReceipt: Boolean(data?.bestellungId),
  })
  const operationalStatus = normalizeOperationalStatus(data?.status)
  const operationalBlocker = data?.status === 'OFFEN'
    ? 'Die Auftragsbestaetigung ist noch nicht geprueft und kann Termin- oder Preisabweichungen enthalten.'
    : null
  const contextSections = [
    {
      title: 'Bestaetigung',
      items: [
        { label: 'Nummer', value: String(data?.bestaetigungsNummer ?? 'Neu') },
        { label: 'Bestellung', value: String(data?.bestellungId ?? 'Noch offen') },
        { label: 'Status', value: String(data?.status ?? 'OFFEN') },
      ],
    },
    {
      title: 'Pruefkontext',
      items: [
        { label: 'Terminabweichungen', value: `${Array.isArray(data?.bestaetigteTermine) ? data.bestaetigteTermine.length : 0}` },
        { label: 'Preisabweichungen', value: `${Array.isArray(data?.preisabweichungen) ? data.preisabweichungen.length : 0}` },
        { label: 'Naechste Aktion', value: data?.status === 'BESTAETIGT' ? 'Bestellung nachhalten' : data?.status === 'GEPRUEFT' ? 'Bestaetigen' : 'Pruefen' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Auftragsbestaetigung aktiv', detail: String(data?.bestaetigungsNummer ?? 'Neue Bestaetigung') },
    ...(data?.status ? [{ label: 'Status', detail: String(data.status) }] : []),
    ...(Array.isArray(data?.bestaetigteTermine) && data.bestaetigteTermine.length > 0 ? [{ label: 'Terminbezug vorhanden', detail: `${data.bestaetigteTermine.length} bestaetigte Termine.` }] : []),
  ]

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/auftragsbestaetigungen')
    } catch (error: any) {
      toast({ variant: 'destructive', title: t('crud.messages.updateError', { entityType: entityTypeLabel }), description: error?.message })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) {
      navigate('/einkauf/auftragsbestaetigungen')
    }
  }

  return (
    <>
      <ModuleToolbar backTarget="/einkauf/auftragsbestaetigungen" closeTarget="/einkauf/auftragsbestaetigungen" title={entityTypeLabel} />
      <div className="space-y-4">
        <OperationalCaseHeader
          title="Auftragsbestaetigung steuern"
          description="Termin- und Preisabweichungen werden vor der Fachmaske knapp eingeordnet, damit die Pruefung zielgerichtet bleibt."
          status={operationalStatus}
          owner="Einkauf"
          blocker={operationalBlocker}
          nextAction={confirmationOps.nextAction}
          caseLabel={String(data?.bestaetigungsNummer ?? 'Auftragsbestaetigung')}
          tags={['Einkauf', 'Lieferant']}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTimeline title="Bestaetigungsverlauf" items={timelineItems} />
          <OperationalContextPanel title="Bestaetigungskontext" sections={contextSections} />
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Abweichungsdruck</CardTitle></CardHeader>
            <CardContent><Badge variant={confirmationOps.exceptionPressure === 'hoch' ? 'destructive' : 'outline'}>{confirmationOps.exceptionPressure}</Badge></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Termin-/Preisfall</CardTitle></CardHeader>
            <CardContent><div className="text-sm font-semibold">{`${Array.isArray(data?.bestaetigteTermine) ? data.bestaetigteTermine.length : 0} Termine / ${Array.isArray(data?.preisabweichungen) ? data.preisabweichungen.length : 0} Preise`}</div></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm">Naechste Fallaktion</CardTitle></CardHeader>
            <CardContent><div className="text-sm font-semibold">{confirmationOps.nextAction}</div></CardContent>
          </Card>
        </div>
      </div>
      <ObjectPage
        config={auftragsbestaetigungConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={async (actionKey) => {
          const actionMap: Record<string, string> = {
            pruefen: 'review',
            bestaetigen: 'confirm',
          }
          if (!id || !actionMap[actionKey]) {
            toast({ title: 'Aktion nicht moeglich', description: 'Die Auftragsbestaetigung muss zuerst gespeichert werden.', variant: 'destructive' })
            return
          }
          setLoading(true)
          try {
            await apiClient.post(`/api/v1/einkauf/auftragsbestaetigungen/${encodeURIComponent(id)}/${actionMap[actionKey]}`)
            toast({ title: 'Aktion ausgefuehrt', description: `Auftragsbestaetigung ${id} wurde aktualisiert.` })
            navigate('/einkauf/auftragsbestaetigungen')
          } catch (error: any) {
            toast({ title: 'Aktion fehlgeschlagen', description: error.response?.data?.detail || error.message, variant: 'destructive' })
          } finally {
            setLoading(false)
          }
        }}
      />
    </>
  )
}
