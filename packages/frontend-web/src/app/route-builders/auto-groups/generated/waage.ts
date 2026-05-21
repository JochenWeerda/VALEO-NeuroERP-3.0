import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/waage/hofliste",
    "path": "hofliste"
  },
  {
    "module": "@/pages/waage/liste",
    "path": "liste"
  },
  {
    "module": "@/pages/waage/wiegeschein-detail",
    "path": "wiegeschein/:id"
  },
  {
    "module": "@/pages/waage/wiegungen",
    "path": "wiegungen"
  },
  { "module": "@/pages/waage/vorlagen", "path": "vorlagen" },
  { "module": "@/pages/waage/wiegeschein-detail", "path": "wiegeschein-detail" },
]
