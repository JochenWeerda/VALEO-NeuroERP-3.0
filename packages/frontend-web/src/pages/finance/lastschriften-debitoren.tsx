import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Lastschriften Debitoren
const lastschriftenSchema = z.object({
  laufNummer: z.string().min(1, "Laufnummer ist erforderlich"),
  ausfuehrungsDatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Ausführungsdatum muss YYYY-MM-DD Format haben"),
  gesamtBetrag: z.number().positive("Gesamtbetrag muss positiv sein"),
  anzahlLastschriften: z.number().min(1, "Mindestens eine Lastschrift erforderlich"),
  status: z.enum(['entwurf', 'freigegeben', 'ausgefuehrt', 'storniert']),
  freigegebenAm: z.string().optional(),
  freigegebenDurch: z.string().optional(),
  ausgefuehrtAm: z.string().optional(),

  // SEPA-Details
  creditorId: z.string().min(1, "Creditor-ID ist erforderlich"),
  auftraggeberName: z.string().min(1, "Auftraggeber-Name ist erforderlich"),
  auftraggeberIban: z.string().regex(/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/, "IBAN-Format ungültig"),

  // Lastschriften
  lastschriften: z.array(z.object({
    debitorId: z.string().min(1, "Debitor ist erforderlich"),
    debitorName: z.string().min(1, "Debitor-Name ist erforderlich"),
    iban: z.string().regex(/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/, "IBAN-Format ungültig"),
    bic: z.string().optional(),
    betrag: z.number().positive("Betrag muss positiv sein"),
    mandatReferenz: z.string().min(1, "Mandatsreferenz ist erforderlich"),
    mandatDatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Mandatsdatum muss YYYY-MM-DD Format haben"),
    verwendungszweck: z.string().min(1, "Verwendungszweck ist erforderlich"),
    sequenzTyp: z.enum(['FRST', 'RCUR', 'FNAL', 'OOFF'], {
      errorMap: () => ({ message: "Sequenztyp muss FRST, RCUR, FNAL oder OOFF sein" })
    }),
    opReferenz: z.string().optional()
  })).min(1, "Mindestens eine Lastschrift erforderlich"),

  notizen: z.string().optional()
})

// Konfiguration für Lastschriften Debitoren ObjectPage
const lastschriftenConfig: MaskConfig = {
  title: 'Lastschriften Debitoren',
  subtitle: 'SEPA-Lastschriften von Kunden einziehen',
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: 'Grunddaten',
      fields: [
        {
          name: 'laufNummer',
          label: 'Laufnummer',
          type: 'text',
          required: true,
          placeholder: 'LS-2025-001'
        },
        {
          name: 'ausfuehrungsDatum',
          label: 'Ausführungsdatum',
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'entwurf', label: 'Entwurf' },
            { value: 'freigegeben', label: 'Freigegeben' },
            { value: 'ausgefuehrt', label: 'Ausgeführt' },
            { value: 'storniert', label: 'Storniert' }
          ]
        },
        {
          name: 'gesamtBetrag',
          label: 'Gesamtbetrag',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'anzahlLastschriften',
          label: 'Anzahl Lastschriften',
          type: 'number',
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'creditor',
      label: 'Creditor-Informationen',
      fields: [
        {
          name: 'creditorId',
          label: 'Creditor-ID (CI)',
          type: 'text',
          required: true,
          placeholder: 'DE98ZZZ09999999999'
        },
        {
          name: 'auftraggeberName',
          label: 'Auftraggeber-Name',
          type: 'text',
          required: true,
          placeholder: 'Ihre Firma GmbH'
        },
        {
          name: 'auftraggeberIban',
          label: 'Auftraggeber-IBAN',
          type: 'text',
          required: true,
          placeholder: 'DE89370400440532013000'
        }
      ]
    },
    {
      key: 'lastschriften',
      label: 'Lastschriften',
      fields: []
    } as any,
    {
      key: 'lastschriften_custom',
      label: '',
      fields: [],
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <LastschriftenTable
          data={_data.lastschriften || []}
          onChange={(lastschriften) => {
            const gesamtBetrag = lastschriften.reduce((sum: number, l: any) => sum + (l.betrag || 0), 0)
            onChange({
              ..._data,
              lastschriften,
              gesamtBetrag,
              anzahlLastschriften: lastschriften.length
            })
          }}
        />
      )
    },
    {
      key: 'freigabe',
      label: 'Freigabe & Ausführung',
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
          name: 'ausgefuehrtAm',
          label: 'Ausgeführt am',
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
          placeholder: 'Zusätzliche Informationen zum Lastschriftlauf...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'add-direct-debit',
      label: 'Lastschrift hinzufügen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'validate-mandates',
      label: 'Mandate prüfen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'preview',
      label: 'SEPA-Vorschau',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'approve',
      label: 'Freigeben',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'execute',
      label: 'Ausführen',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'export',
      label: 'SEPA-Export',
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/lastschriften-debitoren',
    endpoints: {
      list: '/api/finance/lastschriften-debitoren',
      get: '/api/finance/lastschriften-debitoren/{id}',
      create: '/api/finance/lastschriften-debitoren',
      update: '/api/finance/lastschriften-debitoren/{id}',
      delete: '/api/finance/lastschriften-debitoren/{id}'
    }
  } as any,
  validation: lastschriftenSchema,
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin']
}

