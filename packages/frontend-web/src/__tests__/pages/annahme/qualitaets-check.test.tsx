import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import QualitaetsCheckPage from '@/pages/annahme/qualitaets-check'

const navigateMock = vi.hoisted(() => vi.fn())
const toastMock = vi.hoisted(() => vi.fn())
const apiPostMock = vi.hoisted(() => vi.fn())
const patchStatusMutateMock = vi.hoisted(() => vi.fn())

vi.mock('@/app/routing/typed-router', async () => {
  const actual = await vi.importActual('@/app/routing/typed-router')
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
    fireEvent.click(screen.getAllByRole('button', { name: 'Qualitätsprüfung speichern' }).at(-1)!)

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


// Test identities/read hooks remain explicit doubles; the real Studio compiler,
// runtime and renderer execute the native ScreenDefinition fixture.
vi.mock('@/lib/api/masks', async () => {
  const fixtures = (await import('@/__tests__/fixtures/intake-weighing-screens.json')).default
  return { useScreenDefinition: (id: string) => ({ data: (fixtures as Record<string, unknown>)[id], isLoading: false, error: null }) }
})
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({
  useScreenPermissions: (definition: { actions?: Array<{ permission?: string }> }) => definition?.actions?.flatMap(action => action.permission ? [action.permission] : []) ?? [],
}))
vi.mock('@/lib/api/ux-overlays', () => ({
  useUserScreenOverlay: () => ({ data: undefined }), overlayKeys: { screen: (id: string) => ['test-overlay', id] },
  saveUserOverlay: vi.fn(), deleteUserOverlay: vi.fn(),
}))
vi.mock('@/components/mask-builder/specialized/intake/domain-data', async () => {
  const inventory = await import('@/lib/api/inventory')
  const tickets = await import('@/lib/api/weighing-tickets')
  const supply = await import('@/lib/api/supply-chain')
  return {
    useDomainIdentity: () => ({ tenantId: 'test-tenant', actor: 'test-operator' }),
    useDomainQueue: () => inventory.useWarteschlange(),
    useDomainQueueEntry: (id: string) => inventory.useWarteschlangeEintrag(id),
    useDomainTickets: () => tickets.useWeighingTickets({ limit: 100 }),
    useDomainContracts: () => tickets.useOpenContracts(),
    useDomainSupplyChain: () => supply.useSupplyChainOverview(),
  }
})
