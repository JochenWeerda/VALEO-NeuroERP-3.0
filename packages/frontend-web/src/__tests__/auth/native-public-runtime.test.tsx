import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import LoginPage from '@/pages/auth/Login'
import CallbackPage from '@/pages/auth/Callback'
import { apiClient } from '@/lib/api-client'

const fixture = vi.hoisted(() => ({ login: vi.fn(), callback: vi.fn(), params: new URLSearchParams() }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ login: fixture.login, handleCallback: fixture.callback,
  loading: false, isAuthenticated: false, user: null }) }))
vi.mock('@/app/routing/typed-router', () => ({ useSearchParams: () => [fixture.params], useNavigate: () => vi.fn() }))
vi.mock('@/hooks/use-toast', () => ({ toast: vi.fn() }))

function show(page: JSX.Element) {
  const client = new QueryClient({defaultOptions:{queries:{retry:false}}})
  return render(<QueryClientProvider client={client}>{page}</QueryClientProvider>)
}
beforeEach(() => { vi.restoreAllMocks(); fixture.login.mockReset(); fixture.callback.mockReset(); fixture.params = new URLSearchParams() })

describe('public Studio authentication runtime', () => {
  it('renders a real SSO action without protected schema, overlay or data requests; failed login remains retryable', async () => {
    const get = vi.spyOn(apiClient, 'get'), post = vi.spyOn(apiClient, 'post')
    fixture.login.mockRejectedValueOnce(new Error('Provider unavailable')).mockResolvedValueOnce(undefined)
    show(<LoginPage />)
    fireEvent.click(screen.getByRole('button', {name:'Mit SSO anmelden'}))
    expect(await screen.findByRole('alert')).toHaveTextContent('Provider unavailable')
    fireEvent.click(screen.getByRole('button', {name:'Mit SSO anmelden'}))
    await waitFor(() => expect(fixture.login).toHaveBeenCalledTimes(2))
    expect(get).not.toHaveBeenCalled(); expect(post).not.toHaveBeenCalled()
  })
  it('renders callback failure through the actual plan, never fetching protected workspaces', async () => {
    const get = vi.spyOn(apiClient, 'get'), post = vi.spyOn(apiClient, 'post')
    fixture.params = new URLSearchParams({error:'access_denied'})
    show(<CallbackPage />)
    expect(await screen.findByRole('heading', {name:'Anmeldung fehlgeschlagen'})).toBeInTheDocument()
    expect(screen.getByRole('button', {name:'Zurueck zur Anmeldung'})).toBeEnabled()
    expect(fixture.callback).not.toHaveBeenCalled()
    expect(get).not.toHaveBeenCalled(); expect(post).not.toHaveBeenCalled()
  })
})
