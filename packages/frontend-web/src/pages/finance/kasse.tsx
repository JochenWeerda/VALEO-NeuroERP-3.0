import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import type { TFunction } from 'i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { LeaveConfirmDialog } from '@/components/LeaveConfirmDialog'
import { useUnsavedChanges } from '@/hooks/useUnsavedChanges'
import { inputValue, isRecord, numberValue, recordArrayFromResponse } from '@/lib/record-utils'

const createKasseConfig = (t: TFunction, entityTypeLabel: string): MaskConfig => ({
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
    },
    {
      key: 'bewegungen_custom',
      label: '',
      fields: [],
      customRender: (_data: Record<string, unknown>, onChange: (_data: Record<string, unknown>) => void) => (
        <KassenbewegungenTable
          data={recordArrayFromResponse(_data.bewegungen)}
          onChange={(bewegungen) => {
            const sollEinlagen = bewegungen.filter(b => b.typ === 'einlage').reduce((sum, b) => sum + Number((b as Record<string, unknown>).betrag || 0), 0)
            const sollAuszahlungen = bewegungen.filter(b => b.typ === 'auszahlung').reduce((sum, b) => sum + Number((b as Record<string, unknown>).betrag || 0), 0)
            const istEinlagen = sollEinlagen // Vereinfacht - in Realität würden Ist-Werte manuell erfasst
            const istAuszahlungen = sollAuszahlungen
            const endbestand = (Number(_data.anfangsbestand) || 0) + istEinlagen - istAuszahlungen
            const differenz = Math.abs(endbestand - numberValue(_data.endbestand))

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
    },
    {
      key: 'kassensturz_custom',
      label: '',
      fields: [],
      customRender: (_data: Record<string, unknown>, onChange: (_data: Record<string, unknown>) => void) => (
        <KassensturzForm
          data={isRecord(_data.kassensturz) ? _data.kassensturz : {
            scheine: {},
            muenzen: {},
            gesamtGezaehlt: 0,
            differenzKassensturz: 0
          }}
          erwarteterBestand={numberValue(_data.endbestand)}
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
    { key: 'add-movement', label: t('crud.actions.addMovement'), type: 'secondary' },
    { key: 'count-cash', label: t('crud.actions.performCashCount'), type: 'secondary' },
    { key: 'validate', label: t('crud.actions.validate'), type: 'secondary' },
    { key: 'close', label: t('crud.actions.dailyClosing'), type: 'primary' },
    { key: 'approve', label: t('crud.actions.approve'), type: 'primary' },
    { key: 'export', label: t('crud.actions.export'), type: 'secondary' }
  ],
  api: {
    baseUrl: '/api/v1/finance/cash',
    endpoints: {
      list: '/api/v1/finance/cash',
      get: '/api/v1/finance/cash/{id}',
      create: '/api/v1/finance/cash',
      update: '/api/v1/finance/cash/{id}',
      delete: '/api/v1/finance/cash/{id}'
    }
  },
  permissions: ['fibu.read', 'fibu.write']
})

// Kassenbewegungen-Tabelle Komponente
function KassenbewegungenTable({ data: _data, onChange }: { data: Record<string, unknown>[], onChange: (_data: Record<string, unknown>[]) => void }) {
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

  const updateBewegung = (index: number, field: string, value: unknown) => {
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
                    value={inputValue(bewegung.typ)}
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
                    value={inputValue(bewegung.betrag)}
                    onChange={(e) => updateBewegung(index, 'betrag', parseFloat(e.target.value) || 0)}
                    className="w-full p-1 border rounded"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={inputValue(bewegung.verwendungszweck)}
                    onChange={(e) => updateBewegung(index, 'verwendungszweck', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.purpose')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={inputValue(bewegung.belegNummer)}
                    onChange={(e) => updateBewegung(index, 'belegNummer', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.documentNumber')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={inputValue(bewegung.konto)}
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
  data: Record<string, unknown>,
  erwarteterBestand: number,
  onChange: (_data: Record<string, unknown>) => void
}) {
  const { t } = useTranslation()
  const scheine = [500, 200, 100, 50, 20, 10, 5].map(s => s.toString())
  const muenzen = [2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01].map(m => m.toString())

  const updateAnzahl = (typ: 'scheine' | 'muenzen', wert: string, anzahl: number) => {
    const currentCounts = isRecord(_data[typ]) ? _data[typ] as Record<string, unknown> : {}
    const newData: Record<string, unknown> = {
      ..._data,
      [typ]: { ...currentCounts, [wert]: anzahl },
    }

    // Berechne Gesamtsumme
    let gesamtGezaehlt = 0
    if (isRecord(newData.scheine)) {
      gesamtGezaehlt += Object.entries(newData.scheine).reduce((sum, [wert, anzahl]) =>
        sum + (parseFloat(wert) * numberValue(anzahl)), 0)
    }
    if (isRecord(newData.muenzen)) {
      gesamtGezaehlt += Object.entries(newData.muenzen).reduce((sum, [wert, anzahl]) =>
        sum + (parseFloat(wert) * numberValue(anzahl)), 0)
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
            {scheine.map((schein) => {
              const scheineCounts = isRecord(_data.scheine) ? _data.scheine : {}
              const anzahl = numberValue(scheineCounts[schein])
              return (
              <div key={schein} className="flex items-center justify-between">
                <span>{schein} EUR</span>
                <input
                  type="number"
                  min="0"
                  value={anzahl}
                  onChange={(e) => updateAnzahl('scheine', schein, parseInt(e.target.value) || 0)}
                  className="w-20 p-1 border rounded text-right"
                />
                <span className="w-16 text-right">
                  {(parseFloat(schein) * anzahl).toFixed(2)} EUR
                </span>
              </div>
              )
            })}
          </div>
        </div>

        {/* Münzen */}
        <div>
          <h4 className="font-semibold mb-3">{t('crud.fields.coins')}</h4>
          <div className="space-y-2">
            {muenzen.map((muenze) => {
              const muenzenCounts = isRecord(_data.muenzen) ? _data.muenzen : {}
              const anzahl = numberValue(muenzenCounts[muenze])
              return (
              <div key={muenze} className="flex items-center justify-between">
                <span>{muenze} EUR</span>
                <input
                  type="number"
                  min="0"
                  value={anzahl}
                  onChange={(e) => updateAnzahl('muenzen', muenze, parseInt(e.target.value) || 0)}
                  className="w-20 p-1 border rounded text-right"
                />
                <span className="w-16 text-right">
                  {(parseFloat(muenze) * anzahl).toFixed(2)} EUR
                </span>
              </div>
              )
            })}
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
            <div className="text-lg font-semibold">{numberValue(_data.gesamtGezaehlt).toFixed(2)} EUR</div>
          </div>
          <div>
            <label className="block text-sm font-medium">{t('crud.fields.difference')}</label>
            <div className={`text-lg font-semibold ${Math.abs(numberValue(_data.differenzKassensturz)) > 0.01 ? 'text-red-600' : 'text-green-600'}`}>
              {numberValue(_data.differenzKassensturz).toFixed(2)} EUR
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

  const validate = (formData: Record<string, unknown>) => validateFields(getFieldsFromMaskConfig(kasseConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({
      variant: 'destructive',
      title: t('crud.messages.validationError'),
      description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.`,
    })
  }

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
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
      const errors = validate(formData)
      if (Object.keys(errors).length === 0) {
        const differenz = Math.abs(numberValue(formData.differenz))
        const kassensturz = isRecord(formData.kassensturz) ? formData.kassensturz : {}
        const kassensturzDifferenz = Math.abs(numberValue(kassensturz.differenzKassensturz))

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
        showValidationToast(errors)
      }
    } else if (action === 'close') {
      if (!formData.id) {
        toast({ variant: 'destructive', title: t('common.error'), description: t('crud.messages.saveCashClosingFirst') })
        return
      }

      try {
        await apiClient.post('/api/v1/finance/cash/close-day', { id: formData.id, ...formData })
        toast({ title: t('crud.messages.dailyClosingPerformed'), description: t('crud.messages.cashClosingClosed') })
        setIsDirty(false)
        navigate('/finance/kasse')
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      }
    } else if (action === 'approve') {
      const validationErrors = validate(formData)
      if (Object.keys(validationErrors).length > 0) {
        showValidationToast(validationErrors)
        return
      }

      const differenz = Math.abs(numberValue(formData.differenz))
      const kassensturz = isRecord(formData.kassensturz) ? formData.kassensturz : {}
      const kassensturzDifferenz = Math.abs(numberValue(kassensturz.differenzKassensturz))

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
        toast({ variant: 'destructive', title: t('common.error'), description: t('crud.messages.saveCashClosingFirst') })
        return
      }

      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', { entity: 'cash', format: 'pdf', id: formData.id })
        if (res.data.url) window.open(res.data.url, '_blank')
        toast({ title: t('crud.actions.export'), description: t('crud.messages.exportCreated', { defaultValue: 'Export erstellt' }) })
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      }
    }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
    await handleAction('approve', formData)
  }

  const handleCancel = () => {
    navigate('/finance/kasse')
  }

  const blocker = useUnsavedChanges(isDirty)

  return (
    <>
      <ModuleToolbar backTarget="/finance/kasse" closeTarget="/finance/kasse" title={entityTypeLabel} />
      <LeaveConfirmDialog blocker={blocker} onSave={() => handleSave(data ?? {})} title={t('crud.messages.unsavedChanges', { defaultValue: 'Ungespeicherte Änderungen' })} description={t('crud.messages.unsavedChangesDescription', { defaultValue: 'Möchten Sie speichern, verwerfen oder hier bleiben?' })} />
      <ObjectPage
        config={kasseConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={(key, formData) => handleAction(key, formData)}
        loadingActionKey={loadingActionKey}
      />
    </>
  )
}
