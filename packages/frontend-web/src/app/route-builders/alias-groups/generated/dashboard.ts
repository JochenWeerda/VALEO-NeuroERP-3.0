import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/dashboard/einkauf-dashboard",
    "path": "einkauf"
  },
  {
    "module": "@/pages/dashboard/sales-dashboard",
    "path": "sales"
  },
  {
    "module": "@/pages/dashboard/customizable",
    "path": "customizable"
  }
]
