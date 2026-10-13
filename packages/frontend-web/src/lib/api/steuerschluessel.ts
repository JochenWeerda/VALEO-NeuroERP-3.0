/**
 * Steuerschluessel — Backend: /api/v1/finance/tax-keys.
 *
 * Gespeichert wird ueber den Kommando-Weg der ScreenDefinition `finance/steuerschluessel`
 * (Pruefung, Audit, Idempotenz). Der Schluessel entscheidet: vorhanden = Aenderung, sonst Anlage.
 */
import { apiClient } from '@/lib/api-client'
import type { KommandoErgebnis } from '@/lib/api/gutschrift'

const WEG = '/api/v1/finance/tax-keys'

export type Steuerschluessel = {
  id: string
  code: string
  bezeichnung: string
  steuersatz: number | string
  ustva_position?: string | null
  ustva_bezeichnung?: string | null
  intracom: boolean
  export: boolean
  reverse_charge: boolean
  par_24_ustg: boolean
  gueltig_von: string
  gueltig_bis?: string | null
  notizen?: string | null
  debit_account?: string | null
  credit_account?: string | null
  revenue_account?: string | null
  active: boolean
  /** Wofuer der Schluessel automatisch bucht — oder warum nicht. Vom Server, aus der Regel der Buchung. */
  verwendung?: string | null
}

/** Die Eingabe der Maske. Leer bleibt leer: Der Server ergaenzt nichts. */
export type SteuerschluesselEingabe = {
  code: string
  bezeichnung: string
  steuersatz: string
  ustva_position: string | null
  ustva_bezeichnung: string | null
  intracom: boolean
  export: boolean
  reverse_charge: boolean
  par_24_ustg: boolean
  gueltig_von: string
  gueltig_bis: string | null
  notizen: string | null
  debit_account: string | null
  credit_account: string | null
  revenue_account: string | null
  active: boolean
}

/** Alle Schluessel des Mandanten, auch inaktive. */
export async function listeSteuerschluessel(): Promise<Steuerschluessel[]> {
  return (await apiClient.get<Steuerschluessel[]>(WEG, { params: { active_only: false } })).data
}

export async function speichereSteuerschluessel(daten: SteuerschluesselEingabe, auftrag: string): Promise<KommandoErgebnis> {
  return (
    await apiClient.post<KommandoErgebnis>(`${WEG}/actions/speichern`, {
      ...daten,
      _mode: 'execute',
      _idempotencyKey: auftrag,
    })
  ).data
}
