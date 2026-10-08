/**
 * Postfaecher des Mandanten (info@, dispo@, fibu@ …) — Backend: /api/v1/admin/postfaecher.
 *
 * Das Passwort wird nur gesendet, nie empfangen: Die Antwort sagt mit
 * `hat_geheimnis`, ob eines hinterlegt ist.
 */
import { apiClient } from '@/lib/api-client'

const WEG = '/api/v1/admin/postfaecher'

export type Postfach = {
  id: string
  kennung: string
  bezeichnung?: string | null
  anbieter: 'ionos' | 'google' | 'smtp' | 'alias'
  anmeldung: 'passwort' | 'oauth2' | 'alias'
  smtp_host?: string | null
  smtp_port?: number | null
  sicherheit?: string | null
  benutzer?: string | null
  absender_email: string
  absender_name?: string | null
  zugang_von?: string | null
  ist_standard: boolean
  verwendungen: string[]
  rollen: string[]
  benutzer_freigabe: string[]
  persoenlich_fuer?: string | null
  hat_geheimnis: boolean
  status: 'neu' | 'geprueft' | 'fehler'
  geprueft_am?: string | null
  letzter_fehler?: string | null
  testmail_an?: string | null
}

export type PostfachEingabe = {
  kennung: string
  bezeichnung?: string | null
  anbieter: string
  anmeldung?: string
  smtp_host?: string | null
  smtp_port?: number | null
  sicherheit?: string | null
  benutzer?: string | null
  absender_email: string
  absender_name?: string | null
  passwort?: string | null
  zugang_von?: string | null
  ist_standard: boolean
  verwendungen: string[]
  rollen: string[]
  benutzer_freigabe: string[]
  persoenlich_fuer?: string | null
}

export async function listePostfaecher(): Promise<Postfach[]> {
  return (await apiClient.get<Postfach[]>(WEG)).data
}

export async function speicherePostfach(daten: PostfachEingabe, id?: string): Promise<Postfach> {
  return id
    ? (await apiClient.put<Postfach>(`${WEG}/${encodeURIComponent(id)}`, daten)).data
    : (await apiClient.post<Postfach>(WEG, daten)).data
}

export async function testePostfach(id: string, empfaenger?: string): Promise<Postfach> {
  return (await apiClient.post<Postfach>(`${WEG}/${encodeURIComponent(id)}/testen`, { empfaenger: empfaenger || null })).data
}

export async function entfernePostfach(id: string): Promise<void> {
  await apiClient.delete(`${WEG}/${encodeURIComponent(id)}`)
}

export async function starteGoogleAnmeldung(id: string): Promise<string> {
  return (await apiClient.post<{ url: string }>(`${WEG}/${encodeURIComponent(id)}/google/start`)).data.url
}

export async function schliesseGoogleAnmeldungAb(code: string, state: string): Promise<Postfach> {
  return (await apiClient.post<Postfach>(`${WEG}/google/abschluss`, { code, state })).data
}
