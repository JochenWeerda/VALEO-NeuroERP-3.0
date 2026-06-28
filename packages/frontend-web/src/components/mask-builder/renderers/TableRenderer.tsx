import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { VirtualDataTable } from '@/components/ui/VirtualDataTable'
import type { ScreenTableDefinition } from '../schema'

export function TableRenderer({
  table,
  rows,
}: {
  table: ScreenTableDefinition
  rows: Record<string, unknown>[]
}): JSX.Element {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{table.label}</CardTitle>
      </CardHeader>
      <CardContent>
        <VirtualDataTable
          data={rows}
          rowHeight={table.rowHeight ?? 52}
          columns={table.columns.map((column) => ({
            key: column.key,
            label: column.label,
            width: column.width,
            numeric: column.numeric,
            render: column.render,
          }))}
        />
      </CardContent>
    </Card>
  )
}
