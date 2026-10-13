import type { ScreenActionDefinition } from '../schema'
import { actionIsEnabled } from '../governance/screen-context'
import type { ActionRequest, ActionResult, ActionRuntimeOptions } from './ActionRuntime'

const paths = {
  release: '/release', post: '/post', reverse: '/reverse', convert: '/convert',
  approval_request: '/approvals', approval_decide: '/approvals/{approval_id}/decision',
} as const
const fields = {
  release: [], post: ['posting_date'], reverse: ['reason'], convert: ['quantities_by_source_item_id'],
  approval_request: ['reason'], approval_decide: ['note'],
} as const

/** Transport adaptation, never domain logic or a grant of permission. */
export function prepareDocflowCommand(action: ScreenActionDefinition, req: ActionRequest,
  opts: ActionRuntimeOptions, idempotencyKey: string): { url: string; body: Record<string, unknown> } {
  const binding = action.commandBinding
  if (!binding || binding.adapter !== 'docflow.v1' || !Object.prototype.hasOwnProperty.call(paths, binding.command)) {
    throw new Error('DocFlow-Command-Adapter fehlt oder ist unbekannt.')
  }
  if (req.bindingSnapshot && req.bindingSnapshot !== JSON.stringify(binding)) throw new Error('Command-Metadaten haben sich geaendert. Bitte erneut pruefen.')
  if (opts.isAgentCaller) throw new Error('Schreibende DocFlow-Agentenaktionen sind nicht freigeschaltet.')
  const command = binding.command
  const entityId = opts.entityId
  if (!entityId || req.entityId && req.entityId !== entityId) throw new Error('Belegbindung fehlt oder widerspricht dem Aufruf.')
  const expectedEndpoint = `/api/v1/docflow/{entity_id}${paths[command]}`
  if (action.commandEndpoint !== expectedEndpoint || (action.method ?? 'POST') !== 'POST') {
    throw new Error('DocFlow-Endpoint widerspricht dem versionierten Kommando.')
  }
  const data = opts.entityData
  const available = Array.isArray(data?.aktionen) ? data.aktionen as Record<string, unknown>[] : []
  const serverAction = available.find(candidate => candidate.key === (binding.stateAction ?? action.key))
  if (!actionIsEnabled(action, data) || serverAction?.erlaubt !== true) {
    throw new Error('Diese Aktion ist im aktuellen Belegzustand gesperrt.')
  }
  if (req.mode !== 'execute' && (command !== 'convert' || !binding.preview || req.mode !== 'dryRun')) {
    throw new Error('Dieses DocFlow-Kommando bietet keine schreibfreie Vorschau.')
  }
  const version = req.expectedVersion ?? data?.version
  if (!Number.isInteger(version) || Number(version) < 1) throw new Error('Belegversion fehlt.')
  if (data?.version !== version) throw new Error('Belegversion hat sich geaendert. Bitte erneut pruefen.')
  const payload = req.payload ?? {}
  const allowed = fields[command] as readonly string[]
  if (Object.keys(payload).some(key => !allowed.includes(key))) {
    throw new Error('Unzulaessige Eingaben fuer das DocFlow-Kommando.')
  }
  const body: Record<string, unknown> = { ...payload }
  let url = expectedEndpoint.replace('{entity_id}', encodeURIComponent(entityId))
  if (command === 'approval_request') {
    const target = binding.defaults?.action
    if (target !== 'post' && target !== 'reverse') throw new Error('Freigabeaktion fehlt.')
    body.action = target
  } else if (command === 'approval_decide') {
    const approvalId = serverAction?.approval_id
    if (typeof approvalId !== 'string' || !approvalId || req.approvalId !== approvalId || typeof binding.defaults?.granted !== 'boolean' ||
      !['post', 'reverse'].includes(String(binding.defaults?.action))) {
      throw new Error('Konkrete Freigabebindung fehlt.')
    }
    url = url.replace('{approval_id}', encodeURIComponent(approvalId))
    body.granted = binding.defaults.granted
  } else {
    if (idempotencyKey.length < 8 || idempotencyKey.length > 120) throw new Error('Idempotenzschluessel fehlt oder ist ungueltig.')
    body.expected_version = version
    body.idempotency_key = idempotencyKey
    if (command === 'convert') {
      const target = binding.defaults?.target_doc_type
      if (typeof target !== 'string' || !target) throw new Error('Folgebelegart fehlt.')
      body.target_doc_type = target
      body.dry_run = req.mode === 'dryRun'
    }
    if (command === 'reverse') {
      const reason = req.auditReason ?? payload.reason
      if (typeof reason !== 'string' || reason.trim().length < 3 || reason.length > 300) throw new Error('Stornogrund fehlt oder ist ungueltig.')
      body.reason = reason.trim()
    }
  }
  return { url, body }
}

export function docflowCommandResult(action: ScreenActionDefinition, req: ActionRequest,
  opts: ActionRuntimeOptions, response: unknown): ActionResult {
  const data = response as Record<string, unknown> | null
  const command = action.commandBinding?.command
  const base = { actionKey: req.actionKey, mode: req.mode }
  if (command === 'approval_request' || command === 'approval_decide') {
    const status = command === 'approval_request' ? ['requested', 'granted'] :
      [action.commandBinding?.defaults?.granted ? 'granted' : 'denied']
    const sourceKey = action.commandBinding?.stateAction ?? action.key
    const serverActions = opts.entityData?.aktionen as Record<string, unknown>[] | undefined
    const approvalId = serverActions?.find(candidate => candidate.key === sourceKey)?.approval_id
    if (typeof data?.id !== 'string' || !status.includes(String(data.status)) ||
      data.action !== action.commandBinding?.defaults?.action || command === 'approval_decide' && data.id !== approvalId) {
      return { ...base, success: false, error: 'Freigabeantwort entspricht nicht dem Aufrufvertrag.' }
    }
    return { ...base, success: true, summary: command === 'approval_request' ? 'Freigabe angefragt.' :
      action.commandBinding?.defaults?.granted ? 'Freigabe erteilt.' : 'Freigabe abgelehnt.' }
  }
  const expectedStatus = req.mode === 'dryRun' ? 'dry_run' : 'ok'
  if (data?.command !== command || data?.status !== expectedStatus || data?.source_doc_id !== opts.entityId) {
    return { ...base, success: false, error: 'DocFlow-Antwort entspricht nicht dem Aufrufvertrag.' }
  }
  const payload = data.payload as Record<string, unknown> | undefined
  return { ...base, success: true, summary: req.mode === 'dryRun' ? 'Folgebeleg-Vorschau ohne Speicherung.' : 'Belegaktion abgeschlossen.',
    proposedChanges: req.mode === 'dryRun' ? [{ description: `${action.label} – Positionen: ${String(payload?.item_count ?? '')}` }] : undefined,
    affectedIds: [data.source_doc_id, data.target_doc_id, data.posting_id].filter((value): value is string => typeof value === 'string' && Boolean(value)) }
}

export function docflowErrorResult(req: ActionRequest, error: unknown): ActionResult {
  const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  const validationErrors = Array.isArray(detail) ? detail.map((item: { loc?: unknown[]; msg?: string }) => ({
    field: item.loc?.slice(1).join('.'), message: item.msg ?? 'Ungueltige Eingabe', severity: 'blocking' as const,
  })) : undefined
  return { actionKey: req.actionKey, mode: req.mode, success: false, validationErrors,
    error: typeof detail === 'string' ? detail : error instanceof Error ? error.message : 'DocFlow-Aufruf fehlgeschlagen.' }
}
