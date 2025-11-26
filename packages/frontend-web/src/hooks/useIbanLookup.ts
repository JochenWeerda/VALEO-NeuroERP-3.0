import { useState, useCallback } from 'react'
import { lookupIBAN, type IBANLookupResponse, formatIBAN } from '@/lib/utils/iban-validator'
import { toast } from 'sonner'

interface UseIbanLookupOptions {
  onSuccess?: (data: IBANLookupResponse) => void
  onError?: (error: Error) => void
  autoLookup?: boolean // Automatically lookup when IBAN is valid
  minLength?: number // Minimum IBAN length before attempting lookup
}

/**
 * Hook for IBAN lookup functionality
 * Automatically validates IBAN and retrieves bank information
 */
export function useIbanLookup(options: UseIbanLookupOptions = {}) {
  const {
    onSuccess,
    onError,
    autoLookup = true,
    minLength = 15
  } = options

  const [isLoading, setIsLoading] = useState(false)
  const [lookupData, setLookupData] = useState<IBANLookupResponse | null>(null)

  const performLookup = useCallback(async (iban: string): Promise<IBANLookupResponse | null> => {
    if (!iban || iban.trim().length < minLength) {
      return null
    }

    setIsLoading(true)
    setLookupData(null)

    try {
      const result = await lookupIBAN(iban)
      setLookupData(result)

      if (result.valid) {
        onSuccess?.(result)
      } else {
        const error = new Error(result.message || 'Invalid IBAN')
        onError?.(error)
      }

      return result
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Failed to lookup IBAN')
      onError?.(err)
      setLookupData(null)
      return null
    } finally {
      setIsLoading(false)
    }
  }, [onSuccess, onError, minLength])

  const handleIbanChange = useCallback(async (iban: string) => {
    const normalized = iban.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
    
    // Format IBAN for display
    const formatted = formatIBAN(normalized)
    
    // Auto-lookup if enabled and IBAN seems complete
    if (autoLookup && normalized.length >= minLength) {
      // Debounce: only lookup if IBAN looks complete (typical length)
      if (normalized.length >= 15 && normalized.length <= 34) {
        await performLookup(normalized)
      }
    }

    return formatted
  }, [autoLookup, minLength, performLookup])

  const reset = useCallback(() => {
    setLookupData(null)
    setIsLoading(false)
  }, [])

  return {
    performLookup,
    handleIbanChange,
    isLoading,
    lookupData,
    reset
  }
}

