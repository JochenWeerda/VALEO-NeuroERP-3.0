const DOMAIN_PREFETCHERS = [
  () => import('./route-prefetch-domains/sales').then((module) => module.prefetchSalesPriorityRoutes()),
  () => import('./route-prefetch-domains/crm').then((module) => module.prefetchCrmPriorityRoutes()),
  () => import('./route-prefetch-domains/finance').then((module) => module.prefetchFinancePriorityRoutes()),
  () => import('./route-prefetch-domains/procurement').then((module) => module.prefetchProcurementPriorityRoutes()),
]

export function prefetchPriorityRoutes(): void {
  const nav = navigator as Navigator & { connection?: { saveData?: boolean; effectiveType?: string } }
  if (nav.connection?.saveData) return

  const schedule = typeof requestIdleCallback === 'function'
    ? requestIdleCallback
    : (cb: () => void) => setTimeout(cb, 2000)

  schedule(() => {
    for (const prefetcher of DOMAIN_PREFETCHERS) {
      void prefetcher()
    }
  })
}
