import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Kontrakt-Settlement-Übergabe & Storno (DOM-CON-004.4).
 * Bewegung→Abrechnung + Storno von Bewegungen/Fixierungen.
 * Backend: app/api/v1/endpoints/contract_settlement.py
 */

export type SettlementMovement = {
  movement_id: string
  menge: number | null
  datum: string | null
  status: 'offen' | 'abgerechnet' | 'storniert' | string
  invoice_no: string | null
  settled_at: string | null
  storno_grund: string | null
}

export type SettlementFixing = {
  fixing_no: number
  fixing_id: string
  menge: number | null
  effektiv_preis: number | null
  status: 'aktiv' | 'storniert' | string
  storno_grund: string | null
}

export type SettlementStatus = {
  found: boolean
  detail?: string
  contract_no?: string
  einheit?: string | null
  bewegungen?: SettlementMovement[]
  fixierungen?: SettlementFixing[]
  summary?: { abgerufen: number; abgerechnet: number; offen_abruf: number; fixiert_aktiv: number }
}

const BASE = '/api/v1/contracts'

export function useSettlementStatus(kontrakt: string | null) {
  return useQuery({
    queryKey: ['contract-settlement', 'status', kontrakt],
    enabled: !!kontrakt,
    queryFn: async () => (await apiClient.get<SettlementStatus>(`${BASE}/settlement/status`, { params: { kontrakt } })).data,
  })
}

export function useHandover() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { kontrakt: string; movementId?: string; invoiceNo?: string }) =>
      (await apiClient.post<{ ok: boolean; uebergeben: number }>(`${BASE}/settlement`, input)).data,
    onSuccess: (_d, vars) => { void qc.invalidateQueries({ queryKey: ['contract-settlement', 'status', vars.kontrakt] }) },
  })
}

export function useStornoMovement(kontrakt: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { movementId: string; grund: string }) =>
      (await apiClient.post<{ ok: boolean; frei_menge: number }>(`${BASE}/movements/${encodeURIComponent(input.movementId)}/storno`, { grund: input.grund })).data,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['contract-settlement', 'status', kontrakt] }) },
  })
}

export function useStornoFixing(kontrakt: string | null) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { fixingId: string; grund: string }) =>
      (await apiClient.post<{ ok: boolean; frei_menge: number }>(`${BASE}/fixings/${encodeURIComponent(input.fixingId)}/storno`, { grund: input.grund })).data,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['contract-settlement', 'status', kontrakt] })
      void qc.invalidateQueries({ queryKey: ['contract-fixing', 'workspace', kontrakt] })
    },
  })
}
