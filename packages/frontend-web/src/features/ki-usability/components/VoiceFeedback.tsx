/**
 * Toast-like feedback for voice result (success or error)
 */

import { useEffect } from 'react'
import { cn } from '@/lib/utils'

export interface VoiceFeedbackProps {
  message: string
  variant?: 'success' | 'error'
  onDismiss: () => void
  autoHideMs?: number
}

export function VoiceFeedback({
  message,
  variant = 'success',
  onDismiss,
  autoHideMs = 2500,
}: VoiceFeedbackProps): JSX.Element {
  useEffect(() => {
    const t = setTimeout(onDismiss, autoHideMs)
    return () => clearTimeout(t)
  }, [onDismiss, autoHideMs])

  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        'fixed bottom-20 left-1/2 z-50 -translate-x-1/2 rounded-lg px-4 py-2 text-sm shadow-lg',
        variant === 'success' && 'bg-primary text-primary-foreground',
        variant === 'error' && 'bg-destructive text-destructive-foreground'
      )}
    >
      {message}
    </div>
  )
}
