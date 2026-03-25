import { createRouteElement } from '@/app/route-builders/route-elements'
import type { PageModule, PageModuleFactory } from '@/app/route-builders/types'
import type { PageModuleGroupModule } from '@/app/page-module-groups/types'

type PageModuleGroupName = 'core' | 'commercial' | 'finance' | 'operations' | 'portal'

const PAGE_MODULE_GROUP_LOADERS: Record<PageModuleGroupName, () => Promise<PageModuleGroupModule>> = {
  core: () => import('@/app/page-module-groups/core'),
  commercial: () => import('@/app/page-module-groups/commercial'),
  finance: () => import('@/app/page-module-groups/finance'),
  operations: () => import('@/app/page-module-groups/operations'),
  portal: () => import('@/app/page-module-groups/portal'),
}

const GROUP_BY_PREFIX: Record<string, PageModuleGroupName> = {
  admin: 'core',
  agrar: 'operations',
  agribusiness: 'operations',
  analytics: 'core',
  annahme: 'operations',
  artikel: 'operations',
  auth: 'core',
  banken: 'finance',
  benachrichtigungen: 'core',
  charge: 'operations',
  compliance: 'finance',
  'contracts-v2': 'commercial',
  controlling: 'finance',
  crm: 'commercial',
  dashboard: 'commercial',
  dashboards: 'commercial',
  disposition: 'operations',
  document: 'core',
  dokumente: 'operations',
  einkauf: 'operations',
  einstellungen: 'core',
  energie: 'operations',
  errors: 'core',
  etiketten: 'operations',
  export: 'finance',
  fibu: 'finance',
  finance: 'finance',
  finanzplanung: 'finance',
  foerderung: 'operations',
  fuhrpark: 'operations',
  futter: 'operations',
  futtermittel: 'operations',
  inbox: 'operations',
  inventory: 'operations',
  'inventory-dashboard': 'core',
  'inventory-reports': 'core',
  kasse: 'finance',
  kontrakte: 'commercial',
  labor: 'operations',
  lager: 'operations',
  logistik: 'operations',
  mahnwesen: 'finance',
  management: 'commercial',
  marketing: 'commercial',
  mobile: 'operations',
  nachhaltigkeit: 'operations',
  nawaro: 'operations',
  personal: 'core',
  portal: 'portal',
  'policy-manager': 'core',
  pos: 'finance',
  preise: 'commercial',
  pricing: 'core',
  produktion: 'operations',
  projekte: 'operations',
  prospecting: 'commercial',
  public: 'core',
  qualitaet: 'operations',
  reports: 'commercial',
  rezepte: 'operations',
  sales: 'commercial',
  schaeden: 'operations',
  schichtplan: 'operations',
  service: 'commercial',
  setup: 'core',
  silo: 'operations',
  'start-dashboard': 'core',
  statistik: 'operations',
  'stock-management': 'core',
  strecke: 'operations',
  subventionen: 'operations',
  system: 'core',
  tankstelle: 'operations',
  termine: 'commercial',
  transporte: 'operations',
  verkauf: 'commercial',
  verladung: 'operations',
  versand: 'operations',
  versicherungen: 'operations',
  vertrag: 'operations',
  vertrieb: 'commercial',
  waage: 'operations',
  wartung: 'operations',
  weighing: 'core',
  workflow: 'core',
  workflows: 'core',
  zertifikate: 'operations',
}

const pageModuleGroupCache = new Map<PageModuleGroupName, Promise<PageModuleGroupModule>>()
const pageModuleLoaderCache = new Map<string, PageModuleFactory>()

function resolveModuleKey(modulePath: string): string {
  let resolved = modulePath.replace(/^@\//, '../../')
  if (!resolved.startsWith('../../')) {
    resolved = `../../${resolved.replace(/^\.\.\//, '')}`
  }
  if (!resolved.endsWith('.tsx')) {
    resolved = `${resolved}.tsx`
  }
  return resolved
}

function getTopLevelSegment(modulePath: string): string {
  const normalized = modulePath.replace(/^@\//, '').replace(/^pages\//, '')
  return normalized.split('/')[0] ?? normalized
}

function getPageModuleGroupName(modulePath: string): PageModuleGroupName {
  const groupName = GROUP_BY_PREFIX[getTopLevelSegment(modulePath)]
  if (!groupName) {
    throw new Error(`Route references unsupported page group: ${modulePath}`)
  }
  return groupName
}

function loadPageModuleGroup(groupName: PageModuleGroupName): Promise<PageModuleGroupModule> {
  let pending = pageModuleGroupCache.get(groupName)
  if (!pending) {
    pending = PAGE_MODULE_GROUP_LOADERS[groupName]()
    pageModuleGroupCache.set(groupName, pending)
  }
  return pending
}

export function getPageModuleLoader(modulePath: string): PageModuleFactory {
  const cachedLoader = pageModuleLoaderCache.get(modulePath)
  if (cachedLoader) {
    return cachedLoader
  }

  const moduleKey = resolveModuleKey(modulePath)
  const groupName = getPageModuleGroupName(modulePath)

  const loader: PageModuleFactory = async () => {
    const groupModule = await loadPageModuleGroup(groupName)
    const pageLoader = groupModule.PAGE_MODULES[moduleKey]
    if (!pageLoader) {
      throw new Error(`Route references unknown module: ${modulePath}`)
    }
    return pageLoader()
  }

  pageModuleLoaderCache.set(modulePath, loader)
  return loader
}

export function createRouteElementByModule(modulePath: string): JSX.Element {
  return createRouteElement(getPageModuleLoader(modulePath))
}
