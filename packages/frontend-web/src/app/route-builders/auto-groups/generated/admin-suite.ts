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
  },
  {
    "module": "@/pages/admin-suite/security",
    "path": "security"
  },
  {
    "module": "@/pages/admin-suite/connectors",
    "path": "connectors"
  },
  {
    "module": "@/pages/admin-suite/devices",
    "path": "devices"
  },
  {
    "module": "@/pages/admin-suite/operations",
    "path": "operations"
  },
  {
    "module": "@/pages/admin-suite/compliance",
    "path": "compliance"
  },
  {
    "module": "@/pages/admin-suite/system-status",
    "path": "system-status"
  }
]
