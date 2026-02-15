import { apiClient } from '@/lib/api-client'

export type FuhrparkFahrzeug = {
  id: string
  ro_nummer?: string | null
  is_neu?: boolean
  betrieb?: string | null
  bereich?: string | null
  pol_kennzeichen?: string | null
  kennzeichen: string
  typ: string
  marke?: string | null
  modell?: string | null
  baujahr?: number | null
  verwendung?: string | null
  kfz_brief_nummer?: string | null
  schadstoffgruppe?: string | null
  leistung_kw?: number | null
  kraftstoff?: string | null
  fahrgestellnummer?: string | null
  erstzulassung?: string | null
  ausstattung?: string | null
  fahrtenschreiber_vorhanden?: boolean
  ahk_vorhanden?: boolean
  ladekran_vorhanden?: boolean
  fahrer_name?: string | null
  fahrer_vorname?: string | null
  kilometerstand?: number | null
  km_stand_alle_eintraege?: boolean
  bestellnummer?: string | null
  bestelldatum?: string | null
  haendler?: string | null
  zustand?: string | null
  kaufsumme_eur?: number | null
  kaufdatum?: string | null
  verkaufsdatum?: string | null
  abmeldedatum?: string | null
  kostenstelle?: string | null
  abschreibungsart?: string | null
  afa_jahre?: number | null
  afa_eur_jaehrlich?: number | null
  afa_eur_monatlich?: number | null
  leasingdauer_monate?: number | null
  leasinggesellschaft?: string | null
  leasingrate_eur?: number | null
  kfz_steuer_eur?: number | null
  kfz_steuernummer?: string | null
  kontierung?: string | null
  finanzamt?: string | null
  versicherungs_gesellschaft?: string | null
  versicherungsschein_nr?: string | null
  versicherung_satz_eur_monat?: number | null
  versicherung_haftpflicht?: boolean
  versicherung_kasko?: boolean
  naechster_tuev_termin?: string | null
  naechster_asu_termin?: string | null
  naechste_inspektion?: string | null
  leergewicht_kg?: number | null
  nutzlast_kg?: number | null
  gesamtgewicht_kg?: number | null
  anhaengerlast_kg?: number | null
  winterreifen_vorhanden?: boolean
  winterreifen_eingelagert?: boolean
  handy_freisprecheinrichtung?: boolean
  handy_fabrikat?: string | null
  handy_rufnummer?: string | null
  status?: string | null
}

export type FuhrparkFahrzeugPayload = Omit<FuhrparkFahrzeug, 'id'>

export async function listFuhrparkFahrzeuge(): Promise<FuhrparkFahrzeug[]> {
  return (await apiClient.get<FuhrparkFahrzeug[]>('/api/v1/fuhrpark/fahrzeuge')).data
}

export async function getFuhrparkFahrzeug(id: string): Promise<FuhrparkFahrzeug> {
  return (await apiClient.get<FuhrparkFahrzeug>(`/api/v1/fuhrpark/fahrzeuge/${id}`)).data
}

export async function createFuhrparkFahrzeug(payload: FuhrparkFahrzeugPayload): Promise<FuhrparkFahrzeug> {
  return (await apiClient.post<FuhrparkFahrzeug>('/api/v1/fuhrpark/fahrzeuge', payload)).data
}

export async function updateFuhrparkFahrzeug(id: string, payload: FuhrparkFahrzeugPayload): Promise<FuhrparkFahrzeug> {
  return (await apiClient.patch<FuhrparkFahrzeug>(`/api/v1/fuhrpark/fahrzeuge/${id}`, payload)).data
}

export async function deleteFuhrparkFahrzeug(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/fuhrpark/fahrzeuge/${id}`)
}

export async function setupFuhrparkDrucker(id: string, drucker_name: string): Promise<void> {
  await apiClient.post(`/api/v1/fuhrpark/fahrzeuge/${id}/drucker-einrichten`, { drucker_name })
}

export async function printFuhrparkAkte(id: string): Promise<void> {
  await apiClient.post(`/api/v1/fuhrpark/fahrzeuge/${id}/drucken`)
}

export async function unfallAnzeige(
  id: string,
  payload: { datum: string; ort: string; beschreibung: string },
): Promise<void> {
  await apiClient.post(`/api/v1/fuhrpark/fahrzeuge/${id}/unfall-anzeige`, payload)
}
