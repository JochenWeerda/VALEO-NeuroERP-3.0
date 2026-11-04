import { memo, useEffect, useRef, useState, type ReactNode } from 'react'
import { Columns3, RotateCcw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { NativeSelect } from '@/components/ui/native-select'
import { VirtualDataTable } from '@/components/ui/VirtualDataTable'
import type { RenderColumnKind, RenderTablePlan } from '../render-plan/types'
import type { FilterPlan, TableQueryState } from '../runtime/types'
import { navigateRowRoute, rowIdentity } from './row-identity'
import { columnsForWidth } from './column-priority'
import { evaluateCondition, matchesValueList } from '../governance/condition-engine'
import { statusLabel } from './status-labels'
import { formatBusinessDate, formatBusinessDateTime } from '@/lib/business-time'
import { computeValue, sumColumn } from '../runtime/computed-fields'
import { convertQuantity, convertUnitPrice, sumQuantities } from '../runtime/units'

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
  onVisibleColumnsChange?: (visibleColumns: string[]) => void | Promise<void>
  onResetOverlay?: () => void | Promise<void>
  onRowAction?: (_actionKey: string, _row: Record<string, unknown>) => void | Promise<void>
  errorMessage?: string
  onRetry?: () => void
  selectedRowKey?: string
  onRowSelect?: (_row: Record<string, unknown>) => void
  /** Die Seitenüberschrift trägt den Namen schon. Keine zweite Überschrift darüber. */
  suppressHeading?: boolean
}

export function formatCellValue(value: unknown, renderKind: RenderColumnKind | undefined, currency = 'EUR', unit?: string): ReactNode {
  if (value == null) return '–'
  switch (renderKind) {
    case 'quantity': {
      const menge = Number(value)
      return Number.isFinite(menge) ? `${new Intl.NumberFormat('de-DE').format(menge)}${unit ? ` ${unit}` : ''}` : String(value)
    }
    case 'percentage': {
      const anteil = Number(value)
      return Number.isFinite(anteil) ? `${new Intl.NumberFormat('de-DE', { maximumFractionDigits: 2 }).format(anteil)} %` : String(value)
    }
    case 'number': {
      const zahl = Number(value)
      return Number.isFinite(zahl) ? new Intl.NumberFormat('de-DE').format(zahl) : String(value)
    }
    case 'currency':
      return /^[A-Z]{3}$/.test(currency) ? new Intl.NumberFormat('de-DE', { style: 'currency', currency }).format(Number(value)) : 'Währung fehlt'
    case 'date':
    case 'datetime': {
      // Geschaeftstag: ein Kalendertag wird nie als UTC-Zeitpunkt gelesen, Zeitpunkte in der Betriebszeitzone.
      const raw = String(value).trim()
      if (!raw) return '–'
      return (renderKind === 'date' ? formatBusinessDate(raw) : formatBusinessDateTime(raw)) ?? '–'
    }
    case 'boolean':
      return value ? 'Ja' : 'Nein'
    case 'status':
      return (
        <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ring-border">
          {statusLabel(String(value))}
        </span>
      )
    default:
      return String(value)
  }
}

/** Wert einer Zelle; eine rechnende Spalte rechnet aus derselben Zeile (Vorschau, der Server bleibt massgeblich). */
function cellValue(column: RenderTablePlan['columns'][number], row: Record<string, unknown>, value: unknown): unknown {
  return column.computed ? computeValue(column.computed, (key) => row[key]) : value
}

function columnUnit(column: RenderTablePlan['columns'][number], row: Record<string, unknown>): string | undefined {
  return column.unitField ? String(row[column.unitField] ?? '') || column.unit : column.unit
}

