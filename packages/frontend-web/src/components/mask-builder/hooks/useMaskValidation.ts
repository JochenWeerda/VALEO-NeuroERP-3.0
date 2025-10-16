import { useState, useCallback } from 'react'
import { z } from 'zod'
import { useToast } from '@/hooks/use-toast'

interface ValidationResult {
  isValid: boolean
  errors: Record<string, string>
}

export function useMaskValidation(schema?: z.ZodSchema) {
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const { toast } = useToast()

  const validate = useCallback((data: any): ValidationResult => {
    if (!schema) {
      return { isValid: true, errors: {} }
    }

    try {
      schema.parse(data)
      setValidationErrors({})
      return { isValid: true, errors: {} }
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errors: Record<string, string> = {}
        error.errors.forEach((err) => {
          const path = err.path.join('.')
          errors[path] = err.message
        })
        setValidationErrors(errors)
        return { isValid: false, errors }
      }

      const errorMessage = 'Validation failed'
      setValidationErrors({ general: errorMessage })
      return { isValid: false, errors: { general: errorMessage } }
    }
  }, [schema])

  const validateField = useCallback((field: string, value: any): string | null => {
    if (!schema) return null

    try {
      // Create a partial schema for single field validation
      const fieldSchema = (schema as any).shape?.[field]
      if (fieldSchema) {
        fieldSchema.parse(value)
        setValidationErrors(prev => {
          const newErrors = { ...prev }
          delete newErrors[field]
          return newErrors
        })
        return null
      }
      return null
    } catch (error) {
      if (error instanceof z.ZodError) {
        const errorMessage = error.errors[0]?.message || 'Invalid value'
        setValidationErrors(prev => ({
          ...prev,
          [field]: errorMessage
        }))
        return errorMessage
      }
      return 'Invalid value'
    }
  }, [schema])

  const clearErrors = useCallback(() => {
    setValidationErrors({})
  }, [])

  const showValidationToast = useCallback((errors: Record<string, string>) => {
    const errorCount = Object.keys(errors).length
    if (errorCount > 0) {
      toast({
        title: "Validierungsfehler",
        description: `${errorCount} Feld(er) müssen korrigiert werden.`,
        variant: "destructive",
      })
    }
  }, [toast])

  return {
    validationErrors,
    validate,
    validateField,
    clearErrors,
    showValidationToast,
  }
}