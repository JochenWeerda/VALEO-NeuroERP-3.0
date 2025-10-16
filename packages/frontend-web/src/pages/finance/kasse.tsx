import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'

// Zod-Schema für Kasse
const kasseSchema = z.object({
  datum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Datum muss YYYY-MM-DD Format haben"),
  kassenbuchNummer: z.string().min(1, "Kassenbuch-Nummer ist erforderlich"),
  anfangsbestand: z.number().min(0, "Anfangsbestand kann nicht negativ sein"),
  sollEinlagen: z.number().min(0, "Soll-Einlagen können nicht negativ sein"),
  sollAuszahlungen: z.number().min(0, "Soll-Auszahlungen können nicht negativ sein"),
  istEinlagen: z.number().min(0, "Ist-Einlagen können nicht negativ sein"),
  istAuszahlungen: z.number().min(0, "Ist-Auszahlungen können nicht negativ sein"),
  endbestand: z.number().min(0, "Endbestand kann nicht negativ sein"),
  differenz: z.number().max(0.01, "Kassendifferenz muss 0,00 sein"),
  status: z.enum(['offen', 'geschlossen', 'freigegeben']),
  freigegebenAm: z.string().optional(),
  freigegebenDurch: z.string().optional(),

  // Kassenbewegungen
  bewegungen: z.array(z.object({
    typ: z.enum(['einlage', 'auszahlung']),
    betrag: z.number().positive("Betrag muss positiv sein"),
    verwendungszweck: z.string().min(1, "Verwendungszweck ist erforderlich"),
    belegNummer: z.string().optional(),
    konto: z.string().optional()
  })).optional(),

  // Kassensturz
  kassensturz: z.object({
    scheine: z.record(z.string(), z.number().min(0)),
    muenzen: z.record(z.string(), z.number().min(0)),
    gesamtGezaehlt: z.number().min(0),
    differenzKassensturz: z.number().max(0.01, "Kassensturzdifferenz muss 0,00 sein")
  }).optional(),

  notizen: z.string().optional()
})

