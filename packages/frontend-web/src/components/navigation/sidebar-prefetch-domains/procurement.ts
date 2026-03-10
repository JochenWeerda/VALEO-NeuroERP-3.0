import type { SidebarPageModuleMap } from './types'

export const procurementPageModules: SidebarPageModuleMap = {
  ...import.meta.glob('../../pages/einkauf/**/*.tsx'),
  ...import.meta.glob('../../pages/charge/**/*.tsx'),
}
