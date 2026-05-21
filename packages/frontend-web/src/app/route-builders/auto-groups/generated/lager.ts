import type { AutoGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AutoGroupRouteEntry[] = [
  {
    "module": "@/pages/lager/auslagerung",
    "path": "auslagerung"
  },
  {
    "module": "@/pages/lager/bestandsuebersicht",
    "path": "bestandsuebersicht"
  },
  {
    "module": "@/pages/lager/einlagerung",
    "path": "einlagerung"
  },
  {
    "module": "@/pages/lager/inventur",
    "path": "inventur"
  },
  {
    "module": "@/pages/lager/lagerbewegungen",
    "path": "lagerbewegungen"
  },
  {
    "module": "@/pages/lager/lagerplaetze",
    "path": "lagerplaetze"
  },
  {
    "module": "@/pages/lager/terminal",
    "path": "terminal"
  },
  { "module": "@/pages/lager/bestandskorrektur", "path": "bestandskorrektur" },
  { "module": "@/pages/lager/gs1-scanner", "path": "gs1-scanner" },
]
