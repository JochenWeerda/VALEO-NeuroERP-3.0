import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/disposition/liste",
    "path": ""
  },
  {
    "module": "@/pages/disposition/LstCommodityPositionMatrix",
    "path": "position-matrix"
  },
  {
    "module": "@/pages/disposition/FrmPositionRules",
    "path": "regeln"
  },
  {
    "module": "@/pages/disposition/FrmCoverageMonitor",
    "path": "coverage-monitor"
  }
]
