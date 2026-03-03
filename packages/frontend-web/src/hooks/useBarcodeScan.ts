/**
 * Barcode Scanner Hook
 *
 * Unterstützt:
 * - USB/Bluetooth Barcode-Scanner (Keyboard-Emulation)
 * - Kamera-Scan auf mobilen Geräten
 * - EAN-13, EAN-8, Code 128, Code 39, QR-Code
 */

import { useState, useEffect, useCallback, useRef } from 'react'

export interface BarcodeResult {
  /** Der gescannte Barcode-Wert */
  value: string
  /** Format des Barcodes (EAN-13, QR, etc.) */
  format: string
  /** Zeitpunkt des Scans */
  timestamp: Date
  /** Quelle: keyboard oder camera */
  source: 'keyboard' | 'camera'
}

interface UseBarcodeScanOptions {
  /** Callback bei erfolgreichem Scan */
  onScan: (result: BarcodeResult) => void
  /** Callback bei Fehler */
  onError?: (error: Error) => void
  /** Minimale Länge für gültigen Barcode */
  minLength?: number
  /** Maximale Zeit zwischen Tastendrücken (ms) */
  maxInputDelay?: number
  /** Präfix-Zeichen für Start (optional) */
  prefix?: string
  /** Suffix-Zeichen für Ende (optional) */
  suffix?: string
  /** Tastatur-Scan aktiviert */
  keyboardEnabled?: boolean
  /** Automatisch fokussieren */
  autoFocus?: boolean
}

interface UseBarcodeScanReturn {
  /** Aktueller Scan-Status */
  isScanning: boolean
  /** Letzter gescannter Wert */
  lastScan: BarcodeResult | null
  /** Scan-Historie */
  history: BarcodeResult[]
  /** Historie leeren */
  clearHistory: () => void
  /** Kamera-Scan starten (nur mobile) */
  startCameraScan: () => Promise<void>
  /** Kamera-Scan stoppen */
  stopCameraScan: () => void
  /** Kamera aktiv? */
  isCameraActive: boolean
  /** Kamera unterstützt? */
  cameraSupported: boolean
}

/**
 * Erkennt das Barcode-Format anhand des Wertes
 */
function detectBarcodeFormat(value: string): string {
  // EAN-13
  if (/^\d{13}$/.test(value)) return 'EAN-13'
  // EAN-8
  if (/^\d{8}$/.test(value)) return 'EAN-8'
  // UPC-A
  if (/^\d{12}$/.test(value)) return 'UPC-A'
  // Code 39 (alphanumerisch + spezielle Zeichen)
  if (/^[A-Z0-9.$/+% -]+$/i.test(value)) return 'CODE-39'
  // Code 128 (ASCII range)
  if ([...value].every((char) => char.charCodeAt(0) <= 127)) return 'CODE-128'
  // QR-Code (beliebiger Inhalt, oft URL oder JSON)
  if (value.startsWith('http') || value.startsWith('{')) return 'QR-CODE'

  return 'UNKNOWN'
}

/**
 * Validiert EAN/UPC Prüfziffer
 */
function validateCheckDigit(barcode: string): boolean {
  if (!/^\d+$/.test(barcode)) return true // Nicht-numerische Barcodes nicht prüfen

  const digits = barcode.split('').map(Number)
  const length = digits.length

  if (length !== 8 && length !== 12 && length !== 13) return true

  let sum = 0
  for (let i = 0; i < length - 1; i++) {
    const weight = length === 13
      ? (i % 2 === 0 ? 1 : 3)
      : (i % 2 === 0 ? 3 : 1)
    sum += digits[i] * weight
  }

  const checkDigit = (10 - (sum % 10)) % 10
  return checkDigit === digits[length - 1]
}

/**
 * Hook für Barcode-Scanner Integration
 */
