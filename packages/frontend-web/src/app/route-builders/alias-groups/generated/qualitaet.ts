import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/qualitaet/labor-auftrag",
    "path": "labor-auftrag"
  },
  {
    "module": "@/pages/qualitaet/labor-liste",
    "path": "labor"
  },
  {
    "module": "@/pages/qualitaet/reklamationen",
    "path": "reklamationen"
  },
  {
    "module": "@/pages/qualitaet/reklamation-detail",
    "path": "reklamation/:id"
  }
]
