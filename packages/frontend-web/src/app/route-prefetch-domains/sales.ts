const pageModules = {
  ...import.meta.glob('../../pages/sales/**/*.tsx'),
  ...import.meta.glob('../../pages/verkauf/**/*.tsx'),
  ...import.meta.glob('../../pages/artikel/**/*.tsx'),
  ...import.meta.glob('../../pages/start-dashboard.tsx'),
}

const HIGH_PRIORITY_MODULES = [
  '../../pages/start-dashboard.tsx',
] as const

export function prefetchSalesPriorityRoutes(): void {
  for (const key of HIGH_PRIORITY_MODULES) {
    pageModules[key]?.()
  }
}
