import { memo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { VirtualDataTable } from '@/components/ui/VirtualDataTable'
import type { RenderTablePlan } from '../render-plan/types'

export const FastTableRenderer = memo(function FastTableRenderer({
  table,
  rows,
}: {
  table: RenderTablePlan
  rows: Record<string, unknown>[]
}): JSX.Element {
  const visibleRows = rows.slice(0, table.pageSize)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{table.label}</CardTitle>
      </CardHeader>
      <CardContent>
        <VirtualDataTable
          data={visibleRows}
          rowHeight={table.rowHeight}
          columns={table.columns.map((column) => ({
            key: column.key,
            label: column.label,
            width: column.width,
            numeric: column.numeric,
          }))}
        />
      </CardContent>
    </Card>
  )
})
