import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { MemoryRouter } from '@/app/routing/test-router'

const mocks = vi.hoisted(() => ({
  post: vi.fn(), navigate: vi.fn(), roles: ['admin'],
  definition: undefined as ScreenDefinition | undefined,
}))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: mocks.definition, isError: false }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: mocks.post }, getAxiosErrorMessage: () => 'Fehler' }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { sub: 'test', scopes: [], roles: mocks.roles } }) }))
vi.mock('@/app/routing/typed-router', async importOriginal => ({
  ...await importOriginal<object>(), useNavigate: () => mocks.navigate,
}))

const definition: ScreenDefinition = {
  schemaVersion: 1, id: 'crm/lead', domain: 'crm', mode: 'detail', title: 'Kundenakte',
  subtitle: 'CRM / Interessent', adapter: { type: 'native', sourceId: 'crm/lead', temporary: false },
  creation: { endpoint: '/api/v1/crm/leads', permission: 'crm.lead.create',
    detailRoute: '/crm/lead/{entity_id}', defaults: { source: 'unknown', status: 'NEW', priority: 'medium' } },
  dataSources: [{ key: 'entity', endpoint: '/api/v1/crm/leads/{entity_id}' }],
  tabs: [{ key: 'kopf', label: 'Lead-Daten', dataSourceKey: 'entity', fields: [
    { key: 'company_name', label: 'Unternehmen', type: 'text', required: true },
    { key: 'contact_person', label: 'Ansprechpartner', type: 'text' },
    { key: 'source', label: 'Quelle', type: 'text' },
    { key: 'status', label: 'Status', type: 'text' },
    { key: 'priority', label: 'Priorität', type: 'text' },
    { key: 'tenant_id', label: 'Mandant', type: 'text', readOnly: true },
  ] }],
  layout: { floorplan: 'objectPage', density: 'compact', contextRail: 'none' },
}
function mount() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<MemoryRouter><QueryClientProvider client={client}><UniversalNativeCreatePage screenId="crm/lead" /></QueryClientProvider></MemoryRouter>)
}
beforeEach(() => {
  mocks.post.mockReset(); mocks.navigate.mockReset(); mocks.roles = ['admin']; mocks.definition = definition
})
describe('native creation contract', () => {
  it('renders real fields with defaults without requesting a fictitious entity', () => {
    mount()
    expect(screen.getByLabelText('Unternehmen')).toBeVisible()
    expect(screen.getByLabelText('Quelle')).toHaveValue('unknown')
    expect(screen.getByTestId('form-submit-btn')).toBeDisabled()
    expect(mocks.post).not.toHaveBeenCalled()
  })
  it('creates through the canonical API and opens the returned identity', async () => {
    mocks.post.mockResolvedValue({ data: { id: 'lead/42' } })
    mount()
    fireEvent.change(screen.getByLabelText('Unternehmen'), { target: { value: 'Test GmbH' } })
    fireEvent.click(screen.getByTestId('form-submit-btn'))
    await waitFor(() => expect(mocks.navigate).toHaveBeenCalledWith('/crm/lead/lead%2F42'))
    expect(mocks.post).toHaveBeenCalledExactlyOnceWith('/api/v1/crm/leads', {
      company_name: 'Test GmbH', source: 'unknown', status: 'NEW', priority: 'medium',
    })
  })
  it('reports save failures and does not navigate', async () => {
    mocks.post.mockRejectedValue(new Error('Speichern fehlgeschlagen'))
    mount()
    fireEvent.change(screen.getByLabelText('Unternehmen'), { target: { value: 'Test GmbH' } })
    fireEvent.click(screen.getByTestId('form-submit-btn'))
    await waitFor(() => expect(screen.getAllByText(/Speichern fehlgeschlagen/).length).toBeGreaterThan(0))
    expect(mocks.navigate).not.toHaveBeenCalled()
  })
  it('denies read-only users before exposing a writable form', () => {
    mocks.roles = ['CRM_LESEN']
    mount()
    expect(screen.getByRole('alert')).toHaveTextContent('Keine Berechtigung')
    expect(screen.queryByLabelText('Unternehmen')).not.toBeInTheDocument()
    expect(mocks.post).not.toHaveBeenCalled()
  })
})
