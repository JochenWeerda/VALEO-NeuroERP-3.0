import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Search, Filter, Plus, Download, Upload } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { ListConfig, ListColumn, Action, Field } from './types'

function inputValue(value: unknown): string | number {
  return typeof value === 'string' || typeof value === 'number' ? value : ''
}

type ListFilter = Field & { labelKey?: string; placeholderKey?: string }
type BulkAction = Action & { labelKey?: string }

export interface ServerPaginationParams {
  page: number
  pageSize: number
  sortField?: string
  sortDirection?: 'asc' | 'desc'
  search?: string
  filters?: Record<string, unknown>
}

interface ListReportProps<TItem extends object = Record<string, unknown>> {
  config: ListConfig
  data: TItem[]
  total: number
  onCreate?: () => void
  onEdit?: (_item: TItem) => void
  onDelete?: (_item: TItem) => void
  pendingRows?: Set<string>
  onExport?: () => void
  onImport?: () => void
  /** Generic row action: (actionKey, item). When set, row buttons use config.actions and call this. */
  onAction?: (_actionKey: string, _item: TItem) => void
  /** Generic bulk action: (actionKey, selectedItems). Called when bulk action has no onClick. */
  onBulkAction?: (_actionKey: string, _items: TItem[]) => void
  /** Called when config.serverPagination is true and page/sort/filter changes. */
  onPageChange?: (_params: ServerPaginationParams) => void
  isLoading?: boolean
  loading?: boolean
}

function recordFromItem(item: object): Record<string, unknown> {
  return item as Record<string, unknown>
}

