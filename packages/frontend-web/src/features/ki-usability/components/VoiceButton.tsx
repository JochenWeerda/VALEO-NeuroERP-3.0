/**
 * Microphone button: start voice input → polish → resolve → dispatch
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
  enablePolish?: boolean
}

export function VoiceButton({
  variant = 'ghost',
  size = 'icon',
  className,
  showFeedback = true,
  enablePolish = true,
}: VoiceButtonProps): JSX.Element {
  const [feedback, setFeedback] = useState<string | null>(null)
  const [feedbackVariant, setFeedbackVariant] = useState<'success' | 'error' | 'info'>('success')
  const [rawPreview, setRawPreview] = useState<string | null>(null)
  const [polishedPreview, setPolishedPreview] = useState<string | null>(null)

  const onResolved = useCallback((actionId: string) => {
    setFeedbackVariant('success')
    setFeedback(`Befehl ausgeführt: ${actionId}`)
  }, [])

  const onPolished = useCallback((raw: string, polished: string) => {
    setRawPreview(raw)
    setPolishedPreview(polished)
    if (polished !== raw) {
      setFeedbackVariant('info')
      setFeedback('Transkript poliert')
    }
  }, [])

  const onError = useCallback((msg: string) => {
    setFeedbackVariant('error')
    setFeedback(msg)
  }, [])

  const dismissFeedback = useCallback(() => {
    setFeedback(null)
    setRawPreview(null)
    setPolishedPreview(null)
  }, [])

  const { startListening, listening } = useVoiceIntent({
    minConfidence: 0.7,
    enablePolish,
    onResolved,
    onPolished,
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
        title="Sprachbefehl (Diktat wird optional per Ollama poliert)"
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
          rawText={rawPreview}
          polishedText={polishedPreview}
          variant={feedbackVariant}
          onDismiss={dismissFeedback}
        />
      )}
    </>
  )
}
