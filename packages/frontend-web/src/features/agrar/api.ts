import { type FertilizerProduct, type SeedOrderPayload, type SeedProduct } from './types'

const delay = async (ms = 120): Promise<void> =>
  new Promise((resolve) => {
    setTimeout(resolve, ms)
  })

const ORDER_NUMBER_MIN = 1_000
const ORDER_NUMBER_RANGE = 9_000

const SEED_PRODUCTS: SeedProduct[] = [
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
    quality: {
      purityPercent: 99.1,
      germinationPercent: 93,
      moisturePercent: 12.4,
    },
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
  {
    id: 'SEED-00442',
    name: 'Talblick Hybrid',
    variety: 'Mais Hybrid',
    category: 'Saatgut Mais',
    season: 'Fruehjahr 2025',
    supplier: 'Agro Westfalen',
    status: 'draft',
    licenseCount: 2,
    forecastTons: 860,
    quality: {
      purityPercent: 98.4,
      germinationPercent: 91,
      moisturePercent: 13.1,
    },
    pricing: [
      { minQuantityKg: 0, maxQuantityKg: 2000, pricePerKg: 5.1, validUntil: '2025-05-31' },
      { minQuantityKg: 2000, pricePerKg: 4.95, validUntil: '2025-05-31' },
    ],
    licenses: [
      { id: 'LIC-112', name: 'EU Hybrid Zulassung', validUntil: '2027-01-15', status: 'active' },
    ],
    createdAt: '2024-10-01T10:11:00Z',
    updatedAt: '2024-10-09T07:45:00Z',
  },
]

const FERTILIZER_PRODUCTS: FertilizerProduct[] = [
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
  {
    id: 'FERT-2019',
    name: 'Ammonsulfatsalpeter 27%',
    productGroup: 'Stickstoffduenger',
    composition: [
      { label: 'Stickstoff (N)', percentage: 27 },
      { label: 'Schwefel (S)', percentage: 4 },
    ],
    supplier: 'Chemie Rhein-Main',
    status: 'active',
    stockTons: 310,
    pricing: [
      { minQuantityKg: 0, maxQuantityKg: 1500, pricePerKg: 0.72, validUntil: '2025-02-28' },
      { minQuantityKg: 1500, pricePerKg: 0.69, validUntil: '2025-02-28' },
    ],
    createdAt: '2024-06-12T11:22:00Z',
    updatedAt: '2024-10-05T08:55:00Z',
  },
]

export const fetchSeedProducts = async (): Promise<SeedProduct[]> => {
  await delay()
  return SEED_PRODUCTS.map((product) => ({ ...product }))
}

export const fetchSeedProductById = async (productId: string): Promise<SeedProduct | undefined> => {
  await delay()
  return SEED_PRODUCTS.find((product) => product.id === productId)
}

export const fetchFertilizerProducts = async (): Promise<FertilizerProduct[]> => {
  await delay()
  return FERTILIZER_PRODUCTS.map((product) => ({ ...product }))
}

export const fetchFertilizerProductById = async (productId: string): Promise<FertilizerProduct | undefined> => {
  await delay()
  return FERTILIZER_PRODUCTS.find((product) => product.id === productId)
}

export const submitSeedOrder = async (payload: SeedOrderPayload): Promise<{ orderId: string }> => {
  await delay(180)
  const randomComponent = Math.floor(Math.random() * ORDER_NUMBER_RANGE + ORDER_NUMBER_MIN)
  const identifier = `SO-${randomComponent}`
  if (import.meta.env.DEV) {
    console.info('Seed order submitted', payload)
  }
  return { orderId: identifier }
}
