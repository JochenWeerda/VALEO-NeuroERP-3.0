import React, { useState } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
// Badge import removed - not used
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { AlertTriangle, CheckCircle, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { WizardConfig, WizardStep, Field } from './types'

interface WizardProps {
  config: WizardConfig
  onComplete: (data: any) => void
  onCancel: () => void
  isLoading?: boolean
}

const Wizard: React.FC<WizardProps> = ({
  config,
  onComplete,
  onCancel,
  isLoading = false
}) => {
  const { toast } = useToast()
  const [currentStep, setCurrentStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set())

  const currentStepConfig = config.steps[currentStep]
  const isLastStep = currentStep === config.steps.length - 1
  const isFirstStep = currentStep === 0

  // Create schema for current step
  const createStepSchema = (step: WizardStep) => {
    const schema: any = {}

    step.fields.forEach(field => {
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

    return z.object(schema)
  }

  const stepSchema = createStepSchema(currentStepConfig)
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    trigger,
    getValues
  } = useForm({
    resolver: zodResolver(stepSchema),
    mode: 'onChange'
  })

  const handleNext = async () => {
    const isValid = await trigger()
    if (!isValid) {
      toast({
        title: "Validierungsfehler",
        description: "Bitte korrigieren Sie die Eingaben.",
        variant: "destructive",
      })
      return
    }

    setCompletedSteps(prev => new Set([...prev, currentStep]))
    setCurrentStep(currentStep + 1)
  }

  const handlePrevious = () => {
    setCurrentStep(currentStep - 1)
  }

  const handleStepClick = async (stepIndex: number) => {
    if (stepIndex > currentStep) {
      // Going forward - validate current step
      const isValid = await trigger()
      if (!isValid) return
      setCompletedSteps(prev => new Set([...prev, currentStep]))
    }

    setCurrentStep(stepIndex)
  }

  const onSubmit = async (_stepData: any) => {
    if (!isLastStep) {
      handleNext()
      return
    }

    try {
      // Collect all step data
      const allData = getValues()
      await onComplete(allData)

      toast({
        title: "Erfolgreich abgeschlossen",
        description: "Der Prozess wurde erfolgreich abgeschlossen.",
      })
    } catch (error) {
      toast({
        title: "Fehler",
        description: "Beim Abschließen ist ein Fehler aufgetreten.",
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
                    className={error ? 'border-red-500' : ''}
                  />
                )

              case 'textarea':
                return (
                  <Textarea
                    {...controllerField}
                    id={field.name}
                    placeholder={field.placeholder}
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
                    className={error ? 'border-red-500' : ''}
                  />
                )

              case 'datetime':
                return (
                  <Input
                    {...controllerField}
                    id={field.name}
                    type="datetime-local"
                    className={error ? 'border-red-500' : ''}
                  />
                )

              default:
                return (
                  <Input
                    {...controllerField}
                    id={field.name}
                    placeholder={field.placeholder}
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
        <Button variant="outline" onClick={onCancel}>
          Abbrechen
        </Button>
      </div>

      {/* Progress Indicator */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium">Schritt {currentStep + 1} von {config.steps.length}</span>
            <span className="text-sm text-muted-foreground">{currentStepConfig.title}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / config.steps.length) * 100}%` }}
            ></div>
          </div>

          {/* Step Navigation */}
          <div className="flex justify-between">
            {config.steps.map((step, index) => {
              const isCompleted = completedSteps.has(index)
              const isCurrent = index === currentStep
              const isClickable = index <= currentStep || completedSteps.has(index - 1)

              return (
                <button
                  key={index}
                  onClick={() => isClickable && handleStepClick(index)}
                  disabled={!isClickable}
                  className={`flex flex-col items-center p-2 rounded-lg transition-colors ${
                    isCurrent
                      ? 'bg-blue-100 border-2 border-blue-500'
                      : isCompleted
                      ? 'bg-green-100 border-2 border-green-500'
                      : 'bg-gray-100 border-2 border-gray-300'
                  } ${isClickable ? 'cursor-pointer hover:bg-opacity-80' : 'cursor-not-allowed opacity-50'}`}
                >
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium mb-1 ${
                    isCurrent
                      ? 'bg-blue-500 text-white'
                      : isCompleted
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-300 text-gray-600'
                  }`}>
                    {isCompleted ? <CheckCircle className="h-4 w-4" /> : index + 1}
                  </div>
                  <span className="text-xs text-center">{step.title}</span>
                </button>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Current Step Content */}
      <Card>
        <CardHeader>
          <CardTitle>{currentStepConfig.title}</CardTitle>
          {currentStepConfig.description && (
            <p className="text-muted-foreground">{currentStepConfig.description}</p>
          )}
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="grid gap-4 md:grid-cols-2">
              {currentStepConfig.fields.map(renderField)}
            </div>

            {/* Navigation */}
            <div className="flex justify-between mt-6 pt-6 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={handlePrevious}
                disabled={isFirstStep}
                className="gap-2"
              >
                <ChevronLeft className="h-4 w-4" />
                Zurück
              </Button>

              <div className="flex gap-2">
                {!isLastStep ? (
                  <Button type="submit" className="gap-2">
                    Weiter
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                ) : (
                  <Button
                    type="submit"
                    disabled={isSubmitting}
                    className="gap-2"
                  >
                    {isSubmitting ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCircle className="h-4 w-4" />
                    )}
                    Abschließen
                  </Button>
                )}
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default Wizard