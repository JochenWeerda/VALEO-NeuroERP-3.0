/**
 * Fetch actions for current domain/mask from ki-usability-api (optional)
 */

import { useQuery } from '@tanstack/react-query'
import { fetchActions } from '../api/actions'

export function useActionsForMask(domain?: string, mask?: string) {
  return useQuery({
    queryKey: ['ki-usability', 'actions', domain, mask],
    queryFn: () => fetchActions(domain, mask),
    staleTime: 5 * 60 * 1000,
    enabled: true,
  })
}
