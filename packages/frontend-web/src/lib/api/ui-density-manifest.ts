import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export interface UIDensityManifestEntry {
  page_domain: string
  aggregate_types: string[]
  command_names: string[]
  allowed_roles: string[]
  approval_roles: string[]
  approval_actor_types: string[]
  approval_statuses: string[]
  explainability_statuses: string[]
  policy_rule_ids: string[]
  source_contracts: string[]
  requires_human_confirmation: boolean
  requires_explainability: boolean
  restricted_command_count: number
  recommended_density: 'focused' | 'standard' | 'dense'
  schema_version: number
}

export interface UIDensityManifest {
  entries: UIDensityManifestEntry[]
  schema_version: number
}

export async function fetchUIDensityManifest(): Promise<UIDensityManifest> {
  const response = await apiClient.get<UIDensityManifest>('/api/v1/commands/ui-density-manifest')
  return response.data
}

export function useUIDensityManifest(pageDomain?: string) {
  return useQuery({
    queryKey: ['commands', 'ui-density-manifest'],
    queryFn: fetchUIDensityManifest,
    staleTime: 5 * 60 * 1000,
    select: (manifest) => ({
      manifest,
      entry:
        manifest.entries.find((candidate) => candidate.page_domain === (pageDomain ?? '').trim().toLowerCase()) ?? null,
    }),
    enabled: typeof pageDomain === 'string' && pageDomain.length > 0,
  })
}
