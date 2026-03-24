import { useQuery, type UseQueryResult } from '@tanstack/react-query'
import {
  fetchFlowSpineCatalog,
  fetchFlowSpineWorkspace,
  type FlowSpineCatalog,
  type FlowSpineWorkspace,
} from '@/lib/api/flow-spines'

export function useFlowSpineState(processKey: string): UseQueryResult<FlowSpineWorkspace> {
  return useQuery({
    queryKey: ['workflow', 'flow-spine', processKey],
    queryFn: () => fetchFlowSpineWorkspace(processKey),
    retry: false,
  })
}

export function useFlowSpineCatalog(): UseQueryResult<FlowSpineCatalog> {
  return useQuery({
    queryKey: ['workflow', 'flow-spine', 'catalog'],
    queryFn: () => fetchFlowSpineCatalog(),
    retry: false,
  })
}
