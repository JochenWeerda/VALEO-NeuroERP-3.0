/**
 * Rohware-Annahme — Wizard-Schrittvalidierung (VK-020) über IntakeWeighingPage.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from '@/app/routing/test-router'
import RohwareAnnahmePage from '@/pages/annahme/rohware'

const toastMock = vi.hoisted(() => vi.fn())
const apiPostMock = vi.hoisted(() => vi.fn())

vi.mock('@/app/routing/typed-router', async () => {
  const actual = await vi.importActual('@/app/routing/typed-router')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: toastMock }),
}))

vi.mock('@/lib/axios', () => ({
  api: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: (...args: unknown[]) => apiPostMock(...args),
  },
}))

vi.mock('@/components/agent', () => ({
  AgentProcessPanel: (): JSX.Element => <div data-testid="agent-process-panel" />,
  AgentSuggestionBadge: (): null => null,
}))

vi.mock('@/lib/api/supply-chain', () => ({
  useSupplyChainOverview: () => ({
    data: {
      waitingInbound: 0,
      openWeighingTickets: 0,
      blockedCharges: 0,
      freightInTransit: 0,
    },
  }),
}))

vi.mock('@/lib/api/masks', async () => {
  const fixtures = (await import('@/__tests__/fixtures/intake-weighing-screens.json')).default
  return { useScreenDefinition: (id: string) => ({ data: (fixtures as Record<string, unknown>)[id], isLoading: false, error: null }) }
})
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({
  useScreenPermissions: (definition: { actions?: Array<{ permission?: string }> }) =>
    definition?.actions?.flatMap(action => action.permission ? [action.permission] : []) ?? [],
}))
vi.mock('@/lib/api/ux-overlays', () => ({
  useUserScreenOverlay: () => ({ data: undefined }),
  overlayKeys: { screen: (id: string) => ['test-overlay', id] },
  saveUserOverlay: vi.fn(),
  deleteUserOverlay: vi.fn(),
}))
vi.mock('@/components/mask-builder/specialized/intake/domain-data', async () => {
  const supply = await import('@/lib/api/supply-chain')
  return {
    useDomainIdentity: () => ({ tenantId: 'test-tenant', actor: 'test-operator' }),
    useDomainSupplyChain: () => supply.useSupplyChainOverview(),
  }
})

describe('RohwareAnnahmePage', () => {
  beforeEach(() => {
    toastMock.mockReset()
    apiPostMock.mockReset()
    apiPostMock.mockResolvedValue({ data: { id: 'ha-1', acceptance_number: 'A-2026-001' } })
  })

  const renderPage = (): ReturnType<typeof render> => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    })
    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <RohwareAnnahmePage />
        </MemoryRouter>
      </QueryClientProvider>,
    )
  }

  it('sollte Rohware-Annahme-Titel anzeigen', () => {
    renderPage()
    expect(screen.getAllByRole('heading', { name: 'Rohware-Annahme' }).length).toBeGreaterThanOrEqual(1)
  })

  it('blockiert Weiter im ersten Schritt ohne Lieferant und Kennzeichen', async () => {
    renderPage()

    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))

    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Schritt unvollstaendig',
          description: 'Lieferant ist ein Pflichtfeld.',
          variant: 'destructive',
        }),
      )
    })
  })

  it('blockiert Weiter im Ware-Schritt ohne Artikel/Lager/positives Netto', async () => {
    renderPage()

    fireEvent.change(screen.getByPlaceholderText('Name des Lieferanten'), {
      target: { value: 'Testhof Nord' },
    })
    fireEvent.change(screen.getByPlaceholderText(/AB-CD 1234/i), {
      target: { value: 'AB CD 999' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))

    await waitFor(() => {
      expect(screen.getAllByText('Ware & Gewicht').length).toBeGreaterThanOrEqual(1)
    })

    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))

    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Schritt unvollstaendig',
          description: 'Bitte einen Artikel auswaehlen.',
          variant: 'destructive',
        }),
      )
    })
  })

  it('validiert Lagerziel und Nettogewicht im Ware-Schritt', async () => {
    renderPage()
    fireEvent.change(screen.getByPlaceholderText('Name des Lieferanten'), { target: { value: 'Testhof Nord' } })
    fireEvent.change(screen.getByPlaceholderText(/AB-CD 1234/i), { target: { value: 'AB CD 999' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await waitFor(() => expect(screen.getAllByText('Ware & Gewicht').length).toBeGreaterThanOrEqual(1))

    fireEvent.click(screen.getByText('Weizen'))
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Schritt unvollstaendig',
          description: 'Bitte ein Lagerziel auswaehlen.',
          variant: 'destructive',
        }),
      )
    })

    fireEvent.click(screen.getByText('Silo 1'))
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Schritt unvollstaendig',
          description: expect.stringMatching(/Nettogewicht/),
          variant: 'destructive',
        }),
      )
    })
  })

})
