import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/analytics",
    "path": ""
  },
  { "module": "@/pages/analytics/analyticsdashboardcharts", "path": "analyticsdashboardcharts" },
  { "module": "@/pages/analytics/charts/inventorybarchart", "path": "charts/inventorybarchart" },
  { "module": "@/pages/analytics/charts/salestrendlinechart", "path": "charts/salestrendlinechart" },
]
