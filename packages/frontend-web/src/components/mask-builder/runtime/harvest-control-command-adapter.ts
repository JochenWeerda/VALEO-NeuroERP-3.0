import type { ScreenActionDefinition } from '../schema'
import type { ActionRequest, ActionResult, ActionRuntimeOptions } from './ActionRuntime'
import contract from './harvest-control-contract.generated.json'

const base = '/api/v1/agrar/harvest-acceptance'
const control = `${base}/settlement-controls`
export const harvestControlBase = control
const paths = contract.paths

function record(value: unknown): Record<string, unknown> {
  return value != null && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {}
}
function required(value: unknown, label: string): string {
  if (value == null || !String(value).trim()) throw new Error(`${label} fehlt. Bitte Auswahl oder Eingabe ergänzen.`)
  return String(value)
}
function expiry(value: unknown): string {
  const date = new Date(required(value, 'Genehmigungsfrist'))
  if (Number.isNaN(date.getTime())) throw new Error('Genehmigungsfrist ist ungültig.')
  return date.toISOString()
}

/** Exact transport mapping. Neither field values nor UI visibility grant approval. */
export function prepareHarvestControl(action: ScreenActionDefinition, req: ActionRequest,
  opts: ActionRuntimeOptions, idempotencyKey: string): { url: string; body: Record<string, unknown> } {
  const binding = action.commandBinding
  if (binding?.adapter !== 'harvest.control.v1' || !Object.prototype.hasOwnProperty.call(paths, binding.command)) {
    throw new Error('Unbekannter Ernte-Commandvertrag.')
  }
  if (req.mode !== 'execute' || opts.isAgentCaller) throw new Error('Dieser Schreibweg ist nur für die menschliche Bedienung freigeschaltet.')
  if (req.bindingSnapshot && req.bindingSnapshot !== JSON.stringify(binding)) throw new Error('Commandvertrag wurde geändert. Bitte erneut prüfen.')
  const command = binding.command
  if (action.commandEndpoint !== paths[command] || action.method !== 'POST') throw new Error('Endpunkt widerspricht dem Ernte-Commandvertrag.')
  const payload = req.payload ?? {}
  if (action.requiresConfirmation && payload.confirm_execution !== 'confirm') throw new Error('Ausführung wurde nicht bestätigt.')
  const selected = record(opts.entityData?.selected_rule)
  const definition = record(selected.definition)
  const context = record(opts.entityData?.control_context)
  const state = record(context.state)
  const acceptance = record(state.acceptance)
  const body: Record<string, unknown> = { idempotency_key: idempotencyKey }
  let url: string = paths[command]
  if (command === 'create_rule') {
    const name = required(payload.rule_id, 'Regelbezeichnung')
    body.rule_id = name
    body.expected_version = definition.rule_id === name ? definition.rule_version : 0
    const keys = ['customer_id', 'article_id', 'valid_from', 'valid_until', 'source_reference',
      'measurement_method', 'measurement_method_version', 'impurities_free_pct']
    body.terms = Object.fromEntries(keys.map(key => [key, required(payload[key], 'Vertragsangabe')]))
    Object.assign(body.terms as object, { contract_id: payload.contract_id || null,
      quality_limit_pct: payload.quality_limit_pct === '' || payload.quality_limit_pct == null ? null : payload.quality_limit_pct })
  } else if (command === 'approve_rule' || command === 'revoke_rule') {
    url = url.replace('{version_id}', encodeURIComponent(required(selected.id, 'Ausgewählte Regelversion')))
    body.expected_hash = required(selected.content_hash, 'Regelprüfung')
    body.reason = required(req.auditReason ?? payload.reason, 'Prüfvermerk')
    if (command === 'approve_rule') body.expires_at = expiry(payload.expires_at)
  } else {
    const id = required(opts.entityId, 'Annahme')
    if (acceptance.id !== id || payload.acceptance_id !== id) throw new Error('Annahme wurde geändert. Bitte Annahme und Nachweise neu laden.')
    url = url.replace('{acceptance_id}', encodeURIComponent(id))
    if (command === 'bind_rule' || command === 'attest' || command === 'calculate') {
      body.expected_context_hash = required(context.context_hash, 'Geladener Eingabestand')
    }
    if (command === 'bind_rule') body.rule_version_id = required(selected.id, 'Ausgewählte Regelversion')
    if (command === 'attest') {
      body.protocol_id = required(record(state.protocol).id, 'Messprotokoll der Annahme')
      body.expected_protocol_hash = required(context.protocol_hash, 'Messprotokollstand')
      body.measurement_method = required(payload.measurement_method, 'Untersuchungsmethode')
      body.measurement_method_version = required(payload.measurement_method_version, 'Methodenfassung')
      body.source_reference = required(payload.measurement_source, 'Messbericht / Nachweisquelle')
    }
    if (command === 'approve_calculation' || command === 'release') {
      body.expected_calculation_hash = required(context.calculation_hash, 'Geprüfte Berechnungsfassung')
    }
    if (command === 'approve_calculation') {
      body.reason = required(req.auditReason ?? payload.reason, 'Prüfvermerk')
      body.expires_at = expiry(payload.expires_at)
      body.acknowledge_quality_exception = payload.acknowledge_quality_exception === true
    }
  }
  return { url, body }
}

export function harvestControlResult(req: ActionRequest, response: unknown): ActionResult {
  const data = record(response)
  if (!data.id && !data.control_event_id && !data.acceptance_number) {
    return { actionKey: req.actionKey, mode: req.mode, success: false, error: 'Nachweisantwort ist unvollständig.' }
  }
  return { actionKey: req.actionKey, mode: req.mode, success: true, data,
    summary: 'Vorgang mit unveränderlichem Nachweis gespeichert.' }
}
