/**
 * Sales API Hooks
 * TanStack Query hooks for Verkauf (Orders, Offers, Deliveries, Invoices)
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────

export type AuftragStatus = 'offen' | 'teilgeliefert' | 'geliefert' | 'fakturiert' | 'storniert'
export type AngebotStatus = 'offen' | 'angenommen' | 'abgelehnt' | 'abgelaufen'
export type LieferungStatus = 'geplant' | 'unterwegs' | 'zugestellt' | 'storniert'
export type RechnungStatus = 'offen' | 'teilbezahlt' | 'bezahlt' | 'ueberfaellig' | 'storniert'

export type Auftrag = {
  id: string
  nummer: string
  datum: string
  kunde: string
  betrag: number
  status: AuftragStatus
  liefertermin: string
}

export type Angebot = {
  id: string
  nummer: string
  datum: string
  kunde: string
  betrag: number
  status: AngebotStatus
  gueltigBis: string
}

export type Lieferung = {
  id: string
  nummer: string
  datum: string
  kunde: string
  auftragsNr: string
  menge: number
  status: LieferungStatus
}

export type Rechnung = {
  id: string
  nummer: string
  datum: string
  kunde: string
  auftragsNr: string
  betrag: number
  faelligAm: string
  status: RechnungStatus
}

// ── Query Keys ─────────────────────────────────────────────────────────

export const salesKeys = {
  all: ['sales'] as const,
  auftraege: (filters?: Record<string, unknown>) => [...salesKeys.all, 'auftraege', filters] as const,
  angebote: (filters?: Record<string, unknown>) => [...salesKeys.all, 'angebote', filters] as const,
  lieferungen: (filters?: Record<string, unknown>) => [...salesKeys.all, 'lieferungen', filters] as const,
  rechnungen: (filters?: Record<string, unknown>) => [...salesKeys.all, 'rechnungen', filters] as const,
}

// ── Fallback Data ──────────────────────────────────────────────────────

const fallbackAuftraege: Auftrag[] = [
  { id: '1', nummer: 'SO-2026-0001', datum: '2026-01-08', kunde: 'Landhandel Nord GmbH', betrag: 12500.0, status: 'teilgeliefert', liefertermin: '2026-02-15' },
  { id: '2', nummer: 'SO-2026-0002', datum: '2026-01-09', kunde: 'Agrar-Zentrum Süd', betrag: 8750.5, status: 'geliefert', liefertermin: '2026-01-12' },
  { id: '3', nummer: 'SO-2026-0003', datum: '2026-01-10', kunde: 'Müller Landwirtschaft', betrag: 5200.0, status: 'offen', liefertermin: '2026-02-20' },
]

const fallbackAngebote: Angebot[] = [
  { id: '1', nummer: 'ANG-2026-001', datum: '2026-01-08', kunde: 'Landhandel Nord GmbH', betrag: 12500.0, status: 'offen', gueltigBis: '2026-02-07' },
  { id: '2', nummer: 'ANG-2026-002', datum: '2026-01-09', kunde: 'Agrar-Zentrum Süd', betrag: 8750.5, status: 'angenommen', gueltigBis: '2026-02-08' },
  { id: '3', nummer: 'ANG-2026-003', datum: '2026-01-10', kunde: 'Müller Landwirtschaft', betrag: 5200.0, status: 'offen', gueltigBis: '2026-02-09' },
]

const fallbackLieferungen: Lieferung[] = [
  { id: '1', nummer: 'LF-2026-0001', datum: '2026-02-11', kunde: 'Landhandel Nord GmbH', auftragsNr: 'SO-2026-0001', menge: 25, status: 'unterwegs' },
  { id: '2', nummer: 'LF-2026-0002', datum: '2026-02-10', kunde: 'Agrar-Zentrum Süd', auftragsNr: 'SO-2026-0002', menge: 15, status: 'zugestellt' },
  { id: '3', nummer: 'LF-2026-0003', datum: '2026-02-12', kunde: 'Müller Landwirtschaft', auftragsNr: 'SO-2026-0003', menge: 10, status: 'geplant' },
]

const fallbackRechnungen: Rechnung[] = [
  { id: '1', nummer: 'RE-2026-0001', datum: '2026-02-11', kunde: 'Landhandel Nord GmbH', auftragsNr: 'SO-2026-0001', betrag: 12500.0, faelligAm: '2026-03-13', status: 'offen' },
  { id: '2', nummer: 'RE-2026-0002', datum: '2026-02-10', kunde: 'Agrar-Zentrum Süd', auftragsNr: 'SO-2026-0002', betrag: 8750.5, faelligAm: '2026-03-12', status: 'bezahlt' },
  { id: '3', nummer: 'RE-2026-0003', datum: '2026-01-15', kunde: 'Müller Landwirtschaft', auftragsNr: 'SO-2025-0890', betrag: 5200.0, faelligAm: '2026-02-14', status: 'ueberfaellig' },
]

// ── Transform helpers ──────────────────────────────────────────────────

function transformMCPAuftrag(doc: any): Auftrag {
  return {
    id: doc.number ?? doc.id,
    nummer: doc.number,
    datum: doc.date,
    kunde: doc.customerId ?? '',
    betrag: doc.totalGross ?? 0,
    status: (doc.status?.toLowerCase() ?? 'offen') as AuftragStatus,
    liefertermin: doc.deliveryDate ?? '',
  }
}

function transformMCPAngebot(doc: any): Angebot {
  return {
    id: doc.number ?? doc.id,
    nummer: doc.number,
    datum: doc.date,
    kunde: doc.customerId ?? '',
    betrag: doc.totalGross ?? 0,
    status: (doc.status?.toLowerCase() ?? 'offen') as AngebotStatus,
    gueltigBis: doc.validUntil ?? '',
  }
}

function transformMCPLieferung(doc: any): Lieferung {
  return {
    id: doc.number ?? doc.id,
    nummer: doc.number,
    datum: doc.date,
    kunde: doc.customerId ?? '',
    auftragsNr: doc.sourceOrder ?? '',
    menge: doc.lines?.reduce((sum: number, line: any) => sum + (line.qty ?? 0), 0) ?? 0,
    status: (doc.status?.toLowerCase() ?? 'geplant') as LieferungStatus,
  }
}

function transformMCPRechnung(doc: any): Rechnung {
  return {
    id: doc.number ?? doc.id,
    nummer: doc.number,
    datum: doc.date,
    kunde: doc.customerId ?? '',
    auftragsNr: doc.sourceOrder ?? '',
    betrag: doc.totalGross ?? 0,
    faelligAm: doc.dueDate ?? '',
    status: (doc.status?.toLowerCase() ?? 'offen') as RechnungStatus,
  }
}

// ── Generic MCP document fetcher ───────────────────────────────────────

async function fetchMCPDocuments<T>(
  docType: string,
  transform: (doc: any) => T,
  fallback: T[],
): Promise<T[]> {
  // Try new API first
  try {
    const response = await apiClient.get<{ data: T[] }>(`/api/v1/sales/${docType}`)
    if (response.data?.data?.length) return response.data.data
  } catch { /* try MCP fallback */ }

  // Try legacy MCP API
  try {
    const response = await fetch(`/api/mcp/documents/${docType}?skip=0&limit=100`)
    if (response.ok) {
      const result = await response.json()
      if (result.ok && result.data?.length) {
        return result.data.map(transform)
      }
    }
  } catch { /* use fallback */ }

  return fallback
}

