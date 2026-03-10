import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/futtermittel/charge-verfolgung",
    "path": "charge-verfolgung"
  },
  {
    "module": "@/pages/futtermittel/einzelfuttermittel-liste",
    "path": "einzelfuttermittel-liste"
  },
  {
    "module": "@/pages/futtermittel/einzelfuttermittel-stamm",
    "path": "einzelfuttermittel/:id"
  },
  {
    "module": "@/pages/futtermittel/futtermittel-bestellung",
    "path": "futtermittel-bestellung"
  },
  {
    "module": "@/pages/futtermittel/futtermittel-qualitaetskontrolle",
    "path": "futtermittel-qualitaetskontrolle"
  },
  {
    "module": "@/pages/futtermittel/futtermittel-statistik",
    "path": "futtermittel-statistik"
  },
  {
    "module": "@/pages/futtermittel/futtermittel-wareneingang",
    "path": "futtermittel-wareneingang"
  },
  {
    "module": "@/pages/futtermittel/mischfuttermittel-liste",
    "path": "mischfuttermittel-liste"
  },
  {
    "module": "@/pages/futtermittel/mischfuttermittel-stamm",
    "path": "mischfuttermittel/:id"
  }
]
