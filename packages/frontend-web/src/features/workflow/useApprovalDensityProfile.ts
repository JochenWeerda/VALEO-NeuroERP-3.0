import type { DecisionView } from '@/policy/decision-view'
import { auth } from '@/lib/auth'
import { resolveRoleDensityProfile } from '@/features/role-density'
import { useUIDensityManifest } from '@/lib/api/ui-density-manifest'
import { useTenant } from '@/hooks/useTenant'

export function useApprovalDensityProfile(
  pageDomain: string,
  view: DecisionView | null | undefined,
) {
  const { tenantId } = useTenant()
  const densityManifestQuery = useUIDensityManifest(pageDomain)

  if (view == null) {
    return undefined
  }

  return resolveRoleDensityProfile(auth.getUser()?.roles, {
    tenantId,
    pageDomain,
    processDetails: view.details,
    requiresApproval: view.requiresApproval,
    backendDensity: densityManifestQuery.data?.entry?.recommended_density,
  })
}
