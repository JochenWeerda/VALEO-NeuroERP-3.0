import { useMemo } from 'react'
import {
  adaptMaskConfigToScreenDefinition,
  useRenderPlan,
  type ScreenDefinition,
  type ScreenSummaryItem,
  type ScreenTabDefinition,
} from '@/components/mask-builder'
import type { MaskConfig } from '@/components/mask-builder/types'

export interface PilotScreenSummaryAction {
  key: string
  label: string
  permission?: string
}

export interface PilotScreenSummaryLike {
  title?: string
  subtitle?: string
  available_tabs?: string[]
  actions?: PilotScreenSummaryAction[]
  performance?: {
    initial_payload_budget_kb?: number
    lookup_min_chars?: number
  }
}

export interface UsePilotRenderPlanOptions {
  screenId: string
  domain: ScreenDefinition['domain']
  maskConfig: MaskConfig
  entityId?: string
  summaryEndpointPrefix: string
  summary?: PilotScreenSummaryLike
  nativeScreen?: ScreenDefinition
  supplementalTabs?: ScreenTabDefinition[]
  enrichTabs?: (tabs: ScreenTabDefinition[]) => ScreenTabDefinition[]
  summaryItems?: ScreenSummaryItem[]
  permissions?: string[]
  tenantId?: string
  enabled?: boolean
}

export function usePilotRenderPlan({
  screenId,
  domain,
  maskConfig,
  entityId,
  summaryEndpointPrefix,
  summary,
  nativeScreen,
  supplementalTabs = [],
  enrichTabs,
  summaryItems = [],
  permissions = [],
  tenantId,
  enabled = true,
}: UsePilotRenderPlanOptions) {
  const schema = useMemo((): ScreenDefinition | undefined => {
    if (!enabled) return undefined

    const adapted = adaptMaskConfigToScreenDefinition(
      {
        ...maskConfig,
        title: summary?.title ?? maskConfig.title,
        subtitle: summary?.subtitle ?? maskConfig.subtitle,
      },
      {
        id: screenId,
        domain,
        summaryEndpoint: entityId ? `${summaryEndpointPrefix}/${entityId}/screen-summary` : undefined,
      },
    )

    const mergedNative: ScreenDefinition = nativeScreen
      ? {
          ...adapted,
          ...nativeScreen,
          adapter: nativeScreen.adapter,
          performance: nativeScreen.performance,
          layout: nativeScreen.layout,
          summaryEndpoint: nativeScreen.summaryEndpoint ?? adapted.summaryEndpoint,
          tabs: adapted.tabs,
          fields: adapted.fields,
        }
      : adapted

    const existingTabKeys = new Set((mergedNative.tabs ?? []).map((tab) => tab.key))
    const extraTabs = supplementalTabs.filter((tab) => {
      if (existingTabKeys.has(tab.key)) return false
      return !summary?.available_tabs || summary.available_tabs.includes(tab.key)
    })

    let tabs = [...(mergedNative.tabs ?? []), ...extraTabs]
    if (enrichTabs) {
      tabs = enrichTabs(tabs)
    }

    if (summary?.available_tabs?.length) {
      const allowed = new Set(summary.available_tabs)
      tabs = tabs.filter((tab) => allowed.has(tab.key))
    }

    return {
      ...mergedNative,
      tabs,
      actions:
        summary?.actions?.map((action) => ({
          key: action.key,
          label: action.label,
          kind: action.key === 'edit' ? ('primary' as const) : ('secondary' as const),
          permission: action.permission,
        })) ?? mergedNative.actions,
      performance: {
        ...mergedNative.performance,
        initialPayloadBudgetKb:
          summary?.performance?.initial_payload_budget_kb ??
          mergedNative.performance?.initialPayloadBudgetKb ??
          64,
        requiresLazyTabs: true,
        requiresVirtualTables: true,
        lookupMinChars: summary?.performance?.lookup_min_chars ?? 2,
      },
      layout: mergedNative.layout ?? {
        preferredMode: 'desktopDense',
        mobileMode: 'mobileStack',
        touchTargetPx: 44,
      },
    }
  }, [
    domain,
    enabled,
    enrichTabs,
    entityId,
    maskConfig,
    nativeScreen,
    screenId,
    summary,
    summaryEndpointPrefix,
    supplementalTabs,
  ])

  const resolvedPermissions = useMemo(() => {
    const fromSummary =
      summary?.actions?.flatMap((action) => (action.permission ? [action.permission] : [])) ?? []
    return permissions.length > 0 ? permissions : fromSummary
  }, [permissions, summary?.actions])

  const plan = useRenderPlan({
    schema,
    enabled: enabled && Boolean(schema),
    permissions: resolvedPermissions,
    tenantId,
    summary: {
      title: summary?.title,
      subtitle: summary?.subtitle,
      availableTabs: summary?.available_tabs,
      summaryItems,
    },
  })

  return { plan, schema }
}
