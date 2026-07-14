import { Clock3 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export type OperationalTimelineItem = {
  label: string
  detail?: string
  timestamp?: string | null
}

type OperationalTimelineProps = {
  title?: string
  items: OperationalTimelineItem[]
}

export function OperationalTimeline({
  title = 'Timeline',
  items,
}: OperationalTimelineProps): JSX.Element {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="text-sm text-slate-500">Noch keine Vorgangshistorie verfuegbar.</div>
        ) : (
          <div className="space-y-4">
            {items.map((item, index) => (
              <div key={`${item.label}-${index}`} className="flex gap-3">
                <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border bg-slate-50 text-slate-600">
                  <Clock3 className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-medium text-slate-950">{item.label}</div>
                  {item.detail ? <div className="text-sm text-slate-600">{item.detail}</div> : null}
                  {item.timestamp ? (
                    <div className="text-xs text-slate-500">{new Date(item.timestamp).toLocaleString('de-DE')}</div>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
