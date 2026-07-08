import { LazyTabs } from '@/components/ui/LazyTabs'
import { resolveContextRailSections, type ScreenDefinition, type ScreenFieldDefinition } from './schema'
import type { RenderPlan } from './render-plan/types'
import type { ScreenOverlay } from './render-plan/overlay'
import type { LookupBinding, TableQueryState } from './runtime/types'
import type { UniversalFormState } from './runtime/FormState'
import type { WorkflowState } from './runtime/WorkflowRuntime'
import { LookupBindingContext } from './runtime/LookupBindingContext'
import { FormStateContext } from './runtime/FormStateContext'
import {
  ActionBarRenderer,
  FastFormRenderer,
  FastSummaryRenderer,
  FastTabRenderer,
  FastTableRenderer,
  CalendarRenderer,
  TabContentRenderer,
  TileGridRenderer,
  WorkflowPanelRenderer,
  layoutClasses,
} from './renderers'

interface UniversalMaskRendererProps {
  /** Preferred: pre-compiled render plan */
  plan?: RenderPlan
  /** Legacy: raw screen definition (compiled internally once per reference) */
  screen?: ScreenDefinition
  data?: Record<string, unknown>
  entityId?: string
  tables?: Record<string, Record<string, unknown>[]>
  allowedPermissions?: string[]
  onTabChange?: (_tabKey: string) => void
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  // Runtime query state (from useUniversalMaskRuntime)
  tableQueryStates?: Record<string, TableQueryState>
  tableTotals?: Record<string, number>
  onTableQueryChange?: (_tableKey: string, _patch: Partial<TableQueryState>) => void
  overlay?: ScreenOverlay
  onOverlayChange?: (_patch: ScreenOverlay) => void | Promise<void>
  onOverlayReset?: () => void | Promise<void>
  lookupBindings?: Record<string, LookupBinding>
  /** Optional edit-mode form state (from useUniversalFormState) */
  formState?: UniversalFormState
  /** Optional rich workflow state (from useWorkflowState) */
  workflowState?: WorkflowState
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
  onOverlayChange,
  onOverlayReset,
  onTabChange,
  onAction,
  formState,
  workflowState,
  entityId,
}: {
  plan: RenderPlan
  payload: Record<string, unknown>
  entityId?: string
  tables: Record<string, Record<string, unknown>[]>
  tableQueryStates?: Record<string, TableQueryState>
  tableTotals?: Record<string, number>
  onTableQueryChange?: (_tableKey: string, _patch: Partial<TableQueryState>) => void
  onOverlayChange?: (_patch: ScreenOverlay) => void | Promise<void>
  onOverlayReset?: () => void | Promise<void>
  onTabChange?: (_tabKey: string) => void
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  formState?: UniversalFormState
  workflowState?: WorkflowState
}): JSX.Element {
  const classes = layoutClasses(plan.shell.layoutMode, plan.shell.density)
  const effectivePayload = formState ? formState.values : payload
  const effectiveEntityId = entityId ?? String(effectivePayload.id ?? effectivePayload.entity_id ?? '')

  return (
    <FormStateContext.Provider value={formState}>
    <div
      className={classes.root}
      data-screen-definition={plan.screenId}
      data-testid={`screen-${plan.screenId}`}
      data-layout-mode={plan.shell.layoutMode}
      data-mobile-layout={plan.shell.mobileMode}
      data-render-plan-cache-key={plan.cacheKey}
      data-floorplan={plan.shell.floorplan}
      data-density={plan.shell.density}
      data-context-rail={plan.shell.contextRail}
      data-context-rail-sections={plan.shell.contextRailSections.join(',')}
      data-table-profile={plan.shell.tableProfile}
    >
      <ActionBarRenderer
        domain={plan.shell.domain}
        mode={plan.shell.mode}
        title={plan.shell.title}
        subtitle={plan.shell.subtitle}
        actions={plan.actions}
        floorplan={plan.shell.floorplan}
        density={plan.shell.density}
        contextRail={plan.shell.contextRail}
        headerClassName={classes.header}
        touchTargetClass={classes.touchTarget}
        onAction={onAction}
        payload={effectivePayload}
      />

      <WorkflowPanelRenderer
        workflow={plan.workflow}
        workflowState={workflowState}
        contextRailSections={plan.shell.contextRailSections}
        entityType={plan.screenId}
        entityId={effectiveEntityId}
      />
      <FastSummaryRenderer items={plan.summaryItems} />
      <TileGridRenderer tiles={plan.tiles} />
      <CalendarRenderer calendar={plan.calendar} />

      <FastFormRenderer
        fieldKeys={plan.rootFieldKeys}
        fieldsByKey={plan.fieldsByKey}
        payload={effectivePayload}
        className={classes.fields}
        performance={plan.performance}
        voiceEnabled={plan.shell.voice?.enabled}
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
            q={tableQueryStates?.[tableKey]?.q}
            filterPlan={tableQueryStates?.[tableKey]?.filterPlan}
            total={tableTotals?.[tableKey]}
            onQueryChange={onTableQueryChange ? (patch) => onTableQueryChange(tableKey, patch) : undefined}
            onVisibleColumnsChange={onOverlayChange ? (visibleColumns) => onOverlayChange({ tables: { [tableKey]: { visibleColumns } } }) : undefined}
            onResetOverlay={onOverlayReset}
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
                payload={effectivePayload}
                tables={tables}
                tableQueryStates={tableQueryStates}
                tableTotals={tableTotals}
                onQueryChange={onTableQueryChange}
                onVisibleColumnsChange={onOverlayChange}
                onResetOverlay={onOverlayReset}
              />
            ),
          }))}
        />
      )}

      {formState && (
        <div
          className="sticky bottom-0 flex items-center justify-between gap-3 border-t bg-background px-4 py-3"
          data-testid="form-submit-bar"
          aria-live="polite"
        >
          <span className="text-sm text-muted-foreground">
            {formState.submitState === 'error' && formState.submitError
              ? `Fehler: ${formState.submitError}`
              : formState.dirtyState.isDirty
              ? 'Ungespeicherte Änderungen'
              : formState.submitState === 'success'
              ? 'Gespeichert'
              : ''}
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              className="rounded border px-3 py-1.5 text-sm hover:bg-muted disabled:opacity-50"
              disabled={!formState.dirtyState.isDirty || formState.submitState === 'submitting'}
              onClick={() => formState.resetForm()}
              data-testid="form-reset-btn"
            >
              Zurücksetzen
            </button>
            <button
              type="button"
              className="rounded bg-primary px-3 py-1.5 text-sm text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              disabled={!formState.canSubmit}
              onClick={() => { void formState.submit() }}
              data-testid="form-submit-btn"
              aria-busy={formState.submitState === 'submitting'}
            >
              {formState.submitState === 'submitting' ? 'Speichern…' : 'Speichern'}
            </button>
          </div>
        </div>
      )}
    </div>
    </FormStateContext.Provider>
  )
}

