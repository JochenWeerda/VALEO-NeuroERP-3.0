/**
 * UStVA (Umsatzsteuer-Voranmeldung) API Client
 * TanStack Query Hooks für Vorberechnung und Einreichung
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type UStVAVorberechnung = {
  zeitraum: string
  umsatz_netto: number
  umsatzsteuer: number
  vorsteuer: number
  zahllast: number
  positionen: Record<string, unknown>[]
}

export type VATReturnCalculateRequest = {
  period: string
  tenant_id?: string
}

export type VATReturnResponse = {
  id: string
  period: string
  return_type: string
  taxpayer_name: string
  total_sales_net: number
  total_input_tax: number
  total_output_tax: number
  vat_payable: number
  status: string
  elster_reference?: string
}

// ========== QUERY KEYS ==========

export const ustvaKeys = {
  all: ['ustva'] as const,
  vorberechnung: (zeitraum: string) => [...ustvaKeys.all, 'vorberechnung', zeitraum] as const,
}

// ========== HOOKS ==========

export function useUStVAVorberechnung(zeitraum: string) {
  return useQuery({
    queryKey: ustvaKeys.vorberechnung(zeitraum),
    queryFn: async () => {
      const response = await apiClient.get<UStVAVorberechnung>(
        `/api/v1/finance/vat-return/vorberechnung?zeitraum=${encodeURIComponent(zeitraum)}`,
      )
      return response.data
    },
    enabled: !!zeitraum,
  })
}

export function useUStVAEinreichen() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: VATReturnCalculateRequest) => {
      const response = await apiClient.post<VATReturnResponse>(
        '/api/v1/finance/vat-return/calculate',
        data,
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ustvaKeys.all })
    },
  })
}
