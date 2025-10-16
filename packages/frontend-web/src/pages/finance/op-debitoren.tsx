import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für OP-Debitoren
const opDebitorenSchema = z.object({
  debitorId: z.string().min(1, "Debitor ist erforderlich"),
  opNummer: z.string().min(1, "OP-Nummer ist erforderlich"),
  rechnungId: z.string().optional(),
  buchungsdatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Buchungsdatum muss YYYY-MM-DD Format haben"),
  faelligkeit: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Fälligkeit muss YYYY-MM-DD Format haben"),
  betrag: z.number().positive("Betrag muss positiv sein"),
  waehrung: z.string().default("EUR"),
  offen: z.number().min(0, "Offener Betrag kann nicht negativ sein"),
  skontoBetrag: z.number().min(0).optional(),
  skontoDatum: z.string().optional(),
  zahlungen: z.array(z.object({
    datum: z.string(),
    betrag: z.number(),
    typ: z.enum(['zahlung', 'skonto', 'gutschrift', 'storno']),
    referenz: z.string().optional()
  })).optional(),
  status: z.enum(['offen', 'teilbezahlt', 'ausgeglichen', 'mahnung', 'inkasso']),
  letzteZahlung: z.string().optional(),
  mahnstufe: z.number().min(0).max(3).default(0),
  notizen: z.string().optional()
})

