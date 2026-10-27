import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Truck } from 'lucide-react'
import { MemoryRouter } from '@/app/routing/test-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import * as domMatchers from '@testing-library/jest-dom/matchers'

expect.extend(domMatchers)
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

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ user: null }),
}))

vi.mock('@/workspace/home-signals', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/workspace/home-signals')>()
  return {
    ...actual,
    workspaceNow: () => new Date('2026-10-22T08:00:00'),
  }
})

vi.mock('@/hooks/usePinnedTiles', () => ({
  usePinnedTiles: () => ({
    isPinned: () => false,
    pinnedTileIds: [],
    togglePin: vi.fn(),
  }),
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: analyticsGetMock,
    post: vi.fn(),
  },
}))

class SilentEventSource {
  url: string
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  constructor(url: string) {
    this.url = url
  }
  addEventListener(): void {}
  removeEventListener(): void {}
  close(): void {}
}

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

function mockInboxQueue(options?: { documentKind?: string; canOpen?: boolean }): void {
  mockAnnahmeNav()
  analyticsGetMock.mockImplementation(async (path: string) => {
    if (String(path).includes('/api/mcp/documents/inbox/queue')) {
      const proposal: {
        policy_id: string
        label: string
        document_type: string
        document_kind?: string
        direction: 'incoming'
        target_route: string
        reason: string
      } = {
        policy_id: 'incoming-supplier-invoice',
        label: 'Rechnungseingang erfassen',
        document_type: 'supplier_invoice',
        direction: 'incoming',
        target_route: '/einkauf/rechnung-eingang-erfassung',
        reason: 'test',
      }
      if (options?.documentKind) {
        proposal.document_kind = options.documentKind
      }
      return {
        data: {
          ok: true,
          source: 'mcp',
          available: true,
          booking_allowed: false,
          count: 1,
          items: [
            {
              id: 'INBOX-9',
              status: 'pending',
              parsed_fields: {},
              match_values: { supplierName: 'Nordkorn AG' },
              confidence: 0.4,
              confidence_band: 'low',
              source: 'default-incoming-invoice',
              proposal,
              duplicates: [],
              blockers: [],
              actions: [
                {
                  key: 'open_mask',
                  label: 'Beleg öffnen',
                  kind: 'primary',
                  href: '/einkauf/rechnung-eingang-erfassung',
                  booking: false,
                },
              ],
              command: {
                command: 'document.capture.open',
                executable: false,
                booking: false,
                reason: 'keine Buchung',
                policy_id: 'incoming-supplier-invoice',
                document_type: 'supplier_invoice',
                target_route: '/einkauf/rechnung-eingang-erfassung',
                prefill: {},
                confidence: 0.4,
                confidence_band: 'low',
                blockers: [],
                source: { kind: 'dms_inbox', id: 'INBOX-9' },
                gaps: ['create_from_inbox_bucht_nicht'],
              },
              ...(options?.canOpen === undefined ? {} : { can_open: options.canOpen }),
              booking_allowed: false,
            },
          ],
          gaps: ['create_from_inbox_bucht_nicht'],
        },
      }
    }
    return { data: { revenue: 1200, orders: 4, customers: 9 } }
  })
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
  analyticsGetMock.mockImplementation(async (path: string) => {
    if (String(path).includes('/api/mcp/documents/inbox/queue')) {
      return {
        data: {
          ok: true,
          source: 'mcp',
          available: true,
          booking_allowed: false,
          count: 0,
          items: [],
          gaps: ['create_from_inbox_bucht_nicht'],
        },
      }
    }
    if (String(path) === '/api/v1/kontrakte') {
      return { data: { items: [], total: 0, skip: 0, limit: 20 } }
    }
    if (String(path) === '/api/v1/agrar/contracts') {
      return { data: { items: [], total: 0 } }
    }
    if (String(path).startsWith('/api/v1/logistik/tours')) {
      return { data: [] }
    }
    return { data: { revenue: 1200, orders: 4, customers: 9 } }
  })
}

