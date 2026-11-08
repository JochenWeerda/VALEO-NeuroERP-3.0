import { renderStudio as render } from '@/__tests__/helpers/studio-intake-render'
import { fireEvent, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import WarteschlangePage from '@/pages/annahme/warteschlange'

const navigateMock = vi.fn()
const refetchMock = vi.fn()

vi.mock('@/app/routing/typed-router', async () => {
  const actual = await vi.importActual('@/app/routing/typed-router')
  return {
    ...actual,
    useNavigate: () => navigateMock,
  }
})

vi.mock('@/lib/api/supply-chain', () => ({
  useSupplyChainOverview: () => ({ data: null, isLoading: false }),
}))

vi.mock('@/lib/professional-control-centers', () => ({
  summarizeSupplyOps: () => ({ totalOpen: 0, totalInTransit: 0, totalDelivered: 0, kpis: [] }),
}))

vi.mock('@/lib/api/inventory', () => ({
  useWarteschlange: () => ({
    data: {
      items: [
        {
          id: 'queue-1',
          position: 1,
          kennzeichen: 'AB-CD 1234',
          lieferant: 'Mueller Agrar',
          article_id: null,
          artikel: 'Weizen',
          ankunft: '08:15',
          wartezeit: 12,
          status: 'wartend',
          lieferschein_nr: 'LS-42',
        },
        {
          id: 'queue-2',
          position: 2,
          kennzeichen: 'EF-GH 5678',
          lieferant: 'Hof Meyer',
          article_id: 'art-raps',
          artikel: 'Raps',
          ankunft: '08:45',
          wartezeit: 4,
          status: 'abgeschlossen',
          lieferschein_nr: 'LS-99',
        },
        {
          id: 'queue-3',
          position: 3,
          kennzeichen: 'IJ-KL 9012',
          lieferant: 'Agrar Schmidt',
          article_id: 'art-gerste',
          artikel: 'Gerste',
          ankunft: '09:10',
          wartezeit: 2,
          status: 'gesperrt',
          lieferschein_nr: 'LS-77',
        },
      ],
      total: 3,
    },
    isLoading: false,
    refetch: refetchMock,
  }),
  useRepairWarteschlangeArticle: () => ({
    mutate: vi.fn(),
  }),
}))

describe('WarteschlangePage', () => {
  it('rendert Queue-Sicht im DS-Rahmen', () => {
    render(
      <MemoryRouter>
        <WarteschlangePage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Annahme-Warteschlange', level: 1 })).toBeInTheDocument()
    expect(screen.getByLabelText('Suche Warteschlange')).toBeInTheDocument()
    expect(screen.getByText('AB-CD 1234')).toBeInTheDocument()
  })

  it('filtert die Queue ueber die Suche', () => {
    render(
      <MemoryRouter>
        <WarteschlangePage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Suche Warteschlange'), { target: { value: 'Mais' } })
    expect(screen.queryByText('AB-CD 1234')).not.toBeInTheDocument()
  })

  it('bietet fuer abgeschlossene Queue-Eintraege den CTA zur Ernte-Annahme', () => {
    render(
      <MemoryRouter>
        <WarteschlangePage />
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Ernte-Annahme anlegen' }))

    expect(navigateMock).toHaveBeenCalledWith(
      '/agrar/ernte-annahme-erfassung?workflowProcess=harvest-to-settlement&workflowLabel=queue-entry%3Aqueue-2&entryMode=Warteschlange&partnerName=Hof+Meyer&lieferscheinNr=LS-99&vehiclePlate=EF-GH+5678&articleId=art-raps&articleName=Raps&subject=Raps+%2F+Queue&queueEntryId=queue-2',
    )
  })

  it('bietet fuer gesperrte Queue-Eintraege den CTA zur Klaerung', () => {
    render(
      <MemoryRouter>
        <WarteschlangePage />
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Klaerung starten' }))

    expect(navigateMock).toHaveBeenCalledWith('/annahme/klaerung-gesperrt?queueEntryId=queue-3')
  })

  it('bietet fuer Eintraege ohne article_id den Repair-CTA', () => {
    render(
      <MemoryRouter>
        <WarteschlangePage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('button', { name: 'Artikel reparieren' })).toBeInTheDocument()
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
