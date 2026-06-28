import { useState } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { useTranslation, type TFunction } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const createAngebotConfig = (t: TFunction, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.edit'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        { name: 'angebotNummer', label: t('crud.fields.number'), type: 'text', required: true, readonly: true },
        {
          name: 'anfrageId',
          label: t('crud.entities.purchaseRequest'),
          type: 'lookup',
          endpoint: '/api/v1/einkauf/anfragen?status=FREIGEGEBEN',
          displayField: 'anfrageNummer',
          valueField: 'id',
          helpText: t('crud.tooltips.fields.linkedRequest')
        },
        {
          name: 'lieferantId',
          label: t('crud.entities.supplier'),
          type: 'lookup',
          required: true,
          endpoint: '/api/v1/crm/business-partners?type=supplier',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'ERFASST', label: t('status.recorded') },
            { value: 'GEPRUEFT', label: t('status.reviewed') },
            { value: 'GENEHMIGT', label: t('status.approved') },
            { value: 'IN_BESTELLUNG', label: 'In Bestellung' },
            { value: 'ABGELEHNT', label: t('status.rejected') }
          ]
        }
      ]
    },
    {
      key: 'angebot',
      label: t('crud.detail.offerDetails'),
      fields: [
        {
          name: 'artikel',
          label: t('crud.fields.product'),
          type: 'lookup',
          required: true,
          endpoint: '/api/v1/articles',
          displayField: 'name',
          valueField: 'id'
        },
        { name: 'menge', label: t('crud.fields.quantity'), type: 'number', required: true },
        {
          name: 'einheit',
          label: t('crud.fields.unit'),
          type: 'select',
          required: true,
          options: [
            { value: 'kg', label: 'kg' },
            { value: 't', label: 't' },
            { value: 'l', label: 'l' },
            { value: 'Stk', label: 'Stk' }
          ]
        },
        { name: 'preis', label: t('crud.fields.price'), type: 'number', required: true },
        {
          name: 'waehrung',
          label: t('crud.fields.currency'),
          type: 'select',
          options: [
            { value: 'EUR', label: 'EUR' },
            { value: 'USD', label: 'USD' },
            { value: 'GBP', label: 'GBP' }
          ]
        },
        { name: 'lieferzeit', label: t('crud.fields.deliveryTime'), type: 'number', required: true },
        { name: 'gueltigBis', label: t('crud.fields.validUntil'), type: 'date', required: true }
      ]
    },
    {
      key: 'konditionen',
      label: t('crud.fields.conditions'),
      fields: [
        { name: 'mindestabnahme', label: t('crud.fields.minimumOrder'), type: 'number', helpText: t('crud.tooltips.fields.minimumOrder') },
        { name: 'zahlungsbedingungen', label: t('crud.fields.paymentTerms'), type: 'text', placeholder: t('crud.tooltips.placeholders.paymentTerms') },
        {
          name: 'incoterms',
          label: t('crud.fields.incoterms'),
          type: 'select',
          options: [
            { value: 'EXW', label: 'EXW - Ab Werk' },
            { value: 'FCA', label: 'FCA - Frei Frachtfuehrer' },
            { value: 'CPT', label: 'CPT - Frachtfrei bezahlt bis' },
            { value: 'CIP', label: 'CIP - Frachtfrei versichert bis' },
            { value: 'DAT', label: 'DAT - Geliefert Terminal' },
            { value: 'DAP', label: 'DAP - Geliefert benannter Ort' },
            { value: 'DDP', label: 'DDP - Geliefert verzollt' }
          ]
        },
        { name: 'bemerkungen', label: t('crud.fields.notes'), type: 'textarea', placeholder: t('crud.tooltips.placeholders.offerNotes') }
      ]
    }
  ],
  actions: [
    { key: 'pruefen', label: t('crud.actions.review'), type: 'secondary' },
    { key: 'genehmigen', label: t('crud.actions.approve'), type: 'primary' },
    { key: 'ablehnen', label: t('crud.actions.reject'), type: 'danger' },
    { key: 'inBestellung', label: t('crud.actions.convertToOrder'), type: 'secondary' }
  ],
  api: {
    baseUrl: '/api/v1/einkauf/angebote',
    endpoints: {
      list: '/api/v1/einkauf/angebote',
      get: '/api/v1/einkauf/angebote/{id}',
      create: '/api/v1/einkauf/angebote',
      update: '/api/v1/einkauf/angebote/{id}',
      delete: '/api/v1/einkauf/angebote/{id}'
    }
  },
  permissions: ['einkauf.read', 'einkauf.write']
})

