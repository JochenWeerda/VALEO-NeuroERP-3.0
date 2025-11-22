import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Search, Filter, Plus, Download, Upload } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { ListConfig, ListColumn } from './types'
import { getStatusLabel } from '@/features/crud/utils/i18n-helpers'

interface ListReportProps {
  config: ListConfig
  data: any[]
  total: number
  onCreate?: () => void
  onEdit?: (_item: any) => void
  onDelete?: (_item: any) => void
  onExport?: () => void
  onImport?: () => void
  isLoading?: boolean
}

const ListReport: React.FC<ListReportProps> = ({
  config,
  data,
  total,
  onCreate,
  onEdit,
  onDelete,
  onExport,
  onImport,
  isLoading = false
}) => {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [filters, setFilters] = useState<Record<string, any>>({})
  const [sortField, setSortField] = useState(config.defaultSort?.field || '')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>(config.defaultSort?.direction || 'asc')
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedItems, setSelectedItems] = useState<any[]>([])

  const pageSize = config.pageSize || 25
  const totalPages = Math.ceil(total / pageSize)

  // i18n-Helper für Titel und Untertitel
  const displayTitle = config.titleKey ? t(config.titleKey) : config.title
  const displaySubtitle = config.subtitleKey ? t(config.subtitleKey) : config.subtitle

  // i18n-Helper für Spalten-Labels
  const getColumnLabel = (column: ListColumn): string => {
    if (column.labelKey) {
      return t(column.labelKey)
    }
    return column.label
  }

  // i18n-Helper für Filter-Labels
  const getFilterLabel = (filter: any): string => {
    if (filter.labelKey) {
      return t(filter.labelKey)
    }
    return filter.label
  }

  // i18n-Helper für Filter-Placeholder
  const getFilterPlaceholder = (filter: any): string => {
    if (filter.placeholderKey) {
      return t(filter.placeholderKey)
    }
    return filter.placeholder || ''
  }

  // i18n-Helper für Bulk-Action-Labels
  const getBulkActionLabel = (action: any): string => {
    if (action.labelKey) {
      return t(action.labelKey)
    }
    return action.label
  }

  // Filter data based on search and filters
  const filteredData = data.filter(item => {
    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      const searchableFields = config.columns
        .filter(col => col.filterable !== false)
        .map(col => col.key)

      const matchesSearch = searchableFields.some(field => {
        const value = item[field]
        return value?.toString().toLowerCase().includes(searchLower)
      })

      if (!matchesSearch) return false
    }

    // Custom filters
    for (const [field, value] of Object.entries(filters)) {
      if (value && item[field] !== value) {
        return false
      }
    }

    return true
  })

  // Sort data
  const sortedData = [...filteredData].sort((a, b) => {
    if (!sortField) return 0

    const aValue = a[sortField]
    const bValue = b[sortField]

    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1
    return 0
  })

  // Paginate data
  const paginatedData = sortedData.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const handleFilterChange = (field: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }))
    setCurrentPage(1) // Reset to first page when filtering
  }

  const handleBulkAction = (action: any) => {
    if (selectedItems.length === 0) {
      toast({
        title: t('crud.messages.noSelection'),
        description: t('crud.messages.selectAtLeastOne'),
        variant: "destructive",
      })
      return
    }

    // Handle bulk actions
    if (action.onClick) {
      action.onClick(selectedItems)
    }
  }

  const renderCell = (column: ListColumn, item: any) => {
    const value = item[column.key]

    if (column.render) {
      return column.render(value, item)
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

    return value || '-'
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{displayTitle}</h1>
          {displaySubtitle && (
            <p className="text-muted-foreground">{displaySubtitle}</p>
          )}
        </div>
        <div className="flex gap-2">
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
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            {t('crud.list.searchAndFilter')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {/* Search */}
            <div>
              <Label>{t('common.search')}</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder={t('crud.list.searchPlaceholder')}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Dynamic filters */}
            {config.filters?.map(filter => (
              <div key={filter.name}>
                <Label>{getFilterLabel(filter)}</Label>
                {filter.type === 'select' ? (
                  <Select
                    value={filters[filter.name] || ''}
                    onValueChange={(value) => handleFilterChange(filter.name, value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={getFilterPlaceholder(filter)} />
                    </SelectTrigger>
                    <SelectContent>
                      {(filter as any).options?.map((option: any) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.labelKey ? t(option.labelKey) : option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Input
                    placeholder={getFilterPlaceholder(filter)}
                    value={filters[filter.name] || ''}
                    onChange={(e) => handleFilterChange(filter.name, e.target.value)}
                  />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedItems.length > 0 && config.bulkActions && (
        <Card className="border-blue-500 bg-blue-50">
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
          <CardTitle>
            {t('crud.list.results', { count: filteredData.length, total })}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <input
                      type="checkbox"
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
                      className={column.sortable ? 'cursor-pointer hover:bg-muted' : ''}
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
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={config.columns.length + 2} className="text-center py-8">
                      {t('crud.list.loading', { entityType: displayTitle })}
                    </TableCell>
                  </TableRow>
                ) : paginatedData.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={config.columns.length + 2} className="text-center py-8">
                      {t('crud.list.noResults', { entityType: displayTitle })}
                    </TableCell>
                  </TableRow>
                ) : (
                  paginatedData.map((item, index) => (
                    <TableRow key={item.id || index}>
                      <TableCell>
                        <input
                          type="checkbox"
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
                          {onEdit && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => onEdit(item)}
                            >
                              {t('crud.actions.edit')}
                            </Button>
                          )}
                          {onDelete && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => onDelete(item)}
                              className="text-red-600 hover:text-red-700"
                            >
                              {t('crud.actions.delete')}
                            </Button>
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
        <div className="flex justify-center items-center gap-4">
          <Button
            variant="outline"
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
          >
            {t('crud.list.previous')}
          </Button>

          <span className="text-sm">
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