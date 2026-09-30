import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

export const maskKeys = {
  all: ['masks'] as const,
  screenDefinition: (maskId: string) => [...maskKeys.all, 'screen-definition', maskId] as const,
}

export function useScreenDefinition(maskId: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: maskKeys.screenDefinition(maskId),
    queryFn: async () => {
      const encoded = maskId.replace(/\//g, '__')
      const response = await apiClient.get<ScreenDefinition>(
        `/api/v1/masks/${encoded}/screen-definition`,
        { timeout: 8_000 },
      )
      return response.data
    },
    enabled: Boolean(maskId) && (options?.enabled ?? true),
    staleTime: 10 * 60 * 1000,
    retry: 1,
    retryDelay: 800,
  })
}
