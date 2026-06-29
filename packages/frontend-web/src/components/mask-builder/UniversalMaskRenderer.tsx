import { LazyTabs } from '@/components/ui/LazyTabs'
import type { ScreenDefinition, ScreenFieldDefinition } from './schema'
import type { RenderPlan } from './render-plan/types'
import type { LookupBinding, TableQueryState } from './runtime/types'
import {
  ActionBarRenderer,
  FastFormRenderer,
  FastSummaryRenderer,
  FastTabRenderer,
  FastTableRenderer,
  TabContentRenderer,
  WorkflowPanelRenderer,
  layoutClasses,
} from './renderers'

interface UniversalMaskRendererProps {
  /** Preferred: pre-compiled render plan */
  plan?: RenderPlan
  /** Legacy: raw screen definition (compiled internally once per reference) */
  screen?: ScreenDefinition
  data?: Record<string, unknown>
  tables?: Record<string, Record<string, unknown>[]>
  allowedPermissions?: string[]
  onTabChange?: (_tabKey: string) => void
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  // Runtime query state (from useUniversalMaskRuntime)
  tableQueryStates?: Record<string, TableQueryState>
  tableTotals?: Record<string, number>
  onTableQueryChange?: (_tableKey: string, _patch: Partial<TableQueryState>) => void
  lookupBindings?: Record<string, LookupBinding>
}

function renderLegacyFields(
  fields: ScreenFieldDefinition[] = [],
  payload: Record<string, unknown>,
  className: string,
): JSX.Element | null {
  if (fields.length === 0) return null
  return (
    <FastFormRenderer
      fieldKeys={fields.map((field) => field.key)}
      fieldsByKey={Object.fromEntries(
        fields.map((field, index) => [
          field.key,
          {
            key: field.key,
            label: field.label,
            componentKind: field.type === 'table' ? 'text' : field.type,
            dataPath: field.key,
            order: index,
            required: field.required ?? false,
            readOnly: field.readOnly ?? false,
            visible: true,
            placeholder: field.placeholder,
            helpText: field.helpText,
            options: field.options,
            dataSourceKey: field.dataSourceKey,
            minSearchChars: field.minSearchChars ?? 2,
            renderHint: field.renderHint,
          },
        ]),
      )}
      payload={payload}
      className={className}
    />
  )
}

function RenderFromPlan({
  plan,
  payload,
  tables,
  tableQueryStates,
  tableTotals,
  onTableQueryChange,
  onTabChange,
  onAction,
}: {
  plan: RenderPlan
  payload: Record<string, unknown>
  tables: Record<string, Record<string, unknown>[]>
  tableQueryStates?: Record<string, TableQueryState>
  tableTotals?: Record<string, number>
  onTableQueryChange?: (_tableKey: string, _patch: Partial<TableQueryState>) => void
  onTabChange?: (_tabKey: string) => void
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
}): JSX.Element {
  const classes = layoutClasses(plan.shell.layoutMode)

  return (
    <div
      className={classes.root}
      data-screen-definition={plan.screenId}
      data-testid={`screen-${plan.screenId}`}
      data-layout-mode={plan.shell.layoutMode}
      data-mobile-layout={plan.shell.mobileMode}
      data-render-plan-cache-key={plan.cacheKey}
    >
      <ActionBarRenderer
        domain={plan.shell.domain}
        mode={plan.shell.mode}
        title={plan.shell.title}
        subtitle={plan.shell.subtitle}
        actions={plan.actions}
        headerClassName={classes.header}
        touchTargetClass={classes.touchTarget}
        onAction={onAction}
        payload={payload}
      />

      <WorkflowPanelRenderer workflow={plan.workflow} />
      <FastSummaryRenderer items={plan.summaryItems} />

      <FastFormRenderer
        fieldKeys={plan.rootFieldKeys}
        fieldsByKey={plan.fieldsByKey}
        payload={payload}
        className={classes.fields}
        performance={plan.performance}
      />

      {plan.rootTableKeys.map((tableKey) => {
        const tablePlan = plan.tablesByKey[tableKey]
        if (!tablePlan) return null
        return (
          <FastTableRenderer
            key={tableKey}
            table={tablePlan}
            rows={tables[tableKey] ?? []}
            page={tableQueryStates?.[tableKey]?.page}
            sort={tableQueryStates?.[tableKey]?.sort}
            sortDir={tableQueryStates?.[tableKey]?.sortDir}
            total={tableTotals?.[tableKey]}
            onQueryChange={onTableQueryChange ? (patch) => onTableQueryChange(tableKey, patch) : undefined}
          />
        )
      })}

      {plan.visibleTabs.length > 0 && (
        <LazyTabs
          onValueChange={onTabChange}
          tabs={plan.visibleTabs.map((tab) => ({
            key: tab.key,
            label: tab.label,
            lazy: tab.lazy,
            keepAlive: tab.keepAlive,
            content: () => (
              <FastTabRenderer
                plan={plan}
                tabKey={tab.key}
                payload={payload}
                tables={tables}
                tableQueryStates={tableQueryStates}
                tableTotals={tableTotals}
                onQueryChange={onTableQueryChange}
              />
            ),
          }))}
        />
      )}
    </div>
  )
}

