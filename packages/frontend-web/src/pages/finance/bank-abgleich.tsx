import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// Zod-Schema für Bank-Abgleich (wird in Komponente mit i18n erstellt)
const createBankAbgleichSchema = (t: any) => z.object({
  kontoId: z.string().min(1, t('crud.messages.validationError')),
  periode: z.string().regex(/^\d{4}-\d{2}$/, t('crud.messages.validationError')),
  camtFile: z.string().optional(),
  startSaldo: z.number(),
  endSaldo: z.number(),
  gebuchteUmsaetze: z.number(),
  nichtZugeordnet: z.number(),
  zugeordnet: z.number(),
  abgleichsDifferenz: z.number().max(0.01, t('crud.messages.validationError')),
  abgleichsDatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
  regelAngewendet: z.array(z.object({
    regelName: z.string(),
    treffer: z.number(),
    zugeordnet: z.number()
  })).optional()
})

// Konfiguration für Bank-Abgleich ObjectPage (wird in Komponente mit i18n erstellt)
const createBankAbgleichConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.fields.bankReconciliation'),
  type: 'object-page',
  tabs: [
    {
      key: 'import',
      label: t('crud.fields.camtImport'),
      fields: [
        {
          name: 'kontoId',
          label: t('crud.fields.bankAccount'),
          type: 'select',
          required: true,
          options: [
            { value: '1200', label: '1200 - ' + t('crud.fields.bankAccount') + ' Deutsche Bank' },
            { value: '1300', label: '1300 - ' + t('crud.fields.bankAccount') + ' Commerzbank' },
            { value: '1400', label: '1400 - ' + t('crud.fields.bankAccount') + ' Sparkasse' }
          ]
        },
        {
          name: 'periode',
          label: t('crud.fields.period'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.period'),
          pattern: '^\\d{4}-\\d{2}$'
         } as any, {},
        {
          name: 'camtFile',
          label: t('crud.fields.camtFile'),
          type: 'file',
          accept: '.xml,.camt',
           } as any, {helpText: t('crud.tooltips.fields.camtFile')
        },
        {
          name: 'abgleichsDatum',
          label: t('crud.fields.reconciliationDate'),
          type: 'date',
          required: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'salden',
      label: t('crud.fields.balances'),
      fields: [
        {
          name: 'startSaldo',
          label: t('crud.fields.openingBalance'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.importedFromCamt')
        },
        {
          name: 'endSaldo',
          label: t('crud.fields.closingBalance'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.importedFromCamt')
        },
        {
          name: 'gebuchteUmsaetze',
          label: t('crud.fields.bookedTransactions'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.sumOfImportedTransactions')
        }
      ],
      layout: 'grid',
      columns: 3
    },
    {
      key: 'zuordnung',
      label: t('crud.fields.assignment'),
      fields: []
    } as any,
    {
      key: 'zuordnung_custom',
      label: '',
      fields: [],
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <BankZuordnungTable
          data={_data.zuordnungData || []}
          onChange={(zuordnungData) => onChange({ ..._data, zuordnungData })}
        />
      )
    },
    {
      key: 'regeln',
      label: t('crud.fields.rulesAndStatistics'),
      fields: [
        {
          name: 'regelAngewendet',
          label: t('crud.fields.appliedRules'),
          type: 'custom',
           } as any, {          customRender: (value: any) => (
            <div className="space-y-2">
              {(value || []).map((regel: any, index: number) => (
                <div key={index} className="flex justify-between p-2 bg-gray-50 rounded">
                  <span>{regel.regelName}</span>
                  <span>{regel.zugeordnet}/{regel.treffer} {t('crud.fields.matches')}</span>
                </div>
              ))}
            </div>
          )
        }
      ]
    },
    {
      key: 'abgleich',
      label: t('crud.fields.reconciliation'),
      fields: [
        {
          name: 'zugeordnet',
          label: t('crud.fields.assignedTransactions'),
          type: 'number',
          readonly: true
        },
        {
          name: 'nichtZugeordnet',
          label: t('crud.fields.unassignedTransactions'),
          type: 'number',
          readonly: true
        },
        {
          name: 'abgleichsDifferenz',
          label: t('crud.fields.reconciliationDifference'),
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: t('crud.tooltips.fields.reconciliationMustBeZero')
        }
      ],
      layout: 'grid',
      columns: 3
    }
  ],
  actions: [
    {
      key: 'import',
      label: t('crud.actions.camtImport'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'auto-assign',
      label: t('crud.actions.autoAssign'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'validate',
      label: t('crud.actions.validate'),
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'book',
      label: t('crud.actions.book'),
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'export',
      label: t('crud.actions.export'),
      type: 'secondary'
    , onClick: () => {} }
  ],
  api: {
    baseUrl: '/api/finance/bank',
    endpoints: {
      list: '/api/finance/bank',
      get: '/api/finance/bank/{id}',
      create: '/api/finance/bank',
      update: '/api/finance/bank/{id}',
      delete: '/api/finance/bank/{id}'
    }
  } as any,
  validation: createBankAbgleichSchema(t),
  permissions: ['fibu.read', 'fibu.write']
})

// Bank-Zuordnung Tabelle Komponente
function BankZuordnungTable({ data: _data, onChange }: { data: any[], onChange: (_data: any[]) => void }) {
  const { t } = useTranslation()
  const updateZuordnung = (index: number, field: string, value: any) => {
    const newData = [..._data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const toggleZuordnung = (index: number) => {
    const newData = [..._data]
    newData[index].zugeordnet = !newData[index].zugeordnet
    onChange(newData)
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.fields.assignBankTransactions')}</h3>
        <div className="text-sm text-gray-600">
          {t('crud.fields.assignedCount', { assigned: _data.filter(d => d.zugeordnet).length, total: _data.length })}
        </div>
      </div>

      <div className="overflow-x-auto max-h-96">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="px-4 py-2 border">{t('crud.fields.date')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.amount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.purpose')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.counterAccount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.opReference')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.assigned')}</th>
            </tr>
          </thead>
          <tbody>
            {_data.map((row, index) => (
              <tr key={index} className={`border ${row.zugeordnet ? 'bg-green-50' : ''}`}>
                <td className="px-4 py-2 border">{row.datum}</td>
                <td className="px-4 py-2 border text-right">
                  {row.betrag?.toFixed(2)} €
                </td>
                <td className="px-4 py-2 border max-w-xs truncate" title={row.verwendungszweck}>
                  {row.verwendungszweck}
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={row.gegenkonto || ''}
                    onChange={(e) => updateZuordnung(index, 'gegenkonto', e.target.value)}
                    className="w-full p-1 border rounded text-sm"
                    placeholder={t('crud.tooltips.placeholders.account')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={row.opReferenz || ''}
                    onChange={(e) => updateZuordnung(index, 'opReferenz', e.target.value)}
                    className="w-full p-1 border rounded text-sm"
                    placeholder={t('crud.tooltips.placeholders.opReference')}
                  />
                </td>
                <td className="px-4 py-2 border text-center">
                  <input
                    type="checkbox"
                    checked={row.zugeordnet || false}
                    onChange={() => toggleZuordnung(index)}
                    className="h-4 w-4"
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function BankAbgleichPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const entityType = 'bankReconciliation'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Bank-Abgleich')
  const bankAbgleichConfig = createBankAbgleichConfig(t, entityTypeLabel)

  const { data, loading, saveData } = useMaskData({
    apiUrl: bankAbgleichConfig.api.baseUrl,
    id: 'new'
  })

  const { validate, showValidationToast } = useMaskValidation(bankAbgleichConfig.validation)

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'import') {
      // CAMT Import - simuliere Import von Beispieldaten
      const mockUmsaetze = [
        { datum: '2025-01-15', betrag: -1250.00, verwendungszweck: 'Rechnung RE-2025-0123 Müller GmbH', gegenkonto: '4400', opReferenz: 'OP-2025-0001', zugeordnet: false },
        { datum: '2025-01-16', betrag: 3500.00, verwendungszweck: 'Kundenüberweisung K001 Schmidt KG', gegenkonto: '1400', opReferenz: 'OP-2025-0002', zugeordnet: false },
        { datum: '2025-01-17', betrag: -450.00, verwendungszweck: 'Büromaterial Bürobedarf AG', gegenkonto: '4650', opReferenz: '', zugeordnet: false },
        { datum: '2025-01-18', betrag: -89.50, verwendungszweck: 'Stromabrechnung Stadtwerke', gegenkonto: '4100', opReferenz: '', zugeordnet: false },
        { datum: '2025-01-19', betrag: 2200.00, verwendungszweck: 'Verkauf Getreide Bauer e.K.', gegenkonto: '4400', opReferenz: 'OP-2025-0003', zugeordnet: false }
      ]

      formData.zuordnungData = mockUmsaetze
      formData.startSaldo = 15000.00
      formData.endSaldo = 16910.50
      formData.gebuchteUmsaetze = mockUmsaetze.reduce((sum, u) => sum + u.betrag, 0)
      formData.nichtZugeordnet = mockUmsaetze.length
      formData.zugeordnet = 0
      formData.abgleichsDifferenz = Math.abs(formData.startSaldo + formData.gebuchteUmsaetze - formData.endSaldo)

      toast({
        title: t('crud.messages.camtFileImported'),
        description: t('crud.messages.camtFileImportedDesc', { count: mockUmsaetze.length }),
      })
    } else if (action === 'auto-assign') {
      // Auto-Zuordnung - wende einfache Regeln an
      if (!formData.zuordnungData || formData.zuordnungData.length === 0) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.noData'),
          description: t('crud.messages.importCamtFileFirst'),
        })
        return
      }

      const rules = [
        { name: 'Rechnung-Zuordnung', pattern: /Rechnung|RE-/, konto: '4400' },
        { name: 'Kunden-Zuordnung', pattern: /K001|K002|K003/, konto: '1400' },
        { name: 'Strom-Zuordnung', pattern: /Strom|Stadtwerke/, konto: '4100' },
        { name: 'Büro-Zuordnung', pattern: /Büro|Material/, konto: '4650' }
      ]

      let zugeordnetCount = 0
      const regelStats = rules.map(regel => ({ regelName: regel.name, treffer: 0, zugeordnet: 0 }))

      formData.zuordnungData.forEach((umsatz: any) => {
        if (!umsatz.zugeordnet) {
          rules.forEach((regel, index) => {
            if (regel.pattern.test(umsatz.verwendungszweck)) {
              regelStats[index].treffer++
              if (!umsatz.gegenkonto) {
                umsatz.gegenkonto = regel.konto
                umsatz.zugeordnet = true
                regelStats[index].zugeordnet++
                zugeordnetCount++
              }
            }
          })
        }
      })

      formData.regelAngewendet = regelStats
      formData.zugeordnet = (formData.zugeordnet || 0) + zugeordnetCount
      formData.nichtZugeordnet = formData.zuordnungData.length - formData.zugeordnet

      toast({
        title: t('crud.messages.autoAssignCompleted'),
        description: t('crud.messages.autoAssignCompletedDesc', { count: zugeordnetCount }),
      })
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        const differenz = Math.abs(formData.abgleichsDifferenz || 0)
        if (differenz < 0.01) {
          toast({
            title: t('crud.messages.validationSuccess'),
            description: t('crud.messages.reconciliationBalanced'),
          })
        } else {
          toast({
            variant: 'destructive',
            title: t('crud.messages.reconciliationNotBalanced'),
            description: t('crud.messages.reconciliationNotBalancedDesc', { difference: differenz.toFixed(2) }),
          })
        }
      } else {
        showValidationToast(isValid.errors)
      }
    } else if (action === 'book') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }

      const differenz = Math.abs(formData.abgleichsDifferenz || 0)
      if (differenz >= 0.01) {
        toast({
          variant: 'destructive',
          title: t('crud.messages.bookingNotPossible'),
          description: t('crud.messages.reconciliationMustBeBalanced'),
        })
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        toast({
          title: t('crud.messages.reconciliationBooked'),
          description: t('crud.messages.reconciliationBookedDesc'),
        })
        navigate('/finance/bank')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: t('common.error'),
          description: t('crud.messages.saveReconciliationFirst'),
        })
        return
      }
      window.open(`/api/finance/bank/${formData.id}/export`, '_blank')
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('book', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/bank')
  }

  return (
    <ObjectPage
      config={bankAbgleichConfig}
      data={data}
      onSave={handleSave}
      onCancel={handleCancel}
      isLoading={loading}
    />
  )
}