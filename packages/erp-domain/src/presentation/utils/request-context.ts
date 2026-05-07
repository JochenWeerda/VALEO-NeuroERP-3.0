import { Request } from 'express'

const allowSystemActor =
  process.env.NODE_ENV === 'development' ||
  process.env.NODE_ENV === 'test' ||
  process.env.ERP_ALLOW_SYSTEM_ACTOR === '1'

/**
 * Authentifizierter Akteur für Audit und Schreiboperationen (ADR M-01).
 * In Production ohne ERP_ALLOW_SYSTEM_ACTOR: wirft bei fehlendem User.
 */
export function resolveActorId(req: Request): string {
  const id = req.user?.id
  if (id && String(id).trim()) {
    return String(id).trim()
  }
  if (allowSystemActor) {
    return 'system'
  }
  throw Object.assign(new Error('Unauthorized: authenticated user required'), { statusCode: 401 })
}

/** Optional: Lesenden Kontext ohne harten Fehler (z. B. legacy GET). */
export function resolveActorIdOptional(req: Request): string | undefined {
  const id = req.user?.id
  if (id && String(id).trim()) {
    return String(id).trim()
  }
  return allowSystemActor ? 'system' : undefined
}
