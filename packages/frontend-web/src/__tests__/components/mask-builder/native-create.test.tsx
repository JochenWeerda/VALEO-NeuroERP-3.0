import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { MemoryRouter } from '@/app/routing/test-router'

const mocks = vi.hoisted(() => ({
  post: vi.fn(), get: vi.fn(), navigate: vi.fn(), roles: ['admin'],
  definition: undefined as ScreenDefinition | undefined,
}))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: mocks.definition, isError: false }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: mocks.post, get: mocks.get }, getAxiosErrorMessage: () => 'Fehler' }))
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
  return render(<MemoryRouter><QueryClientProvider client={client}><UniversalNativeCreatePage screenId={mocks.definition?.id ?? 'crm/lead'} /></QueryClientProvider></MemoryRouter>)
}
beforeEach(() => {
  mocks.post.mockReset(); mocks.get.mockReset(); mocks.navigate.mockReset(); mocks.roles = ['admin']; mocks.definition = definition
})

describe('native document creation uses the same real renderer and form state', () => {
  beforeEach(() => {
    mocks.definition = {
      ...definition, id: 'beleg/sales-offer', domain: 'sales', title: 'Angebot',
      adapter: { type: 'native', temporary: false, sourceId: 'beleg/sales-offer' },
      documentVariant: { family: 'beleg', variantId: 'sales_offer', baseVersion: '1.2.0', variantVersion: '1.2.0',
        baseHash: 'a'.repeat(64), variantHash: 'b'.repeat(64), materializedHash: 'c'.repeat(64) },
      creationContext: { screen_id: 'beleg/sales-offer', definition_hash: 'd'.repeat(64) },
      creation: { adapter: 'docflow.create.v1', endpoint: '/api/v1/docflow/', permission: 'belege.bearbeiten',
        detailRoute: '/belege/sales_offer/{entity_id}', defaults: { items: [{ article_number: 'SYNTHETIC', quantity: 1, unit_price: 10 }] },
        dataSources: [{ key: 'partner', endpoint: '/api/v1/belege/sales_offer/partner-auswahl' }], fields: [
          { key: 'doc_number', label: 'Entwurfsbezeichnung', type: 'text', required: true },
          { key: 'customer_id', label: 'Kunde', type: 'lookup', dataSourceKey: 'partner', required: true },
          { key: 'items', label: 'Positionen', type: 'table', required: true, rowFields: [
            { key: 'article_number', label: 'Artikel', type: 'text', required: true },
            { key: 'quantity', label: 'Menge', type: 'number', required: true }], tableEditing: { allowAdd: true, allowDelete: true } },
        ] },
    }
    mocks.get.mockResolvedValue({ data: { items: [{ value: 'synthetic-customer', label: 'KD-SYNTH - Testbetrieb' }] } })
  })
  async function fill() {
    mount()
    fireEvent.change(screen.getByLabelText('Entwurfsbezeichnung'), { target: { value: 'SYNTHETIC DRAFT' } })
    fireEvent.change(screen.getByLabelText('Kunde'), { target: { value: 'Testbetrieb' } })
    fireEvent.click(await screen.findByRole('option', { name: 'KD-SYNTH - Testbetrieb' }))
  }
  it('selects a named partner and preserves one creation key and input after an uncertain transport', async () => {
    mocks.post.mockRejectedValueOnce(new Error('Transport unklar')).mockImplementation(async (_endpoint, payload) => ({
      data: { id: 'new-document', doc_type: 'sales_offer', status: 'draft', version: 1, screen_context: payload.screen_context },
    }))
    await fill()
    expect(screen.queryByLabelText('Unternehmen')).not.toBeInTheDocument()
    fireEvent.click(screen.getByTestId('form-submit-btn'))
    await waitFor(() => expect(screen.getAllByText(/Transport unklar/).length).toBeGreaterThan(0))
    expect(screen.getByLabelText('Entwurfsbezeichnung')).toHaveValue('SYNTHETIC DRAFT')
    fireEvent.click(screen.getByTestId('form-submit-btn'))
    await waitFor(() => expect(mocks.navigate).toHaveBeenCalledWith('/belege/sales_offer/new-document'))
    expect(mocks.post.mock.calls[1][1]).toEqual(mocks.post.mock.calls[0][1])
    expect(mocks.post.mock.calls[0][1]).toMatchObject({ customer_id: 'synthetic-customer', doc_type: 'sales_offer', status: 'draft' })
  })
  it('rejects a response for another document variant instead of navigating', async () => {
    mocks.post.mockResolvedValue({ data: { id: 'foreign', doc_type: 'purchase_invoice', status: 'draft', version: 1 } })
    await fill()
    fireEvent.click(screen.getByTestId('form-submit-btn'))
    await waitFor(() => expect(screen.getAllByText(/Anlageantwort entspricht nicht/).length).toBeGreaterThan(0))
    expect(mocks.navigate).not.toHaveBeenCalled()
  })
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
    mocks.navigate.mockImplementation(() => {
      expect(screen.queryByText('Ungespeicherte Änderungen')).not.toBeInTheDocument()
      expect(screen.getByTestId('form-submit-btn')).toBeDisabled()
    })
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
