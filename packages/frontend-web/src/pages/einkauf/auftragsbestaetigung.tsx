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

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/auftragsbestaetigungen')
    } catch (error) {
      console.error(t('crud.messages.updateError', { entityType: entityTypeLabel }), error)
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