// Konfiguration für Kasse ObjectPage
const kasseConfig: MaskConfig = {
  title: 'Kasse',
  subtitle: 'Tagesabschluss und Kassenbuchführung',
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: 'Grunddaten',
      fields: [
        {
          name: 'datum',
          label: 'Datum',
          type: 'date',
          required: true
        },
        {
          name: 'kassenbuchNummer',
          label: 'Kassenbuch-Nr.',
          type: 'text',
          required: true,
          placeholder: 'KB-2025-001'
        },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          required: true,
          options: [
            { value: 'offen', label: 'Offen' },
            { value: 'geschlossen', label: 'Geschlossen' },
            { value: 'freigegeben', label: 'Freigegeben' }
          ]
        },
        {
          name: 'anfangsbestand',
          label: 'Anfangsbestand',
          type: 'number',
          required: true,
          step: 0.01,
          placeholder: '0.00'
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'soll',
      label: 'Soll-Buchungen',
      fields: [
        {
          name: 'sollEinlagen',
          label: 'Soll-Einlagen',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'sollAuszahlungen',
          label: 'Soll-Auszahlungen',
          type: 'number',
          readonly: true,
          step: 0.01
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'ist',
      label: 'Ist-Buchungen',
      fields: [
        {
          name: 'istEinlagen',
          label: 'Ist-Einlagen',
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'istAuszahlungen',
          label: 'Ist-Auszahlungen',
          type: 'number',
          readonly: true,
          step: 0.01
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'bewegungen',
      label: 'Kassenbewegungen',
      fields: []
    } as any,
    {
      key: 'bewegungen_custom',
      label: '',
      fields: [],
      customRender: (data: any, onChange: (data: any) => void) => (
        <KassenbewegungenTable
          data={data.bewegungen || []}
          onChange={(bewegungen) => {
            const sollEinlagen = bewegungen.filter((b: any) => b.typ === 'einlage').reduce((sum: number, b: any) => sum + (b.betrag || 0), 0)
            const sollAuszahlungen = bewegungen.filter((b: any) => b.typ === 'auszahlung').reduce((sum: number, b: any) => sum + (b.betrag || 0), 0)
            const istEinlagen = sollEinlagen // Vereinfacht - in Realität würden Ist-Werte manuell erfasst
            const istAuszahlungen = sollAuszahlungen
            const endbestand = (data.anfangsbestand || 0) + istEinlagen - istAuszahlungen
            const differenz = Math.abs(endbestand - (data.endbestand || 0))

            onChange({
              ...data,
              bewegungen,
              sollEinlagen,
              sollAuszahlungen,
              istEinlagen,
              istAuszahlungen,
              endbestand,
              differenz
            })
          }}
        />
      )
    },
    {
      key: 'kassensturz',
      label: 'Kassensturz',
      fields: []
    } as any,
    {
      key: 'kassensturz_custom',
      label: '',
      fields: [],
      customRender: (data: any, onChange: (data: any) => void) => (
        <KassensturzForm
          data={data.kassensturz || {
            scheine: {},
            muenzen: {},
            gesamtGezaehlt: 0,
            differenzKassensturz: 0
          }}
          erwarteterBestand={data.endbestand || 0}
          onChange={(kassensturz) => onChange({ ...data, kassensturz })}
        />
      )
    },
    {
      key: 'abschluss',
      label: 'Abschluss',
      fields: [
        {
          name: 'endbestand',
          label: 'Endbestand (berechnet)',
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
          helpText: 'Muss 0,00 sein für korrekten Abschluss'
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
          placeholder: 'Zusätzliche Informationen zum Tagesabschluss...'
        }
      ]
    }
  ],
  actions: [
    {
      key: 'add-movement',
      label: 'Bewegung hinzufügen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'count-cash',
      label: 'Kassensturz durchführen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'validate',
      label: 'Prüfen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'close',
      label: 'Tagesabschluss',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'approve',
      label: 'Freigeben',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'export',
      label: 'Export',
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/kasse',
    endpoints: {
      list: '/api/finance/kasse',
      get: '/api/finance/kasse/{id}',
      create: '/api/finance/kasse',
      update: '/api/finance/kasse/{id}',
      delete: '/api/finance/kasse/{id}'
    }
  } as any,
  validation: kasseSchema,
  permissions: ['fibu.read', 'fibu.write']
}

// Kassenbewegungen-Tabelle Komponente
function KassenbewegungenTable({ data, onChange }: { data: any[], onChange: (data: any[]) => void }) {
  const addBewegung = () => {
    onChange([...data, {
      typ: 'einlage',
      betrag: 0,
      verwendungszweck: '',
      belegNummer: '',
      konto: ''
    }])
  }

  const updateBewegung = (index: number, field: string, value: any) => {
    const newData = [...data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeBewegung = (index: number) => {
    onChange(data.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Kassenbewegungen</h3>
        <button
          onClick={addBewegung}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + Bewegung hinzufügen
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">Typ</th>
              <th className="px-4 py-2 border">Betrag</th>
              <th className="px-4 py-2 border">Verwendungszweck</th>
              <th className="px-4 py-2 border">Beleg-Nr.</th>
              <th className="px-4 py-2 border">Konto</th>
              <th className="px-4 py-2 border">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            {data.map((bewegung, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <select
                    value={bewegung.typ}
                    onChange={(e) => updateBewegung(index, 'typ', e.target.value)}
                    className="w-full p-1 border rounded"
                  >
                    <option value="einlage">Einlage</option>
                    <option value="auszahlung">Auszahlung</option>
                  </select>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="number"
                    step="0.01"
                    value={bewegung.betrag}
                    onChange={(e) => updateBewegung(index, 'betrag', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={bewegung.verwendungszweck}
                    onChange={(e) => updateBewegung(index, 'verwendungszweck', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="z.B. Barverkauf Bürobedarf"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={bewegung.belegNummer || ''}
                    onChange={(e) => updateBewegung(index, 'belegNummer', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="BE-001"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={bewegung.konto || ''}
                    onChange={(e) => updateBewegung(index, 'konto', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder="z.B. 4400"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <button
                    onClick={() => removeBewegung(index)}
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

// Kassensturz-Form Komponente
function KassensturzForm({ data, erwarteterBestand, onChange }: {
  data: any,
  erwarteterBestand: number,
  onChange: (data: any) => void
}) {
  const scheine = [500, 200, 100, 50, 20, 10, 5].map(s => s.toString())
  const muenzen = [2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01].map(m => m.toString())

  const updateAnzahl = (typ: 'scheine' | 'muenzen', wert: string, anzahl: number) => {
    const newData = { ...data }
    if (!newData[typ]) newData[typ] = {}
    newData[typ][wert] = anzahl

    // Berechne Gesamtsumme
    let gesamtGezaehlt = 0
    if (newData.scheine) {
      gesamtGezaehlt += Object.entries(newData.scheine).reduce((sum, [wert, anzahl]) =>
        sum + (parseFloat(wert) * (anzahl as number)), 0)
    }
    if (newData.muenzen) {
      gesamtGezaehlt += Object.entries(newData.muenzen).reduce((sum, [wert, anzahl]) =>
        sum + (parseFloat(wert) * (anzahl as number)), 0)
    }

    newData.gesamtGezaehlt = gesamtGezaehlt
    newData.differenzKassensturz = Math.abs(gesamtGezaehlt - erwarteterBestand)

    onChange(newData)
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Kassensturz</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Scheine */}
        <div>
          <h4 className="font-semibold mb-3">Scheine</h4>
          <div className="space-y-2">
            {scheine.map(schein => (
              <div key={schein} className="flex items-center justify-between">
                <span>{schein} €</span>
                <input
                  type="number"
                  min="0"
                  value={data.scheine?.[schein] || 0}
                  onChange={(e) => updateAnzahl('scheine', schein, parseInt(e.target.value) || 0)}
                  className="w-20 p-1 border rounded text-right"
                />
                <span className="w-16 text-right">
                  {(parseFloat(schein) * (data.scheine?.[schein] || 0)).toFixed(2)} €
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Münzen */}
        <div>
          <h4 className="font-semibold mb-3">Münzen</h4>
          <div className="space-y-2">
            {muenzen.map(münze => (
              <div key={münze} className="flex items-center justify-between">
                <span>{münze} €</span>
                <input
                  type="number"
                  min="0"
                  value={data.muenzen?.[münze] || 0}
                  onChange={(e) => updateAnzahl('muenzen', münze, parseInt(e.target.value) || 0)}
                  className="w-20 p-1 border rounded text-right"
                />
                <span className="w-16 text-right">
                  {(parseFloat(münze) * (data.muenzen?.[münze] || 0)).toFixed(2)} €
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Summen */}
      <div className="border-t pt-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium">Erwarteter Bestand</label>
            <div className="text-lg font-semibold">{erwarteterBestand.toFixed(2)} €</div>
          </div>
          <div>
            <label className="block text-sm font-medium">Gezählter Bestand</label>
            <div className="text-lg font-semibold">{(data.gesamtGezaehlt || 0).toFixed(2)} €</div>
          </div>
          <div>
            <label className="block text-sm font-medium">Differenz</label>
            <div className={`text-lg font-semibold ${Math.abs(data.differenzKassensturz || 0) > 0.01 ? 'text-red-600' : 'text-green-600'}`}>
              {(data.differenzKassensturz || 0).toFixed(2)} €
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function KassePage(): JSX.Element {
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

  const { data, loading, saveData } = useMaskData({
    apiUrl: kasseConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(kasseConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'add-movement') {
      // Neue Bewegung hinzufügen wird in der Tabelle behandelt
      alert('Verwenden Sie die Tabelle um Bewegungen hinzuzufügen')
    } else if (action === 'count-cash') {
      // Kassensturz wird im Tab behandelt
      alert('Führen Sie den Kassensturz im entsprechenden Tab durch')
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        alert('Kassenabschluss-Validierung erfolgreich!')
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'close') {
      // Tagesabschluss
      alert('Tagesabschluss-Funktion wird implementiert')
    } else if (action === 'approve') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        navigate('/finance/kasse')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'export') {
      window.open('/api/finance/kasse/export', '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('approve', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/kasse')
  }

  return (
    <ObjectPage
      config={kasseConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}