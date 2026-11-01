import type { ScreenActionDefinition } from '../schema'

import type { ActionRequest, ActionResult, ActionRuntimeOptions } from './ActionRuntime'



/** Execute-only compatibility for fixed human REST handlers, never an agent command. */

const RESOURCE_ROUTES: Record<string, string[]> = {

  'crm/campaign-template': ['DELETE /api/v1/crm/campaigns/templates/{entity_id}', 'PUT /api/v1/crm/campaigns/templates/{entity_id}', 'POST /api/v1/crm/campaigns/templates/{entity_id}/duplicate'],

  'crm/campaign': ['DELETE /api/v1/crm/campaigns/{entity_id}', 'PUT /api/v1/crm/campaigns/{entity_id}', ...['activate','pause','resume','complete','archive','recipients'].map(key => `POST /api/v1/crm/campaigns/{entity_id}/${key}`)],

  'crm/consent': ['PUT /api/v1/crm/consents/{entity_id}', 'POST /api/v1/crm/consents/{entity_id}/revoke', 'POST /api/v1/crm/consents/{entity_id}/resend-confirmation'],

  'crm/gdpr-request': ['verify','reject','export','delete'].map(key => `POST /api/v1/gdpr/requests/{entity_id}/${key}`),

  'crm/segment': ['PUT /api/v1/crm/segments/{entity_id}', 'DELETE /api/v1/crm/segments/{entity_id}', 'POST /api/v1/crm/segments/{entity_id}/calculate', 'POST /api/v1/crm/segments/{entity_id}/members', 'POST /api/v1/crm/segments/{entity_id}/members/remove'],

}

export function checkResourceAction(action: ScreenActionDefinition, req: ActionRequest, opts: ActionRuntimeOptions): void {

  const route = `${action.method ?? 'POST'} ${action.commandEndpoint ?? ''}`

  if (action.responseAdapter !== 'resource.v1' || !opts.entityId || opts.entityId.length > 128 || /[\s/\\?#]/.test(opts.entityId) || opts.isAgentCaller || action.forbiddenForAgents !== true

    || req.mode !== 'execute' || !RESOURCE_ROUTES[opts.screenId]?.includes(route)) throw new Error('REST-Ressourcenaktion ist für diesen Aufruf gesperrt.')

}



export function resourceActionResult(action: ScreenActionDefinition, req: ActionRequest, opts: ActionRuntimeOptions, body: unknown, status?: number): ActionResult {
  const deletion = action.method === 'DELETE' && ['DELETE /api/v1/crm/campaigns/{entity_id}', 'DELETE /api/v1/crm/campaigns/templates/{entity_id}'].includes(`${action.method} ${action.commandEndpoint}`)
  if (deletion && status === 204 && (body == null || body === '') && opts.entityId && !/[\s/\\?#]/.test(opts.entityId) && opts.entityId.length <= 128) {
    return { actionKey: req.actionKey, mode: req.mode, success: true, resourceId: opts.entityId, affectedIds: [opts.entityId] }
  }
  if (deletion) throw new Error('Die Löschung wurde nicht eindeutig bestätigt.')

  const resource = body && typeof body === 'object' ? body as Record<string, unknown> : undefined

  const id = resource?.id

  const createsChild = action.method === 'POST' && (action.commandEndpoint?.endsWith('/duplicate') || action.commandEndpoint === '/api/v1/crm/campaigns/{entity_id}/recipients')

  if (typeof id !== 'string' || !id.trim() || id.length > 128 || /[\s/\\?#]/.test(id)

    || (createsChild ? id === opts.entityId : id !== opts.entityId)

    || action.commandEndpoint === '/api/v1/crm/campaigns/{entity_id}/recipients' && resource?.campaign_id !== opts.entityId) throw new Error('Die Serverantwort bestätigt die betroffene Ressource nicht.')

  return { actionKey: req.actionKey, mode: req.mode, success: true, resourceId: id, affectedIds: createsChild ? [opts.entityId!, id] : [id] }

}



export function prefillDeclaredInputs(action: ScreenActionDefinition, entity: Record<string, unknown>, payload: Record<string, unknown>): Record<string, unknown> {

  if (action.inputPrefill !== 'entity') return payload

  return Object.fromEntries((action.inputFields ?? []).map(field => [field.key, entity[field.key]]).filter(([, value]) => value !== undefined))

}



export function resourceActionPayload(action: ScreenActionDefinition, payload: Record<string, unknown>): Record<string, unknown> {

  return Object.fromEntries((action.inputFields ?? []).filter(field => Object.prototype.hasOwnProperty.call(payload, field.key)).map(field => [field.key, payload[field.key]]))

}
