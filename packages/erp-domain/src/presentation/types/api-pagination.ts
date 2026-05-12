/**
 * Standard-Listen-Contract (erp-domain, Meilensteine M-02/M-03).
 *
 * Erfolgs-Body der paginierten GET-Listen:
 * `{ success: true, data: T[], pagination: { total, limit, offset } }`
 *
 * - `total`: COUNT(*) mit **denselben** Filtern wie die Liste (ohne LIMIT/OFFSET).
 * - `limit` / `offset`: nach {@link clampLimit} / {@link clampOffset}
 *   (Defaults gemäß {@link DEFAULT_LIST_LIMIT}, Cap {@link MAX_LIST_LIMIT}).
 */
export const DEFAULT_LIST_LIMIT = 50
export const MAX_LIST_LIMIT = 500

export function clampLimit(limit?: number): number {
  const raw = limit ?? DEFAULT_LIST_LIMIT
  if (!Number.isFinite(raw) || raw <= 0) {
    return DEFAULT_LIST_LIMIT
  }
  return Math.min(Math.floor(raw), MAX_LIST_LIMIT)
}

export function clampOffset(offset?: number): number {
  const raw = offset ?? 0
  if (!Number.isFinite(raw) || raw < 0) {
    return 0
  }
  return Math.floor(raw)
}

export interface PaginationMeta {
  total: number
  limit: number
  offset: number
}

export interface ListResult<T> {
  items: T[]
  total: number
}
