import { Card, CardContent } from '@/components/ui/card'
import type { ScreenSummaryItem } from '../schema'
import { renderValue } from './render-utils'

export function ScreenSummaryGrid({ items }: { items: ScreenSummaryItem[] }): JSX.Element | null {
  if (items.length === 0) return null

  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <Card key={item.key}>
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">{item.label}</p>
            <p className="mt-1 text-lg font-semibold">{renderValue(item.value) || '-'}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
