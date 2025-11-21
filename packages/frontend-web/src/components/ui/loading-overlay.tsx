import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

interface LoadingOverlayProps {
  isVisible: boolean
  message?: string
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function LoadingOverlay({
  isVisible,
  message = 'Lädt...',
  className,
  size = 'md'
}: LoadingOverlayProps): JSX.Element | null {
  if (!isVisible) return null

  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  }

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm',
        className
      )}
    >
      <div className="flex flex-col items-center gap-4 rounded-lg bg-card p-6 shadow-lg">
        <Loader2 className={cn('animate-spin text-primary', sizeClasses[size])} />
        {message && (
          <p className="text-sm text-muted-foreground">{message}</p>
        )}
      </div>
    </div>
  )
}

interface InlineLoaderProps {
  message?: string
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function InlineLoader({
  message = 'Lädt...',
  className,
  size = 'md'
}: InlineLoaderProps): JSX.Element {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  }

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Loader2 className={cn('animate-spin text-primary', sizeClasses[size])} />
      {message && (
        <span className="text-sm text-muted-foreground">{message}</span>
      )}
    </div>
  )
}

interface SkeletonLoaderProps {
  className?: string
  lines?: number
}

export function SkeletonLoader({
  className,
  lines = 3
}: SkeletonLoaderProps): JSX.Element {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 animate-pulse rounded bg-muted"
          style={{
            width: i === lines - 1 ? '60%' : '100%'
          }}
        />
      ))}
    </div>
  )
}