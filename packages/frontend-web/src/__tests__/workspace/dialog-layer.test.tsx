import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AdaptiveWorkspaceLayer } from '@/workspace/AdaptiveWorkspaceLayer'
import { requestExistingCommandPalette } from '@/workspace/request-command-palette'

const postMock = vi.hoisted(() => vi.fn())

vi.mock('@/app/navigation/nav-runtime', () => ({
  useNavSections: () => [],
}))

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ user: null }),
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
}))

vi.mock('@/lib/auth', () => ({
  auth: {
    getAccessToken: () => 'dialog-layer-fixture-jwt',
  },
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (String(path).includes('/api/mcp/documents/inbox/queue')) {
        return {
          data: {
            ok: true,
            source: 'mcp',
            available: true,
            booking_allowed: false,
            count: 0,
            items: [],
            gaps: [],
          },
        }
      }
      if (String(path).startsWith('/api/v1/logistik/tours')) {
        return { data: [] }
      }
      return { data: { items: [], total: 0 } }
    }),
    post: postMock,
  },
}))

class SilentEventSource {
  url: string
  constructor(url: string) {
    this.url = url
  }
  addEventListener(): void {}
  removeEventListener(): void {}
  close(): void {}
}

function renderLayer(): void {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <AdaptiveWorkspaceLayer />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

function isPaletteShortcut(event: KeyboardEvent): boolean {
  return event.key === 'k' && event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey
}

describe('Dialogebene', () => {
  beforeEach(() => {
    vi.stubGlobal('EventSource', SilentEventSource)
    postMock.mockReset()
    localStorage.clear()
    sessionStorage.clear()
  })

  it('zeigt den Strg+K-Einstieg und oeffnet die bestehende Palette ohne zweite Kommandozeile', async () => {
    const user = userEvent.setup()
    const keys: KeyboardEvent[] = []
    const onKey = (event: Event): void => {
      keys.push(event as KeyboardEvent)
    }
    window.addEventListener('keydown', onKey, true)
    try {
      renderLayer()
      expect(screen.getByTestId('workspace-dialog-layer')).toBeInTheDocument()
      expect(screen.getByText('Strg+K öffnet die Suche.')).toBeInTheDocument()
      expect(screen.queryByRole('textbox', { name: 'Belege und Apps suchen' })).not.toBeInTheDocument()
      expect(screen.queryByRole('heading', { name: 'Treffer' })).not.toBeInTheDocument()

      await user.click(screen.getByRole('button', { name: 'Suche öffnen' }))

      expect(keys.some(isPaletteShortcut)).toBe(true)
      expect(postMock).not.toHaveBeenCalled()
    } finally {
      window.removeEventListener('keydown', onKey, true)
    }
  })

  it('sendet denselben Strg+K-Tastendruck, den die Palette schon hoert', () => {
    const keys: KeyboardEvent[] = []
    const onKey = (event: Event): void => {
      keys.push(event as KeyboardEvent)
    }
    window.addEventListener('keydown', onKey, true)
    try {
      requestExistingCommandPalette()
      expect(keys).toHaveLength(1)
      expect(isPaletteShortcut(keys[0])).toBe(true)
      expect(keys[0].cancelable).toBe(true)
    } finally {
      window.removeEventListener('keydown', onKey, true)
    }
  })
})
