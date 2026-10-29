import { type ReactNode, useEffect, useState, useSyncExternalStore } from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { FeatureFlagProvider } from '@/app/providers/FeatureFlagProvider'
import { auth, getAccessToken } from '@/lib/auth'
import { createQueryClient } from '@/lib/query'
import { tenantFromToken } from '@/lib/tenant-from-token'

function subscribeSession(onChange: () => void): () => void {
  window.addEventListener('valeo-auth-changed', onChange)
  window.addEventListener('storage', onChange)
  return () => {
    window.removeEventListener('valeo-auth-changed', onChange)
    window.removeEventListener('storage', onChange)
  }
}

function sessionSnapshot(): string {
  const user = auth.getUser()
  // Only partition browser state; the server remains authoritative for access.
  // Token refresh, display names and email changes must preserve current drafts.
  return JSON.stringify(user ? [user.sub, tenantFromToken(getAccessToken()),
    [...new Set(user.roles)].sort((left, right) => left.localeCompare(right)),
    [...new Set(user.scopes)].sort((left, right) => left.localeCompare(right))] : null)
}

function SessionBootstrap({ children }: { children: ReactNode }): JSX.Element {
  const [queryClient] = useState(createQueryClient)
  useEffect(() => () => {
    void queryClient.cancelQueries()
    queryClient.clear()
  }, [queryClient])
  return (
    <QueryClientProvider client={queryClient}>
      <FeatureFlagProvider>{children}</FeatureFlagProvider>
    </QueryClientProvider>
  )
}

export default function DataBootstrap({ children }: { children: ReactNode }): JSX.Element {
  const session = useSyncExternalStore(subscribeSession, sessionSnapshot, () => 'null')
  return <SessionBootstrap key={session}>{children}</SessionBootstrap>
}
