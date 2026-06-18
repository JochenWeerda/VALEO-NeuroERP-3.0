import { apiClient } from '@/lib/api-client'

// ── Types ─────────────────────────────────────────────────────────────────────

export type KostenstelleArt = 'KOSTENSTELLE' | 'KOSTENTRAEGER' | 'PROJEKT' | 'ABTEILUNG'
export type BudgetPeriode = 'MONAT' | 'QUARTAL' | 'JAHR'
export type KostenartGruppe = 'PERSONAL' | 'MATERIAL' | 'ABSCHREIBUNG' | 'FREMDLEISTUNG' | 'ENERGIE' | 'SONSTIGE'

export type Kostenstelle = {
  id: string
  tenant_id: string
  nummer: string
  bezeichnung: string
  kostenstelle_art: KostenstelleArt
  uebergeordnet?: string | null
  verantwortlicher?: string | null
  budget?: number | null
  budget_periode?: BudgetPeriode | null
  aktiv: boolean
  created_at: string
  updated_at: string
}

export type KostenstelleCreate = Omit<Kostenstelle, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>

export type Kostenart = {
  id: string
  tenant_id: string
  nummer: string
  bezeichnung: string
  kostenart_gruppe: KostenartGruppe
  konto_nr?: string | null
  aktiv: boolean
  created_at: string
}

export type KostenartCreate = Omit<Kostenart, 'id' | 'tenant_id' | 'created_at'>

export type Kostenbuchung = {
  id: string
  tenant_id: string
  kostenstelle_id: string
  kostenart_id?: string | null
  buchungsdatum: string
  betrag_eur: number
  buchungstext?: string | null
  belegnummer?: string | null
  periode: string
  erstellt_von?: string | null
  created_at: string
}

export type BuchungCreate = {
  kostenstelle_id: string
  kostenart_id?: string
  buchungsdatum: string
  betrag_eur: number
  buchungstext?: string
  belegnummer?: string
}

export type KostenstelleAuswertung = {
  kostenstelle_id: string
  nummer: string
  bezeichnung: string
  kostenstelle_art: KostenstelleArt
  budget: number
  budget_periode?: string | null
  verbraucht: number
  offen: number
  auslastung_prozent: number
  buchungen_anzahl: number
}

export type KostenstellenReport = {
  periode_von: string
  periode_bis: string
  gesamt_budget: number
  gesamt_verbraucht: number
  gesamt_offen: number
  auswertungen: KostenstelleAuswertung[]
}

// ── Kostenstellen ─────────────────────────────────────────────────────────────

export async function listKostenstellen(params?: { art?: string; aktiv?: boolean }): Promise<Kostenstelle[]> {
  const p = new URLSearchParams()
  if (params?.art) p.set('art', params.art)
  if (params?.aktiv != null) p.set('aktiv', String(params.aktiv))
  const qs = p.toString() ? `?${p.toString()}` : ''
  return (await apiClient.get<Kostenstelle[]>(`/api/v1/kostenrechnung/kostenstellen${qs}`)).data
}

export async function getKostenstelle(id: string): Promise<Kostenstelle> {
  return (await apiClient.get<Kostenstelle>(`/api/v1/kostenrechnung/kostenstellen/${id}`)).data
}

export async function createKostenstelle(payload: KostenstelleCreate): Promise<Kostenstelle> {
  return (await apiClient.post<Kostenstelle>('/api/v1/kostenrechnung/kostenstellen', payload)).data
}

export async function updateKostenstelle(id: string, payload: KostenstelleCreate): Promise<Kostenstelle> {
  return (await apiClient.patch<Kostenstelle>(`/api/v1/kostenrechnung/kostenstellen/${id}`, payload)).data
}

export async function deleteKostenstelle(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/kostenrechnung/kostenstellen/${id}`)
}

// ── Kostenarten ───────────────────────────────────────────────────────────────

export async function listKostenarten(params?: { aktiv?: boolean; gruppe?: string }): Promise<Kostenart[]> {
  const p = new URLSearchParams()
  if (params?.aktiv != null) p.set('aktiv', String(params.aktiv))
  if (params?.gruppe) p.set('gruppe', params.gruppe)
  const qs = p.toString() ? `?${p.toString()}` : ''
  return (await apiClient.get<Kostenart[]>(`/api/v1/kostenrechnung/kostenarten${qs}`)).data
}

export async function createKostenart(payload: KostenartCreate): Promise<Kostenart> {
  return (await apiClient.post<Kostenart>('/api/v1/kostenrechnung/kostenarten', payload)).data
}

export async function deleteKostenart(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/kostenrechnung/kostenarten/${id}`)
}

// ── Buchungen ─────────────────────────────────────────────────────────────────

export async function listBuchungen(params?: { kostenstelle_id?: string; periode?: string }): Promise<Kostenbuchung[]> {
  const p = new URLSearchParams()
  if (params?.kostenstelle_id) p.set('kostenstelle_id', params.kostenstelle_id)
  if (params?.periode) p.set('periode', params.periode)
  const qs = p.toString() ? `?${p.toString()}` : ''
  return (await apiClient.get<Kostenbuchung[]>(`/api/v1/kostenrechnung/buchungen${qs}`)).data
}

export async function createBuchung(payload: BuchungCreate): Promise<Kostenbuchung> {
  return (await apiClient.post<Kostenbuchung>('/api/v1/kostenrechnung/buchungen', payload)).data
}

export async function deleteBuchung(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/kostenrechnung/buchungen/${id}`)
}

// ── Report ────────────────────────────────────────────────────────────────────

export async function getKostenstellenReport(von: string, bis: string): Promise<KostenstellenReport> {
  return (await apiClient.get<KostenstellenReport>(`/api/v1/kostenrechnung/report?von=${von}&bis=${bis}`)).data
}
