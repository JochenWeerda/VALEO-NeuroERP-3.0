import { memo, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { VirtualDataTable } from '@/components/ui/VirtualDataTable'
import type { RenderColumnKind, RenderTablePlan } from '../render-plan/types'
import type { TableQueryState } from '../runtime/types'

interface FastTableRendererProps {
  table: RenderTablePlan
  rows: Record<string, unknown>[]
  total?: number
  page?: number
  sort?: string
  sortDir?: 'asc' | 'desc'
  onQueryChange?: (patch: Partial<TableQueryState>) => void
}

function formatCellValue(value: unknown, renderKind: RenderColumnKind | undefined): ReactNode {
  if (value == null) return '–'
  switch (renderKind) {
    case 'currency':
      return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(Number(value))
    case 'date':
      try { return new Date(String(value)).toLocaleDateString('de-DE') } catch { return String(value) }
    case 'datetime':
      try { return new Date(String(value)).toLocaleString('de-DE') } catch { return String(value) }
    case 'boolean':
      return value ? 'Ja' : 'Nein'
    case 'status':
      return (
        <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ring-border">
          {String(value)}
        </span>
      )
    default:
      return String(value)
  }
}

export const FastTableRenderer = memo(function FastTableRenderer({
  table,
  rows,
  total,
  page,
  sort,
  sortDir,
  onQueryChange,
}: FastTableRendererProps): JSX.Element {
  const isServerPaged = table.serverPagination && Boolean(onQueryChange)
  const visibleRows = isServerPaged ? rows : rows.slice(0, table.pageSize)
  const totalPages = total !== undefined ? Math.ceil(total / table.pageSize) : undefined

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{table.label}</CardTitle>
      </CardHeader>
      <CardContent>
        <VirtualDataTable
          data={visibleRows}
          rowHeight={table.rowHeight}
          sortColumn={sort}
          sortDir={sortDir}
          onSortChange={
            onQueryChange
              ? (colKey, dir) => onQueryChange({ sort: colKey, sortDir: dir })
              : undefined
          }
          columns={table.columns.map((column) => ({
            key: column.key,
            label: column.label,
            width: column.width,
            numeric: column.numeric,
            sortable: column.sortable,
            render: column.renderKind
              ? (value: unknown) => formatCellValue(value, column.renderKind)
              : undefined,
          }))}
        />
        {isServerPaged && totalPages !== undefined && totalPages > 1 ? (
          <div className="flex items-center justify-end gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!page || page <= 1}
              onClick={() => onQueryChange?.({ page: (page ?? 1) - 1 })}
            >
              Zurück
            </Button>
            <span className="text-sm text-muted-foreground">
              Seite {page ?? 1} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={(page ?? 1) >= totalPages}
              onClick={() => onQueryChange?.({ page: (page ?? 1) + 1 })}
            >
              Weiter
            </Button>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
})
