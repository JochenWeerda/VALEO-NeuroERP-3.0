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

export type FuhrparkTerminart = {
  id: string
  terminart: string
  intervall_monate: number
  intervall_km: number
}

export type FuhrparkTerminartPayload = Omit<FuhrparkTerminart, 'id'>

export type FuhrparkRechnung = {
  id: string
  rechnungs_nr: string
  datum: string
  fahrzeug_id?: string | null
  fahrzeug_kennzeichen?: string | null
  sachkonto?: string | null
  kostenart?: string | null
  betrag_eur: number
  notiz?: string | null
}

export type FuhrparkRechnungPayload = Omit<FuhrparkRechnung, 'id'>

export type FuhrparkAusgehendesDokument = {
  id: string
  beleg_typ: string
  formular?: string | null
  ziel_modul?: string | null
  beschreibung?: string | null
  aktiv: boolean
  letzter_druck?: string | null
}

export type FuhrparkAusgehendesDokumentPayload = Omit<FuhrparkAusgehendesDokument, 'id'>

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

export async function listFuhrparkTerminarten(): Promise<FuhrparkTerminart[]> {
  return (await apiClient.get<FuhrparkTerminart[]>('/api/v1/fuhrpark/terminarten')).data
}

export async function createFuhrparkTerminart(payload: FuhrparkTerminartPayload): Promise<FuhrparkTerminart> {
  return (await apiClient.post<FuhrparkTerminart>('/api/v1/fuhrpark/terminarten', payload)).data
}

export async function updateFuhrparkTerminart(id: string, payload: FuhrparkTerminartPayload): Promise<FuhrparkTerminart> {
  return (await apiClient.patch<FuhrparkTerminart>(`/api/v1/fuhrpark/terminarten/${id}`, payload)).data
}

export async function deleteFuhrparkTerminart(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/fuhrpark/terminarten/${id}`)
}

export async function listFuhrparkRechnungen(): Promise<FuhrparkRechnung[]> {
  return (await apiClient.get<FuhrparkRechnung[]>('/api/v1/fuhrpark/rechnungen')).data
}

export async function createFuhrparkRechnung(payload: FuhrparkRechnungPayload): Promise<FuhrparkRechnung> {
  return (await apiClient.post<FuhrparkRechnung>('/api/v1/fuhrpark/rechnungen', payload)).data
}

export async function updateFuhrparkRechnung(id: string, payload: FuhrparkRechnungPayload): Promise<FuhrparkRechnung> {
  return (await apiClient.patch<FuhrparkRechnung>(`/api/v1/fuhrpark/rechnungen/${id}`, payload)).data
}

export async function deleteFuhrparkRechnung(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/fuhrpark/rechnungen/${id}`)
}

export async function listFuhrparkAusgehendeDokumente(): Promise<FuhrparkAusgehendesDokument[]> {
  return (await apiClient.get<FuhrparkAusgehendesDokument[]>('/api/v1/fuhrpark/ausgehende-dokumente')).data
}

export async function createFuhrparkAusgehendesDokument(
  payload: FuhrparkAusgehendesDokumentPayload,
): Promise<FuhrparkAusgehendesDokument> {
  return (await apiClient.post<FuhrparkAusgehendesDokument>('/api/v1/fuhrpark/ausgehende-dokumente', payload)).data
}

export async function updateFuhrparkAusgehendesDokument(
  id: string,
  payload: FuhrparkAusgehendesDokumentPayload,
): Promise<FuhrparkAusgehendesDokument> {
  return (await apiClient.patch<FuhrparkAusgehendesDokument>(`/api/v1/fuhrpark/ausgehende-dokumente/${id}`, payload))
    .data
}

