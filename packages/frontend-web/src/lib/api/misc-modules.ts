/**
 * Misc Module API Hooks
 * Error-first fetching without mock fallback data.
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

export type PlanIstWert = { plan: number; ist: number; abweichung: number }
export type PlanIstBereich = { bereich: string; plan: number; ist: number; abweichung: number }
export type PlanIstData = {
  umsatz: PlanIstWert
  kosten: PlanIstWert
  ertrag: PlanIstWert
  bereiche: PlanIstBereich[]
  periode: string
}

export function usePlanIst(periode?: string) {
  return useQuery({
    queryKey: ['controlling', 'plan-ist', periode],
    queryFn: async () => {
      const params = periode ? `?periode=${periode}` : ''
      return (await apiClient.get<PlanIstData>(`/api/v1/controlling/plan-ist${params}`)).data
    },
    staleTime: 5 * 60 * 1000,
  })
}

export type Tour = { id: string; fahrer: string; stopps: number; km: number; status: 'geplant' | 'unterwegs' | 'abgeschlossen' }
export type TourenData = {
  heute: number
  offen: number
  unterwegs: number
  abgeschlossen: number
  tourenListe: Tour[]
}

export function useTouren() {
  return useQuery({
    queryKey: ['logistik', 'touren'],
    queryFn: async () => (await apiClient.get<TourenData>('/api/v1/logistik/touren')).data,
    staleTime: 30 * 1000,
  })
}

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

export function useFrachtbriefe() {
  return useQuery({
    queryKey: ['logistik', 'frachtbriefe'],
    queryFn: async () => (await apiClient.get<Frachtbrief[]>('/api/v1/logistik/frachtbriefe')).data,
    staleTime: 2 * 60 * 1000,
  })
}

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

export function useReklamationen() {
  return useQuery({
    queryKey: ['qualitaet', 'reklamationen'],
    queryFn: async () => (await apiClient.get<Reklamation[]>('/api/v1/qualitaet/reklamationen')).data,
    staleTime: 2 * 60 * 1000,
  })
}
