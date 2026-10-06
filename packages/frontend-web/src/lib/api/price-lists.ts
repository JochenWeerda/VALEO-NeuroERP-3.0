import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type PriceListItem = {
  article_id: string
  article_number?: string | null
  unit_price: number
  min_quantity: number
  max_quantity?: number | null
  discount_percent: number
  valid_from?: string | null
  valid_until?: string | null
}

export type PriceList = {
  id: string
  tenant_id: string
  name: string
  description?: string | null
  currency: string
  price_list_type: string
  valid_from?: string | null
  valid_until?: string | null
  is_active: boolean
  item_count: number
  created_at?: string | null
  updated_at?: string | null
  items?: PriceListItem[]
}

export function usePriceLists() {
  return useQuery({
    queryKey: ['pricing', 'price-lists'],
    queryFn: async () => (await apiClient.get<PriceList[]>('/api/v1/price-lists')).data ?? [],
    initialData: [],
    // Sofort veraltet: Sonst gilt der Platzhalter als frisch geladen und
    // `staleTime` verhindert den Mount-Fetch (Nutzermeldung 17.07.2026).
    initialDataUpdatedAt: 0,
    staleTime: 2 * 60 * 1000,
  })
}
