import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/qualitaet/labor-auftrag",
    "path": "labor-auftrag"
  },
  {
    "module": "@/pages/qualitaet/labor-liste",
    "path": "labor-liste"
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
