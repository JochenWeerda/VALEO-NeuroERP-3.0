import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

export type Versandart = 'email' | 'fax' | 'edi' | 'post' | 'api'

export type VersandprofilOut = {
  id: string
  profil_nr: string
  bezeichnung: string
  versandart: Versandart
  smtp_server?: string | null
  smtp_port?: number | null
  smtp_benutzer?: string | null
  absender_email?: string | null
  absender_name?: string | null
  cc_email?: string | null
  bcc_email?: string | null
  betreff_vorlage?: string | null
  archiv_kennzeichen: boolean
  aktiv: boolean
  created_at?: string | null
}

export type VersandprofilPayload = {
  profil_nr: string
  bezeichnung: string
  versandart?: Versandart
  smtp_server?: string | null
  smtp_port?: number | null
  smtp_benutzer?: string | null
  absender_email?: string | null
  absender_name?: string | null
  cc_email?: string | null
  bcc_email?: string | null
  betreff_vorlage?: string | null
  archiv_kennzeichen?: boolean
}

export type LieferavisOut = {
  id: string
  avis_datum: string
  lieferdatum_erwartet?: string | null
  lieferant_nr?: string | null
  kunden_nr?: string | null
  artikel_nr?: string | null
  menge?: number | null
  notiz?: string | null
  created_at?: string | null
}

export type LieferavisPayload = {
  avis_datum: string
  lieferdatum_erwartet?: string | null
  lieferant_nr?: string | null
  kunden_nr?: string | null
  artikel_nr?: string | null
  menge?: number | null
  notiz?: string | null
}

export async function listVersandprofile(): Promise<VersandprofilOut[]> {
  return (await apiClient.get<VersandprofilOut[]>('/api/v1/logistik/versand/profile')).data
}

export async function createVersandprofil(payload: VersandprofilPayload): Promise<VersandprofilOut> {
  return (await apiClient.post<VersandprofilOut>('/api/v1/logistik/versand/profile', payload)).data
}

export async function deleteVersandprofil(profil_nr: string): Promise<void> {
  await apiClient.delete(`/api/v1/logistik/versand/profile/${encodeURIComponent(profil_nr)}`)
}

export async function listLieferavise(): Promise<LieferavisOut[]> {
  return (await apiClient.get<LieferavisOut[]>('/api/v1/logistik/versand/avise')).data
}

export async function createLieferavis(payload: LieferavisPayload): Promise<LieferavisOut> {
  return (await apiClient.post<LieferavisOut>('/api/v1/logistik/versand/avise', payload)).data
}

export function useVersandprofile() {
  return useQuery({
    queryKey: ['versandprofile'],
    queryFn: listVersandprofile,
  })
}

export function useCreateVersandprofil() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createVersandprofil,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['versandprofile'] }) },
  })
}

export function useDeleteVersandprofil() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (profil_nr: string) => deleteVersandprofil(profil_nr),
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['versandprofile'] }) },
  })
}

export function useLieferavise() {
  return useQuery({
    queryKey: ['lieferavise'],
    queryFn: listLieferavise,
  })
}

export function useCreateLieferavis() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createLieferavis,
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['lieferavise'] }) },
  })
}
