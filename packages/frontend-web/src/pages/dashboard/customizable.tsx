import { useDashboardLayout } from '@/hooks/useDashboardLayout'
import { DashboardGrid, getWidgetComponent, widgetRegistry } from '@/components/dashboard'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Edit2, LayoutGrid, Plus, RotateCcw, Settings } from 'lucide-react'

export default function CustomizableDashboardPage() {
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
    const definition = widgetRegistry.find((w) => w.type === type)
    if (definition) {
      addWidget({
        type,
        x: 0,
        y: 99, // Will be placed at the end
        w: definition.defaultSize.w,
        h: definition.defaultSize.h,
        visible: true,
      })
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Personalisierte Übersicht Ihrer wichtigsten Kennzahlen
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant={isEditing ? 'default' : 'outline'}
            size="sm"
            onClick={() => setIsEditing(!isEditing)}
          >
            <Edit2 className="h-4 w-4 mr-2" />
            {isEditing ? 'Bearbeitung beenden' : 'Anpassen'}
          </Button>

          {isEditing && (
            <>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Widget hinzufügen
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuLabel>Widget-Typ wählen</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  {widgetRegistry.map((widget) => (
                    <DropdownMenuItem
                      key={widget.type}
                      onClick={() => handleAddWidget(widget.type)}
                    >
                      <span className="mr-2">{widget.icon}</span>
                      <div>
                        <div className="font-medium">{widget.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {widget.description}
                        </div>
                      </div>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>

              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Widgets
                  </Button>
                </SheetTrigger>
                <SheetContent>
                  <SheetHeader>
                    <SheetTitle>Widget-Einstellungen</SheetTitle>
                    <SheetDescription>
                      Widgets ein- oder ausblenden
                    </SheetDescription>
                  </SheetHeader>
                  <div className="mt-6 space-y-4">
                    {allWidgets.map((widget) => (
                      <div
                        key={widget.id}
                        className="flex items-center justify-between"
                      >
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
                  <div className="mt-8">
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={resetLayout}
                    >
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Layout zurücksetzen
                    </Button>
                  </div>
                </SheetContent>
              </Sheet>
            </>
          )}
        </div>
      </div>

      {isEditing && (
        <div className="p-4 bg-muted rounded-lg text-sm text-muted-foreground">
          <strong>Bearbeitungsmodus:</strong> Ziehen Sie Widgets per Drag & Drop,
          um sie neu anzuordnen. Verwenden Sie die Buttons, um Widgets zu
          vergrößern/verkleinern oder zu entfernen.
        </div>
      )}

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
