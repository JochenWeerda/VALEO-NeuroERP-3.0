import { StrictMode, useMemo } from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'
import { FeatureFlagProvider } from '@/app/providers/FeatureFlagProvider'
import { SSEProvider } from '@/app/providers/SSEProvider'
import { router } from '@/app/routes'
import { ToastProvider } from '@/components/ui/toast-provider'
// Temporarily disabled - will be re-enabled later
// import { CommandPalette } from '@/components/command/CommandPalette'
// import { AskVALEO } from '@/components/ai/AskVALEO'
// import { SemanticSearch } from '@/components/search/SemanticSearch'
import { auth } from '@/lib/auth'
import { createQueryClient } from '@/lib/query'
import { useFeature } from '@/hooks/useFeature'
import '@/i18n/config' // Initialize i18n
import './index.css'

const queryClient = createQueryClient()

const resolveSseToken = (): string | undefined => {
  return auth.getAccessToken() ?? undefined
}

function Application(): JSX.Element {
  // useFeature kann nur innerhalb von FeatureFlagProvider verwendet werden
  // Da Application innerhalb von FeatureFlagProvider ist, sollte es funktionieren
  const sseUrl = (import.meta.env as Record<string, string | undefined>).VITE_MCP_EVENTS_URL
  const sseEnabled = useFeature('sse') && Boolean(sseUrl)

  const providerConfig = useMemo(
    () => ({
      url: sseUrl,
      enabled: sseEnabled,
      withCredentials: true,
    }),
    [sseEnabled],
  )

  return (
    <SSEProvider {...providerConfig} tokenResolver={resolveSseToken}>
      <ToastProvider>
        <RouterProvider router={router} />
        {/* TODO: Diese Komponenten müssen in Router-Kontext verschoben werden */}
        {/* <CommandPalette /> */}
        {/* <AskVALEO /> */}
        {/* <SemanticSearch /> */}
      </ToastProvider>
    </SSEProvider>
  )
}

const rootElement = document.getElementById('root')

if (rootElement instanceof HTMLElement) {
  const existingRoot = (rootElement as any).__reactRoot ?? null
  const root = existingRoot ?? ReactDOM.createRoot(rootElement)
  ;(rootElement as any).__reactRoot = root

  root.render(
    <StrictMode>
      <QueryClientProvider client={queryClient}>
        <FeatureFlagProvider>
          <Application />
        </FeatureFlagProvider>
      </QueryClientProvider>
    </StrictMode>,
  )
}
