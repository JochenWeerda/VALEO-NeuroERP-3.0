import type { ToolbarAction } from '@/components/navigation/PageToolbar'

export type InformationDensity = 'focused' | 'standard' | 'dense'

export interface DensityContext {
  tenantId?: string
  pageDomain?: string
  availableActionIds?: string[]
  processDetails?: string[]
  requiresApproval?: boolean
  backendDensity?: InformationDensity
}

export interface RoleDensityProfile {
  density: InformationDensity
  label: string
  maxPrimaryActions: number
  maxKpis: number
  maxCharts: number
  maxLists: number
  processDetailLimit: number
  showSectionBadges: boolean
  showKeyInfo: boolean
}

const ROLE_PRIORITY: Array<{ density: InformationDensity; matches: string[] }> = [
  {
    density: 'dense',
    matches: ['admin', 'manager', 'fibu.admin', 'agrar.manager', 'controlling.admin'],
  },
  {
    density: 'standard',
    matches: ['approver', 'fibu.write', 'sales.write', 'crm.write', 'disponent', 'operator'],
  },
]

const DENSITY_PROFILES: Record<InformationDensity, RoleDensityProfile> = {
  focused: {
    density: 'focused',
    label: 'Fokussiert',
    maxPrimaryActions: 2,
    maxKpis: 4,
    maxCharts: 1,
    maxLists: 1,
    processDetailLimit: 1,
    showSectionBadges: false,
    showKeyInfo: false,
  },
  standard: {
    density: 'standard',
    label: 'Standard',
    maxPrimaryActions: 3,
    maxKpis: 6,
    maxCharts: 2,
    maxLists: 2,
    processDetailLimit: 2,
    showSectionBadges: true,
    showKeyInfo: true,
  },
  dense: {
    density: 'dense',
    label: 'Verdichtet',
    maxPrimaryActions: 4,
    maxKpis: 8,
    maxCharts: 4,
    maxLists: 4,
    processDetailLimit: Number.POSITIVE_INFINITY,
    showSectionBadges: true,
    showKeyInfo: true,
  },
}

const DENSITY_ORDER: InformationDensity[] = ['focused', 'standard', 'dense']
const DEFAULT_TENANT_ID = '00000000-0000-0000-0000-000000000001'

function normalizeRole(role: string): string {
  return role.trim().toLowerCase()
}

function normalizeDomain(pageDomain: string | undefined): string {
  return (pageDomain ?? '').trim().toLowerCase()
}

function bumpDensity(density: InformationDensity): InformationDensity {
  const index = DENSITY_ORDER.indexOf(density)
  return DENSITY_ORDER[Math.min(index + 1, DENSITY_ORDER.length - 1)]
}

function resolveRoleBaseDensity(roles: string[] | undefined): InformationDensity {
  const normalizedRoles = (roles ?? []).map(normalizeRole)

  for (const candidate of ROLE_PRIORITY) {
    if (candidate.matches.some((role) => normalizedRoles.includes(role))) {
      return candidate.density
    }
  }

  return 'focused'
}

function applyContextAdjustments(baseDensity: InformationDensity, context?: DensityContext): InformationDensity {
  if (!context) {
    return baseDensity
  }

  let density = baseDensity
  const pageDomain = normalizeDomain(context.pageDomain)
  const actionCount = context.availableActionIds?.length ?? 0
  const processDetailCount = context.processDetails?.length ?? 0
  const tenantId = (context.tenantId ?? '').trim()

  if (
    pageDomain.includes('finance') ||
    pageDomain.includes('fibu') ||
    pageDomain.includes('controlling') ||
    pageDomain.includes('abschluss') ||
    pageDomain.includes('approval')
  ) {
    density = bumpDensity(density)
  }

  if (context.requiresApproval === true || actionCount >= 5 || processDetailCount >= 3) {
    density = bumpDensity(density)
  }

  if (tenantId.length > 0 && tenantId !== DEFAULT_TENANT_ID && tenantId !== 'system' && pageDomain.startsWith('agrar')) {
    density = bumpDensity(density)
  }

  if (context.backendDensity) {
    while (DENSITY_ORDER.indexOf(density) < DENSITY_ORDER.indexOf(context.backendDensity)) {
      density = bumpDensity(density)
    }
  }

  return density
}

export function resolveRoleDensityProfile(
  roles: string[] | undefined,
  context?: DensityContext,
): RoleDensityProfile {
  const baseDensity = resolveRoleBaseDensity(roles)
  return DENSITY_PROFILES[applyContextAdjustments(baseDensity, context)]
}

export function mergeToolbarActionsForDensity(
  primaryActions: ToolbarAction[],
  overflowActions: ToolbarAction[],
  profile: RoleDensityProfile,
): {
  primaryActions: ToolbarAction[]
  overflowActions: ToolbarAction[]
} {
  const primarySlice = primaryActions.slice(0, profile.maxPrimaryActions)
  const overflowMap = new Map<string, ToolbarAction>()

  for (const action of [...primaryActions.slice(profile.maxPrimaryActions), ...overflowActions]) {
    overflowMap.set(action.id, action)
  }

  return {
    primaryActions: primarySlice,
    overflowActions: Array.from(overflowMap.values()),
  }
}

export function limitItemsForDensity<T>(items: T[] | undefined, limit: number): T[] {
  if (!Array.isArray(items)) {
    return []
  }
  if (!Number.isFinite(limit)) {
    return items
  }
  return items.slice(0, limit)
}

export function limitProcessDetails(details: string[], profile: RoleDensityProfile): string[] {
  return limitItemsForDensity(details, profile.processDetailLimit)
}
