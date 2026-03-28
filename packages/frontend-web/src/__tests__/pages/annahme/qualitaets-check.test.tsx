import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import QualitaetsCheckPage from '@/pages/annahme/qualitaets-check'

const navigateMock = vi.hoisted(() => vi.fn())
const toastMock = vi.hoisted(() => vi.fn())
const apiPostMock = vi.hoisted(() => vi.fn())
const patchStatusMutateMock = vi.hoisted(() => vi.fn())

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => navigateMock,
    useLocation: () => ({ state: { eintragId: 'queue-1' } }),
  }
})

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: toastMock }),
}))

vi.mock('@/components/navigation/ModuleToolbar', () => ({
  ModuleToolbar: ({ title }: { title: string }) => <div>{title}</div>,
}))

vi.mock('@/components/workflow/ProcessStatusPanel', () => ({
  ProcessStatusPanel: () => <div data-testid="process-status-panel" />,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: apiPostMock,
  },
}))

vi.mock('@/lib/api/inventory', () => ({
  useWarteschlangeEintrag: () => ({
    data: {
      id: 'queue-1',
      kennzeichen: 'AB-CD 1234',
      lieferant: 'Hof Meyer',
      article_id: 'art-weizen',
      artikel: 'Weizen',
      lieferschein_nr: 'LS-42',
      status: 'wartend',
    },
  }),
  usePatchWarteschlangeStatus: () => ({
    mutate: patchStatusMutateMock,
  }),
}))

describe('QualitaetsCheckPage', () => {
  beforeEach(() => {
    navigateMock.mockReset()
    toastMock.mockReset()
    apiPostMock.mockReset()
    patchStatusMutateMock.mockReset()
    apiPostMock.mockResolvedValue({
      data: {
        id: 'qp-1',
        reference_context: null,
      },
    })
  })

  function renderPage() {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    })

    return render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <QualitaetsCheckPage />
        </MemoryRouter>
      </QueryClientProvider>,
    )
  }

  it('navigiert nach erfolgreicher Qualitaetspruefung mit restart-sicherem Handover in die Ernte-Annahme', async () => {
    renderPage()

    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await screen.findByRole('heading', { name: 'Messungen' })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await screen.findByRole('heading', { name: 'Ergebnis' })
    fireEvent.click(screen.getByRole('button', { name: 'Abschliessen' }))

    await waitFor(() => {
      expect(apiPostMock).toHaveBeenCalled()
    })
    await waitFor(() => {
      expect(navigateMock).toHaveBeenCalledWith({
        pathname: '/agrar/ernte-annahme-erfassung',
        search:
          '?workflowProcess=harvest-to-settlement&workflowLabel=quality-protocol%3Aqp-1&entryMode=Qualitaetspruefung&partnerName=Hof+Meyer&subject=Weizen+%2F+freigegeben&lieferscheinNr=LS-42&vehiclePlate=AB-CD+1234&articleId=art-weizen&articleName=Weizen&qpResult=freigegeben&qualityProtocolId=qp-1',
      })
    })
  })
})
