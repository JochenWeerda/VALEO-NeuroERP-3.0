import type { ReactNode } from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import CustomerPortalLayout from '@/layouts/CustomerPortalLayout'
const fixture = vi.hoisted(() => ({ staff: true, logout: vi.fn() }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ hasRole: (role: string) => fixture.staff && role === 'admin', logout: fixture.logout }) }))
vi.mock('@/components/portal/PortalKontoWahl', () => ({ PortalKontoWahl: () => <div>Betriebsauswahl</div>, PortalKontoGate: ({ children }: {children: ReactNode}) => <>{children}</> }))
vi.mock('@/lib/auth', () => ({ auth: { getUser: () => null, getAccessToken: () => null } }))
beforeEach(() => { fixture.staff = true; fixture.logout.mockReset() })
describe('internal customer inspection shell', () => {
  it('marks the staff inspection as staff access without impersonating the customer', () => {
    render(<MemoryRouter initialEntries={['/portal?preview=customer']}><CustomerPortalLayout /></MemoryRouter>)
    expect(screen.getByRole('status', { name: 'Interne Kundenansicht' })).toHaveTextContent('Sie bleiben als interner Bearbeiter angemeldet')
    expect(screen.getByRole('button', { name: 'Prüfansicht verlassen' })).toBeInTheDocument()
  })
  it('does not mount tenant-wide advisory data as a selected-customer inspection', () => {
    render(<MemoryRouter initialEntries={['/portal/rationsoptimierung?preview=customer']}><CustomerPortalLayout /></MemoryRouter>)
    expect(screen.getByText('Die Kundenanbindung ist noch nicht freigeschaltet. Interne Beratungsdaten werden in dieser Ansicht nicht geladen.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Interne Futterberatung öffnen' })).toHaveAttribute('href', '/futtermittel/rationsoptimierung')
  })
  it('uses canonical logout instead of only navigating away', () => {
    render(<MemoryRouter initialEntries={['/portal']}><CustomerPortalLayout /></MemoryRouter>)
    fireEvent.click(screen.getByRole('button', { name: 'Benutzermenü öffnen' }))
    fireEvent.click(screen.getByRole('button', { name: 'Abmelden' }))
    expect(fixture.logout).toHaveBeenCalledTimes(1)
  })
  it('does not turn a caller-supplied preview parameter into staff privileges', () => {
    fixture.staff = false
    render(<MemoryRouter initialEntries={['/portal?preview=customer']}><CustomerPortalLayout /></MemoryRouter>)
    expect(screen.queryByRole('status', { name: 'Interne Kundenansicht' })).not.toBeInTheDocument()
  })
})
