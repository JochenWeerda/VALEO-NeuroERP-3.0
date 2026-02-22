import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type ChargeStatus = 'erfasst' | 'freigegeben' | 'in-pruefung' | 'gesperrt'

export type Charge = {
  id: string
  chargenId: string
  losnummer?: string | null
  artikel: string
  artikelId: string
  produktbezeichnung?: string | null
  menge: number
  lagerort: string
  eingang: string
  herstellungsdatum?: string | null
  status: ChargeStatus
  qualitaetsstatus?: string | null
  freigabeDatum?: string | null
  herkunft?: string | null
  bemerkungen?: string | null
  rueckverfolgbar_bis_stunden: number
  rohstoffe: Array<Record<string, unknown>>
  lieferant_info: Record<string, unknown>
  kunden_info: Record<string, unknown>
  produktionsprozess: Record<string, unknown>
  digitales_mischbuch: Record<string, unknown>
  haccp_system: Record<string, unknown>
  eigenkontrollen: Array<Record<string, unknown>>
  warentrennung_qs_nicht_qs: boolean
  krisenmanagement: Record<string, unknown>
  futtermittelmonitoring: Record<string, unknown>
  qualitaetspersonal: Record<string, unknown>
  qs_datenbank: Record<string, unknown>
  createdAt?: string | null
  updatedAt?: string | null
}

export type ChargeCreatePayload = {
  artikel_id: string
  artikel: string
  chargen_id: string
  menge: number
  lagerort: string
  eingang: string
  herstellungsdatum?: string | null
  losnummer?: string | null
  produktbezeichnung?: string | null
  rueckverfolgbar_bis_stunden?: number
  herkunft?: string | null
  qualitaetsstatus?: string
  bemerkungen?: string | null
  rohstoffe?: Array<Record<string, unknown>>
  lieferant_info?: Record<string, unknown>
  kunden_info?: Record<string, unknown>
  produktionsprozess?: Record<string, unknown>
  digitales_mischbuch?: Record<string, unknown>
  haccp_system?: Record<string, unknown>
  eigenkontrollen?: Array<Record<string, unknown>>
  warentrennung_qs_nicht_qs?: boolean
  krisenmanagement?: Record<string, unknown>
  futtermittelmonitoring?: Record<string, unknown>
  qualitaetspersonal?: Record<string, unknown>
  qs_datenbank?: Record<string, unknown>
}

export type ChargeUpdatePayload = Partial<Omit<ChargeCreatePayload, 'artikel_id' | 'artikel' | 'chargen_id' | 'eingang'>> & {
  status?: ChargeStatus
  freigabe_datum?: string | null
}

export type ChargeListResponse = {
  items: Charge[]
  total: number
  limit: number
  offset: number
}

export type ChargeQsReadiness = {
  charge_id: string
  checks: Record<string, boolean>
  score: number
  max_score: number
  ready: boolean
}

export const chargeKeys = {
  all: ['chargen'] as const,
  detail: (id: string) => ['chargen', id] as const,
  readiness: (id: string) => ['chargen', id, 'qs-readiness'] as const,
}

export async function listCharges(): Promise<Charge[]> {
  const res = await apiClient.get<ChargeListResponse>('/api/v1/chargen')
  return res.data.items ?? []
}

export async function getCharge(id: string): Promise<Charge> {
  return (await apiClient.get<Charge>(`/api/v1/chargen/${encodeURIComponent(id)}`)).data
}

export async function createCharge(payload: ChargeCreatePayload): Promise<Charge> {
  return (await apiClient.post<Charge>('/api/v1/chargen', payload)).data
}

export async function updateCharge(id: string, payload: ChargeUpdatePayload): Promise<Charge> {
  return (await apiClient.patch<Charge>(`/api/v1/chargen/${encodeURIComponent(id)}`, payload)).data
}

export async function deleteCharge(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/chargen/${encodeURIComponent(id)}`)
}

export async function getChargeQsReadiness(id: string): Promise<ChargeQsReadiness> {
  return (await apiClient.get<ChargeQsReadiness>(`/api/v1/chargen/${encodeURIComponent(id)}/qs-readiness`)).data
}

export function useCharges() {
  return useQuery({
    queryKey: chargeKeys.all,
    queryFn: listCharges,
  })
}

export function useCharge(id: string | undefined) {
  return useQuery({
    queryKey: id ? chargeKeys.detail(id) : ['chargen', 'none'],
    queryFn: () => getCharge(id as string),
    enabled: Boolean(id),
  })
}

export function useChargeQsReadiness(id: string | undefined) {
  return useQuery({
    queryKey: id ? chargeKeys.readiness(id) : ['chargen', 'none', 'qs-readiness'],
    queryFn: () => getChargeQsReadiness(id as string),
    enabled: Boolean(id),
  })
}

export function useCreateCharge() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createCharge,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: chargeKeys.all })
    },
  })
}

export function useUpdateCharge() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: ChargeUpdatePayload }) => updateCharge(id, payload),
    onSuccess: (_data, variables) => {
      void qc.invalidateQueries({ queryKey: chargeKeys.all })
      void qc.invalidateQueries({ queryKey: chargeKeys.detail(variables.id) })
      void qc.invalidateQueries({ queryKey: chargeKeys.readiness(variables.id) })
    },
  })
}

export function useDeleteCharge() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: deleteCharge,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: chargeKeys.all })
    },
  })
}
