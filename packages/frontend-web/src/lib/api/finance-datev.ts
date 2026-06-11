import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * DATEV-Export (DOM-FIN-004.5).
 * Backend: app/api/v1/endpoints/finance_datev.py
 */

export type DatevExport = { filename: string; zeilen: number; summe: number; csv: string }

export function useDatevExport() {
  return useMutation({
    mutationFn: async (typ: 'alle' | 'debitor' | 'kreditor' = 'alle') =>
      (await apiClient.get<DatevExport>('/api/v1/finance/datev-export', { params: { typ } })).data,
  })
}
