/**
 * Microphone button: start voice input → resolve → dispatch via ActionDispatchContext
 */

import { useState, useCallback } from 'react'
import { Mic, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useVoiceIntent } from '../hooks/useVoiceIntent'
import { VoiceFeedback } from './VoiceFeedback'

export interface VoiceButtonProps {
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  className?: string
  showFeedback?: boolean
}

export function VoiceButton({
  variant = 'ghost',
  size = 'icon',
  className,
  showFeedback = true,
}: VoiceButtonProps): JSX.Element {
  const [feedback, setFeedback] = useState<string | null>(null)
  const [feedbackVariant, setFeedbackVariant] = useState<'success' | 'error'>('success')

  const onResolved = useCallback(() => {
    setFeedbackVariant('success')
    setFeedback('Befehl ausgeführt.')
    setTimeout(() => setFeedback(null), 2000)
  }, [])

  const onError = useCallback((msg: string) => {
    setFeedbackVariant('error')
    setFeedback(msg)
    setTimeout(() => setFeedback(null), 3000)
  }, [])

  const { startListening, listening } = useVoiceIntent({
    minConfidence: 0.7,
    onResolved,
    onError,
  })

  return (
    <>
      <Button
        variant={variant}
        size={size}
        className={className}
        onClick={startListening}
        disabled={listening}
        aria-label={listening ? 'Höre zu…' : 'Sprachbefehl starten'}
        title="Sprachbefehl (z. B. „Speichern“, „Aufträge öffnen“)"
      >
        {listening ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Mic className="h-4 w-4" />
        )}
      </Button>
      {showFeedback && feedback && (
        <VoiceFeedback
          message={feedback}
          variant={feedbackVariant}
          onDismiss={() => setFeedback(null)}
        />
      )}
    </>
  )
}
