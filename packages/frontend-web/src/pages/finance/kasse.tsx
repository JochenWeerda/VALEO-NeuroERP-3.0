import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Kasse (wird in Komponente mit i18n erstellt)
const createKasseSchema = (t: any) => z.object({
  datum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
  kassenbuchNummer: z.string().min(1, t('crud.messages.validationError')),
  anfangsbestand: z.number().min(0, t('crud.messages.validationError')),
  sollEinlagen: z.number().min(0, t('crud.messages.validationError')),
  sollAuszahlungen: z.number().min(0, t('crud.messages.validationError')),
  istEinlagen: z.number().min(0, t('crud.messages.validationError')),
  istAuszahlungen: z.number().min(0, t('crud.messages.validationError')),
  endbestand: z.number().min(0, t('crud.messages.validationError')),
  differenz: z.number().max(0.01, t('crud.messages.validationError')),
  status: z.enum(['offen', 'geschlossen', 'freigegeben']),
  freigegebenAm: z.string().optional(),
  freigegebenDurch: z.string().optional(),

  // Kassenbewegungen
  bewegungen: z.array(z.object({
    typ: z.enum(['einlage', 'auszahlung']),
    betrag: z.number().positive(t('crud.messages.validationError')),
    verwendungszweck: z.string().min(1, t('crud.messages.validationError')),
    belegNummer: z.string().optional(),
    konto: z.string().optional()
  })).optional(),

  // Kassensturz
  kassensturz: z.object({
    scheine: z.record(z.string(), z.number().min(0)),
    muenzen: z.record(z.string(), z.number().min(0)),
    gesamtGezaehlt: z.number().min(0),
    differenzKassensturz: z.number().max(0.01, t('crud.messages.validationError'))
  }).optional(),

  notizen: z.string().optional()
})

