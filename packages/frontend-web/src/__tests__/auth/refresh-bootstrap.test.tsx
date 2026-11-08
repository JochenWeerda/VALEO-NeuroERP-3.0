import { act, cleanup, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuth } from '@/hooks/useAuth'

const fixture = vi.hoisted(() => ({ authenticated: false, refreshable: true, fresh: vi.fn() }))
vi.mock('@/lib/auth', () => ({ auth: {
  getUser: () => fixture.authenticated ? { sub: 'synthetic-person', name: 'Synthetic' } : null,
  isAuthenticated: () => fixture.authenticated, canRefresh: () => fixture.refreshable,
  getFreshAccessToken: fixture.fresh, hasScope: () => false, hasRole: () => false,
} }))
beforeEach(() => { fixture.authenticated = false; fixture.refreshable = true; fixture.fresh.mockReset() })
afterEach(cleanup)

describe('refresh bootstrap boundary', () => {
  it('waits before granting access or redirecting an expired restored session', async () => {
    let finish!: () => void
    fixture.fresh.mockReturnValue(new Promise<void>(resolve => { finish = resolve }))
    const { result } = renderHook(useAuth)
    expect(result.current.loading).toBe(true)
    expect(result.current.isAuthenticated).toBe(false)
    await act(async () => { fixture.authenticated = true; finish() })
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user?.sub).toBe('synthetic-person')
  })

  it('ends loading without authentication after a rejected renewal', async () => {
    fixture.fresh.mockResolvedValue(null)
    const { result } = renderHook(useAuth)
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
  })

  it('does not renew when no refresh session exists', () => {
    fixture.refreshable = false
    const { result } = renderHook(useAuth)
    expect(result.current.loading).toBe(false)
    expect(fixture.fresh).not.toHaveBeenCalled()
  })
})
