import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FastTableRenderer } from '@/components/mask-builder/renderers/FastTableRenderer'
import { FastTabRenderer } from '@/components/mask-builder/renderers/FastTabRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { RenderTablePlan } from '@/components/mask-builder/render-plan/types'

const table: RenderTablePlan = {
  key: 'queue',
  label: 'MDE-Ereignisse',
  columns: [
    { key: 'sync_status', label: 'Status', renderKind: 'status' },
    { key: 'device_id', label: 'Geraet' },
  ],
  pageSize: 25,
  virtualized: true,
  rowHeight: 44,
  serverPagination: true,
  tableProfile: 'audit',
  rowActions: [
    {
      key: 'retry_event',
      label: 'Wiederholen',
      dangerLevel: 'moderate',
      visibleWhen: { field: 'sync_status', values: ['failed', 'quarantined'] },
    },
  ],
}

describe('FastTableRenderer row actions', () => {
  it('rendert Aktionen zentral und nur fuer passende Zeilen', () => {
    const onRowAction = vi.fn()
    render(
      <FastTableRenderer
        table={table}
        rows={[
          { id: 'evt-ok', device_id: 'MDE-1', sync_status: 'done' },
          { id: 'evt-fail', device_id: 'MDE-2', sync_status: 'failed' },
        ]}
        onRowAction={onRowAction}
      />,
    )

    const actions = screen.getAllByTestId('row-action-retry_event')
    expect(actions).toHaveLength(1)
    fireEvent.click(actions[0])
    expect(onRowAction).toHaveBeenCalledWith('retry_event', expect.objectContaining({ id: 'evt-fail' }))
  })

  it('uebergibt zentral ausgewaehlte Zeilen an eine Bulk-Aktion', async () => {
    const onRowAction = vi.fn()
    render(
      <FastTableRenderer
        table={{ ...table, rowActions: [], bulkActions: [{ key: 'release', label: 'Freigeben' }] }}
        rows={[{ id: 'lot-1', device_id: 'Charge 1', sync_status: 'ready' }]}
        onRowAction={onRowAction}
      />,
    )
    fireEvent.click(screen.getByLabelText('Zeile lot-1 auswaehlen'))
    fireEvent.click(screen.getByTestId('bulk-action-release'))
    await waitFor(() => expect(onRowAction).toHaveBeenCalledWith('release', {
        selectedIds: ['lot-1'],
        selectedRows: [expect.objectContaining({ id: 'lot-1' })],
      }))
    await waitFor(() => expect(screen.getByTestId('bulk-action-release')).toBeDisabled())
  })

  it('behaelt die Auswahl bei fehlgeschlagenen Bulk-Aktionen und leert sie beim Seitenwechsel', async () => {
    const onRowAction = vi.fn().mockRejectedValue(new Error('quality gate'))
    const props = {
      table: { ...table, rowActions: [], bulkActions: [{ key: 'release', label: 'Freigeben' }] },
      rows: [{ id: 'lot-1', device_id: 'Charge 1', sync_status: 'ready' }],
      onRowAction,
    }
    const { rerender } = render(<FastTableRenderer {...props} page={1} />)
    fireEvent.click(screen.getByLabelText('Zeile lot-1 auswaehlen'))
    fireEvent.click(screen.getByTestId('bulk-action-release'))
    await waitFor(() => expect(onRowAction).toHaveBeenCalled())
    await waitFor(() => expect(screen.getByLabelText('Zeile lot-1 auswaehlen')).toBeChecked())

    rerender(<FastTableRenderer {...props} page={2} />)
    await waitFor(() => expect(screen.getByLabelText('Zeile lot-1 auswaehlen')).not.toBeChecked())
  })

  it('navigiert aus einer Zeile ueber rowRouteTemplate', () => {
    const pushState = vi.spyOn(window.history, 'pushState')
    render(
      <FastTableRenderer
        table={{
          ...table,
          rowActions: [],
          rowRouteTemplate: '/lager/stock-movement/{movement_id}',
        }}
        rows={[{ movement_id: 'mv-9', device_id: 'MDE-9', sync_status: 'done' }]}
      />,
    )
    fireEvent.click(screen.getByText('MDE-9'))
    expect(pushState).toHaveBeenCalledWith(null, '', '/lager/stock-movement/mv-9')
    pushState.mockRestore()
  })
})

describe('FastTabRenderer row actions', () => {
  const definition: ScreenDefinition = {
    id: 'test/tab-actions',
    schemaVersion: 1,
    domain: 'lager',
    mode: 'detail',
    title: 'Artikel',
    layout: { floorplan: 'objectPage', contextRail: 'none' },
    tabs: [{
      key: 'bewegungen',
      label: 'Bewegungen',
      tables: [{
        key: 'bewegungen',
        label: 'Bewegungen',
        columns: [{ key: 'typ', label: 'Typ' }],
        rowActions: [{ key: 'open_movement', label: 'Zur Bewegung' }],
        pageSize: 25,
        virtualized: true,
        rowHeight: 44,
      }],
    }],
  }

  it('reicht Zeilenaktionen aus Registertabellen an onRowAction weiter', () => {
    const onRowAction = vi.fn()
    render(
      <FastTabRenderer
        plan={compileRenderPlanFromScreenDefinition(definition)}
        tabKey="bewegungen"
        payload={{}}
        tables={{ bewegungen: [{ id: 'mv-1', typ: 'Zugang' }] }}
        onRowAction={onRowAction}
      />,
    )
    fireEvent.click(screen.getByTestId('row-action-open_movement'))
    expect(onRowAction).toHaveBeenCalledWith('open_movement', expect.objectContaining({ id: 'mv-1' }))
  })
})
