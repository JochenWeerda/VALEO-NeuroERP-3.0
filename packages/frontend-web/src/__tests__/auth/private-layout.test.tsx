import { cleanup, render } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ReactNode } from 'react'
import { AppRouteLayout } from '@/app/routing/route-layouts'

const fixture = vi.hoisted(() => ({ authenticated: false }))
vi.mock('@/components/auth/ProtectedRoute', () => ({ ProtectedRoute: ({ children }: { children: ReactNode }) => fixture.authenticated ? children : <span>Anmeldung erforderlich</span> }))
vi.mock('@/layouts/DashboardLayout', () => ({ default: () => <span>Privater Arbeitsplatz</span> }))
vi.mock('@/layouts/CustomerPortalLayout', () => ({ default: () => null }))
vi.mock('@/app/page-module-loader', () => ({ createRouteElementByModule: () => null }))
vi.mock('@/app/FibuSuiteRuntime', () => ({ default: () => null }))
afterEach(() => { cleanup(); vi.unstubAllEnvs() })

describe.each(['true', 'false', undefined])('private layout with auth flag %s', flag => {
  it('always uses the authentication boundary', () => {
    vi.stubEnv('VITE_AUTH_REQUIRED', flag)
    fixture.authenticated = false
    const view = render(<AppRouteLayout />)
    expect(view.getByText('Anmeldung erforderlich')).toBeTruthy()
    expect(view.queryByText('Privater Arbeitsplatz')).toBeNull()
  })
  it('renders the private layout after the boundary grants access', () => {
    vi.stubEnv('VITE_AUTH_REQUIRED', flag)
    fixture.authenticated = true
    const view = render(<AppRouteLayout />)
    expect(view.getByText('Privater Arbeitsplatz')).toBeTruthy()
  })
})
