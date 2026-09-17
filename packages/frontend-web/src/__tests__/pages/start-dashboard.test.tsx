import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Truck } from 'lucide-react'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { NavItem } from '@/app/navigation/types'
import { LAUNCHPAD_OVERLAY_STORAGE_KEY } from '@/app/navigation/launchpad-personalization'
import i18n from '@/i18n/config'
import StartDashboardPage from '@/pages/start-dashboard'

const analyticsGetMock = vi.hoisted(() => vi.fn())
const useNavSectionsMock = vi.hoisted(() => vi.fn())

vi.mock('@/app/navigation/nav-runtime', () => ({
  useNavSections: useNavSectionsMock,
}))

vi.mock('@/hooks/useFeature', () => ({
  useFeature: () => true,
}))

vi.mock('@/hooks/usePinnedTiles', () => ({
  usePinnedTiles: () => ({
    isPinned: () => false,
    pinnedTileIds: [],
    togglePin: vi.fn(),
  }),
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: analyticsGetMock,
  },
}))

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    i18n,
    t: (value: string) => value,
  }),
}))

function renderPage(): void {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <StartDashboardPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

function mockAnnahmeNav(): void {
  const annahmeSection: NavItem = {
    id: 'annahme',
    label: 'Annahme & Waage',
    icon: Truck,
    mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
    children: [
      {
        id: 'warteschlange',
        label: 'Warteschlange',
        icon: Truck,
        path: '/annahme/warteschlange',
        keywords: ['waage', 'hofliste'],
        mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
      },
    ],
  }

  useNavSectionsMock.mockReturnValue([annahmeSection])
  analyticsGetMock.mockResolvedValue({ data: { revenue: 1200, orders: 4, customers: 9 } })
}

describe('StartDashboardPage', () => {
  beforeEach(() => {
    window.localStorage.clear()
    window.sessionStorage.clear()
    Object.defineProperty(i18n, 'resolvedLanguage', { value: 'de', configurable: true })
    Object.defineProperty(i18n, 'language', { value: 'de', configurable: true })
  })

  it('zeigt Beleg-First-Einstieg statt Flow-Spine-Prozesskacheln', async () => {
    mockAnnahmeNav()
    renderPage()

    expect(await screen.findByRole('heading', { name: 'Start', level: 1 })).toBeInTheDocument()
    expect(screen.getByText(/Wo bin ich, was kann ich tun, was ist wichtig/i)).toBeInTheDocument()
    expect(screen.getByText('Schnellaktionen')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'App-Katalog öffnen' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: '+ Kunde' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: '+ Angebot' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: '+ Auftrag' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: '+ Aktivität' })).toBeInTheDocument()
    expect(screen.getAllByText('Zur Auswertung')).toHaveLength(3)
    expect(screen.getByText(/Zeitraum, Trend und Abweichung sind nicht ermittelt/i)).toBeInTheDocument()
    expect(screen.queryByText('Trend: nicht ermittelt')).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Umsatz zur Auswertung' })).toHaveAttribute('href', '/dashboard/sales')
    expect(screen.getByRole('button', { name: 'App-Katalog öffnen' })).toHaveClass('h-11')
    expect(screen.getByRole('link', { name: '+ Kunde' })).toHaveClass('h-11')
    expect(screen.getByRole('tab', { name: 'Ernte & Warenannahme' })).toHaveClass('min-h-11')
    expect(screen.queryByText('Lagerauslastung')).not.toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Ernte & Warenannahme' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Annahme & Waage', level: 2 })).toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'Annahme & Waage' })).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Warteschlange' })).toHaveAttribute('href', '/annahme/warteschlange')
    expect(screen.getByRole('link', { name: 'Leitstand' })).toHaveAttribute('href', '/workflow/leitstand')
    expect(screen.getByRole('button', { name: 'Weitere Schnellaktionen' })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Letzte Dokumente' })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Weitere Schnellaktionen' }))
    expect(await screen.findByRole('menuitem', { name: 'Letzte Dokumente' })).toHaveAttribute('href', '/workspace/letzte-dokumente')
    await userEvent.keyboard('{Escape}')
    expect(screen.queryByText(/logistics:read/i)).not.toBeInTheDocument()
    expect(screen.queryByText('Flow Spine Prozesse')).not.toBeInTheDocument()
    expect(screen.queryByText(/End-to-End Prozesskontrolle/i)).not.toBeInTheDocument()
    expect(screen.queryByText('Auftrag bis Zahlung')).not.toBeInTheDocument()
  })

  it('öffnet den Anpassen-Modus und entfernt eine Kachel lokal', async () => {
    const user = userEvent.setup()
    mockAnnahmeNav()
    renderPage()

    await screen.findByRole('link', { name: 'Warteschlange' })
    await user.click(screen.getByRole('button', { name: 'Startseite anpassen' }))
    expect(screen.queryByRole('link', { name: 'Warteschlange' })).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Warteschlange entfernen' }))
    expect(screen.queryByRole('button', { name: 'Warteschlange Aktionen' })).not.toBeInTheDocument()
    expect(window.localStorage.getItem(LAUNCHPAD_OVERLAY_STORAGE_KEY)).toContain('warteschlange')
  })

  it('findet Apps über Beschreibung und Nav-Stichworte', async () => {
    const user = userEvent.setup()
    mockAnnahmeNav()
    renderPage()

    await screen.findByRole('link', { name: 'Warteschlange' })
    await user.type(screen.getByLabelText('Belege und Apps suchen'), 'waage')
    expect(await screen.findByRole('heading', { name: 'Treffer' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Warteschlange' })).toHaveAttribute('href', '/annahme/warteschlange')
  })
})
