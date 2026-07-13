import { type ReactNode, useEffect, useRef, useState, useCallback } from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { Columns, BookmarkPlus, RotateCcw } from 'lucide-react'

export type ColumnRenderArgs<T> = {
  row: {
    original: T
  }
}

export type ColumnDef<T> = {
  accessorKey?: keyof T | string
  id?: string
  header: ReactNode
  cell?: (_args: ColumnRenderArgs<T>) => ReactNode
  className?: string
  numeric?: boolean
  /** If true, column is hidden by default in the visibility picker */
  defaultHidden?: boolean
}

export type LegacyColumnDef<T> = {
  key: keyof T | string
  label: string
  render?: (_item: T) => ReactNode
}

interface DataTableProps<T> {
  columns: ColumnDef<T>[] | LegacyColumnDef<T>[]
  data: T[]
  selectable?: boolean
  onSelectionChange?: (_selected: T[]) => void
  loading?: boolean
  skeletonRows?: number
  /** When true, renders a column visibility picker button above the table */
  columnVisibilityPicker?: boolean
  /** Accessible label for the empty state */
  emptyMessage?: string
  /** Stable ID used to persist column visibility and sort preferences in localStorage */
  tableId?: string
  /** Arrow-key row navigation: calls onRowFocus with the focused row item */
  onRowFocus?: (_item: T) => void
}

function SkeletonRow({ colCount }: { colCount: number }): JSX.Element {
  return (
    <TableRow className="animate-pulse">
      {Array.from({ length: colCount }).map((_, i) => (
        <TableCell key={i}>
          <div className="h-4 rounded bg-muted" style={{ width: `${60 + (i % 3) * 20}%` }} />
        </TableCell>
      ))}
    </TableRow>
  )
}

