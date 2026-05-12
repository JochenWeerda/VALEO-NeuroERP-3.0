import { Request, Response } from 'express'

const allowSystemActor =
  process.env.NODE_ENV === 'development' ||
  process.env.NODE_ENV === 'test' ||
  process.env.ERP_ALLOW_SYSTEM_ACTOR === '1'

const allowImplicitDevTenant =
  process.env.NODE_ENV === 'development' ||
  process.env.NODE_ENV === 'test' ||
  process.env.ERP_ALLOW_MISSING_TENANT === '1'

function extractStatusCode(error: unknown): number | undefined {
  if (error === null || typeof error !== 'object' || !('statusCode' in error)) {
    return undefined
  }
  const raw = (error as { statusCode?: unknown }).statusCode
  const status = typeof raw === 'number' ? raw : Number(raw)
  if (Number.isFinite(status) && status >= 400 && status < 600) {
    return status
  }
  return undefined
}

/** True, wenn `error` einen nutzbaren HTTP-`statusCode` trägt (resolveTenantId, resolveActorId, …). */
export function errorHasStatusCode(error: unknown): boolean {
  return extractStatusCode(error) !== undefined
}

/**
 * Mandanten-ID (ADR M-01): zuerst Header `x-tenant-id`, sonst `req.user.tenantId`.
 * Produktion: fehlend → 400 „Missing tenant“.
 * Dev/Test oder ERP_ALLOW_MISSING_TENANT: Fallback ERP_DEV_TENANT_ID oder `dev-tenant`.
 */
export function resolveTenantId(req: Request): string {
  const rawHeader = req.headers['x-tenant-id']
  const headerVal = Array.isArray(rawHeader) ? rawHeader[0] : rawHeader
  const fromHeader = typeof headerVal === 'string' ? headerVal.trim() : ''
  if (fromHeader.length > 0) {
    return fromHeader
  }
  const uid = req.user?.tenantId
  const fromUser = uid !== undefined && uid !== null ? String(uid).trim() : ''
  if (fromUser.length > 0) {
    return fromUser
  }
  if (allowImplicitDevTenant) {
    const envTenant = process.env.ERP_DEV_TENANT_ID?.trim()
    if (envTenant) {
      return envTenant
    }
    return 'dev-tenant'
  }
  throw Object.assign(new Error('Missing tenant'), { statusCode: 400 })
}

/**
 * Fehler-Antwort mit optionalem `statusCode` auf dem geworfenen Fehler (M-04),
 * sonst `fallbackStatus` (Listen oft 500, Validierung oft 400).
 */
export function respondControllerError(res: Response, error: unknown, fallbackStatus: number): void {
  const status = extractStatusCode(error)
  if (status !== undefined) {
    res.status(status).json({
      success: false,
      error: error instanceof Error ? error.message : 'Fehler',
    })
    return
  }
  if (fallbackStatus >= 500) {
    res.status(fallbackStatus).json({
      success: false,
      error: 'Interner Serverfehler',
    })
    return
  }
  res.status(fallbackStatus).json({
    success: false,
    error: error instanceof Error ? error.message : 'Unbekannter Fehler',
  })
}

/** Domain-Fehler in Schreib-Endpunkten: zuerst HTTP-statusCode vom Kontext, sonst „nicht gefunden“→404 sonst 400. */
export function respondDomainMutationError(res: Response, error: unknown): void {
  if (errorHasStatusCode(error)) {
    respondControllerError(res, error, 400)
    return
  }
  const status = error instanceof Error && error.message.includes('nicht gefunden') ? 404 : 400
  res.status(status).json({
    success: false,
    error: error instanceof Error ? error.message : 'Unbekannter Fehler',
  })
}

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