// Lastschriften-Tabelle Komponente
function LastschriftenTable({ data: _data, onChange }: { data: any[], onChange: (_data: any[]) => void }) {
  const addLastschrift = () => {
    onChange([..._data, {
      debitorId: '',
      debitorName: '',
      iban: '',
      bic: '',
      betrag: 0,
      mandatReferenz: '',
      mandatDatum: '',
      verwendungszweck: '',
      sequenzTyp: 'FRST',
      opReferenz: ''
    }])
  }

  const updateLastschrift = (index: number, field: string, value: any) => {
    const newData = [..._data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeLastschrift = (index: number) => {
    onChange(_data.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Lastschriften</h3>
        <button
          onClick={addLastschrift}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + Lastschrift hinzufügen
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">Debitor</th>
              <th className="px-4 py-2 border">IBAN</th>
              <th className="px-4 py-2 border">Betrag</th>
              <th className="px-4 py-2 border">Mandat</th>
              <th className="px-4 py-2 border">Sequenz</th>
              <th className="px-4 py-2 border">Verwendungszweck</th>
              <th className="px-4 py-2 border">OP-Ref</th>
              <th className="px-4 py-2 border">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {_data.map((lastschrift, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="text"
                      value={lastschrift.debitorId}
                      onChange={(e) => updateLastschrift(index, 'debitorId', e.target.value)}
                      className="w-full p-1 border rounded text-sm mb-1"
                      placeholder="Debitor-Nr"
                    />
                    <input
                      type="text"
                      value={lastschrift.debitorName}
                      onChange={(e) => updateLastschrift(index, 'debitorName', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                      placeholder="Name"
                    />
                  </div>
                </td>
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="text"
                      value={lastschrift.iban}
                      onChange={(e) => updateLastschrift(index, 'iban', e.target.value)}
                      className="w-full p-1 border rounded text-sm mb-1"
                      placeholder="IBAN"
                    />
                    <input
                      type="text"
                      value={lastschrift.bic || ''}
                      onChange={(e) => updateLastschrift(index, 'bic', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                      placeholder="BIC (optional)"
                    />
                  </div>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={lastschrift.betrag}
                    onChange={(e) => updateLastschrift(index, 'betrag', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="text"
                      value={lastschrift.mandatReferenz}
                      onChange={(e) => updateLastschrift(index, 'mandatReferenz', e.target.value)}
                      className="w-full p-1 border rounded text-sm mb-1"
                      placeholder="Mandatsref."
                    />
                    <input
                      type="date"
                      value={lastschrift.mandatDatum}
                      onChange={(e) => updateLastschrift(index, 'mandatDatum', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                    />
                  </div>
                </td>
                <td className="px-4 py-2 border">
                  <select
                    value={lastschrift.sequenzTyp}
                    onChange={(e) => updateLastschrift(index, 'sequenzTyp', e.target.value)}
                    className="w-full p-1 border rounded"
                  >
                    <option value="FRST">FRST - Erste</option>
                    <option value="RCUR">RCUR - Wiederholung</option>
                    <option value="FNAL">FNAL - Letzte</option>
                    <option value="OOFF">OOFF - Einmalig</option>
                  </select>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={lastschrift.verwendungszweck}
                    onChange={(e) => updateLastschrift(index, 'verwendungszweck', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="Rechnung 12345"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={lastschrift.opReferenz || ''}
                    onChange={(e) => updateLastschrift(index, 'opReferenz', e.target.value)}
                    className="w-full p-1 border rounded text-sm"
                    placeholder="OP-12345"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <button
                    onClick={() => removeLastschrift(index)}
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

export default function LastschriftenDebitorenPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: lastschriftenConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(lastschriftenConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'add-direct-debit') {
      // Neue Lastschrift hinzufügen wird in der Tabelle behandelt
      alert('Verwenden Sie die Tabelle um Lastschriften hinzuzufügen')
    } else if (action === 'validate-mandates') {
      // Mandate prüfen
      alert('Mandatsprüfung-Funktion wird implementiert')
    } else if (action === 'preview') {
      // SEPA-Vorschau
      window.open('/api/finance/lastschriften-debitoren/preview', '_blank')
    } else if (action === 'approve') {
      // Freigeben
      alert('Freigabe-Funktion wird implementiert')
    } else if (action === 'execute') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        navigate('/finance/lastschriften-debitoren')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'export') {
      window.open('/api/finance/lastschriften-debitoren/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('execute', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/lastschriften-debitoren')
  }

  return (
    <ObjectPage
      config={lastschriftenConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}