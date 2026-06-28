import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UniversalSalesOrderPilotPage from '@/pages/sales/UniversalSalesOrderPilotPage'
import { useSalesOrder, useSalesOrderScreenSummary } from '@/lib/api/sales'
import { useSalesOrderTabData } from '@/features/sales-masks/use-sales-order-tab-data'
import { useScreenDefinition } from '@/lib/api/masks'

vi.mock('@/app/routing/typed-router', () => ({
  useParams: () => ({ id: 'order-1' }),
  useSearchParams: () => [new URLSearchParams()],
  useNavigate: () => vi.fn(),
}))

vi.mock('@/lib/api/sales', () => ({
  useSalesOrder: vi.fn(),
  useSalesOrderScreenSummary: vi.fn(),
}))

vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: vi.fn(),
}))

vi.mock('@/features/sales-masks/use-sales-order-tab-data', () => ({
  useSalesOrderTabData: vi.fn(),
  mapTabDataToTables: vi.fn((response) => (response ? { [response.table_key]: response.items } : {})),
}))

const mockedUseSalesOrder = vi.mocked(useSalesOrder)
const mockedUseSalesOrderScreenSummary = vi.mocked(useSalesOrderScreenSummary)
const mockedUseSalesOrderTabData = vi.mocked(useSalesOrderTabData)
const mockedUseScreenDefinition = vi.mocked(useScreenDefinition)

const summaryFixture = {
  schema_version: 1 as const,
  screen_id: 'sales/sales-order' as const,
  order_id: 'order-1',
  tenant_id: 'tenant-1',
  title: 'Weizen Lieferung',
  subtitle: 'SO-100',
  customer_name: 'Musterkunde AG',
  summary: {
    total_amount: 1500,
    item_count: 2,
    status: 'open',
    delivery_date: '2026-07-01',
  },
  available_tabs: ['kopf', 'positionen', 'lieferung', 'dokumente'],
  tab_endpoints: {
    positionen: '/api/v1/sales/orders/order-1/tabs/positionen',
    lieferung: '/api/v1/sales/orders/order-1/tabs/lieferung',
    dokumente: '/api/v1/sales/orders/order-1/tabs/dokumente',
  },
  actions: [{ key: 'edit', label: 'Bearbeiten', permission: 'sales.order.update' }],
  performance: {
    initial_payload_budget_kb: 56,
    tabs_lazy: true,
    lookup_min_chars: 2,
    default_table_limit: 25,
  },
}

describe('UniversalSalesOrderPilotPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockedUseScreenDefinition.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useScreenDefinition>)
    mockedUseSalesOrderTabData.mockReturnValue({
      data: undefined,
      isFetching: false,
      error: null,
    } as ReturnType<typeof useSalesOrderTabData>)
  })

  it('loads order details only after summary is available', () => {
    mockedUseSalesOrder.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useSalesOrder>)
    mockedUseSalesOrderScreenSummary.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as ReturnType<typeof useSalesOrderScreenSummary>)

    render(<UniversalSalesOrderPilotPage />)

    expect(screen.getByText('Summary wird geladen...')).toBeInTheDocument()
    expect(mockedUseSalesOrder).toHaveBeenCalledWith('order-1', { enabled: false })
  })

  it('renders generator shell with summary KPIs', () => {
    mockedUseSalesOrder.mockReturnValue({
      data: {
        id: 'order-1',
        tenant_id: 'tenant-1',
        order_number: 'SO-100',
        subject: 'Weizen Lieferung',
        total_amount: 1500,
        currency: 'EUR',
        status: 'open',
        items: [],
        version: 1,
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useSalesOrder>)
    mockedUseSalesOrderScreenSummary.mockReturnValue({
      data: summaryFixture,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useSalesOrderScreenSummary>)

    render(<UniversalSalesOrderPilotPage />)

    expect(screen.getByTestId('universal-sales-order-pilot')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Weizen Lieferung' })).toBeInTheDocument()
    expect(screen.getByText('Auftragssumme')).toBeInTheDocument()
    expect(mockedUseSalesOrder).toHaveBeenCalledWith('order-1', { enabled: true })
  })

  it('loads positions tab data on tab switch', async () => {
    const user = userEvent.setup()
    mockedUseSalesOrder.mockReturnValue({
      data: {
        id: 'order-1',
        tenant_id: 'tenant-1',
        order_number: 'SO-100',
        subject: 'Weizen Lieferung',
        total_amount: 1500,
        currency: 'EUR',
        status: 'open',
        items: [],
        version: 1,
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useSalesOrder>)
    mockedUseSalesOrderScreenSummary.mockReturnValue({
      data: summaryFixture,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useSalesOrderScreenSummary>)

    render(<UniversalSalesOrderPilotPage />)

    await user.click(screen.getByRole('tab', { name: /positionen/i }))

    await waitFor(() => {
      expect(mockedUseSalesOrderTabData).toHaveBeenLastCalledWith(
        'order-1',
        'positionen',
        summaryFixture.tab_endpoints,
        1,
      )
    })
  })

  it('loads delivery tab data on tab switch', async () => {
    const user = userEvent.setup()
    mockedUseSalesOrder.mockReturnValue({
      data: {
        id: 'order-1',
        tenant_id: 'tenant-1',
        order_number: 'SO-100',
        subject: 'Weizen Lieferung',
        total_amount: 1500,
        currency: 'EUR',
        status: 'open',
        items: [],
        version: 1,
      },
      isLoading: false,
      error: null,
    } as ReturnType<typeof useSalesOrder>)
    mockedUseSalesOrderScreenSummary.mockReturnValue({
      data: summaryFixture,
      isLoading: false,
      error: null,
    } as ReturnType<typeof useSalesOrderScreenSummary>)

    render(<UniversalSalesOrderPilotPage />)

    await user.click(screen.getByRole('tab', { name: /lieferung/i }))

    await waitFor(() => {
      expect(mockedUseSalesOrderTabData).toHaveBeenLastCalledWith(
        'order-1',
        'lieferung',
        summaryFixture.tab_endpoints,
        1,
      )
    })
  })
})
