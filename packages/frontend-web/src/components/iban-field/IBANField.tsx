import { useState, useEffect, useCallback } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Loader2, Search } from 'lucide-react'
import { useIbanLookup } from '@/hooks/useIbanLookup'
import { validateIBAN, formatIBAN } from '@/lib/utils/iban-validator'
import { useTranslation } from 'react-i18next'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

interface IBANFieldProps {
  value?: string
  onChange: (value: string) => void
  onBankData?: (data: { bank_name?: string; bic?: string }) => void
  placeholder?: string
  disabled?: boolean
  showLookupButton?: boolean
  autoLookup?: boolean
  className?: string
  error?: string
}

/**
 * IBAN Field Component with automatic bank lookup
 * Automatically validates IBAN and retrieves bank information
 */
export function IBANField({
  value = '',
  onChange,
  onBankData,
  placeholder,
  disabled = false,
  showLookupButton = true,
  autoLookup = true,
  className,
  error
}: IBANFieldProps) {
  const { t } = useTranslation()
  const [localValue, setLocalValue] = useState(value)

  const { performLookup, isLoading, lookupData } = useIbanLookup({
    onSuccess: (result) => {
      if (result.valid && result.bank_name) {
        onBankData?.({
          bank_name: result.bank_name || undefined,
          bic: result.bic || undefined
        })
        toast.success(t('crud.messages.ibanLookupSuccess', {
          defaultValue: 'Bankinformationen automatisch ausgefüllt',
          bankName: result.bank_name
        }))
      }
    },
    onError: (error) => {
      // Silent error for auto-lookup, only show for manual lookup
      console.warn('IBAN lookup failed:', error)
    },
    autoLookup: false // Manual control
  })

  // Update local value when prop changes
  useEffect(() => {
    setLocalValue(value)
  }, [value])

  // Auto-lookup when IBAN seems complete
  useEffect(() => {
    if (!autoLookup || !localValue) return

    const normalized = localValue.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
    
    if (normalized.length >= 15 && normalized.length <= 34) {
      const timer = setTimeout(() => {
        if (validateIBAN(normalized)) {
          performLookup(normalized)
        }
      }, 1000) // 1 second debounce

      return () => clearTimeout(timer)
    }
  }, [localValue, autoLookup, performLookup])

  // Update parent when bank data is retrieved
  useEffect(() => {
    if (lookupData?.valid && lookupData.bank_name) {
      onBankData?.({
        bank_name: lookupData.bank_name || undefined,
        bic: lookupData.bic || undefined
      })
    }
  }, [lookupData, onBankData])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value
    const formatted = formatIBAN(inputValue)
    setLocalValue(formatted)
    onChange(formatted)
  }, [onChange])

  const handleLookup = useCallback(() => {
    const normalized = localValue.replace(/\s/g, '').replace(/-/g, '').toUpperCase()
    if (normalized.length < 15) {
      toast.error(t('crud.messages.invalidIban', {
        defaultValue: 'Bitte geben Sie eine vollständige IBAN ein'
      }))
      return
    }
    if (!validateIBAN(normalized)) {
      toast.error(t('crud.messages.invalidIban'))
      return
    }
    performLookup(normalized)
  }, [localValue, performLookup, t])

  return (
    <div className="space-y-1">
      <div className="flex gap-2">
        <div className="flex-1">
          <Input
            type="text"
            value={localValue}
            onChange={handleChange}
            placeholder={placeholder || t('crud.tooltips.placeholders.iban', { defaultValue: 'z.B. DE89370400440532013000' })}
            disabled={disabled}
            className={cn("font-mono", className, error && "border-red-500")}
          />
        </div>
        {showLookupButton && (
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={handleLookup}
            disabled={disabled || isLoading || !localValue}
            title={t('crud.actions.lookupBank', { defaultValue: 'Bank aus IBAN ermitteln' })}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Search className="h-4 w-4" />
            )}
          </Button>
        )}
      </div>
      {error && (
        <p className="text-sm text-red-500">{error}</p>
      )}
    </div>
  )
}