function RenderFromScreen({
  screen,
  payload,
  tables,
  allowedPermissions,
  onTabChange,
  onAction,
  entityId,
}: {
  screen: ScreenDefinition
  payload: Record<string, unknown>
  entityId?: string
  tables: Record<string, Record<string, unknown>[]>
  allowedPermissions: string[]
  onTabChange?: (_tabKey: string) => void
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
}): JSX.Element {
  const classes = layoutClasses(screen.layout?.preferredMode ?? 'desktopDense', screen.layout?.density ?? 'compact')
  const visibleActions = (screen.actions ?? []).filter(
    (action) => !action.permission || allowedPermissions.includes(action.permission),
  )
  const contextRail = screen.layout?.contextRail ?? 'combined'
  const contextRailSections = resolveContextRailSections(contextRail, screen.layout?.contextRailSections)
  const effectiveEntityId = entityId ?? String(payload.id ?? payload.entity_id ?? '')

  return (
    <div
      className={classes.root}
      data-screen-definition={screen.id}
      data-testid={`screen-${screen.id}`}
      data-layout-mode={screen.layout?.preferredMode ?? 'desktopDense'}
      data-mobile-layout={screen.layout?.mobileMode ?? 'mobileStack'}
      data-floorplan={screen.layout?.floorplan ?? 'objectPage'}
      data-density={screen.layout?.density ?? 'compact'}
      data-context-rail={contextRail}
      data-context-rail-sections={contextRailSections.join(',')}
      data-table-profile={screen.layout?.tableProfile ?? 'standard'}
    >
      <ActionBarRenderer
        domain={screen.domain}
        mode={screen.mode}
        title={screen.title}
        subtitle={screen.subtitle}
        actions={visibleActions}
        floorplan={screen.layout?.floorplan ?? 'objectPage'}
        density={screen.layout?.density ?? 'compact'}
        contextRail={contextRail}
        headerClassName={classes.header}
        touchTargetClass={classes.touchTarget}
        onAction={onAction}
        payload={payload}
      />

      <WorkflowPanelRenderer
        workflow={screen.workflow}
        contextRailSections={contextRailSections}
        entityType={screen.id}
        entityId={effectiveEntityId}
      />
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
            tableProfile: screen.layout?.tableProfile ?? 'standard',
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
  onOverlayChange,
  onOverlayReset,
  lookupBindings,
  formState,
  workflowState,
  entityId,
}: UniversalMaskRendererProps): JSX.Element {
  const payload = data

  if (plan) {
    return (
      <LookupBindingContext.Provider value={lookupBindings ?? {}}>
        <RenderFromPlan
          plan={plan}
          payload={payload}
          tables={tables}
          tableQueryStates={tableQueryStates}
          tableTotals={tableTotals}
          onTableQueryChange={onTableQueryChange}
          onOverlayChange={onOverlayChange}
          onOverlayReset={onOverlayReset}
          onTabChange={onTabChange}
          onAction={onAction}
          formState={formState}
          workflowState={workflowState}
          entityId={entityId}
        />
      </LookupBindingContext.Provider>
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
        entityId={entityId}
      />
    )
  }

  throw new Error('UniversalMaskRenderer requires plan or screen')
}
