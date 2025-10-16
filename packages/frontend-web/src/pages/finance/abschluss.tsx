import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Monats-/Jahresabschluss
const abschlussSchema = z.object({
  periode: z.string().regex(/^\d{4}-\d{2}$/, "Periode muss YYYY-MM Format haben"),
  abschlussTyp: z.enum(['monatsabschluss', 'quartalsabschluss', 'jahresabschluss']),
  status: z.enum(['offen', 'in_bearbeitung', 'freigegeben', 'abgeschlossen', 'gesperrt']),
  freigegebenAm: z.string().optional(),
  freigegebenDurch: z.string().optional(),
  abgeschlossenAm: z.string().optional(),
  abgeschlossenDurch: z.string().optional(),

  // Salden
  eroeffnungsbilanz: z.number().default(0),
  schlussbilanz: z.number().default(0),
  gewinnVerlust: z.number().default(0),

  // GuV-Positionen
  umsatzErloese: z.number().default(0),
  bestandsveraenderungen: z.number().default(0),
  aktivierteEigenleistungen: z.number().default(0),
  sonstigeBetrieblicheErtraege: z.number().default(0),
  materialaufwand: z.number().default(0),
  personalaufwand: z.number().default(0),
  abschreibungen: z.number().default(0),
  sonstigeBetrieblicheAufwendungen: z.number().default(0),

  // Abgrenzungen
  rechnungsabgrenzungsposten: z.array(z.object({
    beschreibung: z.string(),
    betrag: z.number(),
    typ: z.enum(['aktiv', 'passiv'])
  })).optional(),

  // Rückstellungen
  rueckstellungen: z.array(z.object({
    beschreibung: z.string(),
    betrag: z.number(),
    zweck: z.string()
  })).optional(),

  // Prüfungen
  saldenListeGeprueft: z.boolean().default(false),
  kontenabstimmungDurchgefuehrt: z.boolean().default(false),
  inventurAbgeschlossen: z.boolean().default(false),
  steuerlichePruefungOk: z.boolean().default(false),

  notizen: z.string().optional()
})

