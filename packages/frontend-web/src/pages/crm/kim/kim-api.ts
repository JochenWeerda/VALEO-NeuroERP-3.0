/**
 * KIM — Datenadapter: kapselt alle Backend-Aufrufe des 360°-Cockpits.
 * Das Backend (`/api/v1/crm/kim/*`, app/api/v1/endpoints/crm_kim.py) liefert exakt
 * die hier verwendeten Frontend-Typen, daher ist das Mapping identisch.
 */
import { apiClient } from '@/lib/api-client'
import type {
  Customer,
  ContactPerson,
  ContactLog,
  OpenItem,
  BusinessDocument,
} from './types'

const BASE = '/api/v1/crm/kim'

export async function fetchCustomers(limit = 500): Promise<Customer[]> {
  return (await apiClient.get<Customer[]>(`${BASE}/customers`, { params: { limit } })).data
}

export async function fetchCustomer(id: string): Promise<Customer | null> {
  return (await apiClient.get<Customer | null>(`${BASE}/customers/${encodeURIComponent(id)}`)).data
}

export async function updateCustomer(id: string, patch: Partial<Customer>): Promise<{ status: string }> {
  return (await apiClient.put<{ status: string }>(`${BASE}/customers/${encodeURIComponent(id)}`, patch)).data
}

export async function fetchContacts(id: string): Promise<ContactPerson[]> {
  return (await apiClient.get<ContactPerson[]>(`${BASE}/customers/${encodeURIComponent(id)}/contacts`)).data
}

export async function createContact(id: string, cp: Partial<ContactPerson>): Promise<{ status: string }> {
  return (await apiClient.post<{ status: string }>(`${BASE}/customers/${encodeURIComponent(id)}/contacts`, cp)).data
}

export async function fetchLogs(id: string): Promise<ContactLog[]> {
  return (await apiClient.get<ContactLog[]>(`${BASE}/customers/${encodeURIComponent(id)}/logs`)).data
}

export async function createLog(id: string, log: Partial<ContactLog>): Promise<{ status: string }> {
  return (await apiClient.post<{ status: string }>(`${BASE}/customers/${encodeURIComponent(id)}/logs`, log)).data
}

export async function completeLog(logId: string): Promise<{ status: string }> {
  return (await apiClient.put<{ status: string }>(`${BASE}/contact-logs/${encodeURIComponent(logId)}/completed`, {})).data
}

export async function fetchFinancials(id: string): Promise<OpenItem[]> {
  return (await apiClient.get<OpenItem[]>(`${BASE}/customers/${encodeURIComponent(id)}/financials`)).data
}

export async function fetchDocuments(id: string): Promise<BusinessDocument[]> {
  return (await apiClient.get<BusinessDocument[]>(`${BASE}/customers/${encodeURIComponent(id)}/documents`)).data
}

// ── TAPI Click-to-Dial (KIM-L3-BACKEND-001) ──────────────────────────────────
export interface DialResult {
  id: string
  caller: string
  called: string
  kunden_nr?: string | null
  kunde_name?: string | null
  status: string
}

/** Ausgehende Wahl anfordern; die lokale TAPI-Bridge fuehrt sie aus. */
export async function dial(called: string, kundenNr?: string): Promise<DialResult> {
  return (await apiClient.post<DialResult>('/api/v1/crm/tapi/dial', { called, kunden_nr: kundenNr })).data
}

// ── Kontaktbezogene Belegtabs (Rechnungen/Mahnungen/Kontrakte/Strecken) ───────
export interface ContactDoc {
  id: string
  kind: string
  docNo: string
  date: string
  dueDate?: string | null
  amount: number
  status: string
  info?: string | null
}

export type ContactDocKind = 'invoices' | 'dunning' | 'contracts' | 'drop_shipments'

export async function fetchContactDocs(id: string, kind: ContactDocKind): Promise<ContactDoc[]> {
  return (await apiClient.get<ContactDoc[]>(
    `${BASE}/customers/${encodeURIComponent(id)}/contact-docs`, { params: { kind } },
  )).data
}

// ── Benachrichtigungen (internes Postfach + externe Fachberater-Mail) ─────────
export interface CrmNotification {
  id: string
  kunden_nr?: string | null
  sender?: string | null
  recipient: string
  channel: string
  betreff?: string | null
  kommentar?: string | null
  status: string
  created_at?: string | null
}

export async function fetchNotifications(recipient: string, unread = false): Promise<CrmNotification[]> {
  return (await apiClient.get<CrmNotification[]>(
    `${BASE}/notifications`, { params: { recipient, unread } },
  )).data
}

export async function markNotificationRead(id: string): Promise<CrmNotification> {
  return (await apiClient.post<CrmNotification>(`${BASE}/notifications/${encodeURIComponent(id)}/read`, {})).data
}

// ── Kunden-Präsente (KIM-S3) ──────────────────────────────────────────────────
export interface CustomerGift {
  id: string
  kunden_nr: string
  contact_id?: string | null
  year: number
  gift_date?: string | null
  occasion?: string | null
  gift_name?: string | null
  quantity: number
  sales_rep?: string | null
  operator?: string | null
  representative_officer?: string | null
  sequence_number?: number | null
}

export interface GiftInput {
  year: number
  date?: string
  occasion?: string
  contactId?: string
  giftName?: string
  quantity?: number
  salesRepId?: string
  operatorId?: string
  representativeOfficerId?: string
  sequenceNumber?: number
}

export async function fetchGifts(id: string, year?: number, contactId?: string): Promise<CustomerGift[]> {
  const params: Record<string, unknown> = {}
  if (year != null) params.year = year
  if (contactId) params.contactId = contactId
  return (await apiClient.get<CustomerGift[]>(`${BASE}/customers/${encodeURIComponent(id)}/gifts`, { params })).data
}

export async function createGift(id: string, gift: GiftInput): Promise<CustomerGift> {
  return (await apiClient.post<CustomerGift>(`${BASE}/customers/${encodeURIComponent(id)}/gifts`, gift)).data
}

export async function updateGift(giftId: string, gift: GiftInput): Promise<CustomerGift> {
  return (await apiClient.put<CustomerGift>(`${BASE}/gifts/${encodeURIComponent(giftId)}`, gift)).data
}

export async function deleteGift(giftId: string): Promise<void> {
  await apiClient.delete(`${BASE}/gifts/${encodeURIComponent(giftId)}`)
}

export interface NeuroSummary {
  healthScore: number
  statusLabel: string
  summary: string
  opportunities: string[]
  risks: string[]
}

/** NeuroAI-Dossier über das anbieterunabhängige LLM-Gateway (mit Backend-Fallback). */
export async function fetchNeuroSummary(id: string): Promise<NeuroSummary | null> {
  try {
    return (await apiClient.post<NeuroSummary>(`${BASE}/neuro-summary`, { customerId: id })).data
  } catch {
    return null
  }
}

export interface DraftEmail {
  subject: string
  body: string
  engine?: string
}

/** NeuroComms E-Mail-Entwurf (LLM-Gateway + Backend-Fallback). */
export async function draftEmail(id: string, tone: string): Promise<DraftEmail> {
  return (await apiClient.post<DraftEmail>(`${BASE}/draft-email`, { customerId: id, tone })).data
}
