import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, within } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { UniversalMaskRenderer, validateScreenDefinition } from '@/components/mask-builder'
import {
  compileRenderPlanFromScreenDefinition,
  invalidateRenderPlanCache,
} from '@/components/mask-builder/render-plan/schema-compiler'
import type { ScreenDefinition, ScreenTableDefinition } from '@/components/mask-builder/schema'
import { MemoryRouter } from '@/app/routing/test-router'

const POSITIONS: ScreenTableDefinition = {
  key: 'positionen',
  label: 'Positionen',
  dataSourceKey: 'positionen',
  columns: [
    { key: 'line_no', label: 'Pos.' },
    { key: 'description', label: 'Bezeichnung' },
    { key: 'net_amount', label: 'Netto', numeric: true, renderKind: 'currency' },
  ],
  rowDetail: {
    fields: [
      { key: 'line_no', label: 'Pos.' },
      { key: 'description', label: 'Bezeichnung' },
      { key: 'net_amount', label: 'Netto', renderKind: 'currency' },
      { key: 'vat_rate', label: 'Steuersatz %', renderKind: 'number' },
      { key: 'herkunft', label: 'Herkunft' },
    ],
  },
}

// The render-plan cache is keyed by screen id, so every variant needs its own id.
function invoice(table: ScreenTableDefinition = POSITIONS, id = 'sales/invoice'): ScreenDefinition {
  return {
    schemaVersion: 1,
    id,
    domain: 'sales',
    mode: 'detail',
    title: 'Ausgangsrechnung',
    layout: {
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      floorplan: 'objectPage',
      columnNavigation: 'single',
      sectionNavigation: 'anchors',
      contextRail: 'none',
      tableProfile: 'financial',
    },
    dataSources: [{ key: 'positionen', endpoint: '/api/v1/sales/invoices/{entity_id}/tabs/positionen' }],
    tabs: [
      { key: 'kopf', label: 'Rechnungskopf', fields: [{ key: 'invoice_number', label: 'Rechnungsnr.', type: 'text', readOnly: true }] },
      { key: 'positionen', label: 'Positionen', tables: [table] },
    ],
    actions: [],
  }
}

const ROWS = [
  { line_no: '1', description: 'Weizen A', net_amount: 2500, vat_rate: 7, herkunft: 'Belegt' },
  { line_no: '2', description: 'Duenger NPK', net_amount: 1000, vat_rate: 19, herkunft: '40 dt ohne Zuordnung' },
]

function Providers({ children }: { children: ReactNode }): JSX.Element {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/verkauf/rechnung/1']}>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

function renderInvoice(definition: ScreenDefinition = invoice()): void {
  render(
    <Providers>
      <UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition(definition)} tables={{ positionen: ROWS }} />
    </Providers>,
  )
}

function rowOf(text: string): HTMLElement {
  const row = within(screen.getByTestId('table-positionen')).getByText(text).closest('[role="button"]')
  if (!(row instanceof HTMLElement)) throw new Error(`row for ${text} is not selectable`)
  return row
}

describe('Row detail band (table.rowDetail)', () => {
  beforeEach(() => {
    invalidateRenderPlanCache()
    Element.prototype.scrollIntoView = vi.fn()
  })

  it('compiles declared fields and falls back to the table columns', () => {
    const declared = compileRenderPlanFromScreenDefinition(invoice())
    expect(declared.tablesByKey.positionen.rowDetail?.fields.map((field) => field.key)).toEqual([
      'line_no', 'description', 'net_amount', 'vat_rate', 'herkunft',
    ])

    const fallback = compileRenderPlanFromScreenDefinition(invoice({ ...POSITIONS, rowDetail: {} }, 'sales/invoice-fallback'))
    expect(fallback.tablesByKey.positionen.rowDetail?.fields).toEqual([
      { key: 'line_no', label: 'Pos.', renderKind: undefined },
      { key: 'description', label: 'Bezeichnung', renderKind: undefined },
      { key: 'net_amount', label: 'Netto', renderKind: 'currency' },
    ])

    const without = compileRenderPlanFromScreenDefinition(invoice({ ...POSITIONS, rowDetail: undefined }, 'sales/invoice-plain'))
    expect(without.tablesByKey.positionen.rowDetail).toBeUndefined()
  })

  it('rejects detail fields without label and duplicated keys', () => {
    expect(validateScreenDefinition(invoice())).toEqual([])
    const broken = invoice({
      ...POSITIONS,
      rowDetail: { fields: [{ key: 'line_no', label: ' ' }, { key: 'unit', label: 'Einheit' }, { key: 'unit', label: 'Einheit' }] },
    })
    expect(validateScreenDefinition(broken)).toEqual([
      'table positionen rowDetail field requires key and label',
      'table positionen rowDetail field is duplicated: unit',
    ])
  })

  it('opens the selected position below the grid instead of a dialog', () => {
    renderInvoice()
    expect(screen.queryByTestId('row-detail-band-positionen')).not.toBeInTheDocument()

    fireEvent.click(rowOf('Duenger NPK'))

    const band = screen.getByTestId('row-detail-band-positionen')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(band).toHaveAccessibleName('Pos. 2')
    expect(within(band).getByTestId('row-detail-positionen-herkunft')).toHaveTextContent('40 dt ohne Zuordnung')
    expect(within(band).getByTestId('row-detail-positionen-vat_rate')).toHaveTextContent('19')
    expect(within(band).getByTestId('row-detail-positionen-net_amount').textContent).toMatch(/1\.000,00\s€/)
    expect(rowOf('Duenger NPK')).toHaveAttribute('aria-selected', 'true')
  })

  it('switches to another position and closes by toggle, button and Escape', () => {
    renderInvoice()

    fireEvent.click(rowOf('Weizen A'))
    expect(screen.getByTestId('row-detail-band-positionen')).toHaveAccessibleName('Pos. 1')
    fireEvent.click(rowOf('Duenger NPK'))
    expect(screen.getByTestId('row-detail-band-positionen')).toHaveAccessibleName('Pos. 2')

    fireEvent.click(rowOf('Duenger NPK'))
    expect(screen.queryByTestId('row-detail-band-positionen')).not.toBeInTheDocument()

    fireEvent.click(rowOf('Weizen A'))
    fireEvent.click(screen.getByRole('button', { name: 'Details schließen' }))
    expect(screen.queryByTestId('row-detail-band-positionen')).not.toBeInTheDocument()

    fireEvent.click(rowOf('Weizen A'))
    fireEvent.keyDown(screen.getByTestId('row-detail-band-positionen'), { key: 'Escape' })
    expect(screen.queryByTestId('row-detail-band-positionen')).not.toBeInTheDocument()
  })

  it('keeps rows plain when the table declares no detail band', () => {
    renderInvoice(invoice({ ...POSITIONS, rowDetail: undefined }, 'sales/invoice-plain'))
    expect(screen.getByText('Weizen A').closest('[role="button"]')).toBeNull()
    expect(screen.queryByTestId('row-detail-band-positionen')).not.toBeInTheDocument()
  })
})
