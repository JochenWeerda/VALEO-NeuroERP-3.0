import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskValidation, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { z } from 'zod'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'
import { lookupIBAN, formatIBAN, validateIBAN } from '@/lib/utils/iban-validator'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/axios'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { LeaveConfirmDialog } from '@/components/LeaveConfirmDialog'
import { useUnsavedChanges } from '@/hooks/useUnsavedChanges'

// Zod-Schema für Lastschriften Debitoren (wird in Komponente mit i18n erstellt)
const createLastschriftenSchema = (t: any) => z.object({
  laufNummer: z.string().min(1, t('crud.messages.validationError')),
  ausfuehrungsDatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
  gesamtBetrag: z.number().positive(t('crud.messages.validationError')),
  anzahlLastschriften: z.number().min(1, t('crud.messages.validationError')),
  status: z.enum(['entwurf', 'freigegeben', 'ausgefuehrt', 'storniert']),
  freigegebenAm: z.string().optional(),
  freigegebenDurch: z.string().optional(),
  ausgefuehrtAm: z.string().optional(),

  // SEPA-Details
  creditorId: z.string().min(1, t('crud.messages.validationError')),
  auftraggeberName: z.string().min(1, t('crud.messages.validationError')),
  auftraggeberIban: z.string().regex(/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/, t('crud.messages.validationError')),

  // Lastschriften
  lastschriften: z.array(z.object({
    debitorId: z.string().min(1, t('crud.messages.validationError')),
    debitorName: z.string().min(1, t('crud.messages.validationError')),
    iban: z.string().regex(/^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/, t('crud.messages.validationError')),
    bic: z.string().optional(),
    betrag: z.number().positive(t('crud.messages.validationError')),
    mandatReferenz: z.string().min(1, t('crud.messages.validationError')),
    mandatDatum: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, t('crud.messages.validationError')),
    verwendungszweck: z.string().min(1, t('crud.messages.validationError')),
    sequenzTyp: z.enum(['FRST', 'RCUR', 'FNAL', 'OOFF'], {
      errorMap: () => ({ message: t('crud.messages.validationError') })
    }),
    opReferenz: z.string().optional()
  })).min(1, t('crud.messages.validationError')),

  notizen: z.string().optional()
})

