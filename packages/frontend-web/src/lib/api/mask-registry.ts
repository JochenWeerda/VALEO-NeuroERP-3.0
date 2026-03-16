import { apiClient } from '@/lib/api-client'

export type MaskClass = 'A' | 'B' | 'C'

export interface MaskRegistryEntry {
  mask_id: string
  route: string
  label: string
  domain: string
  mask_class: MaskClass
  process_key?: string | null
  explainability: string
  requires_approval_ui: boolean
  gobd_relevant: boolean
  wave1_contract: boolean
  notes?: string | null
  schema_version: number
}

export interface MaskRegistryResponse {
  masks: MaskRegistryEntry[]
  schema_version: number
}

export async function fetchMaskRegistry(): Promise<MaskRegistryResponse> {
  const response = await apiClient.get<MaskRegistryResponse>('/api/v1/ui/mask-registry')
  return response.data
}
