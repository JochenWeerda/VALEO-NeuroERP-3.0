import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/reports",
    "path": ""
  },
  {
    "module": "@/pages/reports/deckungsbeitrag",
    "path": "deckungsbeitrag"
  },
  {
    "module": "@/pages/reports/lagerbestand",
    "path": "lagerbestand"
  },
  {
    "module": "@/pages/reports/ReportsDashboardCharts",
    "path": "ReportsDashboardCharts"
  },
  {
    "module": "@/pages/reports/umsatz",
    "path": "umsatz"
  },
]
