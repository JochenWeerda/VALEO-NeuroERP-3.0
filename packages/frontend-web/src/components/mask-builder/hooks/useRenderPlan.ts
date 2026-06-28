import { useMemo } from 'react'
import type { ScreenDefinition } from '../schema'
import {
  compileRenderPlan,
  type CompileContext,
  type CompileSummaryContext,
} from '../render-plan'

export interface UseRenderPlanOptions {
  schema: ScreenDefinition | undefined
  summary?: CompileSummaryContext
  permissions?: string[]
  tenantId?: string
  roleHash?: string
  featureFlags?: Record<string, boolean>
  enabled?: boolean
}

export function useRenderPlan({
  schema,
  summary,
  permissions = [],
  tenantId,
  roleHash,
  featureFlags,
  enabled = true,
}: UseRenderPlanOptions) {
  return useMemo(() => {
    if (!enabled || !schema) return undefined

    const context: CompileContext = {
      screenId: schema.id,
      schemaVersion: schema.schemaVersion,
      summary: {
        ...summary,
        title: summary?.title ?? schema.title,
        subtitle: summary?.subtitle ?? schema.subtitle,
      },
      auth: {
        tenantId,
        roleHash,
        permissions: permissions.length > 0 ? permissions : schema.permissions ?? [],
      },
      featureFlags: { flags: featureFlags },
    }

    return compileRenderPlan(schema, context)
  }, [
    enabled,
    schema,
    summary,
    permissions,
    tenantId,
    roleHash,
    featureFlags,
  ])
}
