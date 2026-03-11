import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/axios'

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
         } as any,
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
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <AbgrenzungenTable
          data={_data.rechnungsabgrenzungsposten || []}
          onChange={(rechnungsabgrenzungsposten) => onChange({ ..._data, rechnungsabgrenzungsposten })}
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
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <RueckstellungenTable
          data={_data.rueckstellungen || []}
          onChange={(rueckstellungen) => onChange({ ..._data, rueckstellungen })}
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
    { key: 'calculate', label: 'Berechnen', type: 'secondary' },
    { key: 'validate', label: 'Prüfen', type: 'secondary' },
    { key: 'approve', label: 'Freigeben', type: 'primary' },
    { key: 'close', label: 'Abschließen', type: 'primary' },
    { key: 'lock', label: 'Sperren', type: 'danger' },
    { key: 'export', label: 'Export', type: 'secondary' }
  ],
  api: {
    baseUrl: '/api/v1/finance/abschluss',
    endpoints: {
      list: '/api/v1/finance/abschluss',
      get: '/api/v1/finance/abschluss/{id}',
      create: '/api/v1/finance/abschluss',
      update: '/api/v1/finance/abschluss/{id}',
      delete: '/api/v1/finance/abschluss/{id}'
    }
  } as any,
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin']
}

// Abgrenzungen-Tabelle Komponente
function AbgrenzungenTable({ data: _data, onChange }: { data: any[], onChange: (_data: any[]) => void }) {
  const addPosten = () => {
    onChange([..._data, {
      beschreibung: '',
      betrag: 0,
      typ: 'aktiv'
    }])
  }

  const updatePosten = (index: number, field: string, value: any) => {
    const newData = [..._data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removePosten = (index: number) => {
    onChange(_data.filter((_, i) => i !== index))
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
            {_data.map((posten, index) => (
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
function RueckstellungenTable({ data: _data, onChange }: { data: any[], onChange: (_data: any[]) => void }) {
  const addRueckstellung = () => {
    onChange([..._data, {
      beschreibung: '',
      betrag: 0,
      zweck: ''
    }])
  }

  const updateRueckstellung = (index: number, field: string, value: any) => {
    const newData = [..._data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeRueckstellung = (index: number) => {
    onChange(_data.filter((_, i) => i !== index))
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
            {_data.map((rueckstellung, index) => (
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
  const [actionLoadingKey, setActionLoadingKey] = useState<string | null>(null)

  const { data, loading } = useMaskData({
    apiUrl: abschlussConfig.api.baseUrl,
    id: 'new'
  })

  const validate = (formData: any) => validateFields(getFieldsFromMaskConfig(abschlussConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({
      variant: 'destructive',
      title: 'Validierungsfehler',
      description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.`,
    })
  }

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'calculate') {
      setActionLoadingKey('calculate')
      try {
        await apiClient.post('/api/v1/finance/closing/calculate', formData ?? {})
        toast({ title: 'Berechnung abgeschlossen', description: 'Abschlusszahlen wurden berechnet.' })
      } catch (error: any) {
        toast({ variant: 'destructive', title: 'Fehler', description: error.response?.data?.detail ?? error.message })
      } finally {
        setActionLoadingKey(null)
      }
      return
    }
    if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) toast({ title: 'Abschlussprüfung erfolgreich!' })
      else showValidationToast(isValid.errors)
      return
    }
    if (action === 'approve') {
      setActionLoadingKey('approve')
      try {
        await apiClient.post('/api/v1/finance/closing/approve', formData ?? {})
        toast({ title: 'Abschluss freigegeben', description: 'Abschlussgenehmigung wurde erteilt.' })
      } catch (error: any) {
        toast({ variant: 'destructive', title: 'Fehler', description: error.response?.data?.detail ?? error.message })
      } finally {
        setActionLoadingKey(null)
      }
      return
    }
    if (action === 'close') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }
      setActionLoadingKey('close')
      try {
        await apiClient.post('/api/v1/finance/closing/run', formData ?? {})
        toast({ title: 'Abschluss durchgeführt' })
        setIsDirty(false)
        navigate('/finance/abschluss')
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: 'Fehler', description: msg })
      } finally {
        setActionLoadingKey(null)
      }
      return
    }
    if (action === 'lock') {
      if (!confirm('Abschluss sperren? Diese Aktion kann nicht rückgängig gemacht werden.')) return
      setActionLoadingKey('lock')
      try {
        await apiClient.post('/api/v1/finance/closing/lock', formData ?? {})
        toast({ title: 'Abschluss gesperrt', description: 'Die Periode wurde endgültig gesperrt.' })
        navigate('/finance/abschluss')
      } catch (error: any) {
        toast({ variant: 'destructive', title: 'Fehler', description: error.response?.data?.detail ?? error.message })
      } finally {
        setActionLoadingKey(null)
      }
      return
    }
    if (action === 'export') {
      setActionLoadingKey('export')
      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', { entity: 'closing', format: 'pdf' })
        if (res?.url) window.open(res.url, '_blank')
        toast({ title: 'Export erstellt' })
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: 'Fehler', description: msg })
      } finally {
        setActionLoadingKey(null)
      }
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
      onAction={(key, formData) => handleAction(key, formData)}
      loadingActionKey={actionLoadingKey}
    />
  )
}
