import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/fuhrpark/fahrzeug-stamm",
    "path": "fahrzeug/neu"
  },
  {
    "module": "@/pages/fuhrpark/fahrzeug-stamm",
    "path": "fahrzeug/:id"
  },
  {
    "module": "@/pages/fuhrpark/fahrzeuge",
    "path": "fahrzeuge"
  }
]
