import { useState } from 'react'
import { useDashboardLayout } from '@/hooks/useDashboardLayout'
import { DashboardGrid, getWidgetComponent, widgetRegistry } from '@/components/dashboard'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Edit2, LayoutGrid, Plus, RotateCcw, Settings } from 'lucide-react'

export default function CustomizableDashboardPage() {
  const [showAddPanel, setShowAddPanel] = useState(false)
  const [showWidgetPanel, setShowWidgetPanel] = useState(false)
  const {
    widgets,
    allWidgets,
    isEditing,
    setIsEditing,
    swapWidgets,
    removeWidget,
    resizeWidget,
    toggleWidget,
    addWidget,
    resetLayout,
  } = useDashboardLayout()

  const handleAddWidget = (type: string) => {
    const definition = widgetRegistry.find((widget) => widget.type === type)
    if (!definition) {
      return
    }
    addWidget({
      type,
      x: 0,
      y: 99,
      w: definition.defaultSize.w,
      h: definition.defaultSize.h,
      visible: true,
    })
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">Personalisierte Uebersicht Ihrer wichtigsten Kennzahlen</p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant={isEditing ? 'default' : 'outline'}
            size="sm"
            onClick={() => setIsEditing(!isEditing)}
          >
            <Edit2 className="mr-2 h-4 w-4" />
            {isEditing ? 'Bearbeitung beenden' : 'Anpassen'}
          </Button>

          {isEditing ? (
            <>
              <Button variant="outline" size="sm" onClick={() => setShowAddPanel((prev) => !prev)}>
                <Plus className="mr-2 h-4 w-4" />
                Widget hinzufuegen
              </Button>
              <Button variant="outline" size="sm" onClick={() => setShowWidgetPanel((prev) => !prev)}>
                <Settings className="mr-2 h-4 w-4" />
                Widgets
              </Button>
            </>
          ) : null}
        </div>
      </div>

      {isEditing && showAddPanel ? (
        <section className="rounded-lg border bg-card p-4">
          <div className="mb-3 text-sm font-medium">Widget-Typ waehlen</div>
          <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
            {widgetRegistry.map((widget) => (
              <button
                key={widget.type}
                type="button"
                onClick={() => {
                  handleAddWidget(widget.type)
                  setShowAddPanel(false)
                }}
                className="rounded-md border p-3 text-left transition-colors hover:bg-accent"
              >
                <div className="mb-1 flex items-center gap-2">
                  <span>{widget.icon}</span>
                  <span className="font-medium">{widget.name}</span>
                </div>
                <div className="text-xs text-muted-foreground">{widget.description}</div>
              </button>
            ))}
          </div>
        </section>
      ) : null}

      {isEditing && showWidgetPanel ? (
        <section className="rounded-lg border bg-card p-4">
          <div className="mb-1 text-base font-semibold">Widget-Einstellungen</div>
          <div className="mb-4 text-sm text-muted-foreground">Widgets ein- oder ausblenden</div>
          <div className="space-y-4">
            {allWidgets.map((widget) => (
              <div key={widget.id} className="flex items-center justify-between">
                <Label htmlFor={widget.id} className="flex items-center gap-2">
                  <LayoutGrid className="h-4 w-4" />
                  <span>{widget.id}</span>
                </Label>
                <Switch
                  id={widget.id}
                  checked={widget.visible}
                  onCheckedChange={() => toggleWidget(widget.id)}
                />
              </div>
            ))}
          </div>
          <div className="mt-6">
            <Button variant="outline" className="w-full" onClick={resetLayout}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Layout zuruecksetzen
            </Button>
          </div>
        </section>
      ) : null}

      {isEditing ? (
        <div className="rounded-lg bg-muted p-4 text-sm text-muted-foreground">
          <strong>Bearbeitungsmodus:</strong> Ziehen Sie Widgets per Drag and Drop, um sie neu
          anzuordnen. Verwenden Sie die Buttons, um Widgets zu vergroessern, zu verkleinern oder
          zu entfernen.
        </div>
      ) : null}

      <DashboardGrid
        widgets={widgets}
        isEditing={isEditing}
        onSwap={swapWidgets}
        onRemove={removeWidget}
        onResize={resizeWidget}
        renderWidget={(widget) => {
          const WidgetComponent = getWidgetComponent(widget.type)
          return <WidgetComponent widget={widget} />
        }}
      />
    </div>
  )
}