// ── Hooks ──────────────────────────────────────────────────────────────

export function useAuftraege(filters?: { status?: AuftragStatus; search?: string }) {
  return useQuery({
    queryKey: salesKeys.auftraege(filters),
    queryFn: () => fetchMCPDocuments('sales_order', transformMCPAuftrag, fallbackAuftraege),
    staleTime: 2 * 60 * 1000,
    select: (data) => {
      let items = data
      if (filters?.status) items = items.filter(a => a.status === filters.status)
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter(a => a.nummer.toLowerCase().includes(s) || a.kunde.toLowerCase().includes(s))
      }
      return items
    },
  })
}

export function useAngebote(filters?: { status?: AngebotStatus; search?: string }) {
  return useQuery({
    queryKey: salesKeys.angebote(filters),
    queryFn: () => fetchMCPDocuments('sales_offer', transformMCPAngebot, fallbackAngebote),
    staleTime: 2 * 60 * 1000,
    select: (data) => {
      let items = data
      if (filters?.status) items = items.filter(a => a.status === filters.status)
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter(a => a.nummer.toLowerCase().includes(s) || a.kunde.toLowerCase().includes(s))
      }
      return items
    },
  })
}

export function useLieferungen(filters?: { status?: LieferungStatus; search?: string }) {
  return useQuery({
    queryKey: salesKeys.lieferungen(filters),
    queryFn: () => fetchMCPDocuments('sales_delivery', transformMCPLieferung, fallbackLieferungen),
    staleTime: 2 * 60 * 1000,
    select: (data) => {
      let items = data
      if (filters?.status) items = items.filter(l => l.status === filters.status)
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter(l => l.nummer.toLowerCase().includes(s) || l.kunde.toLowerCase().includes(s) || l.auftragsNr.toLowerCase().includes(s))
      }
      return items
    },
  })
}

export function useRechnungen(filters?: { status?: RechnungStatus; search?: string }) {
  return useQuery({
    queryKey: salesKeys.rechnungen(filters),
    queryFn: () => fetchMCPDocuments('sales_invoice', transformMCPRechnung, fallbackRechnungen),
    staleTime: 2 * 60 * 1000,
    select: (data) => {
      let items = data
      if (filters?.status) items = items.filter(r => r.status === filters.status)
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter(r => r.nummer.toLowerCase().includes(s) || r.kunde.toLowerCase().includes(s) || r.auftragsNr.toLowerCase().includes(s))
      }
      return items
    },
  })
}
