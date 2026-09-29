import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { act, fireEvent, render, screen, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { UniversalMaskRenderer, validateScreenDefinition } from '@/components/mask-builder'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import {
  HEADER_COLLAPSE_AT_PX,
  HEADER_EXPAND_BELOW_PX,
  nextCondensedState,
} from '@/components/mask-builder/renderers/SectionPageRenderer'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { UniversalFormState } from '@/components/mask-builder/runtime/FormState'
import { MemoryRouter, useLocation, useNavigate } from '@/app/routing/test-router'

function deliveryNote(overrides: Partial<ScreenDefinition['layout']> = {}): ScreenDefinition {
  return {
    schemaVersion: 1,
    id: 'sales/delivery-note',
    domain: 'sales',
    mode: 'detail',
    title: 'Lieferschein',
    subtitle: 'Verkauf / Warenausgang',
    layout: {
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      floorplan: 'transaction',
      sectionNavigation: 'anchors',
      contextRail: 'none',
      tableProfile: 'standard',
      ...overrides,
    },
    tabs: [
      {
        key: 'kopf',
        label: 'Lieferschein-Kopf',
        lazy: false,
        fields: [
          { key: 'delivery_note_number', label: 'LS-Nr.', type: 'text', readOnly: true },
          { key: 'delivery_date', label: 'Lieferdatum', type: 'date', readOnly: true },
        ],
      },
      { key: 'positionen', label: 'Positionen', lazy: true, fields: [{ key: 'charge', label: 'Charge', type: 'text' }] },
      { key: 'dokumente', label: 'Dokumente', lazy: true, fields: [{ key: 'bemerkung', label: 'Bemerkung', type: 'text' }] },
    ],
    processChain: { chainId: 'k2_verkauf', stepKey: 'lieferschein' },
    processChains: {
      k2_verkauf: {
        label: 'Verkauf',
        steps: [
          { key: 'auftrag', label: 'Auftrag', screenId: 'sales/sales-order', routePath: '/verkauf/auftraege' },
          { key: 'lieferschein', label: 'Lieferschein', screenId: 'sales/delivery-note', routePath: '/verkauf/lieferschein-erfassung' },
          { key: 'rechnung', label: 'Rechnung', screenId: 'sales/invoice' },
        ],
      },
    },
    actions: [{ key: 'drucken', label: 'Lieferschein drucken', kind: 'primary', zone: 'footer', keyboardShortcut: 'Ctrl+P' }],
  }
}

function Providers({ children }: { children: ReactNode }): JSX.Element {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/verkauf/lieferschein/1']}>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

class DormantIntersectionObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
  takeRecords(): IntersectionObserverEntry[] { return [] }
}

describe('Meridian one-page document (sectionNavigation=anchors)', () => {
  const scrollIntoView = vi.fn()

  beforeEach(() => {
    scrollIntoView.mockReset()
    Element.prototype.scrollIntoView = scrollIntoView
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('compiles anchors only for document floorplans and defaults to sticky header and footer', () => {
    const plan = compileRenderPlanFromScreenDefinition(deliveryNote())
    expect(plan.shell.sectionNavigation).toBe('anchors')
    expect(plan.shell.stickyHeader).toBe(true)
    expect(plan.shell.stickyFooter).toBe(true)

    const explicit = compileRenderPlanFromScreenDefinition({ ...deliveryNote({ stickyFooter: false }), id: 'sales/explicit-footer' })
    expect(explicit.shell.stickyFooter).toBe(false)

    const worklist = compileRenderPlanFromScreenDefinition({ ...deliveryNote({ floorplan: 'worklist' }), id: 'sales/anchors-worklist' })
    expect(worklist.shell.sectionNavigation).toBe('tabs')

    const split = compileRenderPlanFromScreenDefinition({
      ...deliveryNote({ floorplan: 'objectPage', columnNavigation: 'listDetail' }),
      id: 'sales/anchors-split',
    })
    expect(split.shell.sectionNavigation).toBe('tabs')

    const tabs = compileRenderPlanFromScreenDefinition({ ...deliveryNote({ sectionNavigation: undefined }), id: 'sales/tabs-default' })
    expect(tabs.shell.sectionNavigation).toBe('tabs')
    expect(tabs.shell.stickyHeader).toBe(false)
  })

  it('rejects anchors outside document floorplans and unknown values', () => {
    expect(validateScreenDefinition(deliveryNote())).toEqual([])
    expect(validateScreenDefinition(deliveryNote({ floorplan: 'cockpit' }))).toContain(
      'layout.sectionNavigation=anchors is only supported for objectPage and transaction',
    )
    expect(validateScreenDefinition(deliveryNote({ floorplan: 'objectPage', columnNavigation: 'listDetail' }))).toContain(
      'layout.sectionNavigation=anchors requires columnNavigation=single',
    )
    const invalid = deliveryNote()
    ;(invalid.layout as { sectionNavigation?: string }).sectionNavigation = 'accordion'
    expect(validateScreenDefinition(invalid)).toContain('layout.sectionNavigation is invalid: accordion')
  })

  it('collapses the header with hysteresis instead of a single threshold', () => {
    expect(nextCondensedState(false, HEADER_COLLAPSE_AT_PX)).toBe(false)
    expect(nextCondensedState(false, HEADER_COLLAPSE_AT_PX + 1)).toBe(true)
    expect(nextCondensedState(true, HEADER_COLLAPSE_AT_PX - 10)).toBe(true)
    expect(nextCondensedState(true, HEADER_EXPAND_BELOW_PX + 1)).toBe(true)
    expect(nextCondensedState(true, HEADER_EXPAND_BELOW_PX)).toBe(false)
  })

  it('renders every register as a section on one page with anchors instead of tabs', () => {
    render(
      <Providers>
        <UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition(deliveryNote())} data={{ delivery_note_number: 'LS-1001' }} />
      </Providers>,
    )

    const root = screen.getByTestId('screen-sales/delivery-note')
    expect(root).toHaveAttribute('data-section-navigation', 'anchors')
    expect(screen.queryByRole('tablist')).not.toBeInTheDocument()
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1)
    expect(screen.getByRole('heading', { level: 2, name: 'Lieferschein-Kopf' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'Positionen' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 2, name: 'Dokumente' })).toBeInTheDocument()
    expect(screen.getByDisplayValue('LS-1001')).toBeInTheDocument()

    const nav = screen.getByRole('navigation', { name: 'Abschnitte' })
    const anchors = within(nav).getAllByRole('link')
    expect(anchors.map((anchor) => anchor.textContent)).toEqual(['Lieferschein-Kopf', 'Positionen', 'Dokumente', 'Belegfluss'])
    expect(anchors.map((anchor) => anchor.getAttribute('aria-current'))).toEqual(['location', null, null, null])
    expect(anchors[1]).toHaveAttribute('aria-keyshortcuts', 'Alt+2')
    expect(screen.queryByText(/sales \/ transaction/i)).not.toBeInTheDocument()
  })

  it('jumps to a section by anchor click and by Alt+digit and marks it current', () => {
    render(
      <Providers>
        <UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition(deliveryNote())} />
      </Providers>,
    )

    fireEvent.click(screen.getByTestId('section-anchor-positionen'))
    expect(scrollIntoView).toHaveBeenCalledWith(expect.objectContaining({ block: 'start' }))
    expect(screen.getByTestId('section-anchor-positionen')).toHaveAttribute('aria-current', 'location')
    expect(screen.getByRole('heading', { level: 2, name: 'Positionen' })).toHaveFocus()

    fireEvent.keyDown(screen.getByLabelText('LS-Nr.'), { key: '3', code: 'Digit3', altKey: true })
    expect(screen.getByTestId('section-anchor-dokumente')).toHaveAttribute('aria-current', 'location')
    expect(screen.getByRole('heading', { level: 2, name: 'Dokumente' })).toHaveFocus()
  })

  it('mounts lazy sections only when they approach the viewport or are jumped to', () => {
    vi.stubGlobal('IntersectionObserver', DormantIntersectionObserver)
    render(
      <Providers>
        <UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition(deliveryNote())} />
      </Providers>,
    )

    expect(screen.getByLabelText('LS-Nr.')).toBeInTheDocument()
    expect(screen.queryByLabelText('Charge')).not.toBeInTheDocument()
    fireEvent.click(screen.getByTestId('section-anchor-positionen'))
    expect(screen.getByLabelText('Charge')).toBeInTheDocument()
    expect(screen.queryByLabelText('Bemerkung')).not.toBeInTheDocument()
  })

  it('shows the document flow as the last section with the current step as plain text', () => {
    render(
      <Providers>
        <UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition(deliveryNote())} />
      </Providers>,
    )

    const flow = screen.getByTestId('page-section-belegfluss')
    const current = within(flow).getByTestId('ribbon-step-lieferschein')
    expect(current.tagName).toBe('SPAN')
    expect(current).toHaveAttribute('aria-current', 'step')
    expect(within(flow).getByTestId('ribbon-step-auftrag').tagName).toBe('BUTTON')
    expect(within(flow).getByTestId('ribbon-step-rechnung')).toBeDisabled()
    expect(screen.getAllByTestId('process-ribbon')).toHaveLength(1)
  })

  it('pulls the sticky area over the scroll container padding so content cannot show above it', () => {
    render(
      <Providers>
        <div data-testid="app-scroll" style={{ overflowY: 'auto', paddingTop: '32px' }}>
          <UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition(deliveryNote())} />
        </div>
      </Providers>,
    )

    const sticky = screen.getByTestId('section-page-sticky')
    expect(sticky.style.top).toBe('-32px')
    expect(sticky.style.marginTop).toBe('-32px')
    expect(sticky.style.paddingTop).toBe('32px')
  })

  it('names the document by its number and keeps the mask type as kicker', () => {
    const identified = { ...deliveryNote(), id: 'sales/delivery-note-identity', identityField: 'delivery_note_number' }
    const { unmount } = render(
      <Providers>
        <UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition(identified)} data={{ delivery_note_number: 'LS-1001' }} />
      </Providers>,
    )
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('LS-1001')
    expect(screen.getByTestId('mask-kicker')).toHaveTextContent('Lieferschein')
    unmount()

    render(
      <Providers>
        <UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition(identified)} data={{ delivery_note_number: '  ' }} />
      </Providers>,
    )
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Lieferschein')
    expect(screen.queryByTestId('mask-kicker')).not.toBeInTheDocument()
  })

  it('rejects an identity field the mask does not declare', () => {
    expect(validateScreenDefinition({ ...deliveryNote(), identityField: 'belegnummer' })).toContain(
      'identityField belegnummer is not a declared field',
    )
  })

  it('keeps register tabs when the screen does not declare anchors', () => {
    render(
      <Providers>
        <UniversalMaskRenderer
          plan={compileRenderPlanFromScreenDefinition({ ...deliveryNote({ sectionNavigation: 'tabs' }), id: 'sales/delivery-note-tabs' })}
        />
      </Providers>,
    )

    expect(screen.getByTestId('screen-sales/delivery-note-tabs')).toHaveAttribute('data-section-navigation', 'tabs')
    expect(screen.getByRole('tablist')).toBeInTheDocument()
    expect(screen.queryByTestId('section-anchor-nav')).not.toBeInTheDocument()
  })
})

