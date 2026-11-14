import { expect, it } from 'vitest'
import { checkResourceAction, resourceActionResult } from '@/components/mask-builder/runtime/resource-response-adapter'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'
import type { ActionRequest, ActionRuntimeOptions } from '@/components/mask-builder/runtime/ActionRuntime'
import { getScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { User } from '@/lib/auth'
import definition from '../../fixtures/agrar-sorte-studio.json'

it('erlaubt ausschliesslich den menschlichen Sorten-PUT auf eine gueltige ID', () => {
  const action = { key: 'edit', method: 'PUT', commandEndpoint: '/api/v1/agrar/varieties/{entity_id}', responseAdapter: 'resource.v1', forbiddenForAgents: true } as ScreenActionDefinition
  const req = { actionKey: 'edit', mode: 'execute' } as ActionRequest
  const opts = { screenId: 'agrar/saatgut/sorte', entityId: 's1', isAgentCaller: false } as ActionRuntimeOptions
  expect(() => checkResourceAction(action, req, opts)).not.toThrow()
  expect(() => checkResourceAction(action, req, { ...opts, isAgentCaller: true })).toThrow()
  expect(() => checkResourceAction(action, { ...req, mode: 'dryRun' }, opts)).toThrow()
  expect(() => checkResourceAction(action, req, { ...opts, entityId: '../s1' })).toThrow()
  expect(() => checkResourceAction(action, req, { ...opts, screenId: 'agrar/andere' })).toThrow()
  expect(() => checkResourceAction({ ...action, method: 'DELETE' }, req, opts)).toThrow()
  expect(() => checkResourceAction({ ...action, forbiddenForAgents: false }, req, opts)).toThrow()
})

it.each(['.', '..'])('lehnt das Pfadsegment %s auch ohne Schraegstrich ab', entityId => {
  const action = { key: 'edit', method: 'PUT', commandEndpoint: '/api/v1/agrar/varieties/{entity_id}', responseAdapter: 'resource.v1', forbiddenForAgents: true } as ScreenActionDefinition
  const req = { actionKey: 'edit', mode: 'execute' } as ActionRequest
  const opts = { screenId: 'agrar/saatgut/sorte', entityId, isAgentCaller: false } as ActionRuntimeOptions
  expect(() => checkResourceAction(action, req, opts)).toThrow()
  expect(() => resourceActionResult(action, req, opts, { id: entityId })).toThrow()
})

it.each([
  ['AGRAR_BEARBEITEN', true], ['AGRAR_LESEN', false],
  ['FINANCE_ADMIN', false], ['manager', false],
] as const)('projiziert die echte Sorten-Schreibberechtigung fuer %s: %s', (role, allowed) => {
  const user = { id: 'synthetic', roles: [role], scopes: [] } as User
  const granted = getScreenPermissions(definition as unknown as ScreenDefinition, user)
  expect(granted.includes('agrar.sorte.update')).toBe(allowed)
  expect(getScreenPermissions(definition as unknown as ScreenDefinition, null)).toEqual([])
})