const ListReport = <TItem extends object = Record<string, unknown>>({
  config,
  data,
  total,
  onCreate,
  onEdit,
  onDelete,
  pendingRows,
  onExport,
  onImport,
  onAction,
  onBulkAction,
  onPageChange,
  isLoading = false,
  loading
}: ListReportProps<TItem>) => {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState<Record<string, unknown>>({})
  const [sortField, setSortField] = useState(config.defaultSort?.field || '')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>(config.defaultSort?.direction || 'asc')
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedItems, setSelectedItems] = useState<TItem[]>([])

  const pageSize = config.pageSize || 25
  const totalPages = Math.ceil(total / pageSize)
  const isServerPaginated = config.serverPagination === true && !!onPageChange
  const effectiveLoading = loading ?? isLoading

  const notifyServer = useRef(onPageChange)
  notifyServer.current = onPageChange

  useEffect(() => {
    if (!isServerPaginated) return
    notifyServer.current?.({
      page: currentPage,
      pageSize,
      sortField: sortField || undefined,
      sortDirection: sortField ? sortDirection : undefined,
      search: searchTerm || undefined,
      filters: Object.keys(filters).length > 0 ? filters : undefined,
    })
  }, [isServerPaginated, currentPage, pageSize, sortField, sortDirection, searchTerm, filters])

  const searchRef = useRef<HTMLInputElement>(null)

  // Gap 023: Keyboard-first — Ctrl+F Suche, Ctrl+N Neu, F5 Aktualisieren
  useKeyboardShortcuts([
    {
      key: 'f',
      ctrl: true,
      label: 'Suchen',
      action: () => searchRef.current?.focus(),
      allowInInputs: false,
    },
    ...(onCreate
      ? [{
          key: 'n',
          ctrl: true,
          label: 'Neu',
          action: onCreate,
          disabled: effectiveLoading,
        }]
      : []),
  ])

  // i18n-Helper für Titel und Untertitel
  const displayTitle = config.titleKey ? t(config.titleKey, { entityType: config.title }) : config.title
  const displaySubtitle = config.subtitleKey ? t(config.subtitleKey, { entityType: config.title }) : config.subtitle

  // i18n-Helper für Spalten-Labels
  const getColumnLabel = (column: ListColumn): string => {
    if (column.labelKey) {
      return t(column.labelKey)
    }
    return column.label
  }

  // i18n-Helper für Filter-Labels
  const getFilterLabel = (filter: ListFilter): string => {
    if (filter.labelKey) {
      return t(filter.labelKey)
    }
    return filter.label
  }

  // i18n-Helper für Filter-Placeholder
  const getFilterPlaceholder = (filter: ListFilter): string => {
    if (filter.placeholderKey) {
      return t(filter.placeholderKey)
    }
    return filter.placeholder || ''
  }

  // i18n-Helper für Bulk-Action-Labels
  const getBulkActionLabel = (action: BulkAction): string => {
    if (action.labelKey) {
      return t(action.labelKey)
    }
    return action.label
  }

  // When server-paginated, data is already filtered/sorted/paged by the backend.
  const filteredData = isServerPaginated
    ? data
    : data.filter(item => {
        if (searchTerm) {
          const searchLower = searchTerm.toLowerCase()
          const searchableFields = config.columns
            .filter(col => col.filterable !== false)
            .map(col => col.key)

          const matchesSearch = searchableFields.some(field => {
            const value = recordFromItem(item)[field]
            return value?.toString().toLowerCase().includes(searchLower)
          })

          if (!matchesSearch) return false
        }

        for (const [field, value] of Object.entries(filters)) {
          if (value && recordFromItem(item)[field] !== value) {
            return false
          }
        }

        return true
      })

  const sortedData = isServerPaginated
    ? filteredData
    : [...filteredData].sort((a, b) => {
        if (!sortField) return 0
        const aValue = recordFromItem(a)[sortField] as string | number | null | undefined
        const bValue = recordFromItem(b)[sortField] as string | number | null | undefined
        if ((aValue ?? '') < (bValue ?? '')) return sortDirection === 'asc' ? -1 : 1
        if ((aValue ?? '') > (bValue ?? '')) return sortDirection === 'asc' ? 1 : -1
        return 0
      })

  const paginatedData = isServerPaginated
    ? sortedData
    : sortedData.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const handleFilterChange = (field: string, value: unknown) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }))
    setCurrentPage(1) // Reset to first page when filtering
  }

  const handleBulkAction = (action: BulkAction) => {
    if (selectedItems.length === 0) {
      toast({
        title: t('crud.messages.noSelection'),
        description: t('crud.messages.selectAtLeastOne'),
        variant: "destructive",
      })
      return
    }

    if (action.onClick) {
      action.onClick(selectedItems)
    } else if (onBulkAction) {
      onBulkAction(action.key, selectedItems)
    }
  }

  const renderCell = (column: ListColumn, item: TItem) => {
    const itemRecord = recordFromItem(item)
    const value = itemRecord[column.key]

    if (column.render) {
      return column.render(value, itemRecord)
    }

    // Default rendering based on value type
    if (typeof value === 'boolean') {
      return (
        <Badge variant={value ? 'default' : 'secondary'}>
          {value ? t('common.yes') : t('common.no')}
        </Badge>
      )
    }

    if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/)) {
      // Date formatting
      return new Date(value).toLocaleDateString('de-DE')
    }

    // React cannot render plain objects – convert to JSON string
    if (value !== null && typeof value === 'object') {
      return (
        <span className="font-mono text-xs">
          {JSON.stringify(value)}
        </span>
      )
    }

    if (value === null || value === undefined) return '-'
    return String(value)
  }

  return (
    <div className="space-y-8 p-4 md:p-8">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4 rounded-[var(--radius)] border border-border bg-card p-6 shadow-sm">
        <div>
          <h1 className="text-xl font-bold tracking-normal text-foreground">{displayTitle}</h1>
          {displaySubtitle && (
            <p className="mt-1 text-sm text-muted-foreground">{displaySubtitle}</p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          {onImport && (
            <Button variant="outline" onClick={onImport} className="gap-2">
              <Upload className="h-4 w-4" />
              {t('crud.actions.import')}
            </Button>
          )}
          {onExport && (
            <Button variant="outline" onClick={onExport} className="gap-2">
              <Download className="h-4 w-4" />
              {t('crud.actions.export')}
            </Button>
          )}
          {onCreate && (
            <Button onClick={onCreate} className="gap-2">
              <Plus className="h-4 w-4" />
              {t('crud.actions.new')}
            </Button>
          )}
        </div>
      </div>

      {/* Filters */}
      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Filter className="h-5 w-5 text-primary" />
            {t('crud.list.searchAndFilter')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {/* Search */}
            <div>
              <Label htmlFor="list-report-search">{t('common.search')}</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="list-report-search"
                  ref={searchRef}
                  placeholder={t('crud.list.searchPlaceholder')}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Dynamic filters */}
            {config.filters?.map(filter => {
              const filterName = filter.name || filter.key || ''
              const filterId = `list-report-filter-${filterName}`
              return (
              <div key={filterName}>
                <Label htmlFor={filterId}>{getFilterLabel(filter)}</Label>
                {filter.type === 'select' ? (
                  <NativeSelect
                    id={filterId}
                    value={inputValue(filters[filterName])}
                    onValueChange={(value) => handleFilterChange(filterName, value)}
                    options={((filter['options'] as Array<{ value: string | number; label: string; labelKey?: string }>) ?? []).map((option) => ({
                      value: String(option.value),
                      label: option.labelKey ? t(option.labelKey) : option.label,
                    }))}
                    placeholder={getFilterPlaceholder(filter)}
                  />
                ) : filter.type === 'number' ? (
                  <div className="relative">
                    <Input
                      id={filterId}
                      type="number"
                      placeholder={getFilterPlaceholder(filter) || t('crud.placeholders.enterAmount')}
                      value={inputValue(filters[filterName])}
                      onChange={(e) => handleFilterChange(filterName, e.target.value)}
                      min={filter['min'] as number | undefined}
                      max={filter['max'] as number | undefined}
                      step={(filter['step'] as number | undefined) || 0.01}
                      className="pr-8"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm">€</span>
                  </div>
                ) : filter.type === 'date' ? (
                  <Input
                    id={filterId}
                    type="date"
                    placeholder={getFilterPlaceholder(filter)}
                    value={inputValue(filters[filterName])}
                    onChange={(e) => handleFilterChange(filterName, e.target.value)}
                    max={(filter['maxDate'] as string | undefined) || new Date().toISOString().split('T')[0]}
                    min={filter['minDate'] as string | undefined}
                    lang="de-DE"
                  />
                ) : (
                  <Input
                    id={filterId}
                    placeholder={getFilterPlaceholder(filter)}
                    value={inputValue(filters[filterName])}
                    onChange={(e) => handleFilterChange(filterName, e.target.value)}
                  />
                )}
              </div>
            )})}
          </div>
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedItems.length > 0 && config.bulkActions && (
        <Card className="border-primary/30 bg-primary/5">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">
                {t('crud.list.selectedItems', { count: selectedItems.length })}
              </span>
              <div className="flex gap-2">
                {config.bulkActions.map(action => (
                  <Button
                    key={action.key}
                    variant="outline"
                    size="sm"
                    onClick={() => handleBulkAction(action)}
                    className="gap-2"
                  >
                    {getBulkActionLabel(action)}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            {t('crud.list.results', { count: filteredData.length, total })}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto rounded-[var(--radius)] border border-border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <input
                      type="checkbox"
                      aria-label={t('crud.list.selectAll')}
                      checked={selectedItems.length === paginatedData.length && paginatedData.length > 0}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedItems(paginatedData)
                        } else {
                          setSelectedItems([])
                        }
                      }}
                    />
                  </TableHead>
                  {config.columns.map(column => (
                    <TableHead
                      key={column.key}
                      className={column.sortable ? 'cursor-pointer hover:bg-primary/5' : ''}
                      onClick={() => column.sortable && handleSort(column.key)}
                    >
                      <div className="flex items-center gap-2">
                        {getColumnLabel(column)}
                        {column.sortable && sortField === column.key && (
                          <span className="text-xs">
                            {sortDirection === 'asc' ? '↑' : '↓'}
                          </span>
                        )}
                      </div>
                    </TableHead>
                  ))}
                  <TableHead className="w-20">{t('crud.list.actions')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {effectiveLoading ? (
                  <TableRow>
                    <TableCell colSpan={config.columns.length + 2} className="text-center py-8">
                      {t('crud.list.loading', { entityType: displayTitle })}
                    </TableCell>
                  </TableRow>
                ) : paginatedData.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={config.columns.length + 2} className="py-12">
                      <div className="flex flex-col items-center gap-3 text-center text-muted-foreground">
                        {config.emptyState?.icon && (
                          <span className="text-4xl" aria-hidden="true">{config.emptyState.icon}</span>
                        )}
                        <p className="font-medium text-foreground">
                          {config.emptyState?.title ?? t('crud.list.noResults', { entityType: displayTitle })}
                        </p>
                        {config.emptyState?.description && (
                          <p className="text-sm">{config.emptyState.description}</p>
                        )}
                        {config.emptyState?.actionLabel && onCreate && (
                          <Button size="sm" onClick={onCreate} className="mt-2">
                            <Plus className="h-4 w-4 mr-1" aria-hidden="true" />
                            {config.emptyState.actionLabel}
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  paginatedData.map((item, index) => (
                    <TableRow key={typeof recordFromItem(item).id === 'string' || typeof recordFromItem(item).id === 'number' ? recordFromItem(item).id : index}>
                      <TableCell>
                        <input
                          type="checkbox"
                          aria-label={t('crud.list.selectItem', {
                            item: String(recordFromItem(item).purchaseOrderNumber ?? recordFromItem(item).name ?? recordFromItem(item).id ?? index + 1),
                          })}
                          checked={selectedItems.includes(item)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedItems(prev => [...prev, item])
                            } else {
                              setSelectedItems(prev => prev.filter(i => i !== item))
                            }
                          }}
                        />
                      </TableCell>
                      {config.columns.map(column => (
                        <TableCell key={column.key}>
                          {renderCell(column, item)}
                        </TableCell>
                      ))}
                      <TableCell>
                        <div className="flex gap-1">
                          {onAction
                            ? config.actions
                                .filter(a => a.key !== 'create')
                                .map(action => (
                                  <Button
                                    key={action.key}
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => onAction(action.key, item)}
                                    disabled={pendingRows?.has(String(recordFromItem(item).id))}
                                    className={action.type === 'danger' ? 'text-destructive hover:text-destructive' : undefined}
                                  >
                                    {action.labelKey ? t(action.labelKey) : action.label}
                                  </Button>
                                ))
                            : (
                              <>
                                {onEdit && (
                                  <Button variant="ghost" size="sm" onClick={() => onEdit(item)}>
                                    {t('crud.actions.edit')}
                                  </Button>
                                )}
                                {onDelete && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => onDelete(item)}
                                    disabled={pendingRows?.has(String(recordFromItem(item).id))}
                                    className="text-destructive hover:text-destructive"
                                  >
                                    {t('crud.actions.delete')}
                                  </Button>
                                )}
                              </>
                            )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Simple Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-4 rounded-[var(--radius)] border border-border bg-card p-3 shadow-sm">
          <Button
            variant="outline"
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
          >
            {t('crud.list.previous')}
          </Button>

          <span className="text-sm text-muted-foreground">
            {t('crud.list.page')} {currentPage} {t('crud.list.of')} {totalPages}
          </span>

          <Button
            variant="outline"
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
          >
            {t('crud.list.next')}
          </Button>
        </div>
      )}
    </div>
  )
}

export default ListReport