/** Menge in der Anzeigeeinheit; nicht umrechenbar (Zaehleinheit) bleibt sie in ihrer eigenen Einheit stehen. */
function displayQuantity(column: RenderTablePlan['columns'][number], row: Record<string, unknown>, value: unknown): [unknown, string | undefined] {
  const einheit = columnUnit(column, row)
  if (column.renderKind === 'currency' && column.pricePer && column.displayPricePer && value != null && value !== '') {
    const preis = convertUnitPrice(Number(value), column.pricePer, column.displayPricePer)
    return [preis === null ? value : Math.round((preis + Number.EPSILON) * 100) / 100, einheit]
  }
  if (column.renderKind !== 'quantity' || !column.displayUnit || value == null || value === '') return [value, einheit]
  const umgerechnet = convertQuantity(Number(value), einheit, column.displayUnit)
  return umgerechnet === null ? [value, einheit] : [umgerechnet, column.displayUnit]
}

/** Summenzeile einer Mengenspalte: gemischte Masse/Volumen umgerechnet (Masse in dt), sonst keine Summe. */
function quantityTotal(column: RenderTablePlan['columns'][number], rows: Record<string, unknown>[]): ReactNode {
  const summe = sumQuantities(rows.map((row) => {
    const roh = cellValue(column, row, row[column.key])
    const zahl = roh == null || roh === '' ? null : Number(roh)
    return { wert: zahl !== null && Number.isFinite(zahl) ? zahl : null, einheit: columnUnit(column, row) }
  }), column.displayUnit)
  return summe ? formatCellValue(summe.wert, 'quantity', 'EUR', summe.einheit || undefined) : 'Einheiten nicht umrechenbar'
}

/** Einheit/Waehrung der Summenzeile nur, wenn alle Zeilen dieselbe tragen; sonst keine (gemischte Summe). */
function einheitlich(rows: Record<string, unknown>[], key: string): string | undefined {
  const werte = new Set(rows.map((row) => String(row[key] ?? '')))
  return werte.size === 1 ? [...werte][0] || undefined : undefined
}

