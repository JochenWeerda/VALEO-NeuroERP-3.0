import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type HazardExportRow = {
  deliveryNumber?: string | null
  deliveryDate?: string | null
  supplierName?: string | null
  customerId?: string | null
  article?: string | null
  bvlZulassungsnummer?: string | null
  hazardHinweise?: string | null
  sdsReference?: string | null
  sachkundeStatus?: string | null
  sdsMitgeliefert?: string | null
  adrPunkte?: number
  compliant?: boolean
}

export type HazardExportResponse = {
  year?: number | null
  rows: HazardExportRow[]
  total: number
  generated_at: string
}

export type NutrientMonth = {
  deliveries: number
  n_kg: number
  p2o5_kg: number
}

export type NutrientExportResponse = {
  year: number
  deliveryCount: number
  totalNutrientNKg: number
  totalNutrientP2o5Kg: number
  byMonth: Record<string, NutrientMonth>
  generated_at: string
}

const EMPTY_HAZARD_EXPORT: HazardExportResponse = {
  year: null,
  rows: [],
  total: 0,
  generated_at: '',
}

const EMPTY_NUTRIENT_EXPORT: NutrientExportResponse = {
  year: 0,
  deliveryCount: 0,
  totalNutrientNKg: 0,
  totalNutrientP2o5Kg: 0,
  byMonth: {},
  generated_at: '',
}

export type LotTraceResponse = {
  lot?: {
    id: string
    lotId?: string | null
    article?: string | null
    articleId?: string | null
    quantity?: number
    location?: string | null
    status?: string | null
    qualityStatus?: string | null
    origin?: string | null
  }
  events?: Array<{ type: string; date?: string | null; note?: string | null }>
  linkedDeliveries?: Array<{
    deliveryNumber?: string | null
    deliveryDate?: string | null
    article?: string | null
    quantity?: number
    customerId?: string | null
  }>
  deliveryCount?: number
  generated_at?: string
  error?: string
  lot_id?: string
}

export function useGefahrstoffExport(year?: number): ReturnType<typeof useQuery<HazardExportResponse>> {
  return useQuery({
    queryKey: ['compliance', 'exports', 'gefahrstoffdoku', year ?? null],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (year) params.set('year', String(year))
      const path = params.size > 0 ? `/api/v1/compliance/exports/gefahrstoffdoku?${params.toString()}` : '/api/v1/compliance/exports/gefahrstoffdoku'
      return (await apiClient.get<HazardExportResponse>(path)).data
    },
    initialData: EMPTY_HAZARD_EXPORT,
    staleTime: 60 * 1000,
  })
}

export function useNaehrstoffExport(year: number): ReturnType<typeof useQuery<NutrientExportResponse>> {
  return useQuery({
    queryKey: ['compliance', 'exports', 'naehrstoffstrom', year],
    queryFn: async () => {
      return (await apiClient.get<NutrientExportResponse>(`/api/v1/compliance/exports/naehrstoffstrom?year=${encodeURIComponent(String(year))}`)).data
    },
    enabled: Number.isInteger(year) && year >= 2000 && year <= 2100,
    initialData: EMPTY_NUTRIENT_EXPORT,
    staleTime: 60 * 1000,
  })
}

export async function fetchLotTrace(lotId: string): Promise<LotTraceResponse> {
  const id = lotId.trim()
  if (!id) {
    throw new Error('lot_id ist erforderlich')
  }
  return (await apiClient.get<LotTraceResponse>(`/api/v1/compliance/exports/chargen-trace/${encodeURIComponent(id)}`)).data
}

export async function downloadComplianceCsv(kind: 'gefahrstoffdoku' | 'naehrstoffstrom', year?: number): Promise<void> {
  const params = new URLSearchParams()
  if (year) params.set('year', String(year))
  const endpoint = kind === 'gefahrstoffdoku' ? 'gefahrstoffdoku.csv' : 'naehrstoffstrom.csv'
  const query = params.size > 0 ? `?${params.toString()}` : ''
  const response = await apiClient.get<Blob>(`/api/v1/compliance/exports/${endpoint}${query}`, {
    responseType: 'blob',
  })
  const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = kind === 'gefahrstoffdoku'
    ? (year ? `gefahrstoffdoku-${year}.csv` : 'gefahrstoffdoku.csv')
    : `naehrstoffstrom-${year ?? 'export'}.csv`
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  URL.revokeObjectURL(url)
}
