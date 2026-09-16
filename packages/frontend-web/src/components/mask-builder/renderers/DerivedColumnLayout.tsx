import { useEffect, useState } from 'react'
import { LazyTabs } from '@/components/ui/LazyTabs'
import type { RenderPlan } from '../render-plan/types'
import type { ScreenOverlay } from '../render-plan/overlay'
import type { TableQueryState } from '../runtime/types'
import type { ScreenColumnNavigation } from '../schema'
import { ColumnLayoutRenderer, type NavigationColumn } from './ColumnLayoutRenderer'
import { FastFormRenderer } from './FastFormRenderer'
import { FastTabRenderer } from './FastTabRenderer'
import { FastTableRenderer } from './FastTableRenderer'
import { layoutClasses } from './render-utils'
import { rowIdentity } from './row-identity'
import { SelectedRecordPanel } from './SelectedRecordPanel'

export function firstListTableKey(plan: RenderPlan): string | undefined {
  return plan.rootTableKeys[0] ?? Object.keys(plan.tablesByKey)[0]
}

export function firstChildTableKey(plan: RenderPlan, listKey: string): string | undefined {
  return Object.keys(plan.tablesByKey).find((key) => key !== listKey)
}

export function shouldDeriveColumns(plan: RenderPlan, explicitColumns?: NavigationColumn[]): boolean {
  if (explicitColumns && explicitColumns.length > 0) return false
  const pattern = plan.shell.columnNavigation
  if (pattern !== 'listDetail' && pattern !== 'listDetailDetail') return false
  return Boolean(firstListTableKey(plan))
}

function tabsExcludingListOnly(plan: RenderPlan, listTableKey: string) {
  return plan.visibleTabs.filter((tab) => {
    const content = plan.tabContent[tab.key]
    if (!content) return true
    const onlyList = content.tableKeys.length === 1
      && content.tableKeys[0] === listTableKey
      && content.fieldKeys.length === 0
    return !onlyList
  })
}

