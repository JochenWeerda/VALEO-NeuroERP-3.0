import type { ReactNode } from 'react'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import MaterialflussPage from '@/pages/lager/materialfluss-legacy'

const fixture = vi.hoisted(() => ({
  empty: [] as Record<string, unknown>[], error: false,
  systems: [{ id: 'system-a', system_code: 'SYNTH', name: 'Testanlage' }],
  toast: vi.fn(), createSystem: vi.fn(), createCell: vi.fn(),
  warehouseReads: vi.fn(),
  cells: [] as Record<string, unknown>[], nodes: [] as Record<string, unknown>[], edges: [] as Record<string, unknown>[],
  patchCell: vi.fn(), patchNode: vi.fn(), patchEdge: vi.fn(), syncLot: vi.fn(),
  createNode: vi.fn(), createEdge: vi.fn(), bookTransfer: vi.fn(), bookLot: vi.fn(),
  validateRoute: vi.fn(), suggestLot: vi.fn(),
}))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: fixture.toast }) }))
vi.mock('@/components/navigation/PageToolbar', () => ({
  PageToolbar: ({ rightSlot }: { rightSlot?: ReactNode }) => <header>{rightSlot}</header>,
}))
vi.mock('@xyflow/react', async () => {
  const React = await import('react')
  return {
    ReactFlow: ({
      children,
      nodes,
      nodeTypes,
    }: {
      children?: ReactNode
      nodes?: Array<{ id: string; type?: string; data?: Record<string, unknown> }>
      nodeTypes?: Record<string, React.ComponentType<{ id: string; data: Record<string, unknown> }>>
    }) => (
      <section aria-label="Materialflussgraph">
        {(nodes ?? []).map((node) => {
          const Comp = node.type ? nodeTypes?.[node.type] : undefined
          return Comp ? (
            <div key={node.id} data-testid={`mf-node-${node.id}`}>
              {React.createElement(Comp, { id: node.id, data: node.data ?? {} })}
            </div>
          ) : null
        })}
        {children}
      </section>
    ),
    Background: () => null, Controls: () => null, Handle: () => null, MiniMap: () => null,
    Panel: ({ children }: { children?: ReactNode }) => <div>{children}</div>,
    Position: { Left: 'left', Right: 'right' },
  }
})
vi.mock('@/lib/api/inventory', () => ({
  useWarehouses: () => ({ data: { items: [{ id: 'warehouse-a', code: 'A', name: 'Testlager A' }, { id: 'warehouse-b', code: 'B', name: 'Testlager B' }] } }),
}))
vi.mock('@/lib/api/agri-material-flow', async importOriginal => {
  const original = await importOriginal<typeof import('@/lib/api/agri-material-flow')>()
  const query = (warehouseId: string | undefined, data: Record<string, unknown>[]) => {
    fixture.warehouseReads(warehouseId)
    return { data: warehouseId ? data : fixture.empty, isLoading: false, isError: fixture.error, error: new Error('Synthetischer Lesefehler') }
  }
  const mutation = () => ({ mutateAsync: vi.fn(), isPending: false })
  return { ...original,
    useAgriSiloCells: (warehouseId?: string) => query(warehouseId, fixture.cells),
    useAgriFlowNodes: (warehouseId?: string) => query(warehouseId, fixture.nodes),
    useAgriFlowEdges: (warehouseId?: string) => query(warehouseId, fixture.edges),
    useAgriSiloSystems: (warehouseId?: string) => ({ data: warehouseId ? fixture.systems : fixture.empty, isLoading: false }),
    useCreateAgriSiloSystem: () => ({ mutateAsync: fixture.createSystem }),
    useCreateAgriSiloCell: () => ({ mutateAsync: fixture.createCell }),
    usePatchAgriSiloCell: () => ({ mutateAsync: fixture.patchCell }),
    usePatchAgriFlowNode: () => ({ mutateAsync: fixture.patchNode }),
    usePatchAgriFlowEdge: () => ({ mutateAsync: fixture.patchEdge }),
    useCreateAgriFlowNode: () => ({ mutateAsync: fixture.createNode, isPending: false }),
    useCreateAgriFlowEdge: () => ({ mutateAsync: fixture.createEdge, isPending: false }),
    useBookAgriMaterialTransfer: () => ({ mutateAsync: fixture.bookTransfer, isPending: false }),
    useBookAgriLotToCell: () => ({ mutateAsync: fixture.bookLot, isPending: false }),
    useSyncAgriSiloCellFromLots: () => ({ mutateAsync: fixture.syncLot, isPending: false }),
    validateAgriMaterialRoute: (...args: unknown[]) => fixture.validateRoute(...args),
    suggestAgriLotLink: (...args: unknown[]) => fixture.suggestLot(...args),
  }
})
function selectWarehouse(id = 'warehouse-a') {
  fireEvent.change(screen.getByLabelText('Lager'), { target: { value: id } })
}
beforeEach(() => {
  vi.clearAllMocks()
  fixture.error = false
  fixture.cells = []
  fixture.nodes = []
  fixture.edges = []
  fixture.patchCell.mockResolvedValue({})
  fixture.patchNode.mockResolvedValue({})
  fixture.patchEdge.mockResolvedValue({})
  fixture.syncLot.mockResolvedValue({})
  fixture.createSystem.mockResolvedValue({ id: 'new-system' })
  fixture.createCell.mockResolvedValue({ id: 'new-cell' })
  fixture.createNode.mockResolvedValue({ id: 'node-new' })
  fixture.createEdge.mockResolvedValue({ id: 'edge-new' })
  fixture.bookTransfer.mockResolvedValue({ ok: true })
  fixture.bookLot.mockResolvedValue({ ok: true })
  fixture.validateRoute.mockResolvedValue({ valid: true, path: ['node-a', 'node-b'] })
  fixture.suggestLot.mockResolvedValue({ lot_id: 'LOT-S', cell_id: 'cell-a' })
})
afterEach(cleanup)

