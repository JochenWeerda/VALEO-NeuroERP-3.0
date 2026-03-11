import type { SidebarPageModuleMap } from './types'

export const agrarPageModules: SidebarPageModuleMap = {
  ...import.meta.glob('../../pages/agrar/**/*.tsx'),
  ...import.meta.glob('../../pages/futtermittel/**/*.tsx'),
}
