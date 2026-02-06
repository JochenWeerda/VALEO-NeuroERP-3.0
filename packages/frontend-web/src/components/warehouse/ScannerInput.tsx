/**
 * Scanner Input
 *
 * Großes, touch-optimiertes Eingabefeld für Barcode-Scanner
 * - Automatischer Fokus
 * - Visuelles Feedback bei Scan
 * - Keyboard-Scanner und manuelle Eingabe
 */

import { useState, useRef, useEffect, forwardRef } from 'react'
import { cn } from '@/lib/utils'
import { ScanLine, Keyboard, X, Check, AlertCircle } from 'lucide-react'
import { useBarcodeScan, BarcodeResult } from '@/hooks/useBarcodeScan'

interface ScannerInputProps {
  onScan: (barcode: string, format: string) => void
  onError?: (error: string) => void
  placeholder?: string
  autoFocus?: boolean
  disabled?: boolean
  className?: string
}

type ScanState = 'idle' | 'scanning' | 'success' | 'error'

export const ScannerInput = forwardRef<HTMLInputElement, ScannerInputProps>(
  function ScannerInput(
    {
      onScan,
      onError,
      placeholder = 'Barcode scannen oder eingeben...',
      autoFocus = true,
      disabled = false,
      className,
    },
    ref
  ) {
    const [manualInput, setManualInput] = useState('')
    const [scanState, setScanState] = useState<ScanState>('idle')
    const [lastValue, setLastValue] = useState('')
    const inputRef = useRef<HTMLInputElement>(null)
    const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    // Barcode-Scanner Hook
    const { isScanning, lastScan } = useBarcodeScan({
      onScan: (result: BarcodeResult) => {
        handleScanSuccess(result.value, result.format)
      },
      onError: (error) => {
        handleScanError(error.message)
      },
      minLength: 4,
    })

    // Erfolgreicher Scan
    const handleScanSuccess = (value: string, format: string) => {
      setLastValue(value)
      setScanState('success')
      onScan(value, format)

      // Reset nach 2 Sekunden
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      timeoutRef.current = setTimeout(() => {
        setScanState('idle')
        setManualInput('')
      }, 2000)
    }

    // Scan-Fehler
    const handleScanError = (message: string) => {
      setScanState('error')
      onError?.(message)

      // Reset nach 2 Sekunden
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      timeoutRef.current = setTimeout(() => {
        setScanState('idle')
      }, 2000)
    }

    // Manuelle Eingabe bestätigen
    const handleManualSubmit = () => {
      if (manualInput.trim().length >= 4) {
        handleScanSuccess(manualInput.trim(), 'MANUAL')
      } else {
        handleScanError('Eingabe zu kurz (min. 4 Zeichen)')
      }
    }

    // Auto-Fokus
    useEffect(() => {
      if (autoFocus && inputRef.current) {
        inputRef.current.focus()
      }
    }, [autoFocus])

    // Update Scanning State
    useEffect(() => {
      if (isScanning && scanState === 'idle') {
        setScanState('scanning')
      }
    }, [isScanning, scanState])

    // Cleanup
    useEffect(() => {
      return () => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current)
      }
    }, [])

    const stateStyles = {
      idle: 'border-border focus-within:border-primary',
      scanning: 'border-primary bg-primary/10 animate-pulse',
      success: 'border-emerald-500 bg-emerald-500/20',
      error: 'border-red-500 bg-red-500/20',
    }

    const stateIcons = {
      idle: <ScanLine className="h-8 w-8 text-muted-foreground" />,
      scanning: <ScanLine className="h-8 w-8 text-primary animate-pulse" />,
      success: <Check className="h-8 w-8 text-emerald-500" />,
      error: <AlertCircle className="h-8 w-8 text-red-500" />,
    }

    return (
      <div className={cn('space-y-3', className)}>
        {/* Haupt-Scan-Bereich */}
        <div
          className={cn(
            'relative flex items-center gap-4 p-4 rounded-xl border-4 transition-all',
            stateStyles[scanState],
            disabled && 'opacity-50 pointer-events-none'
          )}
        >
          {/* Status Icon */}
          <div className="flex-shrink-0">{stateIcons[scanState]}</div>

          {/* Input oder Status */}
          <div className="flex-1 min-w-0">
            {scanState === 'success' ? (
              <div>
                <p className="text-lg font-bold text-emerald-500 truncate">
                  {lastValue}
                </p>
                <p className="text-sm text-muted-foreground">
                  Erfolgreich gescannt
                </p>
              </div>
            ) : scanState === 'error' ? (
              <div>
                <p className="text-lg font-bold text-red-500">Fehler</p>
                <p className="text-sm text-muted-foreground">
                  Barcode ungültig
                </p>
              </div>
            ) : (
              <input
                ref={(node) => {
                  // Beide Refs zuweisen
                  ;(inputRef as React.MutableRefObject<HTMLInputElement | null>).current = node
                  if (typeof ref === 'function') {
                    ref(node)
                  } else if (ref) {
                    ref.current = node
                  }
                }}
                type="text"
                inputMode="none" // Verhindert virtuelle Tastatur auf Mobile
                value={manualInput}
                onChange={(e) => setManualInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && manualInput) {
                    handleManualSubmit()
                  }
                }}
                placeholder={placeholder}
                disabled={disabled || scanState !== 'idle'}
                className="w-full bg-transparent text-xl font-medium placeholder:text-muted-foreground focus:outline-none"
              />
            )}
          </div>

          {/* Löschen-Button */}
          {manualInput && scanState === 'idle' && (
            <button
              onClick={() => setManualInput('')}
              className="flex-shrink-0 h-12 w-12 flex items-center justify-center rounded-lg bg-neutral-700 text-white active:bg-neutral-600"
              aria-label="Löschen"
            >
              <X className="h-6 w-6" />
            </button>
          )}
        </div>

        {/* Manuelle Eingabe Button */}
        {manualInput && scanState === 'idle' && (
          <button
            onClick={handleManualSubmit}
            className="w-full h-16 flex items-center justify-center gap-3 rounded-xl bg-primary text-primary-foreground text-lg font-bold active:opacity-80"
          >
            <Keyboard className="h-6 w-6" />
            Eingabe bestätigen
          </button>
        )}

        {/* Anleitung */}
        {scanState === 'idle' && !manualInput && (
          <div className="text-center text-muted-foreground">
            <p className="text-sm">
              Scanner bereit. Halten Sie den Barcode vor den Scanner.
            </p>
          </div>
        )}
      </div>
    )
  }
)
