import type { ReactNode } from 'react'
import type { DecisionView } from '@/policy/decision-view'
import { auth } from '@/lib/auth'
import {
  type RoleDensityProfile,
  limitProcessDetails,
  resolveRoleDensityProfile,
} from '@/features/role-density'
import { useTenant } from '@/hooks/useTenant'

interface ProcessStatusPanelProps {
  view: DecisionView
  title?: string
  className?: string
  children?: ReactNode
  densityProfileOverride?: RoleDensityProfile
}

export function ProcessStatusPanel({
  view,
  title,
  className,
  children,
  densityProfileOverride,
}: ProcessStatusPanelProps): JSX.Element {
  const { tenantId } = useTenant()
  const roleDensityProfile =
    densityProfileOverride ??
    resolveRoleDensityProfile(auth.getUser()?.roles, {
      tenantId,
      pageDomain: view.context?.pageDomain,
      processDetails: view.details,
      requiresApproval: view.requiresApproval,
    })
  const visibleDetails = limitProcessDetails(view.details, roleDensityProfile)
  return (
    <div className={`rounded-md border px-3 py-2 ${view.statusClassName}${className ? ` ${className}` : ''}`}>
      {title ? <div className="mb-1 text-xs uppercase opacity-70">{title}</div> : null}
      <div className="text-sm font-semibold">{view.statusLabel}</div>
      <p className="mt-1 text-sm">{view.summary}</p>
      {visibleDetails.length > 0 ? (
        <ul className="mt-2 list-disc pl-4 text-xs">
          {visibleDetails.map((detail) => (
            <li key={detail}>{detail}</li>
          ))}
        </ul>
      ) : null}
      {children}
    </div>
  )
}
