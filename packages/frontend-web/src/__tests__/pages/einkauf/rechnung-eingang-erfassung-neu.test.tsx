import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from '@/app/routing/test-router'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import {
  INBOX_PREFILL_SCHEMA,
  INBOX_PREFILL_STORAGE_KEY,
  INBOX_SUPPLIER_INVOICE_CREATE_ROUTE,
  storeInboxPrefill,
  type InboxPrefillPayload,
} from '@/components/adaptive-workspace/inbox'

const mocks = vi.hoisted(() => ({
  post: vi.fn(),
  get: vi.fn(),
  navigate: vi.fn(),
  roles: ['EINKAUF_BEARBEITEN'],
  definition: undefined as ScreenDefinition | undefined,
}))

vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: () => ({ data: mocks.definition, isError: false }),
}))
vi.mock('@/lib/api-client', () => ({
  apiClient: { post: mocks.post, get: mocks.get },
  getAxiosErrorMessage: () => 'Fehler',
}))
vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ user: { sub: 'test', scopes: [], roles: mocks.roles } }),
}))
vi.mock('@/app/routing/typed-router', async (importOriginal) => ({
  ...(await importOriginal<object>()),
  useNavigate: () => mocks.navigate,
}))

import RechnungEingangErfassungNeuPage from '@/pages/einkauf/rechnung-eingang-erfassung-neu'

const definition: ScreenDefinition = {
  schemaVersion: 1,
  id: 'beleg/purchase-invoice',
  domain: 'einkauf',
  mode: 'detail',
  title: 'Eingangsrechnung',
  subtitle: 'Lieferant · mit Preisen',
  adapter: { type: 'native', sourceId: 'beleg/purchase-invoice', temporary: false },
  documentVariant: {
    family: 'beleg',
    variantId: 'purchase_invoice',
    baseVersion: '1.2.0',
    variantVersion: '1.2.0',
    baseHash: 'a'.repeat(64),
    variantHash: 'b'.repeat(64),
    materializedHash: 'c'.repeat(64),
  },
  creationContext: { screen_id: 'beleg/purchase-invoice', definition_hash: 'd'.repeat(64) },
  creation: {
    adapter: 'docflow.create.v1',
    endpoint: '/api/v1/docflow/',
    permission: 'belege.bearbeiten',
    detailRoute: '/belege/purchase_invoice/{entity_id}',
    defaults: { currency: 'EUR', items: [] },
    dataSources: [{ key: 'partner', endpoint: '/api/v1/belege/purchase_invoice/partner-auswahl' }],
    fields: [
      { key: 'doc_number', label: 'Entwurfsbezeichnung', type: 'text', required: true },
      { key: 'supplier_id', label: 'Lieferant', type: 'lookup', dataSourceKey: 'partner', required: true },
      { key: 'document_date', label: 'Belegdatum', type: 'date', required: true },
      { key: 'currency', label: 'Waehrung', type: 'text', required: true },
      { key: 'source_ref', label: 'Externe Referenz', type: 'text' },
    ],
  },
  dataSources: [],
  layout: { floorplan: 'transaction', density: 'compact', contextRail: 'workflow' },
}

function samplePrefill(overrides: Partial<InboxPrefillPayload> = {}): InboxPrefillPayload {
  return {
    schema: INBOX_PREFILL_SCHEMA,
    documentId: 'INBOX-44',
    documentNumber: 'RE-44',
    partner: { id: 'L-22', number: 'L-22', name: 'Nordkorn AG', role: 'supplier' },
    amounts: { total: '1280.50', tax: '204.29', currency: 'EUR' },
    source: { kind: 'dms_inbox', id: 'INBOX-44', dmsDocumentId: 44, classification: 'parsed-or-ocr-hint' },
    confidence: 0.72,
    confidenceBand: 'medium',
    policyId: 'incoming-supplier-invoice',
    documentType: 'supplier_invoice',
    targetRoute: '/einkauf/rechnung-eingang-erfassung',
    booking: false,
    matchValues: { invoiceNumber: 'RE-44', supplierId: 'L-22', date: '2026-10-22' },
    storageKey: INBOX_PREFILL_STORAGE_KEY,
    maskConsumesPrefill: true,
    ...overrides,
  }
}

