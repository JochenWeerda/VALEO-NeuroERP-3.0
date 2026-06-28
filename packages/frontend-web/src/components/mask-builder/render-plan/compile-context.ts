import type { ScreenSummaryItem } from '../schema'

export interface CompileSummaryContext {
  title?: string
  subtitle?: string
  availableTabs?: string[]
  summaryItems?: ScreenSummaryItem[]
  tabEndpoints?: Record<string, string>
}

export interface CompileAuthContext {
  tenantId?: string
  roleHash?: string
  permissions: string[]
}

export interface CompileFeatureFlags {
  flags?: Record<string, boolean>
}

export interface CompileContext {
  screenId: string
  schemaVersion: number
  summary?: CompileSummaryContext
  auth: CompileAuthContext
  featureFlags?: CompileFeatureFlags
}

export function buildPermissionHash(permissions: string[]): string {
  return [...permissions].sort().join('|')
}

export function buildFeatureFlagHash(flags: Record<string, boolean> | undefined): string {
  if (!flags || Object.keys(flags).length === 0) return '_'
  return Object.entries(flags)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => `${key}=${value ? '1' : '0'}`)
    .join('|')
}

export function buildRenderPlanCacheKey(context: CompileContext): string {
  const parts = [
    context.screenId,
    String(context.schemaVersion),
    context.auth.tenantId ?? '_',
    context.auth.roleHash ?? '_',
    buildPermissionHash(context.auth.permissions),
    buildFeatureFlagHash(context.featureFlags?.flags),
  ]
  return parts.join('::')
}
