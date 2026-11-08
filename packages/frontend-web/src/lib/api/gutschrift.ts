/**
 * Gutschrift (Rechnungskorrektur) — Backend: /api/v1/sales/credit-notes.
 *
 * Die Maske rechnet keine Steuer: `steuerVorschau` fragt den Server, der dieselbe Stelle wie die
 * Buchung benutzt. Speichern und Buchen laufen ueber die Kommando-Wege der ScreenDefinition
 * `sales/gutschrift` (Trockenlauf, Audit, Idempotenz).
 */
import { apiClient } from '@/lib/api-client'

const WEG = '/api/v1/sales/credit-notes'

export type GutschriftPosition = {
  description: string
  quantity: number
  unit_price: number
  /** Steuerschluessel des Mandanten. Leer = nicht angegeben; es gibt keinen Vorgabewert. */
  tax_code: string | null
}

export type Gutschrift = {
  id: string
  credit_note_number: string
  customer_id: string
  customer_name?: string | null
  invoice_reference?: string | null
  reason: string
  correction_type: 'rechnungskorrektur' | 'gutschrift_14_ustg'
  total_amount: number | string
  net_amount?: number | string | null
  tax_amount?: number | string | null
  status: string
  notes?: string | null
  lines?: Array<GutschriftPosition & { id?: string; line_total?: number | string }>
}

export type Steuerschluessel = {
  id: string
  code: string
  bezeichnung: string
  steuersatz: number | string
  debit_account?: string | null
  credit_account?: string | null
  revenue_account?: string | null
}

export type SteuerVorschau = {
  geklaert: boolean
  pruefgrund?: string | null
  netto: number | string
  steuer?: number | string | null
  brutto?: number | string | null
  gruppen: Array<{ tax_code: string; satz: number | string; netto: number | string; steuer: number | string; brutto: number | string }>
}

export type GutschriftEingabe = {
  credit_note_number: string
  customer_id: string
  customer_name?: string | null
  invoice_reference?: string | null
  reason: string
  correction_type: string
  notes?: string | null
  lines: GutschriftPosition[]
}

/** Antwort eines Kommando-Wegs; `error` nennt bei einer Ablehnung den Grund. */
export type KommandoErgebnis = {
  actionKey: string
  mode: string
  success: boolean
  summary?: string | null
  error?: string | null
  validationErrors?: Array<{ field: string; message: string; severity: string }> | null
  affectedIds?: string[] | null
  auditEntryId?: string | null
}

/** Vorschlag eines Agenten, eine Gutschrift zu buchen. Ein Mensch prueft und gibt frei. */
export type Buchungsvorschlag = {
  proposal_id: string
  credit_note_id: string
  credit_note_number: string
  netto: number | string
  steuer: number | string
  brutto: number | string
  approval_status: 'pending' | 'approved' | 'rejected' | string
  vorgeschlagen_von?: string | null
  geprueft_von?: string | null
  ablehnungsgrund?: string | null
  gebucht: boolean
}

export async function listeBuchungsvorschlaege(): Promise<Buchungsvorschlag[]> {
  return (await apiClient.get<Buchungsvorschlag[]>(`${WEG}/buchungsvorschlaege`)).data
}

export async function gibVorschlagFrei(id: string): Promise<KommandoErgebnis> {
  return (
    await apiClient.post<KommandoErgebnis>(`${WEG}/buchungsvorschlaege/${encodeURIComponent(id)}/actions/freigeben`, {
      _mode: 'execute',
      _idempotencyKey: `gutschrift-vorschlag-freigeben-${id}`,
    })
  ).data
}

export async function lehneVorschlagAb(id: string, grund: string): Promise<KommandoErgebnis> {
  return (
    await apiClient.post<KommandoErgebnis>(`${WEG}/buchungsvorschlaege/${encodeURIComponent(id)}/actions/ablehnen`, {
      _mode: 'execute',
      _idempotencyKey: `gutschrift-vorschlag-ablehnen-${id}`,
      _auditReason: grund,
    })
  ).data
}

export async function listeGutschriften(): Promise<Gutschrift[]> {
  return (await apiClient.get<Gutschrift[]>(WEG)).data
}

export async function ladeGutschrift(id: string): Promise<Gutschrift> {
  return (await apiClient.get<Gutschrift>(`${WEG}/${encodeURIComponent(id)}`)).data
}

export async function listeSteuerschluessel(): Promise<Steuerschluessel[]> {
  return (await apiClient.get<Steuerschluessel[]>('/api/v1/finance/tax-keys', { params: { active_only: true } })).data
}

export async function steuerVorschau(lines: GutschriftPosition[]): Promise<SteuerVorschau> {
  return (await apiClient.post<SteuerVorschau>(`${WEG}/steuer-vorschau`, { lines })).data
}

export async function speichereGutschrift(daten: GutschriftEingabe, auftrag: string): Promise<KommandoErgebnis> {
  return (
    await apiClient.post<KommandoErgebnis>(`${WEG}/actions/speichern`, {
      ...daten,
      _mode: 'execute',
      _idempotencyKey: auftrag,
    })
  ).data
}

export async function bucheGutschrift(id: string, auftrag: string): Promise<KommandoErgebnis> {
  return (
    await apiClient.post<KommandoErgebnis>(`${WEG}/${encodeURIComponent(id)}/actions/buchen`, {
      _mode: 'execute',
      _idempotencyKey: auftrag,
    })
  ).data
}
