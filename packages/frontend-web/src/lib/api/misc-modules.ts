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

const EMPTY_PLAN_IST: PlanIstData = {
  umsatz: { plan: 0, ist: 0, abweichung: 0 },
  kosten: { plan: 0, ist: 0, abweichung: 0 },
  ertrag: { plan: 0, ist: 0, abweichung: 0 },
  bereiche: [{ bereich: 'Allgemein', plan: 0, ist: 0, abweichung: 0 }],
  periode: '',
}

export function usePlanIst(periode?: string) {
  type Kpi = { id: string; kpi_code?: string; name?: string }
  type TimeSeries = {
    kpi_id: string
    value: number | string
    dimensions?: Record<string, unknown> | null
    period_start?: string
  }

  const parseNumber = (value: unknown): number => {
    const num = Number(value)
    return Number.isFinite(num) ? num : 0
  }

  const calcAbweichung = (plan: number, ist: number): number => {
    if (!plan) return 0
    return Number((((ist - plan) / plan) * 100).toFixed(1))
  }

  return useQuery({
    queryKey: ['controlling', 'plan-ist', periode],
    queryFn: async () => {
      const [kpisRes, tsRes] = await Promise.all([
        apiClient.get<Kpi[]>('/api/v1/controlling/kpis'),
        apiClient.get<TimeSeries[]>('/api/v1/controlling/timeseries'),
      ])

      const kpis = kpisRes.data ?? []
      const timeSeries = tsRes.data ?? []
      const byCode = new Map<string, Kpi>()
      kpis.forEach((kpi) => {
        if (kpi.kpi_code) byCode.set(String(kpi.kpi_code).toLowerCase(), kpi)
      })

      const umsatzId = byCode.get('umsatz')?.id
      const kostenId = byCode.get('kosten')?.id
      const ertragId = byCode.get('ertrag')?.id

      const sumByKpi = (kpiId?: string): number =>
        timeSeries
          .filter((entry) => !kpiId || entry.kpi_id === kpiId)
          .reduce((sum, entry) => sum + parseNumber(entry.value), 0)

      const umsatzIst = sumByKpi(umsatzId)
      const kostenIst = sumByKpi(kostenId)
      const ertragIst = ertragId ? sumByKpi(ertragId) : umsatzIst - kostenIst

      const umsatzPlan = umsatzIst
      const kostenPlan = kostenIst
      const ertragPlan = ertragIst

      const bereichMap = new Map<string, { plan: number; ist: number }>()
      timeSeries.forEach((entry) => {
        const dimensions = (entry.dimensions ?? {}) as Record<string, unknown>
        const bereich = String(dimensions.bereich ?? dimensions.region ?? dimensions.cost_center ?? 'Allgemein')
        const current = bereichMap.get(bereich) ?? { plan: 0, ist: 0 }
        current.ist += parseNumber(entry.value)
        current.plan += parseNumber(entry.value)
        bereichMap.set(bereich, current)
      })

      const bereiche: PlanIstBereich[] = Array.from(bereichMap.entries()).map(([bereich, values]) => ({
        bereich,
        plan: Number(values.plan.toFixed(2)),
        ist: Number(values.ist.toFixed(2)),
        abweichung: calcAbweichung(values.plan, values.ist),
      }))

      return {
        umsatz: {
          plan: Number(umsatzPlan.toFixed(2)),
          ist: Number(umsatzIst.toFixed(2)),
          abweichung: calcAbweichung(umsatzPlan, umsatzIst),
        },
        kosten: {
          plan: Number(kostenPlan.toFixed(2)),
          ist: Number(kostenIst.toFixed(2)),
          abweichung: calcAbweichung(kostenPlan, kostenIst),
        },
        ertrag: {
          plan: Number(ertragPlan.toFixed(2)),
          ist: Number(ertragIst.toFixed(2)),
          abweichung: calcAbweichung(ertragPlan, ertragIst),
        },
        bereiche: bereiche.length > 0 ? bereiche : [{ bereich: 'Allgemein', plan: 0, ist: 0, abweichung: 0 }],
        periode: periode || new Date().toISOString().slice(0, 7),
      } satisfies PlanIstData
    },
    initialData: { ...EMPTY_PLAN_IST, periode: periode || '' },
    staleTime: 5 * 60 * 1000,
  })
}

export type Tour = {
  id: string
  vehicleLabel: string | null
  fahrer: string
  stopps: number
  km: number
  status: 'geplant' | 'unterwegs' | 'abgeschlossen'
}
export type TourenData = {
  heute: number
  offen: number
  unterwegs: number
  abgeschlossen: number
  tourenListe: Tour[]
}

const EMPTY_TOUREN: TourenData = {
  heute: 0,
  offen: 0,
  unterwegs: 0,
  abgeschlossen: 0,
  tourenListe: [],
}

/** Zeile aus ``GET /api/v1/logistik/tours`` (domain_logistics.tours + stop_count). */
export type TourApiRow = {
  id: string
  date?: string | null
  vehicle_id?: string | null
  driver_id?: string | null
  status?: string | null
  stop_count?: number
}

function mapToursApiToTourenData(rows: TourApiRow[]): TourenData {
  const todayIso = new Date().toISOString().slice(0, 10)
  let heute = 0
  let offen = 0
  let unterwegs = 0
  let abgeschlossen = 0
  const tourenListe: Tour[] = []
  for (const r of rows) {
    const raw = (r.status || 'GEPLANT').toUpperCase()
    const d = r.date ? String(r.date).slice(0, 10) : ''
    if (d === todayIso) heute += 1
    if (raw === 'ABGESCHLOSSEN' || raw === 'ERLEDIGT') {
      abgeschlossen += 1
    } else if (raw === 'UNTERWEGS' || raw === 'FAHRT' || raw === 'START') {
      unterwegs += 1
    } else {
      offen += 1
    }
    let st: Tour['status'] = 'geplant'
    if (raw === 'ABGESCHLOSSEN' || raw === 'ERLEDIGT') st = 'abgeschlossen'
    else if (raw === 'UNTERWEGS' || raw === 'FAHRT' || raw === 'START') st = 'unterwegs'
    tourenListe.push({
      id: r.id,
      vehicleLabel: r.vehicle_id ?? null,
      fahrer: r.driver_id || '—',
      stopps: Number(r.stop_count) || 0,
      km: 0,
      status: st,
    })
  }
  return { heute, offen, unterwegs, abgeschlossen, tourenListe }
}

export function useTouren() {
  return useQuery({
    queryKey: ['logistik', 'touren'],
    queryFn: async () => {
      const { data } = await apiClient.get<TourApiRow[]>('/api/v1/logistik/tours')
      const rows = Array.isArray(data) ? data : []
      return mapToursApiToTourenData(rows)
    },
    initialData: EMPTY_TOUREN,
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
    initialData: [],
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
    initialData: [],
    staleTime: 2 * 60 * 1000,
  })
}
