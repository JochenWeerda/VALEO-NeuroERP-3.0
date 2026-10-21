import type { TableBinding, TableQueryState } from './types'
import { toQueryParams } from './table-query-state'

/** Explicit client tables use the same bounded projector as CLI and MCP. */
export function tableSourceRequest(screenId: string, entityId: string | undefined, binding: TableBinding, state: TableQueryState): string | undefined {
  if (!binding.clientQuery || !binding.sourceKey) return undefined
  const params = new URLSearchParams({ ...toQueryParams(state), table_key: binding.tableKey })
  if (entityId) params.set('entity_id', entityId)
  return `/api/v1/masks/${encodeURIComponent(screenId)}/data/${encodeURIComponent(binding.sourceKey)}?${params}`
}
