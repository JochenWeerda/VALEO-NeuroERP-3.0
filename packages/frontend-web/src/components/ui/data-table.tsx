import { type ReactNode, useEffect } from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

export type ColumnRenderArgs<T> = {
  row: {
    original: T
  }
}

export type ColumnDef<T> = {
  accessorKey: keyof T | string
  header: ReactNode
  cell?: (args: ColumnRenderArgs<T>) => ReactNode
  className?: string
}

export type LegacyColumnDef<T> = {
  key: keyof T | string
  label: string
  render?: (item: T) => ReactNode
}

interface DataTableProps<T> {
  columns: ColumnDef<T>[] | LegacyColumnDef<T>[]
  data: T[]
  selectable?: boolean
  onSelectionChange?: (selected: T[]) => void
}

export function DataTable<T>({ columns, data, selectable, onSelectionChange }: DataTableProps<T>): JSX.Element {
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
        header: col.label,
        cell: col.render ? (args: ColumnRenderArgs<T>) => col.render?.(args.row.original) : undefined,
      }
    }
    return col
  })

  return (
    <Table>
      <TableHeader>
        <TableRow>
          {normalizedColumns.map((column) => (
            <TableHead key={String(column.accessorKey)} className={column.className}>
              {column.header}
            </TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((row, rowIndex) => (
          <TableRow key={rowIndex}>
            {normalizedColumns.map((column) => {
              const cellContent =
                typeof column.cell === 'function'
                  ? column.cell({ row: { original: row } })
                  : (row as Record<string, unknown>)[column.accessorKey as string]
              return (
                <TableCell key={String(column.accessorKey)} className={column.className}>
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
