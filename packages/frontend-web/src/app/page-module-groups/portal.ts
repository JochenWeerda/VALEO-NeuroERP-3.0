import type { PageModuleGlob } from '@/app/page-module-groups/types'

export const PAGE_MODULES = import.meta.glob([
  '../../pages/portal/**/*.tsx',
]) as PageModuleGlob
