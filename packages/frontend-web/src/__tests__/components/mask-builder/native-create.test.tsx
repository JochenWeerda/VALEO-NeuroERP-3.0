import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as domMatchers from '@testing-library/jest-dom/matchers'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { MemoryRouter } from '@/app/routing/test-router'
import prepared from '../../fixtures/inbox-prepared-synthetic.json'
import { auth } from '@/lib/auth'

expect.extend(domMatchers)

const mocks = vi.hoisted(() => ({
  post: vi.fn(), get: vi.fn(), navigate: vi.fn(), roles: ['admin'], sub: 'test', token: '',
  definition: undefined as ScreenDefinition | undefined,
}))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: mocks.definition, isError: false }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: mocks.post, get: mocks.get }, getAxiosErrorMessage: () => 'Fehler' }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: mocks.sub ? { sub: mocks.sub, scopes: [], roles: mocks.roles } : null }) }))
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
function mount(entry = '/') {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return { ...render(<MemoryRouter initialEntries={[entry]}><QueryClientProvider client={client}><UniversalNativeCreatePage screenId={mocks.definition?.id ?? 'crm/lead'} /></QueryClientProvider></MemoryRouter>), client }
}
function fakeTenantToken(tenantId: string, refresh = 'first'): string {
  return ['header', btoa(JSON.stringify({ tenant_id: tenantId, refresh })), 'test-signature'].join('.')
}
beforeEach(() => {
  mocks.post.mockReset(); mocks.get.mockReset(); mocks.navigate.mockReset(); mocks.roles = ['admin']; mocks.sub = 'test'; mocks.token = fakeTenantToken('tenant-a'); mocks.definition = definition
  vi.spyOn(auth, 'getAccessToken').mockImplementation(() => mocks.token || null)
})