// Konfiguration für Kasse ObjectPage (wird in Komponente mit i18n erstellt)
const createKasseConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.fields.dailyClosing'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'datum',
          label: t('crud.fields.date'),
          type: 'date',
          required: true
        },
        {
          name: 'kassenbuchNummer',
          label: t('crud.fields.cashBookNumber'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.cashBookNumber')
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'offen', label: t('crud.fields.open') },
            { value: 'geschlossen', label: t('crud.fields.closed') },
            { value: 'freigegeben', label: t('status.approved') }
          ]
        },
        {
          name: 'anfangsbestand',
          label: t('crud.fields.openingBalance'),
          type: 'number',
          required: true,
          step: 0.01,
          placeholder: t('crud.tooltips.placeholders.amount')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'soll',
      label: t('crud.fields.shouldBookings'),
      fields: [
        {
          name: 'sollEinlagen',
          label: t('crud.fields.shouldDeposits'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'sollAuszahlungen',
          label: t('crud.fields.shouldWithdrawals'),
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
      label: t('crud.fields.actualBookings'),
      fields: [
        {
          name: 'istEinlagen',
          label: t('crud.fields.actualDeposits'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'istAuszahlungen',
          label: t('crud.fields.actualWithdrawals'),
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
      label: t('crud.fields.cashMovements'),
      fields: []
    } as any,
    {
      key: 'bewegungen_custom',
      label: '',
      fields: [],
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <KassenbewegungenTable
          data={_data.bewegungen || []}
          onChange={(bewegungen) => {
            const sollEinlagen = bewegungen.filter((b: any) => b.typ === 'einlage').reduce((sum: number, b: any) => sum + (b.betrag || 0), 0)
            const sollAuszahlungen = bewegungen.filter((b: any) => b.typ === 'auszahlung').reduce((sum: number, b: any) => sum + (b.betrag || 0), 0)
            const istEinlagen = sollEinlagen // Vereinfacht - in Realität würden Ist-Werte manuell erfasst
            const istAuszahlungen = sollAuszahlungen
            const endbestand = (_data.anfangsbestand || 0) + istEinlagen - istAuszahlungen
            const differenz = Math.abs(endbestand - (_data.endbestand || 0))

            onChange({
              ..._data,
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
      label: t('crud.fields.cashCount'),
      fields: []
    } as any,
    {
      key: 'kassensturz_custom',
      label: '',
      fields: [],
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <KassensturzForm
          data={_data.kassensturz || {
            scheine: {},
            muenzen: {},
            gesamtGezaehlt: 0,
            differenzKassensturz: 0
          }}
          erwarteterBestand={_data.endbestand || 0}
          onChange={(kassensturz) => onChange({ ..._data, kassensturz })}
        />
      )
    },
    {
      key: 'abschluss',
      label: t('crud.fields.closing'),
      fields: [
        {
          name: 'endbestand',
          label: t('crud.fields.closingBalance'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'differenz',
          label: t('crud.fields.difference'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.differenceMustBeZero')
        },
        {
          name: 'freigegebenAm',
          label: t('crud.fields.approvedOn'),
          type: 'date',
          readonly: true
        },
        {
          name: 'freigegebenDurch',
          label: t('crud.fields.approvedBy'),
          type: 'text',
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notizen',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.cashNotes')
        }
      ]
    }
  ],
  actions: [
    {
      key: 'add-movement',
      label: t('crud.actions.addMovement'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'count-cash',
      label: t('crud.actions.performCashCount'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'validate',
      label: t('crud.actions.validate'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'close',
      label: t('crud.actions.dailyClosing'),
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'approve',
      label: t('crud.actions.approve'),
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'export',
      label: t('crud.actions.export'),
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
  validation: createKasseSchema(t),
  permissions: ['fibu.read', 'fibu.write']
})

// Kassenbewegungen-Tabelle Komponente
function KassenbewegungenTable({ data: _data, onChange }: { data: any[], onChange: (_data: any[]) => void }) {
  const { t } = useTranslation()
  const addBewegung = () => {
    onChange([..._data, {
      typ: 'einlage',
      betrag: 0,
      verwendungszweck: '',
      belegNummer: '',
      konto: ''
    }])
  }

  const updateBewegung = (index: number, field: string, value: any) => {
    const newData = [..._data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeBewegung = (index: number) => {
    onChange(_data.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.fields.cashMovements')}</h3>
        <button
          onClick={addBewegung}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + {t('crud.actions.addMovement')}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">{t('crud.fields.type')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.amount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.purpose')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.documentNumber')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.account')}</th>
              <th className="px-4 py-2 border">{t('crud.actions.delete')}</th>
            </tr>
          </thead>
          <tbody>
            {_data.map((bewegung, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <select
                    value={bewegung.typ}
                    onChange={(e) => updateBewegung(index, 'typ', e.target.value)}
                    className="w-full p-1 border rounded"
                  >
                    <option value="einlage">{t('crud.fields.deposit')}</option>
                    <option value="auszahlung">{t('crud.fields.withdrawal')}</option>
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
                    placeholder={t('crud.tooltips.placeholders.purpose')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={bewegung.belegNummer || ''}
                    onChange={(e) => updateBewegung(index, 'belegNummer', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.documentNumber')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={bewegung.konto || ''}
                    onChange={(e) => updateBewegung(index, 'konto', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.account')}
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
function KassensturzForm({ data: _data, erwarteterBestand, onChange }: {
  data: any,
  erwarteterBestand: number,
  onChange: (_data: any) => void
}) {
  const { t } = useTranslation()
  const scheine = [500, 200, 100, 50, 20, 10, 5].map(s => s.toString())
  const muenzen = [2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01].map(m => m.toString())

  const updateAnzahl = (typ: 'scheine' | 'muenzen', wert: string, anzahl: number) => {
    const newData = { ..._data }
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
      <h3 className="text-lg font-semibold">{t('crud.fields.cashCount')}</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Scheine */}
        <div>
          <h4 className="font-semibold mb-3">{t('crud.fields.bills')}</h4>
          <div className="space-y-2">
            {scheine.map(schein => (
              <div key={schein} className="flex items-center justify-between">
                <span>{schein} €</span>
                <input
                  type="number"
                  min="0"
                  value={_data.scheine?.[schein] || 0}
                  onChange={(e) => updateAnzahl('scheine', schein, parseInt(e.target.value) || 0)}
                  className="w-20 p-1 border rounded text-right"
                />
                <span className="w-16 text-right">
                  {(parseFloat(schein) * (_data.scheine?.[schein] || 0)).toFixed(2)} €
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Münzen */}
        <div>
          <h4 className="font-semibold mb-3">{t('crud.fields.coins')}</h4>
          <div className="space-y-2">
            {muenzen.map(münze => (
              <div key={münze} className="flex items-center justify-between">
                <span>{münze} €</span>
                <input
                  type="number"
                  min="0"
                  value={_data.muenzen?.[münze] || 0}
                  onChange={(e) => updateAnzahl('muenzen', münze, parseInt(e.target.value) || 0)}
                  className="w-20 p-1 border rounded text-right"
                />
                <span className="w-16 text-right">
                  {(parseFloat(münze) * (_data.muenzen?.[münze] || 0)).toFixed(2)} €
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
            <label className="block text-sm font-medium">{t('crud.fields.expectedBalance')}</label>
            <div className="text-lg font-semibold">{erwarteterBestand.toFixed(2)} €</div>
          </div>
          <div>
            <label className="block text-sm font-medium">{t('crud.fields.countedBalance')}</label>
            <div className="text-lg font-semibold">{(_data.gesamtGezaehlt || 0).toFixed(2)} €</div>
          </div>
          <div>
            <label className="block text-sm font-medium">{t('crud.fields.difference')}</label>
            <div className={`text-lg font-semibold ${Math.abs(_data.differenzKassensturz || 0) > 0.01 ? 'text-red-600' : 'text-green-600'}`}>
              {(_data.differenzKassensturz || 0).toFixed(2)} €
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function KassePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'cash'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kasse')
  const kasseConfig = createKasseConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: kasseConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(kasseConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'add-movement') {
      // Neue Bewegung hinzufügen wird in der Tabelle behandelt
      toast({
        title: t('crud.actions.addMovement'),
        description: t('crud.messages.useTableToAddMovements'),
      })
    } else if (action === 'count-cash') {
      // Kassensturz wird im Tab behandelt
      toast({
        title: t('crud.fields.cashCount'),
        description: t('crud.messages.performCashCountInTab'),
      })
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        const differenz = Math.abs(formData.differenz || 0)
        const kassensturzDifferenz = Math.abs(formData.kassensturz?.differenzKassensturz || 0)

        if (differenz < 0.01 && kassensturzDifferenz < 0.01) {
          toast({
            title: t('crud.messages.validationSuccess'),
            description: t('crud.messages.cashClosingCorrect'),
          })
        } else {
          toast({
            variant: 'destructive',
            title: t('crud.messages.validationFailed'),
            description: t('crud.messages.validationFailedDesc', { 
              bookingDiff: differenz.toFixed(2), 
              cashCountDiff: kassensturzDifferenz.toFixed(2) 
            }),
          })
        }
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'close') {
      // Tagesabschluss - setze Status auf geschlossen
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveCashClosingFirst'),
        })
        return
      }

      try {
        const updatedData = { ...formData, status: 'geschlossen' }
        await saveData(updatedData)
        setIsDirty(false)
        toast({
          title: t('crud.messages.dailyClosingPerformed'),
          description: t('crud.messages.cashClosingClosed'),
        })
        navigate('/finance/kasse')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'approve') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      const differenz = Math.abs(formData.differenz || 0)
      const kassensturzDifferenz = Math.abs(formData.kassensturz?.differenzKassensturz || 0)

      if (differenz >= 0.01 || kassensturzDifferenz >= 0.01) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.approvalNotPossible'),
          description: t('crud.messages.cashClosingMustBeBalanced'),
        })
        return
      }

      try {
        const updatedData = {
          ...formData,
          status: 'freigegeben',
          freigegebenAm: new Date().toISOString().split('T')[0]
        }
        await saveData(updatedData)
        setIsDirty(false)
        toast({
          title: t('crud.messages.cashClosingApproved'),
          description: t('crud.messages.dailyClosingApproved'),
        })
        navigate('/finance/kasse')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveCashClosingFirst'),
        })
        return
      }
      window.open(`/api/finance/kasse/${formData.id}/export`, '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('approve', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
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