function RenderFromScreen({
  screen,
  payload,
  tables,
  allowedPermissions,
  onTabChange,
  onAction,
}: {
  screen: ScreenDefinition
  payload: Record<string, unknown>
  tables: Record<string, Record<string, unknown>[]>
  allowedPermissions: string[]
  onTabChange?: (_tabKey: string) => void
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
}): JSX.Element {
  const classes = layoutClasses(screen.layout?.preferredMode ?? 'desktopDense')
  const visibleActions = (screen.actions ?? []).filter(
    (action) => !action.permission || allowedPermissions.includes(action.permission),
  )

  return (
    <div
      className={classes.root}
      data-screen-definition={screen.id}
      data-testid={`screen-${screen.id}`}
      data-layout-mode={screen.layout?.preferredMode ?? 'desktopDense'}
      data-mobile-layout={screen.layout?.mobileMode ?? 'mobileStack'}
    >
      <ActionBarRenderer
        domain={screen.domain}
        mode={screen.mode}
        title={screen.title}
        subtitle={screen.subtitle}
        actions={visibleActions}
        headerClassName={classes.header}
        touchTargetClass={classes.touchTarget}
        onAction={onAction}
        payload={payload}
      />

      <WorkflowPanelRenderer workflow={screen.workflow} />
      <FastSummaryRenderer items={screen.summary ?? []} />
      {renderLegacyFields(screen.fields, payload, classes.fields)}

      {(screen.tables ?? []).map((table) => (
        <FastTableRenderer
          key={table.key}
          table={{
            key: table.key,
            label: table.label,
            columns: table.columns.map((column) => ({
              key: column.key,
              label: column.label,
              width: column.width,
              numeric: column.numeric,
            })),
            pageSize: Math.min(table.pageSize ?? 25, 50),
            virtualized: table.virtualized ?? true,
            rowHeight: table.rowHeight ?? 52,
            serverPagination: table.serverPagination ?? true,
          }}
          rows={tables[table.key] ?? []}
        />
      ))}

      {screen.tabs && screen.tabs.length > 0 && (
        <LazyTabs
          onValueChange={onTabChange}
          tabs={screen.tabs.map((tab) => ({
            key: tab.key,
            label: tab.label,
            lazy: tab.lazy ?? true,
            keepAlive: tab.keepAlive ?? true,
            content: () => (
              <TabContentRenderer
                fields={tab.fields}
                tables={tab.tables}
                fieldsClassName={classes.fields}
                payload={payload}
                tableRows={tables}
              />
            ),
          }))}
        />
      )}
    </div>
  )
}

export function UniversalMaskRenderer({
  plan,
  screen,
  data = {},
  tables = {},
  allowedPermissions = [],
  onTabChange,
  onAction,
  tableQueryStates,
  tableTotals,
  onTableQueryChange,
}: UniversalMaskRendererProps): JSX.Element {
  const payload = data

  if (plan) {
    return (
      <RenderFromPlan
        plan={plan}
        payload={payload}
        tables={tables}
        tableQueryStates={tableQueryStates}
        tableTotals={tableTotals}
        onTableQueryChange={onTableQueryChange}
        onTabChange={onTabChange}
        onAction={onAction}
      />
    )
  }

  if (screen) {
    return (
      <RenderFromScreen
        screen={screen}
        payload={payload}
        tables={tables}
        allowedPermissions={allowedPermissions}
        onTabChange={onTabChange}
        onAction={onAction}
      />
    )
  }

  throw new Error('UniversalMaskRenderer requires plan or screen')
}
