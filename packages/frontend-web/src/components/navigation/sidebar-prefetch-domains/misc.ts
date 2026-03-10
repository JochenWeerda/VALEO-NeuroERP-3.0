import type { SidebarPageModuleMap } from './types'

export const miscPageModules: SidebarPageModuleMap = {
  ...import.meta.glob('../../pages/personal/**/*.tsx'),
  ...import.meta.glob('../../pages/pos/**/*.tsx'),
  ...import.meta.glob('../../pages/einstellungen/**/*.tsx'),
  ...import.meta.glob('../../pages/start-dashboard.tsx'),
  ...import.meta.glob('../../pages/index.tsx'),
}
