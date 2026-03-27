import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import ErntefensterKonfigPage from '@/pages/agrar/erntefenster-konfig'

const navigateMock = vi.hoisted(() => vi.fn())
const apiGetMock = vi.hoisted(() => vi.fn())
const apiPostMock = vi.hoisted(() => vi.fn())
const toastMock = vi.hoisted(() => vi.fn())

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => navigateMock,
  }
})

vi.mock('@/hooks/use-toast', () => ({
  toast: toastMock,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: apiGetMock,
    post: apiPostMock,
  },
}))

describe('ErntefensterKonfigPage', () => {
  beforeEach(() => {
    navigateMock.mockReset()
    apiGetMock.mockReset()
    apiPostMock.mockReset()
    toastMock.mockReset()

    apiGetMock.mockImplementation(async (url: string) => {
      if (url.includes('/erntefenster-templates')) {
        return {
          data: [{ id: 'tpl-1', name: 'Getreide', description: 'Vorlage', process_key: 'harvest-to-settlement', default_start_mmdd: '07-01', default_end_mmdd: '07-31', product_groups: ['Getreide'] }],
        }
      }
      if (url.includes('/erntefenster-campaigns')) {
        return {
          data: [{ id: 'camp-1', template_id: 'tpl-1', name: 'Ernte 2026', start_date: '2026-07-01', end_date: '2026-07-31', process_key: 'harvest-to-settlement', product_groups: ['Getreide'], created_at: '2026-06-01T08:00:00Z' }],
        }
      }
      if (url.includes('/api/v1/agrar/settlements')) {
        return {
          data: [
            { id: 'set-1', settlement_number: 'SET-1', campaign_id: 'camp-1', net_amount_eur: 1000, total_deductions_eur: 50, approval_status: 'VERBUCHT', status: 'posted', created_at: '2026-07-10T10:00:00Z' },
            { id: 'set-2', settlement_number: 'SET-2', campaign_id: 'camp-1', net_amount_eur: 500, total_deductions_eur: 20, approval_status: 'ENTWURF', status: 'draft', created_at: '2026-07-20T10:00:00Z' },
            { id: 'set-legacy', settlement_number: 'SET-LEG', net_amount_eur: 250, total_deductions_eur: 15, approval_status: 'VERBUCHT', status: 'posted', created_at: '2026-07-15T10:00:00Z' },
            { id: 'set-wrong-campaign', settlement_number: 'SET-WRONG', campaign_id: 'camp-2', net_amount_eur: 777, total_deductions_eur: 12, approval_status: 'VERBUCHT', status: 'posted', created_at: '2026-07-12T10:00:00Z' },
            { id: 'set-3', settlement_number: 'SET-3', net_amount_eur: 999, total_deductions_eur: 10, approval_status: 'VERBUCHT', status: 'posted', created_at: '2026-08-05T10:00:00Z' },
          ],
        }
      }
      return { data: [] }
    })

    apiPostMock.mockImplementation(async (url: string) => {
      if (url.includes('/campaign-reference/backfill')) {
        return {
          data: {
            campaign_id: 'camp-1',
            matched_count: 1,
            updated_count: 1,
            ambiguous_count: 0,
            skipped_count: 0,
          },
        }
      }
      return { data: {} }
    })
  })

  function renderPage() {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    })

    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <ErntefensterKonfigPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )
  }

  it('zeigt Abschlussreife und navigiert in die gefilterte Settlement-Pruefung', async () => {
    renderPage()

    expect(await screen.findByText('Ernte 2026')).toBeInTheDocument()
    expect(screen.getByText('Abschluss offen')).toBeInTheDocument()
    expect(screen.getByText((content) => content.includes('1.750,00'))).toBeInTheDocument()
    expect(screen.getByText((content) => content.includes('85,00'))).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Settlement-Abschluss pruefen' }))

    await waitFor(() => {
      expect(navigateMock).toHaveBeenCalledWith(
        '/annahme/abrechnung?campaignId=camp-1&campaignName=Ernte+2026&campaignStart=2026-07-01&campaignEnd=2026-07-31',
      )
    })
  })

  it('stoesst den Backfill fuer Legacy-Settlements aus der Kampagnenkarte an', async () => {
    renderPage()

    expect(await screen.findByText('Ernte 2026')).toBeInTheDocument()
    expect(screen.getByText('1 Alt-Settlement(s) nutzen noch den Datumsfenster-Fallback.')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Alt-Daten zuordnen' }))

    await waitFor(() => {
      expect(apiPostMock).toHaveBeenCalledWith('/api/v1/agrar/settlements/campaign-reference/backfill', {
        campaign_id: 'camp-1',
      })
    })

    expect(toastMock).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Alt-Daten geprueft',
        description: '1 Alt-Settlements wurden der Kampagne zugeordnet.',
      }),
    )
  })
})
