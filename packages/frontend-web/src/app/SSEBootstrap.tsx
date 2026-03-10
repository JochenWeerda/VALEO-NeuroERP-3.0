import { type ReactNode, useMemo } from 'react'
import { SSEProvider } from '@/app/providers/SSEProvider'
import { useFeature } from '@/hooks/useFeature'
import { auth } from '@/lib/auth'

const resolveSseToken = (): string | undefined => {
  return auth.getAccessToken() ?? undefined
}

export default function SSEBootstrap({ children }: { children: ReactNode }): JSX.Element {
  const sseUrl =
    (import.meta.env as Record<string, string | undefined>).VITE_MCP_EVENTS_URL ||
    '/api/events?stream=mcp'
  const sseEnabled = useFeature('sse') && Boolean(sseUrl)

  const providerConfig = useMemo(
    () => ({
      url: sseUrl,
      enabled: sseEnabled,
      withCredentials: true,
    }),
    [sseEnabled, sseUrl],
  )

  return (
    <SSEProvider {...providerConfig} tokenResolver={resolveSseToken}>
      {children}
    </SSEProvider>
  )
}
