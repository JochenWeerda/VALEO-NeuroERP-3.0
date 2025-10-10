import { useLive } from '@/state/live'
import NavLiveStatus from '@/components/app/NavLiveStatus'

export default function LiveMonitorPage() {
  const { sales, inventory, policy } = useLive()
  return (
    <div className="container py-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Live Monitor</h1>
        <NavLiveStatus />
      </div>
      <section>
        <h2 className="font-semibold">Sales Documents</h2>
        <pre className="text-xs bg-zinc-950 text-zinc-100 p-3 rounded-md overflow-auto">{JSON.stringify(sales, null, 2)}</pre>
      </section>
      <section>
        <h2 className="font-semibold">Inventory Events</h2>
        <pre className="text-xs bg-zinc-950 text-zinc-100 p-3 rounded-md overflow-auto">{JSON.stringify(inventory, null, 2)}</pre>
      </section>
      <section>
        <h2 className="font-semibold">Policy Alerts</h2>
        <pre className="text-xs bg-zinc-950 text-zinc-100 p-3 rounded-md overflow-auto">{JSON.stringify(policy, null, 2)}</pre>
      </section>
    </div>
  )
}