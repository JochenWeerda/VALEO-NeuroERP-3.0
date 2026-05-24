import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/preise/historie",
    "path": "historie"
  },
  {
    "module": "@/pages/preise/konditionen",
    "path": "konditionen"
  },
  { "module": "@/pages/preise/kalkulation", "path": "kalkulation" },
  { "module": "@/pages/preise/zu-abschlaggruppen", "path": "zu-abschlaggruppen" },
  { "module": "@/pages/preise/rabattgruppen", "path": "rabattgruppen" },
]
