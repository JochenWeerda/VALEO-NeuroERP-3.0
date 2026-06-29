import { memo, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { VirtualDataTable } from '@/components/ui/VirtualDataTable'
import type { RenderColumnKind, RenderTablePlan } from '../render-plan/types'
import type { FilterPlan, TableQueryState } from '../runtime/types'

interface FastTableRendererProps {
  table: RenderTablePlan
  rows: Record<string, unknown>[]
  total?: number
  page?: number
  sort?: string
  sortDir?: 'asc' | 'desc'
  q?: string
  filterPlan?: FilterPlan
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

function FilterChips({
  filterPlan,
  columns,
  onRemove,
}: {
  filterPlan: FilterPlan
  columns: RenderTablePlan['columns']
  onRemove: (colKey: string) => void
}): JSX.Element | null {
  const entries = Object.entries(filterPlan)
  if (entries.length === 0) return null
  return (
    <div
      className="flex flex-wrap gap-1 pb-2"
      role="list"
      aria-label="Aktive Filter"
      data-testid="filter-chips"
    >
      {entries.map(([colKey, spec]) => {
        const col = columns.find((c) => c.key === colKey)
        const colLabel = col?.label ?? colKey
        const label = spec.label ?? String(spec.value)
        return (
          <span
            key={colKey}
            role="listitem"
            className="inline-flex items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
            data-filter-key={colKey}
            data-filter-op={spec.op}
          >
            <span className="font-medium">{colLabel}:</span>
            <span>{label}</span>
            <button
              type="button"
              aria-label={`Filter ${colLabel} entfernen`}
              className="ml-0.5 rounded-full hover:text-foreground focus:outline-none focus:ring-1"
              onClick={() => onRemove(colKey)}
            >
              ×
            </button>
          </span>
        )
      })}
    </div>
  )
}

export const FastTableRenderer = memo(function FastTableRenderer({
  table,
  rows,
  total,
  page,
  sort,
  sortDir,
  q,
  filterPlan,
  onQueryChange,
}: FastTableRendererProps): JSX.Element {
  const isServerPaged = table.serverPagination && Boolean(onQueryChange)
  const visibleRows = isServerPaged ? rows : rows.slice(0, table.pageSize)
  const totalPages = total !== undefined ? Math.ceil(total / table.pageSize) : undefined
  const activeFilterPlan = filterPlan && Object.keys(filterPlan).length > 0 ? filterPlan : undefined

  function handleRemoveFilter(colKey: string) {
    if (!onQueryChange || !filterPlan) return
    const next = { ...filterPlan }
    delete next[colKey]
    onQueryChange({ filterPlan: Object.keys(next).length > 0 ? next : undefined, page: 1 })
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="text-base">{table.label}</CardTitle>
          {onQueryChange && (
            <input
              type="search"
              placeholder="Suchen…"
              value={q ?? ''}
              onChange={(e) => onQueryChange({ q: e.target.value || undefined, page: 1 })}
              className="h-7 w-40 rounded border border-input bg-background px-2 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
              aria-label={`Suche in ${table.label}`}
              data-testid={`search-${table.key}`}
            />
          )}
        </div>
      </CardHeader>
      <CardContent>
        {activeFilterPlan && (
          <FilterChips
            filterPlan={activeFilterPlan}
            columns={table.columns}
            onRemove={handleRemoveFilter}
          />
        )}
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
