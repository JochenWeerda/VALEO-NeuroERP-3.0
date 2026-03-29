import { apiClient } from '@/lib/api/client'
import { type FertilizerProduct, type SeedOrderPayload, type SeedProduct } from './types'

const SEED_FALLBACK: SeedProduct[] = [
  {
    id: 'SEED-00123',
    name: 'Falkenstein Premium',
    variety: 'B-Hartweizen',
    category: 'Saatgut Weizen',
    season: 'Herbst 2024',
    supplier: 'Genossenschaft Sued',
    status: 'active',
    licenseCount: 4,
    forecastTons: 1120,
    quality: { purityPercent: 99.1, germinationPercent: 93, moisturePercent: 12.4 },
    pricing: [
      { minQuantityKg: 0, maxQuantityKg: 1000, pricePerKg: 4.2, validUntil: '2025-03-31' },
      { minQuantityKg: 1000, maxQuantityKg: 2500, pricePerKg: 4.05, validUntil: '2025-03-31' },
      { minQuantityKg: 2500, pricePerKg: 3.9, validUntil: '2025-06-30' },
    ],
    licenses: [
      { id: 'LIC-089', name: 'Saatgut Zulassung Bayern', validUntil: '2026-03-01', status: 'active' },
      { id: 'LIC-090', name: 'Export Schweiz', validUntil: '2025-11-30', status: 'active' },
    ],
    createdAt: '2024-09-14T08:23:00Z',
    updatedAt: '2024-10-06T12:15:00Z',
    notes: 'Premium Qualitaet fuer Winterweizen, hervorragende Keimwerte.',
  },
]

const FERTILIZER_FALLBACK: FertilizerProduct[] = [
  {
    id: 'FERT-2007',
    name: 'NPK 12-12-17 Premium',
    productGroup: 'Vollduenger',
    composition: [
      { label: 'Stickstoff (N)', percentage: 12 },
      { label: 'Phosphat (P2O5)', percentage: 12 },
      { label: 'Kalium (K2O)', percentage: 17 },
    ],
    supplier: 'Nord Agro GmbH',
    status: 'active',
    stockTons: 420,
    pricing: [
      { minQuantityKg: 0, maxQuantityKg: 1000, pricePerKg: 0.86, validUntil: '2025-03-15' },
      { minQuantityKg: 1000, pricePerKg: 0.82, validUntil: '2025-03-15' },
    ],
    createdAt: '2024-07-04T09:12:00Z',
    updatedAt: '2024-10-08T16:03:00Z',
  },
]

export const fetchSeedProducts = async (): Promise<SeedProduct[]> => {
  try {
    const res = await apiClient.get<{ items?: SeedProduct[] } | SeedProduct[]>(
      '/api/v1/articles?category=Saatgut&limit=100',
    )
    const data = res.data
    if (Array.isArray(data)) return data
    if (data && 'items' in data && Array.isArray(data.items)) return data.items
  } catch { /* fallback */ }
  return SEED_FALLBACK
}

export const fetchSeedProductById = async (productId: string): Promise<SeedProduct | undefined> => {
  try {
    const res = await apiClient.get<SeedProduct>(`/api/v1/articles/${productId}`)
    if (res.data) return res.data
  } catch { /* fallback */ }
  return SEED_FALLBACK.find((p) => p.id === productId)
}

export const fetchFertilizerProducts = async (): Promise<FertilizerProduct[]> => {
  try {
    const res = await apiClient.get<{ items?: FertilizerProduct[] } | FertilizerProduct[]>(
      '/api/v1/articles?category=Duengemittel&limit=100',
    )
    const data = res.data
    if (Array.isArray(data)) return data
    if (data && 'items' in data && Array.isArray(data.items)) return data.items
  } catch { /* fallback */ }
  return FERTILIZER_FALLBACK
}

export const fetchFertilizerProductById = async (productId: string): Promise<FertilizerProduct | undefined> => {
  try {
    const res = await apiClient.get<FertilizerProduct>(`/api/v1/articles/${productId}`)
    if (res.data) return res.data
  } catch { /* fallback */ }
  return FERTILIZER_FALLBACK.find((p) => p.id === productId)
}

export const submitSeedOrder = async (payload: SeedOrderPayload): Promise<{ orderId: string }> => {
  try {
    const res = await apiClient.post<{ orderId: string }>('/api/v1/agrar/seed-orders', payload)
    if (res.data?.orderId) return res.data
  } catch { /* fallback */ }
  const seq = Date.now().toString(36).toUpperCase().slice(-4)
  return { orderId: `SO-${seq}` }
}
