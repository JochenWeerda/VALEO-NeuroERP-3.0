import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Zahlungslauf Kreditoren
const zahlungslaufSchema = z.object({
  laufNummer: z.string().min(1, "Laufnummer ist erforderlich"),
  ausfuehrungsDatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Ausführungsdatum muss YYYY-MM-DD Format haben"),
  gesamtBetrag: z.number().positive("Gesamtbetrag muss positiv sein"),
  anzahlZahlungen: z.number().min(1, "Mindestens eine Zahlung erforderlich"),
  status: z.enum(['entwurf', 'freigegeben', 'ausgefuehrt', 'storniert']),
  freigegebenAm: z.string().optional(),
  freigegebenDurch: z.string().optional(),
  ausgefuehrtAm: z.string().optional(),

  // SEPA-Details
  auftraggeberName: z.string().min(1, "Auftraggeber-Name ist erforderlich"),
  auftraggeberIban: z.string().regex(/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/, "IBAN-Format ungültig"),
  auftraggeberBic: z.string().min(1, "BIC ist erforderlich"),

  // Zahlungen
  zahlungen: z.array(z.object({
    kreditorId: z.string().min(1, "Kreditor ist erforderlich"),
    kreditorName: z.string().min(1, "Kreditor-Name ist erforderlich"),
    iban: z.string().regex(/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/, "IBAN-Format ungültig"),
    bic: z.string().min(1, "BIC ist erforderlich"),
    betrag: z.number().positive("Betrag muss positiv sein"),
    verwendungszweck: z.string().min(1, "Verwendungszweck ist erforderlich"),
    skontoGenutzt: z.boolean().default(false),
    skontoBetrag: z.number().min(0).default(0),
    opReferenz: z.string().optional()
  })).min(1, "Mindestens eine Zahlung erforderlich"),

  notizen: z.string().optional()
})

// Konfiguration für Zahlungslauf Kreditoren ObjectPage
const zahlungslaufConfig: MaskConfig = {
  title: 'Zahlungslauf Kreditoren',
  subtitle: 'SEPA-Überweisungen an Lieferanten erstellen und freigeben',
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
          placeholder: 'ZL-2025-001'
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
          name: 'anzahlZahlungen',
          label: 'Anzahl Zahlungen',
          type: 'number',
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'auftraggeber',
      label: 'Auftraggeber',
      fields: [
        {
          name: 'auftraggeberName',
          label: 'Name',
          type: 'text',
          required: true,
          placeholder: 'Ihre Firma GmbH'
        },
        {
          name: 'auftraggeberIban',
          label: 'IBAN',
          type: 'text',
          required: true,
          placeholder: 'DE89370400440532013000'
        },
        {
          name: 'auftraggeberBic',
          label: 'BIC',
          type: 'text',
          required: true,
          placeholder: 'DEUTDEDBBER'
        }
      ]
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
          onChange={(zahlungen) => {
            const gesamtBetrag = zahlungen.reduce((sum: number, z: any) => sum + (z.betrag || 0), 0)
            onChange({
              ...data,
              zahlungen,
              gesamtBetrag,
              anzahlZahlungen: zahlungen.length
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
          placeholder: 'Zusätzliche Informationen zum Zahlungslauf...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'add-payment',
      label: 'Zahlung hinzufügen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'validate',
      label: 'Validieren',
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
    baseUrl: '/api/finance/zahlungslauf-kreditoren',
    endpoints: {
      list: '/api/finance/zahlungslauf-kreditoren',
      get: '/api/finance/zahlungslauf-kreditoren/{id}',
      create: '/api/finance/zahlungslauf-kreditoren',
      update: '/api/finance/zahlungslauf-kreditoren/{id}',
      delete: '/api/finance/zahlungslauf-kreditoren/{id}'
    }
  } as any,
  validation: zahlungslaufSchema,
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin']
}

// Zahlungen-Tabelle Komponente
function ZahlungenTable({ data, onChange }: { data: any[], onChange: (data: any[]) => void }) {
  const addZahlung = () => {
    onChange([...data, {
      kreditorId: '',
      kreditorName: '',
      iban: '',
      bic: '',
      betrag: 0,
      verwendungszweck: '',
      skontoGenutzt: false,
      skontoBetrag: 0,
      opReferenz: ''
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

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Zahlungen</h3>
        <button
          onClick={addZahlung}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + Zahlung hinzufügen
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">Kreditor</th>
              <th className="px-4 py-2 border">IBAN</th>
              <th className="px-4 py-2 border">Betrag</th>
              <th className="px-4 py-2 border">Verwendungszweck</th>
              <th className="px-4 py-2 border">Skonto</th>
              <th className="px-4 py-2 border">OP-Ref</th>
              <th className="px-4 py-2 border">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {data.map((zahlung, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="text"
                      value={zahlung.kreditorId}
                      onChange={(e) => updateZahlung(index, 'kreditorId', e.target.value)}
                      className="w-full p-1 border rounded text-sm mb-1"
                      placeholder="Kreditor-Nr"
                    />
                    <input
                      type="text"
                      value={zahlung.kreditorName}
                      onChange={(e) => updateZahlung(index, 'kreditorName', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                      placeholder="Name"
                    />
                  </div>
                </td>
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="text"
                      value={zahlung.iban}
                      onChange={(e) => updateZahlung(index, 'iban', e.target.value)}
                      className="w-full p-1 border rounded text-sm mb-1"
                      placeholder="IBAN"
                    />
                    <input
                      type="text"
                      value={zahlung.bic}
                      onChange={(e) => updateZahlung(index, 'bic', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                      placeholder="BIC"
                    />
                  </div>
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
                  <input
                    type="text"
                    value={zahlung.verwendungszweck}
                    onChange={(e) => updateZahlung(index, 'verwendungszweck', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="Rechnung 12345"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <div>
                    <input
                      type="checkbox"
                      checked={zahlung.skontoGenutzt || false}
                      onChange={(e) => updateZahlung(index, 'skontoGenutzt', e.target.checked)}
                      className="mr-2"
                    />
                    <input
                      type="number"
                      step="0.01"
                      value={zahlung.skontoBetrag}
                      onChange={(e) => updateZahlung(index, 'skontoBetrag', parseFloat(e.target.value) || 0)}
                      className="w-20 p-1 border rounded text-sm"
                      placeholder="0.00"
                    />
                  </div>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={zahlung.opReferenz || ''}
                    onChange={(e) => updateZahlung(index, 'opReferenz', e.target.value)}
                    className="w-full p-1 border rounded text-sm"
                    placeholder="OP-12345"
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

export default function ZahlungslaufKreditorenPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: zahlungslaufConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(zahlungslaufConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'add-payment') {
      // Neue Zahlung hinzufügen wird in der Tabelle behandelt
      alert('Verwenden Sie die Tabelle um Zahlungen hinzuzufügen')
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        alert('Validierung erfolgreich!')
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'preview') {
      // SEPA-Vorschau
      window.open('/api/finance/zahlungslauf-kreditoren/preview', '_blank')
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
        navigate('/finance/zahlungslauf-kreditoren')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'export') {
      window.open('/api/finance/zahlungslauf-kreditoren/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('execute', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/zahlungslauf-kreditoren')
  }

  return (
    <ObjectPage
      config={zahlungslaufConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}