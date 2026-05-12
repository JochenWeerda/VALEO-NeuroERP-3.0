import type { Request, Response } from 'express'
import { clampLimit, clampOffset } from '../types/api-pagination'

/** Query-Parameter `limit` / `offset` für Finanz-Stammdatenlisten (erp-domain List-Contract M-02/M-03). */
export function parseFinanzListQuery(req: Request): { limit: number; offset: number } {
  const limitRaw = req.query.limit !== undefined ? parseInt(String(req.query.limit), 10) : undefined
  const offsetRaw = req.query.offset !== undefined ? parseInt(String(req.query.offset), 10) : undefined
  return { limit: clampLimit(limitRaw), offset: clampOffset(offsetRaw) }
}

export function jsonFinanzList(
  res: Response,
  items: { toPrimitives(): object }[],
  total: number,
  limit: number,
  offset: number,
): void {
  res.json({
    success: true,
    data: items.map((e) => e.toPrimitives()),
    pagination: { total, limit, offset },
  })
}

export function jsonFinanzData(res: Response, entity: { toPrimitives(): object }, status = 200): void {
  res.status(status).json({ success: true, data: entity.toPrimitives() })
}

export function jsonFinanzError(res: Response, status: number, error: string): void {
  res.status(status).json({ success: false, error })
}
