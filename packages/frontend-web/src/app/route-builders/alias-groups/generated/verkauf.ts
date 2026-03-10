import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/verkauf/kunden-stamm",
    "path": "kunde/neu"
  },
  {
    "module": "@/pages/verkauf/kunden-stamm",
    "path": "kunde/:id"
  },
  {
    "module": "@/pages/verkauf/kunden-stamm",
    "path": "kunden-stamm/:id"
  },
  {
    "module": "@/pages/verkauf/kunden-stamm-enhanced",
    "path": "kunden-stamm-enhanced/:id"
  },
  {
    "module": "@/pages/verkauf/kunden-liste",
    "path": "kunden-liste"
  },
  {
    "module": "@/pages/verkauf/lieferschein-erfassung",
    "path": "lieferschein-erfassung"
  },
  {
    "module": "@/pages/verkauf/kunde-neu",
    "path": "kunde-neu"
  }
]
