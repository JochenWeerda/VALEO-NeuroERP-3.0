import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/kontrakte/FrmKontraktDetail",
    "path": "FrmKontraktDetail"
  },
  {
    "module": "@/pages/kontrakte/FrmKontraktProtokoll",
    "path": "FrmKontraktProtokoll"
  },
  {
    "module": "@/pages/kontrakte/LstKontraktUebersicht",
    "path": "LstKontraktUebersicht"
  },
  {
    "module": "@/pages/kontrakte/KontraktAlarmDashboard",
    "path": "KontraktAlarmDashboard"
  },
  {
    "module": "@/pages/kontrakte/KontraktPositionsmonitor",
    "path": "KontraktPositionsmonitor"
  },
  { "module": "@/pages/kontrakte/kontraktklassen", "path": "kontraktklassen" },
  { "module": "@/pages/kontrakte/mengenzeitraeume", "path": "mengenzeitraeume" },
]