function isProfileNumeric(table: RenderTablePlan, column: RenderTablePlan['columns'][number]): boolean {
  if (column.numeric || column.computed || ['currency', 'number', 'quantity', 'percentage'].includes(column.renderKind ?? '')) return true
  if (table.tableProfile === 'financial') return /betrag|saldo|soll|haben|steuer|skonto|summe|differenz|amount|debit|credit/i.test(column.key)
  if (table.tableProfile === 'inventory') return /menge|bestand|reserv|verfueg|block|quantity|qty|stock|unit/i.test(column.key)
  return false
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
              className="ml-0.5 rounded-full hover:text-foreground focus:outline-hidden focus:ring-1"
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
  onVisibleColumnsChange,
  onResetOverlay,
  onRowAction,
  errorMessage,
  onRetry,
  selectedRowKey,
  onRowSelect,
  suppressHeading = false,
}: FastTableRendererProps): JSX.Element {
  // Blaettern am Server oder, ohne Serverblaetterung, in der Laufzeit (die dann `total` liefert und die Seite schneidet).
  const isServerPaged = Boolean(onQueryChange) && (table.serverPagination || total !== undefined)
  const visibleRows = isServerPaged ? rows : rows.slice(0, table.pageSize)
  const totalPages = total !== undefined ? Math.ceil(total / table.pageSize) : undefined
  const activeFilterPlan = filterPlan && Object.keys(filterPlan).length > 0 ? filterPlan : undefined
  const filterableColumns = table.columns.filter((column) => column.filterable)
  const [filterColumn, setFilterColumn] = useState<string>(filterableColumns[0]?.key ?? '')
  const [filterValue, setFilterValue] = useState('')
  const [columnPickerOpen, setColumnPickerOpen] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [bulkActionPending, setBulkActionPending] = useState<string | null>(null)
  useEffect(() => {
    setSelectedIds(new Set())
  }, [page, sort, sortDir, q, filterPlan])
  useEffect(() => {
    const visibleIds = new Set(rows.flatMap((row) => row.id == null ? [] : [String(row.id)]))
    setSelectedIds((current) => {
      const next = new Set([...current].filter((id) => visibleIds.has(id)))
      return next.size === current.size ? current : next
    })
  }, [rows])
  const frameRef = useRef<HTMLDivElement>(null)
  const [frameWidth, setFrameWidth] = useState(1280)
  useEffect(() => {
    const node = frameRef.current
    if (!node || typeof ResizeObserver === 'undefined') return undefined
    const observer = new ResizeObserver((entries) => {
      const next = entries[0]?.contentRect.width
      if (typeof next === 'number') setFrameWidth(next)
    })
    observer.observe(node)
    return () => observer.disconnect()
  }, [])
  const priorityColumns = columnsForWidth(table.columns, frameWidth)
  const availableColumns = table.availableColumns ?? table.columns
  const visibleColumnKeys = new Set(priorityColumns.map((column) => column.key))
  const dataColumns = priorityColumns.map((column) => ({
    key: column.key,
    label: column.label,
    width: column.width,
    numeric: isProfileNumeric(table, column),
    sortable: column.sortable,
    render: column.renderKind || column.computed
      ? (value: unknown, row: Record<string, unknown>) => {
        const [wert, einheit] = displayQuantity(column, row, cellValue(column, row, value))
        return formatCellValue(wert, column.renderKind ?? 'number',
          column.currencyField ? String(row[column.currencyField] ?? '') : 'EUR', einheit)
      }
      : undefined,
  }))
  const summen = priorityColumns.filter((column) => column.aggregate === 'sum')
  const selectableColumns = table.bulkActions?.length && onRowAction
    ? [{
        key: '__selected',
        label: '',
        width: 44,
        sortable: false,
        render: (_value: unknown, row: Record<string, unknown>) => {
          const id = String(row.id ?? '')
          const selectable = row.id != null && id.length > 0
          return (
            <input
              type="checkbox"
              aria-label={`Zeile ${id} auswaehlen`}
              checked={selectedIds.has(id)}
              disabled={!selectable}
              onChange={(event) => {
                event.stopPropagation()
                setSelectedIds((current) => {
                  const next = new Set(current)
                  if (event.target.checked) next.add(id)
                  else next.delete(id)
                  return next
                })
              }}
              onClick={(event) => event.stopPropagation()}
            />
          )
        },
      }, ...dataColumns]
    : dataColumns
  const renderedColumns = table.rowActions?.length && onRowAction
    ? [
        ...selectableColumns,
        {
          key: '__actions',
          label: 'Aktionen',
          width: 170,
          sortable: false,
          render: (_value: unknown, row: Record<string, unknown>) => (
            <span className="flex gap-1">
              {table.rowActions?.filter((action) => matchesValueList(row, action.visibleWhen)).map((action) => (
                <Button
                  key={action.key}
                  type="button"
                  variant={['high', 'critical', 'destructive'].includes(action.dangerLevel ?? '') ? 'destructive' : 'outline'}
                  className="min-h-touch px-2 text-xs"
                  data-testid={`row-action-${action.key}`}
                  disabled={Boolean(action.disabledWhen && matchesValueList(row, action.disabledWhen)) || Boolean(action.enabledWhen && !evaluateCondition(action.enabledWhen, row))}
                  onClick={(event) => {
                    event.stopPropagation()
                    void onRowAction(action.key, row)
                  }}
                >
                  {action.label}
                </Button>
              ))}
            </span>
          ),
        },
      ]
    : selectableColumns

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

  function handleToggleColumn(columnKey: string): void {
    if (!onVisibleColumnsChange) return
    const next = new Set(visibleColumnKeys)
    if (next.has(columnKey)) {
      if (next.size <= 1) return
      next.delete(columnKey)
    } else {
      next.add(columnKey)
    }
    const ordered = availableColumns.map((column) => column.key).filter((key) => next.has(key))
    void onVisibleColumnsChange(ordered)
  }

  return (
    <div ref={frameRef}>
    <Card data-table-profile={table.tableProfile} data-testid={`table-${table.key}`}>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-2">
          {suppressHeading ? null : <CardTitle className="text-base">{table.label}</CardTitle>}
          {table.bulkActions?.length && onRowAction ? (
            <div className="flex items-center gap-1" data-testid={`bulk-actions-${table.key}`}>
              <span className="mr-1 text-xs text-muted-foreground">{selectedIds.size} gewaehlt</span>
              {table.bulkActions.map((action) => (
                <Button
                  key={action.key}
                  type="button"
                  variant={['high', 'critical', 'destructive'].includes(action.dangerLevel ?? '') ? 'destructive' : 'outline'}
                  disabled={selectedIds.size === 0 || bulkActionPending !== null}
                  data-testid={`bulk-action-${action.key}`}
                  onClick={async () => {
                    const selectedRows = rows.filter((row) => selectedIds.has(String(row.id ?? '')))
                    setBulkActionPending(action.key)
                    try {
                      await onRowAction(action.key, { selectedIds: [...selectedIds], selectedRows })
                      setSelectedIds(new Set())
                    } catch {
                      // The action runtime owns user-facing error reporting; retain selection for retry.
                    } finally {
                      setBulkActionPending(null)
                    }
                  }}
                 className="min-h-touch">
                  {action.label}
                </Button>
              ))}
            </div>
          ) : null}
          {onQueryChange && (
            <input
              type="search"
              placeholder="Suchen…"
              value={q ?? ''}
              onChange={(e) => onQueryChange({ q: e.target.value || undefined, page: 1 })}
              className="min-h-touch w-40 rounded border border-input bg-background px-2 text-sm focus:outline-hidden focus:ring-1 focus:ring-ring"
              aria-label={`Suche in ${table.label}`}
              data-testid={`search-${table.key}`}
            />
          )}
          {(onVisibleColumnsChange || onResetOverlay) && (
            <div className="flex items-center gap-1">
              {onVisibleColumnsChange && (
                <Button
                  type="button"
                  variant="outline"
                  className="min-h-touch px-2 text-xs"
                  onClick={() => setColumnPickerOpen((open) => !open)}
                  aria-expanded={columnPickerOpen}
                  aria-controls={`column-picker-${table.key}`}
                  data-testid={`column-picker-toggle-${table.key}`}
                >
                  <Columns3 className="mr-1 h-3.5 w-3.5" />
                  Spalten
                </Button>
              )}
              {onResetOverlay && (
                <Button
                  type="button"
                  variant="outline"
                  className="min-h-touch px-2 text-xs"
                  onClick={() => { void onResetOverlay() }}
                  data-testid={`reset-overlay-${table.key}`}
                  aria-label={`Ansicht ${table.label} zuruecksetzen`}
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                </Button>
              )}
            </div>
          )}
        </div>
        {columnPickerOpen && onVisibleColumnsChange ? (
          <div
            id={`column-picker-${table.key}`}
            className="flex flex-wrap gap-2 pt-2"
            data-testid={`column-picker-${table.key}`}
          >
            {availableColumns.map((column) => (
              <label
                key={column.key}
                className="inline-flex min-h-touch items-center gap-1.5 rounded border border-input bg-background px-2 text-xs"
              >
                <input
                  type="checkbox"
                  className="h-3.5 w-3.5"
                  checked={visibleColumnKeys.has(column.key)}
                  disabled={visibleColumnKeys.has(column.key) && visibleColumnKeys.size <= 1}
                  onChange={() => handleToggleColumn(column.key)}
                  data-testid={`column-toggle-${table.key}-${column.key}`}
                />
                <span>{column.label}</span>
              </label>
            ))}
          </div>
        ) : null}
        {onQueryChange && filterableColumns.length > 0 ? (
          <div className="flex flex-wrap items-center gap-2 pt-2">
            <div className="min-w-32">
              <NativeSelect
                value={filterColumn}
                onValueChange={setFilterColumn}
                aria-label={`Filterspalte fuer ${table.label}`}
                data-testid={`filter-column-${table.key}`}
                options={filterableColumns.map((column) => ({
                  value: column.key,
                  label: column.label,
                }))}
              />
            </div>
            <input
              type="text"
              value={filterValue}
              onChange={(event) => setFilterValue(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') handleApplyFilter()
              }}
              placeholder="Filterwert"
              className="min-h-touch w-40 rounded border border-input bg-background px-2 text-sm focus:outline-hidden focus:ring-1 focus:ring-ring"
              aria-label={`Filterwert fuer ${table.label}`}
              data-testid={`filter-value-${table.key}`}
            />
            <Button
              type="button"
              variant="outline"
              className="min-h-touch px-2 text-xs"
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
        {errorMessage ? (
          <div role="alert" className="space-y-2 pb-4 text-sm" data-testid={`table-load-error-${table.key}`}>
            <p className="text-destructive">{errorMessage}</p>
            {onRetry ? (
              <Button type="button" variant="outline" onClick={onRetry} className="min-h-touch">Erneut laden</Button>
            ) : null}
          </div>
        ) : null}
        {errorMessage && visibleRows.length === 0 ? null : (
          <VirtualDataTable
            data={visibleRows}
            rowHeight={table.rowHeight}
            fitToContent
            sortColumn={sort}
            sortDir={sortDir}
            onSortChange={
              onQueryChange
                ? (colKey, dir) => onQueryChange({ sort: colKey, sortDir: dir })
                : undefined
            }
            onRowClick={onRowSelect
              ? (row) => onRowSelect(row)
              : table.rowRouteTemplate
                ? (row) => navigateRowRoute(table.rowRouteTemplate, row)
                : undefined}
            selectedRowKey={selectedRowKey}
            getRowKey={(row, index) => rowIdentity(row, index)}
            columns={renderedColumns}
          />
        )}
        {summen.length > 0 && visibleRows.length > 0 ? (
          <dl className="flex flex-wrap justify-end gap-x-6 gap-y-1 border-t pt-2 text-sm" data-table-totals={table.key}>
            {summen.map((column) => (
              <div key={column.key} className="flex gap-2">
                <dt className="text-muted-foreground">Summe {column.label}</dt>
                <dd className="font-medium tabular-nums">
                  {column.currencyField && !einheitlich(visibleRows, column.currencyField) ? 'Währungen gemischt'
                    : column.renderKind === 'quantity' ? quantityTotal(column, visibleRows) : formatCellValue(sumColumn(visibleRows, (row) => cellValue(column, row, row[column.key])),
                    column.renderKind ?? 'number', column.currencyField ? einheitlich(visibleRows, column.currencyField) : 'EUR',
                    column.unitField ? einheitlich(visibleRows, column.unitField) : column.unit)}
                </dd>
              </div>
            ))}
          </dl>
        ) : null}
        {isServerPaged && totalPages !== undefined && totalPages > 1 ? (
          <div className="flex items-center justify-end gap-2 pt-2">
            <Button
              variant="outline"
              disabled={!page || page <= 1}
              onClick={() => onQueryChange?.({ page: (page ?? 1) - 1 })}
              className="min-h-touch"
            >
              Zurück
            </Button>
            <span className="text-sm text-muted-foreground">
              Seite {page ?? 1} / {totalPages}
            </span>
            <Button
              variant="outline"
              disabled={(page ?? 1) >= totalPages}
              onClick={() => onQueryChange?.({ page: (page ?? 1) + 1 })}
              className="min-h-touch"
            >
              Weiter
            </Button>
          </div>
        ) : null}
      </CardContent>
    </Card>
    </div>
  )
})
