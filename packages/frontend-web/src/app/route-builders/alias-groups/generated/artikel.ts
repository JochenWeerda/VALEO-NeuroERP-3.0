import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/artikel/stamm",
    "path": ":id"
  },
  {
    "module": "@/pages/artikel/stamm",
    "path": "neu"
  },
  {
    "module": "@/pages/artikel/liste",
    "path": ""
  }
]
