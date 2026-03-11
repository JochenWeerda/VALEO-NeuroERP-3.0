const pageModules = {
  ...import.meta.glob('../../pages/einkauf/**/*.tsx'),
  ...import.meta.glob('../../pages/charge/**/*.tsx'),
}

const HIGH_PRIORITY_MODULES = [
  '../../pages/einkauf/bestellungen-liste.tsx',
] as const

export function prefetchProcurementPriorityRoutes(): void {
  for (const key of HIGH_PRIORITY_MODULES) {
    pageModules[key]?.()
  }
}
