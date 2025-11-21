import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { toast } from '@/hooks/use-toast'

// Zod-Schema für Bank-Abgleich
const bankAbgleichSchema = z.object({
  kontoId: z.string().min(1, "Konto ist erforderlich"),
  periode: z.string().regex(/^\d{4}-\d{2}$/, "Periode muss YYYY-MM Format haben"),
  camtFile: z.string().optional(),
  startSaldo: z.number(),
  endSaldo: z.number(),
  gebuchteUmsaetze: z.number(),
  nichtZugeordnet: z.number(),
  zugeordnet: z.number(),
  abgleichsDifferenz: z.number().max(0.01, "Abgleich muss ausgeglichen sein"),
  abgleichsDatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Abgleichsdatum muss YYYY-MM-DD Format haben"),
  regelAngewendet: z.array(z.object({
    regelName: z.string(),
    treffer: z.number(),
    zugeordnet: z.number()
  })).optional()
})

// Konfiguration für Bank-Abgleich ObjectPage
const bankAbgleichConfig: MaskConfig = {
  title: 'Bank (Kontoauszug-Abgleich)',
  subtitle: 'CAMT-Import und automatische Buchungszuordnung',
  type: 'object-page',
  tabs: [
    {
      key: 'import',
      label: 'CAMT-Import',
      fields: [
        {
          name: 'kontoId',
          label: 'Bankkonto',
          type: 'select',
          required: true,
          options: [
            { value: '1200', label: '1200 - Bankkonto Deutsche Bank' },
            { value: '1300', label: '1300 - Bankkonto Commerzbank' },
            { value: '1400', label: '1400 - Bankkonto Sparkasse' }
          ]
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
          name: 'camtFile',
          label: 'CAMT-Datei',
          type: 'file',
          accept: '.xml,.camt',
           } as any, {helpText: 'CAMT.053 oder CAMT.054 Datei vom Bankserver'
        },
        {
          name: 'abgleichsDatum',
          label: 'Abgleichsdatum',
          type: 'date',
          required: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'salden',
      label: 'Salden',
      fields: [
        {
          name: 'startSaldo',
          label: 'Anfangssaldo',
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: 'Aus CAMT-Datei importiert'
        },
        {
          name: 'endSaldo',
          label: 'Endsaldo',
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: 'Aus CAMT-Datei importiert'
        },
        {
          name: 'gebuchteUmsaetze',
          label: 'Gebuchte Umsätze',
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: 'Summe aller importierten Umsätze'
        }
      ],
      layout: 'grid',
      columns: 3
    },
    {
      key: 'zuordnung',
      label: 'Zuordnung',
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
      label: 'Regeln & Statistik',
      fields: [
        {
          name: 'regelAngewendet',
          label: 'Angewendete Regeln',
          type: 'custom',
           } as any, {customRender: (value: any) => (
            <div className="space-y-2">
              {(value || []).map((regel: any, index: number) => (
                <div key={index} className="flex justify-between p-2 bg-gray-50 rounded">
                  <span>{regel.regelName}</span>
                  <span>{regel.zugeordnet}/{regel.treffer} Treffer</span>
                </div>
              ))}
            </div>
          )
        }
      ]
    },
    {
      key: 'abgleich',
      label: 'Abgleich',
      fields: [
        {
          name: 'zugeordnet',
          label: 'Zugeordnete Umsätze',
          type: 'number',
          readonly: true
        },
        {
          name: 'nichtZugeordnet',
          label: 'Nicht zugeordnete Umsätze',
          type: 'number',
          readonly: true
        },
        {
          name: 'abgleichsDifferenz',
          label: 'Abgleichsdifferenz',
          type: 'number',
          readonly: true,
          step: 0.01,
          helpText: 'Muss 0,00 sein für erfolgreichen Abgleich'
        }
      ],
      layout: 'grid',
      columns: 3
    }
  ],
  actions: [
    {
      key: 'import',
      label: 'CAMT Import',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'auto-assign',
      label: 'Auto-Zuordnung',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'validate',
      label: 'Prüfen',
      type: 'secondary'
    , onClick: () => {} },
    {
      key: 'book',
      label: 'Buchen',
      type: 'primary'
    , onClick: () => {} },
    {
      key: 'export',
      label: 'Export',
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
  validation: bankAbgleichSchema,
  permissions: ['fibu.read', 'fibu.write']
}

// Bank-Zuordnung Tabelle Komponente
function BankZuordnungTable({ data: _data, onChange }: { data: any[], onChange: (_data: any[]) => void }) {
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
        <h3 className="text-lg font-semibold">Bankumsätze zuordnen</h3>
        <div className="text-sm text-gray-600">
          {_data.filter(d => d.zugeordnet).length} von {_data.length} zugeordnet
        </div>
      </div>

      <div className="overflow-x-auto max-h-96">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="px-4 py-2 border">Datum</th>
              <th className="px-4 py-2 border">Betrag</th>
              <th className="px-4 py-2 border">Verwendungszweck</th>
              <th className="px-4 py-2 border">Gegenkonto</th>
              <th className="px-4 py-2 border">OP-Referenz</th>
              <th className="px-4 py-2 border">Zugeordnet</th>
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
                    placeholder="z.B. 4400"
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={row.opReferenz || ''}
                    onChange={(e) => updateZuordnung(index, 'opReferenz', e.target.value)}
                    className="w-full p-1 border rounded text-sm"
                    placeholder="OP-12345"
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
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)

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
        title: 'CAMT-Datei importiert',
        description: `${mockUmsaetze.length} Umsätze wurden erfolgreich importiert.`,
      })
    } else if (action === 'auto-assign') {
      // Auto-Zuordnung - wende einfache Regeln an
      if (!formData.zuordnungData || formData.zuordnungData.length === 0) {
        toast({
          variant: 'destructive',
          title: 'Keine Daten',
          description: 'Importieren Sie zuerst eine CAMT-Datei.',
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
        title: 'Auto-Zuordnung abgeschlossen',
        description: `${zugeordnetCount} Umsätze wurden automatisch zugeordnet.`,
      })
    } else if (action === 'validate') {
      const isValid = validate(formData)
      if (isValid.isValid) {
        const differenz = Math.abs(formData.abgleichsDifferenz || 0)
        if (differenz < 0.01) {
          toast({
            title: 'Validierung erfolgreich',
            description: 'Alle Daten sind korrekt und der Abgleich ist ausgeglichen.',
          })
        } else {
          toast({
            variant: 'destructive',
            title: 'Abgleich nicht ausgeglichen',
            description: `Differenz: ${differenz.toFixed(2)} €`,
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
          title: 'Buchung nicht möglich',
          description: 'Der Abgleich muss ausgeglichen sein.',
        })
        return
      }

      try {
        await saveData(formData)
        setIsDirty(false)
        toast({
          title: 'Abgleich gebucht',
          description: 'Alle zugeordneten Umsätze wurden erfolgreich gebucht.',
        })
        navigate('/finance/bank')
      } catch (error) {
        // Error wird bereits in useMaskData behandelt
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast({
          variant: 'destructive',
          title: 'Fehler',
          description: 'Speichern Sie den Abgleich zuerst.',
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
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
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