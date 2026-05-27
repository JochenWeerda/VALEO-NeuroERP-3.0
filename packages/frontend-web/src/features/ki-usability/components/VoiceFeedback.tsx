/**
 * Toast-like feedback for voice result (success or error)
 * Slice-013: raw + polished transcript; Slice-013b: summary + play
 */

import { useEffect } from 'react'
import { Volume2, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

export interface VoiceFeedbackProps {
  message?: string
  rawText?: string | null
  polishedText?: string | null
  summaryText?: string | null
  estimatedSeconds?: number
  onPlaySummary?: () => void
  playingSummary?: boolean
  variant?: 'success' | 'error' | 'info'
  onDismiss: () => void
  autoHideMs?: number
}

export function VoiceFeedback({
  message,
  rawText,
  polishedText,
  summaryText,
  estimatedSeconds,
  onPlaySummary,
  playingSummary = false,
  variant = 'success',
  onDismiss,
  autoHideMs = 6000,
}: VoiceFeedbackProps): JSX.Element {
  useEffect(() => {
    const t = setTimeout(onDismiss, autoHideMs)
    return () => clearTimeout(t)
  }, [onDismiss, autoHideMs])

  const showTranscript = Boolean(rawText?.trim() || polishedText?.trim())
  const showSummary = Boolean(summaryText?.trim())

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
      {showSummary ? (
        <div
          data-testid="voice-feedback-summary"
          className={cn(
            'space-y-2',
            message || showTranscript ? 'mt-2 border-t border-white/20 pt-2' : ''
          )}
        >
          <div className="flex items-start justify-between gap-2">
            <div>
              <span className="text-xs font-semibold opacity-90">
                Zusammenfassung
                {estimatedSeconds ? ` (~${estimatedSeconds}s)` : ''}
              </span>
              <p className="text-xs leading-snug">{summaryText}</p>
            </div>
            {onPlaySummary ? (
              <Button
                type="button"
                size="icon"
                variant="secondary"
                className="h-7 w-7 shrink-0"
                disabled={playingSummary}
                aria-label="Zusammenfassung vorlesen"
                onClick={onPlaySummary}
              >
                {playingSummary ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Volume2 className="h-3.5 w-3.5" />
                )}
              </Button>
            ) : null}
          </div>
        </div>
      ) : null}
    </div>
  )
}
