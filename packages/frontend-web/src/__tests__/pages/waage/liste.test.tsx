import { renderStudio as render } from '@/__tests__/helpers/studio-intake-render'
import { fireEvent, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import WaageListePage from '@/pages/waage/liste'

const { navigateMock, getMock } = vi.hoisted(() => ({ navigateMock: vi.fn(), getMock: vi.fn() }))
vi.mock('@/app/routing/typed-router', async () => ({
  ...await vi.importActual('@/app/routing/typed-router'), useNavigate: () => navigateMock,
}))
vi.mock('@/lib/api-client', async () => ({
  ...await vi.importActual('@/lib/api-client'), apiClient: { get: getMock },
}))
vi.mock('@/lib/api/masks', async () => {
  const fixtures = (await import('@/__tests__/fixtures/intake-weighing-screens.json')).default
  return { useScreenDefinition: (id: string) => ({ data: (fixtures as Record<string, unknown>)[id], isLoading: false, error: null }) }
})
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({
  useScreenPermissions: (definition: { actions?: Array<{ permission?: string }> }) => definition?.actions?.flatMap(action => action.permission ? [action.permission] : []) ?? [],
}))
vi.mock('@/lib/api/ux-overlays', () => ({
  useUserScreenOverlay: () => ({ data: undefined }), overlayKeys: { screen: (id: string) => ['test-overlay', id] },
  saveUserOverlay: vi.fn(), deleteUserOverlay: vi.fn(),
}))
vi.mock('@/components/mask-builder/specialized/intake/domain-data', () => ({
  useDomainIdentity: () => ({ tenantId: 'test-tenant', actor: 'test-operator' }),
  useDomainSupplyChain: () => ({ data: null }),
}))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => true }))
vi.mock('@/hooks/useKeyboardShortcuts', () => ({ buildCoreMaskShortcuts: () => [], useKeyboardShortcuts: () => undefined }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))

const scales = [
  { id: 'W-001', standort: 'Annahme 1', typ: 'LKW-Waage', max_kapazitaet: 60, letzte_eichung: '2025-08-15', naechste_eichung: '2099-08-15', status: 'aktiv' },
  { id: 'W-002', standort: 'Verladung', typ: 'Bodenwaage', max_kapazitaet: 30, letzte_eichung: '2025-06-01', naechste_eichung: '2099-06-30', status: 'wartung' },
]

function renderPage() { render(<MemoryRouter><WaageListePage /></MemoryRouter>) }

describe('Waagenliste über Studio', () => {
  beforeEach(() => {
    navigateMock.mockReset()
    getMock.mockReset()
    getMock.mockImplementation(async (url: string) => ({ data: url.includes('fehlerqueue') ? [] : scales }))
  })

  it('zeigt eine leere Liste ohne erfundene Waagen', async () => {
    getMock.mockResolvedValue({ data: [] })
    renderPage()
    expect(await screen.findByText('Keine Einträge vorhanden.')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Hofliste für .* öffnen/ })).not.toBeInTheDocument()
  })

  it('meldet einen API-Fehler und lädt nach erneutem Versuch echte Daten', async () => {
    let failed = true
    getMock.mockImplementation(async (url: string) => {
      if (url.includes('fehlerqueue')) return { data: [] }
      if (failed) throw new Error('Waagenabruf fehlgeschlagen')
      return { data: scales }
    })
    renderPage()
    expect(await screen.findByRole('heading', { name: 'Backend nicht erreichbar' })).toBeInTheDocument()
    expect(screen.getByText('Waagenabruf fehlgeschlagen')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /Hofliste für .* öffnen/ })).not.toBeInTheDocument()
    failed = false
    fireEvent.click(screen.getByRole('button', { name: 'Erneut versuchen' }))
    expect(await screen.findByRole('button', { name: 'Hofliste für Annahme 1 öffnen' })).toBeInTheDocument()
  })
  it('lädt und zeigt Waagen mit Standort und Typ', async () => {
    renderPage()
    expect(await screen.findByRole('heading', { name: 'Waagen', level: 1 })).toBeInTheDocument()
    expect(await screen.findByRole('button', { name: 'Hofliste für Annahme 1 öffnen' })).toBeInTheDocument()
    expect(screen.getByText('Bodenwaage')).toBeInTheDocument()
    expect(getMock).toHaveBeenCalledWith('/api/v1/waage/waagen?limit=1000')
  })

  it('öffnet die Hofliste über die Studio-Aktion', async () => {
    renderPage()
    await screen.findByRole('button', { name: 'Hofliste für Annahme 1 öffnen' })
    fireEvent.click(screen.getByRole('button', { name: 'Hofliste', exact: true }))
    expect(navigateMock).toHaveBeenCalledWith('/waage/hofliste')
  })

  it('filtert die sichtbaren Waagen nach Standort und Typ', async () => {
    renderPage()
    await screen.findByRole('button', { name: 'Hofliste für Annahme 1 öffnen' })
    const search = screen.getByLabelText('Suche Waagen')
    fireEvent.change(search, { target: { value: 'boden' } })
    expect(screen.queryByRole('button', { name: 'Hofliste für Annahme 1 öffnen' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Hofliste für Verladung öffnen' })).toBeInTheDocument()
    fireEvent.change(search, { target: { value: 'annahme' } })
    expect(screen.getByRole('button', { name: 'Hofliste für Annahme 1 öffnen' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Hofliste für Verladung öffnen' })).not.toBeInTheDocument()
  })
})
