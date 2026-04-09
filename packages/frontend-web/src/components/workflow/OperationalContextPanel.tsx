import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export type OperationalContextSection = {
  title: string
  items: Array<{ label: string; value: string }>
}

type OperationalContextPanelProps = {
  title?: string
  sections: OperationalContextSection[]
}

export function OperationalContextPanel({
  title = 'Objektkontext',
  sections,
}: OperationalContextPanelProps): JSX.Element {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {sections.map((section) => (
          <div key={section.title} className="space-y-2 rounded-xl border bg-slate-50/70 p-3">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">{section.title}</div>
            <div className="space-y-2">
              {section.items.map((item) => (
                <div key={`${section.title}-${item.label}`} className="flex items-start justify-between gap-4 text-sm">
                  <span className="text-slate-600">{item.label}</span>
                  <span className="text-right font-medium text-slate-950">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}
