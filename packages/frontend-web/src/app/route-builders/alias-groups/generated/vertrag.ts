import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/vertrag/rahmenvertraege",
    "path": "rahmenvertraege"
  },
  {
    "module": "@/pages/kontrakte/FrmKontraktDetail",
    "path": "neu"
  },
  {
    "module": "@/pages/kontrakte/FrmKontraktDetail",
    "path": ":id"
  }
]
