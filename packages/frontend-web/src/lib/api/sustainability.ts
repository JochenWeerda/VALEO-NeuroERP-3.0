import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type SustainabilityProviders = {
  providers: {
    bvl_psm: { configured: boolean; base_url: string; cache_ttl_seconds: number }
    climatiq: { configured: boolean; base_url: string }
    faostat: { configured: boolean; base_url: string }
  }
}

export type SustainabilityPsmResponse = {
  source: string
  tenant_id: string
  zulassungsnummer: string
  item: Record<string, unknown>
}

export function useSustainabilityProviders() {
  return useQuery({
    queryKey: ['sustainability', 'providers'],
    queryFn: async () => (await apiClient.get<SustainabilityProviders>('/api/v1/sustainability/providers/status')).data,
    staleTime: 5 * 60 * 1000,
  })
}

export function useSustainabilityPsm(zulassungsnummer: string | null, tenantId = 'system') {
  return useQuery({
    queryKey: ['sustainability', 'psm', zulassungsnummer, tenantId],
    queryFn: async () => (
      await apiClient.get<SustainabilityPsmResponse>(
        `/api/v1/sustainability/psm/${encodeURIComponent(zulassungsnummer ?? '')}?tenant_id=${encodeURIComponent(tenantId)}`
      )
    ).data,
    enabled: Boolean(zulassungsnummer),
    staleTime: 30 * 60 * 1000,
  })
}
