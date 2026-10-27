import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import Page from '@/pages/disposition/touren-disposition'
import builder from '@/components/mask-builder/specialized/disposition-board-screen.json'

const http = vi.hoisted(() => ({ get: vi.fn(), request: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: http, getAxiosErrorMessage: (error: Error) => error.message }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { id: 'synthetic-reader', roles: ['LOGISTIK_LESEN'], scopes: ['logistics:read'] } }) }))
vi.mock('@/hooks/useTenant', () => ({ useTenant: () => ({ currentTenant: { id: 'synthetic-tenant' } }) }))

describe('routed native disposition contract', () => {
  it('renders the backend-declared specialist through the shared runtime without a write', async () => {
    http.get.mockImplementation(async (url: string) => {
      if (url === '/api/v1/masks/disposition__touren-disposition/screen-definition') return { data: builder }
      if (url.startsWith('/api/v1/ux/overlays/')) return { data: { overlay: {} } }
      if (url.includes('/data/list')) return { data: { data: { items: [], total: 0 } } }
      return { data: [] }
    })
    const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
    render(<QueryClientProvider client={client}><MemoryRouter><Page /></MemoryRouter></QueryClientProvider>)
    expect(await screen.findByTestId('disposition-board')).toBeInTheDocument()
    expect(http.get).toHaveBeenCalledWith('/api/v1/masks/disposition__touren-disposition/screen-definition', expect.objectContaining({ timeout: 8000 }))
    expect(http.request).not.toHaveBeenCalled()
  })
})
