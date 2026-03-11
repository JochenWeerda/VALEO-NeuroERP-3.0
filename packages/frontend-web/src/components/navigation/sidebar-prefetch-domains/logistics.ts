import type { SidebarPageModuleMap } from './types'

export const logisticsPageModules: SidebarPageModuleMap = {
  ...import.meta.glob('../../pages/lager/**/*.tsx'),
  ...import.meta.glob('../../pages/warehouse/**/*.tsx'),
  ...import.meta.glob('../../pages/versand/**/*.tsx'),
  ...import.meta.glob('../../pages/strecke/**/*.tsx'),
  ...import.meta.glob('../../pages/produktion/**/*.tsx'),
  ...import.meta.glob('../../pages/disposition/**/*.tsx'),
}
