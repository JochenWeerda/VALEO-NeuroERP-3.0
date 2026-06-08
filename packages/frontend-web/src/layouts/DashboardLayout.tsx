import { Suspense, lazy, useCallback, useEffect, useMemo, useState } from "react"
import { Outlet } from '@/app/routing/typed-router'
import { ActionDispatchProvider, VoiceWhisperBarHost } from "@/features/ki-usability"
import { AppShell } from "@/components/navigation/AppShell"
import { AdvisorDock } from "@/features/copilot/AdvisorDock"
import { useFeature } from "@/hooks/useFeature"
import { type McpRealtimeEvent, useMcpConnectionState, useMcpRealtime } from "@/lib/useMcpRealtime"

const AskVALEO = lazy(() =>
  import("@/components/ai/AskVALEO").then((module) => ({ default: module.AskVALEO })),
)

const Breadcrumbs = lazy(() =>
  import("@/components/navigation/Breadcrumbs").then((module) => ({ default: module.Breadcrumbs })),
)

const GlobalButtonHandler = lazy(() =>
  import("@/components/GlobalButtonHandler").then((module) => ({ default: module.GlobalButtonHandler })),
)

const CallWidget = lazy(() =>
  import("@/components/cti/CallWidget").then((module) => ({ default: module.CallWidget })),
)

export default function AppLayout(): JSX.Element {
  const commandPaletteEnabled = useFeature('commandPalette')
  const voiceControlEnabled = useFeature('voiceControl')
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
    return { label: "Connecting", className: "text-amber-700" }
  }, [connectionState, realtimeEnabled])

  return (
    <ActionDispatchProvider>
    <AppShell enableCommandPalette={commandPaletteEnabled}>
      <div className="flex h-full flex-col">
        <Suspense fallback={<div className="h-11 border-b bg-background/60" />}>
          <Breadcrumbs />
        </Suspense>
        <div className="flex-1 overflow-y-auto bg-background p-4 md:p-8">
          <Outlet />
        </div>
        {realtimeEnabled ? (
          <footer className="border-t border-border bg-muted/40 px-6 py-2 text-xs text-muted-foreground">
            <div className="flex items-center justify-between gap-2">
              <span className={`${connectionMeta.className} font-medium`}>Realtime: {connectionMeta.label}</span>
              <span className="truncate" title={lastEvent}>
                Last event: {lastEvent}
              </span>
            </div>
          </footer>
        ) : null}
      </div>
      <Suspense fallback={null}>
        <GlobalButtonHandler />
      </Suspense>
      <AdvisorDock />
      <Suspense fallback={null}>
        <CallWidget />
      </Suspense>
      <Suspense fallback={null}>
        <AskVALEO />
      </Suspense>
      <VoiceWhisperBarHost enabled={voiceControlEnabled} />
    </AppShell>
    </ActionDispatchProvider>
  )
}
