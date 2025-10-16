import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für UStVA
const ustvaSchema = z.object({
  periode: z.string().regex(/^\d{4}-\d{2}$/, "Periode muss YYYY-MM Format haben"),
  voranmeldungszeitraum: z.enum(['monatlich', 'quartalsweise']),
  steuerpflichtiger: z.string().min(1, "Steuerpflichtiger ist erforderlich"),
  ustId: z.string().optional(),
  steuerberater: z.string().optional(),

  // Umsätze
  umsatz19: z.number().default(0),
  umsatz7: z.number().default(0),
  umsatz0: z.number().default(0),
  umsatzSonstige: z.number().default(0),
  gesamtUmsatz: z.number().default(0),

  // Vorsteuer
  vorsteuer19: z.number().default(0),
  vorsteuer7: z.number().default(0),
  vorsteuer0: z.number().default(0),
  vorsteuerSonstige: z.number().default(0),
  gesamtVorsteuer: z.number().default(0),

  // Berechnung
  ust19: z.number().default(0),
  ust7: z.number().default(0),
  ust0: z.number().default(0),
  ustSonstige: z.number().default(0),
  gesamtUst: z.number().default(0),

  // Abweichungen
  abweichungen: z.array(z.object({
    position: z.string(),
    beschreibung: z.string(),
    betrag: z.number(),
    grund: z.string()
  })).optional(),

  // Status
  status: z.enum(['entwurf', 'pruefung', 'freigegeben', 'abgegeben']),
  freigegebenAm: z.string().optional(),
  freigegebenDurch: z.string().optional(),
  abgegebenAm: z.string().optional(),
  elsterReferenz: z.string().optional(),
  notizen: z.string().optional()
})

