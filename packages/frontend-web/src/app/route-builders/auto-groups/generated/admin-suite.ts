import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/admin-suite/index",
    "path": ""
  },
  {
    "module": "@/pages/admin-suite/setup",
    "path": "setup"
  },
  {
    "module": "@/pages/admin-suite/migration",
    "path": "migration"
  }
]
