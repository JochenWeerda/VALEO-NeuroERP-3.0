import { useCallback, useState } from "react"
import { NavLink, Outlet } from "react-router-dom"
import { Menu } from "lucide-react"
import { type McpRealtimeEvent, useMcpConnectionState, useMcpRealtime } from "@/lib/useMcpRealtime"
import { AdvisorDock } from "@/features/copilot/AdvisorDock"

const nav = [
  { to: '/', label: 'Dashboard' },
  { to: '/contracts', label: 'Contracts' },
  { to: '/pricing', label: 'Pricing' },
  { to: '/inventory', label: 'Inventory' },
  { to: '/weighing', label: 'Weighing' },
  { to: '/sales', label: 'Sales' },
  { to: '/document', label: 'Document' },
  { to: '/policies', label: 'Policies' },
]

export default function AppLayout(): JSX.Element {
  const [lastEvent, setLastEvent] = useState<string>('–')
  const connectionState = useMcpConnectionState()

  const handleAnyEvent = useCallback((event: McpRealtimeEvent): void => {
    if (event.rawType === 'heartbeat') {
      return
    }
    setLastEvent(`${event.service}:${event.rawType}`)
  }, [])

  useMcpRealtime('*', handleAnyEvent)

  const connectionLabel = connectionState === 'open'
    ? 'Connected'
    : connectionState === 'error'
      ? 'Disconnected'
      : 'Connecting'

  const connectionClass = connectionState === 'open'
    ? 'text-green-600'
    : connectionState === 'error'
      ? 'text-red-500'
      : 'text-amber-500'

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b">
        <div className="container flex items-center gap-3 py-3">
          <Menu className="h-5 w-5 opacity-60" />
          <h1 className="text-lg font-semibold">VALEO NeuroERP</h1>
          <nav className="ml-auto flex gap-4">
            {nav.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }): string =>
                  `text-sm ${isActive ? 'font-semibold underline' : 'opacity-80 hover:opacity-100'}`
                }
              >
                {n.label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="container flex items-center justify-end pb-2 text-xs text-muted-foreground">
          <span className={`${connectionClass} font-medium`}>Realtime: {connectionLabel}</span>
          <span className="ml-3 truncate" title={lastEvent}>Last event: {lastEvent}</span>
        </div>
      </header>
      <main className="container py-6">
        <Outlet />
      </main>
      <AdvisorDock />
    </div>
  )
}