import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { expect, it, vi } from 'vitest'
import { useIdempotencyOverview } from '@/lib/api/process-mining'

const session = vi.hoisted(() => ({ tenant: 'tenant-a', actor: 'actor-a', get: vi.fn() }))

vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { sub: session.actor } }) }))
vi.mock('@/lib/auth', () => ({ auth: { getAccessToken: () => session.tenant } }))
vi.mock('@/lib/tenant-from-token', () => ({ tenantFromToken: (token: string) => token }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: session.get } }))

it('reads the response body and isolates cached monitor data by tenant and actor', async () => {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const wrapper = ({ children }: { children: ReactNode }) =>
    <QueryClientProvider client={client}>{children}</QueryClientProvider>

  session.get.mockResolvedValueOnce({ data: { tenant: 'tenant-a' } })
  const { result, rerender } = renderHook(useIdempotencyOverview, { wrapper })
  await waitFor(() => expect(result.current.data).toEqual({ tenant: 'tenant-a' }))

  session.tenant = 'tenant-b'
  session.get.mockResolvedValueOnce({ data: { tenant: 'tenant-b' } })
  rerender()
  expect(result.current.data).toBeUndefined()
  await waitFor(() => expect(result.current.data).toEqual({ tenant: 'tenant-b' }))

  session.actor = ''
  rerender()
  expect(result.current.data).toBeUndefined()
  expect(session.get).toHaveBeenCalledTimes(2)
})
