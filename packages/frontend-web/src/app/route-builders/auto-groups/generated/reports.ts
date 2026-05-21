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
  { "module": "@/pages/reports/charts/customeranalyticscharts", "path": "charts/customeranalyticscharts" },
  { "module": "@/pages/reports/charts/financialanalyticscharts", "path": "charts/financialanalyticscharts" },
  { "module": "@/pages/reports/charts/productanalyticscharts", "path": "charts/productanalyticscharts" },
  { "module": "@/pages/reports/charts/salesperformancecharts", "path": "charts/salesperformancecharts" },
  { "module": "@/pages/reports/charts/trendanalyticscharts", "path": "charts/trendanalyticscharts" },
]
