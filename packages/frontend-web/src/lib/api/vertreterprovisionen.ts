/**
 * Vertreterprovisionsgruppen und -staffeln API Client
 * TanStack Query Hooks für /api/v1/crm/vertreter/provisionen
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type Richtung = 'ek' | 'vk'
export type Provisionstyp = 'fix' | 'staffel_optpreis' | 'staffel_preis_zuab'

export type ProvisionsGruppe = {
  id: string
  gruppe_nr: string
  bezeichnung: string
  richtung: Richtung
  provisionstyp: Provisionstyp
  provisionssatz: number | null
  aktiv: boolean
  created_at: string
}

export type ProvisionsStaffelZeile = {
  id: string
  staffel_id: string
  zeile_nr: number
  ab_wert: number
  provisionssatz: number
}

export type ProvisionsStaffel = {
  id: string
  gruppe_id: string
  vertreterklasse: string | null
  zeilen: ProvisionsStaffelZeile[]
  created_at: string
}

// ========== QUERY KEYS ==========

export const PROV_KEYS = {
  gruppen: (richtung?: Richtung) => ['vertreter-provisionsgruppen', richtung ?? 'all'] as const,
  staffeln: (gruppeId?: string) => ['vertreter-provisionsstaffeln', gruppeId ?? ''] as const,
}

// ========== PROVISIONSGRUPPEN ==========

export function useProvisionsgruppen(richtung?: Richtung) {
  return useQuery({
    queryKey: PROV_KEYS.gruppen(richtung),
    queryFn: async () => {
      const params = richtung ? `?richtung=${richtung}` : ''
      const res = await apiClient.get<ProvisionsGruppe[]>(
        `/api/v1/crm/vertreter/provisionen/gruppen${params}`
      )
      return res.data
    },
  })
}

export function useCreateProvisionsgruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: {
      gruppe_nr: string
      bezeichnung: string
      richtung: Richtung
      provisionstyp: Provisionstyp
      provisionssatz?: number | null
    }) =>
      apiClient.post<ProvisionsGruppe>(
        '/api/v1/crm/vertreter/provisionen/gruppen',
        payload
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vertreter-provisionsgruppen'] })
    },
  })
}

export function useDeleteProvisionsgruppe() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (gruppe_nr: string) =>
      apiClient.delete(`/api/v1/crm/vertreter/provisionen/gruppen/${gruppe_nr}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vertreter-provisionsgruppen'] })
    },
  })
}

// ========== PROVISIONSSTAFFELN ==========

export function useProvisionsstaffeln(gruppeId?: string) {
  return useQuery({
    queryKey: PROV_KEYS.staffeln(gruppeId),
    queryFn: async () => {
      const params = gruppeId ? `?gruppe_id=${gruppeId}` : ''
      const res = await apiClient.get<ProvisionsStaffel[]>(
        `/api/v1/crm/vertreter/provisionen/staffeln${params}`
      )
      return res.data
    },
    enabled: gruppeId !== undefined,
  })
}

export function useCreateProvisionsstaffel() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: {
      gruppe_id: string
      vertreterklasse?: string | null
      zeilen: { zeile_nr: number; ab_wert: number; provisionssatz: number }[]
    }) =>
      apiClient.post<ProvisionsStaffel>(
        '/api/v1/crm/vertreter/provisionen/staffeln',
        payload
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vertreter-provisionsstaffeln'] })
    },
  })
}
