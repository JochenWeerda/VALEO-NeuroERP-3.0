import { useMemo, useRef, type ReactNode } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import { cn } from '@/lib/utils'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { TouchRecordCard } from '@/components/list/TouchRecordStack'

export interface VirtualDataTableColumn<T extends Record<string, unknown>> {
  key: keyof T | string
  label: string
  width?: number
  numeric?: boolean
  sortable?: boolean
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  render?: (_value: any, _row: T) => ReactNode
}

interface VirtualDataTableProps<T extends Record<string, unknown>> {
  columns: VirtualDataTableColumn<T>[]
  data: T[]
  rowHeight?: number
  height?: number
  /** Shrinks the body to the rows it holds; `height` stays the upper bound. */
  fitToContent?: boolean
  loading?: boolean
  emptyMessage?: string
  onRowClick?: (_row: T) => void
  selectedRowKey?: string
  getRowKey?: (_row: T, _index: number) => string
  sortColumn?: string
  sortDir?: 'asc' | 'desc'
  onSortChange?: (_columnKey: string, _dir: 'asc' | 'desc') => void
}

export function VirtualDataTable<T extends Record<string, unknown>>({
  columns,
  data,
  rowHeight = 52,
  height = 420,
  fitToContent = false,
  loading = false,
  emptyMessage = 'Keine Eintraege vorhanden.',
  onRowClick,
  selectedRowKey,
  getRowKey,
  sortColumn,
  sortDir,
  onSortChange,
}: VirtualDataTableProps<T>): JSX.Element {
  const isTouch = useTouchDevice()
  const estimatedRowSize = isTouch ? 160 : rowHeight
  const parentRef = useRef<HTMLDivElement>(null)
  const virtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => estimatedRowSize,
    overscan: 8,
  })

  const gridTemplateColumns = useMemo(
    () => columns.map((column) => `${column.width ?? 160}px`).join(' '),
    [columns],
  )
  const virtualItems = virtualizer.getVirtualItems()
  const fallbackItems = useMemo(() => {
    const visibleCount = Math.max(1, Math.ceil(height / estimatedRowSize) + 8)
    return data.slice(0, visibleCount).map((_, index) => ({
      key: `fallback-${index}`,
      index,
      start: index * estimatedRowSize,
      size: estimatedRowSize,
    }))
  }, [data, height, estimatedRowSize])
  const renderedItems = virtualItems.length > 0 ? virtualItems : fallbackItems
  // The touch list pads its scroll container with p-2 (8 px top and bottom).
  const contentHeight = virtualItems.length > 0 ? virtualizer.getTotalSize() : data.length * estimatedRowSize
  const bodyHeight = fitToContent
    ? Math.min(height, contentHeight + (isTouch ? 16 : 0))
    : height
  const emptyHeight = fitToContent ? Math.min(height, 96) : height

  function renderCell(column: VirtualDataTableColumn<T>, row: T): ReactNode {
    const value = row[column.key as string]
    if (column.render) return column.render(value, row)
    if (value == null) return '-'
    if (typeof value === 'boolean') return value ? 'Ja' : 'Nein'
    return String(value)
  }

  if (loading) {
    return (
      <div className="rounded-md border border-border p-4" style={{ height }}>
        <div className="space-y-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="h-9 animate-pulse rounded bg-muted" />
          ))}
        </div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center rounded-md border border-border p-8 text-sm text-muted-foreground" style={{ height: emptyHeight }}>
        {emptyMessage}
      </div>
    )
  }

  const dataColumns = columns.filter((column) => {
    const key = String(column.key)
    return key !== '__selected' && key !== '__actions'
  })
  const selectColumn = columns.find((column) => String(column.key) === '__selected')
  const actionColumn = columns.find((column) => String(column.key) === '__actions')
  const titleColumn = dataColumns[0]
  const fieldColumns = dataColumns.slice(1, 6)

  if (isTouch) {
    return (
      <div className="rounded-md border border-border" data-testid="virtual-data-table">
        <div ref={parentRef} className="relative overflow-auto p-2" style={{ height: bodyHeight }}>
          <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
            {renderedItems.map((virtualRow) => {
              const row = data[virtualRow.index]
              const rowKey = getRowKey?.(row, virtualRow.index) ?? String(row.id ?? virtualRow.index)
              const selected = Boolean(selectedRowKey) && rowKey === selectedRowKey
              return (
                // Cards grow with their field count, so each one is measured instead of assuming the estimate.
                <div
                  key={virtualRow.key}
                  ref={virtualizer.measureElement}
                  data-index={virtualRow.index}
                  className="absolute left-0 w-full px-0 pb-2"
                  style={{ transform: `translateY(${virtualRow.start}px)` }}
                >
                  <TouchRecordCard
                    selected={selected}
                    onOpen={onRowClick ? () => onRowClick(row) : undefined}
                    title={
                      <span className="flex items-center gap-2">
                        {selectColumn ? renderCell(selectColumn, row) : null}
                        {titleColumn ? renderCell(titleColumn, row) : rowKey}
                      </span>
                    }
                    fields={fieldColumns.map((column) => ({
                      key: String(column.key),
                      label: column.label,
                      value: renderCell(column, row),
                    }))}
                    actionSlot={actionColumn ? renderCell(actionColumn, row) : undefined}
                  />
                </div>
              )
            })}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="rounded-md border border-border" data-testid="virtual-data-table">
      <div className="overflow-x-auto">
        <div className="min-w-full" style={{ width: 'max-content' }}>
          {/* Header and body reserve the same scrollbar gutter: columns stay aligned and the
              body's vertical scrollbar cannot push the rows into a second horizontal scrollbar. */}
          <div
            className="grid overflow-y-hidden border-b bg-muted text-[11px] font-semibold uppercase tracking-normal text-muted-foreground"
            style={{ gridTemplateColumns, scrollbarGutter: 'stable' }}
          >
            {columns.map((column) => {
              const colKey = String(column.key)
              const isActive = sortColumn === colKey
              const canSort = column.sortable && Boolean(onSortChange)
              return (
                <div
                  key={colKey}
                  className={cn(
                    'px-3 py-3',
                    column.numeric && 'text-right',
                    canSort && 'cursor-pointer select-none hover:text-foreground',
                  )}
                  onClick={
                    canSort
                      ? () => onSortChange?.(colKey, isActive && sortDir === 'asc' ? 'desc' : 'asc')
                      : undefined
                  }
                >
                  {column.label}
                  {canSort && isActive ? (
                    <span className="ml-1">{sortDir === 'asc' ? '↑' : '↓'}</span>
                  ) : canSort ? (
                    <span className="ml-1 opacity-30">⇅</span>
                  ) : null}
                </div>
              )
            })}
          </div>
          <div
            ref={parentRef}
            className="relative overflow-y-auto overflow-x-hidden"
            style={{ height: bodyHeight, scrollbarGutter: 'stable' }}
          >
            <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
              {renderedItems.map((virtualRow) => {
                const row = data[virtualRow.index]
                const rowKey = getRowKey?.(row, virtualRow.index) ?? String(row.id ?? virtualRow.index)
                const selected = Boolean(selectedRowKey) && rowKey === selectedRowKey
                return (
                  <div
                    key={virtualRow.key}
                    className={cn(
                      'absolute left-0 grid w-full border-b bg-background text-left text-sm hover:bg-primary/5 focus:outline-hidden focus:ring-2 focus:ring-primary/40',
                      selected && 'bg-muted',
                    )}
                    style={{
                      gridTemplateColumns,
                      height: virtualRow.size,
                      transform: `translateY(${virtualRow.start}px)`,
                    }}
                    onClick={() => onRowClick?.(row)}
                    role={onRowClick ? 'button' : 'row'}
                    aria-selected={selected || undefined}
                    data-selected={selected || undefined}
                    tabIndex={onRowClick ? 0 : undefined}
                    onKeyDown={onRowClick ? (event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault()
                        onRowClick(row)
                      }
                    } : undefined}
                  >
                    {columns.map((column) => (
                      <span
                        key={String(column.key)}
                        className={cn('truncate px-3 py-3', column.numeric && 'text-right tabular-nums')}
                      >
                        {renderCell(column, row)}
                      </span>
                    ))}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
