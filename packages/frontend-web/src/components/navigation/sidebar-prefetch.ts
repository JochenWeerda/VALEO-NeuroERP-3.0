import type { NavItem } from '@/app/navigation/types'
import type { SidebarPageModuleMap } from './sidebar-prefetch-domains/types'

const DOMAIN_IMPORTERS: Record<string, () => Promise<SidebarPageModuleMap>> = {
  admin: () => import('./sidebar-prefetch-domains/admin').then((module) => module.adminPageModules),
  agrar: () => import('./sidebar-prefetch-domains/agrar').then((module) => module.agrarPageModules),
  compliance: () => import('./sidebar-prefetch-domains/admin').then((module) => module.adminPageModules),
  core: () => import('./sidebar-prefetch-domains/misc').then((module) => module.miscPageModules),
  crm: () => import('./sidebar-prefetch-domains/crm').then((module) => module.crmPageModules),
  finance: () => import('./sidebar-prefetch-domains/finance').then((module) => module.financePageModules),
  hr: () => import('./sidebar-prefetch-domains/misc').then((module) => module.miscPageModules),
  logistics: () => import('./sidebar-prefetch-domains/logistics').then((module) => module.logisticsPageModules),
  marketing: () => import('./sidebar-prefetch-domains/crm').then((module) => module.crmPageModules),
  pos: () => import('./sidebar-prefetch-domains/misc').then((module) => module.miscPageModules),
  procurement: () => import('./sidebar-prefetch-domains/procurement').then((module) => module.procurementPageModules),
  quality: () => import('./sidebar-prefetch-domains/logistics').then((module) => module.logisticsPageModules),
  sales: () => import('./sidebar-prefetch-domains/sales').then((module) => module.salesPageModules),
  workflow: () => import('./sidebar-prefetch-domains/workflow').then((module) => module.workflowPageModules),
}

const moduleMapCache = new Map<string, Promise<SidebarPageModuleMap>>()

function normalizeModulePath(modulePath: string): string {
  const key = modulePath.replace(/^@\//, '../../').replace(/^\.\//, '../../')
  return key.endsWith('.tsx') ? key : `${key}.tsx`
}

function loadDomainModuleMap(domain: string): Promise<SidebarPageModuleMap> {
  const cached = moduleMapCache.get(domain)
  if (cached) {
    return cached
  }

  const importer = DOMAIN_IMPORTERS[domain] ?? DOMAIN_IMPORTERS.core
  const pending = importer()
  moduleMapCache.set(domain, pending)
  return pending
}

export function prefetchVisibleModules(items: NavItem[], maxPrefetch = 8): void {
  const nav = navigator as Navigator & { connection?: { saveData?: boolean } }
  if (nav.connection?.saveData) return

  const visibleModules = items
    .filter((item): item is NavItem & { module: string } => Boolean(item.module))
    .slice(0, maxPrefetch)

  if (visibleModules.length === 0) {
    return
  }

  const schedule = typeof requestIdleCallback === 'function'
    ? requestIdleCallback
    : (cb: () => void) => setTimeout(cb, 3000)

  schedule(() => {
    const groupedByDomain = new Map<string, string[]>()

    for (const item of visibleModules) {
      const domain = item.mcp.businessDomain || 'core'
      const normalizedPath = normalizeModulePath(item.module)
      const existing = groupedByDomain.get(domain)
      if (existing) {
        existing.push(normalizedPath)
      } else {
        groupedByDomain.set(domain, [normalizedPath])
      }
    }

    for (const [domain, modulePaths] of groupedByDomain.entries()) {
      void loadDomainModuleMap(domain).then((pageModules) => {
        for (const modulePath of modulePaths) {
          pageModules[modulePath]?.()
        }
      })
    }
  })
}
