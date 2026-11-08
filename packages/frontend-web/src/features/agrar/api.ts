import { apiClient } from '@/lib/api/client'
import { type FertilizerProduct, type SeedProduct } from './types'

// Fehler gehen an die Abfrage (Fehlerzustand der Seite). Bis 20.10.2026 lieferten diese Abrufe bei jedem Fehler
// erfundene Produkte mit Bestand und Preisen, und eine gescheiterte Saatgutbestellung meldete eine erfundene
// Bestellnummer als Erfolg.

function liste<T>(data: { items?: T[] } | T[] | undefined): T[] {
  if (Array.isArray(data)) return data
  return Array.isArray(data?.items) ? data.items : []
}

export const fetchSeedProducts = async (): Promise<SeedProduct[]> =>
  liste((await apiClient.get<{ items?: SeedProduct[] } | SeedProduct[]>('/api/v1/articles/',
    { params: { category: 'Saatgut', limit: 100 } })).data)

export const fetchSeedProductById = async (productId: string): Promise<SeedProduct | undefined> =>
  (await apiClient.get<SeedProduct>(`/api/v1/articles/${productId}`)).data

export const fetchFertilizerProducts = async (): Promise<FertilizerProduct[]> =>
  liste((await apiClient.get<{ items?: FertilizerProduct[] } | FertilizerProduct[]>('/api/v1/articles/',
    { params: { category: 'Duengemittel', limit: 100 } })).data)

export const fetchFertilizerProductById = async (productId: string): Promise<FertilizerProduct | undefined> =>
  (await apiClient.get<FertilizerProduct>(`/api/v1/articles/${productId}`)).data
