import React, { useState, useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
// Badge import removed - not used
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { AlertTriangle, Loader2, Save, X } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { MaskConfig, Field } from './types'

interface ObjectPageProps {
  config: MaskConfig
  data?: any
  onSave: (data: any) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

const ObjectPage: React.FC<ObjectPageProps> = ({
  config,
  data,
  onSave,
  onCancel,
  isLoading = false
}) => {
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState(config.tabs[0]?.key || '')
  const [isDirty, setIsDirty] = useState(false)

  // Create dynamic Zod schema from config
  const createSchema = (tabs: MaskConfig['tabs']) => {
    const schema: any = {}

    tabs.forEach(tab => {
      tab.fields.forEach(field => {
        let fieldSchema: any

        switch (field.type) {
          case 'text':
            fieldSchema = z.string()
            if ((field as any).minLength) fieldSchema = fieldSchema.min((field as any).minLength)
            if ((field as any).maxLength) fieldSchema = fieldSchema.max((field as any).maxLength)
            break
          case 'number':
            fieldSchema = z.number()
            if ((field as any).min !== undefined) fieldSchema = fieldSchema.min((field as any).min)
            if ((field as any).max !== undefined) fieldSchema = fieldSchema.max((field as any).max)
            break
          case 'boolean':
            fieldSchema = z.boolean()
            break
          case 'date':
          case 'datetime':
            fieldSchema = z.string()
            break
          case 'select':
            fieldSchema = z.string()
            break
          case 'multiselect':
            fieldSchema = z.array(z.string())
            break
          case 'textarea':
            fieldSchema = z.string()
            break
          default:
            fieldSchema = z.any()
        }

        if (!field.required) {
          fieldSchema = fieldSchema.optional()
        }

        schema[field.name] = fieldSchema
      })
    })

    return z.object(schema)
  }

  const schema = createSchema(config.tabs)
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    reset
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: data || {}
  })

  // Watch for changes to mark form as dirty
  useEffect(() => {
    const subscription = watch(() => setIsDirty(true))
    return () => subscription.unsubscribe()
  }, [watch])

  // Reset dirty state when data changes
  useEffect(() => {
    if (data) {
      reset(data)
      setIsDirty(false)
    }
  }, [data, reset])

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

              case 'select':
                const selectField = field as any
                return (
                  <Select
                    value={controllerField.value}
                    onValueChange={controllerField.onChange}
                    disabled={field.readonly}
                  >
                    <SelectTrigger className={error ? 'border-red-500' : ''}>
                      <SelectValue placeholder={field.placeholder} />
                    </SelectTrigger>
                    <SelectContent>
                      {selectField.options?.map((option: any) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )

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
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{config.title}</h1>
          {config.subtitle && (
            <p className="text-muted-foreground">{config.subtitle}</p>
          )}
        </div>
        <div className="flex gap-2">
          {config.actions.map(action => (
            <Button
              key={action.key}
              variant={action.type === 'primary' ? 'default' : 'outline'}
              onClick={action.onClick}
              disabled={action.disabled}
              className="gap-2"
            >
              {action.icon && <span className="text-sm">{action.icon}</span>}
              {action.label}
            </Button>
          ))}
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
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            {config.tabs.map(tab => (
              <TabsTrigger key={tab.key} value={tab.key}>
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {config.tabs.map(tab => (
            <TabsContent key={tab.key} value={tab.key} className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>{tab.label}</CardTitle>
                </CardHeader>
                <CardContent>
                  {renderTabContent(tab)}
                </CardContent>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      </form>
    </div>
  )
}

export default ObjectPage