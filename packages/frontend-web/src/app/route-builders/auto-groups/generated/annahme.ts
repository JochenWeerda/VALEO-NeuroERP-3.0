import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/annahme/abrechnung",
    "path": "abrechnung"
  },
  {
    "module": "@/pages/annahme/annahme-qr",
    "path": "annahme-qr"
  },
  {
    "module": "@/pages/annahme/lkw-registrierung",
    "path": "lkw-registrierung"
  },
  {
    "module": "@/pages/annahme/qualitaets-check",
    "path": "qualitaets-check"
  },
  {
    "module": "@/pages/annahme/warteschlange",
    "path": "warteschlange"
  }
]
