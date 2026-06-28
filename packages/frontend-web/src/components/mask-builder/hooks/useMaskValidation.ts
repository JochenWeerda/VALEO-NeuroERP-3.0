import { useState, useCallback } from 'react'
import { useToast } from '@/hooks/use-toast'
import { validateSchemaField, validateSchemaLike } from '../validation'

interface ValidationResult {
  isValid: boolean
  errors: Record<string, string>
}

export function useMaskValidation(schema?: unknown) {
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const { toast } = useToast()

  const validate = useCallback((data: Record<string, unknown>): ValidationResult => {
    const result = validateSchemaLike(schema, data)
    setValidationErrors(result.errors)
    return result
  }, [schema])

  const validateField = useCallback((field: string, value: unknown): string | null => {
    if (!schema) return null
    const errorMessage = validateSchemaField(schema, field, value)
    setValidationErrors(prev => {
      if (!errorMessage) {
        const next = { ...prev }
        delete next[field]
        return next
      }
      return {
        ...prev,
        [field]: errorMessage
      }
    })
    return errorMessage
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
