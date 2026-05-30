/**
 * Poll GET /voice/status for admin ops (Slice-016)
 */

import { useQuery } from '@tanstack/react-query'
import { fetchVoiceStatus, type VoiceStatusResponse } from '../api/voice'

const VOICE_STATUS_QUERY_KEY = ['ki-usability', 'voice', 'status'] as const

export function useVoiceStackStatus(enabled = true): {
  status: VoiceStatusResponse | null | undefined
  loading: boolean
  error: boolean
  refetch: () => void
} {
  const query = useQuery({
    queryKey: VOICE_STATUS_QUERY_KEY,
    queryFn: async () => fetchVoiceStatus(),
    enabled,
    staleTime: 30_000,
    refetchInterval: 60_000,
  })

  return {
    status: query.data,
    loading: query.isLoading,
    error: query.isError,
    refetch: () => {
      void query.refetch()
    },
  }
}
