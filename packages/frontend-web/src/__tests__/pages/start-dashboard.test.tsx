import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { Truck } from 'lucide-react'
import { MemoryRouter } from '@/app/routing/test-router'
import { describe, expect, it, vi } from 'vitest'
import type { NavItem } from '@/app/navigation/types'
import i18n from '@/i18n/config'
import StartDashboardPage from '@/pages/start-dashboard'

const analyticsGetMock = vi.hoisted(() => vi.fn())
const flowSpineGetMock = vi.hoisted(() => vi.fn())
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

vi.mock('@/lib/axios', () => ({
  apiClient: {
    get: analyticsGetMock,
  },
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: flowSpineGetMock,
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

describe('StartDashboardPage', () => {
  it('zeigt klare lokalisierte Labels statt technischer MCP-Scope-Texte', async () => {
    Object.defineProperty(i18n, 'resolvedLanguage', { value: 'de', configurable: true })
    Object.defineProperty(i18n, 'language', { value: 'de', configurable: true })

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
          mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
        },
      ],
    }

    useNavSectionsMock.mockReturnValue([annahmeSection])
    analyticsGetMock.mockResolvedValue({ data: { revenue: 1200, orders: 4, customers: 9, inventory: 62 } })
    flowSpineGetMock.mockResolvedValue({
      data: {
        schema_version: 1,
        manifest_kind: 'FLOW_SPINE_PROCESS_CATALOG',
        generated_at: '2026-03-25T20:00:00Z',
        processes: [
          {
            key: 'order-to-cash',
            label: 'Auftrag bis Zahlung',
            route_path: '/workflow/flow-spine-order-to-cash',
            summary: 'Vertrieb, Lieferung, Faktura und Zahlung in einem agentenfaehigen Steuerraum.',
            domain: 'Vertrieb',
          },
        ],
      },
    })

    renderPage()

    expect(await screen.findByRole('heading', { name: 'App Starter', level: 1 })).toBeInTheDocument()
    expect(screen.getByText(/Annahme, Waage und Hoflogistik/i)).toBeInTheDocument()
    expect(screen.getByText('Logistik')).toBeInTheDocument()
    expect(screen.getByText('Öffnet: Warteschlange')).toBeInTheDocument()
    expect(screen.queryByText(/logistics:read/i)).not.toBeInTheDocument()
    expect(await screen.findByText('Vertrieb')).toBeInTheDocument()
  })
})
