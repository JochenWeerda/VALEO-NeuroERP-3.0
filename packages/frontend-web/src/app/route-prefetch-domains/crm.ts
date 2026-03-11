const pageModules = import.meta.glob('../../pages/{crm,prospecting}/**/*.tsx')

const HIGH_PRIORITY_MODULES = [
  '../../pages/crm/kontakt-detail.tsx',
] as const

export function prefetchCrmPriorityRoutes(): void {
  for (const key of HIGH_PRIORITY_MODULES) {
    pageModules[key]?.()
  }
}
