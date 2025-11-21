import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { toast } from '@/hooks/use-toast'

// Zod-Schema für Dunning
const dunningSchema = z.object({
  opId: z.string().min(1, "OP-Referenz ist erforderlich"),
  debitorId: z.string().min(1, "Debitor ist erforderlich"),
  dunningLevel: z.number().min(1).max(3, "Mahnstufe muss 1-3 sein"),
  dunningDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Mahndatum muss YYYY-MM-DD Format haben"),
  dueDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Fälligkeit muss YYYY-MM-DD Format haben"),
  amount: z.number().positive("Betrag muss positiv sein"),
  dunningFee: z.number().min(0, "Mahngebühr kann nicht negativ sein").default(0),
  interest: z.number().min(0, "Zinsen können nicht negativ sein").default(0),
  totalAmount: z.number().positive("Gesamtforderung muss positiv sein"),
  text: z.string().min(1, "Mahntext ist erforderlich"),
  paymentDeadline: z.string().optional(),
  status: z.enum(['created', 'sent', 'paid', 'escalated', 'collection']),
  sentDate: z.string().optional(),
  paymentDate: z.string().optional(),
  notes: z.string().optional(),
  reminderCount: z.number().min(0).default(0),
  lastReminderDate: z.string().optional()
})

// Konfiguration für Dunning ObjectPage
const dunningConfig: MaskConfig = {
  title: 'Mahnung erstellen/bearbeiten',
  subtitle: 'Mahnwesen für Zahlungserinnerungen und -mahnungen',
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: 'Grunddaten',
      fields: [
        {
          name: 'opId',
          label: 'OP-Referenz',
          type: 'text',
          required: true,
          placeholder: 'OP-2025-0001'
        },
        {
          name: 'debitorId',
          label: 'Debitor',
          type: 'lookup',
          required: true,
          endpoint: '/api/finance/debitors',
          displayField: 'name',
          valueField: 'id'
        },
        {
          name: 'dunningLevel',
          label: 'Mahnstufe',
          type: 'select',
          required: true,
          options: [
            { value: 1, label: '1. Mahnung' },
            { value: 2, label: '2. Mahnung' },
            { value: 3, label: '3. Mahnung' }
          ]
        },
        {
          name: 'dunningDate',
          label: 'Mahndatum',
          type: 'date',
          required: true
        },
        {
          name: 'dueDate',
          label: 'Ursprüngliche Fälligkeit',
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'created', label: 'Erstellt' },
            { value: 'sent', label: 'Versendet' },
            { value: 'paid', label: 'Bezahlt' },
            { value: 'escalated', label: 'Eskaliert' },
            { value: 'collection', label: 'Inkasso' }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'betrag',
      label: 'Betrag & Gebühren',
      fields: [
        {
          name: 'amount',
          label: 'Offener Betrag',
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: 'Aus OP übernommen'
        },
        {
          name: 'dunningFee',
          label: 'Mahngebühr',
          type: 'number',
          step: 0.01,
          placeholder: '5.00',
          helpText: 'Pauschale Mahngebühr je nach Mahnstufe'
        },
        {
          name: 'interest',
          label: 'Verzugszinsen',
          type: 'number',
          step: 0.01,
          placeholder: '0.00',
          helpText: 'Berechnete Verzugszinsen'
        },
        {
          name: 'totalAmount',
          label: 'Gesamtforderung',
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: 'Betrag + Gebühr + Zinsen'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'text',
      label: 'Mahntext',
      fields: [
        {
          name: 'text',
          label: 'Mahnungstext',
          type: 'textarea',
          required: true,
          placeholder: `Sehr geehrte Damen und Herren,

trotz Zahlungserinnerung steht Ihre Rechnung noch offen.
Wir bitten Sie, den offenen Betrag innerhalb der gesetzten Frist zu begleichen.

Bei Zahlungseingang innerhalb der Zahlungsfrist erlassen wir die Mahngebühr.

Mit freundlichen Grüßen`
        },
        {
          name: 'paymentDeadline',
          label: 'Zahlungsfrist',
          type: 'text',
          placeholder: '7 Tage'
        }
      ]
    },
    {
      key: 'versand',
      label: 'Versand & Zahlung',
      fields: [
        {
          name: 'sentDate',
          label: 'Versanddatum',
          type: 'date'
        },
        {
          name: 'paymentDate',
          label: 'Zahlungseingang',
          type: 'date'
        },
        {
          name: 'reminderCount',
          label: 'Erinnerungen gesendet',
          type: 'number',
          readonly: true,
          helpText: 'Anzahl der versendeten Zahlungserinnerungen'
        },
        {
          name: 'lastReminderDate',
          label: 'Letzte Erinnerung',
          type: 'date',
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'notizen',
      label: 'Notizen',
      fields: [
        {
          name: 'notes',
          label: 'Interne Notizen',
          type: 'textarea',
          placeholder: 'Zusätzliche Informationen zur Mahnung...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'generate',
      label: 'Mahnung generieren',
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
      key: 'send',
      label: 'Versenden',
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'payment',
      label: 'Zahlung buchen',
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'escalate',
      label: 'Eskalieren',
      type: 'danger',
      onClick: () => {}
    },
    {
      key: 'collection',
      label: 'Inkasso übergeben',
      type: 'danger',
      onClick: () => {}
    },
    {
      key: 'export',
      label: 'PDF Export',
      type: 'secondary',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/finance/dunning',
    endpoints: {
      list: '/api/finance/dunning',
      get: '/api/finance/dunning/{id}',
      create: '/api/finance/dunning',
      update: '/api/finance/dunning/{id}',
      delete: '/api/finance/dunning/{id}'
    }
  },
  validation: dunningSchema,
  permissions: ['finance.write', 'finance.dunning']
}

export default function DunningEditorPage(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: dunningConfig.api.baseUrl,
    id: id ?? 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(dunningConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
    if (action === 'generate') {
      // Mahnung generieren - berechne Gesamtforderung und generiere Text
      const gesamtForderung = (formData.amount as number || 0) + (formData.dunningFee as number || 0) + (formData.interest as number || 0)
      formData.totalAmount = gesamtForderung

      // Generiere Standard-Mahntext basierend auf Mahnstufe
      if (!formData.text || (formData.text as string).trim() === '') {
        const mahnstufe = formData.dunningLevel as number || 1
        const betrag = formData.amount as number || 0
        const frist = formData.paymentDeadline as string || '7 Tage'

        formData.text = `Sehr geehrte Damen und Herren,

trotz ${mahnstufe > 1 ? `${mahnstufe - 1}. Mahnung und ` : ''}Zahlungserinnerung steht Ihre Rechnung noch offen.
Wir bitten Sie, den offenen Betrag von ${betrag.toFixed(2)} € innerhalb von ${frist} zu begleichen.

Bei Zahlungseingang innerhalb der Zahlungsfrist erlassen wir die Mahngebühr.

Mit freundlichen Grüßen`
      }

      toast({
        title: 'Mahnung generiert',
        description: `Mahnung der Stufe ${formData.dunningLevel} wurde erstellt.`,
      })
    } else if (action === 'preview') {
      // Vorschau
      if (!id || id === 'new') {
        toast({
          variant: 'destructive',
          title: 'Fehler',
          description: 'Speichern Sie die Mahnung zuerst.',
        })
        return
      }
      window.open(`/api/finance/dunning/${id}/preview`, '_blank')
    } else if (action === 'send') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData({ ...formData, status: 'sent', sentDate: new Date().toISOString().split('T')[0] })
        setIsDirty(false)
        toast({
          title: 'Mahnung versendet',
          description: 'Die Mahnung wurde erfolgreich versendet.',
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
          title: 'Fehler',
          description: 'Speichern Sie die Mahnung zuerst.',
        })
        return
      }

      try {
        const response = await fetch(`/api/finance/dunning/${id}/payment`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            betrag: formData.totalAmount || 0,
            datum: new Date().toISOString().split('T')[0]
          })
        })

        if (response.ok) {
          formData.status = 'paid'
          formData.paymentDate = new Date().toISOString().split('T')[0]
          toast({
            title: 'Zahlung gebucht',
            description: 'Die Zahlung wurde erfolgreich gebucht.',
          })
        } else {
          const error = await response.json()
          toast({
            variant: 'destructive',
            title: 'Fehler bei Zahlung',
            description: error.detail || 'Zahlung konnte nicht gebucht werden.',
          })
        }
      } catch (error) {
        toast({
          variant: 'destructive',
          title: 'Netzwerkfehler',
          description: 'Verbindung zum Server fehlgeschlagen.',
        })
      }
    } else if (action === 'escalate') {
      if (window.confirm('Mahnung wirklich eskalieren?')) {
        try {
          await saveData({ ...formData, status: 'escalated' })
          setIsDirty(false)
          toast({
            title: 'Mahnung eskaliert',
            description: 'Die Mahnung wurde eskaliert.',
          })
          navigate('/finance/dunning')
        } catch (error) {
          // Error wird bereits in useMaskData behandelt
        }
      }
    } else if (action === 'collection') {
      if (window.confirm('Wirklich an Inkasso übergeben?')) {
        try {
          await saveData({ ...formData, status: 'collection' })
          setIsDirty(false)
          toast({
            title: 'Inkasso übergeben',
            description: 'Der Fall wurde an das Inkasso-Büro übergeben.',
          })
          navigate('/finance/dunning')
        } catch (error) {
          // Error wird bereits in useMaskData behandelt
        }
      }
    } else if (action === 'export') {
      if (!id || id === 'new') {
        toast({
          variant: 'destructive',
          title: 'Fehler',
          description: 'Speichern Sie die Mahnung zuerst.',
        })
        return
      }
      window.open(`/api/finance/dunning/${id}/export`, '_blank')
    }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
    await handleAction('send', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/dunning')
  }

  return (
    <ObjectPage
      config={dunningConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}