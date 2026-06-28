import { memo } from 'react'
import type { RenderPlan } from '../render-plan/types'
import { FastFormRenderer } from './FastFormRenderer'
import { FastTableRenderer } from './FastTableRenderer'
import { layoutClasses } from './render-utils'

export const FastTabRenderer = memo(function FastTabRenderer({
  plan,
  tabKey,
  payload,
  tables,
}: {
  plan: RenderPlan
  tabKey: string
  payload: Record<string, unknown>
  tables: Record<string, Record<string, unknown>[]>
}): JSX.Element {
  const content = plan.tabContent[tabKey]
  const classes = layoutClasses(plan.shell.layoutMode)

  return (
    <div data-tab-key={tabKey}>
      <FastFormRenderer
        fieldKeys={content?.fieldKeys ?? []}
        fieldsByKey={plan.fieldsByKey}
        payload={payload}
        className={classes.fields}
        performance={plan.performance}
      />
      {(content?.tableKeys ?? []).map((tableKey) => {
        const tablePlan = plan.tablesByKey[tableKey]
        if (!tablePlan) return null
        return (
          <FastTableRenderer
            key={tableKey}
            table={tablePlan}
            rows={tables[tableKey] ?? []}
          />
        )
      })}
    </div>
  )
})
