import { useEffect, useRef, type KeyboardEvent as ReactKeyboardEvent } from 'react'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { RenderTablePlan } from '../render-plan/types'
import { formatCellValue } from './FastTableRenderer'
import { navigateRowRoute, resolveRowRoute } from './row-identity'

/**
 * Details der gewaehlten Zeile direkt unter der Tabelle. Die Tabelle bleibt
 * sichtbar, damit man Position fuer Position durchgehen kann, ohne einen
 * Dialog zu oeffnen und zu schliessen.
 */
export function RowDetailBand({
  table,
  row,
  onClose,
}: {
  table: RenderTablePlan
  row: Record<string, unknown>
  onClose: () => void
}): JSX.Element | null {
  const bandRef = useRef<HTMLElement>(null)
  const fields = table.rowDetail?.fields ?? []
  const titleColumn = table.columns[0]
  const title = titleColumn ? row[titleColumn.key] : undefined
  const heading = title == null || title === '' ? `Details ${table.label}` : `${titleColumn?.label} ${String(title)}`
  const canOpen = Boolean(resolveRowRoute(table.rowRouteTemplate, row))

  useEffect(() => {
    bandRef.current?.scrollIntoView?.({ block: 'nearest' })
  }, [row])

  if (fields.length === 0) return null

  function handleKeyDown(event: ReactKeyboardEvent<HTMLElement>): void {
    if (event.key !== 'Escape') return
    event.stopPropagation()
    onClose()
  }

  return (
    <section
      ref={bandRef}
      aria-label={heading}
      onKeyDown={handleKeyDown}
      className="mt-3 rounded-md border border-border bg-muted/40 p-4"
      data-testid={`row-detail-band-${table.key}`}
    >
      <div className="mb-3 flex items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-foreground">{heading}</h3>
        <div className="flex items-center gap-2">
          {canOpen ? (
            <Button type="button" variant="outline" className="min-h-touch" onClick={() => navigateRowRoute(table.rowRouteTemplate, row)}>
              In Vollansicht öffnen
            </Button>
          ) : null}
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="min-h-touch min-w-touch"
            onClick={onClose}
            aria-label="Details schließen"
            data-testid={`row-detail-close-${table.key}`}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>
      <dl className="grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2 xl:grid-cols-3">
        {fields.map((field) => (
          <div key={field.key} className="grid grid-cols-[minmax(7rem,10rem)_1fr] gap-2">
            <dt className="text-muted-foreground">{field.label}</dt>
            <dd className="min-w-0 break-words font-medium" data-testid={`row-detail-${table.key}-${field.key}`}>
              {formatCellValue(row[field.key] === '' ? null : row[field.key], field.renderKind)}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  )
}
