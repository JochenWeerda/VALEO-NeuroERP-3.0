import { memo, useState, type ReactNode } from 'react'
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

function isProfileNumeric(table: RenderTablePlan, column: RenderTablePlan['columns'][number]): boolean {
  if (column.numeric || column.renderKind === 'currency' || column.renderKind === 'number') return true
  if (table.tableProfile === 'financial') return /betrag|saldo|soll|haben|steuer|skonto|summe|differenz|amount|debit|credit/i.test(column.key)
  if (table.tableProfile === 'inventory') return /menge|bestand|reserv|verfueg|block|quantity|qty|stock|unit/i.test(column.key)
  return false
}

function profileLabel(profile: RenderTablePlan['tableProfile']): string {
  if (profile === 'financial') return 'Financial Table Profile'
  if (profile === 'inventory') return 'Inventory Table Profile'
  if (profile === 'audit') return 'Audit Table Profile'
  return 'Standard Table Profile'
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
  const filterableColumns = table.columns.filter((column) => column.filterable)
  const [filterColumn, setFilterColumn] = useState<string>(filterableColumns[0]?.key ?? '')
  const [filterValue, setFilterValue] = useState('')

  function handleRemoveFilter(colKey: string) {
    if (!onQueryChange || !filterPlan) return
    const next = { ...filterPlan }
    delete next[colKey]
    onQueryChange({ filterPlan: Object.keys(next).length > 0 ? next : undefined, page: 1 })
  }

  function handleApplyFilter() {
    const value = filterValue.trim()
    if (!onQueryChange || !filterColumn || !value) return
    onQueryChange({
      filterPlan: {
        ...(filterPlan ?? {}),
        [filterColumn]: { op: 'contains', value, label: value },
      },
      page: 1,
    })
  }

  return (
    <Card data-table-profile={table.tableProfile} data-testid={`table-${table.key}`}>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <CardTitle className="text-base">{table.label}</CardTitle>
            <p className="mt-0.5 text-[11px] uppercase tracking-normal text-muted-foreground">
              {profileLabel(table.tableProfile)}
            </p>
          </div>
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
        {onQueryChange && filterableColumns.length > 0 ? (
          <div className="flex flex-wrap items-center gap-2 pt-2">
            <select
              value={filterColumn}
              onChange={(event) => setFilterColumn(event.target.value)}
              className="h-7 rounded border border-input bg-background px-2 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
              aria-label={`Filterspalte fuer ${table.label}`}
              data-testid={`filter-column-${table.key}`}
            >
              {filterableColumns.map((column) => (
                <option key={column.key} value={column.key}>
                  {column.label}
                </option>
              ))}
            </select>
            <input
              type="text"
              value={filterValue}
              onChange={(event) => setFilterValue(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') handleApplyFilter()
              }}
              placeholder="Filterwert"
              className="h-7 w-40 rounded border border-input bg-background px-2 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
              aria-label={`Filterwert fuer ${table.label}`}
              data-testid={`filter-value-${table.key}`}
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-7 px-2 text-xs"
              onClick={handleApplyFilter}
              disabled={!filterColumn || filterValue.trim().length === 0}
              data-testid={`apply-filter-${table.key}`}
            >
              Filtern
            </Button>
          </div>
        ) : null}
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
            numeric: isProfileNumeric(table, column),
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