export async function deleteFuhrparkAusgehendesDokument(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/fuhrpark/ausgehende-dokumente/${id}`)
}

// ─── VERTIEFUNG: Statushistorie, Schadensfälle, Bußgeld, Wartungsvorhersage ──

export type FahrzeugStatusHistorieEintrag = {
  id: string
  fahrzeug_id: string
  von_status: string | null
  zu_status: string
  grund: string | null
  benutzer: string | null
  km_stand: number | null
  timestamp: string
}

export type FahrzeugSchaden = {
  id: string
  fahrzeug_id: string
  datum: string
  ort: string
  beschreibung: string
  schadenhoehe_eur: number | null
  versicherung_gemeldet: boolean
  versicherungs_nr: string | null
  gegner_kennzeichen: string | null
  polizei_aktenzeichen: string | null
  status: 'offen' | 'bearbeitung' | 'abgeschlossen'
  abgeschlossen_am: string | null
  erstellt_von: string | null
  created_at: string
  updated_at: string
}

export type FahrzeugBussgeld = {
  id: string
  fahrzeug_id: string
  fahrer_id: string | null
  datum: string
  ort: string | null
  tatbestand: string
  betrag_eur: number
  faellig_am: string | null
  bezahlt_am: string | null
  aktenzeichen: string | null
  status: 'offen' | 'bezahlt' | 'einspruch' | 'verjährt'
  notiz: string | null
  created_at: string
}

export type WartungsVorhersage = {
  fahrzeug_id: string
  kennzeichen: string
  aktueller_km_stand: number
  tuev_faellig_in_tagen: number | null
  asu_faellig_in_tagen: number | null
  inspektion_faellig_in_tagen: number | null
  vorhersagen_nach_km: Array<{
    terminart: string
    intervall_monate: number
    intervall_km: number
    faellig_in_km: number | null
    faellig_bei_km: number | null
    dringend: boolean
  }>
}

// Statushistorie
export async function changeFahrzeugStatus(
  fahrzeugId: string,
  payload: { zu_status: string; grund?: string; benutzer?: string; km_stand?: number },
): Promise<FuhrparkFahrzeug> {
  return (await apiClient.post<FuhrparkFahrzeug>(`/api/v1/fuhrpark/fahrzeuge/${fahrzeugId}/status`, payload)).data
}

export async function getFahrzeugStatusHistorie(
  fahrzeugId: string,
  limit = 50,
): Promise<FahrzeugStatusHistorieEintrag[]> {
  return (
    await apiClient.get<FahrzeugStatusHistorieEintrag[]>(
      `/api/v1/fuhrpark/fahrzeuge/${fahrzeugId}/status-historie?limit=${limit}`,
    )
  ).data
}

// Schadensfälle
export async function listFahrzeugSchaeden(fahrzeugId: string, status?: string): Promise<FahrzeugSchaden[]> {
  const qs = status ? `?status=${status}` : ''
  return (await apiClient.get<FahrzeugSchaden[]>(`/api/v1/fuhrpark/fahrzeuge/${fahrzeugId}/schaeden${qs}`)).data
}

export async function createFahrzeugSchaden(
  fahrzeugId: string,
  payload: Omit<FahrzeugSchaden, 'id' | 'fahrzeug_id' | 'created_at' | 'updated_at' | 'abgeschlossen_am'>,
): Promise<FahrzeugSchaden> {
  return (await apiClient.post<FahrzeugSchaden>(`/api/v1/fuhrpark/fahrzeuge/${fahrzeugId}/schaeden`, payload)).data
}

export async function updateFahrzeugSchaden(
  fahrzeugId: string,
  schadenId: string,
  payload: Partial<Pick<FahrzeugSchaden, 'schadenhoehe_eur' | 'versicherung_gemeldet' | 'versicherungs_nr' | 'status' | 'polizei_aktenzeichen'>>,
): Promise<FahrzeugSchaden> {
  return (
    await apiClient.patch<FahrzeugSchaden>(`/api/v1/fuhrpark/fahrzeuge/${fahrzeugId}/schaeden/${schadenId}`, payload)
  ).data
}

// Bußgelder
export async function listFahrzeugBussgeld(fahrzeugId: string, status?: string): Promise<FahrzeugBussgeld[]> {
  const qs = status ? `?status=${status}` : ''
  return (await apiClient.get<FahrzeugBussgeld[]>(`/api/v1/fuhrpark/fahrzeuge/${fahrzeugId}/bussgeld${qs}`)).data
}

export async function createFahrzeugBussgeld(
  fahrzeugId: string,
  payload: { datum: string; tatbestand: string; betrag_eur: number; ort?: string; faellig_am?: string; aktenzeichen?: string; notiz?: string },
): Promise<FahrzeugBussgeld> {
  return (await apiClient.post<FahrzeugBussgeld>(`/api/v1/fuhrpark/fahrzeuge/${fahrzeugId}/bussgeld`, payload)).data
}

export async function updateFahrzeugBussgeld(
  fahrzeugId: string,
  bgId: string,
  payload: { bezahlt_am?: string; status?: string; notiz?: string; aktenzeichen?: string },
): Promise<FahrzeugBussgeld> {
  return (
    await apiClient.patch<FahrzeugBussgeld>(`/api/v1/fuhrpark/fahrzeuge/${fahrzeugId}/bussgeld/${bgId}`, payload)
  ).data
}

// Wartungsvorhersage
export async function getFahrzeugWartungVorhersage(fahrzeugId: string): Promise<WartungsVorhersage> {
  return (await apiClient.get<WartungsVorhersage>(`/api/v1/fuhrpark/fahrzeuge/${fahrzeugId}/wartung-vorhersage`)).data
}

// Leasing-Rückgabe
export async function leasingRueckgabe(
  fahrzeugId: string,
  payload: { rueckgabedatum: string; km_stand_bei_rueckgabe: number; zustand_bemerkung?: string; benutzer?: string },
): Promise<FuhrparkFahrzeug & { rueckgabe_protokoll: Record<string, unknown> }> {
  return (
    await apiClient.post<FuhrparkFahrzeug & { rueckgabe_protokoll: Record<string, unknown> }>(
      `/api/v1/fuhrpark/fahrzeuge/${fahrzeugId}/leasing-rueckgabe`,
      payload,
    )
  ).data
}
