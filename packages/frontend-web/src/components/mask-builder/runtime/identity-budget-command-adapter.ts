/** Project native form input onto the existing strict quota command contract.
 * Session/entity context must never become command input or caller identity.
 */
export function identityBudgetInput(endpoint: string, payload: Record<string, unknown>): Record<string, unknown> {
  if (!/^\/api\/v1\/identity\/budgets\/actions\/(root|allocate)$/.test(endpoint)) return payload
  const fields = endpoint.endsWith('/root') ? ['tokens', 'max_children']
    : ['tokens', 'max_children', 'parent', 'owner', 'kind', 'request_id']
  return Object.fromEntries(fields.filter(key => payload[key] !== undefined).map(key => [key, payload[key]]))
}