export function DerivedColumnLayout({
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
  activeTab,
  onActiveTabChange,
  tableLoadError,
  onRetry,
}: {
  plan: RenderPlan
  payload: Record<string, unknown>
  tables: Record<string, Record<string, unknown>[]>
  tableQueryStates?: Record<string, TableQueryState>
  tableTotals?: Record<string, number>
  onTableQueryChange?: (_tableKey: string, _patch: Partial<TableQueryState>) => void
  onOverlayChange?: (_patch: ScreenOverlay) => void | Promise<void>
  onOverlayReset?: () => void | Promise<void>
  onTabChange?: (_tabKey: string) => void
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  activeTab?: string
  onActiveTabChange?: (_tabKey: string) => void
  tableLoadError: (_tableKey: string) => string | undefined
  onRetry?: () => void
}): JSX.Element | null {
  const listKey = firstListTableKey(plan)
  const listTable = listKey ? plan.tablesByKey[listKey] : undefined
  const requested = plan.shell.columnNavigation ?? 'single'
  const childKey = listKey && requested === 'listDetailDetail' ? firstChildTableKey(plan, listKey) : undefined
  const childTable = childKey ? plan.tablesByKey[childKey] : undefined
  const pattern: ScreenColumnNavigation = requested === 'listDetailDetail' && childKey ? 'listDetailDetail' : 'listDetail'
  const listRows = listKey ? (tables[listKey] ?? []) : []
  const childRows = childKey ? (tables[childKey] ?? []) : []
  const [selectedListKey, setSelectedListKey] = useState<string | undefined>()
  const [selectedChildKey, setSelectedChildKey] = useState<string | undefined>()
  const classes = layoutClasses(plan.shell.layoutMode, plan.shell.density)
  const listFloor = plan.shell.floorplan === 'worklist' || plan.shell.floorplan === 'analyticalList'

  useEffect(() => {
    setSelectedListKey(undefined)
    setSelectedChildKey(undefined)
  }, [plan.screenId])

  useEffect(() => {
    if (listRows.length === 0) {
      setSelectedListKey(undefined)
      return
    }
    if (selectedListKey && listRows.some((row, index) => rowIdentity(row, index) === selectedListKey)) return
    setSelectedListKey(rowIdentity(listRows[0], 0))
  }, [listRows, selectedListKey])

  if (!listKey || !listTable) return null

  const selectedRow = listRows.find((row, index) => rowIdentity(row, index) === selectedListKey)
  const selectedChild = childRows.find((row, index) => rowIdentity(row, index) === selectedChildKey)
  const objectPayload = listFloor ? (selectedRow ?? {}) : payload
  const remainingTabs = tabsExcludingListOnly(plan, listKey)
  const hideTableKeys = new Set([listKey, ...(childKey ? [childKey] : [])])
  const listFields = listFloor ? plan.rootFieldKeys : []
  const objectFields = listFloor ? [] : plan.rootFieldKeys
  const objectTitle = selectedRow
    ? String(selectedRow.bezeichnung ?? selectedRow.name ?? selectedRow.nr ?? selectedRow.probe_nr ?? plan.shell.title)
    : plan.shell.title

  function renderTable(
    tableKey: string,
    options?: { selectedRowKey?: string; onRowSelect?: (row: Record<string, unknown>) => void },
  ): JSX.Element | null {
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
        onRowAction={onAction}
        errorMessage={tableLoadError(tableKey)}
        onRetry={onRetry}
        selectedRowKey={options?.selectedRowKey}
        onRowSelect={options?.onRowSelect}
      />
    )
  }

  const columns: NavigationColumn[] = [
    {
      key: 'list',
      title: listTable.label,
      content: (
        <div className="space-y-3">
          {listFields.length > 0 ? (
            <FastFormRenderer
              fieldKeys={listFields}
              fieldsByKey={plan.fieldsByKey}
              payload={payload}
              className={classes.fields}
              performance={plan.performance}
              voiceEnabled={plan.shell.voice?.enabled}
            />
          ) : null}
          {renderTable(listKey, {
            selectedRowKey: selectedListKey,
            onRowSelect: (row) => setSelectedListKey(rowIdentity(row) || undefined),
          })}
        </div>
      ),
    },
    {
      key: 'object',
      title: objectTitle,
      content: selectedRow ? (
        <div className="space-y-3">
          <SelectedRecordPanel table={listTable} row={selectedRow} />
          {objectFields.length > 0 ? (
            <FastFormRenderer
              fieldKeys={objectFields}
              fieldsByKey={plan.fieldsByKey}
              payload={objectPayload}
              className={classes.fields}
              performance={plan.performance}
              voiceEnabled={plan.shell.voice?.enabled}
            />
          ) : null}
          {childKey ? renderTable(childKey, {
            selectedRowKey: selectedChildKey,
            onRowSelect: (row) => setSelectedChildKey(rowIdentity(row) || undefined),
          }) : null}
          {remainingTabs.length > 0 ? (
            <LazyTabs
              value={activeTab}
              variant="register"
              onValueChange={(key) => { onActiveTabChange?.(key); onTabChange?.(key) }}
              tabs={remainingTabs.map((tab) => ({
                key: tab.key,
                label: tab.label,
                lazy: tab.lazy,
                keepAlive: tab.keepAlive,
                content: () => (
                  <FastTabRenderer
                    plan={plan}
                    tabKey={tab.key}
                    payload={objectPayload}
                    tables={tables}
                    tableQueryStates={tableQueryStates}
                    tableTotals={tableTotals}
                    onQueryChange={onTableQueryChange}
                    onVisibleColumnsChange={onOverlayChange}
                    onResetOverlay={onOverlayReset}
                    tableLoadError={tableLoadError}
                    onRetry={onRetry}
                    hideTableKeys={hideTableKeys}
                    tableSelection={{
                      [listKey]: {
                        selectedRowKey: selectedListKey,
                        onRowSelect: (row) => setSelectedListKey(rowIdentity(row) || undefined),
                      },
                    }}
                  />
                ),
              }))}
            />
          ) : null}
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">Datensatz in der Liste wählen.</p>
      ),
    },
  ]

  if (pattern === 'listDetailDetail') {
    columns.push({
      key: 'subobject',
      title: childTable?.label ?? 'Unterobjekt',
      content: selectedChild && childTable ? (
        <SelectedRecordPanel table={childTable} row={selectedChild} />
      ) : (
        <p className="text-sm text-muted-foreground">Unterobjekt in der Tabelle wählen.</p>
      ),
    })
  }

  return <ColumnLayoutRenderer pattern={pattern} columns={columns} source="derived" />
}
