import type { ToolbarAction } from '@/components/navigation/PageToolbar'
import { useUIDensityManifest, fetchUIDensityManifest } from '@/lib/api/ui-density-manifest'

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

/**
 * Enhanced role density resolution that utilizes more data from the backend manifest
 * beyond just recommended_density, making it more dynamic and context-aware
 */
export async function resolveRoleDensityProfileFromManifest(
  roles: string[] | undefined,
  context?: DensityContext,
  pageDomain?: string
): Promise<RoleDensityProfile> {
  // Fetch the whole manifest
  const manifest = await fetchUIDensityManifest()
  
  // Find the entry for the pageDomain
  const normalizedPageDomain = normalizeDomain(pageDomain)
  const entry = manifest.entries.find((candidate) => candidate.page_domain === normalizedPageDomain) ?? null
  
  // Start with backend recommended density or fallback to focused
  let baseDensity: InformationDensity = entry?.recommended_density ?? 'focused'
  
  // Enhance base density with additional manifest data
  if (entry) {
    // Adjust density based on policy complexity
    if (entry.policy_rule_ids && entry.policy_rule_ids.length > 3) {
      baseDensity = bumpDensity(baseDensity)
    }
    
    // Adjust density based on explainability requirements
    if (entry.requires_explainability || (entry.explainability_statuses && entry.explainability_statuses.length > 0)) {
      baseDensity = bumpDensity(baseDensity)
    }
    
    // Adjust density based on approval complexity
    if (entry.requires_human_confirmation || 
        (entry.approval_roles && entry.approval_roles.length > 2) ||
        (entry.approval_statuses && entry.approval_statuses.length > 1)) {
      baseDensity = bumpDensity(baseDensity)
    }
    
    // Adjust density based on command restrictions
    if (entry.restricted_command_count && entry.restricted_command_count > 5) {
      baseDensity = bumpDensity(baseDensity)
    }
    
    // Adjust density based on aggregate type complexity
    if (entry.aggregate_types && entry.aggregate_types.length > 3) {
      baseDensity = bumpDensity(baseDensity)
    }
    
    // Adjust density based on source contract diversity
    if (entry.source_contracts && entry.source_contracts.length > 4) {
      baseDensity = bumpDensity(baseDensity)
    }
  }
  
  // Resolve role-based density as fallback/adjustment
  let roleBasedDensity: InformationDensity = 'focused'
  try {
    const normalizedRoles = (roles ?? []).map(normalizeRole)
    
    // Dynamic role-based mapping that could be enhanced to come from manifest in future
    const roleDensityMap: Record<string, InformationDensity> = {
      'admin': 'dense',
      'manager': 'dense',
      'fibu.admin': 'dense',
      'agrar.manager': 'dense',
      'controlling.admin': 'dense',
      'approver': 'standard',
      'fibu.write': 'standard',
      'sales.write': 'standard',
      'crm.write': 'standard',
      'disponent': 'standard',
      'operator': 'standard',
      'viewer': 'focused',
      'guest': 'focused'
    }
    
    // Find highest density role
    for (const role of normalizedRoles) {
      const roleDensity = roleDensityMap[role]
      if (roleDensity) {
        const currentIndex = DENSITY_ORDER.indexOf(roleBasedDensity)
        const roleIndex = DENSITY_ORDER.indexOf(roleDensity)
        if (roleIndex > currentIndex) {
          roleBasedDensity = roleDensity
        }
      }
    }
  } catch (error) {
    // Fallback to focused if role resolution fails
    roleBasedDensity = 'focused'
  }
  
  // Use the more restrictive density between manifest-based and role-based
  const finalBaseDensity = 
    DENSITY_ORDER.indexOf(baseDensity) > DENSITY_ORDER.indexOf(roleBasedDensity)
      ? baseDensity
      : roleBasedDensity
  
  // Apply context adjustments
  const adjustedDensity = applyContextAdjustments(finalBaseDensity, context)
  return DENSITY_PROFILES[adjustedDensity]
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

// Keep the original function for backward compatibility
export function resolveRoleDensityProfile(
  roles: string[] | undefined,
  context?: DensityContext,
): RoleDensityProfile {
  // Synchronous fallback - use role-based resolution only
  const normalizedRoles = (roles ?? []).map(normalizeRole)
  
  // Simple role-based mapping
  const roleDensityMap: Record<string, InformationDensity> = {
    'admin': 'dense',
    'manager': 'dense',
    'fibu.admin': 'dense',
    'agrar.manager': 'dense',
    'controlling.admin': 'dense',
    'approver': 'standard',
    'fibu.write': 'standard',
    'sales.write': 'standard',
    'crm.write': 'standard',
    'disponent': 'standard',
    'operator': 'standard',
  }
  
  let baseDensity: InformationDensity = 'focused'
  
  // Find highest density role
  for (const role of normalizedRoles) {
    const roleDensity = roleDensityMap[role]
    if (roleDensity) {
      const currentIndex = DENSITY_ORDER.indexOf(baseDensity)
      const roleIndex = DENSITY_ORDER.indexOf(roleDensity)
      if (roleIndex > currentIndex) {
        baseDensity = roleDensity
      }
    }
  }
  
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
