import { useEffect, useId, useRef, useState, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import type { ScreenColumnNavigation } from '../schema'

export interface NavigationColumn {
  key: string
  title: string
  content: ReactNode
}

/** Business navigation only. Audit/copilot rails are not navigation columns. */
export function ColumnLayoutRenderer({ pattern, columns }: {
  pattern: ScreenColumnNavigation
  columns: NavigationColumn[]
}): JSX.Element {
  const maximum = pattern === 'listDetailDetail' ? 3 : pattern === 'listDetail' ? 2 : 1
  const lastColumn = columns[columns.length - 1]
  if (!lastColumn || columns.length > maximum || new Set(columns.map(c => c.key)).size !== columns.length) {
    throw new Error('Column content must match the ScreenDefinition navigation contract and use unique keys')
  }
  const id = useId()
  const root = useRef<HTMLDivElement>(null)
  const [width, setWidth] = useState(0)
  const [activeKey, setActiveKey] = useState(lastColumn.key)
  const [fullScreen, setFullScreen] = useState(false)
  const trail = columns.map(c => c.key).join('\u001f')
  const previousTrail = useRef(trail)
  useEffect(() => {
    if (previousTrail.current !== trail) {
      const next = columns[columns.length - 1]
      if (next) setActiveKey(next.key)
      previousTrail.current = trail
    }
  }, [trail, columns])
  useEffect(() => {
    const element = root.current
    if (!element) return
    setWidth(element.getBoundingClientRect().width)
    if (typeof ResizeObserver === 'undefined') return
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width))
    observer.observe(element)
    return () => observer.disconnect()
  }, [])
  const active = Math.max(0, columns.findIndex(c => c.key === activeKey))
  // Available container width matters: the application shell consumes space too.
  const capacity = fullScreen || width < 900 ? 1 : width < 1440 ? 2 : 3
  const first = Math.max(0, active - capacity + 1)
  const visible = columns.filter((_, index) => index >= first && index <= active)
  const grid = visible.length === 3 ? 'minmax(260px, 1fr) minmax(360px, 1.4fr) minmax(320px, 1.2fr)'
    : visible.length === 2 ? 'minmax(280px, 1fr) minmax(400px, 1.6fr)' : 'minmax(0, 1fr)'
  return (
    <div ref={root} data-column-navigation={pattern} data-visible-columns={visible.length}>
      <nav aria-label="Ansichten" className="mb-2 flex flex-wrap items-center gap-2">
        {active > 0 && <Button type="button" variant="outline" size="sm" onClick={() => setActiveKey(columns[active - 1].key)}>Zurück zu {columns[active - 1].title}</Button>}
        {columns.map((column, index) => <Button key={column.key} type="button" size="sm"
          variant={index === active ? 'secondary' : 'ghost'} aria-current={index === active ? 'page' : undefined}
          aria-controls={`${id}-${index}`} onClick={() => setActiveKey(column.key)}>{column.title}</Button>)}
        {columns.length > 1 && <Button type="button" variant="outline" size="sm" aria-pressed={fullScreen}
          onClick={() => setFullScreen(value => !value)}>{fullScreen ? 'Geteilte Ansicht' : 'Vollansicht'}</Button>}
      </nav>
      <div className="grid gap-3" style={{ gridTemplateColumns: grid }}>
        {columns.map((column, index) => <section key={column.key} id={`${id}-${index}`}
          aria-label={column.title} hidden={!visible.includes(column)}
          className="min-w-0 overflow-auto" tabIndex={-1}>
          {column.content}
        </section>)}
      </div>
    </div>
  )
}