export function DataTable<T>({
  columns,
  data,
  selectable,
  onSelectionChange,
  loading = false,
  skeletonRows = 5,
  columnVisibilityPicker = false,
  emptyMessage = 'Keine Einträge vorhanden.',
  tableId,
  onRowFocus,
}: DataTableProps<T>): JSX.Element {
  useEffect(() => {
    if (selectable !== true) {
      onSelectionChange?.([])
    }
  }, [onSelectionChange, selectable])

  const isLegacyFormat = (col: ColumnDef<T> | LegacyColumnDef<T>): col is LegacyColumnDef<T> => {
    return 'key' in col && 'label' in col
  }

  const normalizedColumns: ColumnDef<T>[] = columns.map((col) => {
    if (isLegacyFormat(col)) {
      return {
        accessorKey: col.key as string,
        id: String(col.key),
        header: col.label,
        cell: col.render ? (_args: ColumnRenderArgs<T>) => col.render?.(_args.row.original) : undefined,
      }
    }
    return col
  })

  const storageKey = tableId ? `data-table-hidden-${tableId}` : null

  const [hiddenCols, setHiddenCols] = useState<Set<string>>(() => {
    if (storageKey) {
      try {
        const saved = localStorage.getItem(storageKey)
        if (saved) return new Set<string>(JSON.parse(saved) as string[])
      } catch { /* ignore */ }
    }
    const hidden = new Set<string>()
    normalizedColumns.forEach((col) => {
      if (col.defaultHidden) {
        hidden.add(String(col.id ?? col.accessorKey))
      }
    })
    return hidden
  })
  const [pickerOpen, setPickerOpen] = useState(false)
  const [focusedRowIndex, setFocusedRowIndex] = useState<number>(-1)
  const tbodyRef = useRef<HTMLTableSectionElement>(null)

  const persistHiddenCols = useCallback((next: Set<string>): void => {
    if (storageKey) {
      try {
        localStorage.setItem(storageKey, JSON.stringify([...next]))
      } catch { /* ignore */ }
    }
  }, [storageKey])

  const visibleColumns = normalizedColumns.filter(
    (col) => !hiddenCols.has(String(col.id ?? col.accessorKey)),
  )

  function toggleColumn(colKey: string): void {
    setHiddenCols((prev) => {
      const next = new Set(prev)
      if (next.has(colKey)) {
        next.delete(colKey)
      } else {
        next.add(colKey)
      }
      persistHiddenCols(next)
      return next
    })
  }

  function resetColumnVisibility(): void {
    const defaults = new Set<string>()
    normalizedColumns.forEach((col) => {
      if (col.defaultHidden) defaults.add(String(col.id ?? col.accessorKey))
    })
    setHiddenCols(defaults)
    persistHiddenCols(defaults)
  }

  function handleTableKeyDown(e: React.KeyboardEvent<HTMLTableSectionElement>): void {
    if (data.length === 0) return
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      const next = Math.min(focusedRowIndex + 1, data.length - 1)
      setFocusedRowIndex(next)
      onRowFocus?.(data[next])
      ;(tbodyRef.current?.children[next] as HTMLElement)?.focus()
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      const next = Math.max(focusedRowIndex - 1, 0)
      setFocusedRowIndex(next)
      onRowFocus?.(data[next])
      ;(tbodyRef.current?.children[next] as HTMLElement)?.focus()
    } else if (e.key === 'Home') {
      e.preventDefault()
      setFocusedRowIndex(0)
      onRowFocus?.(data[0])
      ;(tbodyRef.current?.children[0] as HTMLElement)?.focus()
    } else if (e.key === 'End') {
      e.preventDefault()
      const last = data.length - 1
      setFocusedRowIndex(last)
      onRowFocus?.(data[last])
      ;(tbodyRef.current?.children[last] as HTMLElement)?.focus()
    }
  }

  return (
    <div className="space-y-2">
      {columnVisibilityPicker && (
        <div className="relative flex justify-end gap-1">
          {tableId && (
            <Button
              variant="ghost"
              size="sm"
              className="gap-1.5 text-xs text-muted-foreground"
              onClick={resetColumnVisibility}
              title="Spalten zurücksetzen"
              aria-label="Spaltenauswahl zurücksetzen"
            >
              <RotateCcw className="h-3.5 w-3.5" aria-hidden="true" />
            </Button>
          )}
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 text-xs"
            onClick={() => setPickerOpen((o) => !o)}
            aria-expanded={pickerOpen}
            aria-haspopup="listbox"
          >
            <Columns className="h-3.5 w-3.5" aria-hidden="true" />
            Spalten
          </Button>
          {pickerOpen && (
            <div
              role="listbox"
              aria-label="Spalten ein-/ausblenden"
              aria-multiselectable="true"
              className="absolute right-0 top-full z-20 mt-1 min-w-[180px] rounded-md border bg-popover p-2 shadow-lg"
            >
              {normalizedColumns.map((col) => {
                const colKey = String(col.id ?? col.accessorKey)
                const isVisible = !hiddenCols.has(colKey)
                return (
                  <label
                    key={colKey}
                    className="flex cursor-pointer items-center gap-2 rounded px-2 py-1 text-sm hover:bg-muted"
                    role="option"
                    aria-selected={isVisible}
                  >
                    <input
                      type="checkbox"
                      checked={isVisible}
                      onChange={() => toggleColumn(colKey)}
                      className="h-3.5 w-3.5"
                    />
                    {typeof col.header === 'string' ? col.header : colKey}
                  </label>
                )
              })}
            </div>
          )}
        </div>
      )}

      <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            {visibleColumns.map((column) => (
              <TableHead
                key={String(column.id ?? column.accessorKey)}
                className={column.numeric ? `text-right ${column.className ?? ''}` : column.className}
              >
                {column.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody ref={tbodyRef} onKeyDown={handleTableKeyDown} role="rowgroup">
          {loading ? (
            Array.from({ length: skeletonRows }).map((_, i) => (
              <SkeletonRow key={i} colCount={visibleColumns.length} />
            ))
          ) : data.length === 0 ? (
            <TableRow>
              <TableCell colSpan={visibleColumns.length} className="py-8 text-center text-muted-foreground">
                {emptyMessage}
              </TableCell>
            </TableRow>
          ) : (
            data.map((row, rowIndex) => (
              <TableRow
                key={rowIndex}
                tabIndex={0}
                aria-selected={focusedRowIndex === rowIndex}
                onFocus={() => { setFocusedRowIndex(rowIndex); onRowFocus?.(row) }}
                className={focusedRowIndex === rowIndex ? 'outline-solid outline-2 outline-primary/50' : undefined}
              >
                {visibleColumns.map((column, columnIndex) => {
                  const cellContent =
                    typeof column.cell === 'function'
                      ? column.cell({ row: { original: row } })
                      : (column.accessorKey ? (row as Record<string, unknown>)[column.accessorKey as string] : null)
                  return (
                    <TableCell
                      key={String(column.id ?? column.accessorKey ?? columnIndex)}
                      className={column.numeric ? `text-right tabular-nums ${column.className ?? ''}` : column.className}
                    >
                      {cellContent as ReactNode}
                    </TableCell>
                  )
                })}
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      </div>
    </div>
  )
}