export default function AngebotStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'purchaseOffer'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Angebot')
  const angebotConfig = createAngebotConfig(t, entityTypeLabel)

  const { data, saveData } = useMaskData({
    apiUrl: angebotConfig.api.baseUrl,
    id: id || undefined
  })

  const { handleAction, loadingActionKey } = useMaskActions(async (actionKey: string) => {
          if (!id || !transitionMap[actionKey]) {
            toast({ title: 'Aktion nicht moeglich', description: 'Das Angebot muss zuerst gespeichert werden.', variant: 'destructive' })
            return
          }
          try {
            const response = await apiClient.post<{ purchaseOrderId?: string; purchaseOrderNumber?: string }>(
              `/api/v1/einkauf/angebote/${encodeURIComponent(id)}/${transitionMap[actionKey]}`,
            )
            if (actionKey === 'inBestellung' && response.data?.purchaseOrderId) {
              toast({ title: 'Bestellung erzeugt', description: response.data.purchaseOrderNumber || 'Folgebeleg erzeugt.' })
              navigate(`/einkauf/bestellungen/${encodeURIComponent(response.data.purchaseOrderId)}`)
              return
            }
            toast({ title: 'Aktion ausgefuehrt', description: `Angebot ${id} wurde aktualisiert.` })
            navigate('/einkauf/angebote')
          } catch (error: any) {
            toast({ title: 'Aktion fehlgeschlagen', description: error.response?.data?.detail || error.message, variant: 'destructive' })
          }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/angebote')
    } catch (error: any) {
      toast({ variant: 'destructive', title: t('crud.messages.updateError', { entityType: entityTypeLabel }), description: error?.message })
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) {
      navigate('/einkauf/angebote')
    }
  }

  const transitionMap: Record<string, string> = {
    pruefen: 'review',
    genehmigen: 'approve',
    ablehnen: 'reject',
    inBestellung: 'convert-to-order',
  }

  return (
    <div className="space-y-6">
      <OperationalCaseHeader
        title={data?.angebotNummer || 'Angebot'}
        description="Angebot als eigenstaendiger Einkaufsvorgang mit Preis-, Governance- und Folgebelegkontext."
        status={normalizeOperationalStatus(data?.status)}
        owner={data?.lieferantId ? 'Lieferantenbezug gepflegt' : 'Lieferant offen'}
        blocker={data?.status === 'ABGELEHNT' ? 'Dieses Angebot ist abgelehnt und blockiert den Folgeprozess.' : null}
        nextAction={
          data?.status === 'ERFASST'
            ? 'Angebot pruefen'
            : data?.status === 'GEPRUEFT'
              ? 'Angebot freigeben'
              : data?.status === 'GENEHMIGT'
                ? 'Bestellung erzeugen'
                : 'Vorgang abschliessen'
        }
        caseLabel="Angebotsvorgang"
        tags={[data?.status || 'Status offen', data?.waehrung || 'EUR']}
      />
      <OperationalContextPanel
        title="Angebotskontext"
        sections={[
          {
            title: 'Ressourcenlage',
            items: [
              { label: 'Artikel', value: data?.artikel || '-' },
              { label: 'Menge', value: data?.menge != null ? `${data.menge} ${data?.einheit || ''}`.trim() : '-' },
            ],
          },
          {
            title: 'Wirtschaftslage',
            items: [
              { label: 'Preis', value: data?.preis != null ? `${data.preis} ${data?.waehrung || 'EUR'}` : '-' },
              { label: 'Gueltig bis', value: data?.gueltigBis || '-' },
            ],
          },
          {
            title: 'Governance',
            items: [
              { label: 'Anfragebezug', value: data?.anfrageId || '-' },
              { label: 'Naechster Schritt', value: data?.status === 'GENEHMIGT' ? 'Bestellung erzeugen' : 'Review abschliessen' },
            ],
          },
        ]}
      />
      <ObjectPage
        config={angebotConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={handleAction}
        loadingActionKey={loadingActionKey}
      />
    </div>
  )
}
