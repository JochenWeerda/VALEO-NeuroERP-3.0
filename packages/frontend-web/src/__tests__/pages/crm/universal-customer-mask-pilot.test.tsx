import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import UniversalCustomerMaskPilotPage from '@/pages/crm/kunden-stamm-modern/UniversalCustomerMaskPilotPage'
import { useCustomer, useCustomerScreenSummary } from '@/lib/api/crm'
import { useCustomerTabData } from '@/features/crm-masks/use-customer-tab-data'

vi.mock('@/app/routing/typed-router', () => ({
  useParams: () => ({ id: 'customer-1' }),
  useNavigate: () => vi.fn(),
}))

vi.mock('@/lib/api/crm', () => ({
  useCustomer: vi.fn(),
  useCustomerScreenSummary: vi.fn(),
}))

import { useScreenDefinition } from '@/lib/api/masks'

vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: vi.fn(),
}))

vi.mock('@/features/crm-masks/use-customer-tab-data', () => ({
  useCustomerTabData: vi.fn(),
  mapTabDataToTables: vi.fn((response) => (response ? { [response.table_key]: response.items } : {})),
}))

// Mock the runtime hook to avoid QueryClientProvider requirement in unit tests
vi.mock('@/components/mask-builder', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/components/mask-builder')>()
  return {
    ...actual,
    useUniversalMaskRuntime: vi.fn(() => ({
      plan: undefined,
      binding: undefined,
      entityData: {},
      tableRows: {},
      tableTotals: {},
      tableQueryStates: {},
      setTableQuery: vi.fn(),
      userOverlay: {},
      overlayInvalidPaths: [],
      updateUserOverlay: vi.fn(),
      resetUserOverlay: vi.fn(),
      lookupBindings: {},
      isEntityLoading: false,
      isOverlayLoading: false,
      entityError: null,
      refetch: vi.fn(),
    })),
  }
})

const mockedUseCustomer = vi.mocked(useCustomer)
const mockedUseCustomerScreenSummary = vi.mocked(useCustomerScreenSummary)
const mockedUseCustomerTabData = vi.mocked(useCustomerTabData)
const mockedUseScreenDefinition = vi.mocked(useScreenDefinition)

const summaryFixture = {
  schema_version: 1 as const,
  screen_id: 'crm/customer-360' as const,
  customer_id: 'customer-1',
  tenant_id: 'tenant-1',
  title: 'Musterkunde AG',
  subtitle: 'K-100',
  summary: {
    sales_ytd: 12000,
    open_items_total: 0,
    recent_activity_count: 3,
    credit_status: 'ok' as const,
  },
  badges: [],
  available_tabs: ['stammdaten', 'contacts', 'auftraege', 'aktivitaeten'],
  tab_endpoints: {
    contacts: '/api/v1/crm/customers/customer-1/tabs/contacts',
    kontakte: '/api/v1/crm/customers/customer-1/tabs/kontakte',
    auftraege: '/api/v1/crm/customers/customer-1/tabs/auftraege',
  },
  actions: [{ key: 'edit', label: 'Bearbeiten', permission: 'crm.customer.update' }],
  performance: {
    initial_payload_budget_kb: 48,
    tabs_lazy: true,
    lookup_min_chars: 2,
    default_table_limit: 25,
  },
}

describe('UniversalCustomerMaskPilotPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedUseScreenDefinition.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useScreenDefinition>)
    mockedUseCustomerTabData.mockReturnValue({
      data: undefined,
      isFetching: false,
      error: null,
    } as ReturnType<typeof useCustomerTabData>)
  })

  it('keeps customer detail loading disabled until the summary exists', () => {
    mockedUseCustomer.mockReturnValue({
      data: null,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useCustomer>)
    mockedUseCustomerScreenSummary.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as ReturnType<typeof useCustomerScreenSummary>)

    render(<UniversalCustomerMaskPilotPage />)

    expect(screen.getByText('Summary wird geladen...')).toBeInTheDocument()
    expect(mockedUseCustomer).toHaveBeenCalledWith('customer-1', { enabled: false })
  })

  it('renders the generator shell with summary before customer details are loaded', () => {
    mockedUseCustomer.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    } as ReturnType<typeof useCustomer>)
    mockedUseCustomerScreenSummary.mockReturnValue({
      data: summaryFixture,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useCustomerScreenSummary>)

    render(<UniversalCustomerMaskPilotPage />)

    expect(screen.getByTestId('universal-customer-mask-pilot')).toBeInTheDocument()
    expect(screen.getByTestId('screen-crm/customer-360')).toHaveAttribute('data-mobile-layout', 'mobileStack')
    expect(screen.getByRole('heading', { name: 'Musterkunde AG' })).toBeInTheDocument()
    expect(screen.getByText('Umsatz 12M')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Bearbeiten' })).toBeInTheDocument()
    expect(screen.getByText('Stammdaten werden nachgeladen...')).toBeInTheDocument()
    expect(mockedUseCustomer).toHaveBeenCalledWith('customer-1', { enabled: true })
  })

  // Radix Tabs onValueChange does not propagate through jsdom fireEvent/userEvent;
  // tab-click → activeTabKey behaviour is covered by useMaskPilotState unit tests.
  it.skip('loads tab data when switching to a lazy data tab', async () => {
    mockedUseCustomer.mockReturnValue({
      data: {
        id: 'customer-1',
        customer_number: 'K-100',
        name: 'Musterkunde AG',
        payment_terms: 14,
        is_active: true,
        tenant_id: 'tenant-1',
        created_at: '2026-06-28T00:00:00Z',
        updated_at: '2026-06-28T00:00:00Z',
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useCustomer>)
    mockedUseCustomerScreenSummary.mockReturnValue({
      data: summaryFixture,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useCustomerScreenSummary>)

    render(<UniversalCustomerMaskPilotPage />)

    fireEvent.click(screen.getByRole('tab', { name: /ansprechpartner/i }))

    await waitFor(
      () => {
        const calls = mockedUseCustomerTabData.mock.calls
        const calledWithContacts = calls.some(
          (call) => call[0] === 'customer-1' && call[1] === 'contacts',
        )
        expect(calledWithContacts).toBe(true)
      },
      { timeout: 3000 },
    )
  })
})
