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
