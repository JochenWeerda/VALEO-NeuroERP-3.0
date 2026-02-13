/**
 * Sales API Hooks
 * TanStack Query hooks for Verkauf (Orders, Offers, Deliveries, Invoices)
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

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
  totalNutrientNKg?: number
  totalNutrientP2o5Kg?: number
  totalCo2eKg?: number
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

export const salesKeys = {
  all: ['sales'] as const,
  auftraege: (filters?: Record<string, unknown>) => [...salesKeys.all, 'auftraege', filters] as const,
  angebote: (filters?: Record<string, unknown>) => [...salesKeys.all, 'angebote', filters] as const,
  lieferungen: (filters?: Record<string, unknown>) => [...salesKeys.all, 'lieferungen', filters] as const,
  rechnungen: (filters?: Record<string, unknown>) => [...salesKeys.all, 'rechnungen', filters] as const,
}

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
    totalNutrientNKg: doc.totalNutrientNKg ?? 0,
    totalNutrientP2o5Kg: doc.totalNutrientP2o5Kg ?? 0,
    totalCo2eKg: doc.totalCo2eKg ?? 0,
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

async function fetchMCPDocuments<T>(docType: string, transform: (doc: any) => T): Promise<T[]> {
  try {
    const response = await apiClient.get<{ data: T[] }>(`/api/v1/sales/${docType}`)
    return response.data.data
  } catch {
    const response = await fetch(`/api/mcp/documents/${docType}?skip=0&limit=100`)
    if (!response.ok) {
      throw new Error(`Failed to fetch ${docType}: ${response.status}`)
    }

    const result = await response.json()
    if (!result.ok) {
      throw new Error(`MCP fetch for ${docType} returned not ok`)
    }

    return (result.data ?? []).map(transform)
  }
}

export function useAuftraege(filters?: { status?: AuftragStatus; search?: string }) {
  return useQuery({
    queryKey: salesKeys.auftraege(filters),
    queryFn: () => fetchMCPDocuments('sales_order', transformMCPAuftrag),
    staleTime: 2 * 60 * 1000,
    select: (data) => {
      let items = data
      if (filters?.status) items = items.filter((a) => a.status === filters.status)
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter((a) => a.nummer.toLowerCase().includes(s) || a.kunde.toLowerCase().includes(s))
      }
      return items
    },
  })
}

export function useAngebote(filters?: { status?: AngebotStatus; search?: string }) {
  return useQuery({
    queryKey: salesKeys.angebote(filters),
    queryFn: () => fetchMCPDocuments('sales_offer', transformMCPAngebot),
    staleTime: 2 * 60 * 1000,
    select: (data) => {
      let items = data
      if (filters?.status) items = items.filter((a) => a.status === filters.status)
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter((a) => a.nummer.toLowerCase().includes(s) || a.kunde.toLowerCase().includes(s))
      }
      return items
    },
  })
}

export function useLieferungen(filters?: { status?: LieferungStatus; search?: string }) {
  return useQuery({
    queryKey: salesKeys.lieferungen(filters),
    queryFn: () => fetchMCPDocuments('sales_delivery', transformMCPLieferung),
    staleTime: 2 * 60 * 1000,
    select: (data) => {
      let items = data
      if (filters?.status) items = items.filter((l) => l.status === filters.status)
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter(
          (l) =>
            l.nummer.toLowerCase().includes(s) ||
            l.kunde.toLowerCase().includes(s) ||
            l.auftragsNr.toLowerCase().includes(s),
        )
      }
      return items
    },
  })
}

export function useRechnungen(filters?: { status?: RechnungStatus; search?: string }) {
  return useQuery({
    queryKey: salesKeys.rechnungen(filters),
    queryFn: () => fetchMCPDocuments('sales_invoice', transformMCPRechnung),
    staleTime: 2 * 60 * 1000,
    select: (data) => {
      let items = data
      if (filters?.status) items = items.filter((r) => r.status === filters.status)
      if (filters?.search) {
        const s = filters.search.toLowerCase()
        items = items.filter(
          (r) =>
            r.nummer.toLowerCase().includes(s) ||
            r.kunde.toLowerCase().includes(s) ||
            r.auftragsNr.toLowerCase().includes(s),
        )
      }
      return items
    },
  })
}