// Konfiguration für Monats-/Jahresabschluss ObjectPage
const abschlussConfig: MaskConfig = {
  title: 'Monats-/Jahresabschluss',
  subtitle: 'Periodenabschluss durchführen und Buchungen sperren',
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
          name: 'abschlussTyp',
          label: 'Abschluss-Typ',
          type: 'select',
          required: true,
          options: [
            { value: 'monatsabschluss', label: 'Monatsabschluss' },
            { value: 'quartalsabschluss', label: 'Quartalsabschluss' },
            { value: 'jahresabschluss', label: 'Jahresabschluss' }
          ]
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'offen', label: 'Offen' },
            { value: 'in_bearbeitung', label: 'In Bearbeitung' },
            { value: 'freigegeben', label: 'Freigegeben' },
            { value: 'abgeschlossen', label: 'Abgeschlossen' },
            { value: 'gesperrt', label: 'Gesperrt' }
          ]
        },
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
          name: 'abgeschlossenAm',
          label: 'Abgeschlossen am',
          type: 'date',
          readonly: true
        },
        {
          name: 'abgeschlossenDurch',
          label: 'Abgeschlossen durch',
          type: 'text',
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'bilanz',
      label: 'Bilanz',
      fields: [
        {
          name: 'eroeffnungsbilanz',
          label: 'Eröffnungsbilanz',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'schlussbilanz',
          label: 'Schlussbilanz',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'gewinnVerlust',
          label: 'Gewinn/Verlust',
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: 'Schlussbilanz - Eröffnungsbilanz'
        }
      ],
      layout: 'grid',
      columns: 3
    },
    {
      key: 'guv',
      label: 'GuV',
      fields: [
        {
          name: 'umsatzErloese',
          label: 'Umsatzerlöse',
          type: 'number',
          step: 0.01
        },
        {
          name: 'bestandsveraenderungen',
          label: 'Bestandsveränderungen',
          type: 'number',
          step: 0.01
        },
        {
          name: 'aktivierteEigenleistungen',
          label: 'Aktivierte Eigenleistungen',
          type: 'number',
          step: 0.01
        },
        {
          name: 'sonstigeBetrieblicheErtraege',
          label: 'Sonstige betriebliche Erträge',
          type: 'number',
          step: 0.01
        },
        {
          name: 'materialaufwand',
          label: 'Materialaufwand',
          type: 'number',
          step: 0.01
        },
        {
          name: 'personalaufwand',
          label: 'Personalaufwand',
          type: 'number',
          step: 0.01
        },
        {
          name: 'abschreibungen',
          label: 'Abschreibungen',
          type: 'number',
          step: 0.01
        },
        {
          name: 'sonstigeBetrieblicheAufwendungen',
          label: 'Sonstige betriebliche Aufwendungen',
          type: 'number',
          step: 0.01
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'abgrenzungen',
      label: 'Abgrenzungen',
      fields: []
    } as any,
    {
      key: 'abgrenzungen_custom',
      label: '',
      fields: [],
      customRender: (data: any, onChange: (data: any) => void) => (
        <AbgrenzungenTable
          data={data.rechnungsabgrenzungsposten || []}
          onChange={(rechnungsabgrenzungsposten) => onChange({ ...data, rechnungsabgrenzungsposten })}
        />
      )
    },
    {
      key: 'rueckstellungen',
      label: 'Rückstellungen',
      fields: []
    } as any,
    {
      key: 'rueckstellungen_custom',
      label: '',
      fields: [],
      customRender: (data: any, onChange: (data: any) => void) => (
        <RueckstellungenTable
          data={data.rueckstellungen || []}
          onChange={(rueckstellungen) => onChange({ ...data, rueckstellungen })}
        />
      )
    },
    {
      key: 'pruefungen',
      label: 'Prüfungen',
      fields: [
        {
          name: 'saldenListeGeprueft',
          label: 'Saldenliste geprüft',
          type: 'boolean'
        },
        {
          name: 'kontenabstimmungDurchgefuehrt',
          label: 'Kontenabstimmung durchgeführt',
          type: 'boolean'
        },
        {
          name: 'inventurAbgeschlossen',
          label: 'Inventur abgeschlossen',
          type: 'boolean'
        },
        {
          name: 'steuerlichePruefungOk',
          label: 'Steuerliche Prüfung OK',
          type: 'boolean'
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
          placeholder: 'Zusätzliche Informationen zum Abschluss...'
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
      key: 'close',
      label: 'Abschließen',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'lock',
      label: 'Sperren',
      type: 'danger'
    , onClick: () => {} },
    {
      key: 'export',
      label: 'Export',
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/abschluss',
    endpoints: {
      list: '/api/finance/abschluss',
      get: '/api/finance/abschluss/{id}',
      create: '/api/finance/abschluss',
      update: '/api/finance/abschluss/{id}',
      delete: '/api/finance/abschluss/{id}'
    }
  } as any,
  validation: abschlussSchema,
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin']
}

// Abgrenzungen-Tabelle Komponente
function AbgrenzungenTable({ data, onChange }: { data: any[], onChange: (data: any[]) => void }) {
  const addPosten = () => {
    onChange([...data, {
      beschreibung: '',
      betrag: 0,
      typ: 'aktiv'
    }])
  }

  const updatePosten = (index: number, field: string, value: any) => {
    const newData = [...data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removePosten = (index: number) => {
    onChange(data.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Rechnungsabgrenzungsposten</h3>
        <button
          onClick={addPosten}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + Posten hinzufügen
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">Beschreibung</th>
              <th className="px-4 py-2 border">Betrag</th>
              <th className="px-4 py-2 border">Typ</th>
              <th className="px-4 py-2 border">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {data.map((posten, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={posten.beschreibung}
                    onChange={(e) => updatePosten(index, 'beschreibung', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="z.B. Mietvorauszahlung"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={posten.betrag}
                    onChange={(e) => updatePosten(index, 'betrag', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <select
                    value={posten.typ}
                    onChange={(e) => updatePosten(index, 'typ', e.target.value)}
                    className="w-full p-1 border rounded"
                  >
                    <option value="aktiv">Aktiv</option>
                    <option value="passiv">Passiv</option>
                  </select>
                </td>
                <td className="px-4 py-2 border">
                  <button
                    onClick={() => removePosten(index)}
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

// Rückstellungen-Tabelle Komponente
function RueckstellungenTable({ data, onChange }: { data: any[], onChange: (data: any[]) => void }) {
  const addRueckstellung = () => {
    onChange([...data, {
      beschreibung: '',
      betrag: 0,
      zweck: ''
    }])
  }

  const updateRueckstellung = (index: number, field: string, value: any) => {
    const newData = [...data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeRueckstellung = (index: number) => {
    onChange(data.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Rückstellungen</h3>
        <button
          onClick={addRueckstellung}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + Rückstellung hinzufügen
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">Beschreibung</th>
              <th className="px-4 py-2 border">Betrag</th>
              <th className="px-4 py-2 border">Zweck</th>
              <th className="px-4 py-2 border">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {data.map((rueckstellung, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={rueckstellung.beschreibung}
                    onChange={(e) => updateRueckstellung(index, 'beschreibung', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="z.B. Prozesskosten"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={rueckstellung.betrag}
                    onChange={(e) => updateRueckstellung(index, 'betrag', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={rueckstellung.zweck}
                    onChange={(e) => updateRueckstellung(index, 'zweck', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="z.B. Für erwartete Gerichtskosten"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <button
                    onClick={() => removeRueckstellung(index)}
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

export default function AbschlussPage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: abschlussConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(abschlussConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'calculate') {
      // Berechnung durchführen
      alert('Abschlussberechnung-Funktion wird implementiert')
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        alert('Abschlussprüfung erfolgreich!')
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'approve') {
      // Freigeben
      alert('Abschlussfreigabe-Funktion wird implementiert')
    } else if (action === 'close') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        navigate('/finance/abschluss')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'lock') {
      // Sperren
      alert('Periodensperre-Funktion wird implementiert')
    } else if (action === 'export') {
      window.open('/api/finance/abschluss/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('close', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/abschluss')
  }

  return (
    <ObjectPage
      config={abschlussConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}