export function useBarcodeScan(options: UseBarcodeScanOptions): UseBarcodeScanReturn {
  const {
    onScan,
    onError,
    minLength = 4,
    maxInputDelay = 50,
    prefix,
    suffix,
    keyboardEnabled = true,
    autoFocus = true,
  } = options

  const [isScanning, setIsScanning] = useState(false)
  const [lastScan, setLastScan] = useState<BarcodeResult | null>(null)
  const [history, setHistory] = useState<BarcodeResult[]>([])
  const [isCameraActive, setIsCameraActive] = useState(false)
  const [cameraSupported, setCameraSupported] = useState(false)

  const bufferRef = useRef<string>('')
  const lastKeyTimeRef = useRef<number>(0)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  // Prüfe Kamera-Unterstützung
  useEffect(() => {
    const checkCamera = async () => {
      try {
        const hasCamera = !!navigator.mediaDevices?.getUserMedia
        // Prüfe auch BarcodeDetector API (Chrome)
        const hasBarcodeDetector = 'BarcodeDetector' in window
        setCameraSupported(hasCamera && hasBarcodeDetector)
      } catch {
        setCameraSupported(false)
      }
    }
    checkCamera()
  }, [])

  // Verarbeite gescannten Barcode
  const processBarcode = useCallback((value: string, source: 'keyboard' | 'camera') => {
    const trimmedValue = value.trim()

    // Validierung
    if (trimmedValue.length < minLength) {
      onError?.(new Error(`Barcode zu kurz: ${trimmedValue.length} < ${minLength}`))
      return
    }

    // Präfix/Suffix entfernen wenn konfiguriert
    let processedValue = trimmedValue
    if (prefix && processedValue.startsWith(prefix)) {
      processedValue = processedValue.slice(prefix.length)
    }
    if (suffix && processedValue.endsWith(suffix)) {
      processedValue = processedValue.slice(0, -suffix.length)
    }

    const format = detectBarcodeFormat(processedValue)

    // EAN/UPC Prüfziffer validieren
    if (['EAN-13', 'EAN-8', 'UPC-A'].includes(format)) {
      if (!validateCheckDigit(processedValue)) {
        onError?.(new Error(`Ungültige Prüfziffer: ${processedValue}`))
        return
      }
    }

    const result: BarcodeResult = {
      value: processedValue,
      format,
      timestamp: new Date(),
      source,
    }

    setLastScan(result)
    setHistory(prev => [result, ...prev].slice(0, 50)) // Max 50 Einträge
    onScan(result)
  }, [minLength, prefix, suffix, onScan, onError])

  // Keyboard Event Handler
  useEffect(() => {
    if (!keyboardEnabled) return

    const handleKeyDown = (event: KeyboardEvent) => {
      const now = Date.now()
      const timeSinceLastKey = now - lastKeyTimeRef.current
      lastKeyTimeRef.current = now

      // Reset Buffer wenn zu viel Zeit vergangen
      if (timeSinceLastKey > maxInputDelay && bufferRef.current.length > 0) {
        bufferRef.current = ''
      }

      // Enter = Scan abgeschlossen
      if (event.key === 'Enter') {
        if (bufferRef.current.length >= minLength) {
          processBarcode(bufferRef.current, 'keyboard')
        }
        bufferRef.current = ''
        setIsScanning(false)
        return
      }

      // Tab ignorieren
      if (event.key === 'Tab') return

      // Nur druckbare Zeichen
      if (event.key.length === 1) {
        // Schnelle Eingabe = Scanner (nicht Mensch)
        if (timeSinceLastKey < maxInputDelay || bufferRef.current.length === 0) {
          bufferRef.current += event.key
          setIsScanning(true)

          // Timeout für Auto-Submit (falls kein Enter)
          if (timeoutRef.current) {
            clearTimeout(timeoutRef.current)
          }
          timeoutRef.current = setTimeout(() => {
            if (bufferRef.current.length >= minLength) {
              processBarcode(bufferRef.current, 'keyboard')
            }
            bufferRef.current = ''
            setIsScanning(false)
          }, 100)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [keyboardEnabled, maxInputDelay, minLength, processBarcode])

  // Auto-Focus für bessere Scanner-Erkennung
  useEffect(() => {
    if (autoFocus) {
      // Fokus auf Body setzen für globale Keyboard-Events
      document.body.focus()
    }
  }, [autoFocus])

  // Kamera-Scan starten
  const startCameraScan = useCallback(async () => {
    if (!cameraSupported) {
      onError?.(new Error('Kamera-Scan wird nicht unterstützt'))
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // Rückkamera
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      })

      streamRef.current = stream
      setIsCameraActive(true)

      // BarcodeDetector für kontinuierliches Scannen
      // @ts-expect-error BarcodeDetector ist noch nicht in allen TS-Definitionen
      const barcodeDetector = new window.BarcodeDetector({
        formats: ['ean_13', 'ean_8', 'upc_a', 'code_128', 'code_39', 'qr_code'],
      })

      // Video-Element für Stream
      const video = document.createElement('video')
      video.srcObject = stream
      video.autoplay = true
      video.playsInline = true
      videoRef.current = video

      // Scan-Loop
      const scanLoop = async () => {
        if (!streamRef.current || !videoRef.current) return

        try {
          const barcodes = await barcodeDetector.detect(videoRef.current)
          if (barcodes.length > 0) {
            const barcode = barcodes[0]
            processBarcode(barcode.rawValue, 'camera')
            stopCameraScan()
            return
          }
        } catch {
          // Frame nicht bereit, ignorieren
        }

        if (streamRef.current) {
          requestAnimationFrame(scanLoop)
        }
      }

      video.onloadedmetadata = () => {
        video.play()
        scanLoop()
      }
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error('Kamera-Zugriff verweigert'))
      setIsCameraActive(false)
    }
  }, [cameraSupported, processBarcode, onError])

  // Kamera-Scan stoppen
  const stopCameraScan = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
      videoRef.current = null
    }
    setIsCameraActive(false)
  }, [])

  // Cleanup
  useEffect(() => {
    return () => {
      stopCameraScan()
    }
  }, [stopCameraScan])

  const clearHistory = useCallback(() => {
    setHistory([])
  }, [])

  return {
    isScanning,
    lastScan,
    history,
    clearHistory,
    startCameraScan,
    stopCameraScan,
    isCameraActive,
    cameraSupported,
  }
}

/**
 * Einfacher Hook nur für Keyboard-Scanner
 */
export function useKeyboardScanner(
  onScan: (barcode: string) => void,
  options?: Partial<UseBarcodeScanOptions>
): { isScanning: boolean; lastScan: string | null } {
  const [lastScan, setLastScan] = useState<string | null>(null)

  const { isScanning } = useBarcodeScan({
    onScan: (result) => {
      setLastScan(result.value)
      onScan(result.value)
    },
    keyboardEnabled: true,
    ...options,
  })

  return { isScanning, lastScan }
}
