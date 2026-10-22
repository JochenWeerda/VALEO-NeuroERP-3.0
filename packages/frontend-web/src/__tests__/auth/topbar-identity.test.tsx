import type { ReactNode } from 'react'
import { act, cleanup, fireEvent, render } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { TopBar } from '@/components/navigation/TopBar'

const fixture = vi.hoisted(() => ({
  authenticated: true, user: null as { name: string; email: string } | null, logout: vi.fn(),
}))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({
  user: fixture.user, logout: fixture.logout, isAuthenticated: fixture.user !== null && fixture.authenticated,
}) }))
vi.mock('@/hooks/useFeature', () => ({ useFeature: () => false }))
vi.mock('@/hooks/useTheme', () => ({ useTheme: () => ({ isDark: false, toggleTheme: vi.fn() }) }))
vi.mock('@/components/ui/notification-center', () => ({ NotificationCenter: () => null }))
vi.mock('react-i18next', () => ({ useTranslation: () => ({
  t: (key: string) => key, i18n: { language: 'de', changeLanguage: vi.fn() },
}) }))
vi.mock('@/app/routing/typed-router', () => ({
  useNavigate: () => vi.fn(),
  Link: ({ children, to }: { children: ReactNode; to: string }) => <a href={to}>{children}</a>,
}))

beforeEach(() => {
  fixture.user = { name: 'Synthetic Login Test', email: 'login-test@example.invalid' }
  fixture.authenticated = true
  fixture.logout.mockReset()
})
afterEach(cleanup)

describe('canonical topbar identity and logout', () => {
  it('shows the authenticated user instead of a fixed administrator', async () => {
    const view = render(<TopBar />)
    await act(async () => {})
    fireEvent.click(view.getByRole('button', { name: 'Benutzermenü' }))
    expect(view.getByText('Synthetic Login Test')).toBeTruthy()
    expect(view.getByText('login-test@example.invalid')).toBeTruthy()
    expect(view.queryByText('Test Admin')).toBeNull()
  })

  it('calls central logout once when the user signs out', async () => {
    const view = render(<TopBar />)
    await act(async () => {})
    fireEvent.click(view.getByRole('button', { name: 'Benutzermenü' }))
    fireEvent.click(view.getByRole('button', { name: 'Abmelden' }))
    expect(fixture.logout).toHaveBeenCalledTimes(1)
  })

  it('allows clearing a cached identity after the server session expires', async () => {
    fixture.authenticated = false
    const view = render(<TopBar />)
    await act(async () => {})
    fireEvent.click(view.getByRole('button', { name: 'Benutzermenü' }))
    const logout = view.getByRole('button', { name: 'Abmelden' }) as HTMLButtonElement
    expect(logout.disabled).toBe(false)
    fireEvent.click(logout)
    expect(fixture.logout).toHaveBeenCalledTimes(1)
  })

  it('does not invent an administrator when no user is authenticated', async () => {
    fixture.user = null
    const view = render(<TopBar />)
    await act(async () => {})
    fireEvent.click(view.getByRole('button', { name: 'Benutzermenü' }))
    expect(view.getByText('Nicht angemeldet')).toBeTruthy()
    expect((view.getByRole('button', { name: 'Abmelden' }) as HTMLButtonElement).disabled).toBe(true)
  })
})
