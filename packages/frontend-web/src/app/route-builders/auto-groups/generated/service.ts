import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/service/anfragen",
    "path": "anfragen"
  },
  {
    "module": "@/pages/service/anfrage-detail",
    "path": "anfrage/:id"
  },
  {
    "module": "@/pages/service/anfrage-neu",
    "path": "anfrage/neu"
  },
  {
    "module": "@/pages/service/rueckmeldung",
    "path": "rueckmeldung"
  },
  {
    "module": "@/pages/service/abschluss",
    "path": "abschluss"
  }
]