describe('StartDashboardPage', () => {
  beforeEach(() => {
    vi.stubGlobal('EventSource', SilentEventSource)
    window.localStorage.clear()
    window.sessionStorage.clear()
    Object.defineProperty(i18n, 'resolvedLanguage', { value: 'de', configurable: true })
    Object.defineProperty(i18n, 'language', { value: 'de', configurable: true })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('zeigt Adaptive Workspace auf der Startseite ohne Flow-Spine-Kacheln', async () => {
    mockAnnahmeNav()
    renderPage()

    expect(await screen.findByRole('heading', { name: 'Start', level: 1 })).toBeInTheDocument()
    expect(screen.getByText(/Wo bin ich, was kann ich tun, was ist wichtig/i)).toBeInTheDocument()
    expect(screen.getByTestId('adaptive-workspace-layer')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-work-items')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Handlungsbedarf', level: 2 })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'App-Katalog öffnen' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Oberfläche fixieren' })).toHaveClass('h-11')
    expect(screen.getByRole('button', { name: 'App-Katalog öffnen' })).toHaveClass('h-11')
    expect(screen.getByRole('tab', { name: 'Ernte & Warenannahme' })).toHaveClass('min-h-11')
    expect(screen.getByRole('heading', { name: 'Annahme & Waage', level: 2 })).toBeInTheDocument()
    expect(screen.queryByRole('tab', { name: 'Annahme & Waage' })).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Warteschlange' })).toHaveAttribute('href', '/annahme/warteschlange')
    const queue = screen.getByRole('link', { name: 'Annahme-Warteschlange' })
    expect(queue).toHaveAttribute('href', '/annahme/warteschlange')
    expect(queue.closest('[data-fachaktion-id="harvest.intake-queue"]')).toBeTruthy()
    await userEvent.click(screen.getByRole('tab', { name: 'Steuerung & Compliance' }))
    expect(screen.getByRole('link', { name: 'Leitstand' })).toHaveAttribute('href', '/workflow/leitstand')
    expect(screen.queryByText('Flow Spine Prozesse')).not.toBeInTheDocument()
    expect(screen.queryByText(/End-to-End Prozesskontrolle/i)).not.toBeInTheDocument()
    expect(screen.queryByText('Auftrag bis Zahlung')).not.toBeInTheDocument()
    expect(screen.queryByText(/logistics:read/i)).not.toBeInTheDocument()
    expect(screen.getByLabelText('Rollen-Cockpit')).toBeInTheDocument()
    expect(screen.getByTestId('adaptive-workspace-inbox')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-composition-host')).toHaveAttribute(
      'data-host-variant',
      'embedded',
    )
    expect(screen.getByTestId('workspace-disposition-entry')).toHaveAttribute(
      'data-specialized-type',
      'disposition_board',
    )
    expect(screen.getByTestId('workspace-disposition-entry')).toHaveAttribute(
      'data-specialized-id',
      'lkw-disposition-board',
    )
    expect(screen.getByTestId('workspace-disposition-entry')).toHaveAttribute(
      'data-board-route',
      '/disposition/touren-disposition',
    )
    expect(screen.getByTestId('disposition-board')).toBeInTheDocument()
    expect(await screen.findByText('keine Kette')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-agrar-chain')).toHaveAttribute('data-chain-status', 'empty')
    expect(
      analyticsGetMock.mock.calls.some((call) => String(call[0]) === '/api/v1/kontrakte'),
    ).toBe(true)
    expect(
      analyticsGetMock.mock.calls.some((call) => String(call[0]).includes('/workspace/agrar-chain')),
    ).toBe(false)
  })

  it('zeigt die Inbox ohne Dokumentart und ohne Beleglink', async () => {
    mockInboxQueue()
    renderPage()

    expect(await screen.findByTestId('inbox-row-INBOX-9')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'Zur Belegmaske INBOX-9' })).not.toBeInTheDocument()
    expect(screen.getByTestId('inbox-open-reason-INBOX-9')).toHaveTextContent(
      'Dokumentart nicht erkannt. Ohne Art wird keine Maske geraten.',
    )
    expect(analyticsGetMock).toHaveBeenCalledWith('/api/mcp/documents/inbox/queue')
    expect(analyticsGetMock.mock.calls.some((call) => String(call[0]).includes('approve'))).toBe(false)
  })

  it('verlinkt die Eingangsrechnung nur bei EINGANGSRECHNUNG und can_open', async () => {
    mockInboxQueue({ documentKind: 'EINGANGSRECHNUNG', canOpen: true })
    renderPage()

    expect(await screen.findByTestId('inbox-row-INBOX-9')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'Zur Belegmaske INBOX-9' })).toHaveAttribute(
      'href',
      '/belege/purchase_invoice/neu?inbox=INBOX-9',
    )
    expect(analyticsGetMock).toHaveBeenCalledWith('/api/mcp/documents/inbox/queue')
    expect(analyticsGetMock.mock.calls.some((call) => String(call[0]).includes('approve'))).toBe(false)
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

  it('öffnet die bestehende Suche über den Strg+K-Einstieg', async () => {
    const user = userEvent.setup()
    const keys: KeyboardEvent[] = []
    const onKey = (event: Event): void => {
      keys.push(event as KeyboardEvent)
    }
    window.addEventListener('keydown', onKey, true)
    mockAnnahmeNav()
    try {
      renderPage()

      await screen.findByRole('link', { name: 'Warteschlange' })
      expect(screen.queryByLabelText('Belege und Apps suchen')).not.toBeInTheDocument()
      expect(screen.queryByRole('heading', { name: 'Treffer' })).not.toBeInTheDocument()
      await user.click(screen.getByRole('button', { name: 'Suche öffnen' }))
      expect(keys.some((event) => event.key === 'k' && event.ctrlKey && !event.shiftKey && !event.altKey)).toBe(true)
    } finally {
      window.removeEventListener('keydown', onKey, true)
    }
  })

  it('pinnt Handlungsbedarf und fixiert die Oberflaeche im Overlay', async () => {
    const user = userEvent.setup()
    mockAnnahmeNav()
    renderPage()

    const pin = await screen.findByRole('button', { name: 'Annahme-Warteschlange pinnen' })
    await user.click(pin)
    expect(window.localStorage.getItem(LAUNCHPAD_OVERLAY_STORAGE_KEY)).toContain('harvest.intake-queue')
    await user.click(screen.getByRole('button', { name: 'Oberfläche fixieren' }))
    expect(window.localStorage.getItem(LAUNCHPAD_OVERLAY_STORAGE_KEY)).toContain('"surfaceLocked":true')
  })
})
