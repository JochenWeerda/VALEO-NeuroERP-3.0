/**
 * Einwilligung zur laengeren Aufbewahrung einer Bewerbung (Talentpool).
 * Backend: /api/v1/personal/applications/{id}/einwilligung,
 *          /api/v1/personal/applications/einwilligungserklaerungen
 *
 * Erteilt wird gegen eine **Fassung** der Einwilligungserklaerung. Der Widerruf
 * schickt keinen Rumpf: Art. 7 Abs. 3 DSGVO — nicht schwerer als die Erteilung.
 */
import { apiClient } from '@/lib/api-client'

const WEG = '/api/v1/personal/applications'

export type Kanal = 'WEB' | 'E_MAIL' | 'PAPIER' | 'MUENDLICH'

export type BewerbungKopf = {
  id: string
  applicant_name: string
  position_title?: string | null
}

export type EinwilligungVorgang = {
  id: string
  vorgang: 'ERTEILT' | 'WIDERRUFEN'
  erfolgt_am?: string | null
  gueltig_bis?: string | null
  kanal?: Kanal | null
  fassung?: number | null
  einwilligungstext?: string | null
  erfasst_durch?: string | null
}

export type EinwilligungStand = {
  bewerbung_id: string
  gueltig_bis?: string | null
  erteilt_am?: string | null
  laeuft: boolean
  vorgaenge: EinwilligungVorgang[]
}

export type Erklaerung = {
  id: string
  fassung: number
  wortlaut: string
  erstellt_am?: string | null
  erstellt_durch?: string | null
}

export type ErteilungIn = {
  fassung: number
  gueltig_bis: string
  kanal: Kanal
  erfasst_durch?: string | null
}

export async function getBewerbungKopf(id: string): Promise<BewerbungKopf> {
  return (await apiClient.get<BewerbungKopf>(`${WEG}/${encodeURIComponent(id)}`)).data
}

export async function getEinwilligung(id: string): Promise<EinwilligungStand> {
  return (await apiClient.get<EinwilligungStand>(`${WEG}/${encodeURIComponent(id)}/einwilligung`)).data
}

export async function erteileEinwilligung(id: string, eingabe: ErteilungIn): Promise<EinwilligungVorgang> {
  return (await apiClient.post<EinwilligungVorgang>(`${WEG}/${encodeURIComponent(id)}/einwilligung`, eingabe)).data
}

/** Ohne Rumpf und ohne Grund. */
export async function widerrufeEinwilligung(id: string): Promise<EinwilligungVorgang> {
  return (await apiClient.delete<EinwilligungVorgang>(`${WEG}/${encodeURIComponent(id)}/einwilligung`)).data
}

export async function listErklaerungen(): Promise<Erklaerung[]> {
  return (await apiClient.get<Erklaerung[]>(`${WEG}/einwilligungserklaerungen`)).data
}

export async function legeErklaerungAn(wortlaut: string, erstelltDurch?: string | null): Promise<Erklaerung> {
  return (await apiClient.post<Erklaerung>(`${WEG}/einwilligungserklaerungen`, {
    wortlaut,
    erstellt_durch: erstelltDurch || null,
  })).data
}

/** Bei 409 nennt das Backend die Fassung, die diesen Wortlaut schon traegt. */
export function vorhandeneFassung(fehler: unknown): number | null {
  const antwort = (fehler as { response?: { status?: number; data?: { detail?: { fassung?: unknown } } } })?.response
  if (antwort?.status !== 409) return null
  const fassung = antwort.data?.detail?.fassung
  return typeof fassung === 'number' ? fassung : null
}
