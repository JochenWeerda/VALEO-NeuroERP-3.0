import { useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Banknote } from 'lucide-react'
import { useFibuCockpit } from '@/lib/api/fibu'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'

/** Mappt GET /finance/open-items/{id} (API) auf Masken-Felder (OTC-011). */
function mapOpenItemApiToForm(row: Record<string, unknown>): Record<string, unknown> {
  const opStatus = String(row.op_status ?? 'offen')
  const statusUi: Record<string, string> = {
    offen: 'offen',
    teilweise: 'teilbezahlt',
    geschlossen: 'ausgeglichen',
    storniert: 'ausgeglichen',
  }
  const rd = row.rechnungsdatum ?? row.datum
  const fd = row.faelligkeit
  return {
    id: row.id,
    debitorId: String(row.kunde_id ?? 'K001'),
    opNummer: String(row.rechnungsnr ?? row.id ?? ''),
    rechnungId: String(row.rechnungsnr ?? ''),
    buchungsdatum: rd ? String(rd).slice(0, 10) : '',
    faelligkeit: fd ? String(fd).slice(0, 10) : '',
    status: statusUi[opStatus] ?? 'offen',
    betrag: Number(row.op_betrag ?? row.betrag ?? 0),
    offen: Number(row.offen ?? 0),
    waehrung: String(row.waehrung ?? 'EUR'),
    mahnstufe: Number(row.mahn_stufe ?? 0),
    zahlungen: [],
    notizen: String(row.op_text ?? ''),
  }
}

