import { useEffect, useRef, useState, useCallback } from 'react'
import { Camera, CameraOff, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

export interface BarcodeScanResult {
  rawValue: string
  format: string
}

interface BarcodeScannerProps {
  onScan: (_result: BarcodeScanResult) => void
  onError?: (_error: string) => void
  /** Restart scanning after each successful scan */
  continuous?: boolean
  /** CSS class for the video container */
  className?: string
}

type ScannerState = 'idle' | 'requesting' | 'scanning' | 'error' | 'unsupported'

type DetectedBarcode = {
  rawValue: string
  format: string
}

type BarcodeDetectorInstance = {
  detect: (image: HTMLVideoElement) => Promise<DetectedBarcode[]>
}

type BarcodeDetectorConstructor = new (options: { formats: string[] }) => BarcodeDetectorInstance

/**
 * Camera-based barcode/QR scanner using the BarcodeDetector Web API.
 * Falls back to a visible error if the API is unavailable.
 * Optimised for warehouse scanners and tablets (high contrast UI, 56px buttons).
 */
export function BarcodeScanner({ onScan, onError, continuous = false, className }: BarcodeScannerProps): JSX.Element {
  const [state, setState] = useState<ScannerState>(() =>
    typeof window !== 'undefined' && 'BarcodeDetector' in window ? 'idle' : 'unsupported',
  )
  const [errorMsg, setErrorMsg] = useState<string>('')
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const detectorRef = useRef<BarcodeDetectorInstance | null>(null)
  const animFrameRef = useRef<number>(0)
  const activeRef = useRef(false)

  const stopStream = useCallback((): void => {
    activeRef.current = false
    cancelAnimationFrame(animFrameRef.current)
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
  }, [])

  const startScanning = useCallback(async (): Promise<void> => {
    setState('requesting')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }

      if (!detectorRef.current) {
        const BarcodeDetector = (window as Window & { BarcodeDetector?: BarcodeDetectorConstructor }).BarcodeDetector
        if (!BarcodeDetector) {
          setState('unsupported')
          return
        }
        detectorRef.current = new BarcodeDetector({
          formats: ['qr_code', 'ean_13', 'ean_8', 'code_128', 'code_39', 'data_matrix', 'upc_a', 'upc_e'],
        })
      }

      setState('scanning')
      activeRef.current = true

      const detect = async (): Promise<void> => {
        const detector = detectorRef.current
        if (!activeRef.current || !videoRef.current || !detector) return
        try {
          const barcodes = await detector.detect(videoRef.current)
          if (barcodes.length > 0) {
            const result: BarcodeScanResult = {
              rawValue: barcodes[0].rawValue,
              format: barcodes[0].format,
            }
            onScan(result)
            if (!continuous) {
              stopStream()
              setState('idle')
              return
            }
          }
        } catch {
          // detection frame error — continue
        }
        animFrameRef.current = requestAnimationFrame(() => { void detect() })
      }

      void detect()
    } catch (_rawErr: unknown) {
      const err = _rawErr as { response?: { data?: { detail?: string } }; message?: string; name?: string }
      const msg = err instanceof Error ? err.message : 'Kamerazugriff verweigert'
      setErrorMsg(msg)
      onError?.(msg)
      setState('error')
    }
  }, [continuous, onScan, onError, stopStream])

  useEffect(() => {
    return () => {
      stopStream()
    }
  }, [stopStream])

  if (state === 'unsupported') {
    return (
      <div className={`flex flex-col items-center gap-3 rounded-lg border border-orange-300 bg-orange-50 p-6 text-center ${className ?? ''}`} role="alert">
        <CameraOff className="h-10 w-10 text-orange-500" aria-hidden="true" />
        <p className="font-medium text-orange-900">Scanner nicht verfügbar</p>
        <p className="text-sm text-orange-700">
          Dieser Browser unterstützt die BarcodeDetector Web API nicht.
          Bitte Chrome 88+ oder Edge 88+ verwenden.
        </p>
      </div>
    )
  }

  return (
    <div className={`flex flex-col gap-3 ${className ?? ''}`}>
      {/* Video preview */}
      <div className="relative overflow-hidden rounded-lg bg-black aspect-video">
        <video
          ref={videoRef}
          className="h-full w-full object-cover"
          playsInline
          muted
          aria-label="Kameraansicht für Barcode-Scan"
        />
        {state === 'scanning' && (
          <div
            className="pointer-events-none absolute inset-x-4 top-1/2 h-0.5 -translate-y-1/2 animate-pulse bg-primary/70"
            aria-hidden="true"
          />
        )}
        {state === 'requesting' && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <Loader2 className="h-8 w-8 animate-spin text-white" aria-hidden="true" />
          </div>
        )}
      </div>

      {state === 'error' && (
        <p role="alert" className="text-sm text-red-600">{errorMsg}</p>
      )}

      <Button
        type="button"
        size="lg"
        className="h-14 w-full gap-2 text-base"
        onClick={() => {
          if (state === 'scanning') {
            stopStream()
            setState('idle')
          } else {
            void startScanning()
          }
        }}
        disabled={state === 'requesting'}
        aria-label={state === 'scanning' ? 'Scanner stoppen' : 'Scanner starten'}
      >
        {state === 'requesting' ? (
          <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
        ) : state === 'scanning' ? (
          <CameraOff className="h-5 w-5" aria-hidden="true" />
        ) : (
          <Camera className="h-5 w-5" aria-hidden="true" />
        )}
        {state === 'scanning' ? 'Scanner stoppen' : 'Scanner starten'}
      </Button>
    </div>
  )
}
