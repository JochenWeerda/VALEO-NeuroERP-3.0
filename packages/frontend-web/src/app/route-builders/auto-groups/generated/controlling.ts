import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/controlling/benchmark-cockpit",
    "path": "benchmark-cockpit"
  },
  {
    "module": "@/pages/controlling/dashboard-verwaltung",
    "path": "dashboard-verwaltung"
  },
  {
    "module": "@/pages/controlling/kpi-verwaltung",
    "path": "kpi-verwaltung"
  },
  {
    "module": "@/pages/controlling/massnahmen",
    "path": "massnahmen"
  },
  {
    "module": "@/pages/controlling/plan-ist",
    "path": "plan-ist"
  },
  {
    "module": "@/pages/controlling/timeseries-erfassung",
    "path": "timeseries-erfassung"
  },
  {
    "module": "@/pages/controlling/widget-verwaltung",
    "path": "widget-verwaltung"
  }
]
