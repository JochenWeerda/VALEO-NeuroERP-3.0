import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import AnnahmeAbrechnungPage from '@/pages/annahme/abrechnung'

const apiGetMock = vi.hoisted(() => vi.fn())
const apiPostMock = vi.hoisted(() => vi.fn())
const toastMock = vi.hoisted(() => vi.fn())

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: toastMock }),
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: apiGetMock,
    post: apiPostMock,
  },
}))

vi.mock('@/components/workflow/ProcessStatusPanel', () => ({
  ProcessStatusPanel: () => <div data-testid="process-status-panel" />,
}))

vi.mock('@/components/workflow/CompactDecisionCard', () => ({
  CompactDecisionCard: () => <div data-testid="compact-decision-card" />,
}))

vi.mock('@/features/workflow/useApprovalDensityProfile', () => ({
  useApprovalDensityProfile: () => null,
}))

describe('AnnahmeAbrechnungPage', () => {
  beforeEach(() => {
    apiGetMock.mockReset()
    apiPostMock.mockReset()
    apiPostMock.mockResolvedValue({ data: {} })
    apiGetMock.mockImplementation(async (url: string) => {
      if (url.includes('/api/v1/agrar/settlements')) {
        return {
          data: [
            {
              id: 'set-1',
              settlement_number: 'SET-1',
              supplier_id: 'LW-1',
              gross_quantity_kg: 1000,
              billing_quantity_kg: 950,
              unit_price_eur_per_ton: 220,
              gross_amount_eur: 250,
              total_deductions_eur: 10,
              net_amount_eur: 240,
              status: 'posted',
              approval_status: 'VERBUCHT',
              approval_history: [],
              allowed_transitions: [],
              can_post_fibu: false,
              correction_options: [],
              deductions: [],
              created_at: '2026-07-10T10:00:00Z',
            },
            {
              id: 'set-2',
              settlement_number: 'SET-2',
              supplier_id: 'LW-2',
              gross_quantity_kg: 1000,
              billing_quantity_kg: 950,
              unit_price_eur_per_ton: 220,
              gross_amount_eur: 300,
              total_deductions_eur: 20,
              net_amount_eur: 280,
              status: 'draft',
              approval_status: 'ENTWURF',
              approval_history: [],
              allowed_transitions: [],
              can_post_fibu: false,
              correction_options: [],
              deductions: [],
              created_at: '2026-08-10T10:00:00Z',
            },
          ],
        }
      }
      return { data: [] }
    })
  })

  function renderPage() {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    })

    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/annahme/abrechnung?campaignId=camp-1&campaignName=Ernte+2026&campaignStart=2026-07-01&campaignEnd=2026-07-31']}>
          <AnnahmeAbrechnungPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )
  }

  it('filtert die Settlement-Liste fuer den Kampagnenabschluss ueber Query-Parameter', async () => {
    renderPage()

    expect(await screen.findByText('Kampagnenabschluss: Ernte 2026')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('SET-1')).toBeInTheDocument()
      expect(
        screen.getByText((content) => content.includes('Lieferant: LW-1') && content.includes('Netto: 240,00')),
      ).toBeInTheDocument()
    })
    expect(screen.queryByText('SET-2')).not.toBeInTheDocument()
    expect(screen.queryByText((content) => content.includes('Lieferant: LW-2'))).not.toBeInTheDocument()
  })
})
