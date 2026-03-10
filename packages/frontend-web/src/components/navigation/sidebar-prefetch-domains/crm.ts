import type { SidebarPageModuleMap } from './types'

export const crmPageModules: SidebarPageModuleMap = {
  ...import.meta.glob('../../pages/crm/**/*.tsx'),
  ...import.meta.glob('../../pages/prospecting/**/*.tsx'),
}
