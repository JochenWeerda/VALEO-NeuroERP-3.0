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

const EMPTY_SUSTAINABILITY_PROVIDERS: SustainabilityProviders = {
  providers: {
    bvl_psm: { configured: false, base_url: '', cache_ttl_seconds: 0 },
    climatiq: { configured: false, base_url: '' },
    faostat: { configured: false, base_url: '' },
  },
}

export function useSustainabilityProviders() {
  return useQuery({
    queryKey: ['sustainability', 'providers'],
    queryFn: async () => (await apiClient.get<SustainabilityProviders>('/api/v1/sustainability/providers/status')).data,
    initialData: EMPTY_SUSTAINABILITY_PROVIDERS,
    staleTime: 5 * 60 * 1000,
  })
}

export function useSustainabilityPsm(zulassungsnummer: string | null, tenantId = '00000000-0000-0000-0000-000000000001') {
  return useQuery({
    queryKey: ['sustainability', 'psm', zulassungsnummer, tenantId],
    queryFn: async () => (
      await apiClient.get<SustainabilityPsmResponse>(
        `/api/v1/sustainability/psm/${encodeURIComponent(zulassungsnummer ?? '')}?tenant_id=${encodeURIComponent(tenantId)}`
      )
    ).data,
    enabled: Boolean(zulassungsnummer),
    initialData: null,
    staleTime: 30 * 60 * 1000,
  })
}

/** ESG-Report (Gap 046): Aggregierte Nährstoff- und CO2-Daten aus Lieferscheinen */
export type EsgReportData = {
  year: number
  customerId: string | null
  deliveryCount: number
  totalNutrientNKg: number
  totalNutrientP2o5Kg: number
  totalCo2eKg: number
  byMonth: Record<string, { deliveries: number; n_kg: number; p2o5_kg: number; co2e_kg: number }>
}

export function useEsgReport(year: number, customerId?: string | null) {
  return useQuery({
    queryKey: ['sustainability', 'esg-report', year, customerId ?? 'all'],
    queryFn: async () => {
      const params = new URLSearchParams({ year: String(year) })
      if (customerId) params.set('customer_id', customerId)
      const r = await apiClient.get<EsgReportData>(`/api/v1/sustainability/esg-report?${params.toString()}`)
      return r.data
    },
    enabled: year >= 2020 && year <= 2030,
    initialData: {
      year,
      customerId: customerId ?? null,
      deliveryCount: 0,
      totalNutrientNKg: 0,
      totalNutrientP2o5Kg: 0,
      totalCo2eKg: 0,
      byMonth: {},
    } as EsgReportData,
  })
}

export async function downloadEsgReportCsv(year: number, customerId?: string): Promise<void> {
  const params = new URLSearchParams({ year: String(year) })
  if (customerId) params.set('customer_id', customerId)
  const response = await apiClient.get<Blob>(`/api/v1/sustainability/esg-report/export.csv?${params.toString()}`, {
    responseType: 'blob',
  })
  const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `esg-report-${year}${customerId ? `-${customerId}` : ''}.csv`
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  URL.revokeObjectURL(url)
}

export async function downloadEsgReportPdf(year: number, customerId?: string): Promise<void> {
  const params = new URLSearchParams({ year: String(year) })
  if (customerId) params.set('customer_id', customerId)
  const response = await apiClient.get<Blob>(`/api/v1/sustainability/esg-report/export.pdf?${params.toString()}`, {
    responseType: 'blob',
  })
  const blob = new Blob([response.data], { type: 'application/pdf' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `esg-report-${year}${customerId ? `-${customerId}` : ''}.pdf`
  document.body.appendChild(anchor)
  anchor.click()
  document.body.removeChild(anchor)
  URL.revokeObjectURL(url)
}
