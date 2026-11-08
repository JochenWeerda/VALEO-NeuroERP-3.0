import type { ReactNode } from 'react'
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import MaterialflussPage from '@/pages/lager/materialfluss'

const fixture = vi.hoisted(() => ({
  empty: [] as Record<string, unknown>[], error: false,
  systems: [{ id: 'system-a', system_code: 'SYNTH', name: 'Testanlage' }],
  toast: vi.fn(), createSystem: vi.fn(), createCell: vi.fn(),
  warehouseReads: vi.fn(),
  cells: [] as Record<string, unknown>[], nodes: [] as Record<string, unknown>[], edges: [] as Record<string, unknown>[],
  patchCell: vi.fn(), patchNode: vi.fn(), patchEdge: vi.fn(),
}))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: fixture.toast }) }))
vi.mock('@/components/navigation/PageToolbar', () => ({
  PageToolbar: ({ rightSlot }: { rightSlot?: ReactNode }) => <header>{rightSlot}</header>,
}))
vi.mock('@xyflow/react', () => ({
  ReactFlow: ({ children }: { children?: ReactNode }) => <section aria-label="Materialflussgraph">{children}</section>,
  Background: () => null, Controls: () => null, Handle: () => null, MiniMap: () => null,
  Panel: ({ children }: { children?: ReactNode }) => <div>{children}</div>,
  Position: { Left: 'left', Right: 'right' },
}))
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
    useCreateAgriFlowNode: mutation, useCreateAgriFlowEdge: mutation,
    useBookAgriMaterialTransfer: mutation, useBookAgriLotToCell: mutation, useSyncAgriSiloCellFromLots: mutation,
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
  fixture.createSystem.mockResolvedValue({ id: 'new-system' })
  fixture.createCell.mockResolvedValue({ id: 'new-cell' })
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
})
