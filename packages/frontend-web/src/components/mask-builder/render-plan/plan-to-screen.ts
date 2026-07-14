import type { ScreenDefinition, ScreenFieldDefinition, ScreenTabDefinition } from '../schema'
import type { RenderPlan } from './types'

/** Übergangshilfe: RenderPlan → ScreenDefinition für Legacy-Renderer und Tests. */
export function renderPlanToScreenDefinition(plan: RenderPlan): ScreenDefinition {
  const fieldsFromKeys = (keys: string[]): ScreenFieldDefinition[] =>
    keys
      .map((key) => plan.fieldsByKey[key])
      .filter(Boolean)
      .map((field) => ({
        key: field.key,
        label: field.label,
        type: field.componentKind,
        required: field.required,
        readOnly: field.readOnly,
        placeholder: field.placeholder,
        helpText: field.helpText,
        options: field.options,
        dataSourceKey: field.dataSourceKey,
        minSearchChars: field.minSearchChars,
        renderHint: field.renderHint,
      }))

  const tabs: ScreenTabDefinition[] = plan.visibleTabs.map((tab) => ({
    key: tab.key,
    label: tab.label,
    lazy: tab.lazy,
    keepAlive: tab.keepAlive,
    fields: fieldsFromKeys(plan.tabContent[tab.key]?.fieldKeys ?? []),
    tables: (plan.tablesByTab[tab.key] ?? []).map((table) => ({
      key: table.key,
      label: table.label,
      columns: table.columns,
      dataSourceKey: table.dataSourceKey,
      pageSize: table.pageSize,
      virtualized: table.virtualized,
      rowHeight: table.rowHeight,
      serverPagination: table.serverPagination,
      rowRouteTemplate: table.rowRouteTemplate,
    })),
  }))

  return {
    schemaVersion: 1,
    id: plan.screenId,
    domain: plan.shell.domain,
    mode: plan.shell.mode,
    title: plan.shell.title,
    subtitle: plan.shell.subtitle,
    summaryEndpoint: plan.shell.summaryEndpoint,
    summary: plan.summaryItems,
    fields: fieldsFromKeys(plan.rootFieldKeys),
    tabs,
    tables: plan.rootTableKeys
      .map((key) => plan.tablesByKey[key])
      .filter(Boolean)
      .map((table) => ({
        key: table.key,
        label: table.label,
        columns: table.columns,
        dataSourceKey: table.dataSourceKey,
        pageSize: table.pageSize,
        virtualized: table.virtualized,
        rowHeight: table.rowHeight,
        serverPagination: table.serverPagination,
        rowRouteTemplate: table.rowRouteTemplate,
      })),
    actions: plan.actions.map((action) => ({
      key: action.key,
      label: action.label,
      kind: action.kind,
      disabled: action.disabled,
    })),
    workflow: plan.workflow,
    layout: {
      preferredMode: plan.shell.layoutMode,
      mobileMode: plan.shell.mobileMode,
      touchTargetPx: plan.shell.touchTargetPx,
    },
    performance: {
      initialPayloadBudgetKb: plan.performance.initialPayloadBudgetKb,
      requiresLazyTabs: plan.performance.requiresLazyTabs,
      requiresVirtualTables: plan.performance.requiresVirtualTables,
      lookupMinChars: plan.performance.lookupMinChars,
    },
  }
}
