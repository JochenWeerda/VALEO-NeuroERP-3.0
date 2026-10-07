import { memo, useState } from 'react'
import type { RenderPlan } from '../render-plan/types'
import type { ScreenOverlay } from '../render-plan/overlay'
import type { TableQueryState } from '../runtime/types'
import { FastFormRenderer } from './FastFormRenderer'
import { FastTableRenderer } from './FastTableRenderer'
import { RowDetailBand } from './RowDetailBand'
import { layoutClasses, repeatsCaption } from './render-utils'
import { rowIdentity } from './row-identity'

export const FastTabRenderer = memo(function FastTabRenderer({
  plan,
  tabKey,
  payload,
  tables,
  tableQueryStates,
  tableTotals,
  onQueryChange,
  onVisibleColumnsChange,
  onResetOverlay,
  tableLoadError,
  onRetry,
  hideTableKeys,
  tableSelection,
  onRowAction,
}: {
  plan: RenderPlan
  tabKey: string
  payload: Record<string, unknown>
  tables: Record<string, Record<string, unknown>[]>
  tableQueryStates?: Record<string, TableQueryState>
  tableTotals?: Record<string, number>
  onQueryChange?: (tableKey: string, patch: Partial<TableQueryState>) => void
  onVisibleColumnsChange?: (patch: ScreenOverlay) => void | Promise<void>
  onResetOverlay?: () => void | Promise<void>
  tableLoadError?: (tableKey: string) => string | undefined
  onRetry?: () => void
  hideTableKeys?: Set<string>
  tableSelection?: Record<string, {
    selectedRowKey?: string
    onRowSelect?: (_row: Record<string, unknown>) => void
  }>
  onRowAction?: (_actionKey: string, _row: Record<string, unknown>) => void | Promise<void>
}): JSX.Element {
  const content = plan.tabContent[tabKey]
  const classes = layoutClasses(plan.shell.layoutMode, plan.shell.density)
  const [detailKeys, setDetailKeys] = useState<Record<string, string | undefined>>({})

  return (
    <div data-tab-key={tabKey}>
      <FastFormRenderer
        fieldKeys={content?.fieldKeys ?? []}
        fieldsByKey={plan.fieldsByKey}
        payload={payload}
        className={classes.fields}
        performance={plan.performance}
        voiceEnabled={plan.shell.voice?.enabled}
      />
      {(content?.tableKeys ?? []).map((tableKey) => {
        const tablePlan = plan.tablesByKey[tableKey]
        if (!tablePlan || hideTableKeys?.has(tableKey)) return null
        const rows = tables[tableKey] ?? []
        // An external selection (column layout) owns row clicks; the band only covers single-column pages.
        const detailBand = tablePlan.rowDetail && !tableSelection?.[tableKey]
        const detailKey = detailBand ? detailKeys[tableKey] : undefined
        const detailIndex = detailKey ? rows.findIndex((row, index) => rowIdentity(row, index) === detailKey) : -1
        const detailRow = detailIndex >= 0 ? rows[detailIndex] : undefined
        const selection = detailBand
          ? {
              selectedRowKey: detailRow ? detailKey : undefined,
              onRowSelect: (row: Record<string, unknown>) => {
                const key = rowIdentity(row, rows.indexOf(row))
                setDetailKeys((current) => ({ ...current, [tableKey]: current[tableKey] === key ? undefined : key }))
              },
            }
          : tableSelection?.[tableKey]
        return (
          <div key={tableKey}>
            <FastTableRenderer
              table={tablePlan}
              suppressHeading={repeatsCaption(tablePlan.label, plan.shell.title)}
              rows={rows}
              page={tableQueryStates?.[tableKey]?.page}
              sort={tableQueryStates?.[tableKey]?.sort}
              sortDir={tableQueryStates?.[tableKey]?.sortDir}
              q={tableQueryStates?.[tableKey]?.q}
              filterPlan={tableQueryStates?.[tableKey]?.filterPlan}
              total={tableTotals?.[tableKey]}
              onQueryChange={onQueryChange ? (patch) => onQueryChange(tableKey, patch) : undefined}
              onVisibleColumnsChange={onVisibleColumnsChange ? (visibleColumns) => onVisibleColumnsChange({ tables: { [tableKey]: { visibleColumns } } }) : undefined}
              onResetOverlay={onResetOverlay}
              errorMessage={tableLoadError?.(tableKey)}
              onRetry={onRetry}
              selectedRowKey={selection?.selectedRowKey}
              onRowSelect={selection?.onRowSelect}
              onRowAction={onRowAction}
            />
            {detailRow ? (
              <RowDetailBand
                table={tablePlan}
                row={detailRow}
                onClose={() => setDetailKeys((current) => ({ ...current, [tableKey]: undefined }))}
              />
            ) : null}
          </div>
        )
      })}
    </div>
  )
})
