import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Info } from 'lucide-react'
import type { ScreenSummaryItem } from '../schema'
import { renderValue } from './render-utils'

export function ScreenSummaryGrid({ items }: { items: ScreenSummaryItem[] }): JSX.Element | null {
  if (items.length === 0) return null

  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <Card key={item.key}>
          <CardContent className="p-4">
            <div className="flex items-start justify-between gap-2">
              <p className="min-w-0 text-xs text-muted-foreground">{item.label}</p>
              <SummaryDetails item={item} />
            </div>
            <p className="mt-1 text-lg font-semibold">{renderValue(item.value) || '-'}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

function SummaryDetails({ item }: { item: ScreenSummaryItem }): JSX.Element | null {
  const components = item.details?.components ?? []
  if (components.length === 0) return null

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="h-7 w-7 shrink-0"
          aria-label={`${item.label} Herleitung anzeigen`}
          data-testid={`summary-details-${item.key}`}
        >
          <Info className="h-4 w-4" />
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-80 p-3" data-testid={`summary-details-popover-${item.key}`}>
        <div className="space-y-2">
          <p className="text-sm font-semibold">{item.label}</p>
          <div className="space-y-2">
            {components.map((component) => (
              <div key={`${component.key}:${component.source_ref ?? ''}`} className="rounded border p-2">
                <div className="flex items-center justify-between gap-2 text-xs">
                  <span className="font-medium">{component.label ?? component.key}</span>
                  <span className="font-mono">{renderValue(component.co2e_kg ?? component.value) || '-'}</span>
                </div>
                {component.source_ref && (
                  <p className="mt-1 break-all text-xs text-muted-foreground" data-testid={`summary-source-ref-${component.key}`}>
                    {component.source_ref}
                  </p>
                )}
                {component.source && (
                  <p className="mt-1 text-xs text-muted-foreground">{component.source}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  )
}
