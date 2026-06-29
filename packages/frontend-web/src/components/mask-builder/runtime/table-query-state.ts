import type { TableQueryState } from './types'

export function defaultTableQueryState(pageSize: number): TableQueryState {
  return { page: 1, pageSize }
}

export function toQueryParams(state: TableQueryState): Record<string, string> {
  const params: Record<string, string> = {
    page: String(state.page),
    limit: String(state.pageSize),
  }
  if (state.sort) {
    params['sort'] = state.sort
    params['sort_dir'] = state.sortDir ?? 'asc'
  }
  if (state.q) params['q'] = state.q
  if (state.filterPlan && Object.keys(state.filterPlan).length > 0) {
    params['filterPlan'] = JSON.stringify(state.filterPlan)
  }
  return params
}
