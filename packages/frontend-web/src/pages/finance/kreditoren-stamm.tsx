import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Kreditoren-Stammdaten
const kreditorenSchema = z.object({
  kreditorNummer: z.string().regex(/^\d{6,8}$/, "Kreditornummer muss 6-8-stellig sein"),
  firma: z.string().min(1, "Firma ist erforderlich"),
  ansprechpartner: z.string().optional(),
  strasse: z.string().min(1, "Straße ist erforderlich"),
  plz: z.string().regex(/^\d{5}$/, "PLZ muss 5-stellig sein"),
  ort: z.string().min(1, "Ort ist erforderlich"),
  land: z.string().default("DE"),
  telefon: z.string().optional(),
  email: z.string().email().optional().or(z.literal("")),
  ustId: z.string().optional(),
  steuernummer: z.string().optional(),

  // Bankverbindung
  iban: z.string().regex(/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/, "IBAN-Format ungültig").optional().or(z.literal("")),
  bic: z.string().optional(),
  bankname: z.string().optional(),
  kontoinhaber: z.string().optional(),

  // Konditionen
  zahlungsziel: z.number().min(0, "Zahlungsziel kann nicht negativ sein").default(30),
  skontoTage: z.number().min(0).default(0),
  skontoProzent: z.number().min(0).max(100).default(0),
  kreditlimit: z.number().min(0).default(0),

  // Compliance
  sanktionslisteGeprueft: z.boolean().default(false),
  sanktionslisteGeprueftAm: z.string().optional(),
  vertragsstatus: z.enum(['aktiv', 'gekündigt', 'gesperrt']),
  letzteLieferung: z.string().optional(),
  notizen: z.string().optional()
})

// Konfiguration für Kreditoren-Stammdaten ObjectPage
const kreditorenConfig: MaskConfig = {
  title: 'Kreditoren-Stammdaten',
  subtitle: 'Verwaltung von Lieferanten und Verbindlichkeiten',
  type: 'object-page',
  tabs: [
    {
      key: 'stammdaten',
      label: 'Stammdaten',
      fields: [
        {
          name: 'kreditorNummer',
          label: 'Kreditornummer',
          type: 'text',
          required: true,
          placeholder: 'z.B. 400001',
          maxLength: 8
        },
        {
          name: 'firma',
          label: 'Firma',
          type: 'text',
          required: true,
          placeholder: 'Firmenname'
        },
        {
          name: 'ansprechpartner',
          label: 'Ansprechpartner',
          type: 'text',
          placeholder: 'Vorname Nachname'
        },
        {
          name: 'strasse',
          label: 'Straße',
          type: 'text',
          required: true,
          placeholder: 'Straße Hausnummer'
        },
        {
          name: 'plz',
          label: 'PLZ',
          type: 'text',
          required: true,
          placeholder: '12345',
          maxLength: 5
        },
        {
          name: 'ort',
          label: 'Ort',
          type: 'text',
          required: true,
          placeholder: 'Stadt'
        },
        {
          name: 'land',
          label: 'Land',
          type: 'select',
          options: [
            { value: 'DE', label: 'Deutschland' },
            { value: 'AT', label: 'Österreich' },
            { value: 'CH', label: 'Schweiz' },
            { value: 'NL', label: 'Niederlande' },
            { value: 'FR', label: 'Frankreich' }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'kontakt',
      label: 'Kontakt',
      fields: [
        {
          name: 'telefon',
          label: 'Telefon',
          type: 'text',
          placeholder: '+49 123 456789'
        },
        {
          name: 'email',
          label: 'E-Mail',
          type: 'text',
          placeholder: 'info@firma.de'
        },
        {
          name: 'ustId',
          label: 'USt-ID',
          type: 'text',
          placeholder: 'DE123456789'
        },
        {
          name: 'steuernummer',
          label: 'Steuernummer',
          type: 'text',
          placeholder: '123/456/78901'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'bankverbindung',
      label: 'Bankverbindung',
      fields: [
        {
          name: 'iban',
          label: 'IBAN',
          type: 'text',
          placeholder: 'DE89370400440532013000'
        },
        {
          name: 'bic',
          label: 'BIC',
          type: 'text',
          placeholder: 'DEUTDEDBBER'
        },
        {
          name: 'bankname',
          label: 'Bankname',
          type: 'text',
          placeholder: 'Deutsche Bank'
        },
        {
          name: 'kontoinhaber',
          label: 'Kontoinhaber',
          type: 'text',
          placeholder: 'Firma GmbH'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'konditionen',
      label: 'Konditionen',
      fields: [
        {
          name: 'zahlungsziel',
          label: 'Zahlungsziel (Tage)',
          type: 'number'
        } as any,
        {
          name: 'skontoTage',
          label: 'Skonto-Tage',
          type: 'number'
        } as any,
        {
          name: 'skontoProzent',
          label: 'Skonto (%)',
          type: 'number'
        } as any,
        {
          name: 'kreditlimit',
          label: 'Kreditlimit (€)',
          type: 'number'
        } as any
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'compliance',
      label: 'Compliance',
      fields: [
        {
          name: 'sanktionslisteGeprueft',
          label: 'Sanktionsliste geprüft',
          type: 'boolean'
        },
        {
          name: 'sanktionslisteGeprueftAm',
          label: 'Geprüft am',
          type: 'date',
          readonly: true
        },
        {
          name: 'vertragsstatus',
          label: 'Vertragsstatus',
          type: 'select',
          required: true,
          options: [
            { value: 'aktiv', label: 'Aktiv' },
            { value: 'gekündigt', label: 'Gekündigt' },
            { value: 'gesperrt', label: 'Gesperrt' }
          ]
        },
        {
          name: 'letzteLieferung',
          label: 'Letzte Lieferung',
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
          name: 'notizen',
          label: 'Interne Notizen',
          type: 'textarea',
          placeholder: 'Zusätzliche Informationen zum Kreditor...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'validate',
      label: 'Validieren',
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'save',
      label: 'Speichern',
      type: 'primary',
      onClick: () => {}
    },
    {
      key: 'sanktionspruefung',
      label: 'Sanktionsprüfung',
      type: 'secondary',
      onClick: () => {}
    },
    {
      key: 'export',
      label: 'Export',
      type: 'secondary',
      onClick: () => {}
    }
  ],
  api: {
    baseUrl: '/api/finance/kreditoren',
    endpoints: {
      list: '/api/finance/kreditoren',
      get: '/api/finance/kreditoren/{id}',
      create: '/api/finance/kreditoren',
      update: '/api/finance/kreditoren/{id}',
      delete: '/api/finance/kreditoren/{id}'
      // sanctions: '/api/finance/kreditoren/{id}/sanctions',
      // export: '/api/finance/kreditoren/export'
    }
  },
  validation: kreditorenSchema,
  permissions: ['fibu.read', 'fibu.write']
}

export default function KreditorenStammPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: kreditorenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(kreditorenConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'save') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        navigate('/finance/kreditoren')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        alert('Validierung erfolgreich!')
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'sanktionspruefung') {
      // Sanktionsprüfung
      alert('Sanktionsprüfung-Funktion wird implementiert')
    } else if (action === 'export') {
      window.open('/api/finance/kreditoren/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/kreditoren')
  }

  return (
    <ObjectPage
      config={kreditorenConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}