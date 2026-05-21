import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/workflows/approval",
    "path": "approval"
  },
  {
    "module": "@/pages/workflows/trigger",
    "path": "trigger"
  },
  { "module": "@/pages/workflows/supervisor", "path": "supervisor" },
]
