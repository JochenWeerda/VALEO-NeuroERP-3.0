import type { ScreenActionDefinition } from '../schema'
import type { ActionRequest, ActionResult, ActionRuntimeOptions } from './ActionRuntime'

/** Explicit compatibility for existing human REST edits, never an agent command. */
export function checkResourceAction(action: ScreenActionDefinition, req: ActionRequest, opts: ActionRuntimeOptions): void {
  const endpoint = action.commandEndpoint ?? ''
  const update = action.method === 'PUT' && endpoint === '/api/v1/crm/campaigns/templates/{entity_id}'
  const duplicate = action.method === 'POST' && endpoint === '/api/v1/crm/campaigns/templates/{entity_id}/duplicate'
  if (action.responseAdapter !== 'resource.v1' || opts.screenId !== 'crm/campaign-template' || !opts.entityId || opts.isAgentCaller || action.forbiddenForAgents !== true
    || req.mode !== 'execute' || (!update && !duplicate)) throw new Error('REST-Ressourcenaktion ist für diesen Aufruf gesperrt.')
}

export function resourceActionResult(action: ScreenActionDefinition, req: ActionRequest, opts: ActionRuntimeOptions, body: unknown): ActionResult {
  const id = body && typeof body === 'object' ? (body as Record<string, unknown>).id : undefined
  if (typeof id !== 'string' || !id.trim() || id.length > 128 || /[\s/\\?#]/.test(id)
    || (action.method === 'PUT' ? id !== opts.entityId : id === opts.entityId)) throw new Error('Die Serverantwort bestätigt die betroffene Ressource nicht.')
  return { actionKey: req.actionKey, mode: req.mode, success: true, resourceId: id, affectedIds: [id] }
}

export function prefillDeclaredInputs(action: ScreenActionDefinition, entity: Record<string, unknown>, payload: Record<string, unknown>): Record<string, unknown> {
  if (action.inputPrefill !== 'entity') return payload
  return Object.fromEntries((action.inputFields ?? []).map(field => [field.key, entity[field.key]]).filter(([, value]) => value !== undefined))
}

export function resourceActionPayload(action: ScreenActionDefinition, payload: Record<string, unknown>): Record<string, unknown> {
  if (action.method !== 'PUT') return {}
  return Object.fromEntries((action.inputFields ?? []).filter(field => Object.prototype.hasOwnProperty.call(payload, field.key)).map(field => [field.key, payload[field.key]]))
}
