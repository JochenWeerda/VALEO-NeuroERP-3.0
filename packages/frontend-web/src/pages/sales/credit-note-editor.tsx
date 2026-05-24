import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'

type CreditNoteRoleFocus = 'all' | 'sales' | 'billing' | 'finance' | 'management'

const creditNoteRoleProfiles: Array<{ id: CreditNoteRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt die Gutschrift fuer Vertrieb, Faktura, Finance und Leitung.',
  },
  {
    id: 'sales',
    label: 'Vertrieb',
    description: 'Fokus auf Kunde, Grund, Ausgangsrechnung und Kundenklaerung.',
  },
  {
    id: 'billing',
    label: 'Faktura',
    description: 'Fokus auf Positionen, Betrag, Freigabe, Versand und Druck.',
  },
  {
    id: 'finance',
    label: 'Finance',
    description: 'Fokus auf Betrag, Steuer, Zahlungsziel und OP-Auswirkung.',
  },
  {
    id: 'management',
    label: 'Leitung',
    description: 'Fokus auf Freigabefaehigkeit, Blocker und naechste Aktion.',
  },
]

const createCreditNoteConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: `${t('crud.actions.create')}/${t('crud.actions.edit')} ${entityTypeLabel}`,
  subtitle: t('crud.tooltips.fields.creditNote'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'number',
          label: t('crud.fields.number'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.creditNoteNumber')
        },
        {
          name: 'date',
          label: t('crud.fields.date'),
          type: 'date',
          required: true
        },
        {
          name: 'customerId',
          label: t('crud.entities.customer'),
          type: 'lookup',
          required: true,
          endpoint: '/api/v1/crm/customers',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'sourceInvoice',
          label: t('crud.fields.sourceInvoice'),
          type: 'lookup',
          endpoint: '/api/v1/finance/invoices',
          displayField: 'number',
          valueField: 'id',
          helpText: t('crud.tooltips.fields.sourceInvoice')
        },
        {
          name: 'reason',
          label: t('crud.fields.reason'),
          type: 'select',
          required: true,
          options: [
            { value: 'return', label: t('crud.fields.reasonReturn') },
            { value: 'discount', label: t('crud.fields.reasonDiscount') },
            { value: 'error', label: t('crud.fields.reasonError') },
            { value: 'complaint', label: t('crud.fields.reasonComplaint') },
            { value: 'other', label: t('crud.dialogs.amend.types.other') }
          ]
        },
        {
          name: 'reasonText',
          label: t('crud.fields.reasonDetails'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.creditNoteReason')
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'draft', label: t('status.draft') },
            { value: 'approved', label: t('status.approved') },
            { value: 'sent', label: t('status.sent') },
            { value: 'paid', label: t('status.paid') },
            { value: 'cancelled', label: t('status.cancelled') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'positionen',
      label: t('crud.fields.items'),
      fields: [
        {
          name: 'lines',
          label: t('crud.fields.creditNoteItems'),
          type: 'table',
          required: true,
          columns: [
            { key: 'article', label: t('crud.fields.product'), type: 'lookup', required: true },
            { key: 'qty', label: t('crud.fields.quantity'), type: 'number', required: true },
            { key: 'price', label: t('crud.fields.price'), type: 'number', required: true },
            { key: 'vatRate', label: `${t('crud.fields.taxRate')  } %`, type: 'number', required: true },
            { key: 'discount', label: `${t('crud.fields.discount')  } %`, type: 'number' }
          ],
          minRows: 1,
          helpText: t('crud.tooltips.fields.creditNoteItems')
        }
      ]
    },
    {
      key: 'betrag',
      label: t('crud.fields.amounts'),
      fields: [
        {
          name: 'subtotalNet',
          label: t('crud.fields.netAmount'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.subtotalNet')
        },
        {
          name: 'totalDiscount',
          label: t('crud.fields.totalDiscount'),
          type: 'number',
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.totalDiscount')
        },
        {
          name: 'totalTax',
          label: t('crud.fields.totalTax'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.totalTax')
        },
        {
          name: 'totalGross',
          label: t('crud.fields.grossAmount'),
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: t('crud.tooltips.fields.totalGross')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'zahlung',
      label: t('crud.fields.paymentAndDue'),
      fields: [
        {
          name: 'paymentTerms',
          label: t('crud.fields.paymentTerms'),
          type: 'select',
          required: true,
          options: [
            { value: 'immediate', label: t('crud.fields.paymentTermsImmediate') },
            { value: 'net30', label: t('crud.fields.paymentTermsNet30') },
            { value: 'net60', label: t('crud.fields.paymentTermsNet60') },
            { value: 'net90', label: t('crud.fields.paymentTermsNet90') }
          ]
        },
        {
          name: 'dueDate',
          label: t('crud.fields.dueDate'),
          type: 'date',
          required: true
        }
      ]
    },
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notes',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.creditNoteNotes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'calculate',
      label: t('crud.actions.recalculate'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'preview',
      label: t('crud.actions.preview'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'approve',
      label: t('crud.actions.approve'),
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'send',
      label: t('crud.actions.send'),
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'print',
      label: t('crud.actions.print'),
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'cancel',
      label: t('crud.actions.cancel'),
      type: 'danger',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/v1/sales/credit-notes',
    endpoints: {
      list: '/api/v1/sales/credit-notes',
      get: '/api/v1/sales/credit-notes/{id}',
      create: '/api/v1/sales/credit-notes',
      update: '/api/v1/sales/credit-notes/{id}',
      delete: '/api/v1/sales/credit-notes/{id}'
    }
  },
  permissions: ['sales.write', 'sales.credit_notes']
})

export default function CreditNoteEditorPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const [isDirty, setIsDirty] = useState(false)
  const [roleFocus, setRoleFocus] = useState<CreditNoteRoleFocus>('all')
  const entityType = 'creditNote'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Gutschrift')
  const creditNoteConfig = createCreditNoteConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: creditNoteConfig.api.baseUrl,
    id: id ?? 'new'
  })

  const validate = (formData: any) => validateFields(getFieldsFromMaskConfig(creditNoteConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({ variant: 'destructive', title: t('crud.messages.validationError'), description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.` })
  }

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
    if (action === 'calculate') {
      toast({ title: 'Neuberechnung', description: t('crud.messages.recalculateFunction', { defaultValue: 'Beträge werden neu berechnet.' }) })
    } else if (action === 'preview') {
      // Vorschau anzeigen
      window.open('/api/v1/sales/credit-notes/preview', '_blank')
    } else if (action === 'approve') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      try {
        await saveData({ ...formData, status: 'approved' })
        setIsDirty(false)
        navigate('/sales/credit-notes')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'send') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      try {
        await saveData({ ...formData, status: 'sent' })
        setIsDirty(false)
        navigate('/sales/credit-notes')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'print') {
      window.open('/api/v1/sales/credit-notes/print', '_blank')
    } else if (action === 'cancel') {
      if (window.confirm(t('crud.dialogs.cancel.descriptionGeneric', { entityType: entityTypeLabel }))) {
        try {
          await saveData({ ...formData, status: 'cancelled' })
          setIsDirty(false)
          navigate('/sales/credit-notes')
        } catch (error) {
          // Error wird bereits in useMaskData behandelt
        }
      }
    }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
    await handleAction('approve', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.discardChanges'))) {
      return
    }
    navigate('/sales/credit-notes')
  }

  const creditNote = (data ?? {}) as Record<string, any>
  const lines = Array.isArray(creditNote.lines) ? creditNote.lines : []
  const hasCustomer = Boolean(creditNote.customerId)
  const hasSourceInvoice = Boolean(creditNote.sourceInvoice)
  const hasReason = Boolean(creditNote.reason)
  const hasReasonText = Boolean(String(creditNote.reasonText ?? '').trim())
  const hasLines = lines.length > 0
  const hasAmount = Number(creditNote.totalGross ?? 0) > 0 || lines.some((line: any) => Number(line?.price ?? 0) > 0)
  const hasPaymentPath = Boolean(creditNote.paymentTerms && creditNote.dueDate)
  const isCancelled = creditNote.status === 'cancelled'
  const isCreditNoteReady = hasCustomer && hasReason && hasLines && hasAmount && hasPaymentPath && !isCancelled
  const nextCreditNoteAction = !hasCustomer
    ? 'Kunden fuer die Gutschrift auswaehlen.'
    : !hasSourceInvoice
      ? 'Ausgangsrechnung verknuepfen oder begruenden, warum keine vorhanden ist.'
      : !hasReason
        ? 'Gutschriftsgrund auswaehlen.'
        : !hasLines
          ? 'Mindestens eine Gutschriftsposition erfassen.'
          : !hasAmount
            ? 'Betrag und Steuer pruefen.'
            : !hasPaymentPath
              ? 'Zahlungsbedingung und Faelligkeit setzen.'
              : isCancelled
                ? 'Stornierte Gutschrift pruefen; keine Freigabe moeglich.'
                : 'Gutschrift freigeben, senden oder drucken.'
  const creditNoteTaskItems: UxTaskItem[] = [
    {
      label: 'Kunde und Ausgangsrechnung klaeren',
      done: hasCustomer && (hasSourceInvoice || hasReasonText),
      hint: hasCustomer ? (hasSourceInvoice ? 'Kunde und Ausgangsrechnung sind verbunden.' : 'Kunde ist gesetzt; Ausgangsrechnung oder Begruendung klaeren.') : 'Kunde fehlt noch.',
    },
    {
      label: 'Grund und Positionen erfassen',
      done: hasReason && hasLines,
      hint: hasReason && hasLines ? `${lines.length} Positionen mit Grund ${creditNote.reason}.` : 'Grund und mindestens eine Position sind Pflicht.',
    },
    {
      label: 'Betrag und Zahlungsfolge pruefen',
      done: hasAmount && hasPaymentPath,
      hint: hasAmount && hasPaymentPath ? `Brutto ${Number(creditNote.totalGross ?? 0).toFixed(2)} und Faelligkeit ${creditNote.dueDate}.` : 'Betrag, Steuer, Zahlungsbedingung und Faelligkeit pruefen.',
    },
    {
      label: 'Freigabe und Nachweis sichern',
      done: ['approved', 'sent', 'paid'].includes(String(creditNote.status)),
      hint: creditNote.status ? `Status: ${creditNote.status}.` : 'Freigabe, Versand oder Druck als Nachweis festhalten.',
    },
  ]
  const creditNoteCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen/Speichern',
      available: isCreditNoteReady,
      hint: isCreditNoteReady ? 'Gutschrift kann gespeichert oder freigegeben werden.' : 'Kunde, Grund, Positionen, Betrag und Zahlungsfolge muessen stimmen.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Grunddaten, Positionen, Betrag, Zahlung und Notizen sind in der Maske sichtbar.',
    },
    {
      key: 'update',
      label: 'Bearbeiten',
      available: !isCancelled,
      hint: isCancelled ? 'Stornierte Gutschriften sollten nicht weiter bearbeitet werden.' : 'Felder und Positionen koennen ueber die ObjectPage bearbeitet werden.',
    },
    {
      key: 'approve',
      label: 'Freigeben/Senden',
      available: isCreditNoteReady,
      hint: isCreditNoteReady ? 'Freigabe, Versand und Druck sind als Aktionen vorhanden.' : 'Freigabe braucht vollstaendige Gutschrift.',
    },
    {
      key: 'evidence',
      label: 'Nachweis',
      available: hasReason && (hasSourceInvoice || hasReasonText),
      hint: hasSourceInvoice ? 'Ausgangsrechnung und Grund bilden den Nachweis.' : 'Ohne Ausgangsrechnung braucht die Gutschrift eine klare Begruendung.',
    },
    {
      key: 'audit',
      label: 'Pruefspur',
      available: Boolean(id || creditNote.number),
      hint: id || creditNote.number ? 'Gutschriftsnummer, Status, Grund und Aktionen bilden die Pruefspur.' : 'Pruefspur entsteht beim Speichern.',
    },
  ]

  return (
    <div className="space-y-4">
      <RoleFocusBar
        roles={creditNoteRoleProfiles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={roleFocus === 'all' ? 4 : 1}
        totalCount={4}
      />
      <ManagementDecisionPanel
        decision={{
          allowed: isCreditNoteReady,
          allowedLabel: 'Freigabefaehig',
          blockedLabel: 'Noch nicht freigabefaehig',
          summary: isCreditNoteReady
            ? `Die Gutschrift ist fachlich bereit. ${lines.length} Positionen, ${Number(creditNote.totalGross ?? 0).toFixed(2)} EUR brutto.`
            : `Vor Freigabe ist noch etwas offen: ${nextCreditNoteAction}`,
          blockerCount: [!hasCustomer, !hasReason, !hasLines, !hasAmount, !hasPaymentPath, isCancelled].filter(Boolean).length,
          nextFocus: nextCreditNoteAction,
          template: {
            label: 'Gutschriftenliste oeffnen',
            href: '/sales/credit-notes',
          },
        }}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTaskPlan title="Gutschriften-Freigabeplan" items={creditNoteTaskItems} />
        <div className="space-y-3">
          <NextActionPanel
            action={nextCreditNoteAction}
            tone={isCreditNoteReady ? 'emerald' : isCancelled ? 'red' : hasCustomer ? 'amber' : 'blue'}
          />
          <EvidenceTemplateLink link={{ label: 'Rechnungsliste pruefen', href: '/sales/rechnungen' }} />
        </div>
      </div>
      <CrudCapabilityChecklist capabilities={creditNoteCrudCapabilities} />
      <ObjectPage
        config={creditNoteConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        onAction={handleAction}
        loadingActionKey={loadingActionKey}
        isLoading={loading}
      />
    </div>
  )
}
