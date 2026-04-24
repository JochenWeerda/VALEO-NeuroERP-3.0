/**
 * Rationsoptimierung – DSGVO-Zugangsverwaltung
 * Betriebseigene Grundfutter und Rationen sind mandantenspezifisch geschützt.
 */

import { apiClient } from '../api-client'

const BASE = (tenantId: string) => `/api/v1/agrar/rations/${tenantId}/zugang`

export type ZugangTyp = 'admin' | 'vertriebsberater' | 'portal_user' | 'share_link'

export interface RationsZugangOut {
  id: string
  tenant_id: string
  empfaenger_email: string
  empfaenger_name: string | null
  zugang_typ: ZugangTyp
  gueltig_ab: string | null
  gueltig_bis: string | null
  darf_lesen: boolean
  darf_rationen_anlegen: boolean
  darf_grundfutter_anlegen: boolean
  darf_zugang_verwalten: boolean
  ist_aktiv: boolean
  gesperrt_am: string | null
  gesperrt_durch: string | null
  sperrgrund: string | null
  erstellt_von_email: string
  erstellt_von_name: string | null
  notizen: string | null
  created_at: string | null
  share_token?: string | null
}

export interface ZugangCreate {
  empfaenger_email: string
  empfaenger_name?: string
  zugang_typ?: ZugangTyp
  gueltig_bis?: string | null
  darf_lesen?: boolean
  darf_rationen_anlegen?: boolean
  darf_grundfutter_anlegen?: boolean
  darf_zugang_verwalten?: boolean
  notizen?: string
}

export interface ZugangPatch {
  empfaenger_name?: string
  gueltig_bis?: string | null
  darf_lesen?: boolean
  darf_rationen_anlegen?: boolean
  darf_grundfutter_anlegen?: boolean
  darf_zugang_verwalten?: boolean
  ist_aktiv?: boolean
  sperrgrund?: string
  notizen?: string
}

export interface ShareLinkOut {
  id: string
  share_token: string
  share_url_suffix: string
  gueltig_bis: string | null
}

export async function listRationsZugang(
  tenantId: string,
  aktivOnly = true,
): Promise<RationsZugangOut[]> {
  const { data } = await apiClient.get<RationsZugangOut[]>(BASE(tenantId), {
    params: { aktiv_only: aktivOnly },
  })
  return data
}

export async function createRationsZugang(
  tenantId: string,
  payload: ZugangCreate,
): Promise<RationsZugangOut> {
  const { data } = await apiClient.post<RationsZugangOut>(BASE(tenantId), payload)
  return data
}

export async function patchRationsZugang(
  tenantId: string,
  id: string,
  payload: ZugangPatch,
): Promise<RationsZugangOut> {
  const { data } = await apiClient.patch<RationsZugangOut>(`${BASE(tenantId)}/${id}`, payload)
  return data
}

export async function deleteRationsZugang(tenantId: string, id: string): Promise<void> {
  await apiClient.delete(`${BASE(tenantId)}/${id}`)
}

export async function createShareLink(
  tenantId: string,
  payload: { empfaenger_name?: string; gueltig_bis?: string | null; notizen?: string },
): Promise<ShareLinkOut> {
  const { data } = await apiClient.post<ShareLinkOut>(`${BASE(tenantId)}/share-link`, payload)
  return data
}

export async function validateShareToken(
  token: string,
): Promise<{ valid: boolean; tenant_id?: string; darf_lesen: boolean; reason?: string }> {
  const { data } = await apiClient.get<{ valid: boolean; tenant_id?: string; darf_lesen: boolean; reason?: string }>(
    `/api/v1/agrar/rations/portal/share/${token}`
  )
  return data
}
