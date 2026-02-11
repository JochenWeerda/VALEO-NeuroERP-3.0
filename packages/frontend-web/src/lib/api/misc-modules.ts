/**
 * Misc Module API Hooks
 * TanStack Query hooks for Controlling, Logistik, Qualität
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Controlling: Plan-Ist ──────────────────────────────────────────────

export type PlanIstWert = { plan: number; ist: number; abweichung: number }
export type PlanIstBereich = { bereich: string; plan: number; ist: number; abweichung: number }
export type PlanIstData = {
  umsatz: PlanIstWert
  kosten: PlanIstWert
  ertrag: PlanIstWert
  bereiche: PlanIstBereich[]
  periode: string
}

const fallbackPlanIst: PlanIstData = {
  umsatz: { plan: 1200000, ist: 1250000, abweichung: 4.2 },
  kosten: { plan: 850000, ist: 820000, abweichung: -3.5 },
  ertrag: { plan: 350000, ist: 430000, abweichung: 22.9 },
  bereiche: [
    { bereich: 'Verkauf Getreide', plan: 480000, ist: 525000, abweichung: 9.4 },
    { bereich: 'Verkauf Saatgut', plan: 320000, ist: 295000, abweichung: -7.8 },
    { bereich: 'Verkauf Dünger', plan: 280000, ist: 310000, abweichung: 10.7 },
    { bereich: 'Verkauf Futter', plan: 120000, ist: 120000, abweichung: 0.0 },
  ],
  periode: new Date().toLocaleDateString('de-DE', { month: 'long', year: 'numeric' }),
}

export function usePlanIst(periode?: string) {
  return useQuery({
    queryKey: ['controlling', 'plan-ist', periode],
    queryFn: async () => {
      try {
        const params = periode ? `?periode=${periode}` : ''
        const response = await apiClient.get<PlanIstData>(`/api/v1/controlling/plan-ist${params}`)
        if (response.data) return response.data
      } catch { /* fallback */ }
      return fallbackPlanIst
    },
    staleTime: 5 * 60 * 1000,
  })
}

// ── Logistik: Touren ───────────────────────────────────────────────────

export type Tour = { id: string; fahrer: string; stopps: number; km: number; status: 'geplant' | 'unterwegs' | 'abgeschlossen' }
export type TourenData = {
  heute: number
  offen: number
  unterwegs: number
  abgeschlossen: number
  tourenListe: Tour[]
}

const fallbackTouren: TourenData = {
  heute: 12, offen: 5, unterwegs: 4, abgeschlossen: 3,
  tourenListe: [
    { id: 'T-001', fahrer: 'Schmidt', stopps: 5, km: 85, status: 'unterwegs' },
    { id: 'T-002', fahrer: 'Müller', stopps: 3, km: 45, status: 'geplant' },
    { id: 'T-003', fahrer: 'Weber', stopps: 7, km: 120, status: 'abgeschlossen' },
  ],
}

export function useTouren() {
  return useQuery({
    queryKey: ['logistik', 'touren'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<TourenData>('/api/v1/logistik/touren')
        if (response.data?.tourenListe) return response.data
      } catch { /* fallback */ }
      return fallbackTouren
    },
    staleTime: 30 * 1000,
  })
}

// ── Logistik: Frachtbriefe ─────────────────────────────────────────────

export type Frachtbrief = {
  id: string
  nummer: string
  kennzeichen: string
  artikel: string
  menge: number
  absender: string
  empfaenger: string
  datum: string
  status: 'erstellt' | 'unterwegs' | 'zugestellt'
}

const fallbackFrachtbriefe: Frachtbrief[] = [
  { id: '1', nummer: 'FB-2026-042', kennzeichen: 'AB-CD 1234', artikel: 'Weizen', menge: 25.0, absender: 'VALEO Landhandel', empfaenger: 'Mühle Nord', datum: '2026-02-11', status: 'unterwegs' },
  { id: '2', nummer: 'FB-2026-043', kennzeichen: 'EF-GH 5678', artikel: 'Raps', menge: 18.5, absender: 'VALEO Landhandel', empfaenger: 'Ölmühle Süd', datum: '2026-02-11', status: 'erstellt' },
]

export function useFrachtbriefe() {
  return useQuery({
    queryKey: ['logistik', 'frachtbriefe'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<Frachtbrief[]>('/api/v1/logistik/frachtbriefe')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackFrachtbriefe
    },
    staleTime: 2 * 60 * 1000,
  })
}

// ── Qualität: Reklamationen ────────────────────────────────────────────

export type Reklamation = {
  id: string
  nummer: string
  kunde: string
  artikel: string
  grund: string
  datum: string
  prioritaet: 'hoch' | 'normal' | 'niedrig'
  status: 'neu' | 'in-bearbeitung' | 'geloest' | 'abgelehnt'
}

const fallbackReklamationen: Reklamation[] = [
  { id: '1', nummer: 'REK-2026-001', kunde: 'Landhandel Nord', artikel: 'Weizen', grund: 'Feuchtigkeit zu hoch', datum: '2026-02-11', prioritaet: 'hoch', status: 'neu' },
  { id: '2', nummer: 'REK-2026-002', kunde: 'Müller GmbH', artikel: 'Sojaschrot', grund: 'Falsche Menge', datum: '2026-02-10', prioritaet: 'normal', status: 'in-bearbeitung' },
]

export function useReklamationen() {
  return useQuery({
    queryKey: ['qualitaet', 'reklamationen'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<Reklamation[]>('/api/v1/qualitaet/reklamationen')
        if (response.data?.length) return response.data
      } catch { /* fallback */ }
      return fallbackReklamationen
    },
    staleTime: 2 * 60 * 1000,
  })
}
