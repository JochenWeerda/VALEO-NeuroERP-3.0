import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

/**
 * Kunden-Kontakte (Kontakthistorie + Wiedervorlage) — Kunden-Cockpit.
 * Spiegelt die KONTAKTE-Sicht der Legacy-CRM-Startmaske: Richtung (ein/aus),
 * Art (Telefon/WhatsApp/E-Mail/persönlich/Brief), Kurzinfo, Notiz, Wiedervorlage,
 * Weiterleitung, Bediener, Beleg-Verweis.
 */

export type Kontakt = {
  id: string
  kunden_nr: string
  richtung: 'ein' | 'aus'
  art: 'telefon' | 'whatsapp' | 'email' | 'persoenlich' | 'brief'
  kurzinfo: string | null
  notiz: string | null
  wiedervorlage: string | null
  weiterleitung_an: string | null
  bediener: string | null
  verweis: string | null
  erledigt: boolean
  created_at: string
  kunde?: string | null
}

export type KontaktInput = {
  kunden_nr: string
  richtung?: string
  art?: string
  kurzinfo?: string
  notiz?: string
  wiedervorlage?: string
  weiterleitung_an?: string
  bediener?: string
  verweis?: string
}

const keys = {
  byKunde: (kundenNr: string) => ['kunden-kontakte', kundenNr] as const,
  wvl: (tage: number) => ['kunden-kontakte', 'wvl', tage] as const,
}

export function useKontakte(kundenNr: string | undefined) {
  return useQuery({
    queryKey: keys.byKunde(kundenNr ?? ''),
    queryFn: async () => {
      const res = await apiClient.get<Kontakt[]>(`/api/v1/crm/kunden-kontakte/${encodeURIComponent(kundenNr ?? '')}`)
      return Array.isArray(res.data) ? res.data : []
    },
    enabled: Boolean(kundenNr?.trim()),
  })
}

export function useWiedervorlagen(tage = 14) {
  return useQuery({
    queryKey: keys.wvl(tage),
    queryFn: async () => {
      const res = await apiClient.get<Kontakt[]>('/api/v1/crm/kunden-kontakte/wiedervorlagen', { params: { tage } })
      return Array.isArray(res.data) ? res.data : []
    },
    initialDataUpdatedAt: 0,
  })
}

export function useCreateKontakt() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (input: KontaktInput) => {
      const res = await apiClient.post<Kontakt>('/api/v1/crm/kunden-kontakte', input)
      return res.data
    },
    onSuccess: (k) => {
      void qc.invalidateQueries({ queryKey: keys.byKunde(k.kunden_nr) })
      void qc.invalidateQueries({ queryKey: ['kunden-kontakte', 'wvl'] })
    },
  })
}

export function useErledigtKontakt() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await apiClient.post<Kontakt>(`/api/v1/crm/kunden-kontakte/${encodeURIComponent(id)}/erledigt`, {})
      return res.data
    },
    onSuccess: (k) => {
      if (k?.kunden_nr) void qc.invalidateQueries({ queryKey: keys.byKunde(k.kunden_nr) })
      void qc.invalidateQueries({ queryKey: ['kunden-kontakte', 'wvl'] })
    },
  })
}
