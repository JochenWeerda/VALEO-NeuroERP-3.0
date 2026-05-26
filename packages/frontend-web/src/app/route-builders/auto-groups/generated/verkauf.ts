import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/verkauf/betriebs-auftraege",
    "path": "betriebs-auftraege"
  },
  {
    "module": "@/pages/verkauf/kommissions-auftraege",
    "path": "kommissions-auftraege"
  },
  {
    "module": "@/pages/verkauf/kunde-neu",
    "path": "kunde-neu"
  },
  {
    "module": "@/pages/verkauf/kunden-liste",
    "path": "kunden-liste"
  },
  {
    "module": "@/pages/verkauf/kunden-stamm",
    "path": "kunden-stamm"
  },
  {
    "module": "@/pages/verkauf/kunden-stamm-enhanced",
    "path": "kunden-stamm-enhanced"
  },
  {
    "module": "@/pages/verkauf/lieferschein-erfassung",
    "path": "lieferschein-erfassung"
  },
  {
    "module": "@/pages/verkauf/unerledigte-auftrags-positionen",
    "path": "unerledigte-auftrags-positionen"
  },
  { "module": "@/pages/verkauf/kunde-neu/kundeneumaskbuilderpage", "path": "kunde-neu/kundeneumaskbuilderpage" },
  { "module": "@/pages/verkauf/dauerauftraege", "path": "dauerauftraege" },
]
