import type { PageModuleGlob } from '@/app/page-module-groups/types'

export const PAGE_MODULES = import.meta.glob([
  '../../pages/*.tsx',
  '../../pages/auth/**/*.tsx',
  '../../pages/errors/**/*.tsx',
  '../../pages/einstellungen/**/*.tsx',
  '../../pages/setup/**/*.tsx',
  '../../pages/system/**/*.tsx',
  '../../pages/public/**/*.tsx',
  '../../pages/admin/**/*.tsx',
  '../../pages/admin-suite/**/*.tsx',
  '../../pages/workflow/**/*.tsx',
  '../../pages/workflows/**/*.tsx',
  '../../pages/personal/**/*.tsx',
  '../../pages/benachrichtigungen/**/*.tsx',
  '../../pages/stammdaten/**/*.tsx',
]) as PageModuleGlob
