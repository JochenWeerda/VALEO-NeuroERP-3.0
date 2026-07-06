import type { PageModuleGlob } from '@/app/page-module-groups/types'

export const PAGE_MODULES = import.meta.glob([
  '../../pages/fibu/**/*.tsx',
  '../../pages/finance/**/*.tsx',
  '../../pages/export/**/*.tsx',
  '../../pages/banken/**/*.tsx',
  '../../pages/kasse/**/*.tsx',
  '../../pages/mahnwesen/**/*.tsx',
  '../../pages/finanzplanung/**/*.tsx',
  '../../pages/controlling/**/*.tsx',
  '../../pages/compliance/**/*.tsx',
  '../../pages/docflow/**/*.tsx',
  '../../pages/pos/**/*.tsx',
]) as PageModuleGlob