// Konfiguration für Lastschriften Debitoren ObjectPage (wird in Komponente mit i18n erstellt)
const createLastschriftenConfig = (t: any, entityTypeLabel: string): MaskConfig => ({
  title: entityTypeLabel,
  subtitle: t('crud.fields.collectSepaDirectDebits'),
  type: 'object-page',
  tabs: [
    {
      key: 'grunddaten',
      label: t('crud.detail.basicInfo'),
      fields: [
        {
          name: 'laufNummer',
          label: t('crud.fields.runNumber'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.directDebitRunNumber')
        },
        {
          name: 'ausfuehrungsDatum',
          label: t('crud.fields.executionDate'),
          type: 'date',
          required: true
        },
        {
          name: 'status',
          label: t('crud.fields.status'),
          type: 'select',
          required: true,
          options: [
            { value: 'entwurf', label: t('status.draft') },
            { value: 'freigegeben', label: t('status.approved') },
            { value: 'ausgefuehrt', label: t('crud.fields.executed') },
            { value: 'storniert', label: t('crud.fields.cancelled') }
          ]
        },
        {
          name: 'gesamtBetrag',
          label: t('crud.fields.totalAmount'),
          type: 'number',
          readonly: true,
          step: 0.01
        },
        {
          name: 'anzahlLastschriften',
          label: t('crud.fields.numberOfDirectDebits'),
          type: 'number',
          readonly: true
        }
      ],
      layout: 'grid',
      columns: 2
    },
    {
      key: 'creditor',
      label: t('crud.fields.creditorInformation'),
      fields: [
        {
          name: 'creditorId',
          label: t('crud.fields.creditorId'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.creditorId')
        },
        {
          name: 'auftraggeberName',
          label: t('crud.fields.originatorName'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.companyName')
        },
        {
          name: 'auftraggeberIban',
          label: t('crud.fields.originatorIban'),
          type: 'text',
          required: true,
          placeholder: t('crud.tooltips.placeholders.iban')
        }
      ]
    },
    {
      key: 'lastschriften',
      label: t('crud.fields.directDebits'),
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
      label: t('crud.fields.approvalAndExecution'),
      fields: [
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
        },
        {
          name: 'ausgefuehrtAm',
          label: t('crud.fields.executedOn'),
          type: 'date',
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
          placeholder: t('crud.tooltips.placeholders.directDebitRunNotes')
        }
      ]
    }
  ],
  actions: [
    { key: 'add-direct-debit', label: t('crud.actions.addDirectDebit'), type: 'secondary' },
    { key: 'validate-mandates', label: t('crud.actions.validateMandates'), type: 'secondary' },
    { key: 'preview', label: t('crud.actions.sepaPreview'), type: 'secondary' },
    { key: 'approve', label: t('crud.actions.approve'), type: 'primary' },
    { key: 'execute', label: t('crud.actions.execute'), type: 'primary' },
    { key: 'export', label: t('crud.actions.sepaExport'), type: 'secondary' }
  ],
  api: {
    baseUrl: '/api/v1/finance/direct-debits',
    endpoints: {
      list: '/api/v1/finance/direct-debits',
      get: '/api/v1/finance/direct-debits/{id}',
      create: '/api/v1/finance/direct-debits',
      update: '/api/v1/finance/direct-debits/{id}',
      delete: '/api/v1/finance/direct-debits/{id}'
    }
  } as any,
  validation: createLastschriftenSchema(t),
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin']
})

// Lastschriften-Tabelle Komponente
function LastschriftenTable({ data: _data, onChange }: { data: any[], onChange: (_data: any[]) => void }) {
  const { t } = useTranslation()
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

  const updateLastschrift = async (index: number, field: string, value: any) => {
    const newData = [..._data]
    
    // Format IBAN if field is iban
    if (field === 'iban' && value) {
      const normalized = value.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
      const formatted = formatIBAN(normalized)
      newData[index] = { ...newData[index], [field]: formatted }
      
      // Auto-lookup IBAN when it changes and seems complete
      if (normalized.length >= 15 && normalized.length <= 34 && validateIBAN(normalized)) {
        // Debounce IBAN lookup
        setTimeout(async () => {
          try {
            const result = await lookupIBAN(normalized)
            if (result.valid && result.bic) {
              const updatedData = [..._data]
              updatedData[index] = {
                ...updatedData[index],
                iban: formatted,
                bic: result.bic || updatedData[index].bic
              }
              onChange(updatedData)
              toast.success(t('crud.messages.ibanLookupSuccess', {
                defaultValue: 'BIC automatisch ausgefüllt',
                bankName: result.bank_name || ''
              }))
            }
          } catch (error) {
            // Silent error for auto-lookup
            console.warn('IBAN lookup failed:', error)
          }
        }, 1000)
      }
    } else {
      newData[index] = { ...newData[index], [field]: value }
    }
    
    onChange(newData)
  }

  const removeLastschrift = (index: number) => {
    onChange(_data.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{t('crud.fields.directDebits')}</h3>
        <button
          onClick={addLastschrift}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + {t('crud.actions.addDirectDebit')}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border border-gray-300">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 border">{t('crud.entities.debtor')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.iban')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.amount')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.mandate')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.sequence')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.purpose')}</th>
              <th className="px-4 py-2 border">{t('crud.fields.opReference')}</th>
              <th className="px-4 py-2 border">{t('crud.actions.delete')}</th>
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
                      placeholder={t('crud.tooltips.placeholders.debtorNumber')}
                    />
                    <input
                      type="text"
                      value={lastschrift.debitorName}
                      onChange={(e) => updateLastschrift(index, 'debitorName', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                      placeholder={t('crud.fields.name')}
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
                      placeholder={t('crud.fields.iban')}
                    />
                    <input
                      type="text"
                      value={lastschrift.bic || ''}
                      onChange={(e) => updateLastschrift(index, 'bic', e.target.value)}
                      className="w-full p-1 border rounded text-sm"
                      placeholder={t('crud.tooltips.placeholders.bicOptional')}
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
                      placeholder={t('crud.tooltips.placeholders.mandateReference')}
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
                    <option value="FRST">{t('crud.fields.sequenceFRST')}</option>
                    <option value="RCUR">{t('crud.fields.sequenceRCUR')}</option>
                    <option value="FNAL">{t('crud.fields.sequenceFNAL')}</option>
                    <option value="OOFF">{t('crud.fields.sequenceOOFF')}</option>
                  </select>
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={lastschrift.verwendungszweck}
                    onChange={(e) => updateLastschrift(index, 'verwendungszweck', e.target.value)}
                    className="w-full p-1 border rounded"
                    placeholder={t('crud.tooltips.placeholders.invoiceNumber')}
                  />
                </td>
                <td className="px-4 py-2 border">
                  <input
                    type="text"
                    value={lastschrift.opReferenz || ''}
                    onChange={(e) => updateLastschrift(index, 'opReferenz', e.target.value)}
                    className="w-full p-1 border rounded text-sm"
                    placeholder={t('crud.tooltips.placeholders.opReference')}
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
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isDirty, setIsDirty] = useState(false)
  const [formData, setFormData] = useState<any>({})
  const [actionLoadingKey, setActionLoadingKey] = useState<string | null>(null)
  const entityType = 'directDebit'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Lastschriften Debitoren')
  const lastschriftenConfig = createLastschriftenConfig(t, entityTypeLabel)

  const { data, loading, saveData, updateData } = useMaskData({
    apiUrl: lastschriftenConfig.api.baseUrl,
    id: 'new'
  })
  const initialFormData = {
    laufNummer: '',
    ausfuehrungsDatum: new Date().toISOString().slice(0, 10),
    gesamtBetrag: 0,
    anzahlLastschriften: 0,
    status: 'entwurf',
    freigegebenAm: '',
    freigegebenDurch: '',
    ausgefuehrtAm: '',
    creditorId: '',
    auftraggeberName: '',
    auftraggeberIban: '',
    lastschriften: [],
    notizen: '',
  }
  const safeFormData = { ...initialFormData, ...(data ?? formData ?? {}) }

  const { validate, showValidationToast } = useMaskValidation(lastschriftenConfig.validation)

  // Handle form data changes for IBAN lookup
  const handleFormChange = (newData: any) => {
    setFormData(newData)
    setIsDirty(true)
    
    // Auto-lookup Auftraggeber-IBAN when it changes
    const auftraggeberIban = newData?.auftraggeberIban
    if (auftraggeberIban && auftraggeberIban.replace(/\s/g, '').length >= 15) {
      const normalized = auftraggeberIban.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
      if (normalized.length >= 15 && normalized.length <= 34 && validateIBAN(normalized)) {
        setTimeout(async () => {
          try {
            const result = await lookupIBAN(normalized)
            if (result.valid && result.bic) {
              const updatedData = { ...newData, auftraggeberIban: formatIBAN(normalized) }
              setFormData(updatedData)
              updateData?.(updatedData)
              toast.success(t('crud.messages.ibanLookupSuccess', {
                defaultValue: 'BIC automatisch ausgefüllt',
                bankName: result.bank_name || ''
              }))
            }
          } catch (error) {
            console.warn('IBAN lookup failed:', error)
          }
        }, 1000) // 1 second debounce
      }
    }
  }

  const { handleAction } = useMaskActions(async (action: string, formData: any) => {
    if (action === 'add-direct-debit') {
      toast({ title: 'Hinweis', description: 'Lastschriften werden direkt in der Tabelle hinzugefügt.' })
    } else if (action === 'validate-mandates') {
      const lastschriften: any[] = formData?.lastschriften ?? []
      const errors: string[] = []
      lastschriften.forEach((ls: any, idx: number) => {
        if (!ls.iban) errors.push(`Zeile ${idx + 1}: IBAN fehlt`)
        if (!ls.bic) errors.push(`Zeile ${idx + 1}: BIC fehlt`)
        if (!ls.mandatReferenz) errors.push(`Zeile ${idx + 1}: Mandat-Referenz fehlt`)
        if (!ls.mandatDatum) errors.push(`Zeile ${idx + 1}: Mandat-Datum fehlt`)
        if (!ls.debitor) errors.push(`Zeile ${idx + 1}: Debitor fehlt`)
      })
      if (lastschriften.length === 0) {
        toast({ title: 'Mandatsprüfung', description: 'Keine Lastschriften vorhanden.', variant: 'destructive' })
      } else if (errors.length > 0) {
        toast({ title: `Mandatsprüfung: ${errors.length} Fehler`, description: errors.slice(0, 3).join(' | '), variant: 'destructive' })
      } else {
        toast({ title: 'Mandatsprüfung erfolgreich', description: `${lastschriften.length} Mandate geprüft — alle vollständig.` })
      }
    } else if (action === 'preview') {
      // SEPA-Vorschau
      window.open('/api/v1/finance/direct-debits/preview', '_blank')
    } else if (action === 'approve') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }
      setActionLoadingKey('approve')
      try {
        await saveData({ ...formData, status: 'freigegeben', freigegebenAm: new Date().toISOString() })
        setIsDirty(false)
        toast({ title: 'Freigegeben', description: 'Lastschriftlauf wurde freigegeben.' })
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      } finally {
        setActionLoadingKey(null)
      }
    } else if (action === 'execute') {
      const isValid = validate(formData)
      if (!isValid.isValid) {
        showValidationToast(isValid.errors)
        return
      }
      setActionLoadingKey('execute')
      try {
        await apiClient.post('/api/v1/finance/direct-debit/run', formData ?? {})
        toast({ title: t('crud.messages.executed', { defaultValue: 'Zahlungslauf ausgeführt' }) })
        setIsDirty(false)
        navigate('/finance/lastschriften-debitoren')
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      } finally {
        setActionLoadingKey(null)
      }
    } else if (action === 'export') {
      setActionLoadingKey('export')
      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', { entity: 'direct_debit', format: 'sepa' })
        if (res?.url) window.open(res.url, '_blank')
        toast({ title: t('crud.actions.sepaExport'), description: t('crud.messages.exportCreated', { defaultValue: 'Export erstellt' }) })
      } catch (error: any) {
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: t('common.error'), description: msg })
      } finally {
        setActionLoadingKey(null)
      }
    }
  })

  const handleSave = async (formData: any) => {
    await handleAction('execute', formData)
  }

  const handleCancel = () => {
    navigate('/finance/lastschriften-debitoren')
  }

  const blocker = useUnsavedChanges(isDirty)

  return (
    <>
      <ModuleToolbar backTarget="/finance/lastschriften-debitoren" closeTarget="/finance/lastschriften-debitoren" title={entityTypeLabel} />
      <LeaveConfirmDialog blocker={blocker} onSave={() => handleSave(safeFormData)} title={t('crud.messages.unsavedChanges', { defaultValue: 'Ungespeicherte Änderungen' })} description={t('crud.messages.unsavedChangesDescription', { defaultValue: 'Möchten Sie speichern, verwerfen oder hier bleiben?' })} />
      <ObjectPage
        config={lastschriftenConfig}
        data={safeFormData}
        onChange={handleFormChange}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={(key, fd) => handleAction(key, fd ?? safeFormData)}
        loadingActionKey={actionLoadingKey}
      />
    </>
  )
}
