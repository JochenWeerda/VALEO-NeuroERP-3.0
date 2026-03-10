import { type DragEvent, type ReactNode, useCallback, useRef, useState } from 'react'
import { clsx } from 'clsx'
import { type WidgetLayout } from '@/hooks/useDashboardLayout'
import { GripVertical, X, Maximize2, Minimize2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface DashboardGridProps {
  widgets: WidgetLayout[]
  isEditing: boolean
  onSwap: (sourceId: string, targetId: string) => void
  onRemove: (widgetId: string) => void
  onResize: (widgetId: string, w: number, h: number) => void
  renderWidget: (widget: WidgetLayout) => ReactNode
  columns?: number
}

interface WidgetWrapperProps {
  widget: WidgetLayout
  isEditing: boolean
  onDragStart: (e: DragEvent, widgetId: string) => void
  onDragOver: (e: DragEvent) => void
  onDrop: (e: DragEvent, widgetId: string) => void
  onRemove: (widgetId: string) => void
  onResize: (widgetId: string, w: number, h: number) => void
  children: ReactNode
}

function WidgetWrapper({
  widget,
  isEditing,
  onDragStart,
  onDragOver,
  onDrop,
  onRemove,
  onResize,
  children,
}: WidgetWrapperProps) {
  const [isDragOver, setIsDragOver] = useState(false)

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
    onDragOver(e)
  }

  const handleDragLeave = () => {
    setIsDragOver(false)
  }

  const handleDrop = (e: DragEvent) => {
    setIsDragOver(false)
    onDrop(e, widget.id)
  }

  const isExpanded = widget.w > 1 || widget.h > 1

  return (
    <div
      className={clsx(
        'relative rounded-xl border bg-card text-card-foreground shadow-sm transition-all',
        isEditing && 'cursor-move ring-2 ring-primary/20',
        isDragOver && isEditing && 'ring-4 ring-primary/50 scale-[1.02]',
        widget.w === 2 && 'col-span-2',
        widget.w === 3 && 'col-span-3',
        widget.w === 4 && 'col-span-4',
        widget.h === 2 && 'row-span-2',
        widget.h === 3 && 'row-span-3'
      )}
      draggable={isEditing}
      onDragStart={(e) => onDragStart(e, widget.id)}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {isEditing && (
        <div className="absolute -top-2 -right-2 z-10 flex gap-1">
          <Button
            variant="secondary"
            size="icon"
            className="h-6 w-6 rounded-full shadow-md"
            onClick={() =>
              onResize(widget.id, isExpanded ? 1 : 2, isExpanded ? 1 : 2)
            }
            title={isExpanded ? 'Verkleinern' : 'Vergrößern'}
          >
            {isExpanded ? (
              <Minimize2 className="h-3 w-3" />
            ) : (
              <Maximize2 className="h-3 w-3" />
            )}
          </Button>
          <Button
            variant="destructive"
            size="icon"
            className="h-6 w-6 rounded-full shadow-md"
            onClick={() => onRemove(widget.id)}
            title="Entfernen"
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      )}
      {isEditing && (
        <div className="absolute top-2 left-2 z-10 cursor-grab active:cursor-grabbing">
          <GripVertical className="h-4 w-4 text-muted-foreground" />
        </div>
      )}
      <div className={clsx('h-full', isEditing && 'pointer-events-none')}>
        {children}
      </div>
    </div>
  )
}

export function DashboardGrid({
  widgets,
  isEditing,
  onSwap,
  onRemove,
  onResize,
  renderWidget,
  columns = 4,
}: DashboardGridProps) {
  const draggedWidgetRef = useRef<string | null>(null)

  const handleDragStart = useCallback((e: DragEvent, widgetId: string) => {
    draggedWidgetRef.current = widgetId
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', widgetId)
  }, [])

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }, [])

  const handleDrop = useCallback(
    (e: DragEvent, targetId: string) => {
      e.preventDefault()
      const sourceId = draggedWidgetRef.current
      if (sourceId && sourceId !== targetId) {
        onSwap(sourceId, targetId)
      }
      draggedWidgetRef.current = null
    },
    [onSwap]
  )

  // Sort widgets by position for consistent rendering
  const sortedWidgets = [...widgets].sort((a, b) => {
    if (a.y !== b.y) return a.y - b.y
    return a.x - b.x
  })

  return (
    <div
      className={clsx(
        'grid gap-4 auto-rows-[minmax(120px,auto)]',
        columns === 2 && 'grid-cols-2',
        columns === 3 && 'grid-cols-3',
        columns === 4 && 'grid-cols-4',
        columns === 6 && 'grid-cols-6'
      )}
    >
      {sortedWidgets.map((widget) => (
        <WidgetWrapper
          key={widget.id}
          widget={widget}
          isEditing={isEditing}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onRemove={onRemove}
          onResize={onResize}
        >
          {renderWidget(widget)}
        </WidgetWrapper>
      ))}
    </div>
  )
}