const createOpDebitorenConfig = (t: any, entityTypeLabel: string, customerOptions: Array<{ value: string; label: string }>): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.fields.opKreditoren.subtitle'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'debitorId',
          label: t('crud.entities.debtor'),
          type: 'select',
          required: true,
          options: customerOptions.length > 0
            ? customerOptions
            : [{ value: '', label: t('common.loading') ?? 'Laden...' }]
        },
        {
          name: 'opNummer',
          label: t('crud.fields.opReference'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.opReference')
        },
        {
          name: 'rechnungId',
          label: t('crud.fields.invoiceNumber'),
          type: 'text',
          placeholder: t('crud.tooltips.placeholders.invoiceNumber')
        },
        {
          name: 'buchungsdatum',
          label: t('crud.fields.bookingDate'),
          type: 'date',
          required: true
        },
        {
          name: 'faelligkeit',
          label: t('crud.fields.dueDate'),
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'offen', label: t('status.open') },
            { value: 'teilbezahlt', label: t('status.partial') },
            { value: 'ausgeglichen', label: t('status.settled') },
            { value: 'mahnung', label: t('crud.entities.dunning') },
            { value: 'inkasso', label: t('crud.fields.collection') }
          ]
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'betrag',
      label: t('crud.fields.amounts'),
      fields: [
        {
          name: 'betrag',
          label: t('crud.fields.totalAmount'),
          type: 'number',
          required: true,
          step: 0.01,
          placeholder: '0.00'
        },
        {
          name: 'waehrung',
          label: t('crud.fields.currency'),
          type: 'select',
          options: [
            { value: 'EUR', label: 'EUR' },
            { value: 'USD', label: 'USD' },
            { value: 'GBP', label: 'GBP' }
          ]
        },
        {
          name: 'offen',
          label: t('crud.fields.openAmount'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'skontoBetrag',
          label: t('crud.fields.discountAmount'),
          type: 'number',
          step: 0.01,
          helpText: t('crud.tooltips.fields.discountAvailable')
        },
        {
          name: 'skontoDatum',
          label: t('crud.fields.discountDeadline'),
          type: 'date',
          helpText: t('crud.tooltips.fields.discountDeadline')
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'zahlungen',
      label: t('crud.fields.payments'),
      fields: []
    } as any,
    {
      key: 'zahlungen_custom',
      label: '',
      fields: [],
      customRender: (_data: any, onChange: (_data: any) => void) => (
        <ZahlungenTable
          data={_data.zahlungen || []}
          gesamtBetrag={_data.betrag || 0}
          onChange={(zahlungen) => {
            const totalPaid = zahlungen.reduce((sum: number, z: any) => sum + (z.betrag || 0), 0)
            onChange({
              ..._data,
              zahlungen,
              offen: (_data.betrag || 0) - totalPaid,
              letzteZahlung: zahlungen.length > 0 ? zahlungen[zahlungen.length - 1].datum : _data.letzteZahlung
            })
          }}
          t={t}
        />
      )
    },
    {
      key: 'mahnwesen',
      label: t('crud.entities.dunning'),
      fields: [
        {
          name: 'mahnstufe',
          label: t('crud.fields.dunningLevel'),
          type: 'select',
          options: [
            { value: 0, label: t('crud.fields.noDunning') },
            { value: 1, label: `1. ${  t('crud.entities.dunning')}` },
            { value: 2, label: `2. ${  t('crud.entities.dunning')}` },
            { value: 3, label: `3. ${  t('crud.entities.dunning')}` }
          ]
        },
        {
          name: 'letzteZahlung',
          label: t('crud.fields.lastPayment'),
          type: 'date',
          readonly: true
        }
      ]
    },
    {
      key: 'ausgleichshistorie',
      label: t('crud.fields.settlementHistory') ?? 'Ausgleichshistorie',
      fields: [],
      customRender: (tabData: any) => tabData?.id ? <SettlementsList opId={tabData.id} t={t} /> : <p className="text-sm text-muted-foreground">{t('crud.fields.settlementHistoryEmpty') ?? 'OP speichern, um die Ausgleichshistorie zu sehen.'}</p>
    } as any,
    {
      key: 'notizen',
      label: t('crud.fields.notes'),
      fields: [
        {
          name: 'notizen',
          label: t('crud.fields.internalNotes'),
          type: 'textarea',
          placeholder: t('crud.tooltips.placeholders.opNotes')
        }
      ]
    }
  ],
  actions: [
    { key: 'zahlung', label: t('crud.actions.recordPayment'), type: 'secondary' },
    { key: 'skonto', label: t('crud.actions.useDiscount'), type: 'secondary' },
    { key: 'ausgleich', label: t('crud.actions.settle'), type: 'primary' },
    { key: 'mahnung', label: t('crud.actions.createDunning'), type: 'danger' },
    { key: 'export', label: t('crud.actions.export'), type: 'secondary' }
  ],
  api: {
    baseUrl: '/api/v1/finance/open-items',
    endpoints: {
      list: '/api/v1/finance/open-items',
      get: '/api/v1/finance/open-items/{id}',
      create: '/api/v1/finance/open-items',
      update: '/api/v1/finance/open-items/{id}',
      delete: '/api/v1/finance/open-items/{id}'
    }
  } as any,
  permissions: ['fibu.read', 'fibu.write']
})

