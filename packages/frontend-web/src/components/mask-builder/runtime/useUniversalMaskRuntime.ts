import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueries, useQueryClient } from '@tanstack/react-query'
import type { ScreenDefinition, ScreenSummaryItem } from '../schema'
import type { RenderPlan } from '../render-plan/types'
import { compileRenderPlan } from '../render-plan/schema-compiler'
import { applyOverlay, hashOverlay, type ScreenOverlay } from '../render-plan/overlay'
import type { DataBindingPlan, LookupBinding, TableQueryState } from './types'
import { compileDataBindingPlan } from './compile-data-binding-plan'
import { defaultTableQueryState, toQueryParams } from './table-query-state'
import { appendQueryParams } from './data-source-resolver'
import { apiClient } from '@/lib/api-client'
import { deleteUserOverlay, overlayKeys, saveUserOverlay, useUserScreenOverlay } from '@/lib/api/ux-overlays'

export interface UseUniversalMaskRuntimeOptions {
  screenId: string
  entityId?: string
  schema: ScreenDefinition | undefined
  tabEndpoints?: Record<string, string>
  availableTabs?: string[]
  summaryTitle?: string
  summarySubtitle?: string
  summaryItems?: ScreenSummaryItem[]
  permissions?: string[]
  tenantId?: string
  enabled?: boolean
}

export interface UseUniversalMaskRuntimeResult {
  plan: RenderPlan | undefined
  binding: DataBindingPlan | undefined
  entityData: Record<string, unknown>
  tableRows: Record<string, Record<string, unknown>[]>
  tableTotals: Record<string, number>
  tableQueryStates: Record<string, TableQueryState>
  setTableQuery: (tableKey: string, patch: Partial<TableQueryState>) => void
  userOverlay: ScreenOverlay
  overlayInvalidPaths: string[]
  updateUserOverlay: (patch: ScreenOverlay) => Promise<void>
  resetUserOverlay: () => Promise<void>
  lookupBindings: Record<string, LookupBinding>
  isEntityLoading: boolean
  isOverlayLoading: boolean
  entityError: unknown
  refetch: () => Promise<void>
}

function hasContentChange(patch: Partial<TableQueryState>): boolean {
  return patch.sort !== undefined || patch.q !== undefined || patch.filterPlan !== undefined
}

function mergeOverlay(current: ScreenOverlay, patch: ScreenOverlay): ScreenOverlay {
  return {
    ...current,
    ...patch,
    tables: patch.tables
      ? Object.entries(patch.tables).reduce<Record<string, NonNullable<ScreenOverlay['tables']>[string]>>(
        (acc, [tableKey, tablePatch]) => {
          acc[tableKey] = {
            ...(current.tables?.[tableKey] ?? {}),
            ...tablePatch,
          }
          return acc
        },
        { ...(current.tables ?? {}) },
      )
      : current.tables,
  }
}

