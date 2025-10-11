import { useLiveInventory, useLiveSales, usePolicyAlerts } from '@/hooks/live-hooks'

type LiveStatus = 'closed' | 'open' | 'error'
type StatusClass = 'bg-emerald-500' | 'bg-red-600' | 'bg-zinc-400'

const resolveWorstStatus = (statuses: LiveStatus[]): LiveStatus => {
  if (statuses.includes('error')) {
    return 'error'
  }
  if (statuses.includes('open')) {
    return 'open'
  }
  return 'closed'
}

const resolveStatusClass = (status: LiveStatus): StatusClass => {
  switch (status) {
    case 'open':
      return 'bg-emerald-500'
    case 'error':
      return 'bg-red-600'
    default:
      return 'bg-zinc-400'
  }
}

export default function NavLiveStatus(): JSX.Element {
  const salesStatus = useLiveSales().status as LiveStatus
  const inventoryStatus = useLiveInventory().status as LiveStatus
  const policyStatus = usePolicyAlerts().status as LiveStatus

  const worstStatus = resolveWorstStatus([salesStatus, inventoryStatus, policyStatus])
  const dotClass = resolveStatusClass(worstStatus)

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className={`inline-block h-2 w-2 rounded-full ${dotClass}`} /> Live
    </div>
  )
}
