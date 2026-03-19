import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/waage/liste",
    "path": ""
  },
  {
    "module": "@/pages/waage/hofliste",
    "path": "hofliste"
  },
  {
    "module": "@/pages/waage/wiegeschein-detail",
    "path": "wiegeschein/:id"
  },
  {
    "module": "@/pages/waage/wiegungen",
    "path": "wiegungen"
  }
]
