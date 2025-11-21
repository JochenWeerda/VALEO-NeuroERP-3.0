import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { toast } from '@/hooks/use-toast'

// Zod-Schema für Mahnwesen
const mahnwesenSchema = z.object({
  opId: z.string().min(1, "OP-Referenz ist erforderlich"),
  debitorId: z.string().min(1, "Debitor ist erforderlich"),
  mahnstufe: z.number().min(1).max(3, "Mahnstufe muss 1-3 sein"),
  mahnDatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Mahndatum muss YYYY-MM-DD Format haben"),
  faelligkeit: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Fälligkeit muss YYYY-MM-DD Format haben"),
  betrag: z.number().positive("Betrag muss positiv sein"),
  mahngebuehr: z.number().min(0, "Mahngebühr kann nicht negativ sein").default(0),
  zinsen: z.number().min(0, "Zinsen können nicht negativ sein").default(0),
  gesamtForderung: z.number().positive("Gesamtforderung muss positiv sein"),
  text: z.string().min(1, "Mahntext ist erforderlich"),
  frist: z.string().optional(),
  status: z.enum(['erstellt', 'versendet', 'bezahlt', 'inkasso']),
  versandDatum: z.string().optional(),
  zahlungEingang: z.string().optional(),
  notizen: z.string().optional()
})

// Konfiguration für Mahnwesen ObjectPage
const mahnwesenConfig: MaskConfig = {
  title: 'Mahnwesen',
  subtitle: 'Mahnungen erstellen und verwalten',
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
          type: 'select',
          required: true,
          options: [
            { value: 'K001', label: 'K001 - Müller GmbH' },
            { value: 'K002', label: 'K002 - Schmidt KG' },
            { value: 'K003', label: 'K003 - Bauer e.K.' }
          ]
        },
        {
          name: 'mahnstufe',
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
          name: 'mahnDatum',
          label: 'Mahndatum',
          type: 'date',
          required: true
        },
        {
          name: 'faelligkeit',
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
            { value: 'erstellt', label: 'Erstellt' },
            { value: 'versendet', label: 'Versendet' },
            { value: 'bezahlt', label: 'Bezahlt' },
            { value: 'inkasso', label: 'Inkasso' }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'betrag',
      label: 'Betrag',
      fields: [
        {
          name: 'betrag',
          label: 'Offener Betrag',
          type: 'number',
          required: true,
          step: 0.01,
          readonly: true,
          helpText: 'Aus OP übernommen'
        },
        {
          name: 'mahngebuehr',
          label: 'Mahngebühr',
          type: 'number',
          step: 0.01,
          placeholder: '5.00',
          helpText: 'Pauschale Mahngebühr'
        },
        {
          name: 'zinsen',
          label: 'Verzugszinsen',
          type: 'number',
          step: 0.01,
          placeholder: '0.00',
          helpText: 'Berechnete Verzugszinsen'
        },
        {
          name: 'gesamtForderung',
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
Wir bitten Sie, den offenen Betrag innerhalb von 7 Tagen zu begleichen.

Bei Zahlungseingang innerhalb der Zahlungsfrist erlassen wir die Mahngebühr.

Mit freundlichen Grüßen`
        },
        {
          name: 'frist',
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
          name: 'versandDatum',
          label: 'Versanddatum',
          type: 'date'
        },
        {
          name: 'zahlungEingang',
          label: 'Zahlungseingang',
          type: 'date'
        }
      ]
    },
    {
      key: 'notizen',
      label: 'Notizen',
      fields: [
        {
          name: 'notizen',
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
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'preview',
      label: 'Vorschau',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'send',
      label: 'Versenden',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'payment',
      label: 'Zahlung buchen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'inkasso',
      label: 'Inkasso übergeben',
      type: 'danger'
    , onClick: () => {} },
    {
      key: 'export',
      label: 'PDF Export',
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/mahnwesen',
    endpoints: {
      list: '/api/finance/mahnwesen',
      get: '/api/finance/mahnwesen/{id}',
      create: '/api/finance/mahnwesen',
      update: '/api/finance/mahnwesen/{id}',
      delete: '/api/finance/mahnwesen/{id}'
    }
  } as any,
  validation: mahnwesenSchema,
  permissions: ['fibu.read', 'fibu.write']
}

export default function MahnwesenPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: mahnwesenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(mahnwesenConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'generate') {
      // Mahnung generieren - berechne Gesamtforderung
      const gesamtForderung = (formData.betrag || 0) + (formData.mahngebuehr || 0) + (formData.zinsen || 0)
      formData.gesamtForderung = gesamtForderung

      // Generiere Standard-Mahntext basierend auf Mahnstufe
      if (!formData.text || formData.text.trim() === '') {
        const mahnstufe = formData.mahnstufe || 1
        const betrag = formData.betrag || 0
        const frist = formData.frist || '7 Tage'

        formData.text = `Sehr geehrte Damen und Herren,

trotz ${mahnstufe > 1 ? `${mahnstufe - 1}. Mahnung und ` : ''}Zahlungserinnerung steht Ihre Rechnung noch offen.
Wir bitten Sie, den offenen Betrag von ${betrag.toFixed(2)} € innerhalb von ${frist} zu begleichen.

Bei Zahlungseingang innerhalb der Zahlungsfrist erlassen wir die Mahngebühr.

Mit freundlichen Grüßen`
      }

      toast({
        title: 'Mahnung generiert',
        description: `Mahnung der Stufe ${formData.mahnstufe} wurde erstellt.`,
      })
    } else if (action === 'preview') {
      // Vorschau
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: 'Fehler',
          description: 'Speichern Sie die Mahnung zuerst.',
        })
        return
      }
      window.open(`/api/finance/mahnwesen/${formData.id}/preview`, '_blank')
    } else if (action === 'send') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        toast({
          title: 'Mahnung versendet',
          description: 'Die Mahnung wurde erfolgreich versendet.',
        })
        navigate('/finance/mahnwesen')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'payment') {
      // Zahlung buchen
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: 'Fehler',
          description: 'Speichern Sie die Mahnung zuerst.',
        })
        return
      }

      try {
        const response = await fetch(`/api/finance/mahnwesen/${formData.id}/payment`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            betrag: formData.gesamtForderung || 0,
            datum: new Date().toISOString().split('T')[0]
          })
        })

        if (response.ok) {
          formData.status = 'bezahlt'
          formData.zahlungEingang = new Date().toISOString().split('T')[0]
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
    } else if (action === 'inkasso') {
      // Inkasso übergeben
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: 'Fehler',
          description: 'Speichern Sie die Mahnung zuerst.',
        })
        return
      }

      try {
        const response = await fetch(`/api/finance/mahnwesen/${formData.id}/inkasso`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        })

        if (response.ok) {
          formData.status = 'inkasso'
          toast({
            title: 'Inkasso übergeben',
            description: 'Der Fall wurde an das Inkasso-Büro übergeben.',
          })
        } else {
          const error = await response.json()
          toast({
            variant: 'destructive',
            title: 'Fehler bei Inkasso-Übergabe',
            description: error.detail || 'Inkasso-Übergabe fehlgeschlagen.',
          })
        }
      } catch (error) {
        toast({
          variant: 'destructive',
          title: 'Netzwerkfehler',
          description: 'Verbindung zum Server fehlgeschlagen.',
        })
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: 'Fehler',
          description: 'Speichern Sie die Mahnung zuerst.',
        })
        return
      }
      window.open(`/api/finance/mahnwesen/${formData.id}/export`, '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('send', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/mahnwesen')
  }

  return (
    <ObjectPage
      config={mahnwesenConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}