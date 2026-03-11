import type { SidebarPageModuleMap } from './types'

export const financePageModules: SidebarPageModuleMap = {
  ...import.meta.glob('../../pages/fibu/**/*.tsx'),
  ...import.meta.glob('../../pages/finance/**/*.tsx'),
  ...import.meta.glob('../../pages/controlling/**/*.tsx'),
  ...import.meta.glob('../../pages/finanzplanung/**/*.tsx'),
  ...import.meta.glob('../../pages/export/**/*.tsx'),
}
