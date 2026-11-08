import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from '@/app/routing/test-router'
import Page from '@/pages/crm/campaign-template-detail'
import definition from './campaign-template-studio.fixture.json'

const m = vi.hoisted(() => ({ id: 'template-1', roles: ['admin'], get: vi.fn(), post: vi.fn(), request: vi.fn(), navigate: vi.fn() }))
vi.mock('@/app/routing/typed-router', async original => ({ ...await original<object>(), useParams: () => ({ id: m.id }), useNavigate: () => m.navigate }))
vi.mock('@tanstack/react-router', async original => ({ ...await original<object>(), useNavigate: () => m.navigate }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { sub: 'test', scopes: [], roles: m.roles } }) }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: definition, isError: false }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: m.get, post: m.post, request: m.request }, getAxiosErrorMessage: (e: unknown) => String(e) }))
vi.mock('@/lib/api/ux-overlays', () => ({ useUserScreenOverlay: () => ({ data: undefined, refetch: vi.fn().mockResolvedValue({}) }), deleteUserOverlay: vi.fn(), saveUserOverlay: vi.fn(), overlayKeys: {} }))

const entity = { id: 'template-1', tenant_id: 'tenant-a', name: 'Sommer', description: 'Alt', campaign_type: 'sms', subject_line: 'Hallo', message_body: 'Text', is_active: true, meta: { secret: true } }
function mount() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  render(<MemoryRouter><QueryClientProvider client={client}><Page /></QueryClientProvider></MemoryRouter>)
}
beforeEach(() => {
  vi.clearAllMocks(); m.id = 'template-1'; m.roles = ['admin']
  m.get.mockResolvedValue({ data: entity }); m.post.mockResolvedValue({ data: { id: 'created-1' } })
  m.request.mockResolvedValue({ data: { id: 'template-1' } })
})

describe('Kampagnenvorlage durch Studio-Runtime', () => {
  it('lädt die konkrete ID und übernimmt sechs Eingaben ohne Mandant oder Metadaten', async () => {
    mount()
    await waitFor(() => expect(m.get).toHaveBeenCalledWith('/api/v1/crm/campaigns/templates/template-1'))
    fireEvent.click(await screen.findByRole('button', { name: 'Bearbeiten' }))
    const dialog = await screen.findByRole('dialog')
    expect(within(dialog).getByLabelText(/Name/)).toHaveValue('Sommer')
    expect(within(dialog).getByLabelText('Beschreibung')).toHaveValue('Alt')
    expect(within(dialog).getByLabelText(/Kampagnentyp/)).toHaveValue('sms')
    expect(within(dialog).getByLabelText('Betreff')).toHaveValue('Hallo')
    expect(within(dialog).getByLabelText('Nachricht')).toHaveValue('Text')
    expect(within(dialog).getByLabelText('Aktiv')).toBeChecked()
    fireEvent.change(within(dialog).getByLabelText('Beschreibung'), { target: { value: 'Neu' } })
    fireEvent.click(within(dialog).getByRole('button', { name: 'Weiter' }))
    await waitFor(() => expect(m.request).toHaveBeenCalled())
    expect(m.request.mock.calls[0][0]).toMatchObject({ method: 'PUT', url: '/api/v1/crm/campaigns/templates/template-1', data: { name: 'Sommer', description: 'Neu', campaign_type: 'sms', subject_line: 'Hallo', message_body: 'Text', is_active: true } })
    expect(m.request.mock.calls[0][0].data).not.toHaveProperty('tenant_id')
    expect(m.request.mock.calls[0][0].data).not.toHaveProperty('meta')
  })
  it('dupliziert und navigiert zur zurückgegebenen neuen ID', async () => {
    m.request.mockResolvedValue({ data: { id: 'copy-1' } }); mount()
    fireEvent.click(await screen.findByRole('button', { name: 'Duplizieren' }))
    await waitFor(() => expect(m.navigate).toHaveBeenCalledWith(expect.objectContaining({ to: '/crm/campaign-template/copy-1' })))
    expect(m.request.mock.calls[0][0]).toMatchObject({ method: 'POST', url: '/api/v1/crm/campaigns/templates/template-1/duplicate', data: {} })
  })
  it('meldet einen Serverfehler und navigiert nicht', async () => {
    m.request.mockRejectedValue(new Error('Serverfehler')); mount()
    fireEvent.click(await screen.findByRole('button', { name: 'Duplizieren' }))
    expect(await screen.findByText(/Serverfehler/)).toBeInTheDocument()
    expect(m.navigate).not.toHaveBeenCalled()
  })
  it('sperrt die Anlage ohne Berechtigung', async () => {
    m.id = 'new'; m.roles = []; mount()
    expect(await screen.findByRole('alert')).toHaveTextContent('Keine Berechtigung')
    expect(m.post).not.toHaveBeenCalled(); expect(m.get).not.toHaveBeenCalled()
  })
  it('legt neu an ohne Entity-Abruf und navigiert zur Antwort-ID', async () => {
    m.id = 'new'; mount()
    fireEvent.change(await screen.findByLabelText(/Name/), { target: { value: 'Neue Vorlage' } })
    fireEvent.click(screen.getByTestId('form-submit-btn'))
    await waitFor(() => expect(m.post).toHaveBeenCalledWith('/api/v1/crm/campaigns/templates', expect.objectContaining({ name: 'Neue Vorlage', campaign_type: 'email', is_active: true })))
    expect(m.post.mock.calls[0][1]).not.toHaveProperty('meta')
    expect(m.get).not.toHaveBeenCalled()
    await waitFor(() => expect(m.navigate).toHaveBeenCalledWith('/crm/campaign-template/created-1'))
  })
  it('bricht die Neuanlage ohne Schreiben ab', async () => {
    m.id = 'neu'; mount()
    fireEvent.click(await screen.findByRole('button', { name: 'Abbrechen' }))
    expect(m.navigate).toHaveBeenCalledWith('/crm/campaign-templates')
    expect(m.post).not.toHaveBeenCalled(); expect(m.get).not.toHaveBeenCalled()
  })
})
