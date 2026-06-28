import { useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { ObjectPage } from '@/components/mask-builder'
import { useMaskData, useMaskActions } from '@/components/mask-builder/hooks'
import { MaskConfig } from '@/components/mask-builder/types'
import { getFieldsFromMaskConfig, validateFields } from '@/components/mask-builder/validation'
import { toast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'
import { buildDecisionView } from '@/policy/decision-view'
import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'
import { useApprovalDensityProfile } from '@/features/workflow/useApprovalDensityProfile'
import { WorkflowEntryBanner, readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAccountingPeriods, useFibuCockpit } from '@/lib/api/fibu'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import {
  CrudCapabilityChecklist,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow'
import { normalizeOperationalStatus } from '@/lib/operational-status'

type CloseRoleFocus = 'all' | 'accounting' | 'controlling' | 'tax-advisor' | 'management' | 'audit'

const closeRoleProfiles: Array<{ id: CloseRoleFocus; label: string; description: string }> = [
  {
    id: 'all',
    label: 'Alle Rollen',
    description: 'Zeigt die Abschlusslage fuer alle Beteiligten: FIBU, Controlling, Steuerbuero, Leitung und Audit.',
  },
  {
    id: 'accounting',
    label: 'FIBU',
    description: 'Fokus auf Periode, Buchungsstatus, Abstimmungen, Sperre und Export.',
  },
  {
    id: 'controlling',
    label: 'Controlling',
    description: 'Fokus auf GuV, Bilanz, Abweichungen und Abschlussreife.',
  },
  {
    id: 'tax-advisor',
    label: 'Steuerbuero',
    description: 'Fokus auf Steuerpruefung, VAT-Periode, Export und Nachweise.',
  },
  {
    id: 'management',
    label: 'Leitung',
    description: 'Fokus auf Entscheidung: abschliessen, warten oder offene Punkte klaeren.',
  },
  {
    id: 'audit',
    label: 'Audit',
    description: 'Fokus auf Protokoll, Freigaben, Sperre und nachvollziehbare Abschlussnachweise.',
  },
]

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
         } as Field,
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
    } as Field,
    {
      key: 'abgrenzungen_custom',
      label: '',
      fields: [],
      customRender: (_data: Record<string, unknown>, onChange: (_data: Record<string, unknown>) => void) => (
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
    } as Field,
    {
      key: 'rueckstellungen_custom',
      label: '',
      fields: [],
      customRender: (_data: Record<string, unknown>, onChange: (_data: Record<string, unknown>) => void) => (
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
    baseUrl: '/api/v1/finance/closing-checklists',
    endpoints: {
      list: '/api/v1/finance/closing-checklists',
      get: '/api/v1/finance/closing-checklists/{id}',
      create: '/api/v1/finance/closing-checklists',
      update: '/api/v1/finance/closing-checklists/{id}',
      delete: '/api/v1/finance/closing-checklists/{id}'
    }
  } as Field,
  permissions: ['fibu.read', 'fibu.write', 'fibu.admin']
}

// Abgrenzungen-Tabelle Komponente
function AbgrenzungenTable({ data: _data, onChange }: { data: Record<string, unknown>[], onChange: (_data: Record<string, unknown>[]) => void }) {
  const addPosten = () => {
    onChange([..._data, {
      beschreibung: '',
      betrag: 0,
      typ: 'aktiv'
    }])
  }

  const updatePosten = (index: number, field: string, value: unknown) => {
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
function RueckstellungenTable({ data: _data, onChange }: { data: Record<string, unknown>[], onChange: (_data: Record<string, unknown>[]) => void }) {
  const addRueckstellung = () => {
    onChange([..._data, {
      beschreibung: '',
      betrag: 0,
      zweck: ''
    }])
  }

  const updateRueckstellung = (index: number, field: string, value: unknown) => {
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
  const [searchParams] = useSearchParams()
  const workflowContext = readWorkflowEntryContext(searchParams)
  const [isDirty, setIsDirty] = useState(false)

  const [workspaceData, setWorkspaceData] = useState<Record<string, unknown>>({})
  const [roleFocus, setRoleFocus] = useState<CloseRoleFocus>('all')
  const currentActor = localStorage.getItem('userEmail') || localStorage.getItem('username') || 'api'
  const { data: fibuCockpit } = useFibuCockpit()
  const { data: periods } = useAccountingPeriods()

  const { data, loading } = useMaskData({
    apiUrl: abschlussConfig.api.baseUrl,
    id: 'new',
    transformResponse: (response: unknown) => {
      if (response?.data) {
        return {
          ...response.data,
          id: response.data.id,
          periode: response.data.period,
          abschlussTyp:
            response.data.closing_type === 'yearly'
              ? 'jahresabschluss'
              : response.data.closing_type === 'quarterly'
                ? 'quartalsabschluss'
                : 'monatsabschluss',
          status: response.data.status,
          abgeschlossenAm: response.data.completed_at,
          abgeschlossenDurch: response.data.completed_by,
          approval_status: response.data.approval_status,
          approval_can_close: response.data.approval_can_close,
          approval_override_resolution: response.data.approval_override_resolution,
          approval_explainability: response.data.approval_explainability,
        }
      }
      return response
    }
  })
  const effectiveData = Object.keys(workspaceData).length > 0 ? workspaceData : data
  const approvalDecisionView = buildDecisionView(effectiveData?.approval_explainability)

  const validate = (formData: Record<string, unknown>) => validateFields(getFieldsFromMaskConfig(abschlussConfig), formData ?? {})
  const showValidationToast = (errors: Record<string, string>) => {
    toast({
      variant: 'destructive',
      title: 'Validierungsfehler',
      description: `${Object.keys(errors).length} Feld(er) muessen korrigiert werden.`,
    })
  }

  const buildClosingActionPayload = (formData: Record<string, unknown>) => ({
    checklist_id: formData?.id || undefined,
    period: formData?.periode,
    closing_type: formData?.abschlussTyp,
    actor: currentActor,
  })

  const applyWorkspaceResponse = response => {
    const payload = response?.data ?? response
    if (!payload) {
      return
    }
    setWorkspaceData({
      ...payload,
      id: payload.id,
      periode: payload.period,
      abschlussTyp:
        payload.closing_type === 'yearly'
          ? 'jahresabschluss'
          : payload.closing_type === 'quarterly'
            ? 'quartalsabschluss'
            : 'monatsabschluss',
      status: payload.status,
      abgeschlossenAm: payload.completed_at,
      abgeschlossenDurch: payload.completed_by,
      approval_status: payload.approval_status,
      approval_can_close: payload.approval_can_close,
      approval_override_resolution: payload.approval_override_resolution,
      approval_explainability: payload.approval_explainability,
    })
  }

  const { handleAction, loadingActionKey } = useMaskActions(async (action: string, formData: Record<string, unknown>) => {
    if (action === 'calculate') {

      try {
        const response = await apiClient.post('/api/v1/finance/closing/calculate', buildClosingActionPayload(formData))
        applyWorkspaceResponse(response)
        toast({ title: 'Berechnung abgeschlossen', description: 'Abschlusszahlen wurden berechnet.' })
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        toast({ variant: 'destructive', title: 'Fehler', description: error.response?.data?.detail ?? error.message })
      }
      return
    }
    if (action === 'validate') {
      const validationErrors = validate(formData)
      if (Object.keys(validationErrors).length === 0) {
        toast({ title: 'Abschlussprüfung erfolgreich!' })
      } else {
        showValidationToast(validationErrors)
      }
      return
    }
    if (action === 'approve') {

      try {
        const response = await apiClient.post('/api/v1/finance/closing/approve', buildClosingActionPayload(formData))
        applyWorkspaceResponse(response)
        toast({ title: 'Abschluss freigegeben', description: 'Abschlussgenehmigung wurde erteilt.' })
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        toast({ variant: 'destructive', title: 'Fehler', description: error.response?.data?.detail ?? error.message })
      }
      return
    }
    if (action === 'close') {
      const errors = validate(formData)
      if (Object.keys(errors).length > 0) {
        showValidationToast(errors)
        return
      }

      try {
        const response = await apiClient.post('/api/v1/finance/closing/run', buildClosingActionPayload(formData))
        applyWorkspaceResponse(response)
        toast({ title: 'Abschluss durchgeführt' })
        setIsDirty(false)
        navigate('/finance/abschluss')
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: 'Fehler', description: msg })
      }
      return
    }
    if (action === 'lock') {
      if (!confirm('Abschluss sperren? Diese Aktion kann nicht rückgängig gemacht werden.')) return

      try {
        const response = await apiClient.post('/api/v1/finance/closing/lock', buildClosingActionPayload(formData))
        applyWorkspaceResponse(response)
        toast({ title: 'Abschluss gesperrt', description: 'Die Periode wurde endgültig gesperrt.' })
        navigate('/finance/abschluss')
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        toast({ variant: 'destructive', title: 'Fehler', description: error.response?.data?.detail ?? error.message })
      }
      return
    }
    if (action === 'export') {

      try {
        const res = await apiClient.post<{ url?: string }>('/api/v1/export/list', { entity: 'closing', format: 'pdf' })
        if (res?.url) window.open(res.url, '_blank')
        toast({ title: 'Export erstellt' })
      } catch (_rawErr: unknown) {
        const error = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
        const msg = error.response?.data?.detail ?? error.message
        toast({ variant: 'destructive', title: 'Fehler', description: msg })
      }
    }
  })

  const handleSave = async (formData: Record<string, unknown>) => {
    await handleAction('close', formData)
  }

  const handleCancel = () => {
    if (isDirty && !confirm('Ungespeicherte Änderungen gehen verloren. Wirklich abbrechen?')) {
      return
    }
    navigate('/finance/abschluss')
  }

  const approvalDensityProfile = useApprovalDensityProfile('finance-closing', approvalDecisionView)
  const adjustingPeriods = periods.filter((period) => period.status === 'ADJUSTING').length
  const operationalStatus = normalizeOperationalStatus(
    !effectiveData?.approval_can_close && effectiveData?.id
      ? 'wartet_auf_mensch'
      : effectiveData?.status,
  )
  const operationalBlocker = !effectiveData?.approval_can_close && effectiveData?.id
    ? 'Die Periode ist noch nicht abschliessbar. Freigabe- oder Abstimmungsbedarf ist offen.'
    : fibuCockpit.annual_close.ready_for_year_close
      ? null
      : 'Jahreswechsel ist noch nicht stabil. Reorganisator und Abstimmung muessen weiter bereinigt werden.'
  const nextCloseAction = effectiveData?.approval_can_close
    ? 'Abschluss berechnen, freigeben und danach Periode sperren.'
    : operationalBlocker ?? 'Periode auswaehlen und Abschlusspruefung starten.'
  const hasSelectedPeriod = Boolean(effectiveData?.periode)
  const hasReconciliation = Boolean(effectiveData?.kontenabstimmungDurchgefuehrt || fibuCockpit.annual_close.ready_for_year_close)
  const hasApproval = Boolean(effectiveData?.approval_can_close)
  const isClosed = effectiveData?.status === 'abgeschlossen' || effectiveData?.status === 'gesperrt'
  const closeTaskItems: UxTaskItem[] = [
    {
      label: 'Periode festlegen',
      done: hasSelectedPeriod,
      hint: hasSelectedPeriod ? `Abschluss wird fuer ${effectiveData.periode} gefuehrt.` : 'Periode eintragen oder Abschlussfall laden.',
    },
    {
      label: 'Konten und Nebenbuecher abstimmen',
      done: hasReconciliation,
      hint: hasReconciliation ? 'Abstimmung ist als erledigt oder stabil bewertet.' : 'Offene Perioden, Journal und VAT-Periode pruefen.',
    },
    {
      label: 'Freigabe einholen',
      done: hasApproval,
      hint: hasApproval ? 'Abschluss ist laut Checkliste abschliessbar.' : 'Freigabe- oder Abstimmungsbedarf vor Abschluss klaeren.',
    },
    {
      label: 'Sperren und exportieren',
      done: isClosed,
      hint: isClosed ? 'Periode ist abgeschlossen oder gesperrt.' : 'Nach erfolgreichem Abschluss Export erzeugen und Periode sperren.',
    },
  ]
  const closeCrudCapabilities = [
    {
      key: 'create',
      label: 'Anlegen',
      available: true,
      hint: 'Neue Abschlussfaelle koennen ueber Periode und Abschluss-Typ vorbereitet werden.',
    },
    {
      key: 'read',
      label: 'Lesen',
      available: true,
      hint: 'Periode, Revisionslage, Governance und Abschlusszahlen sind sichtbar.',
    },
    {
      key: 'update',
      label: 'Bearbeiten',
      available: !isClosed,
      hint: isClosed ? 'Gesperrte Perioden werden nicht mehr direkt bearbeitet.' : 'Pruefungen, Abgrenzungen, Rueckstellungen und Notizen koennen gepflegt werden.',
    },
    {
      key: 'delete',
      label: 'Loeschen/Storno',
      available: false,
      hint: 'Abschlussfaelle werden nicht geloescht; Korrekturen laufen ueber Wiedereroeffnung oder neuen Abschlusslauf.',
    },
    {
      key: 'approve',
      label: 'Freigeben',
      available: Boolean(effectiveData?.id),
      hint: 'Freigabe und Abschlusslauf sind als gefuehrte Aktionen vorhanden.',
    },
    {
      key: 'export',
      label: 'Export',
      available: Boolean(effectiveData?.id),
      hint: 'PDF-/Listenexport ist nach angelegtem Abschlussfall verfuegbar.',
    },
    {
      key: 'audit',
      label: 'Audit',
      available: true,
      hint: 'Freigabe, Abschluss, Sperre und Revisionseintraege bleiben nachvollziehbar.',
    },
  ]
  const contextSections = [
    {
      title: 'Periode',
      items: [
        { label: 'Periode', value: effectiveData?.periode || 'Noch offen' },
        { label: 'Typ', value: effectiveData?.abschlussTyp || 'Monatsabschluss' },
        { label: 'Status', value: effectiveData?.status || 'offen' },
      ],
    },
    {
      title: 'Revisionslage',
      items: [
        { label: 'Journal zuletzt', value: fibuCockpit.revision.last_entry_date ?? 'n/a' },
        { label: 'VAT-Periode', value: fibuCockpit.annual_close.latest_vat_period ?? 'n/a' },
        { label: 'Reorganisator', value: `${adjustingPeriods} offene Perioden` },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Freigabe', value: effectiveData?.approval_status || 'offen' },
        { label: 'Abschliessbar', value: effectiveData?.approval_can_close ? 'Ja' : 'Nein' },
        { label: 'Owner', value: effectiveData?.freigegebenDurch || effectiveData?.abgeschlossenDurch || 'Finance' },
      ],
    },
  ]
  const timelineItems = [
    ...(effectiveData?.freigegebenAm
      ? [{ label: 'Freigegeben', timestamp: effectiveData.freigegebenAm, detail: effectiveData.freigegebenDurch || undefined }]
      : [{ label: 'Abschlussfall aktiv', detail: 'Periode wird abgestimmt, geprueft und vorbereitet.' }]),
    ...(effectiveData?.abgeschlossenAm
      ? [{ label: 'Abgeschlossen', timestamp: effectiveData.abgeschlossenAm, detail: effectiveData.abgeschlossenDurch || undefined }]
      : [{ label: 'Jahreswechsel-Lage', detail: fibuCockpit.annual_close.ready_for_year_close ? 'stabil' : 'offene Klaerungen' }]),
    ...(fibuCockpit.revision.last_entry_date
      ? [{ label: 'Letzter Revisionseintrag', detail: fibuCockpit.revision.last_entry_date }]
      : []),
  ]

  return (
    <>
      {effectiveData?.id && approvalDecisionView !== null ? (
        <ProcessStatusPanel view={approvalDecisionView} className="mb-4 px-4 py-3" densityProfileOverride={approvalDensityProfile}>
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            <div>
              <div className="text-xs uppercase tracking-wide text-current/70">Checklistenstatus</div>
              <div className="mt-1 font-medium">{effectiveData.status || '-'}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wide text-current/70">Freigabestatus</div>
              <div className="mt-1 font-medium">{effectiveData.approval_status || '-'}</div>
            </div>
            <div>
              <div className="text-xs uppercase tracking-wide text-current/70">Abschliessbar</div>
              <div className="mt-1 font-medium">{effectiveData.approval_can_close ? 'Ja' : 'Nein'}</div>
            </div>
          </div>
        </ProcessStatusPanel>
      ) : null}
      {workflowContext ? (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover aus Finance-to-Close"
          description="Periode, Abstimmung, Meldewesen und Freigaben werden jetzt im Abschlussarbeitsplatz gepflegt. Der Flow-Fall bleibt als Referenz erhalten."
        />
      ) : null}
      <div className="space-y-4 px-4 pb-4">
        <OperationalCaseHeader
          title="Abschlussfall steuern"
          description="Die Seite verdichtet Periodenlage, Governance und Revisionssicherheit in einer schlanken Leitansicht ueber dem eigentlichen Abschlussarbeitsplatz."
          status={operationalStatus}
          owner={effectiveData?.freigegebenDurch || effectiveData?.abgeschlossenDurch || 'Finance'}
          blocker={operationalBlocker}
          nextAction={nextCloseAction}
          caseLabel={effectiveData?.periode ? `Periode ${effectiveData.periode}` : 'Abschlussfall'}
          tags={['FIBU', 'Abschluss']}
        />
        <RoleFocusBar
          roles={closeRoleProfiles}
          value={roleFocus}
          onChange={setRoleFocus}
          visibleCount={roleFocus === 'all' ? 5 : 1}
          totalCount={5}
        />
        <ManagementDecisionPanel
          decision={{
            allowed: hasApproval,
            allowedLabel: 'Abschluss moeglich',
            blockedLabel: 'Abschluss gestoppt',
            summary: hasApproval
              ? 'Die Abschluss-Checkliste erlaubt den Abschlusslauf. Bitte vor der Sperre Export und Nachweise erzeugen.'
              : operationalBlocker ?? 'Der Abschluss ist noch nicht freigegeben. Pruefen Sie Periode, Abstimmungen und Freigaben.',
            blockerCount: hasApproval ? 0 : 1,
            nextFocus: nextCloseAction,
            template: {
              label: 'Abschluss pruefen und freigeben',
              href: '/finance/abschluss',
            },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan title="Close-Aufgabenplan" items={closeTaskItems} />
          <NextActionPanel
            action={nextCloseAction}
            tone={hasApproval ? 'emerald' : adjustingPeriods > 0 ? 'amber' : 'blue'}
          />
        </div>
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTimeline title="Abschlussverlauf" items={timelineItems} />
          <OperationalContextPanel title="Abschlusskontext" sections={contextSections} />
        </div>
        <CrudCapabilityChecklist capabilities={closeCrudCapabilities} />
      </div>
      <div className="grid gap-4 px-4 pb-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Jahreswechsel</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{fibuCockpit.annual_close.ready_for_year_close ? 'stabil' : 'offene Klärungen'}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Reorganisator</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-semibold">{adjustingPeriods}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Journal zuletzt</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{fibuCockpit.revision.last_entry_date ?? 'n/a'}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">VAT-Periode</CardTitle></CardHeader>
          <CardContent><div className="text-sm font-semibold">{fibuCockpit.annual_close.latest_vat_period ?? 'n/a'}</div></CardContent>
        </Card>
      </div>
      <ObjectPage
        config={abschlussConfig}
        data={effectiveData}
        onSave={handleSave}
        onCancel={handleCancel}
        isLoading={loading}
        onAction={(key, formData) => handleAction(key, formData)}
        loadingActionKey={loadingActionKey}
      />
    </>
  )
}