describe('native purchase invoice from an authorized Inbox pointer', () => {
  beforeEach(() => {
    mocks.definition = {
      ...definition, id: 'beleg/purchase-invoice', domain: 'einkauf', title: 'Eingangsrechnung',
      documentVariant: { family: 'beleg', variantId: 'purchase_invoice', baseVersion: '1.2.0', variantVersion: '1.2.0',
        baseHash: 'a'.repeat(64), variantHash: 'b'.repeat(64), materializedHash: 'c'.repeat(64) },
      creationContext: { screen_id: 'beleg/purchase-invoice', definition_hash: 'd'.repeat(64) },
      creation: { adapter: 'docflow.create.v1', endpoint: '/api/v1/docflow/', permission: 'belege.bearbeiten',
        detailRoute: '/belege/purchase_invoice/{entity_id}', defaults: { currency: 'USD', items: [{ article_number: 'SYNTH', quantity: 1, unit_price: 10 }] },
        fields: [
          { key: 'doc_number', label: 'Belegnummer', type: 'text', required: true },
          { key: 'supplier_id', label: 'Lieferant', type: 'text', required: true },
          { key: 'currency', label: 'Währung', type: 'text' },
          { key: 'source_ref', label: 'Quellreferenz', type: 'text' },
          { key: 'tenant_id', label: 'Mandant', type: 'text', readOnly: true },
          { key: 'items', label: 'Positionen', type: 'table', required: true, rowFields: [
            { key: 'article_number', label: 'Artikel', type: 'text', required: true },
            { key: 'quantity', label: 'Menge', type: 'number', required: true }], tableEditing: { allowAdd: true, allowDelete: true } },
        ] },
    }
  })
  const entry = '/belege/purchase_invoice/neu?inbox=SYNTH-INBOX-1'
  it('loads the exact proposal before rendering, maps editable header fields, and saves only on explicit click', async () => {
    let resolvePrepare!: (value: unknown) => void
    mocks.post.mockReturnValueOnce(new Promise(resolve => { resolvePrepare = resolve }))
      .mockImplementation(async (_endpoint, payload) => ({ data: { id: 'draft-1', doc_type: 'purchase_invoice', status: 'draft', version: 1, screen_context: payload.screen_context } }))
    mount(entry)
    expect(screen.getByRole('status')).toHaveTextContent('Inbox-Vorschlag wird geprüft')
    expect(screen.queryByLabelText('Belegnummer')).not.toBeInTheDocument()
    resolvePrepare({ data: structuredClone(prepared) })
    expect(await screen.findByLabelText('Belegnummer')).toHaveValue('SYNTH-RE-1')
    expect(screen.getByLabelText('Lieferant')).toHaveValue('TEST-L-1')
    expect(screen.getByLabelText('Währung')).toHaveValue('EUR')
    expect(mocks.post).toHaveBeenCalledTimes(1)
    fireEvent.change(screen.getByLabelText('Belegnummer'), { target: { value: 'SYNTH-EDIT' } })
    fireEvent.click(screen.getByTestId('form-submit-btn'))
    await waitFor(() => expect(mocks.navigate).toHaveBeenCalledWith('/belege/purchase_invoice/draft-1'))
    expect(mocks.post.mock.calls[1][1]).toMatchObject({ doc_number: 'SYNTH-EDIT', supplier_id: 'TEST-L-1', currency: 'EUR', doc_type: 'purchase_invoice', status: 'draft' })
    expect(mocks.post.mock.calls[1][1]).not.toHaveProperty('tenant_id')
    expect(mocks.post.mock.calls[1][1]).not.toHaveProperty('booking')
  })
  it.each(['foreign-id', 'booking', 'denied', 'wrong-kind', 'wrong-variant', 'old-schema', 'forbidden', 'missing'])('blocks %s without exposing a form or creating a draft', async reason => {
    const data = structuredClone(prepared)
    if (reason === 'foreign-id') data.item.id = 'OTHER'
    if (reason === 'booking') data.booking_allowed = true
    if (reason === 'denied') data.item.can_open = false
    if (reason === 'wrong-kind') data.item.proposal.document_kind = 'LIEFERSCHEIN'
    if (reason === 'wrong-variant') data.item.proposal.belegart = 'sales_invoice'
    if (reason === 'old-schema') data.item.command.prefill.schema = 'valeo.inbox.prefill.v0'
    if (reason === 'forbidden') mocks.post.mockRejectedValueOnce(new Error('403'))
    else if (reason === 'missing') mocks.post.mockRejectedValueOnce(new Error('404'))
    else mocks.post.mockResolvedValueOnce({ data })
    mount(entry)
    expect(await screen.findByRole('alert')).toHaveTextContent('Inbox-Vorschlag konnte nicht geprüft werden')
    expect(screen.queryByLabelText('Belegnummer')).not.toBeInTheDocument()
    expect(mocks.post).toHaveBeenCalledTimes(1)
  })
  it('does not call prepare or render a form without creation permission', () => {
    mocks.roles = ['CRM_LESEN']
    mount(entry)
    expect(screen.getByRole('alert')).toHaveTextContent('Keine Berechtigung')
    expect(screen.queryByLabelText('Belegnummer')).not.toBeInTheDocument()
    expect(mocks.post).not.toHaveBeenCalled()
  })
  it('hides previously prepared fields immediately when the principal changes', async () => {
    mocks.post.mockResolvedValueOnce({ data: structuredClone(prepared) })
    const rendered = mount(entry)
    expect(await screen.findByLabelText('Belegnummer')).toHaveValue('SYNTH-RE-1')
    mocks.sub = 'other-user'
    mocks.post.mockReturnValueOnce(new Promise(() => {}))
    rendered.rerender(<MemoryRouter initialEntries={[entry]}><QueryClientProvider client={rendered.client}><UniversalNativeCreatePage screenId="beleg/purchase-invoice" /></QueryClientProvider></MemoryRouter>)
    expect(screen.queryByLabelText('Belegnummer')).not.toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('Inbox-Vorschlag wird geprüft')
  })
  it('isolates a same-subject tenant switch even when the browser tenant is unchanged', async () => {
    localStorage.setItem('tenant_id', 'stale-browser-tenant')
    mocks.post.mockResolvedValueOnce({ data: structuredClone(prepared) })
    const rendered = mount(entry)
    expect(await screen.findByLabelText('Belegnummer')).toHaveValue('SYNTH-RE-1')
    let resolveOtherTenant!: (value: unknown) => void
    mocks.post.mockReturnValueOnce(new Promise(resolve => { resolveOtherTenant = resolve }))
    mocks.token = fakeTenantToken('tenant-b')
    rendered.rerender(<MemoryRouter initialEntries={[entry]}><QueryClientProvider client={rendered.client}><UniversalNativeCreatePage screenId="beleg/purchase-invoice" /></QueryClientProvider></MemoryRouter>)
    expect(screen.queryByLabelText('Belegnummer')).not.toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveTextContent('Inbox-Vorschlag wird geprüft')
    expect(mocks.post).toHaveBeenCalledTimes(2)
    expect(mocks.post.mock.calls.every(call => call[0] !== '/api/v1/docflow/')).toBe(true)
    const otherTenant = structuredClone(prepared)
    otherTenant.item.command.prefill.documentNumber = 'TENANT-B-RE'
    resolveOtherTenant({ data: otherTenant })
    expect(await screen.findByLabelText('Belegnummer')).toHaveValue('TENANT-B-RE')
    expect(localStorage.getItem('tenant_id')).toBe('stale-browser-tenant')
    localStorage.removeItem('tenant_id')
  })
  it('keeps edited values across a token refresh for the same tenant', async () => {
    mocks.post.mockResolvedValueOnce({ data: structuredClone(prepared) })
    const rendered = mount(entry)
    const number = await screen.findByLabelText('Belegnummer')
    fireEvent.change(number, { target: { value: 'USER-EDIT' } })
    mocks.token = fakeTenantToken('tenant-a', 'refreshed')
    rendered.rerender(<MemoryRouter initialEntries={[entry]}><QueryClientProvider client={rendered.client}><UniversalNativeCreatePage screenId="beleg/purchase-invoice" /></QueryClientProvider></MemoryRouter>)
    expect(screen.getByLabelText('Belegnummer')).toHaveValue('USER-EDIT')
    expect(mocks.post).toHaveBeenCalledTimes(1)
  })
  it('keeps edited values after a fresh prepare refetch for the same identity', async () => {
    mocks.post.mockResolvedValueOnce({ data: structuredClone(prepared) })
    const rendered = mount(entry)
    fireEvent.change(await screen.findByLabelText('Belegnummer'), { target: { value: 'USER-EDIT' } })
    let resolveRefetch!: (value: unknown) => void
    mocks.post.mockReturnValueOnce(new Promise(resolve => { resolveRefetch = resolve }))
    void rendered.client.invalidateQueries({ queryKey: ['native-create-inbox-prepare'] })
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Inbox-Vorschlag wird geprüft'))
    const refreshed = structuredClone(prepared)
    refreshed.item.command.prefill.documentNumber = 'LATER-SUGGESTION'
    resolveRefetch({ data: refreshed })
    expect(await screen.findByLabelText('Belegnummer')).toHaveValue('USER-EDIT')
    expect(mocks.post).toHaveBeenCalledTimes(2)
  })
  it('fails closed when the authenticated token has no tenant claim', () => {
    mocks.token = fakeTenantToken('')
    mount(entry)
    expect(screen.getByRole('alert')).toHaveTextContent('Mandant der Anmeldung')
    expect(screen.queryByLabelText('Belegnummer')).not.toBeInTheDocument()
    expect(mocks.post).not.toHaveBeenCalled()
  })
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
