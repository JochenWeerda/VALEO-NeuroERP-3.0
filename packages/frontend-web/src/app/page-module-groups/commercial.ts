import type { PageModuleGlob } from '@/app/page-module-groups/types'

export const PAGE_MODULES = import.meta.glob([
  '../../pages/crm/**/*.tsx',
  '../../pages/marketing/**/*.tsx',
  '../../pages/sales/**/*.tsx',
  '../../pages/verkauf/**/*.tsx',
  '../../pages/vertrieb/**/*.tsx',
  '../../pages/kontrakte/**/*.tsx',
  '../../pages/preise/**/*.tsx',
  '../../pages/service/**/*.tsx',
  '../../pages/termine/**/*.tsx',
  '../../pages/prospecting/**/*.tsx',
  '../../pages/analytics/**/*.tsx',
  '../../pages/dashboard/**/*.tsx',
  '../../pages/dashboards/**/*.tsx',
  '../../pages/management/**/*.tsx',
  '../../pages/reports/**/*.tsx',
  '../../pages/genossenschaft/**/*.tsx',
  '../../pages/contracts-v2.tsx',
  '../../pages/reports.tsx',
]) as PageModuleGlob
