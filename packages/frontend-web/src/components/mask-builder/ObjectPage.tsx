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
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { MaskConfig, Tab as MaskTab, Field } from './types'
import { createMaskResolver, getFieldName, getFieldsFromMaskConfig } from './validation'

function inputValue(value: unknown): string | number | readonly string[] | undefined {
  if (typeof value === 'string' || typeof value === 'number' || Array.isArray(value)) return value
  return ''
}

function checkedValue(value: unknown): boolean {
  return value === true
}

interface ObjectPageProps {
  config: MaskConfig
  data?: Record<string, unknown> | null
  onChange?: (_data: Record<string, unknown>) => void
  onSave: (_data: Record<string, unknown>) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  /** When provided, toolbar action buttons call this with (actionKey, formData) instead of action.onClick */
  onAction?: (_actionKey: string, _formData: Record<string, unknown>) => void | Promise<void>
  /** Key of the action currently loading (disables that button and shows spinner) */
  loadingActionKey?: string | null
  /** Enable golden-ratio split layout (61.8% / 38.2%) for the active tab content */
  splitLayout?: boolean
}

const ObjectPage: React.FC<ObjectPageProps> = ({
  config,
  data,
  onChange,
  onSave,
  onCancel,
  isLoading = false,
  onAction,
  loadingActionKey = null,
  splitLayout = true,
}) => {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState(config.tabs[0]?.key || '')
  const [activatedTabs, setActivatedTabs] = useState<Set<string>>(
    () => new Set(config.tabs[0]?.key ? [config.tabs[0].key] : []),
  )
  const [isDirty, setIsDirty] = useState(false)
  const [hasDraft, setHasDraft] = useState(false)
  const isInternalUpdateRef = useRef(false)
  const draftKey = `objectpage-draft-${config.title.replace(/\s+/g, '-').toLowerCase()}`

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
    defaultValues: data || {},
    mode: 'onBlur',
  })

  // Check for existing draft on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(draftKey)
      if (saved) setHasDraft(true)
    } catch {
      // localStorage not available
    }
  }, [draftKey])

  // Watch for changes to mark form as dirty and auto-save draft
  useEffect(() => {
    let autoSaveTimer: ReturnType<typeof setTimeout>
    const subscription = watch((value) => {
      setIsDirty(true)
      if (onChange) {
        isInternalUpdateRef.current = true
        onChange(value)
      }
      clearTimeout(autoSaveTimer)
      autoSaveTimer = setTimeout(() => {
        try {
          localStorage.setItem(draftKey, JSON.stringify(value))
        } catch {
          // localStorage not available or full
        }
      }, 30_000)
    })
    return () => {
      subscription.unsubscribe()
      clearTimeout(autoSaveTimer)
    }
  }, [watch, onChange, draftKey])

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

  // Gap 023: Keyboard-first — Ctrl+S speichern, Escape abbrechen
  useKeyboardShortcuts([
    {
      key: 's',
      ctrl: true,
      label: 'Speichern',
      action: () => { void handleSubmit(onSubmit)() },
      disabled: isSubmitting || isLoading,
      allowInInputs: true,
    },
    {
      key: 'Escape',
      label: 'Abbrechen',
      action: onCancel,
      allowInInputs: false,
    },
  ])

  function restoreDraft(): void {
    try {
      const saved = localStorage.getItem(draftKey)
      if (saved) {
        reset(JSON.parse(saved))
        setHasDraft(false)
        setIsDirty(true)
        toast({ title: 'Entwurf wiederhergestellt', description: 'Der gespeicherte Entwurf wurde geladen.' })
      }
    } catch {
      // ignore
    }
  }

  function discardDraft(): void {
    try {
      localStorage.removeItem(draftKey)
      setHasDraft(false)
    } catch {
      // ignore
    }
  }

  const onSubmit = async (formData: Record<string, unknown>) => {
    try {
      await onSave(formData)
      setIsDirty(false)
      try { localStorage.removeItem(draftKey) } catch { /* ignore */ }
      setHasDraft(false)
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
    const fieldName = getFieldName(field)
    const error = errors[fieldName]?.message as string
    const errorId = error ? `${fieldName}-error` : undefined

    return (
      <div key={fieldName} className="space-y-2">
        <Label htmlFor={fieldName}>
          {field.label}
          {field.required && <span className="ml-1 text-destructive" aria-hidden="true">*</span>}
        </Label>

        <Controller
          name={fieldName}
          control={control}
          render={({ field: controllerField }) => {
            switch (field.type) {
              case 'text':
              case 'number':
                return (
                  <Input
                    {...controllerField}
                    value={inputValue(controllerField.value)}
                    id={fieldName}
                    type={field.type}
                    placeholder={field.placeholder}
                    readOnly={field.readonly ?? field.readOnly}
                    aria-invalid={error ? 'true' : undefined}
                    aria-describedby={errorId}
                    aria-required={field.required ? 'true' : undefined}
                    className={error ? 'border-destructive' : ''}
                  />
                )

              case 'textarea':
                return (
                  <Textarea
                    {...controllerField}
                    value={inputValue(controllerField.value)}
                    id={fieldName}
                    placeholder={field.placeholder}
                    readOnly={field.readonly ?? field.readOnly}
                    className={error ? 'border-destructive' : ''}
                  />
                )

              case 'boolean':
              case 'checkbox': {
                const { value: _value, ...checkboxField } = controllerField
                return (
                  <div className="flex items-center space-x-2">
                    <input
                      {...checkboxField}
                      id={fieldName}
                      type="checkbox"
                      checked={checkedValue(controllerField.value)}
                      className="h-4 w-4"
                    />
                    <Label htmlFor={fieldName} className="text-sm">
                      {field.label}
                    </Label>
                  </div>
                )
              }

              case 'select': {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const selectField = field as any
                return (
                  <NativeSelect
                    id={fieldName}
                    value={String(controllerField.value ?? '')}
                    onValueChange={controllerField.onChange}
                    options={selectField.options ?? []}
                    placeholder={field.placeholder}
                    disabled={field.readonly ?? field.readOnly}
                    className={error ? 'border-destructive' : ''}
                  />
                )
              }

              case 'date':
                return (
                  <Input
                    {...controllerField}
                    value={inputValue(controllerField.value)}
                    id={fieldName}
                    type="date"
                    readOnly={field.readonly ?? field.readOnly}
                    className={error ? 'border-destructive' : ''}
                  />
                )

              case 'datetime':
                return (
                  <Input
                    {...controllerField}
                    value={inputValue(controllerField.value)}
                    id={fieldName}
                    type="datetime-local"
                    readOnly={field.readonly ?? field.readOnly}
                    className={error ? 'border-destructive' : ''}
                  />
                )

              default:
                return (
                  <Input
                    {...controllerField}
                    value={inputValue(controllerField.value)}
                    id={fieldName}
                    placeholder={field.placeholder}
                    readOnly={field.readonly ?? field.readOnly}
                    className={error ? 'border-destructive' : ''}
                  />
                )
            }
          }}
        />

        {error && (
          <p id={errorId} role="alert" aria-live="polite" className="flex items-center gap-1 text-sm text-destructive">
            <AlertTriangle className="h-3 w-3" aria-hidden="true" />
            {error}
          </p>
        )}

        {field.helpText && (
          <p className="text-xs text-muted-foreground">{field.helpText}</p>
        )}
      </div>
    )
  }

  const renderTabSidePanel = (tab: MaskTab) => {
    const errorCount = tab.fields.filter((field) => {
      const fieldName = getFieldName(field)
      return Boolean(errors[fieldName])
    }).length

    const helpFields = tab.fields.filter((field) => field.helpText)

    return (
      <div className="space-y-4">
        <Card className="border-accent/20 bg-accent/5">
          <CardHeader className="pb-2">
            <CardTitle className="text-base text-accent-foreground">Uebersicht</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Register</span>
              <span className="font-medium text-foreground">{tab.label}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Felder</span>
              <span className="tabular-nums font-medium text-foreground">{tab.fields.length}</span>
            </div>
            {errorCount > 0 && (
              <div className="flex justify-between gap-4 text-destructive">
                <span>Validierung</span>
                <span className="tabular-nums font-medium">{errorCount} offen</span>
              </div>
            )}
            {isDirty && (
              <p className="text-xs text-muted-foreground">Ungespeicherte Aenderungen vorhanden.</p>
            )}
          </CardContent>
        </Card>

        {helpFields.length > 0 && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Hinweise</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-xs text-muted-foreground">
              {helpFields.slice(0, 4).map((field) => (
                <p key={getFieldName(field)}>
                  <span className="font-medium text-foreground">{field.label}: </span>
                  {field.helpText}
                </p>
              ))}
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  const renderTabContent = (tab: MaskTab) => {
    if (typeof tab.customRender === 'function') {
      return tab.customRender(watch(), (nextData: Record<string, unknown>) => {
        reset(nextData)
        if (onChange) {
          onChange(nextData)
        }
      })
    }

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
    <div className="space-y-8 p-4 md:p-8">
      {/* Header */}
      <div className="flex flex-col gap-4 rounded-(--radius) border border-border bg-card p-6 shadow-sm md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-normal text-foreground">{config.title}</h1>
          {config.subtitle && (
            <p className="mt-1 text-sm text-muted-foreground">{config.subtitle}</p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          {config.actions.map(action => {
            const isThisLoading = loadingActionKey != null && action.key === loadingActionKey
            return (
              <Button
                key={action.key}
                variant={action.type === 'primary' ? 'default' : 'outline'}
                onClick={() => {
                  if (onAction) {
                    void Promise.resolve(onAction(action.key, watch())).catch((err: unknown) => {
                      const msg = err instanceof Error ? err.message : 'Aktion fehlgeschlagen'
                      toast({ title: 'Fehler', description: msg, variant: 'destructive' })
                    })
                  } else {
                    void Promise.resolve(action.onClick?.(watch())).catch((err: unknown) => {
                      const msg = err instanceof Error ? err.message : 'Aktion fehlgeschlagen'
                      toast({ title: 'Fehler', description: msg, variant: 'destructive' })
                    })
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

      {/* Draft restore banner */}
      {hasDraft && !isDirty && (
        <Card className="border-primary/30 bg-primary/5">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-primary">
                <Save className="h-5 w-5" aria-hidden="true" />
                <span className="font-semibold">Entwurf vorhanden</span>
              </div>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={restoreDraft}>Wiederherstellen</Button>
                <Button size="sm" variant="ghost" onClick={discardDraft}><X className="h-4 w-4" /></Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dirty Warning */}
      {isDirty && (
        <Card className="border-[hsl(var(--accent))]/40 bg-[hsl(var(--accent)/0.10)]">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-[hsl(var(--accent-foreground))]">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">
                Ungespeicherte Änderungen
              </span>
            </div>
            <p className="mt-1 text-sm text-[hsl(var(--accent-foreground))]">
              Sie haben ungespeicherte Änderungen. Vergessen Sie nicht zu speichern.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Validation error summary */}
      {Object.keys(errors).length > 0 && (
        <Card className="border-destructive/40 bg-destructive/10" role="alert" aria-label="Validierungsfehler">
          <CardContent className="pt-4">
            <div className="mb-2 flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" aria-hidden="true" />
              <span className="font-semibold">Bitte korrigieren Sie folgende Felder:</span>
            </div>
            <ul className="list-disc list-inside space-y-1">
              {Object.entries(errors).map(([key, err]) => (
                <li key={key} className="text-sm text-destructive">
                  <a href={`#${key}`} className="underline hover:no-underline">
                    {(err as Error)?.message ?? key}
                  </a>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        <Tabs value={activeTab} onValueChange={handleTabChange}>
          {/* Register-Look als Standard der ObjectPage (Gewohnheits-Prinzip);
              das starre grid-cols-4 brach bei ≠4 Tabs. */}
          <TabsList variant="register">
            {config.tabs.map(tab => (
              <TabsTrigger key={tab.key} value={tab.key}>
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {config.tabs.map(tab => (
            <TabsContent key={tab.key} value={tab.key} className="space-y-6">
              {activatedTabs.has(tab.key) ? (
                splitLayout ? (
                  <div className="grid gap-6 lg:grid-cols-[61.8fr_38.2fr]">
                    <Card>
                      <CardHeader>
                        <CardTitle>{tab.label}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {renderTabContent(tab)}
                      </CardContent>
                    </Card>
                    {renderTabSidePanel(tab)}
                  </div>
                ) : (
                  <Card>
                    <CardHeader>
                      <CardTitle>{tab.label}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {renderTabContent(tab)}
                    </CardContent>
                  </Card>
                )
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
  )
}

export default ObjectPage