export function useUniversalMaskRuntime({
  screenId,
  entityId,
  schema,
  tabEndpoints,
  availableTabs,
  summaryTitle,
  summarySubtitle,
  summaryItems,
  permissions = [],
  tenantId,
  enabled = true,
}: UseUniversalMaskRuntimeOptions): UseUniversalMaskRuntimeResult {
  const queryClient = useQueryClient()
  const overlayQuery = useUserScreenOverlay(screenId, { enabled: enabled && Boolean(schema) })
  const activeOverlay = overlayQuery.data?.overlay ?? {}

  const plan = useMemo<RenderPlan | undefined>(() => {
    if (!schema || !enabled) return undefined
    const compiled = compileRenderPlan(schema, {
      screenId,
      schemaVersion: schema.schemaVersion ?? 1,
      summary: {
        title: summaryTitle,
        subtitle: summarySubtitle,
        availableTabs,
        summaryItems,
        tabEndpoints,
      },
      auth: { permissions },
    })
    const applied = applyOverlay(compiled, activeOverlay)
    return {
      ...applied.plan,
      cacheKey: `${compiled.cacheKey}:overlay:${overlayQuery.data?.schema_version ?? schema.schemaVersion ?? 1}:${hashOverlay(activeOverlay)}`,
      overlayInvalidPaths: applied.invalidPaths.length > 0 ? applied.invalidPaths : applied.plan.overlayInvalidPaths,
    }
  }, [schema, screenId, enabled, summaryTitle, summarySubtitle, availableTabs, summaryItems, tabEndpoints, permissions, activeOverlay, overlayQuery.data?.schema_version])

  const saveOverlayMutation = useMutation({
    mutationFn: (overlay: ScreenOverlay) => saveUserOverlay(screenId, {
      schema_version: schema?.schemaVersion ?? 1,
      overlay,
    }),
    onSuccess: (data) => {
      queryClient.setQueryData(overlayKeys.screen(screenId), data)
    },
  })

  const resetOverlayMutation = useMutation({
    mutationFn: () => deleteUserOverlay(screenId),
    onSuccess: () => {
      queryClient.setQueryData(overlayKeys.screen(screenId), {
        screen_id: screenId,
        schema_version: schema?.schemaVersion ?? 1,
        overlay: {},
        updated_at: null,
      })
    },
  })

  async function updateUserOverlay(patch: ScreenOverlay): Promise<void> {
    await saveOverlayMutation.mutateAsync(mergeOverlay(activeOverlay, patch))
  }

  async function resetUserOverlay(): Promise<void> {
    await resetOverlayMutation.mutateAsync()
  }

  const binding = useMemo<DataBindingPlan | undefined>(() => {
    if (!plan) return undefined
    return compileDataBindingPlan(plan, schema?.dataSources, tabEndpoints, entityId, tenantId)
  }, [plan, schema?.dataSources, tabEndpoints, entityId, tenantId])

  // Per-table query states
  const [tableQueryStates, setTableQueryStates] = useState<Record<string, TableQueryState>>({})

  const resolvedTableQueryStates = useMemo<Record<string, TableQueryState>>(() => {
    if (!binding) return {}
    const result: Record<string, TableQueryState> = {}
    for (const [tableKey, tb] of Object.entries(binding.tableBindings)) {
      const pageSize = plan?.tablesByKey[tableKey]?.pageSize ?? 25
      result[tableKey] = tableQueryStates[tableKey] ?? defaultTableQueryState(pageSize)
      if (tb.requiresServerQuery) {
        // ensure pageSize reflects plan
        result[tableKey] = { ...result[tableKey], pageSize }
      }
    }
    return result
  }, [binding, plan, tableQueryStates])

  function setTableQuery(tableKey: string, patch: Partial<TableQueryState>): void {
    setTableQueryStates((prev) => {
      const pageSize = plan?.tablesByKey[tableKey]?.pageSize ?? 25
      const current = prev[tableKey] ?? defaultTableQueryState(pageSize)
      return {
        ...prev,
        [tableKey]: {
          ...current,
          ...patch,
          page: patch.page ?? (hasContentChange(patch) ? 1 : current.page),
        },
      }
    })
  }

  // Entity query
  const entityQuery = useQuery({
    queryKey: [screenId, entityId, 'entity'],
    queryFn: async () => {
      const ep = binding?.entityBinding.entityEndpoint
      if (!ep) return {}
      const res = await apiClient.get<Record<string, unknown>>(ep)
      return res.data
    },
    enabled: enabled && Boolean(binding?.entityBinding.entityEndpoint),
  })

  // Table queries — one per tableKey that has requiresServerQuery
  const tableEntries = useMemo(
    () => Object.entries(binding?.tableBindings ?? {}).filter(([, tb]) => tb.requiresServerQuery),
    [binding],
  )

  const tableResults = useQueries({
    queries: tableEntries.map(([tableKey, tb]) => ({
      queryKey: [screenId, entityId, 'table', tableKey, resolvedTableQueryStates[tableKey]],
      queryFn: async () => {
        const params = toQueryParams(resolvedTableQueryStates[tableKey] ?? defaultTableQueryState(25))
        const url = appendQueryParams(tb.endpoint, params)
        const res = await apiClient.get<{ items?: Record<string, unknown>[]; total?: number } | Record<string, unknown>[]>(url)
        return res.data
      },
      enabled: enabled && Boolean(tb.endpoint),
      staleTime: tb.staleTimeMs ?? 30_000,
    })),
  })

  const tableRows = useMemo<Record<string, Record<string, unknown>[]>>(() => {
    const result: Record<string, Record<string, unknown>[]> = {}
    tableEntries.forEach(([tableKey], i) => {
      const data = tableResults[i]?.data
      if (!data) return
      if (Array.isArray(data)) {
        result[tableKey] = data as Record<string, unknown>[]
      } else if (Array.isArray((data as { items?: unknown }).items)) {
        result[tableKey] = (data as { items: Record<string, unknown>[] }).items
      }
    })
    return result
  }, [tableEntries, tableResults])

  const tableTotals = useMemo<Record<string, number>>(() => {
    const result: Record<string, number> = {}
    tableEntries.forEach(([tableKey], i) => {
      const data = tableResults[i]?.data
      if (data && !Array.isArray(data) && typeof (data as { total?: unknown }).total === 'number') {
        result[tableKey] = (data as { total: number }).total
      }
    })
    return result
  }, [tableEntries, tableResults])

  return {
    plan,
    binding,
    entityData: (entityQuery.data as Record<string, unknown>) ?? {},
    tableRows,
    tableTotals,
    tableQueryStates: resolvedTableQueryStates,
    setTableQuery,
    userOverlay: activeOverlay,
    overlayInvalidPaths: plan?.overlayInvalidPaths ?? [],
    updateUserOverlay,
    resetUserOverlay,
    lookupBindings: binding?.lookupBindings ?? {},
    isEntityLoading: entityQuery.isLoading,
    isOverlayLoading: overlayQuery.isLoading,
    entityError: entityQuery.error,
    refetch: async () => {
      await Promise.all([
        entityQuery.refetch(),
        overlayQuery.refetch(),
        ...tableResults.map((result) => result.refetch()),
      ])
    },
  }
}