// Konfiguration für OP-Debitoren ObjectPage
const opDebitorenConfig: MaskConfig = {
  title: 'OP-Verwaltung (Debitoren)',
  subtitle: 'Offene Posten verwalten und Zahlungen zuordnen',
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: 'Grunddaten',
      fields: [
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
          name: 'opNummer',
          label: 'OP-Nummer',
          type: 'text',
          required: true,
          placeholder: 'OP-2025-0001'
        },
        {
          name: 'rechnungId',
          label: 'Rechnung',
          type: 'text',
          placeholder: 'RE-2025-0001'
        },
        {
          name: 'buchungsdatum',
          label: 'Buchungsdatum',
          type: 'date',
          required: true
        },
        {
          name: 'faelligkeit',
          label: 'Fälligkeit',
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'offen', label: 'Offen' },
            { value: 'teilbezahlt', label: 'Teilbezahlt' },
            { value: 'ausgeglichen', label: 'Ausgeglichen' },
            { value: 'mahnung', label: 'Mahnung' },
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
          label: 'Gesamtbetrag',
          type: 'number',
          required: true,
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'waehrung',
          label: 'Währung',
          type: 'select',
          options: [
            { value: 'EUR', label: 'EUR' },
            { value: 'USD', label: 'USD' },
            { value: 'GBP', label: 'GBP' }
          ]
        },
        {
          name: 'offen',
          label: 'Offener Betrag',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'skontoBetrag',
          label: 'Skonto-Betrag',
          type: 'number',
          step: 0.01,
          helpText: 'Verfügbarer Skonto-Betrag'
        },
        {
          name: 'skontoDatum',
          label: 'Skonto bis',
          type: 'date',
          helpText: 'Skonto-Frist'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'zahlungen',
      label: 'Zahlungen',
      fields: []
    } as any,
    {
      key: 'zahlungen_custom',
      label: '',
      fields: [],
      customRender: (data: any, onChange: (data: any) => void) => (
        <ZahlungenTable
          data={data.zahlungen || []}
          gesamtBetrag={data.betrag || 0}
          onChange={(zahlungen) => {
            const totalPaid = zahlungen.reduce((sum: number, z: any) => sum + (z.betrag || 0), 0)
            onChange({
              ...data,
              zahlungen,
              offen: (data.betrag || 0) - totalPaid,
              letzteZahlung: zahlungen.length > 0 ? zahlungen[zahlungen.length - 1].datum : data.letzteZahlung
            })
          }}
        />
      )
    },
    {
      key: 'mahnwesen',
      label: 'Mahnwesen',
      fields: [
        {
          name: 'mahnstufe',
          label: 'Mahnstufe',
          type: 'select',
          options: [
            { value: 0, label: '0 - Keine Mahnung' },
            { value: 1, label: '1. Mahnung' },
            { value: 2, label: '2. Mahnung' },
            { value: 3, label: '3. Mahnung' }
          ]
        },
        {
          name: 'letzteZahlung',
          label: 'Letzte Zahlung',
          type: 'date',
          readonly: true
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
          placeholder: 'Zusätzliche Informationen zur Forderung...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'zahlung',
      label: 'Zahlung buchen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'skonto',
      label: 'Skonto nutzen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'ausgleich',
      label: 'Ausgleichen',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'mahnung',
      label: 'Mahnung erstellen',
      type: 'danger',
      onClick: () => {}
    },
    {
      key: 'export',
      label: 'Export',
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/op-debitoren',
    endpoints: {
      list: '/api/finance/op-debitoren',
      get: '/api/finance/op-debitoren/{id}',
      create: '/api/finance/op-debitoren',
      update: '/api/finance/op-debitoren/{id}',
      delete: '/api/finance/op-debitoren/{id}'
    }
  } as any,
  validation: opDebitorenSchema,
  permissions: ['fibu.read', 'fibu.write']
}

// Zahlungen-Tabelle Komponente
function ZahlungenTable({ data, gesamtBetrag, onChange }: {
  data: any[],
  gesamtBetrag: number,
  onChange: (data: any[]) => void
}) {
  const addZahlung = () => {
    onChange([...data, {
      datum: new Date().toISOString().split('T')[0],
      betrag: 0,
      typ: 'zahlung',
      referenz: ''
    }])
  }

  const updateZahlung = (index: number, field: string, value: any) => {
    const newData = [...data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeZahlung = (index: number) => {
    onChange(data.filter((_, i) => i !== index))
  }

  const totalPaid = data.reduce((sum, z) => sum + (z.betrag || 0), 0)
  const remaining = gesamtBetrag - totalPaid

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Zahlungen</h3>
        <div className="text-sm">
          <span className="font-semibold">Offen: {remaining.toFixed(2)} €</span>
          <button
            onClick={addZahlung}
            className="ml-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            + Zahlung hinzufügen
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">Datum</th>
              <th className="px-4 py-2 border">Betrag</th>
              <th className="px-4 py-2 border">Typ</th>
              <th className="px-4 py-2 border">Referenz</th>
              <th className="px-4 py-2 border">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {data.map((zahlung, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <input
                    type="date"
                    value={zahlung.datum}
                    onChange={(e) => updateZahlung(index, 'datum', e.target.value)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={zahlung.betrag}
                    onChange={(e) => updateZahlung(index, 'betrag', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <select
                    value={zahlung.typ}
                    onChange={(e) => updateZahlung(index, 'typ', e.target.value)}
                    className="w-full p-1 border rounded"
                  >
                    <option value="zahlung">Zahlung</option>
                    <option value="skonto">Skonto</option>
                    <option value="gutschrift">Gutschrift</option>
                    <option value="storno">Storno</option>
                  </select>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={zahlung.referenz || ''}
                    onChange={(e) => updateZahlung(index, 'referenz', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="z.B. Bank-123"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <button
                    onClick={() => removeZahlung(index)}
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

export default function OPDebitorenPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: opDebitorenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(opDebitorenConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'zahlung') {
      // Zahlung buchen
      alert('Zahlungsbuchung-Funktion wird implementiert')
    } else if (action === 'skonto') {
      // Skonto nutzen
      alert('Skonto-Funktion wird implementiert')
    } else if (action === 'ausgleich') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        navigate('/finance/op-debitoren')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'mahnung') {
      // Mahnung erstellen
      alert('Mahnung-Funktion wird implementiert')
    } else if (action === 'export') {
      window.open('/api/finance/op-debitoren/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('ausgleich', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/op-debitoren')
  }

  return (
    <ObjectPage
      config={opDebitorenConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}