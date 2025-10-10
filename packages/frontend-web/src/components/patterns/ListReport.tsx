/**
 * ListReport - SAP Fiori Pattern
 * Use-Case: Liste + Filter + Suche + Actions
 * 
 * Features:
 * - DataTable mit Pagination
 * - Filter-Bar
 * - Toolbar mit Actions
 * - Multi-Select
 * - Export-Funktion
 * - i18n-Support
 * - MCP-Metadaten
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PageToolbar, ToolbarAction } from '@/components/navigation/PageToolbar';
import { DataTable, ColumnDef } from '@/components/ui/data-table';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, SlidersHorizontal } from 'lucide-react';
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata';

export interface ListReportProps<T> {
  // Titel & Beschreibung
  title: string;
  titleKey?: string; // i18n-Key
  subtitle?: string;
  subtitleKey?: string;
  
  // Daten
  data: T[];
  columns: ColumnDef<T>[];
  
  // Actions
  primaryActions?: ToolbarAction[];
  overflowActions?: ToolbarAction[];
  
  // Filter & Suche
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  filterOptions?: FilterOption[];
  
  // Features
  selectable?: boolean;
  onSelectionChange?: (selected: T[]) => void;
  
  // MCP
  mcpContext?: {
    domain: string;
    entityType: string;
  };
}

export interface FilterOption {
  field: string;
  label: string;
  labelKey?: string;
  type: 'select' | 'date' | 'number' | 'text';
  options?: Array<{ value: string; label: string }>;
}

export const listReportMCP = createMCPMetadata('ListReport', 'list', {
  accessibility: {
    role: 'region',
    ariaLabel: 'List report with filters and actions',
  },
  intent: {
    purpose: 'Display and manage list of entities with filters',
    userActions: ['search', 'filter', 'select', 'export', 'create'],
  },
  mcpHints: {
    autoFillable: true,
    explainable: true,
    testable: true,
    contextAware: true,
  },
});

export function ListReport<T>({
  title,
  titleKey,
  subtitle,
  subtitleKey,
  data,
  columns,
  primaryActions,
  overflowActions,
  searchPlaceholder,
  onSearch,
  filterOptions,
  selectable = false,
  onSelectionChange,
  mcpContext,
}: ListReportProps<T>) {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedRows, setSelectedRows] = useState<T[]>([]);

  const displayTitle = titleKey ? t(titleKey) : title;
  const displaySubtitle = subtitleKey ? t(subtitleKey) : subtitle;

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    onSearch?.(query);
  };

  return (
    <div
      className="flex flex-col h-full"
      data-mcp-pattern="list-report"
      data-mcp-entity={mcpContext?.entityType}
    >
      {/* Toolbar (SAP Fiori Pattern) */}
      <PageToolbar
        title={displayTitle}
        subtitle={displaySubtitle}
        primaryActions={primaryActions}
        overflowActions={overflowActions}
        mcpContext={mcpContext}
      />

      <div className="flex-1 p-6 space-y-4 overflow-auto">
        {/* Search & Filter-Bar (SAP Fiori Pattern) */}
        <div className="flex gap-4">
          {/* Search */}
          {onSearch && (
            <div className="flex-1 max-w-md relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder={searchPlaceholder || t('common.search')}
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          )}

          {/* Filter-Toggle */}
          {filterOptions && filterOptions.length > 0 && (
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
            >
              <SlidersHorizontal className="mr-2 h-4 w-4" />
              {t('common.filter')}
            </Button>
          )}
        </div>

        {/* Filter-Panel (SAP Fiori Pattern - collapsible) */}
        {showFilters && filterOptions && (
          <div className="p-4 border rounded-lg bg-muted/50">
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filterOptions.map((filter) => (
                <div key={filter.field}>
                  <label className="text-sm font-medium">
                    {filter.labelKey ? t(filter.labelKey) : filter.label}
                  </label>
                  {/* Filter-Input basierend auf type */}
                  <Input type={filter.type === 'text' ? 'text' : filter.type} />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* DataTable (SAP Fiori Pattern) */}
        <DataTable
          columns={columns}
          data={data}
          selectable={selectable}
          onSelectionChange={(rows) => {
            setSelectedRows(rows);
            onSelectionChange?.(rows);
          }}
        />

        {/* Footer mit Item-Count (SAP Fiori Pattern) */}
        <div className="text-sm text-muted-foreground">
          {t('pattern.listreport.items_count', { count: data.length })}
        </div>
      </div>
    </div>
  );
}

