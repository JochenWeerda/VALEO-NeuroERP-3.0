import type { DecisionView } from '@/policy/decision-view'
import { limitProcessDetails } from '@/features/role-density'
import { useApprovalDensityProfile } from '@/features/workflow/useApprovalDensityProfile'

interface CompactDecisionCardProps {
  view: DecisionView
  pageDomain?: string
  className?: string
  title?: string
  showDetails?: boolean
}

export function CompactDecisionCard({
  view,
  pageDomain,
  className,
  title,
  showDetails = true,
}: CompactDecisionCardProps): JSX.Element {
  const densityProfile = useApprovalDensityProfile(pageDomain ?? '', view)
  const visibleDetails =
    showDetails && densityProfile
      ? limitProcessDetails(view.details, densityProfile)
      : showDetails
        ? view.details
        : []

  return (
    <div className={`rounded-md border px-2 py-1.5 ${view.statusClassName}${className ? ` ${className}` : ''}`}>
      {title ? <div className="text-[11px] font-semibold uppercase opacity-80">{title}</div> : null}
      <div className="text-xs font-semibold">{view.statusLabel}</div>
      <div className="text-xs opacity-90">{view.summary}</div>
      {visibleDetails.length > 0 ? (
        <ul className="mt-1 list-disc pl-4 text-[11px] opacity-90">
          {visibleDetails.map((detail) => (
            <li key={detail}>{detail}</li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}
