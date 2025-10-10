import { useLiveSales, useLiveInventory, usePolicyAlerts } from '@/hooks/live-hooks'

export default function NavLiveStatus() {
  const s1 = useLiveSales().status
  const s2 = useLiveInventory().status
  const s3 = usePolicyAlerts().status
  const worst = [s1, s2, s3].includes('error') ? 'error' : ([s1, s2, s3].includes('open') ? 'open' : 'closed')
  const dot = worst === 'open' ? 'bg-emerald-500' : worst === 'error' ? 'bg-red-600' : 'bg-zinc-400'
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className={`inline-block w-2 h-2 rounded-full ${dot}`} /> Live
    </div>
  )
}