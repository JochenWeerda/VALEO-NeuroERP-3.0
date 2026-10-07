import { SourceProposalRenderer } from './renderers/SourceProposalRenderer'
import { useEffect, useRef, useState, type KeyboardEvent as ReactKeyboardEvent } from 'react'
import { ColumnLayoutRenderer, type NavigationColumn } from './renderers/ColumnLayoutRenderer'
import { getValue, repeatsCaption } from './renderers/render-utils'
import { DerivedColumnLayout, shouldDeriveColumns } from './renderers/DerivedColumnLayout'
import { MessagePanelRenderer, type ScreenMessage } from './renderers/MessagePanelRenderer'
import { LazyTabs } from '@/components/ui/LazyTabs'
import { cn } from '@/lib/utils'
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
  ActionFooterRenderer,
  FastFormRenderer,
  FastSummaryRenderer,
  FastTabRenderer,
  FastTableRenderer,
  CalendarRenderer,
  TabContentRenderer,
  TileGridRenderer,
  TwinReadModelRenderer,
  ProcessRibbonRenderer,
  SectionPageRenderer,
  WorkflowPanelRenderer,
  layoutClasses,
  type PageSection,
} from './renderers'
import { UnsavedChangesGuard } from './renderers/UnsavedChangesGuard'
import { conditionRoot, dispatchScreenAction, type ScreenContext } from './governance/screen-context'

const PROCESS_FLOW_SECTION_KEY = 'belegfluss'

function documentIdentity(identityField: string | undefined, payload: Record<string, unknown>): string | undefined {
  if (!identityField) return undefined
  const aliases: Record<string, string[]> = {
    firma: ['firma', 'company_name', 'name', 'display_name'],
    company_name: ['company_name', 'firma', 'name', 'display_name'],
  }
  const keys = aliases[identityField] ?? [identityField]
  for (const key of keys) {
    const value = getValue(payload, key)
    if (value == null || typeof value === 'object') continue
    const text = String(value).trim()
    if (text) return text
  }
  return undefined
}

interface UniversalMaskRendererProps {
  columns?: NavigationColumn[]
  messages?: ScreenMessage[]
  onRetry?: () => void
  /** Preferred: pre-compiled render plan */
  region?: 'sourceProposals'
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
  /** Deep-link into a section or register (`?tab=`). */
  requestedSectionKey?: string
  /** Zeilenklick fuellt den Vorgangskopf. */
  onRowSelect?: (_row: Record<string, unknown>) => void
  /** Die Seite loest Speichern ueber deklarierte Aktionen aus. */
  hideFormSubmit?: boolean
  /** Daten, Policies und Befehle der Anwendung. Der Renderer ruft keine API auf. */
  screenContext?: ScreenContext
}

function matchesShortcut(event: ReactKeyboardEvent<HTMLElement>, shortcut: string): boolean {
  const parts = shortcut.toLowerCase().split('+').map((part) => part.trim()).filter(Boolean)
  const key = parts.at(-1)
  const wantsMod = parts.includes('mod')
  const wantsCtrl = parts.includes('ctrl')
  const wantsMeta = parts.includes('meta') || parts.includes('cmd')
  const wantsAlt = parts.includes('alt')
  const wantsShift = parts.includes('shift')
  if ((wantsMod && !(event.ctrlKey || event.metaKey)) || (wantsCtrl && !event.ctrlKey) || (wantsMeta && !event.metaKey)) return false
  if (event.altKey !== wantsAlt || event.shiftKey !== wantsShift) return false
  if (!wantsMod && !wantsCtrl && !wantsMeta && (event.ctrlKey || event.metaKey)) return false
  return event.key.toLowerCase() === key
}

function declaredAction(plan: RenderPlan, key: string): { key: string; command?: string } {
  const header = plan.actions.find((action) => action.key === key)
  if (header) return header
  for (const table of Object.values(plan.tablesByKey)) {
    const rowAction = table.rowActions?.find((action) => action.key === key)
    if (rowAction) return rowAction
  }
  return { key }
}

