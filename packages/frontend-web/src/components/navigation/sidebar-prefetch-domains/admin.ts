import type { SidebarPageModuleMap } from './types'

export const adminPageModules: SidebarPageModuleMap = import.meta.glob('../../pages/admin/**/*.tsx')
