import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * WhatsApp Bestell-Inbox: eingehende Freitext-Bestellungen (Copy-Paste) → AI-Extraktion
 * (Claude, mit Heuristik-Fallback) → Verkäufer-Bestätigung → Kontakt + Beleg-Vorbelegung.
 */

export type BestellPosition = {
  artikel: string | null
  menge: number | null
  einheit: string | null
  silo: string | null
  preis: number | null
  match_article_number?: string | null
  match_name?: string | null
}

export type ParsedBestellung = {
  kunde: string | null
  ort: string | null
  positionen: BestellPosition[]
  termin: string | null
  logistik: string | null
  wie_letztes_mal: boolean
  notiz: string | null
  match_kunde?: { kunden_nr: string; name: string; plz: string | null; ort: string | null } | null
}

export type InboxItem = {
  id: string
  raw_text: string
  absender: string | null
  quelle: string
  eingegangen_am: string
  status: 'neu' | 'geparst' | 'bestaetigt' | 'verworfen'
  parsed: ParsedBestellung | null
  kunden_nr: string | null
  kunde_text: string | null
  beleg_typ: string | null
  beleg_ref: string | null
  engine: string | null
  confidence: number | null
}

const keys = {
  list: (status: string) => ['bestell-inbox', status] as const,
}

export function useInbox(status = '') {
  return useQuery({
    queryKey: keys.list(status),
    queryFn: async () => {
      const res = await apiClient.get<InboxItem[]>('/api/v1/crm/bestell-inbox', {
        params: status ? { status } : {},
      })
      return Array.isArray(res.data) ? res.data : []
    },
    initialDataUpdatedAt: 0,
  })
}

export function useCreateIntake() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { raw_text: string; absender?: string; quelle?: string }) => {
      const res = await apiClient.post<InboxItem>('/api/v1/crm/bestell-inbox', input)
      return res.data
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['bestell-inbox'] }) },
  })
}

export function useBestaetigen() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: { id: string; kunden_nr?: string; beleg_typ: string; parsed?: ParsedBestellung }) => {
      const { id, ...body } = input
      const res = await apiClient.post<InboxItem>(`/api/v1/crm/bestell-inbox/${encodeURIComponent(id)}/bestaetigen`, body)
      return res.data
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['bestell-inbox'] }) },
  })
}

export function useVerwerfen() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await apiClient.post<InboxItem>(`/api/v1/crm/bestell-inbox/${encodeURIComponent(id)}/verwerfen`, {})
      return res.data
    },
    onSuccess: () => { void qc.invalidateQueries({ queryKey: ['bestell-inbox'] }) },
  })
}
