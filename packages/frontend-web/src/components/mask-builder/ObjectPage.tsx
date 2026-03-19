import React, { useState, useEffect, useRef } from 'react'
import { useForm, Controller } from 'react-hook-form'
// Badge import removed - not used
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { AlertTriangle, Loader2, Save, X } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { MaskConfig, Tab as MaskTab, Field } from './types'
import { createMaskResolver, getFieldsFromMaskConfig } from './validation'
import { useKeyboardShortcuts, buildCoreMaskShortcuts } from '@/hooks/useKeyboardShortcuts'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'

interface ObjectPageProps {
  config: MaskConfig
  data?: any
  onChange?: (_data: any) => void
  onSave: (_data: any) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  /** When provided, toolbar action buttons call this with (actionKey, formData) instead of action.onClick */
  onAction?: (_actionKey: string, _formData: any) => void | Promise<void>
  /** Key of the action currently loading (disables that button and shows spinner) */
  loadingActionKey?: string | null
}

const ObjectPage: React.FC<ObjectPageProps> = ({
  config,
  data,
  onChange,
  onSave,
  onCancel,
  isLoading = false,
  onAction,
  loadingActionKey = null
}) => {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState(config.tabs[0]?.key || '')
  const [activatedTabs, setActivatedTabs] = useState<Set<string>>(
    () => new Set(config.tabs[0]?.key ? [config.tabs[0].key] : []),
  )
  const [isDirty, setIsDirty] = useState(false)
  const isInternalUpdateRef = useRef(false)

  const handleTabChange = (tabKey: string) => {
    setActiveTab(tabKey)
    setActivatedTabs((prev) => {
      if (prev.has(tabKey)) return prev
      const next = new Set(prev)
      next.add(tabKey)
      return next
    })
  }

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    reset
  } = useForm({
    resolver: createMaskResolver(getFieldsFromMaskConfig(config)),
    defaultValues: data || {}
  })

  // Watch for changes to mark form as dirty
  useEffect(() => {
    const subscription = watch((value) => {
      setIsDirty(true)
      if (onChange) {
        isInternalUpdateRef.current = true
        onChange(value)
      }
    })
    return () => subscription.unsubscribe()
  }, [watch, onChange])

  // Reset dirty state when data changes
  useEffect(() => {
    if (!data) {
      return
    }
    if (isInternalUpdateRef.current) {
      isInternalUpdateRef.current = false
      return
    }

    reset(data)
    setIsDirty(false)
  }, [data, reset])

  // Keyboard shortcuts: Ctrl+S → Speichern, Escape → Abbrechen (Gap 023)
  const kbShortcuts = buildCoreMaskShortcuts({
    onSave: () => { void handleSubmit(onSubmit)() },
    onCancel: onCancel,
    isSaveDisabled: isSubmitting || !isDirty,
  })
  useKeyboardShortcuts(kbShortcuts)

  const onSubmit = async (formData: any) => {
    try {
      await onSave(formData)
      setIsDirty(false)
      toast({
        title: "Erfolgreich gespeichert",
        description: "Die Daten wurden erfolgreich gespeichert.",
      })
    } catch (error) {
      toast({
        title: "Fehler beim Speichern",
        description: "Beim Speichern ist ein Fehler aufgetreten.",
        variant: "destructive",
      })
    }
  }

  const renderField = (field: Field) => {
    const error = errors[field.name]?.message as string

    return (
      <div key={field.name} className="space-y-2">
        <Label htmlFor={field.name}>
          {field.label}
          {field.required && <span className="text-red-500 ml-1">*</span>}
        </Label>

        <Controller
          name={field.name}
          control={control}
          render={({ field: controllerField }) => {
            switch (field.type) {
              case 'text':
              case 'number':
                return (
                  <Input
                    {...controllerField}
                    id={field.name}
                    type={field.type}
                    placeholder={field.placeholder}
                    readOnly={field.readonly}
                    className={error ? 'border-red-500' : ''}
                  />
                )

              case 'textarea':
                return (
                  <Textarea
                    {...controllerField}
                    id={field.name}
                    placeholder={field.placeholder}
                    readOnly={field.readonly}
                    className={error ? 'border-red-500' : ''}
                  />
                )

              case 'boolean':
                return (
                  <div className="flex items-center space-x-2">
                    <input
                      {...controllerField}
                      id={field.name}
                      type="checkbox"
                      checked={controllerField.value || false}
                      className="h-4 w-4"
                    />
                    <Label htmlFor={field.name} className="text-sm">
                      {field.label}
                    </Label>
                  </div>
                )

              case 'select': {
                const selectField = field as any
                return (
                  <NativeSelect
                    id={field.name}
                    value={String(controllerField.value ?? '')}
                    onValueChange={controllerField.onChange}
                    options={selectField.options ?? []}
                    placeholder={field.placeholder}
                    disabled={field.readonly}
                    className={error ? 'border-red-500' : ''}
                  />
                )
              }

              case 'date':
                return (
                  <Input
                    {...controllerField}
                    id={field.name}
                    type="date"
                    readOnly={field.readonly}
                    className={error ? 'border-red-500' : ''}
                  />
                )

              case 'datetime':
                return (
                  <Input
                    {...controllerField}
                    id={field.name}
                    type="datetime-local"
                    readOnly={field.readonly}
                    className={error ? 'border-red-500' : ''}
                  />
                )

              default:
                return (
                  <Input
                    {...controllerField}
                    id={field.name}
                    placeholder={field.placeholder}
                    readOnly={field.readonly}
                    className={error ? 'border-red-500' : ''}
                  />
                )
            }
          }}
        />

        {error && (
          <p className="text-sm text-red-600 flex items-center gap-1">
            <AlertTriangle className="h-3 w-3" />
            {error}
          </p>
        )}

        {field.helpText && (
          <p className="text-xs text-muted-foreground">{field.helpText}</p>
        )}
      </div>
    )
  }

  const renderTabContent = (tab: any) => {
    const layout = tab.layout || 'grid'
    const columns = tab.columns || 2

    return (
      <div
        className={
          layout === 'grid'
            ? `grid gap-4 md:grid-cols-${columns}`
            : 'space-y-4'
        }
      >
        {tab.fields.map(renderField)}
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Laden...</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col">
    <div className="flex-1 space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{config.title}</h1>
          {config.subtitle && (
            <p className="text-muted-foreground">{config.subtitle}</p>
          )}
        </div>
        <div className="flex gap-2">
          {config.actions.map(action => {
            const isThisLoading = loadingActionKey != null && action.key === loadingActionKey
            return (
              <Button
                key={action.key}
                variant={action.type === 'primary' ? 'default' : 'outline'}
                onClick={() => {
                  if (onAction) {
                    void Promise.resolve(onAction(action.key, watch())).catch(() => { })
                  } else {
                    action.onClick?.()
                  }
                }}
                disabled={action.disabled || isThisLoading}
                className="gap-2"
              >
                {isThisLoading && <Loader2 className="h-4 w-4 animate-spin" />}
                {!isThisLoading && action.icon && <span className="text-sm">{action.icon}</span>}
                {action.label}
              </Button>
            )
          })}
          <Button variant="outline" onClick={onCancel} className="gap-2">
            <X className="h-4 w-4" />
            Abbrechen
          </Button>
          <Button
            onClick={handleSubmit(onSubmit)}
            disabled={isSubmitting || !isDirty}
            className="gap-2"
          >
            {isSubmitting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            Speichern
          </Button>
        </div>
      </div>

      {/* Dirty Warning */}
      {isDirty && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">
                Ungespeicherte Änderungen
              </span>
            </div>
            <p className="mt-1 text-orange-800">
              Sie haben ungespeicherte Änderungen. Vergessen Sie nicht zu speichern.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <Tabs value={activeTab} onValueChange={handleTabChange}>
          <TabsList className="grid w-full grid-cols-4">
            {config.tabs.map(tab => (
              <TabsTrigger key={tab.key} value={tab.key}>
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {config.tabs.map(tab => (
            <TabsContent key={tab.key} value={tab.key} className="space-y-6">
              {activatedTabs.has(tab.key) ? (
                <Card>
                  <CardHeader>
                    <CardTitle>{tab.label}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {renderTabContent(tab)}
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="flex items-center justify-center py-12">
                    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          ))}
        </Tabs>
      </form>
    </div>
      {/* Keyboard Shortcut Bar — nur auf Desktop sichtbar */}
      <KeyboardShortcutBar shortcuts={kbShortcuts} />
    </div>
  )
}

export default ObjectPage
