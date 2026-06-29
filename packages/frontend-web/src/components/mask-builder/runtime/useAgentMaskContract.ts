import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { AgentMaskContract, ScreenDefinition } from '../schema'
import { generateAgentMaskContract } from './generateAgentMaskContract'

/** Fetches the AgentMaskContract from the backend for a given mask ID. */
export function useAgentMaskContract(maskId: string | undefined, opts?: { enabled?: boolean }) {
  return useQuery<AgentMaskContract>({
    queryKey: ['agent-mask-contract', maskId],
    queryFn: async () => {
      const res = await apiClient.get<AgentMaskContract>(`/api/v1/masks/${maskId}/agent-contract`)
      return res.data
    },
    enabled: Boolean(maskId) && (opts?.enabled !== false),
    staleTime: 5 * 60 * 1000,
  })
}

/** Derives the AgentMaskContract locally from a ScreenDefinition (no network call). */
export function useLocalAgentMaskContract(
  screen: ScreenDefinition | undefined,
): AgentMaskContract | undefined {
  if (!screen) return undefined
  return generateAgentMaskContract(screen)
}
