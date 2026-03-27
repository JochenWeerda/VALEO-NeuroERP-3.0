import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/kontrakte/LstKontraktUebersicht",
    "path": ""
  },
  {
    "module": "@/pages/kontrakte/FrmKontraktDetail",
    "path": "neu"
  },
  {
    "module": "@/pages/kontrakte/FrmKontraktDetail",
    "path": ":id"
  },
  {
    "module": "@/pages/kontrakte/KontraktAlarmDashboard",
    "path": "alarme"
  },
  {
    "module": "@/pages/kontrakte/KontraktPositionsmonitor",
    "path": "positionen"
  }
]
