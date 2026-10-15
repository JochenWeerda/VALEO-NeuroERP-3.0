import { useMemo, useState } from 'react'
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import { jwtDecode } from 'jwt-decode'
import { UniversalMaskRenderer, useHumanActionDispatch, useUniversalMaskRuntime } from '@/components/mask-builder'
import { ActionInputDialog } from '@/components/mask-builder/renderers/ActionInputDialog'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { harvestControlBase } from '@/components/mask-builder/runtime/harvest-control-command-adapter'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'
import { useScreenDefinition } from '@/lib/api/masks'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { auth } from '@/lib/auth'
import { tenantFromToken } from '@/lib/tenant-from-token'
import { useAuth } from '@/hooks/useAuth'

type Rule = { id: string; definition: Record<string, unknown>; content_hash: string }
type Context = { context_hash: string; state: { acceptance: { id: string }; [key: string]: unknown };
  calculation_hash?: string; calculation_current: boolean; release_status: string; issues: string[];
  calculation_approval?: { calculation_hash: string; expires_at: string };
  calculation_result?: { total_net_amount_eur: number; total_vat_amount_eur: number; total_gross_amount_eur: number;
    warnings: string[]; positions: Record<string, unknown>[] } }

function ControlMask(): JSX.Element {
  const schema = useScreenDefinition('agrar/harvest-controls')
  const [selected, setSelected] = useState<Rule>()
  const [context, setContext] = useState<Context>()
  const [feedback, setFeedback] = useState('Vertragsfassung auswählen oder neue Regel erstellen. Für Annahmen anschließend die Nachweise laden.')
  const [busy, setBusy] = useState(false)
  const [pending, setPending] = useState<{ action: ScreenActionDefinition; payload: Record<string, unknown> }>()
  const form = useUniversalFormState({ screen: schema.data, initialValues: {} })
  const acceptanceId = String(form.values.acceptance_id ?? '')
  const permissions = useQuery({ queryKey: ['harvest-control-permissions'],
    queryFn: async () => (await apiClient.get<{ allowed_actions: string[] }>(`${harvestControlBase}/permissions`)).data })
  const allowed = permissions.data?.allowed_actions ?? []
  const definition = useMemo(() => schema.data ? {
    ...schema.data, actions: schema.data.actions?.map(action => ({ ...action, disabled: busy || action.disabled })),
    dataSources: [...(schema.data.dataSources ?? []), ...(acceptanceId ? [{ key: 'audit',
      endpoint: `${harvestControlBase}/acceptances/${encodeURIComponent(acceptanceId)}/history`, pageSize: 25 }] : [])],
    tabs: [...(schema.data.tabs ?? []), ...(acceptanceId ? [{ key: 'audit', label: 'Nachweishistorie', tables: [{
      key: 'audit', label: 'Unveränderliche Nachweise', dataSourceKey: 'audit', serverPagination: true,
      pageSize: 25, virtualized: true, rowHeight: 44, columns: [
        { key: 'recorded_at', label: 'Zeitpunkt', width: 170 }, { key: 'action', label: 'Aktion', width: 180 },
        { key: 'actor', label: 'Urheber', width: 180 }, { key: 'calculation_hash', label: 'Geprüfte Fassung', width: 250 },
      ],
    }] }] : [])],
  } : undefined, [schema.data, busy, acceptanceId])
  const runtime = useUniversalMaskRuntime({ screenId: 'agrar/harvest-controls', entityId: acceptanceId || undefined,
    schema: definition, enabled: Boolean(definition), permissions: allowed })
  const actionRuntime = useHumanActionDispatch(schema.data?.actions ?? [], {
    screenId: 'agrar/harvest-controls', entityId: acceptanceId, permissions: allowed,
    entityData: { selected_rule: selected, control_context: context },
  })

  function selectRule(row: Record<string, unknown>): void {
    if (typeof row.id !== 'string' || !row.definition || typeof row.content_hash !== 'string') return
    const rule = row as unknown as Rule
    setSelected(rule)
    const keys = ['rule_id', 'customer_id', 'article_id', 'contract_id', 'valid_from', 'valid_until',
      'source_reference', 'measurement_method', 'measurement_method_version', 'impurities_free_pct', 'quality_limit_pct']
    form.resetForm({ ...form.values, ...Object.fromEntries(keys.map(key => [key, rule.definition[key] ?? ''])) })
    setFeedback('Ausgewählte Regelversion prüfen. Änderungen erzeugen eine neue Fassung; Genehmigung erfolgt durch eine zweite Person.')
  }

  async function reload(values = form.values): Promise<void> {
    const id = String(values.acceptance_id ?? '')
    if (id) {
      const loaded = (await apiClient.get<Context>(`${harvestControlBase}/acceptances/${encodeURIComponent(id)}/context`)).data
      setContext(loaded)
      const approval = loaded.calculation_approval
      const approved = loaded.calculation_current && approval && approval.calculation_hash === loaded.calculation_hash
        && new Date(approval.expires_at).getTime() > Date.now()
      const status = !['draft', 'provisional'].includes(loaded.release_status) ? `Festgeschrieben: ${loaded.release_status}`
        : loaded.issues.length ? loaded.issues.join(' ') : loaded.calculation_hash && !loaded.calculation_current ? 'Berechnung ist veraltet – neu berechnen.'
          : approved ? 'Konkrete Berechnungsfassung finanziell genehmigt.'
            : loaded.calculation_current ? 'Berechnet – finanzielle Gegenprüfung erforderlich.' : 'Regel und Messung bestätigt – bereit zur Berechnung.'
      form.resetForm({ ...values, control_status: status, calculation_hash: loaded.calculation_hash ?? '',
        net_amount: loaded.calculation_result?.total_net_amount_eur, vat_amount: loaded.calculation_result?.total_vat_amount_eur,
        gross_amount: loaded.calculation_result?.total_gross_amount_eur,
        quality_note: loaded.calculation_result?.warnings.join(' ') ?? 'Noch keine Berechnungsfassung vorhanden.' })
    }
    await runtime.refetch()
  }

  async function execute(action: ScreenActionDefinition, payload: Record<string, unknown>): Promise<void> {
    setPending(undefined); setBusy(true)
    try {
      const result = await actionRuntime.executeAction({ actionKey: action.key, mode: 'execute', payload,
        auditReason: typeof payload.reason === 'string' ? payload.reason : undefined,
        bindingSnapshot: JSON.stringify(action.commandBinding) })
      if (!result.success) { setFeedback(result.error ?? 'Vorgang gesperrt.'); return }
      if (action.key === 'create_rule' && result.data) selectRule(result.data)
      await reload()
      setFeedback(result.summary ?? 'Nachweis gespeichert.')
    } catch (failure) { setFeedback(getAxiosErrorMessage(failure)) }
    finally { setBusy(false) }
  }

  async function onAction(key: string): Promise<void> {
    if (busy) return
    if (key === 'refresh') {
      setBusy(true)
      try { await reload(); setFeedback('Aktueller Stand geladen. Auswahl und Nachweise vor Ausführung prüfen.') }
      catch (failure) { setContext(undefined); setFeedback(getAxiosErrorMessage(failure)) }
      finally { setBusy(false) }
      return
    }
    const action = schema.data?.actions?.find(item => item.key === key)
    if (!action || !allowed.includes(key)) { setFeedback('Für diese Aktion fehlt die Berechtigung.'); return }
    if (action.inputFields?.length) setPending({ action, payload: { ...form.values } })
    else await execute(action, { ...form.values })
  }

  if (schema.isLoading) return <p>Abrechnungssteuerung wird geladen…</p>
  if (schema.error || permissions.error || !runtime.plan) return <p role="alert">Abrechnungsmaske oder Berechtigungen konnten nicht geladen werden.</p>
  return <section data-testid="harvest-controls" aria-label="Vertragsregeln und Freigaben">
    <p role="status" className="p-3 text-sm">{feedback}</p>
    <p className="px-3 text-sm">Genehmigungen benötigen eine andere menschliche Einkaufs- beziehungsweise Finanzleitung. Die Regelqualität und finanzielle Fassung werden getrennt geprüft.</p>
    <UniversalMaskRenderer plan={runtime.plan} formState={form} hideFormSubmit allowedPermissions={allowed}
      lookupBindings={runtime.lookupBindings} tables={{ ...runtime.tableRows, positions: context?.calculation_result?.positions ?? [] }} tableTotals={runtime.tableTotals}
      tableQueryStates={runtime.tableQueryStates} onTableQueryChange={runtime.setTableQuery}
      messages={runtime.messages} onRowSelect={selectRule} onAction={key => onAction(key)} />
    {pending && <ActionInputDialog action={pending.action} open onCancel={() => setPending(undefined)}
      onSubmit={values => { void execute(pending.action, { ...pending.payload, ...values }) }} />}
  </section>
}

function SessionControls(): JSX.Element {
  const [client] = useState(() => new QueryClient({ defaultOptions: { queries: { retry: false } } }))
  return <QueryClientProvider client={client}><ControlMask /></QueryClientProvider>
}

export function HarvestControls(): JSX.Element {
  const { user } = useAuth()
  const token = auth.getAccessToken()
  let issuer = ''
  try { issuer = token ? jwtDecode<{ iss?: string }>(token).iss ?? '' : '' } catch { /* No token grants no data. */ }
  const identity = JSON.stringify([issuer, user?.sub, tenantFromToken(token), user?.roles])
  return <SessionControls key={identity} />
}
