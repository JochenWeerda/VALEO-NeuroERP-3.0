import type { SidebarPageModuleMap } from './types'

export const workflowPageModules: SidebarPageModuleMap = {
  ...import.meta.glob('../../pages/workflow/**/*.tsx'),
  ...import.meta.glob('../../pages/workflows/**/*.tsx'),
}
