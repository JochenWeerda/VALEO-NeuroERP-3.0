import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from '@/app/routing/test-router'
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { ColumnLayoutRenderer, type NavigationColumn } from '@/components/mask-builder/renderers/ColumnLayoutRenderer'
import { FastTableRenderer } from '@/components/mask-builder/renderers/FastTableRenderer'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { validateScreenDefinition, type ScreenDefinition } from '@/components/mask-builder/schema'

let resize: (width: number) => void
beforeEach(() => {
  vi.stubGlobal('ResizeObserver', class {
    constructor(callback: ResizeObserverCallback) {
      resize = width => callback([{ contentRect: { width } } as ResizeObserverEntry], {} as ResizeObserver)
    }
    observe() {}
    unobserve() {}
    disconnect() {}
  })
})
afterEach(() => vi.unstubAllGlobals())
const columns: NavigationColumn[] = [
  { key: 'list', title: 'Aufträge', content: <input aria-label="Suche" defaultValue="Weizen" /> },
  { key: 'object', title: 'Auftrag 100', content: <input aria-label="Notiz" defaultValue="Entwurf" /> },
  { key: 'position', title: 'Position 1', content: <p>25 Tonnen</p> },
]

describe('Meridian column navigation', () => {
  it('adapts to available width and preserves search and edits when returning', () => {
    const { container } = render(<ColumnLayoutRenderer pattern="listDetailDetail" columns={columns} />)
    expect(container.querySelector('[data-visible-columns]')).toHaveAttribute('data-visible-columns', '1')
    act(() => resize(1500))
    expect(container.querySelector('[data-visible-columns]')).toHaveAttribute('data-visible-columns', '3')
    fireEvent.change(screen.getByLabelText('Notiz'), { target: { value: 'Nicht verlieren' } })
    act(() => resize(1100))
    expect(container.querySelector('[data-visible-columns]')).toHaveAttribute('data-visible-columns', '2')
    fireEvent.click(screen.getByRole('button', { name: 'Vollansicht' }))
    expect(container.querySelector('[data-visible-columns]')).toHaveAttribute('data-visible-columns', '1')
    fireEvent.click(screen.getByRole('button', { name: 'Zurück zu Auftrag 100' }))
    expect(screen.getByLabelText('Notiz')).toHaveValue('Nicht verlieren')
    fireEvent.click(screen.getByRole('button', { name: 'Zurück zu Aufträge' }))
    expect(screen.getByLabelText('Suche')).toHaveValue('Weizen')
  })
  it('opens a newly selected object without remounting the list', async () => {
    const { rerender } = render(<ColumnLayoutRenderer pattern="listDetail" columns={columns.slice(0, 1)} />)
    fireEvent.change(screen.getByLabelText('Suche'), { target: { value: 'Gerste' } })
    rerender(<ColumnLayoutRenderer pattern="listDetail" columns={columns.slice(0, 2)} />)
    await waitFor(() => expect(screen.getByRole('region', { name: 'Auftrag 100' })).toBeVisible())
    fireEvent.click(screen.getByRole('button', { name: 'Zurück zu Aufträge' }))
    expect(screen.getByLabelText('Suche')).toHaveValue('Gerste')
  })
  it('rejects columns not enabled by the compiled contract', () => {
    expect(() => render(<ColumnLayoutRenderer pattern="listDetail" columns={columns} />)).toThrow(/contract/)
  })
})