function dirtyFormState(values: Record<string, unknown>): UniversalFormState {
  return {
    values,
    dirtyState: { isDirty: true, dirtyFields: new Set(['bemerkung']) },
    fieldErrors: {},
    submitState: 'idle',
    submitError: null,
    validationPlan: { rules: [], hasBlockingErrors: false },
    canSubmit: true,
    setValue: vi.fn(),
    resetForm: vi.fn(),
    submit: vi.fn(async () => undefined),
  } as unknown as UniversalFormState
}

function LeaveButton(): JSX.Element {
  const navigate = useNavigate()
  const location = useLocation()
  return (
    <>
      <span data-testid="pathname">{location.pathname}</span>
      <button type="button" onClick={() => navigate('/verkauf/auftraege')}>Wegnavigieren</button>
    </>
  )
}

describe('Meridian unsaved changes guard', () => {
  it('asks before leaving a dirty mask and stays on the mask when the user goes back', async () => {
    render(
      <Providers>
        <UniversalMaskRenderer
          plan={compileRenderPlanFromScreenDefinition({ ...deliveryNote(), id: 'sales/delivery-note-dirty' })}
          formState={dirtyFormState({ bemerkung: 'geändert' })}
        />
        <LeaveButton />
      </Providers>,
    )

    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Wegnavigieren' })) })
    expect(await screen.findByTestId('unsaved-changes-dialog')).toBeInTheDocument()
    expect(screen.getByTestId('pathname')).toHaveTextContent('/verkauf/lieferschein/1')

    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Zurück zur Maske' })) })
    expect(screen.queryByTestId('unsaved-changes-dialog')).not.toBeInTheDocument()
    expect(screen.getByTestId('pathname')).toHaveTextContent('/verkauf/lieferschein/1')

    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Wegnavigieren' })) })
    await act(async () => { fireEvent.click(await screen.findByRole('button', { name: 'Änderungen verwerfen' })) })
    expect(screen.queryByTestId('unsaved-changes-dialog')).not.toBeInTheDocument()
  })

  it('does not arm the guard for a clean mask', async () => {
    const clean = { ...dirtyFormState({}), dirtyState: { isDirty: false, dirtyFields: new Set<string>() } } as UniversalFormState
    render(
      <Providers>
        <UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition({ ...deliveryNote(), id: 'sales/delivery-note-clean' })} formState={clean} />
        <LeaveButton />
      </Providers>,
    )

    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Wegnavigieren' })) })
    expect(screen.queryByTestId('unsaved-changes-dialog')).not.toBeInTheDocument()
  })
})
