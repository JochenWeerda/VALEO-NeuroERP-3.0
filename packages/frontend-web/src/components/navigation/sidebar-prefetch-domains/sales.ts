import type { SidebarPageModuleMap } from './types'

export const salesPageModules: SidebarPageModuleMap = {
  ...import.meta.glob('../../pages/sales/**/*.tsx'),
  ...import.meta.glob('../../pages/verkauf/**/*.tsx'),
  ...import.meta.glob('../../pages/dashboard/**/*.tsx'),
  ...import.meta.glob('../../pages/reports/**/*.tsx'),
  ...import.meta.glob('../../pages/analytics.tsx'),
  ...import.meta.glob('../../pages/artikel/**/*.tsx'),
}