describe('Framework contracts', () => {
  const definition: ScreenDefinition = {
    id: 'test/framework', schemaVersion: 1, domain: 'crm', mode: 'detail', title: 'Kunde',
    layout: { floorplan: 'objectPage', contextRail: 'none', columnNavigation: 'listDetailDetail' },
    tabs: [
      { key: 'base', label: 'Basis', fields: [{ key: 'name', label: 'Name', type: 'text' }] },
      { key: 'address', label: 'Adresse', fields: [{ key: 'city', label: 'Ort', type: 'text' }] },
    ],
  }
  it('compiles navigation independently from floorplan and context rail', () => {
    const plan = compileRenderPlanFromScreenDefinition(definition)
    expect(plan.shell.columnNavigation).toBe('listDetailDetail')
    expect(plan.shell.floorplan).toBe('objectPage')
    expect(plan.shell.contextRail).toBe('none')
    expect(validateScreenDefinition({ ...definition, layout: { columnNavigation: 'four' as never } })).toContain('layout.columnNavigation is invalid')
    expect(validateScreenDefinition({
      ...definition,
      id: 'test/transaction-columns',
      layout: { floorplan: 'transaction', columnNavigation: 'listDetail' },
    })).toContain('layout.columnNavigation is not supported for this floorplan')
    const analytical = compileRenderPlanFromScreenDefinition({
      ...definition,
      id: 'test/analytical-list',
      mode: 'list',
      layout: { floorplan: 'analyticalList', columnNavigation: 'listDetail', contextRail: 'none' },
    })
    expect(analytical.shell.floorplan).toBe('analyticalList')
    expect(analytical.shell.columnNavigation).toBe('listDetail')
  })
  it('keeps errors visible and opens the field in an inactive register', async () => {
    render(<QueryClientProvider client={new QueryClient()}><MemoryRouter><UniversalMaskRenderer plan={compileRenderPlanFromScreenDefinition(definition)}
      messages={[{ key: 'city-required', severity: 'error', fieldKey: 'city', message: 'Ort fehlt' }]} /></MemoryRouter></QueryClientProvider>)
    expect(screen.getByRole('alert')).toHaveTextContent('Ort fehlt')
    expect(screen.queryByLabelText('Ort')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Zum Feld' }))
    await waitFor(() => expect(screen.getByLabelText('Ort')).toHaveFocus())
  })
})

describe('Table load errors', () => {
  const table = {
    key: 'orders',
    label: 'Aufträge',
    columns: [{ key: 'nr', label: 'Nr' }, { key: 'status', label: 'Status' }],
    pageSize: 25,
    virtualized: true,
    rowHeight: 44,
    serverPagination: true,
    tableProfile: 'standard' as const,
  }

  it('does not present a load failure as an empty result list', () => {
    const { rerender } = render(
      <FastTableRenderer table={table} rows={[]} errorMessage={'Tabelle „Aufträge“ konnte nicht geladen werden.'} />,
    )
    expect(screen.getByRole('alert')).toHaveTextContent('konnte nicht geladen werden')
    expect(screen.queryByText('Keine Eintraege vorhanden.')).not.toBeInTheDocument()
    rerender(<FastTableRenderer table={table} rows={[]} />)
    expect(screen.getByText('Keine Eintraege vorhanden.')).toBeInTheDocument()
  })
})

describe('Derived worklist columns', () => {
  const definition: ScreenDefinition = {
    id: 'test/derived-worklist',
    schemaVersion: 1,
    domain: 'crm',
    mode: 'list',
    title: 'Analysen',
    layout: { floorplan: 'worklist', contextRail: 'none' },
    tables: [{
      key: 'list',
      label: 'Analysen',
      columns: [{ key: 'probe_nr', label: 'Probe' }, { key: 'bezeichnung', label: 'Material' }],
      rowRouteTemplate: '/analysen/{id}',
      pageSize: 25,
      virtualized: true,
      rowHeight: 44,
    }],
  }

  it('selects a row beside the list and opens the full view from the preview', async () => {
    const pushState = vi.spyOn(window.history, 'pushState')
    render(
      <QueryClientProvider client={new QueryClient()}>
        <MemoryRouter>
          <UniversalMaskRenderer
            plan={compileRenderPlanFromScreenDefinition(definition)}
            tables={{
              list: [
                { id: 'a1', probe_nr: 'P-1', bezeichnung: 'Grassilage' },
                { id: 'a2', probe_nr: 'P-2', bezeichnung: 'Maissilage' },
              ],
            }}
          />
        </MemoryRouter>
      </QueryClientProvider>,
    )
    expect(screen.getByTestId('screen-test/derived-worklist')).toHaveAttribute('data-column-navigation', 'listDetail')
    expect(document.querySelector('[data-column-source]')).toHaveAttribute('data-column-source', 'derived')
    await waitFor(() => expect(screen.getByTestId('selected-record-panel')).toHaveTextContent('Grassilage'))
    fireEvent.click(screen.getByText('Maissilage'))
    expect(screen.getByTestId('selected-record-panel')).toHaveTextContent('Maissilage')
    fireEvent.click(screen.getByRole('button', { name: 'In Vollansicht öffnen' }))
    expect(pushState).toHaveBeenCalledWith(null, '', '/analysen/a2')
    pushState.mockRestore()
  })
})
