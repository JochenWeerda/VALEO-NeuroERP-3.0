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

interface DataTableProps<T> {
  columns: ColumnDef<T>[]
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

  return (
    <Table>
      <TableHeader>
        <TableRow>
          {columns.map((column) => (
            <TableHead key={String(column.accessorKey)} className={column.className}>
              {column.header}
            </TableHead>
          ))}
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((row, rowIndex) => (
          <TableRow key={rowIndex}>
            {columns.map((column) => {
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
