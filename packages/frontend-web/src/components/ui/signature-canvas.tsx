import { forwardRef, useCallback, useEffect, useImperativeHandle, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Eraser, Pen, RotateCcw } from 'lucide-react'

export interface SignatureCanvasRef {
  clear: () => void
  isEmpty: () => boolean
  toDataURL: (type?: string, quality?: number) => string
  toBlob: (callback: (blob: Blob | null) => void, type?: string, quality?: number) => void
}

interface SignatureCanvasProps {
  width?: number
  height?: number
  className?: string
  strokeColor?: string
  strokeWidth?: number
  backgroundColor?: string
  disabled?: boolean
  onChange?: (isEmpty: boolean) => void
  onEnd?: () => void
}

export const SignatureCanvas = forwardRef<SignatureCanvasRef, SignatureCanvasProps>(
  function SignatureCanvas(
    {
      width = 400,
      height = 200,
      className,
      strokeColor = '#000000',
      strokeWidth = 2,
      backgroundColor = '#ffffff',
      disabled = false,
      onChange,
      onEnd,
    },
    ref
  ) {
    const canvasRef = useRef<HTMLCanvasElement>(null)
    const [isDrawing, setIsDrawing] = useState(false)
    const [isEmpty, setIsEmpty] = useState(true)
    const lastPointRef = useRef<{ x: number; y: number } | null>(null)
    const rectCacheRef = useRef<DOMRect | null>(null)

    const getContext = useCallback(() => {
      const canvas = canvasRef.current
      if (!canvas) return null
      return canvas.getContext('2d')
    }, [])

    const clearCanvas = useCallback(() => {
      const canvas = canvasRef.current
      const ctx = getContext()
      if (!canvas || !ctx) return

      ctx.fillStyle = backgroundColor
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      setIsEmpty(true)
      onChange?.(true)
    }, [backgroundColor, getContext, onChange])

    // Initialize canvas
    useEffect(() => {
      const canvas = canvasRef.current
      const ctx = getContext()
      if (!canvas || !ctx) return

      // Set canvas dimensions
      canvas.width = width
      canvas.height = height

      // Fill with background color
      ctx.fillStyle = backgroundColor
      ctx.fillRect(0, 0, width, height)

      // Set drawing styles
      ctx.strokeStyle = strokeColor
      ctx.lineWidth = strokeWidth
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
    }, [width, height, backgroundColor, strokeColor, strokeWidth, getContext])

    const getCoordinates = useCallback(
      (
        e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>,
        rect?: DOMRect
      ) => {
        const canvas = canvasRef.current
        if (!canvas) return null

        const r = rect ?? rectCacheRef.current ?? canvas.getBoundingClientRect()
        if (!rect) rectCacheRef.current = r
        const scaleX = canvas.width / r.width
        const scaleY = canvas.height / r.height

        if ('touches' in e) {
          const touch = e.touches[0]
          if (!touch) return null
          return {
            x: (touch.clientX - r.left) * scaleX,
            y: (touch.clientY - r.top) * scaleY,
          }
        }

        return {
          x: (e.clientX - r.left) * scaleX,
          y: (e.clientY - r.top) * scaleY,
        }
      },
      []
    )

    const startDrawing = useCallback(
      (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
        if (disabled) return
        e.preventDefault()

        const canvas = canvasRef.current
        if (canvas) rectCacheRef.current = canvas.getBoundingClientRect()

        const coords = getCoordinates(e)
        if (!coords) return

        setIsDrawing(true)
        lastPointRef.current = coords

        const ctx = getContext()
        if (ctx) {
          ctx.beginPath()
          ctx.moveTo(coords.x, coords.y)
        }
      },
      [disabled, getCoordinates, getContext]
    )

    const draw = useCallback(
      (e: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>) => {
        if (!isDrawing || disabled) return
        e.preventDefault()

        const coords = getCoordinates(e)
        const ctx = getContext()
        if (!coords || !ctx || !lastPointRef.current) return

        // Draw line from last point to current point
        ctx.strokeStyle = strokeColor
        ctx.lineWidth = strokeWidth
        ctx.beginPath()
        ctx.moveTo(lastPointRef.current.x, lastPointRef.current.y)
        ctx.lineTo(coords.x, coords.y)
        ctx.stroke()

        lastPointRef.current = coords

        if (isEmpty) {
          setIsEmpty(false)
          onChange?.(false)
        }
      },
      [isDrawing, disabled, getCoordinates, getContext, strokeColor, strokeWidth, isEmpty, onChange]
    )

    const stopDrawing = useCallback(() => {
      if (isDrawing) {
        setIsDrawing(false)
        lastPointRef.current = null
        rectCacheRef.current = null
        onEnd?.()
      }
    }, [isDrawing, onEnd])

    // Expose methods via ref
    useImperativeHandle(
      ref,
      () => ({
        clear: clearCanvas,
        isEmpty: () => isEmpty,
        toDataURL: (type = 'image/png', quality = 1) => {
          const canvas = canvasRef.current
          if (!canvas) return ''
          return canvas.toDataURL(type, quality)
        },
        toBlob: (callback, type = 'image/png', quality = 1) => {
          const canvas = canvasRef.current
          if (!canvas) {
            callback(null)
            return
          }
          canvas.toBlob(callback, type, quality)
        },
      }),
      [clearCanvas, isEmpty]
    )

    return (
      <div className={cn('flex flex-col gap-2', className)}>
        <div className="relative rounded-lg border border-input bg-background overflow-hidden">
          <canvas
            ref={canvasRef}
            className={cn(
              'w-full touch-none cursor-crosshair',
              disabled && 'cursor-not-allowed opacity-50'
            )}
            style={{
              aspectRatio: `${width}/${height}`,
            }}
            onMouseDown={startDrawing}
            onMouseMove={draw}
            onMouseUp={stopDrawing}
            onMouseLeave={stopDrawing}
            onTouchStart={startDrawing}
            onTouchMove={draw}
            onTouchEnd={stopDrawing}
          />
          {isEmpty && !disabled && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="flex items-center gap-2 text-muted-foreground/50">
                <Pen className="h-5 w-5" />
                <span className="text-sm">Hier unterschreiben</span>
              </div>
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={clearCanvas}
            disabled={disabled || isEmpty}
          >
            <RotateCcw className="h-4 w-4 mr-1" />
            Löschen
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={clearCanvas}
            disabled={disabled || isEmpty}
          >
            <Eraser className="h-4 w-4 mr-1" />
            Neu
          </Button>
        </div>
      </div>
    )
  }
)