describe('Materialfluss-Arbeitsplatz: Lagerbindung und Eingaben', () => {
  it('kennzeichnet die Vorschau ohne Lager und bietet keine Stammdatenanlage an', () => {
    render(<MaterialflussPage />)
    expect(screen.getByText('Materialfluss (React Flow — Demo)')).toBeTruthy()
    expect(screen.queryByRole('button', { name: 'Siloanlage anlegen' })).toBeNull()
    expect(fixture.createSystem).not.toHaveBeenCalled()
  })

  it('wechselt nach Lagerwahl von Demo auf ehrlichen leeren Livebestand', () => {
    render(<MaterialflussPage />)
    selectWarehouse()
    expect(screen.getByText('Materialfluss (React Flow — noch keine Knoten/Kanten)')).toBeTruthy()
    expect(fixture.warehouseReads).toHaveBeenCalledWith('warehouse-a')
    selectWarehouse('warehouse-b')
    expect(fixture.warehouseReads).toHaveBeenLastCalledWith('warehouse-b')
    expect(fixture.createSystem).not.toHaveBeenCalled()
  })

  it('verschleiert einen API-Fehler nicht durch Demo- oder Leerdaten', () => {
    fixture.error = true
    render(<MaterialflussPage />)
    selectWarehouse()
    expect(screen.getByText('Materialfluss (React Flow — API-Fehler)')).toBeTruthy()
    expect(screen.queryByText('Materialfluss (React Flow — Demo)')).toBeNull()
  })

  it('weist fehlende Pflichtangaben vor jedem Anlageauftrag ab', () => {
    render(<MaterialflussPage />)
    selectWarehouse()
    fireEvent.click(screen.getByRole('button', { name: 'Siloanlage anlegen' }))
    expect(fixture.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Angaben fehlen', variant: 'destructive' }))
    expect(fixture.createSystem).not.toHaveBeenCalled()
  })

  it('bindet den Anlageauftrag an das zuletzt gewaehlte Lager und leert erst nach Erfolg', async () => {
    render(<MaterialflussPage />)
    selectWarehouse()
    fireEvent.change(screen.getByLabelText('system_code'), { target: { value: ' SYNTH-NEW ' } })
    fireEvent.change(screen.getByLabelText('Name', { selector: '#mf-sys-name' }), { target: { value: ' Testanlage neu ' } })
    selectWarehouse('warehouse-b')
    expect(screen.getByLabelText('system_code')).toHaveValue('')
    expect(screen.getByLabelText('Name', { selector: '#mf-sys-name' })).toHaveValue('')
    expect(fixture.createSystem).not.toHaveBeenCalled()
    fireEvent.change(screen.getByLabelText('system_code'), { target: { value: ' SYNTH-NEW ' } })
    fireEvent.change(screen.getByLabelText('Name', { selector: '#mf-sys-name' }), { target: { value: ' Testanlage neu ' } })
    fireEvent.click(screen.getByRole('button', { name: 'Siloanlage anlegen' }))
    await waitFor(() => expect(fixture.createSystem).toHaveBeenCalledExactlyOnceWith({ warehouseId: 'warehouse-b', body: { system_code: 'SYNTH-NEW', name: 'Testanlage neu' } }))
    await waitFor(() => expect(screen.getByLabelText('system_code')).toHaveValue(''))
  })

  it('erhaelt Eingaben nach abgelehntem Auftrag fuer einen bewussten erneuten Versuch', async () => {
    fixture.createSystem.mockRejectedValue(new Error('Synthetischer Schreibfehler'))
    render(<MaterialflussPage />)
    selectWarehouse()
    fireEvent.change(screen.getByLabelText('system_code'), { target: { value: 'RETRY' } })
    fireEvent.change(screen.getByLabelText('Name', { selector: '#mf-sys-name' }), { target: { value: 'Testanlage' } })
    fireEvent.click(screen.getByRole('button', { name: 'Siloanlage anlegen' }))
    await waitFor(() => expect(fixture.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Anlegen fehlgeschlagen', variant: 'destructive' })))
    expect(screen.getByLabelText('system_code')).toHaveValue('RETRY')
    expect(fixture.createSystem).toHaveBeenCalledTimes(1)
  })

  it('legt eine Zelle mit numerischer Kapazitaet in der ausgewaehlten Anlage an', async () => {
    render(<MaterialflussPage />)
    selectWarehouse()
    fireEvent.change(screen.getByLabelText('cell_code'), { target: { value: ' C-NEW ' } })
    fireEvent.change(screen.getByLabelText('Name', { selector: '#mf-cell-name' }), { target: { value: ' Testzelle ' } })
    fireEvent.change(screen.getByLabelText('capacity_kg (optional)'), { target: { value: '1234.5' } })
    fireEvent.click(screen.getByRole('button', { name: 'Silozelle anlegen' }))
    await waitFor(() => expect(fixture.createCell).toHaveBeenCalledExactlyOnceWith({ warehouseId: 'warehouse-a', siloSystemId: 'system-a', body: { cell_code: 'C-NEW', name: 'Testzelle', capacity_kg: 1234.5 } }))
  })

  it('setzt QS-Auswahl nach abgelehnter Aenderung auf den bestaetigten Stand zurueck', async () => {
    fixture.cells = [{ id: 'cell-a', cell_code: 'CELL-A', name: 'Testzelle', qs_status: 'frei' }]
    fixture.patchCell.mockRejectedValue(new Error('Synthetische Sperre'))
    render(<MaterialflussPage />)
    selectWarehouse()
    const row = screen.getByRole('row', { name: /CELL-A/ })
    const status = within(row).getByRole('combobox')
    fireEvent.change(status, { target: { value: 'gesperrt' } })
    await waitFor(() => expect(fixture.patchCell).toHaveBeenCalledExactlyOnceWith({ cellId: 'cell-a', warehouseId: 'warehouse-a', body: { qs_status: 'gesperrt' } }))
    await waitFor(() => expect(status).toHaveValue('frei'))
    expect(fixture.toast).toHaveBeenCalledWith(expect.objectContaining({ title: 'Speichern fehlgeschlagen' }))
  })

  it('bindet einen Knotenstatus an angezeigten Knoten und Lager', async () => {
    fixture.nodes = [{ id: 'node-a', code: 'NODE-A', name: 'Testknoten', node_type: 'intake', status: 'active' }]
    render(<MaterialflussPage />)
    selectWarehouse()
    expect(screen.getByText('Materialfluss (React Flow — Live-Stammdaten)')).toBeTruthy()
    const row = screen.getByRole('row', { name: /NODE-A/ })
    fireEvent.change(within(row).getByRole('combobox'), { target: { value: 'maintenance' } })
    await waitFor(() => expect(fixture.patchNode).toHaveBeenCalledExactlyOnceWith({ nodeId: 'node-a', warehouseId: 'warehouse-a', body: { status: 'maintenance' } }))
  })

  it('rendert Demo-Knoten inkl. Statuslabel und Untertitel', () => {
    render(<MaterialflussPage />)
    expect(screen.getByTestId('mf-node-n-intake')).toBeTruthy()
    expect(screen.getByText('Annahme')).toBeTruthy()
    expect(screen.getByText('Silozelle A1')).toBeTruthy()
    expect(screen.getByText('Weizen')).toBeTruthy()
    expect(screen.getByText('QS gesperrt')).toBeTruthy()
  })

  it('speichert Material/Lot einer Zelle und setzt Legacy-Silo', async () => {
    fixture.cells = [{
      id: 'cell-a',
      cell_code: 'CELL-A',
      name: 'Testzelle',
      qs_status: 'frei',
      current_material_id: 'MAT-1',
      current_lot_id: 'LOT-1',
      legacy_silo_id: 'LEG-1',
    }]
    render(<MaterialflussPage />)
    selectWarehouse()
    const row = screen.getByRole('row', { name: /CELL-A/ })
    const materialInput = within(row).getByPlaceholderText('current_material_id')
    const lotInput = within(row).getByPlaceholderText('current_lot_id')
    fireEvent.change(materialInput, { target: { value: 'MAT-2' } })
    fireEvent.change(lotInput, { target: { value: 'LOT-2' } })
    fireEvent.click(within(row).getByRole('button', { name: 'Material / Lot speichern' }))
    await waitFor(() => expect(fixture.patchCell).toHaveBeenCalledWith(
      expect.objectContaining({
        cellId: 'cell-a',
        warehouseId: 'warehouse-a',
        body: expect.objectContaining({ current_material_id: 'MAT-2', current_lot_id: 'LOT-2' }),
      }),
    ))
    fireEvent.change(within(row).getByPlaceholderText('legacy_silo_id'), { target: { value: 'LEG-9' } })
    fireEvent.click(within(row).getByRole('button', { name: 'Legacy-Silo speichern' }))
    await waitFor(() => expect(fixture.patchCell).toHaveBeenCalledWith(
      expect.objectContaining({
        cellId: 'cell-a',
        body: expect.objectContaining({ legacy_silo_id: 'LEG-9' }),
      }),
    ))
    fireEvent.click(within(row).getByRole('button', { name: 'Aus silo_lots sync' }))
    await waitFor(() => expect(fixture.syncLot).toHaveBeenCalled())
  })

  it('zeigt Live-Knoten im Graph nach Lagerwahl', () => {
    fixture.nodes = [
      { id: 'node-a', code: 'NODE-A', name: 'Annahme Live', node_type: 'intake', status: 'active' },
      { id: 'node-b', code: 'NODE-B', name: 'Waage Live', node_type: 'scale', status: 'blocked', sub: 'gesperrt' },
    ]
    render(<MaterialflussPage />)
    selectWarehouse()
    expect(screen.getByTestId('mf-node-node-a')).toBeTruthy()
    expect(screen.getByText('Annahme Live')).toBeTruthy()
    expect(screen.getByText('Waage Live')).toBeTruthy()
  })

  it('legt Knoten und Kante an und prueft Route sowie Transfer/Lot', async () => {
    fixture.nodes = [
      { id: 'node-a', code: 'NODE-A', name: 'A', node_type: 'intake', status: 'active' },
      { id: 'node-b', code: 'NODE-B', name: 'B', node_type: 'scale', status: 'active' },
    ]
    fixture.cells = [
      { id: 'cell-a', cell_code: 'CELL-A', name: 'Zelle A', qs_status: 'frei', current_material_id: 'ART-1', current_lot_id: 'LOT-A', current_stock_kg: 50 },
      { id: 'cell-b', cell_code: 'CELL-B', name: 'Zelle B', qs_status: 'frei', current_stock_kg: 0 },
    ]
    fixture.edges = [{
      id: 'edge-a',
      from_node_id: 'node-a',
      to_node_id: 'node-b',
      edge_mode: 'gravity',
      status: 'active',
      contamination_guard_enabled: false,
      flush_required: false,
      capacity_kg: 1000,
    }]
    render(<MaterialflussPage />)
    selectWarehouse()

    fireEvent.change(screen.getByLabelText('code'), { target: { value: ' NEW-N ' } })
    fireEvent.change(screen.getByLabelText('name', { selector: '#mf-node-name' }), { target: { value: ' Neu ' } })
    fireEvent.click(screen.getByRole('button', { name: 'Knoten anlegen' }))
    await waitFor(() => expect(fixture.createNode).toHaveBeenCalled())

    fireEvent.change(screen.getByLabelText('von_node_id'), { target: { value: 'node-a' } })
    fireEvent.change(screen.getByLabelText('nach_node_id'), { target: { value: 'node-b' } })
    fireEvent.click(screen.getByRole('button', { name: 'Kante anlegen' }))
    await waitFor(() => expect(fixture.createEdge).toHaveBeenCalled())

    fireEvent.change(screen.getByLabelText('Von-Knoten'), { target: { value: 'node-a' } })
    fireEvent.change(screen.getByLabelText('Nach-Knoten'), { target: { value: 'node-b' } })
    fireEvent.click(screen.getByRole('button', { name: 'Route validieren' }))
    await waitFor(() => expect(fixture.validateRoute).toHaveBeenCalled())

    fireEvent.change(screen.getByLabelText('Von-Silozelle'), { target: { value: 'cell-a' } })
    fireEvent.change(screen.getByLabelText('Nach-Silozelle'), { target: { value: 'cell-b' } })
    fireEvent.change(screen.getByLabelText('quantity_kg'), { target: { value: '10' } })
    fireEvent.change(screen.getByLabelText('article_id'), { target: { value: 'ART-1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Transfer buchen' }))
    await waitFor(() => expect(fixture.bookTransfer).toHaveBeenCalled())

    fireEvent.change(screen.getByLabelText('lot_id (silo_lots)'), { target: { value: 'LOT-1' } })
    fireEvent.change(screen.getByLabelText('Ziel-Silozelle'), { target: { value: 'cell-b' } })
    fireEvent.click(screen.getByRole('button', { name: 'Lot in Silozelle buchen' }))
    await waitFor(() => expect(fixture.bookLot).toHaveBeenCalled())
  })

  it('patcht Kanten-Status, Verschleppung, Spuelcharge und Kapazitaet', async () => {
    fixture.nodes = [
      { id: 'node-a', code: 'NODE-A', name: 'A', node_type: 'intake', status: 'active', layout_x: '10', layout_y: '20' },
      { id: 'node-b', code: 'NODE-B', name: 'B', node_type: 'scale', status: 'active' },
    ]
    fixture.edges = [{
      id: 'edge-a',
      from_node_id: 'node-a',
      to_node_id: 'node-b',
      edge_mode: 'gravity',
      status: 'active',
      contamination_guard_enabled: false,
      flush_required: false,
      max_capacity_kg_h: '100',
    }]
    render(<MaterialflussPage />)
    selectWarehouse()

    const edgeSection = screen.getByText('Kanten').closest('div')!
    const selects = within(edgeSection).getAllByRole('combobox')
    fireEvent.change(selects[1], { target: { value: '1' } }) // Verschleppungsschutz an
    fireEvent.change(selects[2], { target: { value: '1' } }) // Spülcharge nötig
    await waitFor(() => expect(fixture.patchEdge.mock.calls.length).toBeGreaterThanOrEqual(2))

    const capacityInput = within(edgeSection).getByDisplayValue('100')
    fireEvent.change(capacityInput, { target: { value: '250' } })
    fireEvent.click(within(edgeSection).getByRole('button', { name: 'Kapazität' }))
    await waitFor(() => expect(fixture.patchEdge).toHaveBeenCalled())
  })
})