function handleScreenKeyDown(
  event: ReactKeyboardEvent<HTMLDivElement>,
  plan: RenderPlan,
  payload: Record<string, unknown>,
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>,
): void {
  if (!event.repeat) {
    const action = plan.actions.find((candidate) =>
      !candidate.disabled && candidate.keyboardShortcut && matchesShortcut(event, candidate.keyboardShortcut),
    )
    if (action) {
      event.preventDefault()
      void onAction?.(action.key, payload)
      return
    }
  }
  if (!plan.interaction.enterMovesFocus || event.key !== 'Enter' || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey) return
  const target = event.target
  if (!(target instanceof HTMLElement) || target instanceof HTMLTextAreaElement || target instanceof HTMLButtonElement) return
  const controls = Array.from(event.currentTarget.querySelectorAll<HTMLElement>(
    'input:not([disabled]), select:not([disabled]), textarea:not([disabled])',
  )).filter((control) => !control.closest('[hidden], [data-state="inactive"]'))
  const index = controls.indexOf(target)
  const next = index >= 0 ? controls[index + 1] : undefined
  if (next) {
    event.preventDefault()
    next.focus()
  }
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
  columns,
  messages = [],
  onRetry,
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
  requestedSectionKey,
  onRowSelect,
  hideFormSubmit,
  screenContext,
}: {
  columns?: NavigationColumn[]
  messages?: ScreenMessage[]
  onRetry?: () => void
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
  requestedSectionKey?: string
  onRowSelect?: (_row: Record<string, unknown>) => void
  hideFormSubmit?: boolean
  screenContext?: ScreenContext
}): JSX.Element {
  const container = useRef<HTMLDivElement>(null)
  const [activeTab, setActiveTab] = useState<string | undefined>(requestedSectionKey)
  const [locateField, setLocateField] = useState<string | undefined>(undefined)
  useEffect(() => {
    setActiveTab(requestedSectionKey)
    setLocateField(undefined)
  }, [plan.screenId, requestedSectionKey])
  useEffect(() => {
    if (!locateField) return
    let cancelled = false
    const focusField = (): boolean => {
      if (cancelled || !container.current) return false
      const field = Array.from(container.current.querySelectorAll<HTMLElement>('[data-meridian-field]'))
        .find((element) => (
          element.dataset.meridianField === locateField
          && !element.closest('[hidden], [data-state="inactive"]')
        ))
      if (!field) return false
      const control = field.querySelector<HTMLElement>('input, select, textarea, button, [tabindex]:not([tabindex="-1"])') ?? field
      if (control === field) field.tabIndex = -1
      control.focus()
      control.scrollIntoView?.({ block: 'nearest' })
      return document.activeElement === control
    }
    const outer = window.requestAnimationFrame(() => {
      if (focusField()) {
        setLocateField(undefined)
        return
      }
      window.requestAnimationFrame(() => {
        if (focusField()) setLocateField(undefined)
      })
    })
    const timer = window.setTimeout(() => {
      if (focusField()) setLocateField(undefined)
    }, 0)
    return () => {
      cancelled = true
      window.cancelAnimationFrame(outer)
      window.clearTimeout(timer)
    }
  }, [locateField, activeTab])
  const formMessages: ScreenMessage[] = Object.values(formState?.visibleFieldErrors ?? formState?.fieldErrors ?? {}).flat().map((error, index) => ({
    key: `field-${error.fieldKey}-${index}`, fieldKey: error.fieldKey, message: error.message,
    severity: error.severity === 'blocking' ? 'error' : error.severity,
  }))
  if (formState?.submitError) formMessages.push({ key: 'submit-error', severity: 'error', message: formState.submitError })
  const visibleMessages = [...messages, ...formMessages]
  function tableLoadError(tableKey: string): string | undefined {
    return visibleMessages.find((message) => message.key === `table-${tableKey}`)?.message
  }
  const classes = layoutClasses(plan.shell.layoutMode, plan.shell.density)
  const effectivePayload = formState ? formState.values : payload
  const effectiveEntityId = entityId ?? String(effectivePayload.id ?? effectivePayload.entity_id ?? '')
  const headerActions = plan.actions.filter((action) => action.zone === 'header')
  const footerActions = plan.actions.filter((action) => action.zone !== 'header')
  const deriveColumns = shouldDeriveColumns(plan, columns)
  const onePage = plan.shell.sectionNavigation === 'anchors' && !deriveColumns && !columns
  const boundRoot = conditionRoot(screenContext)
  const dispatchAction = (key: string, actionPayload: Record<string, unknown>) => (
    dispatchScreenAction(screenContext, declaredAction(plan, key), actionPayload, onAction)
  )

  const renderHeader = (condensed: boolean, sticky: boolean): JSX.Element => (
    <ActionBarRenderer
      domain={plan.shell.domain}
      mode={plan.shell.mode}
      title={plan.shell.title}
      subtitle={plan.shell.subtitle}
      identity={documentIdentity(plan.shell.identityField, effectivePayload)}
      actions={headerActions}
      floorplan={plan.shell.floorplan}
      density={plan.shell.density}
      contextRail={plan.shell.contextRail}
      headerClassName={cn(classes.header, sticky && 'sticky top-0 z-20')}
      touchTargetClass={classes.touchTarget}
      onAction={dispatchAction}
      payload={effectivePayload}
      conditionRoot={boundRoot}
      condensed={condensed}
    />
  )

  const renderTab = (tabKey: string): JSX.Element => (
    <FastTabRenderer
      plan={plan}
      tabKey={tabKey}
      payload={effectivePayload}
      tables={tables}
      tableQueryStates={tableQueryStates}
      tableTotals={tableTotals}
      onQueryChange={onTableQueryChange}
      onVisibleColumnsChange={onOverlayChange}
      onResetOverlay={onOverlayReset}
      tableLoadError={tableLoadError}
      onRetry={onRetry}
      onRowAction={dispatchAction}
    />
  )

  const pageSections: PageSection[] = onePage
    ? [
        ...plan.visibleTabs.map((tab) => ({
          key: tab.key,
          label: tab.label,
          lazy: tab.lazy,
          render: () => renderTab(tab.key),
        })),
        ...(plan.shell.processRibbon && !plan.visibleTabs.some((tab) => tab.key === PROCESS_FLOW_SECTION_KEY)
          ? [{
              key: PROCESS_FLOW_SECTION_KEY,
              label: 'Belegfluss',
              lazy: false,
              render: () => <ProcessRibbonRenderer ribbon={plan.shell.processRibbon ?? null} embedded />,
            }]
          : []),
      ]
    : []

  const statusAfterFields = plan.shell.statusPlacement === 'afterFields'
  const workflowNode = (
    <WorkflowPanelRenderer
      workflow={plan.workflow}
      workflowState={workflowState}
      contextRailSections={plan.shell.contextRailSections}
      entityType={plan.screenId}
      entityId={effectiveEntityId}
    />
  )

  const registerTabs = !deriveColumns && plan.visibleTabs.length > 0
    ? plan.visibleTabs.length === 1
      ? renderTab(plan.visibleTabs[0].key)
      : (
        <LazyTabs
          value={activeTab}
          variant="register"
          onValueChange={(key) => { setActiveTab(key); onTabChange?.(key) }}
          tabs={plan.visibleTabs.map((tab) => ({
            key: tab.key,
            label: tab.label,
            lazy: tab.lazy,
            keepAlive: tab.keepAlive,
            content: () => renderTab(tab.key),
          }))}
        />
      )
    : null

  const pageBody = (
    <>
      <MessagePanelRenderer messages={visibleMessages} onRetry={onRetry}
        onLocateField={(key) => {
          const field = plan.fieldsByKey[key]
          if (field?.tabKey) setActiveTab(field.tabKey)
          setLocateField(key)
        }} />
      {columns ? <ColumnLayoutRenderer pattern={plan.shell.columnNavigation ?? 'single'} columns={columns} source="explicit" /> : null}
      {deriveColumns ? (
        <DerivedColumnLayout
          plan={plan}
          payload={effectivePayload}
          tables={tables}
          tableQueryStates={tableQueryStates}
          tableTotals={tableTotals}
          onTableQueryChange={onTableQueryChange}
          onOverlayChange={onOverlayChange}
          onOverlayReset={onOverlayReset}
          onTabChange={onTabChange}
          onAction={dispatchAction}
          activeTab={activeTab}
          onActiveTabChange={setActiveTab}
          tableLoadError={tableLoadError}
          onRetry={onRetry}
        />
      ) : null}
      {plan.shell.processRibbon && !onePage ? <ProcessRibbonRenderer ribbon={plan.shell.processRibbon} /> : null}

      {statusAfterFields ? null : workflowNode}
      {!statusAfterFields && plan.shell.summaryPlacement === 'header' ? <FastSummaryRenderer items={plan.summaryItems} /> : null}
      <TileGridRenderer tiles={plan.tiles} />
      <CalendarRenderer calendar={plan.calendar} />
      <TwinReadModelRenderer twin={plan.twin} />
      {plan.sourceProposals ? <SourceProposalRenderer context={effectivePayload[plan.sourceProposals.contextKey]} /> : null}

      {deriveColumns ? null : (
        <>
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
            onRowAction={dispatchAction}
            onRowSelect={onRowSelect}
            errorMessage={tableLoadError(tableKey)}
            onRetry={onRetry}
            suppressHeading={repeatsCaption(tablePlan.label, plan.shell.title)}
          />
        )
      })}
      {statusAfterFields && !onePage ? registerTabs : null}
      {statusAfterFields ? <FastSummaryRenderer items={plan.summaryItems} /> : null}
      {statusAfterFields ? workflowNode : null}

        </>
      )}
    </>
  )

  return (
    <FormStateContext.Provider value={formState}>
    <div
      ref={container}
      className={classes.root}
      onKeyDown={(event) => handleScreenKeyDown(event, plan, effectivePayload, dispatchAction)}
      data-screen-definition={plan.screenId}
      data-testid={`screen-${plan.screenId}`}
      data-layout-mode={plan.shell.layoutMode}
      data-mobile-layout={plan.shell.mobileMode}
      data-render-plan-cache-key={plan.cacheKey}
      data-floorplan={plan.shell.floorplan}
      data-column-navigation={plan.shell.columnNavigation ?? 'single'}
      data-section-navigation={onePage ? 'anchors' : 'tabs'}
      data-density={plan.shell.density}
      data-context-rail={plan.shell.contextRail}
      data-context-rail-sections={plan.shell.contextRailSections.join(',')}
      data-table-profile={plan.shell.tableProfile}
    >
      {onePage ? (
        <SectionPageRenderer
          header={(condensed) => renderHeader(condensed, false)}
          sections={pageSections}
          requestedSectionKey={activeTab}
          onRequestHandled={() => setActiveTab(undefined)}
        >
          {pageBody}
        </SectionPageRenderer>
      ) : (
        <>
          {renderHeader(false, plan.shell.stickyHeader)}
          {pageBody}
          {statusAfterFields ? null : registerTabs}
        </>
      )}

      {!statusAfterFields && plan.shell.summaryPlacement === 'footer' ? <FastSummaryRenderer items={plan.summaryItems} /> : null}
      <ActionFooterRenderer
        actions={footerActions}
        sticky={plan.shell.stickyFooter && !formState}
        payload={effectivePayload}
        conditionRoot={boundRoot}
        onAction={dispatchAction}
      />

      {formState && !hideFormSubmit && (
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
      {formState?.dirtyState.isDirty ? <UnsavedChangesGuard /> : null}
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
  screenContext,
}: {
  screen: ScreenDefinition
  payload: Record<string, unknown>
  entityId?: string
  tables: Record<string, Record<string, unknown>[]>
  allowedPermissions: string[]
  onTabChange?: (_tabKey: string) => void
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  screenContext?: ScreenContext
}): JSX.Element {
  const classes = layoutClasses(screen.layout?.preferredMode ?? 'desktopDense', screen.layout?.density ?? 'compact')
  const boundRoot = conditionRoot(screenContext)
  const dispatchAction = (key: string, actionPayload: Record<string, unknown>) => {
    const declared = (screen.actions ?? []).find((action) => action.key === key)
      ?? (screen.tables ?? []).flatMap((table) => table.rowActions ?? []).find((action) => action.key === key)
    return dispatchScreenAction(screenContext, declared ?? { key }, actionPayload, onAction)
  }
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
        identity={documentIdentity(screen.identityField, payload)}
        actions={visibleActions}
        floorplan={screen.layout?.floorplan ?? 'objectPage'}
        density={screen.layout?.density ?? 'compact'}
        contextRail={contextRail}
        headerClassName={classes.header}
        touchTargetClass={classes.touchTarget}
        onAction={dispatchAction}
        payload={payload}
        conditionRoot={boundRoot}
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
              priority: column.priority,
            })),
            pageSize: Math.min(table.pageSize ?? 25, 50),
            virtualized: table.virtualized ?? true,
            rowHeight: table.rowHeight ?? 52,
            serverPagination: table.serverPagination ?? true,
            tableProfile: screen.layout?.tableProfile ?? 'standard',
          }}
          rows={tables[table.key] ?? []}
          suppressHeading={repeatsCaption(table.label, screen.title)}
        />
      ))}

      {screen.tabs && screen.tabs.length === 1 && (
        <TabContentRenderer
          fields={screen.tabs[0].fields}
          tables={screen.tabs[0].tables}
          fieldsClassName={classes.fields}
          payload={payload}
          tableRows={tables}
          screenTitle={screen.title}
        />
      )}
      {screen.tabs && screen.tabs.length > 1 && (
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
                screenTitle={screen.title}
              />
            ),
          }))}
        />
      )}
    </div>
  )
}

export function UniversalMaskRenderer({
  columns,
  messages,
  onRetry,
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
  region,
  requestedSectionKey,
  onRowSelect,
  hideFormSubmit,
  screenContext,
}: UniversalMaskRendererProps): JSX.Element {
  const payload = data

  if (region === 'sourceProposals') {
    const definition = plan?.sourceProposals ?? screen?.sourceProposals
    return <SourceProposalRenderer context={definition ? payload[definition.contextKey] : undefined} />
  }

  if (plan) {
    return (
      <LookupBindingContext.Provider value={lookupBindings ?? {}}>
        <RenderFromPlan
          columns={columns}
          messages={messages}
          onRetry={onRetry}
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
          requestedSectionKey={requestedSectionKey}
          onRowSelect={onRowSelect}
          hideFormSubmit={hideFormSubmit}
          screenContext={screenContext}
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
        screenContext={screenContext}
      />
    )
  }

  throw new Error('UniversalMaskRenderer requires plan or screen')
}
