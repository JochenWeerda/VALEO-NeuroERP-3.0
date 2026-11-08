import { useState } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import type { TFunction } from 'i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { LeaveConfirmDialog } from '@/components/LeaveConfirmDialog'
import { useUnsavedChanges } from '@/hooks/useUnsavedChanges'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'

const createDunningConfig = (t: TFunction, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.actions.edit'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'opId',
          label: t('crud.fields.opReference'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.opReference')
        },
        {
          name: 'debitorId',
          label: t('crud.entities.debtor'),
          type: 'lookup',
          required: true,
          endpoint: '/api/v1/finance/debtors',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'dunningLevel',
          label: t('crud.fields.dunningLevel'),
          type: 'select',
          required: true,
          options: [
            { value: 1, label: t('crud.fields.dunningLevel1') },
            { value: 2, label: t('crud.fields.dunningLevel2') },
            { value: 3, label: t('crud.fields.dunningLevel3') }
          ]
        },
        {
          name: 'dunningDate',
          label: t('crud.fields.dunningDate'),
          type: 'date',
          required: true
        },
        {
          name: 'dueDate',
          label: t('crud.fields.originalDueDate'),
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'created', label: t('status.recorded') },
            { value: 'sent', label: t('status.sent') },
            { value: 'paid', label: t('status.paid') },
            { value: 'escalated', label: t('crud.fields.escalated') },
            { value: 'collection', label: t('crud.fields.collection') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'betrag',
      label: t('crud.fields.amountAndFees'),
      fields: [
        {
          name: 'amount',
          label: t('crud.fields.openAmount'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.amountFromOp')
        },
        {
          name: 'dunningFee',
          label: t('crud.fields.dunningFee'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.dunningFee'),
          helpText: t('crud.tooltips.fields.dunningFee')
        },
        {
          name: 'interest',
          label: t('crud.fields.interest'),
          type: 'number',
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.interest'),
          helpText: t('crud.tooltips.fields.interest')
        },
        {
          name: 'totalAmount',
          label: t('crud.fields.totalClaim'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.totalClaim')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'text',
      label: t('crud.fields.dunningText'),
      fields: [
        {
          name: 'text',
          label: t('crud.fields.dunningText'),
          type: 'textarea',
          required: true,
          placeholder: t('crud.tooltips.placeholders.dunningText')
        },
        {
          name: 'paymentDeadline',
          label: t('crud.fields.paymentDeadline'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.paymentDeadline')
        }
      ]
    },
    {
      key: 'versand',
      label: t('crud.fields.shippingAndPayment'),
      fields: [
        {
          name: 'sentDate',
          label: t('crud.fields.sentDate'),
          type: 'date'
        },
        {
          name: 'paymentDate',
          label: t('crud.fields.paymentReceived'),
          type: 'date'
        },
        {
          name: 'reminderCount',
          label: t('crud.fields.remindersSent'),
          type: 'number',
          readonly: true,
          helpText: t('crud.tooltips.fields.remindersSent')
        },
        {
          name: 'lastReminderDate',
          label: t('crud.fields.lastReminder'),
          type: 'date',
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notes',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.dunningNotes')
        }
      ]
    }
  ],
  actions: [
    { key: 'generate', label: t('crud.actions.generateDunning'), type: 'secondary' },
    { key: 'preview', label: t('crud.actions.preview'), type: 'secondary' },
    { key: 'send', label: t('crud.actions.send'), type: 'primary' },
    { key: 'payment', label: t('crud.actions.bookPayment'), type: 'secondary' },
    { key: 'escalate', label: t('crud.actions.escalate'), type: 'danger' },
    { key: 'collection', label: t('crud.actions.handOverToCollection'), type: 'danger' },
    { key: 'export', label: t('crud.actions.pdfExport'), type: 'secondary' }
  ],
  api: {
    baseUrl: '/api/v1/finance/dunning',
    endpoints: {
      list: '/api/v1/finance/dunning',
      get: '/api/v1/finance/dunning/{id}',
      create: '/api/v1/finance/dunning',
      update: '/api/v1/finance/dunning/{id}',
      delete: '/api/v1/finance/dunning/{id}'
    }
  },
  permissions: ['finance.write', 'finance.dunning']
})

export default function DunningEditorPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'dunning'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Mahnung')
  const dunningConfig = createDunningConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: dunningConfig.api.baseUrl,
    id: id ?? 'new'
  })

  // --- Operational Case Header (Fallkopf) ---
  const dunningLevel = Number(data?.dunningLevel || 0)
  const dunningStatus = String(data?.status || 'created')
  const isEscalated = dunningStatus === 'escalated' || dunningStatus === 'collection'
  const isPaid = dunningStatus === 'paid'
  const isSent = dunningStatus === 'sent'
  const operationalStatus = normalizeOperationalStatus(
    isPaid ? 'abgeschlossen' : isEscalated ? 'eskaliert' : isSent ? 'wartet_auf_mensch' : 'offen'
  )
  const escalationPath = dunningLevel >= 3 ? 'Inkasso / Rechtsabteilung' : dunningLevel === 2 ? 'Eskalation auf Stufe 3' : 'Eskalation auf Stufe 2'
  const nextAction = isPaid ? 'Vorgang archivieren' : isEscalated ? 'Inkassouebergabe pruefen' : isSent ? 'Zahlungseingang ueberwachen' : dunningLevel > 0 ? 'Mahnung versenden' : 'Mahnung erstellen und versenden'
  const contextSections = [
    {
      title: 'Mahnvorgang',
      items: [
        { label: 'Mahnstufe', value: dunningLevel > 0 ? `Stufe ${dunningLevel}` : 'Neu' },
        { label: 'Status', value: dunningStatus === 'created' ? 'Erstellt' : dunningStatus === 'sent' ? 'Versendet' : dunningStatus === 'paid' ? 'Bezahlt' : dunningStatus === 'escalated' ? 'Eskaliert' : dunningStatus === 'collection' ? 'Inkasso' : dunningStatus },
        { label: 'Offener Betrag', value: `${Number(data?.totalAmount || 0).toFixed(2)} EUR` },
      ],
    },
    {
      title: 'Eskalation',
      items: [
        { label: 'Eskalationspfad', value: escalationPath },
        { label: 'Mahngebuehr', value: `${Number(data?.dunningFee || 0).toFixed(2)} EUR` },
        { label: 'Zinsen', value: `${Number(data?.interest || 0).toFixed(2)} EUR` },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: nextAction },
        { label: 'Erinnerungen', value: `${Number(data?.reminderCount || 0)} versendet` },
        { label: 'Blocker', value: isEscalated ? 'Eskalation aktiv – Inkassouebergabe erforderlich' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Mahnvorgang geoeffnet', detail: id && id !== 'new' ? `Mahnung ${id}` : 'Neue Mahnung' },
    dunningLevel > 0 ? { label: `Mahnstufe ${dunningLevel} erreicht`, detail: `Offener Betrag: ${Number(data?.totalAmount || 0).toFixed(2)} EUR` } : null,
    isSent ? { label: 'Mahnung versendet', detail: data?.sentDate || 'Versanddatum unbekannt' } : null,
    isEscalated ? { label: 'Eskalation eingeleitet', detail: escalationPath } : null,
    isPaid ? { label: 'Zahlung eingegangen', detail: data?.paymentDate || '' } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  const validate = (formData: Record<string, unknown>) => validateFields(getFieldsFromMaskConfig(dunningConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({ variant: 'destructive', title: t('crud.messages.validationError'), description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.` })
  }

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
    if (action === 'generate') {
      try {
        await apiClient.post('/api/v1/finance/dunning/run', formData ?? {})
        toast({ title: t('crud.messages.dunningGenerated'), description: t('crud.messages.dunningGeneratedDesc', { level: formData?.dunningLevel ?? 1 }) })
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      }
      return
    }
    if (action === 'preview') {
      // Vorschau
      if (!id || id === 'new') {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveFirst'),
        })
        return
      }
      window.open(`/api/v1/finance/dunning/${id}/export`, '_blank')
    } else if (action === 'send') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      try {
        await saveData({ ...formData, status: 'sent', sentDate: new Date().toISOString().split('T')[0] })
        setIsDirty(false)
        toast({
          title: t('crud.messages.dunningSent'),
          description: t('crud.messages.dunningSentDesc'),
        })
        navigate('/finance/dunning')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'payment') {
      // Zahlung buchen
      if (!id || id === 'new') {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveFirst'),
        })
        return
      }

      try {
        await apiClient.put(`/api/v1/finance/dunning/${id}/paid`)
        formData.status = 'paid'
        formData.paymentDate = new Date().toISOString().split('T')[0]
        toast({
          title: t('crud.messages.paymentBooked'),
          description: t('crud.messages.paymentBookedDesc'),
        })
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        toast({
          variant: 'destructive',
          title: t('crud.messages.paymentError'),
          description: error.response?.data?.detail || t('crud.messages.paymentErrorDesc'),
        })
      }
    } else if (action === 'escalate') {
      if (window.confirm(t('crud.messages.escalateConfirm'))) {
        try {
          await saveData({ ...formData, status: 'escalated' })
          setIsDirty(false)
          toast({
            title: t('crud.messages.dunningEscalated'),
            description: t('crud.messages.dunningEscalatedDesc'),
          })
          navigate('/finance/dunning')
        } catch (error) {
          // Error wird bereits in useMaskData behandelt
        }
      }
    } else if (action === 'collection') {
      if (window.confirm(t('crud.messages.collectionConfirm'))) {
        try {
          await saveData({ ...formData, status: 'collection' })
          setIsDirty(false)
          toast({
            title: t('crud.messages.collectionHandedOver'),
            description: t('crud.messages.collectionHandedOverDesc'),
          })
          navigate('/finance/dunning')
        } catch (error) {
          // Error wird bereits in useMaskData behandelt
        }
      }
    }
    if (action === 'export') {
      if (!id || id === 'new') {
        toast({ variant: 'destructive', title: t('common.error'), description: t('crud.messages.saveFirst') })
        return
      }
      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', { entity: 'dunning', format: 'pdf', id })
        if (res?.url) window.open(res.url, '_blank')
        toast({ title: t('crud.actions.pdfExport'), description: t('crud.messages.exportCreated', { defaultValue: 'Export erstellt' }) })
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      }
    }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
    await handleAction('send', formData)
  }

  const handleCancel = () => {
    navigate('/finance/dunning')
  }

  const blocker = useUnsavedChanges(isDirty)

  return (
    <>
      <ModuleToolbar backTarget="/finance/dunning" closeTarget="/finance/dunning" title={entityTypeLabel} />
      <LeaveConfirmDialog blocker={blocker} onSave={() => handleSave(data ?? {})} title={t('crud.messages.unsavedChanges', { defaultValue: 'Ungespeicherte Änderungen' })} description={t('crud.messages.unsavedChangesDescription', { defaultValue: 'Möchten Sie speichern, verwerfen oder hier bleiben?' })} />
      <div className="space-y-4 p-4">
        <OperationalCaseHeader
          title={entityTypeLabel}
          description="Mahnvorgang bearbeiten: Mahnstufe, Eskalationspfad und offene Betraege auf einen Blick."
          status={operationalStatus}
          owner="Debitorenbuchhaltung"
          blocker={isEscalated ? 'Eskalation aktiv – Inkassouebergabe erforderlich.' : null}
          nextAction={nextAction}
          caseLabel={id && id !== 'new' ? `Mahnung ${id}` : 'Neue Mahnung'}
          tags={['FIBU', 'Mahnwesen']}
        />
        <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
          <OperationalTimeline title="Mahnverlauf" items={timelineItems} />
          <OperationalContextPanel sections={contextSections} />
        </div>
      </div>
      <ObjectPage
        config={dunningConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={(key, formData) => handleAction(key, formData)}
        loadingActionKey={loadingActionKey}
      />
    </>
  )
}