function mount() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <MemoryRouter>
      <QueryClientProvider client={client}>
        <RechnungEingangErfassungNeuPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

describe('Eingangsrechnung Create-Host', () => {
  beforeEach(() => {
    sessionStorage.clear()
    mocks.post.mockReset()
    mocks.get.mockReset()
    mocks.navigate.mockReset()
    mocks.roles = ['EINKAUF_BEARBEITEN']
    mocks.definition = definition
    mocks.get.mockResolvedValue({ data: { items: [] } })
  })

  it('füllt Felder aus valeo.inbox.prefill, zeigt Konfidenz und leert den Speicher', async () => {
    storeInboxPrefill(samplePrefill())
    mount()

    expect(screen.getByTestId('screen-einkauf/rechnung-eingang-erfassung-neu')).toBeInTheDocument()
    expect(screen.getByTestId('inbox-prefill-banner')).toHaveTextContent('72')
    expect(screen.getByTestId('inbox-prefill-banner')).toHaveTextContent('mittel')
    expect(screen.getByTestId('inbox-prefill-banner')).toHaveTextContent('Nordkorn AG')
    expect(screen.getByLabelText('Entwurfsbezeichnung')).toHaveValue('RE-44')
    expect(screen.getByLabelText('Lieferant')).toHaveValue('L-22')
    expect(screen.getByLabelText('Belegdatum')).toHaveValue('2026-10-22')
    expect(screen.getByLabelText('Waehrung')).toHaveValue('EUR')
    expect(screen.getByLabelText('Externe Referenz')).toHaveValue('RE-44')
    expect(screen.getByTestId('inbox-prefill-banner')).toHaveTextContent('nicht über die Inbox')
    await waitFor(() => expect(sessionStorage.getItem(INBOX_PREFILL_STORAGE_KEY)).toBeNull())
    expect(mocks.post).not.toHaveBeenCalled()
  })

  it('öffnet ohne Prefill die leere Anlagemaske', () => {
    mount()
    expect(screen.queryByTestId('inbox-prefill-banner')).not.toBeInTheDocument()
    expect(screen.getByLabelText('Entwurfsbezeichnung')).toHaveValue('')
    expect(screen.getByLabelText('Waehrung')).toHaveValue('EUR')
  })
})

describe('Listen-Route bleibt Liste', () => {
  it('hält /einkauf/rechnung-eingang-erfassung als NativeListPage', () => {
    const src = readFileSync(
      resolve(__dirname, '../../../pages/einkauf/rechnung-eingang-erfassung.tsx'),
      'utf8',
    )
    expect(src).toContain('NativeListPage')
    expect(src).toContain('screenId="einkauf/rechnung-eingang-erfassung"')
    expect(src).not.toContain('readInboxPrefill')
    expect(src).not.toContain('UniversalNativeCreatePage')
  })

  it('registriert die Create-Route additiv neben der Liste', () => {
    const { aliases } = JSON.parse(
      readFileSync(resolve(__dirname, '../../../app/route-aliases.json'), 'utf8'),
    ) as { aliases: Array<{ module: string; path: string }> }
    const list = aliases.filter((entry) => entry.path === 'einkauf/rechnung-eingang-erfassung')
    const create = aliases.filter((entry) => entry.path === 'einkauf/rechnung-eingang-erfassung/neu')
    expect(list.map((entry) => entry.module)).toEqual(['@/pages/einkauf/rechnung-eingang-erfassung'])
    expect(create.map((entry) => entry.module)).toEqual(['@/pages/einkauf/rechnung-eingang-erfassung-neu'])
    expect(INBOX_SUPPLIER_INVOICE_CREATE_ROUTE).toBe('/einkauf/rechnung-eingang-erfassung/neu')
  })
})
