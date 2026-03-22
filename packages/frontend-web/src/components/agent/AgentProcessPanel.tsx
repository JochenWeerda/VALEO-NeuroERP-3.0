/**
 * AgentProcessPanel — Real-time panel showing agent activity for a domain/process.
 *
 * Subscribes to SSE agent events filtered by domain. Renders a compact activity
 * feed that fades in when agents are active and hides when idle.
 *
 * Usage (add to any Kernfluss page):
 *   <AgentProcessPanel domain="annahme" />
 *   <AgentProcessPanel domain="lager" />
 */
import { useState } from 'react'
import { Activity, Sparkles, CheckCircle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useSSE } from '@/hooks/useSSE'
import type { MCPEvent } from '@/lib/mcp-events'
import { cn } from '@/lib/utils'

type AgentActivity = {
  id: string
  agentId: string
  status: 'starting' | 'running' | 'idle' | 'error' | 'done'
  message?: string
  ts: string
}

interface AgentProcessPanelProps {
  /** Domain filter: 'annahme', 'lager', 'einkauf', 'finanzen', etc. */
  domain: string
  className?: string
  /** Maximum activity items to retain */
  maxItems?: number
}

export function AgentProcessPanel({
  domain,
  className,
  maxItems = 6,
}: AgentProcessPanelProps): JSX.Element | null {
  const [activities, setActivities] = useState<AgentActivity[]>([])
  const [collapsed, setCollapsed] = useState(false)

  useSSE((event: MCPEvent) => {
    if (event.topic !== 'agent') return
    const agentEvent = event as MCPEvent & {
      status?: string
      agentId?: string
      message?: string
    }
    // Domain filter: agentId must contain domain or domain must be omitted
    if (
      agentEvent.agentId &&
      !agentEvent.agentId.toLowerCase().includes(domain.toLowerCase())
    ) {
      return
    }
    setActivities((prev) => [
      {
        id: event.id,
        agentId: agentEvent.agentId ?? 'agent',
        status: (agentEvent.status as AgentActivity['status']) ?? 'running',
        message: agentEvent.message,
        ts: event.ts,
      },
      ...prev.slice(0, maxItems - 1),
    ])
  })

  if (activities.length === 0) return null

  const activeCount = activities.filter(
    (a) => a.status === 'running' || a.status === 'starting',
  ).length

  return (
    <div
      className={cn(
        'rounded-lg border border-violet-100 bg-violet-50/60 p-3 transition-all',
        className,
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Activity
            className={cn(
              'h-4 w-4',
              activeCount > 0 ? 'text-violet-600 animate-pulse' : 'text-slate-400',
            )}
          />
          <span className="text-xs font-medium text-violet-800">Agent-Aktivität</span>
          {activeCount > 0 && (
            <Badge
              variant="outline"
              className="text-xs text-violet-700 border-violet-300 h-5 px-1.5"
            >
              {activeCount} aktiv
            </Badge>
          )}
        </div>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 text-slate-400"
          onClick={() => setCollapsed((c) => !c)}
        >
          {collapsed ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronUp className="h-3 w-3" />
          )}
        </Button>
      </div>

      {/* Activity feed */}
      {!collapsed && (
        <ul className="mt-2 space-y-1">
          {activities.map((a) => (
            <li key={a.id} className="flex items-center gap-2 text-xs text-slate-700">
              {a.status === 'done' ? (
                <CheckCircle className="h-3 w-3 text-green-500 shrink-0" />
              ) : a.status === 'error' ? (
                <AlertCircle className="h-3 w-3 text-red-500 shrink-0" />
              ) : a.status === 'running' || a.status === 'starting' ? (
                <Sparkles className="h-3 w-3 text-violet-500 shrink-0 animate-pulse" />
              ) : (
                <span className="h-3 w-3 shrink-0 rounded-full bg-slate-300 inline-block" />
              )}
              <span className="truncate flex-1">{a.message ?? a.agentId}</span>
              <span className="text-slate-400 shrink-0 tabular-nums">
                {new Date(a.ts).toLocaleTimeString('de-DE', {
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                })}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