// Zahlungen-Tabelle Komponente
function ZahlungenTable({ data: _data, gesamtBetrag, onChange, t }: {
  data: any[],
  gesamtBetrag: number,
  onChange: (_data: any[]) => void,
  t: any
}) {
  const addZahlung = () => {
    onChange([..._data, {
      datum: new Date().toISOString().split('T')[0],
      betrag: 0,
      typ: 'zahlung',
      referenz: ''
    }])
  }

  const updateZahlung = (index: number, field: string, value: any) => {
    const newData = [..._data]
    newData[index] = { ...newData[index], [field]: value }
    onChange(newData)
  }

  const removeZahlung = (index: number) => {
    onChange(_data.filter((_, i) => i !== index))
  }

  const totalPaid = _data.reduce((sum, z) => sum + (z.betrag || 0), 0)
  const remaining = gesamtBetrag - totalPaid

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.fields.payments')}</h3>
        <div className="text-sm">
          <span className="font-semibold">{t('crud.fields.openAmount')}: {remaining.toFixed(2)} €</span>
          <button
            onClick={addZahlung}
            className="ml-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            + {t('crud.actions.addPayment')}
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">{t('crud.fields.date')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.amount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.type')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.reference')}</th>
              <th className="px-4 py-2 border">{t('crud.actions.actions')}</th>
            </tr>
          </thead>
          <tbody>
            {_data.map((zahlung, index) => (
              <tr key={index} className="border">
                <td className="px-4 py-2 border">
                  <input
                    type="date"
                    value={zahlung.datum}
                    onChange={(e) => updateZahlung(index, 'datum', e.target.value)}
                    className="w-full p-1 border rounded"
                  />
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
                  <select
                    value={zahlung.typ}
                    onChange={(e) => updateZahlung(index, 'typ', e.target.value)}
                    className="w-full p-1 border rounded"
                  >
                    <option value="zahlung">{t('crud.fields.payment')}</option>
                    <option value="skonto">{t('crud.fields.discount')}</option>
                    <option value="gutschrift">{t('crud.entities.creditNote')}</option>
                    <option value="storno">{t('crud.actions.reverse')}</option>
                  </select>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={zahlung.referenz || ''}
                    onChange={(e) => updateZahlung(index, 'referenz', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.paymentReference')}
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

function SettlementsList({ opId, t }: { opId: string; t: (key: string) => string }) {
  const { data: settlements, isLoading } = useQuery({
    queryKey: ['finance', 'open-items', 'settlements', opId],
    queryFn: async () => {
      const res = await apiClient.get<Array<{ id: string; payment_amount: number; payment_date: string | null; payment_reference: string; created_at: string | null }>>(
        `/api/v1/finance/open-items/${opId}/settlements`
      )
      return res
    },
    enabled: !!opId,
  })
  if (!opId) return null
  if (isLoading) return <p className="text-sm text-muted-foreground">{t('common.loading') ?? 'Laden…'}</p>
  const list = settlements ?? []
  const label = t('crud.fields.settlementHistory') ?? 'Ausgleichshistorie'
  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold">{label}</h3>
      {list.length === 0 ? (
        <p className="text-sm text-muted-foreground">{t('crud.fields.settlementHistoryEmpty') ?? 'Bisher keine gebuchten Ausgleiche.'}</p>
      ) : (
        <div className="overflow-x-auto rounded border">
          <table className="min-w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-3 py-2 text-left">{t('crud.fields.date')}</th>
                <th className="px-3 py-2 text-left">{t('crud.fields.reference')}</th>
                <th className="px-3 py-2 text-right">{t('crud.fields.amount')}</th>
              </tr>
            </thead>
            <tbody>
              {list.map((s) => (
                <tr key={s.id} className="border-t">
                  <td className="px-3 py-2">{s.payment_date ? new Date(s.payment_date).toLocaleDateString('de-DE') : '–'}</td>
                  <td className="px-3 py-2">{s.payment_reference ?? '–'}</td>
                  <td className="px-3 py-2 text-right">{Number(s.payment_amount).toLocaleString('de-DE', { minimumFractionDigits: 2 })} €</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default function OPDebitorenPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { data: fibuCockpit } = useFibuCockpit()
  const [isDirty, setIsDirty] = useState(false)
  const [actionLoadingKey, setActionLoadingKey] = useState<string | null>(null)
  const entityType = 'openItem'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'OP-Verwaltung (Debitoren)')

  // OTC-011-P1: Debitoren aus CRM laden statt hardcoded
  const { data: customers } = useQuery({
    queryKey: ['crm', 'customers', 'debitor-select'],
    queryFn: async () => {
      const res = await apiClient.get<Array<{ id: string; customer_number?: string; company_name?: string; name?: string }>>('/api/v1/crm/customers?limit=500')
      return (Array.isArray(res) ? res : []).map((c) => ({
        value: c.customer_number ?? c.id,
        label: `${c.customer_number ?? c.id} - ${c.company_name ?? c.name ?? ''}`.trim(),
      }))
    },
    staleTime: 5 * 60 * 1000,
  })
  const customerOptions = customers ?? []

  const opDebitorenConfig = createOpDebitorenConfig(t, entityTypeLabel, customerOptions)

  const opIdParam = searchParams.get('opId') ?? searchParams.get('op')
  const rechnungsnrParam = searchParams.get('rechnungsnr') ?? searchParams.get('rechnung')

  const { data: resolvedOpId, isLoading: resolvingOp } = useQuery({
    queryKey: ['otc-011-resolve-op', opIdParam, rechnungsnrParam],
    queryFn: async (): Promise<string | null> => {
      const direct = opIdParam?.trim()
      if (direct) {
        return direct
      }
      const nr = rechnungsnrParam?.trim()
      if (!nr) {
        return null
      }
      const res = await apiClient.get<{ items: Array<{ id: string; rechnungsnr?: string }> }>(
        `/api/v1/finance/open-items?konto_typ=debitoren&search=${encodeURIComponent(nr)}`,
      )
      const items = res.items ?? []
      const exact = items.find((i) => String(i.rechnungsnr ?? '') === nr) ?? items[0]
      return exact?.id ?? null
    },
    enabled: Boolean(opIdParam?.trim() || rechnungsnrParam?.trim()),
  })

  const maskId = useMemo(() => {
    if (!opIdParam?.trim() && !rechnungsnrParam?.trim()) {
      return undefined
    }
    if (resolvingOp) {
      return undefined
    }
    return resolvedOpId ?? undefined
  }, [opIdParam, rechnungsnrParam, resolvedOpId, resolvingOp])

  const showOtcHandoverHint = Boolean(opIdParam?.trim() || rechnungsnrParam?.trim())
  const noOpMatch =
    showOtcHandoverHint &&
    !resolvingOp &&
    rechnungsnrParam?.trim() &&
    !opIdParam?.trim() &&
    resolvedOpId === null

  const { data, loading, saveData } = useMaskData({
    apiUrl: opDebitorenConfig.api.baseUrl,
    id: maskId,
    transformResponse: (raw) => mapOpenItemApiToForm(raw as Record<string, unknown>),
  })

  const validate = (formData: any) => validateFields(getFieldsFromMaskConfig(opDebitorenConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast.error(`${Object.keys(errors).length} Feld(er) muessen korrigiert werden.`)
  }

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'zahlung') {
      // Zahlung buchen - fügt automatisch eine neue Zahlung hinzu
      const newZahlung = {
        datum: new Date().toISOString().split('T')[0],
        betrag: formData.offen || 0,
        typ: 'zahlung' as const,
        referenz: `Z-${Date.now()}`
      }

      const updatedZahlungen = [...(formData.zahlungen || []), newZahlung]
      const totalPaid = updatedZahlungen.reduce((sum: number, z: any) => sum + (z.betrag || 0), 0)

      formData.zahlungen = updatedZahlungen
      formData.offen = (formData.betrag || 0) - totalPaid
      formData.letzteZahlung = newZahlung.datum

      toast.success(t('crud.messages.paymentRecorded', { amount: newZahlung.betrag.toFixed(2) }))
    } else if (action === 'skonto') {
      // Skonto nutzen
      if (!formData.skontoBetrag || formData.skontoBetrag <= 0) {
        toast.error(t('crud.messages.noDiscountAvailable'))
        return
      }

      const skontoZahlung = {
        datum: new Date().toISOString().split('T')[0],
        betrag: formData.skontoBetrag,
        typ: 'skonto' as const,
        referenz: `SK-${Date.now()}`
      }

      const updatedZahlungen = [...(formData.zahlungen || []), skontoZahlung]
      const totalPaid = updatedZahlungen.reduce((sum: number, z: any) => sum + (z.betrag || 0), 0)

      formData.zahlungen = updatedZahlungen
      formData.offen = (formData.betrag || 0) - totalPaid
      formData.letzteZahlung = skontoZahlung.datum

      toast.success(t('crud.messages.discountUsed', { amount: skontoZahlung.betrag.toFixed(2) }))
    } else if (action === 'ausgleich') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      if (!formData.id) {
        toast.error(t('crud.messages.saveFirst'))
        return
      }

      // Process all payments as settlements
      if (formData.zahlungen && formData.zahlungen.length > 0) {
        try {
          for (const zahlung of formData.zahlungen) {
            if (zahlung.typ === 'storno') {
              // Skip reversed payments
              continue
            }

            const settlement = {
              op_id: formData.id,
              payment_amount: zahlung.betrag,
              payment_date: zahlung.datum,
              payment_reference: zahlung.referenz || `Z-${Date.now()}`,
              payment_type: zahlung.typ === 'skonto' ? 'discount' : 'payment',
              notes: zahlung.typ === 'gutschrift' ? t('crud.entities.creditNote') : null
            }

            await apiClient.post(`/api/v1/finance/open-items/${formData.id}/settle`, settlement)
          }

          // OTC-011-P3: Toast mit OP-Nummer statt Navigation zu leerer Maske
          const opNr = formData.opNummer || formData.id || ''
          toast.success(t('crud.messages.settlementSuccess') + (opNr ? ` (${opNr})` : ''))
          setIsDirty(false)
          navigate('/finance/offene-posten')
        } catch (error: any) {
          toast.error(error.message || t('crud.messages.settlementError'))
        }
      } else {
        // No payments to settle, just save the OP
        try {
          await saveData(formData)
          setIsDirty(false)
          toast.success(t('crud.messages.saveSuccess', { entityType: entityTypeLabel }))
          navigate('/finance/offene-posten')
        } catch (error) {
          // Error wird bereits in useMaskData behandelt
        }
      }
    } else if (action === 'mahnung') {
      // Mahnung erstellen
      if (!formData.id) {
        toast.error(t('crud.messages.saveFirst'))
        return
      }

      // OTC-011-P2: apiClient statt raw fetch (OIDC-kompatibel)
      try {
        await apiClient.post(`/api/v1/finance/dunning/${formData.id}/mahnung`)
        formData.mahnstufe = (formData.mahnstufe || 0) + 1
        toast.success(t('crud.messages.dunningCreated', { level: formData.mahnstufe }))
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message ?? t('crud.messages.dunningError')
        toast.error(msg)
      }
    } else if (action === 'export') {
      if (!formData.id) {
        toast.error(t('crud.messages.saveFirstGeneric'))
        return
      }
      setActionLoadingKey('export')
      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', { entity: 'open_items', format: 'pdf', id: formData.id })
        if (res?.url) window.open(res.url, '_blank')
        toast.success(t('crud.messages.exportCreated', { defaultValue: 'Export erstellt' }))
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast.error(msg)
      } finally {
        setActionLoadingKey(null)
      }
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('ausgleich', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm(t('crud.messages.unsavedChanges'))) {
      return
    }
    navigate('/finance/offene-posten')
  }
  const operationalStatus = normalizeOperationalStatus(
    fibuCockpit.dunning.overdue_items > 0 ? 'wartet_auf_mensch' : data?.offen > 0 ? 'in_pruefung' : 'abgeschlossen',
  )
  const operationalBlocker = noOpMatch
    ? `Kein Debitoren-OP fuer Rechnungsnr. "${rechnungsnrParam}" gefunden.`
    : fibuCockpit.dunning.overdue_items > 0
      ? `${fibuCockpit.dunning.overdue_items} ueberfaellige Debitoren-OP sind im Follow-up.`
      : null
  const contextSections = [
    {
      title: 'OP-Lage',
      items: [
        { label: 'OP-Nummer', value: String(data?.opNummer ?? rechnungsnrParam ?? 'Noch offen') },
        { label: 'Debitor', value: String(data?.debitorId ?? 'Nicht zugeordnet') },
        { label: 'Offener Betrag', value: `${Number(data?.offen ?? 0).toLocaleString('de-DE', { minimumFractionDigits: 2 })} EUR` },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Mahnstufe', value: `${Number(data?.mahnstufe ?? 0)}` },
        { label: 'Rueckstand', value: `${fibuCockpit.dunning.overdue_amount.toFixed(2)} EUR` },
        { label: 'Naechste Aktion', value: Number(data?.offen ?? 0) > 0 ? 'Ausgleich oder Mahnung' : 'Vorgang abgeschlossen' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Debitoren-OP aktiv', detail: String(data?.opNummer ?? rechnungsnrParam ?? 'Neuer OP') },
    ...(showOtcHandoverHint ? [{ label: 'OTC-Handover', detail: rechnungsnrParam ? `Rechnung ${rechnungsnrParam}` : `OP ${opIdParam}` }] : []),
    ...(Number(data?.offen ?? 0) > 0 ? [{ label: 'Offener Betrag', detail: `${Number(data?.offen ?? 0).toLocaleString('de-DE', { minimumFractionDigits: 2 })} EUR` }] : []),
  ]

  return (
    <div className="space-y-4 p-4">
      <OperationalCaseHeader
        title="Debitoren-OP steuern"
        description="Der Forderungsfall zeigt oben nur Rueckstand, Mahnbezug und die naechste zulaessige Folgeaktion."
        status={operationalStatus}
        owner="FIBU / Debitoren"
        blocker={operationalBlocker}
        nextAction={Number(data?.offen ?? 0) > 0 ? 'Zahlung erfassen, ausgleichen oder Mahnung erzeugen' : 'Vorgang nur noch revisionssicher nachhalten'}
        caseLabel={String(data?.opNummer ?? 'Debitoren-OP')}
        tags={['FIBU', 'Debitoren']}
      />
      <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
        <OperationalTimeline title="Forderungsverlauf" items={timelineItems} />
        <OperationalContextPanel title="OP-Kontext" sections={contextSections} />
      </div>
      <Alert>
        <Banknote className="h-4 w-4" />
        <AlertTitle>FIBU-Kernlage Debitoren</AlertTitle>
        <AlertDescription>
          {fibuCockpit.dunning.overdue_items} überfällige OP, {fibuCockpit.interest.candidate_count} Zinskandidaten und
          {` ${fibuCockpit.master_data.connector_profile_count} `}Connector-Profile im Revisionspfad.
        </AlertDescription>
      </Alert>
      {showOtcHandoverHint ? (
        <Alert>
          <Banknote className="h-4 w-4" />
          <AlertTitle>OTC-011 — Zahlungseingang / OP-Abstimmung</AlertTitle>
          <AlertDescription>
            {resolvingOp
              ? 'Offenen Posten werden aufgeloest …'
              : noOpMatch
                ? `Kein Debitoren-OP fuer Rechnungsnr. "${rechnungsnrParam}" gefunden. Legen Sie einen neuen OP an oder pruefen Sie die Nummer.`
                : `Zuordnung zu ${rechnungsnrParam ? `Rechnung ${rechnungsnrParam}` : `OP-ID ${opIdParam}`}. Zahlungen erfassen und ueber „Ausgleich“ verbuchen.`}
          </AlertDescription>
        </Alert>
      ) : null}
      <ObjectPage
        config={opDebitorenConfig}
        data={data}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading || resolvingOp}
        onAction={(key, formData) => handleAction(key, formData)}
        loadingActionKey={actionLoadingKey}
      />
    </div>
  )
}
