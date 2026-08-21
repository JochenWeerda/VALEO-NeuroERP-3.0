import { useMemo, useRef, type ReactNode } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import { cn } from '@/lib/utils'

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
  loading?: boolean
  emptyMessage?: string
  onRowClick?: (_row: T) => void
  sortColumn?: string
  sortDir?: 'asc' | 'desc'
  onSortChange?: (_columnKey: string, _dir: 'asc' | 'desc') => void
}

export function VirtualDataTable<T extends Record<string, unknown>>({
  columns,
  data,
  rowHeight = 52,
  height = 420,
  loading = false,
  emptyMessage = 'Keine Eintraege vorhanden.',
  onRowClick,
  sortColumn,
  sortDir,
  onSortChange,
}: VirtualDataTableProps<T>): JSX.Element {
  const parentRef = useRef<HTMLDivElement>(null)
  const virtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => rowHeight,
    overscan: 8,
  })

  const gridTemplateColumns = useMemo(
    () => columns.map((column) => `${column.width ?? 160}px`).join(' '),
    [columns],
  )
  const virtualItems = virtualizer.getVirtualItems()
  const fallbackItems = useMemo(() => {
    const visibleCount = Math.max(1, Math.ceil(height / rowHeight) + 8)
    return data.slice(0, visibleCount).map((_, index) => ({
      key: `fallback-${index}`,
      index,
      start: index * rowHeight,
      size: rowHeight,
    }))
  }, [data, height, rowHeight])
  const renderedItems = virtualItems.length > 0 ? virtualItems : fallbackItems

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
      <div className="flex items-center justify-center rounded-md border border-border p-8 text-sm text-muted-foreground" style={{ height }}>
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className="rounded-md border border-border" data-testid="virtual-data-table">
      <div className="overflow-x-auto">
        <div className="min-w-full" style={{ width: 'max-content' }}>
          <div
            className="grid border-b bg-muted text-[11px] font-semibold uppercase tracking-normal text-muted-foreground"
            style={{ gridTemplateColumns }}
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
          <div ref={parentRef} className="relative overflow-auto" style={{ height }}>
            <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
              {renderedItems.map((virtualRow) => {
                const row = data[virtualRow.index]
                return (
                  <div
                    key={virtualRow.key}
                    className="absolute left-0 grid w-full border-b bg-background text-left text-sm hover:bg-primary/5 focus:outline-hidden focus:ring-2 focus:ring-primary/40"
                    style={{
                      gridTemplateColumns,
                      height: virtualRow.size,
                      transform: `translateY(${virtualRow.start}px)`,
                    }}
                    onClick={() => onRowClick?.(row)}
                    role={onRowClick ? 'button' : 'row'}
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
