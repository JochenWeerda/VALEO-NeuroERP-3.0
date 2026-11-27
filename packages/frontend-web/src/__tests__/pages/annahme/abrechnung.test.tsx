import { AxiosError } from 'axios'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import AnnahmeAbrechnungPage from '@/pages/annahme/abrechnung-legacy'

function axiosConflict(): AxiosError {
  const err = new AxiosError('conflict')
  err.response = {
    data: { detail: { code: 'row_version_conflict', message: 'stale' } },
    status: 409,
    statusText: 'Conflict',
    headers: {},
    config: {} as never,
  }
  return err
}

function axiosBoom(message = 'boom'): AxiosError {
  const err = new AxiosError(message)
  err.response = {
    data: { detail: message },
    status: 500,
    statusText: 'Err',
    headers: {},
    config: {} as never,
  }
  return err
}

const apiGetMock = vi.hoisted(() => vi.fn())
const apiPostMock = vi.hoisted(() => vi.fn())
const toastMock = vi.hoisted(() => vi.fn())
const navigateMock = vi.hoisted(() => vi.fn())
const locationStateMock = vi.hoisted(() => ({ current: null as Record<string, unknown> | null }))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: toastMock }),
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: apiGetMock,
    post: apiPostMock,
  },
}))

vi.mock('@/app/routing/typed-router', async () => {
  const actual = await vi.importActual<typeof import('@/app/routing/typed-router')>('@/app/routing/typed-router')
  return {
    ...actual,
    useNavigate: () => navigateMock,
    useLocation: () => ({
      ...actual.useLocation(),
      state: locationStateMock.current,
    }),
  }
})

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
    navigateMock.mockReset()
    toastMock.mockReset()
    locationStateMock.current = null
    apiPostMock.mockResolvedValue({ data: {} })
    apiGetMock.mockImplementation(async (url: string) => {
      if (url.includes('/api/v1/agrar/settlements')) {
        return {
          data: [
            {
              id: 'set-1',
              settlement_number: 'SET-1',
              campaign_id: 'camp-1',
              supplier_id: 'LW-1',
              gross_quantity_kg: 1000,
              billing_quantity_kg: 950,
              unit_price_eur_per_ton: 220,
              gross_amount_eur: 250,
              total_deductions_eur: 10,
              net_amount_eur: 240,
              status: 'posted',
              approval_status: 'VERBUCHT',
              posted_journal_ref: 'JNL-1',
              approval_history: [
                {
                  previous_status: 'ENTWURF',
                  new_status: 'FREIGEGEBEN',
                  decided_at: '2026-07-10T09:00:00Z',
                  actor_id: 'u1',
                  reason: 'ok',
                },
              ],
              allowed_transitions: [],
              can_post_fibu: false,
              correction_options: [{ memo_type: 'credit' }, { memo_type: 'debit' }],
              deductions: [
                { id: 'd1', deduction_type: 'drying', mode: 'per_ton', amount_eur: 10 },
                { id: 'd3', deduction_type: 'freight', mode: 'fixed', amount_eur: 4 },
                { id: 'd4', deduction_type: 'other', mode: 'per_ton', amount_eur: 1 },
              ],
              created_at: '2026-07-10T10:00:00Z',
              row_version: 2,
            },
            {
              id: 'set-2',
              settlement_number: 'SET-2',
              campaign_id: 'camp-2',
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
            {
              id: 'set-draft',
              settlement_number: 'SET-DRAFT',
              campaign_id: 'camp-1',
              supplier_id: 'LW-3',
              gross_quantity_kg: 800,
              billing_quantity_kg: 780,
              unit_price_eur_per_ton: 200,
              gross_amount_eur: 160,
              total_deductions_eur: 5,
              net_amount_eur: 155,
              status: 'draft',
              approval_status: 'ENTWURF',
              approval_history: [],
              allowed_transitions: ['ZUR_FREIGABE', 'FREIGEGEBEN', 'ABGELEHNT', 'ENTWURF'],
              can_post_fibu: true,
              correction_options: [],
              deductions: [
                { id: 'd2', deduction_type: 'cleaning', mode: 'fixed', amount_eur: 5 },
              ],
              created_at: '2026-07-11T10:00:00Z',
              row_version: 1,
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

  it('uebergibt campaign_id beim Speichern eines Settlements aus dem Kampagnenkontext', async () => {
    renderPage()

    expect(await screen.findByText('Kampagnenabschluss: Ernte 2026')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByLabelText('Lieferant')).toBeInTheDocument()
    })

    apiPostMock.mockImplementation(async (url: string, payload?: Record<string, unknown>) => {
      if (url.includes('/api/v1/agrar/settlements/drying/compute')) {
        throw new Error('no drying rule')
      }
      if (url.includes('/api/v1/agrar/settlements/billing-weight/preview')) {
        return { data: { billing_weight_kg: 950, deduction_kg: 0 } }
      }
      if (url === '/api/v1/agrar/settlements') {
        return { data: { id: 'set-new', ...payload } }
      }
      return { data: {} }
    })

    const supplierInput = screen.getByLabelText('Lieferant')
    fireEvent.change(supplierInput, { target: { value: 'LW-NEW' } })

    fireEvent.click(screen.getByRole('button', { name: 'Speichern' }))

    await waitFor(() => {
      expect(apiPostMock).toHaveBeenCalledWith(
        '/api/v1/agrar/settlements',
        expect.objectContaining({
          campaign_id: 'camp-1',
          supplier_id: 'LW-NEW',
        }),
      )
    })
  })

  it('zeigt Freigabe/Storno-Aktionen fuer vorhandene Settlements', async () => {
    renderPage()
    expect(await screen.findByText('SET-1')).toBeInTheDocument()
    expect(screen.getByText(/Bestehende Abrechnungen/i)).toBeInTheDocument()
    expect(screen.getByText(/Netto: 240,00/)).toBeInTheDocument()
    expect(screen.getByText(/Lieferant: LW-1/)).toBeInTheDocument()
    expect(screen.getByText(/Trocknung \(je t\)/)).toBeInTheDocument()
    expect(screen.getByText(/Reinigung \(fix\)/)).toBeInTheDocument()
  })

  it('reicht Entwurf zur Freigabe ein und storniert mit Bestaetigung', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    apiPostMock.mockImplementation(async (url: string) => {
      if (url.includes('/freigabe')) {
        return { data: { allowed: true, reason: 'ok', new_status: 'ZUR_FREIGABE', previous_status: 'ENTWURF' } }
      }
      if (url.includes('/cancel')) {
        return { data: { id: 'set-draft', status: 'cancelled' } }
      }
      if (url.includes('/post-fibu')) {
        return { data: { id: 'set-draft' } }
      }
      return { data: {} }
    })
    renderPage()
    expect(await screen.findByText('SET-DRAFT')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Zur Freigabe' }))
    await waitFor(() => {
      expect(apiPostMock).toHaveBeenCalledWith(
        '/api/v1/agrar/settlements/set-draft/freigabe',
        expect.objectContaining({ target_status: 'ZUR_FREIGABE', expected_row_version: 1 }),
      )
    })
    expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Freigabeschritt gespeichert' }))

    fireEvent.click(screen.getByRole('button', { name: 'In Fibu buchen' }))
    await waitFor(() => {
      expect(apiPostMock).toHaveBeenCalledWith(
        '/api/v1/agrar/settlements/set-draft/post-fibu',
        expect.objectContaining({ expected_row_version: 1 }),
      )
    })
    expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Fibu-Buchung erstellt' }))

    fireEvent.click(screen.getByRole('button', { name: 'Stornieren' }))
    await waitFor(() => {
      expect(confirmSpy).toHaveBeenCalled()
      expect(apiPostMock).toHaveBeenCalledWith(
        '/api/v1/agrar/settlements/set-draft/cancel',
        {},
        expect.objectContaining({ params: { expected_row_version: 1 } }),
      )
    })
    confirmSpy.mockRestore()
  })

  it('blockiert Speichern ohne Lieferant', async () => {
    renderPage()
    expect(await screen.findByText('SET-DRAFT')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Speichern' }))
    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Lieferant fehlt' }))
    })
  })

  it('fuehrt Freigeben/Ablehnen/Zuruecksetzen und Korrekturen aus', async () => {
    apiPostMock.mockImplementation(async (url: string, payload?: Record<string, unknown>) => {
      if (url.includes('/freigabe')) {
        return {
          data: {
            allowed: payload?.target_status !== 'ABGELEHNT',
            reason: 'ok',
            new_status: payload?.target_status,
            previous_status: 'ENTWURF',
          },
        }
      }
      return { data: {} }
    })
    renderPage()
    expect(await screen.findByText('SET-DRAFT')).toBeInTheDocument()
    expect(screen.getByText(/Journal: JNL-1/)).toBeInTheDocument()
    expect(screen.getAllByText(/Fracht/).length).toBeGreaterThan(0)
    expect(screen.getAllByText(/Sonstiges/).length).toBeGreaterThan(0)
    expect(screen.getByText(/Freigabehistorie/i)).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Freigeben' }))
    await waitFor(() => {
      expect(apiPostMock).toHaveBeenCalledWith(
        '/api/v1/agrar/settlements/set-draft/freigabe',
        expect.objectContaining({ target_status: 'FREIGEGEBEN' }),
      )
    })

    fireEvent.click(screen.getByRole('button', { name: 'Ablehnen' }))
    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Freigabeschritt abgelehnt' }))
    })

    fireEvent.click(screen.getByRole('button', { name: 'Zurück in Entwurf' }))
    await waitFor(() => {
      expect(apiPostMock).toHaveBeenCalledWith(
        '/api/v1/agrar/settlements/set-draft/freigabe',
        expect.objectContaining({ target_status: 'ENTWURF' }),
      )
    })

    fireEvent.click(screen.getByRole('button', { name: 'Gutschrift' }))
    expect(navigateMock).toHaveBeenCalledWith('/einkauf/gutschriften-belastungen/credit?settlementId=set-1')
    fireEvent.click(screen.getByRole('button', { name: 'Belastung' }))
    expect(navigateMock).toHaveBeenCalledWith('/einkauf/gutschriften-belastungen/debit?settlementId=set-1')
  })

  it('erzeugt Vorschau und zeigt Exception-Hinweise', async () => {
    apiPostMock.mockImplementation(async (url: string) => {
      if (url.includes('/billing-weight/preview')) {
        return { data: { billing_weight_kg: 940, deduction_kg: 10 } }
      }
      if (url.includes('/settlements/preview')) {
        return {
          data: {
            billing_quantity_kg: 940,
            gross_amount_eur: 200,
            total_deductions_eur: 15,
            net_amount_eur: 185,
            exception_hints: [
              {
                rule_id: 'R1',
                category: 'qualitaet',
                decision_mode: 'manual',
                description: 'Hinweis A',
                requires_approval: true,
                approver_roles: ['AGRONOM'],
              },
            ],
            reference_context: {
              process_key: 'settlement',
              anchor_entity: 'settlement',
              anchor_id: 'tmp',
              chain: { step: '1' },
            },
            explainability: null,
          },
        }
      }
      if (url.includes('/drying/compute')) {
        throw new Error('no drying')
      }
      return { data: {} }
    })
    renderPage()
    expect(await screen.findByLabelText('Lieferant')).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Lieferant'), { target: { value: 'LW-P' } })
    const freightFixed = document.getElementById('freightFixed')
    if (freightFixed) {
      fireEvent.change(freightFixed, { target: { value: '12.5' } })
    }
    fireEvent.click(screen.getByRole('button', { name: 'Vorschau' }))
    await waitFor(() => {
      expect(apiPostMock).toHaveBeenCalledWith(
        '/api/v1/agrar/settlements/preview',
        expect.objectContaining({ supplier_id: 'LW-P' }),
      )
    })
    expect(await screen.findByText('Hinweis A')).toBeInTheDocument()
    expect(screen.getByText(/Nettobetrag/)).toBeInTheDocument()
    expect(screen.getAllByText(/Ausnahmehinweise/).length).toBeGreaterThan(0)
  })

  it('bricht Storno ab wenn Confirm verweigert wird', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)
    renderPage()
    expect(await screen.findByText('SET-DRAFT')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Stornieren' }))
    expect(confirmSpy).toHaveBeenCalled()
    expect(apiPostMock).not.toHaveBeenCalledWith(
      expect.stringContaining('/cancel'),
      expect.anything(),
      expect.anything(),
    )
    confirmSpy.mockRestore()
  })

  it('setzt Freigabe-Akteur und uebernimmt QualitaetsCheck-State', async () => {
    locationStateMock.current = {
      fromQualitaetsCheck: true,
      artikel: 'WHEAT',
      feuchtigkeit: 16.5,
      verunreinigung: 3.2,
    }
    apiPostMock.mockImplementation(async (url: string, payload?: Record<string, unknown>) => {
      if (url.includes('/drying/compute')) {
        return {
          data: {
            invoice_weight_kg: 900,
            loss_kg: 50,
            crop_code: 'WHEAT',
            moisture_pct: 16.5,
          },
        }
      }
      if (url.includes('/billing-weight/preview')) {
        return { data: { billing_weight_kg: 900, deduction_kg: 50 } }
      }
      if (url === '/api/v1/agrar/settlements') {
        return { data: { id: 'set-q', ...payload } }
      }
      return { data: {} }
    })
    renderPage()
    expect(await screen.findByLabelText('Freigabe durch (ID)')).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Freigabe durch (ID)'), { target: { value: 'approver-9' } })
    expect(screen.getByLabelText('Freigabe durch (ID)')).toHaveValue('approver-9')
    // NativeSelect ohne htmlFor — Rolle über Combobox
    const roleSelects = screen.getAllByRole('combobox')
    if (roleSelects.length > 0) {
      fireEvent.change(roleSelects[0], { target: { value: 'PROKURIST' } })
    }

    fireEvent.change(screen.getByLabelText('Lieferant'), { target: { value: 'LW-Q' } })
    fireEvent.click(screen.getByRole('button', { name: 'Speichern' }))
    await waitFor(() => {
      expect(apiPostMock).toHaveBeenCalledWith(
        '/api/v1/agrar/settlements',
        expect.objectContaining({
          supplier_id: 'LW-Q',
          article_id: 'WHEAT',
        }),
      )
    })
  })

  it('zeigt Fehlerzustand der Settlement-Liste', async () => {
    apiGetMock.mockImplementation(async () => {
      throw new Error('Liste down')
    })
    renderPage()
    expect(await screen.findByText(/Liste down|fehlgeschlagen|konnten nicht/i)).toBeInTheDocument()
  })

  it('zeigt ungefilterte Settlement-Liste ohne Kampagnenkontext', async () => {
    const { renderPage: renderBare } = (() => {
      function renderBarePage() {
        const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
        return render(
          <QueryClientProvider client={client}>
            <MemoryRouter initialEntries={['/annahme/abrechnung']}>
              <AnnahmeAbrechnungPage />
            </MemoryRouter>
          </QueryClientProvider>,
        )
      }
      return { renderPage: renderBarePage }
    })()
    renderBare()
    expect(await screen.findByText('SET-1')).toBeInTheDocument()
    expect(screen.getByText('SET-2')).toBeInTheDocument()
  })

  it('blockiert Vorschau ohne Lieferant', async () => {
    renderPage()
    expect(await screen.findByText('SET-1')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Vorschau' }))
    await waitFor(() =>
      expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Lieferant fehlt' })),
    )
  })

  it('meldet Daten veraltet bei 409 auf Freigabe/Fibu und generischen Storno-Fehler', async () => {
    apiPostMock.mockImplementation(async (url: string) => {
      if (url.includes('/freigabe')) throw axiosConflict()
      if (url.includes('/post-fibu')) throw axiosConflict()
      if (url.includes('/cancel')) throw axiosBoom('storno failed')
      return { data: {} }
    })
    renderPage()
    expect(await screen.findByText('SET-DRAFT')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Zur Freigabe' }))
    await waitFor(() =>
      expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Daten veraltet' })),
    )

    fireEvent.click(screen.getByRole('button', { name: 'In Fibu buchen' }))
    await waitFor(() =>
      expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Daten veraltet' })),
    )

    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    fireEvent.click(screen.getByRole('button', { name: 'Stornieren' }))
    await waitFor(() =>
      expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Fehler' })),
    )
    confirmSpy.mockRestore()
  })

  it('meldet Daten veraltet bei 409 auf Storno und generischen Freigabe/Fibu-Fehler', async () => {
    apiPostMock.mockImplementation(async (url: string) => {
      if (url.includes('/cancel')) throw axiosConflict()
      if (url.includes('/freigabe')) throw axiosBoom('freigabe down')
      if (url.includes('/post-fibu')) throw axiosBoom('fibu down')
      return { data: {} }
    })
    renderPage()
    expect(await screen.findByText('SET-DRAFT')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'Zur Freigabe' }))
    await waitFor(() =>
      expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Fehler' })),
    )

    fireEvent.click(screen.getByRole('button', { name: 'In Fibu buchen' }))
    await waitFor(() =>
      expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Fehler' })),
    )

    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    fireEvent.click(screen.getByRole('button', { name: 'Stornieren' }))
    await waitFor(() =>
      expect(toastMock).toHaveBeenCalledWith(expect.objectContaining({ title: 'Daten veraltet' })),
    )
    confirmSpy.mockRestore()
  })
})
