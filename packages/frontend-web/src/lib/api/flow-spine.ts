/**
 * Thin re-export layer kept for backward compatibility.
 * All hooks and types now live in flow-spines.ts.
 */
import { type UseQueryResult } from '@tanstack/react-query'
import {
  fetchFlowSpineCatalog,
  fetchFlowSpineWorkspace,
  useFlowSpineWorkspace,
  useFlowSpineCatalogHook,
  type FlowSpineCatalog,
  type FlowSpineWorkspace,
} from '@/lib/api/flow-spines'

export function useFlowSpineState(processKey: string): UseQueryResult<FlowSpineWorkspace> {
  return useFlowSpineWorkspace(processKey)
}

export function useFlowSpineCatalog(options?: { enabled?: boolean }): UseQueryResult<FlowSpineCatalog> {
  return useFlowSpineCatalogHook(options)
}

// Re-export the fetch helpers so existing consumers continue to work
export { fetchFlowSpineWorkspace, fetchFlowSpineCatalog }
export type { FlowSpineWorkspace, FlowSpineCatalog }
