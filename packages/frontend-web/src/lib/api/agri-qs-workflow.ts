/**
 * WM-AGRI-QS-003/004 — QS-Workflow fuer Silo-Lots unter `/api/v1/supply-chain`.
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiClient } from '../api-client'

export type QsWorklistLot = {
  id: string
  virtual_lot_number?: string | null
  article_id?: string | null
  quantity_kg?: number
  status?: string
  qs_status?: string
  source_ticket_id?: string | null
  linked_cell_count?: number
  kind?: 'lot'
}

export type QsWorklistCell = {
  id: string
  cell_code?: string | null
  name?: string | null
  warehouse_id?: string | null
  qs_status?: string
  current_lot_id?: string | null
  current_material_id?: string | null
  current_stock_kg?: number | string | null
  virtual_lot_number?: string | null
  kind?: 'cell'
}

export type QsWorklistResponse = {
  lots: QsWorklistLot[]
  cells: QsWorklistCell[]
  summary: {
    lot_count: number
    cell_count: number
    blocked_cells: number
    in_review: number
  }
}

export type QsReleaseSuggest = {
  ok: boolean
  lot_id: string
  virtual_lot_number?: string | null
  current_lot_status?: string
  production_release_allowed?: boolean
  blockers?: string[]
  suggested?: {
    sampleId?: string | null
    analysisId?: string | null
    labDocumentId?: string | null
    productionReleaseRef?: string | null
    reason?: string
  }
}

export type QsTransitionBody = {
  targetStatus: string
  reason: string
  operator: string
  sampleId?: string
  analysisId?: string
  labDocumentId?: string
  gmpEvidenceId?: string
  vlogEvidenceId?: string
  productionReleaseRef?: string
}

export const agriQsKeys = {
  worklist: ['agri-qs-worklist'] as const,
  suggest: (lotId: string) => ['agri-qs-suggest', lotId] as const,
}

export function useQsWorklist(limit = 100) {
  return useQuery({
    queryKey: [...agriQsKeys.worklist, limit],
    queryFn: async () => {
      const { data } = await apiClient.get<QsWorklistResponse>('/api/v1/supply-chain/qs-worklist', {
        params: { limit },
      })
      return data
    },
    refetchInterval: 30_000,
  })
}

export function useQsReleaseSuggest(lotId: string | null, enabled: boolean) {
  return useQuery({
    queryKey: agriQsKeys.suggest(lotId ?? ''),
    queryFn: async () => {
      if (!lotId) throw new Error('lotId required')
      const { data } = await apiClient.get<QsReleaseSuggest>(
        `/api/v1/supply-chain/lots/${encodeURIComponent(lotId)}/qs-release-suggest`,
      )
      return data
    },
    enabled: enabled && Boolean(lotId),
  })
}

export function useQsTransition() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (vars: { lotId: string; body: QsTransitionBody }) => {
      const { data } = await apiClient.post(
        `/api/v1/supply-chain/lots/${encodeURIComponent(vars.lotId)}/qs-transition`,
        vars.body,
      )
      return data
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: agriQsKeys.worklist })
      void qc.invalidateQueries({ queryKey: ['agri-silo-cells'] })
    },
  })
}

export function qsStatusLabel(status: string): string {
  if (status === 'gesperrt') return 'Gesperrt'
  if (status === 'in_pruefung') return 'In Prüfung'
  if (status === 'reserviert') return 'Reserviert'
  if (status === 'reinigung') return 'Reinigung'
  if (status === 'frei' || status === 'active') return 'Freigegeben'
  return status || '—'
}

export function qsStatusVariant(status: string): 'destructive' | 'secondary' | 'outline' {
  if (status === 'gesperrt') return 'destructive'
  if (status === 'in_pruefung') return 'secondary'
  return 'outline'
}
