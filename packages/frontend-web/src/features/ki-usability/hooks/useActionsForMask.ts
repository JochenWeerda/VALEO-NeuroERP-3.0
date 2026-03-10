/**
 * Fetch actions for current domain/mask from ki-usability-api (optional)
 */

import { useQuery } from '@tanstack/react-query'
import { fetchActions } from '../api/actions'

export function useActionsForMask(domain?: string, mask?: string) {
  return useQuery({
    queryKey: ['ki-usability', 'actions', domain, mask],
    queryFn: async () => {
      try {
        return await fetchActions(domain, mask)
      } catch {
        return { actions: [], total: 0 }
      }
    },
    staleTime: 5 * 60 * 1000,
    enabled: Boolean(domain || mask),
    initialData: { actions: [], total: 0 },
  })
}
