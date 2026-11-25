import { useState, useCallback, useRef } from 'react'
import { lookupIBAN, type IBANLookupResponse, formatIBAN } from '@/lib/utils/iban-validator'

interface UseIbanLookupOptions {
  onSuccess?: (data: IBANLookupResponse) => void
  onError?: (error: Error) => void
  autoLookup?: boolean // Automatically lookup when IBAN is valid
  minLength?: number // Minimum IBAN length before attempting lookup
}

/**
 * Hook for IBAN lookup functionality
 * Automatically validates IBAN and retrieves bank information.
 * Spätere Antworten zu einer älteren IBAN werden verworfen (Race-Schutz).
 */
export function useIbanLookup(options: UseIbanLookupOptions = {}) {
  const {
    onSuccess,
    onError,
    autoLookup = true,
    minLength = 15,
  } = options

  const [isLoading, setIsLoading] = useState(false)
  const [lookupData, setLookupData] = useState<IBANLookupResponse | null>(null)
  const requestSeq = useRef(0)

  const performLookup = useCallback(async (iban: string): Promise<IBANLookupResponse | null> => {
    if (!iban || iban.trim().length < minLength) {
      return null
    }

    const seq = ++requestSeq.current
    setIsLoading(true)
    setLookupData(null)

    try {
      const result = await lookupIBAN(iban)
      if (seq !== requestSeq.current) {
        return null
      }
      setLookupData(result)

      if (result.valid) {
        onSuccess?.(result)
      } else {
        const error = new Error(result.message || 'Invalid IBAN')
        onError?.(error)
      }

      return result
    } catch (error) {
      if (seq !== requestSeq.current) {
        return null
      }
      const err = error instanceof Error ? error : new Error('Failed to lookup IBAN')
      onError?.(err)
      setLookupData(null)
      return null
    } finally {
      if (seq === requestSeq.current) {
        setIsLoading(false)
      }
    }
  }, [onSuccess, onError, minLength])

  const handleIbanChange = useCallback(async (iban: string) => {
    const normalized = iban.replace(/\s/g, '').replace(/-/g, '').toUpperCase()

    // Format IBAN for display
    const formatted = formatIBAN(normalized)

    // Auto-lookup if enabled and IBAN seems complete
    if (autoLookup && normalized.length >= minLength) {
      if (normalized.length >= 15 && normalized.length <= 34) {
        await performLookup(normalized)
      }
    }

    return formatted
  }, [autoLookup, minLength, performLookup])

  const reset = useCallback(() => {
    requestSeq.current += 1
    setLookupData(null)
    setIsLoading(false)
  }, [])

  return {
    performLookup,
    handleIbanChange,
    isLoading,
    lookupData,
    reset,
  }
}
