import { useCallback, useEffect, useMemo, useState } from "react"
import { Outlet } from "react-router-dom"
import { AppShell } from "@/components/navigation/AppShell"
import { AdvisorDock } from "@/features/copilot/AdvisorDock"
import { CallWidget } from "@/components/cti/CallWidget"
import { useFeature } from "@/hooks/useFeature"
import { type McpRealtimeEvent, useMcpConnectionState, useMcpRealtime } from "@/lib/useMcpRealtime"

export default function AppLayout(): JSX.Element {
  const commandPaletteEnabled = useFeature('commandPalette')
  const realtimeEnabled = useFeature('sse')

  const [lastEvent, setLastEvent] = useState<string>(realtimeEnabled ? "idle" : "disabled")
  const connectionState = useMcpConnectionState({ enabled: realtimeEnabled })

  useEffect(() => {
    if (!realtimeEnabled) {
      setLastEvent("disabled")
    }
  }, [realtimeEnabled])

  const handleAnyEvent = useCallback(
    (event: McpRealtimeEvent): void => {
      if (!realtimeEnabled) {
        return
      }
      if (event.rawType === "heartbeat") {
        return
      }
      setLastEvent(`${event.service}:${event.rawType}`)
    },
    [realtimeEnabled],
  )

  useMcpRealtime("*", handleAnyEvent, { enabled: realtimeEnabled })

  const connectionMeta = useMemo(() => {
    if (!realtimeEnabled) {
      return {
        label: "Disabled",
        className: "text-slate-500",
      }
    }
    if (connectionState === "open") {
      return { label: "Connected", className: "text-green-600" }
    }
    if (connectionState === "error") {
      return { label: "Disconnected", className: "text-red-500" }
    }
    return { label: "Connecting", className: "text-amber-500" }
  }, [connectionState, realtimeEnabled])

  return (
    <AppShell enableCommandPalette={commandPaletteEnabled}>
      <div className="flex h-full flex-col">
        <div className="flex-1 overflow-y-auto bg-background p-6">
          <Outlet />
        </div>
        {realtimeEnabled ? (
          <footer className="border-t bg-muted/40 px-6 py-2 text-xs text-muted-foreground">
            <div className="flex items-center justify-between gap-2">
              <span className={`${connectionMeta.className} font-medium`}>Realtime: {connectionMeta.label}</span>
              <span className="truncate" title={lastEvent}>
                Last event: {lastEvent}
              </span>
            </div>
          </footer>
        ) : null}
      </div>
      <AdvisorDock />
      <CallWidget />
    </AppShell>
  )
}
