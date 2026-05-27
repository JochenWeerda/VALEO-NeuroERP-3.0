/**
 * Toast-like feedback for voice result (success or error)
 * Slice-013: optional raw + polished transcript preview
 */

import { useEffect } from 'react'
import { cn } from '@/lib/utils'

export interface VoiceFeedbackProps {
  message?: string
  rawText?: string | null
  polishedText?: string | null
  variant?: 'success' | 'error' | 'info'
  onDismiss: () => void
  autoHideMs?: number
}

export function VoiceFeedback({
  message,
  rawText,
  polishedText,
  variant = 'success',
  onDismiss,
  autoHideMs = 4000,
}: VoiceFeedbackProps): JSX.Element {
  useEffect(() => {
    const t = setTimeout(onDismiss, autoHideMs)
    return () => clearTimeout(t)
  }, [onDismiss, autoHideMs])

  const showTranscript = Boolean(rawText?.trim() || polishedText?.trim())

  return (
    <div
      role="status"
      aria-live="polite"
      data-testid="voice-feedback"
      className={cn(
        'fixed bottom-20 left-1/2 z-50 w-[min(92vw,28rem)] -translate-x-1/2 rounded-lg px-4 py-3 text-sm shadow-lg',
        variant === 'success' && 'bg-primary text-primary-foreground',
        variant === 'error' && 'bg-destructive text-destructive-foreground',
        variant === 'info' && 'border border-border bg-background text-foreground'
      )}
    >
      {message ? <p className="font-medium">{message}</p> : null}
      {showTranscript ? (
        <div className={cn('space-y-2', message ? 'mt-2 border-t border-white/20 pt-2' : '')}>
          {rawText?.trim() ? (
            <div data-testid="voice-feedback-raw">
              <span className="text-xs opacity-80">Rohtext</span>
              <p className="text-xs leading-snug opacity-95">{rawText}</p>
            </div>
          ) : null}
          {polishedText?.trim() && polishedText !== rawText ? (
            <div data-testid="voice-feedback-polished">
              <span className="text-xs font-semibold opacity-90">Poliert</span>
              <p className="text-xs leading-snug">{polishedText}</p>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
