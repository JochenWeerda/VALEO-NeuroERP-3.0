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

import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PageToolbar, ToolbarAction } from '@/components/navigation/PageToolbar';
import { ColumnDef, DataTable } from '@/components/ui/data-table';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, SlidersHorizontal } from 'lucide-react';
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata';
import { buildToolbarActionsFromRegistry, useActionsForMask, useActionDispatchOptional } from '@/features/ki-usability';
import { auth } from '@/lib/auth';
import { resolveRoleDensityProfile } from '@/features/role-density';
import { useTenant } from '@/hooks/useTenant';
import { useUIDensityManifest } from '@/lib/api/ui-density-manifest';
import { PageSection, PageSurface } from '@/components/patterns/PageSurface';

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
  onSearch?: (_query: string) => void;
  filterOptions?: FilterOption[];
  
  // Features
  selectable?: boolean;
  onSelectionChange?: (_selected: T[]) => void;
  
  // MCP
  mcpContext?: {
    pageDomain: string;
    currentDocument?: string;
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
}: ListReportProps<T>): JSX.Element {
  const { t } = useTranslation();
  const actionDispatch = useActionDispatchOptional();
  const { tenantId } = useTenant();
  const { data: actionResponse } = useActionsForMask(mcpContext?.pageDomain, mcpContext?.currentDocument);
  const densityManifestQuery = useUIDensityManifest(mcpContext?.pageDomain);
  const roleDensityProfile = useMemo(
    () =>
      resolveRoleDensityProfile(auth.getUser()?.roles, {
        tenantId,
        pageDomain: mcpContext?.pageDomain,
        availableActionIds: actionResponse?.actions?.map((action) => action.id) ?? [],
        backendDensity: densityManifestQuery.data?.entry?.recommended_density,
      }),
    [actionResponse?.actions, densityManifestQuery.data?.entry?.recommended_density, mcpContext?.pageDomain, tenantId],
  );
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showFilters, setShowFilters] = useState<boolean>(false);

  const displayTitle = typeof titleKey === 'string' && titleKey.length > 0 ? t(titleKey) : title;
  const displaySubtitle = typeof subtitleKey === 'string' && subtitleKey.length > 0 ? t(subtitleKey) : subtitle;
  const contextualToolbarActions = useMemo(
    () => buildToolbarActionsFromRegistry(actionResponse?.actions, actionDispatch),
    [actionDispatch, actionResponse?.actions],
  );

  const mergedPrimaryActions = useMemo<ToolbarAction[]>(() => {
    if (Array.isArray(primaryActions) && primaryActions.length > 0) {
      return primaryActions;
    }
    return contextualToolbarActions.primary;
  }, [contextualToolbarActions.primary, primaryActions]);

  const mergedOverflowActions = useMemo<ToolbarAction[]>(() => {
    const fromProps = overflowActions ?? [];
    const quickOverflow = Array.isArray(primaryActions) && primaryActions.length > 0
      ? contextualToolbarActions.overflow
      : contextualToolbarActions.overflow;
    const byId = new Map<string, ToolbarAction>();
    for (const action of [...fromProps, ...quickOverflow]) {
      byId.set(action.id, action);
    }
    return Array.from(byId.values());
  }, [contextualToolbarActions.overflow, overflowActions, primaryActions]);
  const availableActions = [
    ...(mergedPrimaryActions.map((action) => action.id)),
    ...(mergedOverflowActions.map((action) => action.id)),
  ];
  const toolbarContext = mcpContext
    ? {
        pageDomain: mcpContext.pageDomain,
        currentDocument: mcpContext.currentDocument,
        availableActions,
      }
    : undefined;

  const handleSearch = (query: string): void => {
    setSearchQuery(query);
    if (typeof onSearch === 'function') {
      onSearch(query);
    }
  };

  return (
    <div
      className="flex flex-col h-full"
      data-mcp-pattern="list-report"
    >
      {/* Toolbar (SAP Fiori Pattern) */}
      <PageToolbar
        title={displayTitle}
        subtitle={displaySubtitle}
        primaryActions={mergedPrimaryActions}
        overflowActions={mergedOverflowActions}
        densityProfileOverride={roleDensityProfile}
        mcpContext={toolbarContext}
      />

      <PageSurface data-page-surface="list-report-pattern" contentClassName="space-y-4">
        {/* Search & Filter-Bar (SAP Fiori Pattern) */}
        <PageSection
          title="Listensteuerung"
          description="Suche, Filter und Massenaktionen laufen im gleichen DS-Rahmen wie Tabelle und Ergebnisstatus."
          className="space-y-4"
        >
        <div className="flex gap-4">
          {/* Search */}
          {typeof onSearch === 'function' && (
            <div className="flex-1 max-w-md relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder={searchPlaceholder ?? t('common.search')}
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          )}

          {/* Filter-Toggle */}
          {roleDensityProfile.density !== 'focused' && Array.isArray(filterOptions) && filterOptions.length > 0 && (
            <Button
              variant="outline"
              onClick={() => setShowFilters((prev) => !prev)}
            >
              <SlidersHorizontal className="mr-2 h-4 w-4" />
              {t('common.filter')}
            </Button>
          )}
        </div>

        {/* Filter-Panel (SAP Fiori Pattern - collapsible) */}
        {roleDensityProfile.density !== 'focused' && showFilters && Array.isArray(filterOptions) && (
          <div className="rounded-2xl border border-border/70 bg-muted/50 p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {filterOptions.map((filter) => (
                <div key={filter.field}>
                  <label className="text-sm font-medium">
                    {typeof filter.labelKey === 'string' && filter.labelKey.length > 0
                      ? t(filter.labelKey)
                      : filter.label}
                  </label>
                  {/* Filter-Input basierend auf type */}
                  <Input type={filter.type === 'text' ? 'text' : filter.type} />
                </div>
              ))}
            </div>
          </div>
        )}
        </PageSection>

        {/* DataTable (SAP Fiori Pattern) */}
        <PageSection title="Ergebnisliste" description="Tabellarische Arbeitsfläche mit konsistenter Informationsdichte und responsiver Interaktion.">
          <DataTable
            columns={columns}
            data={data}
            selectable={selectable}
            onSelectionChange={(rows) => {
              if (typeof onSelectionChange === 'function') {
                onSelectionChange(rows);
              }
            }}
          />

          {/* Footer mit Item-Count (SAP Fiori Pattern) */}
          <div className="text-sm text-muted-foreground">
            {t('pattern.listreport.items_count', { count: data.length })}
          </div>
        </PageSection>
      </PageSurface>
    </div>
  );
}
