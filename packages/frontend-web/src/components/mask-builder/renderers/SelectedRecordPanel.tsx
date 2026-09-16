import { Button } from '@/components/ui/button'
import type { RenderTablePlan } from '../render-plan/types'
import { navigateRowRoute, resolveRowRoute } from './row-identity'

export function SelectedRecordPanel({
  table,
  row,
}: {
  table: RenderTablePlan
  row: Record<string, unknown>
}): JSX.Element {
  const canOpen = Boolean(resolveRowRoute(table.rowRouteTemplate, row))
  return (
    <div className="space-y-3" data-testid="selected-record-panel">
      <dl className="grid gap-2 text-sm">
        {table.columns.slice(0, 8).map((column) => {
          const value = row[column.key]
          return (
            <div key={column.key} className="grid grid-cols-[minmax(7rem,11rem)_1fr] gap-2">
              <dt className="text-muted-foreground">{column.label}</dt>
              <dd className="min-w-0 truncate font-medium">{value == null || value === '' ? '–' : String(value)}</dd>
            </div>
          )
        })}
      </dl>
      {canOpen ? (
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => navigateRowRoute(table.rowRouteTemplate, row)}
        >
          In Vollansicht öffnen
        </Button>
      ) : null}
    </div>
  )
}
