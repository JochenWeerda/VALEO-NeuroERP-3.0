import type { AliasGroupRouteEntry } from '@/app/route-builders/types'

export const entries: AliasGroupRouteEntry[] = [
  {
    "module": "@/pages/personal/mitarbeiter-stamm",
    "path": "mitarbeiter/:id"
  },
  {
    "module": "@/pages/personal/mitarbeiter-stamm",
    "path": "mitarbeiter/neu"
  },
  {
    "module": "@/pages/personal/mitarbeiter-liste",
    "path": "mitarbeiter"
  },
  {
    "module": "@/pages/personal/onboarding",
    "path": "onboarding"
  },
  {
    "module": "@/pages/personal/qualifikationen",
    "path": "qualifikationen"
  },
  {
    "module": "@/pages/personal/schulung-neu",
    "path": "schulung-neu"
  },
  {
    "module": "@/pages/personal/schulungen",
    "path": "schulungen"
  },
  {
    "module": "@/pages/personal/stundenzettel-liste",
    "path": "stundenzettel"
  },
  {
    "module": "@/pages/personal/stundenzettel",
    "path": "stundenzettel/:id"
  },
  {
    "module": "@/pages/personal/zeiterfassung",
    "path": "zeiterfassung"
  }
]
