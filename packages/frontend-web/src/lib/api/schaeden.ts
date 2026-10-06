/**
 * Schaeden (Schadenmeldungen) API Client
 * TanStack Query Hooks für Schadenmeldung und Versicherungen
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

// ========== TYPES ==========

export type Versicherung = {
  id: string
  bezeichnung: string
  vertragsnummer: string
  typ: string
  versicherer: string
  gueltig_von?: string | null
  gueltig_bis?: string | null
  /** Frist zur Schadenanzeige; steht am Vertrag, weil sie je Police gilt. */
  meldefrist_tage?: number | null
  ansprechpartner?: string | null
  kontakt?: string | null
}

export type SchadenMeldungCreate = {
  art: string
  /** Hieß bis 06.10.2026 `datum` — die Spalte heißt `schadendatum`. */
  schadendatum: string
  ort?: string
  beschreibung: string
  schadenhoehe: number
  versicherung_id?: string
  zeuge?: string
  erfasst_durch?: string
}

/**
 * Eine Schadenmeldung.
 *
 * Bis zum 06.10.2026 antwortete das Anlegen `status: "gemeldet"` und schrieb
 * nichts; die Liste gab eine erfundene Hagelschadenmeldung zurück. Das Erfassen
 * erzeugt jetzt einen **Entwurf**: Es gibt keinen Versandweg zum Versicherer, und
 * das System darf nicht behaupten, er sei unterrichtet. Das Melden ist ein
 * eigener Schritt (`useMeldungMelden`), der festhält, wann, durch wen und auf
 * welchem Weg.
 */
export type SchadenMeldungResponse = {
  id: string
  tenant_id: string
  meldungsnummer: string
  art: string
  schadendatum?: string | null
  ort?: string | null
  beschreibung: string
  schadenhoehe: number | string
  versicherung_id?: string | null
  zeuge?: string | null
  status: 'ENTWURF' | 'GEMELDET' | 'IN_BEARBEITUNG' | 'REGULIERT' | 'ABGELEHNT'
  gemeldet_am?: string | null
  gemeldet_durch?: string | null
  meldeweg?: string | null
  regulierungsbetrag?: number | string | null
  abgelehnt_grund?: string | null
  /** Abgeleitet aus der Frist des Vertrags, nicht gespeichert. */
  meldefrist_tage?: number | null
  melden_bis?: string | null
  frist_ueberschritten: boolean
  created_at?: string | null
  updated_at?: string | null
}

export type MeldungMelden = {
  meldeweg: 'TELEFON' | 'EMAIL' | 'POST' | 'FAX' | 'PORTAL' | 'PERSOENLICH'
  gemeldet_durch?: string
  gemeldet_am?: string
}

// ========== QUERY KEYS ==========

export const schaedenKeys = {
  all: ['schaeden'] as const,
  versicherungen: () => [...schaedenKeys.all, 'versicherungen'] as const,
  meldungen: () => [...schaedenKeys.all, 'meldungen'] as const,
}

// ========== HOOKS ==========

export function useVersicherungen() {
  return useQuery({
    queryKey: schaedenKeys.versicherungen(),
    queryFn: async () => {
      const response = await apiClient.get<Versicherung[]>('/api/v1/schaeden/versicherungen')
      return response.data
    },
    initialData: [],
  })
}

export function useSchadenMeldungErstellen() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: SchadenMeldungCreate) => {
      const response = await apiClient.post<SchadenMeldungResponse>(
        '/api/v1/schaeden/meldungen',
        data,
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: schaedenKeys.meldungen() })
    },
  })
}
