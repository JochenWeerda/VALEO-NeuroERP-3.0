import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für CreditNote
const creditNoteSchema = z.object({
  number: z.string().min(1, "Gutschriftsnummer ist erforderlich"),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Datum muss YYYY-MM-DD Format haben"),
  customerId: z.string().min(1, "Kunde ist erforderlich"),
  sourceInvoice: z.string().optional(),
  sourceOrder: z.string().optional(),
  reason: z.enum(['return', 'discount', 'error', 'complaint', 'other'], {
    errorMap: () => ({ message: "Gültiger Grund erforderlich" })
  }),
  reasonText: z.string().optional(),
  paymentTerms: z.string().min(1, "Zahlungsbedingungen sind erforderlich"),
  dueDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Fälligkeitsdatum muss YYYY-MM-DD Format haben"),
  status: z.enum(['draft', 'approved', 'sent', 'paid', 'cancelled']),
  notes: z.string().optional(),
  lines: z.array(z.object({
    article: z.string().min(1, "Artikel ist erforderlich"),
    qty: z.number().positive("Menge muss positiv sein"),
    price: z.number().positive("Preis muss positiv sein"),
    vatRate: z.number().min(0).max(100, "MwSt-Satz muss 0-100% sein"),
    discount: z.number().min(0).max(100, "Rabatt muss 0-100% sein").default(0)
  })).min(1, "Mindestens eine Position erforderlich"),
  subtotalNet: z.number().min(0),
  totalTax: z.number().min(0),
  totalDiscount: z.number().min(0),
  totalGross: z.number().min(0)
})

// Konfiguration für CreditNote ObjectPage
const creditNoteConfig: MaskConfig = {
  title: 'Gutschrift erstellen/bearbeiten',
  subtitle: 'Gutschriften für Korrekturen und Rückerstattungen',
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: 'Grunddaten',
      fields: [
        {
          name: 'number',
          label: 'Gutschriftsnummer',
          type: 'text',
          required: true,
          placeholder: 'CN-2025-0001'
        },
        {
          name: 'date',
          label: 'Datum',
          type: 'date',
          required: true
        },
        {
          name: 'customerId',
          label: 'Kunde',
          type: 'lookup',
          required: true,
          endpoint: '/api/customers',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'sourceInvoice',
          label: 'Ursprungsrechnung',
          type: 'lookup',
          endpoint: '/api/invoices',
          displayField: 'number',
          valueField: 'id',
          helpText: 'Optionale Verknüpfung zur ursprünglichen Rechnung'
        },
        {
          name: 'reason',
          label: 'Grund',
          type: 'select',
          required: true,
          options: [
            { value: 'return', label: 'Rücksendung' },
            { value: 'discount', label: 'Nachlass' },
            { value: 'error', label: 'Fehlerkorrektur' },
            { value: 'complaint', label: 'Reklamation' },
            { value: 'other', label: 'Sonstiges' }
          ]
        },
        {
          name: 'reasonText',
          label: 'Grund-Details',
          type: 'textarea',
          placeholder: 'Detaillierte Begründung für die Gutschrift...'
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'draft', label: 'Entwurf' },
            { value: 'approved', label: 'Genehmigt' },
            { value: 'sent', label: 'Versendet' },
            { value: 'paid', label: 'Bezahlt' },
            { value: 'cancelled', label: 'Storniert' }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'positionen',
      label: 'Positionen',
      fields: [
        {
          name: 'lines',
          label: 'Gutschrifts-Positionen',
          type: 'table',
          required: true,
          columns: [
            { key: 'article', label: 'Artikel', type: 'lookup', required: true },
            { key: 'qty', label: 'Menge', type: 'number', required: true },
            { key: 'price', label: 'Preis', type: 'number', required: true },
            { key: 'vatRate', label: 'MwSt %', type: 'number', required: true },
            { key: 'discount', label: 'Rabatt %', type: 'number' }
          ],
          minRows: 1,
          helpText: 'Positionen der Gutschrift mit Artikeln, Mengen und Preisen'
        }
      ]
    },
    {
      key: 'betrag',
      label: 'Betrag',
      fields: [
        {
          name: 'subtotalNet',
          label: 'Netto-Betrag',
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: 'Summe aller Positionen ohne MwSt'
        },
        {
          name: 'totalDiscount',
          label: 'Gesamt-Rabatt',
          type: 'number',
          step: 0.01,
          readonly: true,
          helpText: 'Summe aller Rabatte'
        },
        {
          name: 'totalTax',
          label: 'MwSt Gesamt',
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: 'Gesamte Mehrwertsteuer'
        },
        {
          name: 'totalGross',
          label: 'Brutto-Betrag',
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: 'Endbetrag der Gutschrift'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'zahlung',
      label: 'Zahlung & Fälligkeit',
      fields: [
        {
          name: 'paymentTerms',
          label: 'Zahlungsbedingungen',
          type: 'select',
          required: true,
          options: [
            { value: 'immediate', label: 'Sofort' },
            { value: 'net30', label: '30 Tage netto' },
            { value: 'net60', label: '60 Tage netto' },
            { value: 'net90', label: '90 Tage netto' }
          ]
        },
        {
          name: 'dueDate',
          label: 'Fälligkeitsdatum',
          type: 'date',
          required: true
        }
      ]
    },
    {
      key: 'notizen',
      label: 'Notizen',
      fields: [
        {
          name: 'notes',
          label: 'Interne Notizen',
          type: 'textarea',
          placeholder: 'Zusätzliche Informationen zur Gutschrift...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'calculate',
      label: 'Neu berechnen',
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'preview',
      label: 'Vorschau',
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'approve',
      label: 'Genehmigen',
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'send',
      label: 'Versenden',
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'print',
      label: 'Drucken',
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'cancel',
      label: 'Stornieren',
      type: 'danger',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/sales/credit-notes',
    endpoints: {
      list: '/api/sales/credit-notes',
      get: '/api/sales/credit-notes/{id}',
      create: '/api/sales/credit-notes',
      update: '/api/sales/credit-notes/{id}',
      delete: '/api/sales/credit-notes/{id}'
    }
  },
  validation: creditNoteSchema,
  permissions: ['sales.write', 'sales.credit_notes']
}

export default function CreditNoteEditorPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: creditNoteConfig.api.baseUrl,
    id: id ?? 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(creditNoteConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
    if (action === 'calculate') {
      // Beträge neu berechnen
      alert('Neuberechnung-Funktion wird implementiert')
    } else if (action === 'preview') {
      // Vorschau anzeigen
      window.open('/api/sales/credit-notes/preview', '_blank')
    } else if (action === 'approve') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
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
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
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
      window.open('/api/sales/credit-notes/print', '_blank')
    } else if (action === 'cancel') {
      if (window.confirm('Gutschrift wirklich stornieren?')) {
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
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/sales/credit-notes')
  }

  return (
    <ObjectPage
      config={creditNoteConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}