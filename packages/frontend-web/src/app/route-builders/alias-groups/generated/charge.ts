import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/charge/liste",
    "path": "liste"
  },
  {
    "module": "@/pages/charge/stamm",
    "path": "stamm/:id"
  },
  {
    "module": "@/pages/charge/stamm",
    "path": "stamm"
  },
  {
    "module": "@/pages/charge/wareneingang",
    "path": "wareneingang"
  },
  {
    "module": "@/pages/charge/rueckverfolgung",
    "path": "rueckverfolgung"
  }
]
