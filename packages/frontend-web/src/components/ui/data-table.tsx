import { type ReactNode, useEffect } from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

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
}

export function DataTable<T>({ columns, data, selectable, onSelectionChange, loading = false }: DataTableProps<T>): JSX.Element {
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

  return (
    <Table>
      <TableHeader>
        <TableRow>
          {normalizedColumns.map((column) => (
            <TableHead key={String(column.id ?? column.accessorKey)} className={column.className}>
              {column.header}
            </TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {loading ? (
          <TableRow>
            <TableCell colSpan={normalizedColumns.length} className="text-center text-muted-foreground">
              Laden...
            </TableCell>
          </TableRow>
        ) : data.map((row, rowIndex) => (
          <TableRow key={rowIndex}>
            {normalizedColumns.map((column, columnIndex) => {
              const cellContent =
                typeof column.cell === 'function'
                  ? column.cell({ row: { original: row } })
                  : (column.accessorKey ? (row as Record<string, unknown>)[column.accessorKey as string] : null)
              return (
                <TableCell key={String(column.id ?? column.accessorKey ?? columnIndex)} className={column.className}>
                  {cellContent as ReactNode}
                </TableCell>
              )
            })}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
