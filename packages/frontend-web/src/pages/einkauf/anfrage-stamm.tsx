import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Anfrage (wird in Komponente mit i18n erstellt)
const createAnfrageSchema = (t: any) => z.object({
  anfrageNummer: z.string().min(1, t('crud.messages.validationError')),
  typ: z.enum(['BANF', 'ANF']),
  anforderer: z.string().min(1, t('crud.messages.validationError')),
  artikel: z.string().min(1, t('crud.messages.validationError')),
  menge: z.number().min(0.1, t('crud.messages.validationError')),
  einheit: z.string().min(1, t('crud.messages.validationError')),
  prioritaet: z.enum(['niedrig', 'normal', 'hoch', 'dringend']),
  faelligkeit: z.string().min(1, t('crud.messages.validationError')),
  status: z.enum(['ENTWURF', 'FREIGEGEBEN', 'ANGEBOTSPHASE']),
  begruendung: z.string().min(1, t('crud.messages.validationError')),
  kostenstelle: z.string().optional(),
  projekt: z.string().optional(),
  bemerkungen: z.string().optional()
})

// Konfiguration für Anfrage ObjectPage (wird in Komponente mit i18n erstellt)
const createAnfrageConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.create'),
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'anfrageNummer',
          label: t('crud.fields.number'),
          type: 'text',
          required: true,
          readonly: true
        },
        {
          name: 'typ',
          label: t('crud.fields.type'),
          type: 'select',
          required: true,
          options: [
            { value: 'BANF', label: t('crud.entities.purchaseRequest') + ' (BANF)' },
            { value: 'ANF', label: t('crud.entities.purchaseRequest') + ' (ANF)' }
          ]
        },
        {
          name: 'anforderer',
          label: t('crud.fields.requestedBy'),
          type: 'text',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'ENTWURF', label: t('status.draft') },
            { value: 'FREIGEGEBEN', label: t('status.approved') },
            { value: 'ANGEBOTSPHASE', label: t('status.pending') }
          ]
        }
      ]
    },
    {
      key: 'bedarf',
      label: t('crud.fields.requirement'),
      fields: [
        {
          name: 'artikel',
          label: t('crud.fields.product'),
          type: 'lookup',
          required: true,
          endpoint: '/api/articles',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'menge',
          label: t('crud.fields.quantity'),
          type: 'number',
          required: true
        },
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
        {
          name: 'prioritaet',
          label: t('crud.fields.priority'),
          type: 'select',
          required: true,
          options: [
            { value: 'niedrig', label: t('crud.fields.priorityLow') },
            { value: 'normal', label: t('crud.fields.priorityNormal') },
            { value: 'hoch', label: t('crud.fields.priorityHigh') },
            { value: 'dringend', label: t('crud.fields.priorityUrgent') }
          ]
        },
        {
          name: 'faelligkeit',
          label: t('crud.fields.dueDate'),
          type: 'date',
          required: true
        }
      ]
    },
    {
      key: 'details',
      label: t('crud.detail.additionalInfo'),
      fields: [
        {
          name: 'begruendung',
          label: t('crud.fields.reason'),
          type: 'textarea',
          required: true,
          placeholder: t('crud.tooltips.placeholders.reason')
        },
        {
          name: 'kostenstelle',
          label: t('crud.fields.costCenter'),
          type: 'lookup',
          endpoint: '/api/cost-centers',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'projekt',
          label: t('crud.fields.project'),
          type: 'lookup',
          endpoint: '/api/projects',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'bemerkungen',
          label: t('crud.fields.notes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.notes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'freigeben',
      label: t('crud.actions.approve'),
      type: 'primary',
      onClick: () => console.log('Freigeben clicked')
    },
    {
      key: 'inBestellung',
      label: t('crud.actions.convertToOrder'),
      type: 'secondary',
      onClick: () => console.log('In Bestellung clicked')
    }
  ],
  api: {
    baseUrl: '/api/einkauf/anfragen',
    endpoints: {
      list: '/api/einkauf/anfragen',
      get: '/api/einkauf/anfragen/{id}',
      create: '/api/einkauf/anfragen',
      update: '/api/einkauf/anfragen/{id}',
      delete: '/api/einkauf/anfragen/{id}'
    }
  },
  validation: createAnfrageSchema(t),
  permissions: ['einkauf.read', 'einkauf.write']
})

export default function AnfrageStammPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [loading, setLoading] = useState(false)
  const entityType = 'purchaseRequest'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Anfrage')
  const anfrageConfig = createAnfrageConfig(t, entityTypeLabel)

  const { data, saveData } = useMaskData({
    apiUrl: anfrageConfig.api.baseUrl,
    id: id || undefined
  })

  const handleSave = async (formData: any) => {
    setLoading(true)
    try {
      await saveData(formData)
      navigate('/einkauf/anfragen')
    } catch (error) {
      console.error(t('crud.messages.updateError', { entityType: entityTypeLabel }), error)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    if (confirm(t('crud.messages.discardChanges'))) {
      navigate('/einkauf/anfragen')
    }
  }

  return (
    <ObjectPage
      config={anfrageConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}