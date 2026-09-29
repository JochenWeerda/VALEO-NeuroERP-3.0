import type { ReactNode } from 'react'
import { Button } from '@/components/ui/button'

export type TouchStackField = {
  key: string
  label: ReactNode
  value: ReactNode
}

export type TouchStackAction = {
  key: string
  label: string
  onClick: () => void
  danger?: boolean
  disabled?: boolean
}

type TouchRecordStackProps<T> = {
  items: T[]
  getKey: (_item: T, _index: number) => string
  title: (_item: T) => ReactNode
  fields: (_item: T) => TouchStackField[]
  actions?: (_item: T) => TouchStackAction[]
  actionContent?: (_item: T) => ReactNode
  emptyMessage?: string
}

function isEmptyValue(value: ReactNode): boolean {
  if (value === null || value === undefined || value === false) return true
  if (typeof value === 'string' && value.trim().length === 0) return true
  return false
}

export function TouchRecordCard({
  title,
  fields,
  actionSlot,
  onOpen,
  selected = false,
}: {
  title: ReactNode
  fields: TouchStackField[]
  actionSlot?: ReactNode
  onOpen?: () => void
  selected?: boolean
}): JSX.Element {
  const visibleFields = fields.filter((field) => !isEmptyValue(field.value)).slice(0, 5)
  return (
    <div
      className={`rounded-(--radius) border border-border bg-card p-3 shadow-sm ${selected ? 'ring-2 ring-primary/40' : ''}`}
      role={onOpen ? 'button' : undefined}
      tabIndex={onOpen ? 0 : undefined}
      onClick={onOpen}
      onKeyDown={
        onOpen
          ? (event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault()
                onOpen()
              }
            }
          : undefined
      }
    >
      <div className="text-base font-semibold text-foreground">{title}</div>
      {visibleFields.length > 0 ? (
        <dl className="mt-2 grid grid-cols-2 gap-x-3 gap-y-2">
          {visibleFields.map((field) => (
            <div key={field.key} className="min-w-0">
              <dt className="text-2xs tracking-wide uppercase text-muted-foreground">{field.label}</dt>
              <dd className="truncate text-sm text-foreground">{field.value}</dd>
            </div>
          ))}
        </dl>
      ) : null}
      {actionSlot ? (
        <div
          className="mt-3 flex flex-wrap gap-2"
          onClick={(event) => event.stopPropagation()}
          onKeyDown={(event) => event.stopPropagation()}
        >
          {actionSlot}
        </div>
      ) : null}
    </div>
  )
}

/**
 * Listen auf Touch/Handy als Karten statt Horizontal-Scroll.
 * Desktop bleibt die Tabelle — keine vergrößerte Mobile-App.
 */
export function TouchRecordStack<T>({
  items,
  getKey,
  title,
  fields,
  actions,
  actionContent,
  emptyMessage = 'Keine Einträge vorhanden.',
}: TouchRecordStackProps<T>): JSX.Element {
  if (items.length === 0) {
    return <p className="py-8 text-center text-muted-foreground">{emptyMessage}</p>
  }

  return (
    <ul className="space-y-2">
      {items.map((item, index) => {
        const rowActions = actions?.(item) ?? []
        const renderedActions = actionContent?.(item)
        return (
          <li key={getKey(item, index)}>
            <TouchRecordCard
              title={title(item)}
              fields={fields(item)}
              actionSlot={
                renderedActions ??
                (rowActions.length > 0 ? (
                  <>
                    {rowActions.map((action) => (
                      <Button
                        key={action.key}
                        type="button"
                        variant="outline"
                        disabled={action.disabled}
                        onClick={(event) => {
                          event.stopPropagation()
                          action.onClick()
                        }}
                        className={`min-h-touch touch-manipulation ${action.danger ? 'text-status-error' : ''}`}
                      >
                        {action.label}
                      </Button>
                    ))}
                  </>
                ) : undefined)
              }
            />
          </li>
        )
      })}
    </ul>
  )
}