// Konfiguration für UStVA ObjectPage
const ustvaConfig: MaskConfig = {
  title: 'Umsatzsteuervoranmeldung (UStVA)',
  subtitle: 'UStVA erstellen und an ELSTER übermitteln',
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: 'Grunddaten',
      fields: [
        {
          name: 'periode',
          label: 'Periode',
          type: 'text',
          required: true,
          placeholder: '2025-01',
          pattern: '^\\d{4}-\\d{2}$'
         } as any, {},
        {
          name: 'voranmeldungszeitraum',
          label: 'Voranmeldungszeitraum',
          type: 'select',
          required: true,
          options: [
            { value: 'monatlich', label: 'Monatlich' },
            { value: 'quartalsweise', label: 'Quartalsweise' }
          ]
        },
        {
          name: 'steuerpflichtiger',
          label: 'Steuerpflichtiger',
          type: 'text',
          required: true,
          placeholder: 'Firmenname'
        },
        {
          name: 'ustId',
          label: 'USt-ID',
          type: 'text',
          placeholder: 'DE123456789'
        },
        {
          name: 'steuerberater',
          label: 'Steuerberater',
          type: 'text',
          placeholder: 'Name des Steuerberaters'
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'entwurf', label: 'Entwurf' },
            { value: 'pruefung', label: 'In Prüfung' },
            { value: 'freigegeben', label: 'Freigegeben' },
            { value: 'abgegeben', label: 'Abgegeben' }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'umsatz',
      label: 'Umsätze',
      fields: [
        {
          name: 'umsatz19',
          label: 'Umsätze 19% (§66)',
          type: 'number',
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'umsatz7',
          label: 'Umsätze 7% (§35)',
          type: 'number',
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'umsatz0',
          label: 'Umsätze 0% (§48)',
          type: 'number',
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'umsatzSonstige',
          label: 'Sonstige Umsätze (§67)',
          type: 'number',
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'gesamtUmsatz',
          label: 'Gesamtumsatz',
          type: 'number',
          readonly: true,
          step: 0.01
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'vorsteuer',
      label: 'Vorsteuer',
      fields: [
        {
          name: 'vorsteuer19',
          label: 'Vorsteuer 19% (§60)',
          type: 'number',
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'vorsteuer7',
          label: 'Vorsteuer 7% (§61)',
          type: 'number',
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'vorsteuer0',
          label: 'Vorsteuer 0% (§62)',
          type: 'number',
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'vorsteuerSonstige',
          label: 'Sonstige Vorsteuer (§63)',
          type: 'number',
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'gesamtVorsteuer',
          label: 'Gesamtvorsteuer',
          type: 'number',
          readonly: true,
          step: 0.01
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'berechnung',
      label: 'Berechnung',
      fields: [
        {
          name: 'ust19',
          label: 'USt 19%',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'ust7',
          label: 'USt 7%',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'ust0',
          label: 'USt 0%',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'ustSonstige',
          label: 'USt Sonstige',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'gesamtUst',
          label: 'Gesamt USt',
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: 'Umsatzsteuer abzüglich Vorsteuer'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'abweichungen',
      label: 'Abweichungen',
      fields: []
    } as any,
    {
      key: 'abweichungen_custom',
      label: '',
      fields: [],
      customRender: (data: any, onChange: (data: any) => void) => (
        <AbweichungenTable
          data={data.abweichungen || []}
          onChange={(abweichungen) => onChange({ ...data, abweichungen })}
        />
      )
    },
    {
      key: 'freigabe',
      label: 'Freigabe & Abgabe',
      fields: [
        {
          name: 'freigegebenAm',
          label: 'Freigegeben am',
          type: 'date',
          readonly: true
        },
        {
          name: 'freigegebenDurch',
          label: 'Freigegeben durch',
          type: 'text',
          readonly: true
        },
        {
          name: 'abgegebenAm',
          label: 'Abgegeben am',
          type: 'date',
          readonly: true
        },
        {
          name: 'elsterReferenz',
          label: 'ELSTER-Referenz',
          type: 'text',
          readonly: true,
          placeholder: 'ELSTER-Bestätigungsnummer'
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
          placeholder: 'Zusätzliche Informationen zur UStVA...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'calculate',
      label: 'Berechnen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'validate',
      label: 'Prüfen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'approve',
      label: 'Freigeben',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'submit',
      label: 'An ELSTER übermitteln',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'export',
      label: 'XML Export',
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/ustva',
    endpoints: {
      list: '/api/finance/ustva',
      get: '/api/finance/ustva/{id}',
      create: '/api/finance/ustva',
      update: '/api/finance/ustva/{id}',
      delete: '/api/finance/ustva/{id}'
    }
  } as any,
  validation: ustvaSchema,
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin']
}

// Abweichungen-Tabelle Komponente
function AbweichungenTable({ data, onChange }: { data: any[], onChange: (data: any[]) => void }) {
  const addAbweichung = () => {
    onChange([...data, {
      position: '',
      beschreibung: '',
      betrag: 0,
      grund: ''
    }])
  }

  const updateAbweichung = (index: number, field: string, value: any) => {
    const newData = [...data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeAbweichung = (index: number) => {
    onChange(data.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Abweichungen</h3>
        <button
          onClick={addAbweichung}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + Abweichung hinzufügen
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">Position</th>
              <th className="px-4 py-2 border">Beschreibung</th>
              <th className="px-4 py-2 border">Betrag</th>
              <th className="px-4 py-2 border">Grund</th>
              <th className="px-4 py-2 border">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {data.map((abweichung, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={abweichung.position}
                    onChange={(e) => updateAbweichung(index, 'position', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="z.B. §66"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={abweichung.beschreibung}
                    onChange={(e) => updateAbweichung(index, 'beschreibung', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="Beschreibung der Abweichung"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={abweichung.betrag}
                    onChange={(e) => updateAbweichung(index, 'betrag', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={abweichung.grund}
                    onChange={(e) => updateAbweichung(index, 'grund', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="Begründung"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <button
                    onClick={() => removeAbweichung(index)}
                    className="px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    ✕
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function UStVAPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: ustvaConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(ustvaConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'calculate') {
      // Berechnung durchführen
      alert('UStVA-Berechnung-Funktion wird implementiert')
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        alert('UStVA-Validierung erfolgreich!')
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'approve') {
      // Freigeben
      alert('UStVA-Freigabe-Funktion wird implementiert')
    } else if (action === 'submit') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        navigate('/finance/ustva')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'export') {
      window.open('/api/finance/ustva/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('submit', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/ustva')
  }

  return (
    <ObjectPage
      config={ustvaConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}