import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/futter/einzel/liste",
    "path": "einzel"
  },
  {
    "module": "@/pages/futter/einzel/stamm",
    "path": "einzel/:id"
  },
  {
    "module": "@/pages/futter/misch/liste",
    "path": "misch"
  },
  {
    "module": "@/pages/futter/misch/stamm",
    "path": "misch/:id"
  }
]
