/**
 * Produktion – Mischfutter API Hooks
 * Verfuegbarkeit, Rezepte, Produktionsauftraege.
 */

import { useQuery, useMutation } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────────

export type KomponenteVerfuegbarkeit = {
  name: string
  verfuegbar_t: number
  einheit: string
}

export type RezeptKomponente = {
  name: string
  anteil: number
}

export type Rezept = {
  id: string
  name: string
  code: string
  komponenten: RezeptKomponente[]
}

export type ProduktionsauftragOut = {
  id: string
  chargen_id: string
  rezeptur: string
  menge: number
  status: string
  erstellt: string
}

// ── Hooks ──────────────────────────────────────────────────────────────────

export function useMischfutterVerfuegbarkeit() {
  return useQuery({
    queryKey: ['produktion', 'mischfutter', 'verfuegbarkeit'],
    queryFn: async () =>
      (await apiClient.get<KomponenteVerfuegbarkeit[]>('/api/v1/produktion/mischfutter/verfuegbarkeit')).data,
    initialData: [],
    staleTime: 60 * 1000,
  })
}

export function useMischfutterRezepte() {
  return useQuery({
    queryKey: ['produktion', 'mischfutter', 'rezepte'],
    queryFn: async () =>
      (await apiClient.get<Rezept[]>('/api/v1/produktion/mischfutter/rezepte')).data,
    initialData: [],
    staleTime: 5 * 60 * 1000,
  })
}

export function useCreateProduktionsauftrag() {
  return useMutation({
    mutationFn: async (payload: { rezeptur: string; menge: number; chargen_id?: string }) =>
      (await apiClient.post<ProduktionsauftragOut>('/api/v1/produktion/mischfutter/auftrag', payload)).data,
  })
}
