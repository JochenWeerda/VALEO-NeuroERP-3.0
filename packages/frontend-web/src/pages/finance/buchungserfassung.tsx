import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Buchungserfassung
const buchungSchema = z.object({
  belegart: z.enum(['RE', 'GUT', 'STORNO', 'KASSE', 'BANK'], {
    errorMap: () => ({ message: "Belegart muss RE, GUT, STORNO, KASSE oder BANK sein" })
  }),
  belegnummer: z.string().min(1, "Belegnummer ist erforderlich"),
  buchungsdatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Buchungsdatum muss YYYY-MM-DD Format haben"),
  periode: z.string().regex(/^\d{4}-\d{2}$/, "Periode muss YYYY-MM Format haben"),
  buchungstext: z.string().min(1, "Buchungstext ist erforderlich"),
  gesamtSoll: z.number().min(0, "Soll darf nicht negativ sein"),
  gesamtHaben: z.number().min(0, "Haben darf nicht negativ sein"),
  differenz: z.number().max(0.01, "Soll und Haben müssen ausgeglichen sein").min(-0.01),
  buchungszeilen: z.array(z.object({
    konto: z.string().min(1, "Konto ist erforderlich"),
    soll: z.number().min(0),
    haben: z.number().min(0),
    steuerschluessel: z.string().optional(),
    kostenstelle: z.string().optional(),
    kostentraeger: z.string().optional(),
    beleg: z.string().optional()
  })).min(1, "Mindestens eine Buchungszeile erforderlich")
}).refine((data) => Math.abs(data.gesamtSoll - data.gesamtHaben) < 0.01, {
  message: "Soll und Haben müssen ausgeglichen sein",
  path: ["differenz"]
})

// Konfiguration für Buchungserfassung ObjectPage
const buchungConfig: MaskConfig = {
  title: 'Buchungserfassung (Journal)',
  subtitle: 'Manuelle Buchungserfassung mit Soll/Haben-Prüfung',
  type: 'object-page',
  tabs: [
    {
      key: 'allgemein',
      label: 'Allgemein',
      fields: [
        {
          name: 'belegart',
          label: 'Belegart',
          type: 'select',
          required: true,
          options: [
            { value: 'RE', label: 'RE - Rechnung' },
            { value: 'GUT', label: 'GUT - Gutschrift' },
            { value: 'STORNO', label: 'STORNO - Storno' },
            { value: 'KASSE', label: 'KASSE - Kassenbeleg' },
            { value: 'BANK', label: 'BANK - Bankbeleg' }
          ]
        },
        {
          name: 'belegnummer',
          label: 'Belegnummer',
          type: 'text',
          required: true,
          placeholder: 'Automatisch generiert'
        },
        {
          name: 'buchungsdatum',
          label: 'Buchungsdatum',
          type: 'date',
          required: true
        },
        {
          name: 'periode',
          label: 'Periode',
          type: 'text',
          required: true,
          placeholder: '2025-01',
          pattern: '^\\d{4}-\\d{2}$'
         } as any, {},
        {
          name: 'buchungstext',
          label: 'Buchungstext',
          type: 'text',
          required: true,
          placeholder: 'z.B. Wareneinkauf Bürobedarf'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'buchungszeilen',
      label: 'Buchungszeilen',
      fields: []
    } as any,
    {
      key: 'buchungszeilen_custom',
      label: '',
      fields: [],
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <BuchungszeilenTable
          data={_data.buchungszeilen || []}
          onChange={(zeilen) => {
            const gesamtSoll = zeilen.reduce((sum: number, z: any) => sum + (z.soll || 0), 0)
            const gesamtHaben = zeilen.reduce((sum: number, z: any) => sum + (z.haben || 0), 0)
            onChange({
              ..._data,
              buchungszeilen: zeilen,
              gesamtSoll,
              gesamtHaben,
              differenz: gesamtSoll - gesamtHaben
            })
          }}
        />
      )
    },
    {
      key: 'summen',
      label: 'Summenprüfung',
      fields: [
        {
          name: 'gesamtSoll',
          label: 'Gesamt Soll',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'gesamtHaben',
          label: 'Gesamt Haben',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'differenz',
          label: 'Differenz',
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: 'Muss 0,00 sein für gültige Buchung'
        }
      ],
      layout: 'grid',
      columns: 3
    },
    {
      key: 'anhaenge',
      label: 'Anhänge',
      fields: [
        {
          name: 'belegUpload',
          label: 'Beleg hochladen',
          type: 'file',
          accept: '.pdf,.jpg,.jpeg,.png',
           } as any, {helpText: 'GoBD: Belege müssen digital archiviert werden'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'validate',
      label: 'Prüfen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'save',
      label: 'Buchen',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'storno',
      label: 'Storno',
      type: 'danger'
    , onClick: () => {} },
    {
      key: 'export',
      label: 'DATEV Export',
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/buchungen',
    endpoints: {
      list: '/api/finance/buchungen',
      get: '/api/finance/buchungen/{id}',
      create: '/api/finance/buchungen',
      update: '/api/finance/buchungen/{id}',
      delete: '/api/finance/buchungen/{id}'
    }
  } as any,
  validation: buchungSchema,
  permissions: ['fibu.read', 'fibu.write']
}

// Buchungszeilen-Tabelle Komponente
function BuchungszeilenTable({ data: _data, onChange }: { data: any[], onChange: (_data: any[]) => void }) {
  const addRow = () => {
    onChange([..._data, {
      konto: '',
      soll: 0,
      haben: 0,
      steuerschluessel: '',
      kostenstelle: '',
      kostentraeger: '',
      beleg: ''
    }])
  }

  const updateRow = (index: number, field: string, value: any) => {
    const newData = [..._data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeRow = (index: number) => {
    onChange(_data.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Buchungszeilen</h3>
        <button
          onClick={addRow}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + Zeile hinzufügen
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">Konto</th>
              <th className="px-4 py-2 border">Soll</th>
              <th className="px-4 py-2 border">Haben</th>
              <th className="px-4 py-2 border">Steuer</th>
              <th className="px-4 py-2 border">KST</th>
              <th className="px-4 py-2 border">KTR</th>
              <th className="px-4 py-2 border">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {_data.map((row, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={row.konto}
                    onChange={(e) => updateRow(index, 'konto', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="Kontonummer"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={row.soll}
                    onChange={(e) => updateRow(index, 'soll', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={row.haben}
                    onChange={(e) => updateRow(index, 'haben', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={row.steuerschluessel}
                    onChange={(e) => updateRow(index, 'steuerschluessel', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="1,9,10"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={row.kostenstelle}
                    onChange={(e) => updateRow(index, 'kostenstelle', e.target.value)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={row.kostentraeger}
                    onChange={(e) => updateRow(index, 'kostentraeger', e.target.value)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <button
                    onClick={() => removeRow(index)}
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

export default function BuchungserfassungPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: buchungConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(buchungConfig.validation)

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
        navigate('/finance/buchungen')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        alert('Buchungsprüfung erfolgreich - Soll/Haben ausgeglichen!')
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'storno') {
      if (confirm('Buchung stornieren? Es wird eine Gegenbuchung erstellt.')) {
        // Storno-Logik würde hier implementiert
        alert('Storno-Funktion wird implementiert')
      }
    } else if (action === 'export') {
      window.open('/api/finance/buchungen/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('save', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/buchungen')
  }

  return (
    <ObjectPage
      config={buchungConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}