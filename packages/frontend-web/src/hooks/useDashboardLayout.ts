import { useCallback, useState } from 'react'

export interface WidgetLayout {
  id: string
  type: string
  x: number
  y: number
  w: number
  h: number
  visible: boolean
}

export interface DashboardLayout {
  id: string
  name: string
  widgets: WidgetLayout[]
}

const STORAGE_KEY = 'valeo-dashboard-layouts'
const DEFAULT_LAYOUT_ID = 'default'

const defaultWidgets: WidgetLayout[] = [
  { id: 'kpi-revenue', type: 'kpi', x: 0, y: 0, w: 1, h: 1, visible: true },
  { id: 'kpi-orders', type: 'kpi', x: 1, y: 0, w: 1, h: 1, visible: true },
  { id: 'kpi-customers', type: 'kpi', x: 2, y: 0, w: 1, h: 1, visible: true },
  { id: 'kpi-stock', type: 'kpi', x: 3, y: 0, w: 1, h: 1, visible: true },
  { id: 'chart-sales', type: 'chart', x: 0, y: 1, w: 2, h: 2, visible: true },
  { id: 'chart-trend', type: 'chart', x: 2, y: 1, w: 2, h: 2, visible: true },
  { id: 'list-tasks', type: 'list', x: 0, y: 3, w: 2, h: 2, visible: true },
  { id: 'list-alerts', type: 'list', x: 2, y: 3, w: 2, h: 2, visible: true },
]

function loadLayouts(): DashboardLayout[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return []
    return JSON.parse(stored)
  } catch {
    return []
  }
}

function saveLayouts(layouts: DashboardLayout[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(layouts))
  } catch {
    // Storage full or unavailable
  }
}

export function useDashboardLayout(layoutId: string = DEFAULT_LAYOUT_ID) {
  const [layouts, setLayouts] = useState<DashboardLayout[]>(loadLayouts)
  const [isEditing, setIsEditing] = useState(false)

  const currentLayout = layouts.find((l) => l.id === layoutId) || {
    id: layoutId,
    name: 'Standard',
    widgets: defaultWidgets,
  }

  const updateLayout = useCallback(
    (widgets: WidgetLayout[]) => {
      setLayouts((prev) => {
        const existing = prev.find((l) => l.id === layoutId)
        let updated: DashboardLayout[]

        if (existing) {
          updated = prev.map((l) =>
            l.id === layoutId ? { ...l, widgets } : l
          )
        } else {
          updated = [...prev, { id: layoutId, name: 'Standard', widgets }]
        }

        saveLayouts(updated)
        return updated
      })
    },
    [layoutId]
  )

  const moveWidget = useCallback(
    (widgetId: string, newX: number, newY: number) => {
      const newWidgets = currentLayout.widgets.map((w) =>
        w.id === widgetId ? { ...w, x: newX, y: newY } : w
      )
      updateLayout(newWidgets)
    },
    [currentLayout.widgets, updateLayout]
  )

  const resizeWidget = useCallback(
    (widgetId: string, newW: number, newH: number) => {
      const newWidgets = currentLayout.widgets.map((w) =>
        w.id === widgetId ? { ...w, w: newW, h: newH } : w
      )
      updateLayout(newWidgets)
    },
    [currentLayout.widgets, updateLayout]
  )

  const toggleWidget = useCallback(
    (widgetId: string) => {
      const newWidgets = currentLayout.widgets.map((w) =>
        w.id === widgetId ? { ...w, visible: !w.visible } : w
      )
      updateLayout(newWidgets)
    },
    [currentLayout.widgets, updateLayout]
  )

  const addWidget = useCallback(
    (widget: Omit<WidgetLayout, 'id'>) => {
      const newWidget: WidgetLayout = {
        ...widget,
        id: `widget-${Date.now()}`,
      }
      updateLayout([...currentLayout.widgets, newWidget])
    },
    [currentLayout.widgets, updateLayout]
  )

  const removeWidget = useCallback(
    (widgetId: string) => {
      const newWidgets = currentLayout.widgets.filter((w) => w.id !== widgetId)
      updateLayout(newWidgets)
    },
    [currentLayout.widgets, updateLayout]
  )

  const resetLayout = useCallback(() => {
    updateLayout(defaultWidgets)
  }, [updateLayout])

  const swapWidgets = useCallback(
    (sourceId: string, targetId: string) => {
      const newWidgets = currentLayout.widgets.map((w) => {
        if (w.id === sourceId) {
          const target = currentLayout.widgets.find((t) => t.id === targetId)
          if (target) {
            return { ...w, x: target.x, y: target.y }
          }
        }
        if (w.id === targetId) {
          const source = currentLayout.widgets.find((s) => s.id === sourceId)
          if (source) {
            return { ...w, x: source.x, y: source.y }
          }
        }
        return w
      })
      updateLayout(newWidgets)
    },
    [currentLayout.widgets, updateLayout]
  )

  return {
    layout: currentLayout,
    widgets: currentLayout.widgets.filter((w) => w.visible),
    allWidgets: currentLayout.widgets,
    isEditing,
    setIsEditing,
    moveWidget,
    resizeWidget,
    toggleWidget,
    addWidget,
    removeWidget,
    resetLayout,
    swapWidgets,
  }
}
