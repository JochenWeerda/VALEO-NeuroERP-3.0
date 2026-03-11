const pageModules = {
  ...import.meta.glob('../../pages/finance/**/*.tsx'),
  ...import.meta.glob('../../pages/fibu/**/*.tsx'),
  ...import.meta.glob('../../pages/lager/**/*.tsx'),
}

const HIGH_PRIORITY_MODULES = [
  '../../pages/finance/buchungserfassung.tsx',
  '../../pages/lager/bestandsuebersicht.tsx',
] as const

export function prefetchFinancePriorityRoutes(): void {
  for (const key of HIGH_PRIORITY_MODULES) {
    pageModules[key]?.()
  }
}
