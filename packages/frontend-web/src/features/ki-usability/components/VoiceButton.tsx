/**
 * Microphone button: start voice input → polish → summary → resolve → dispatch
 */

import { useState, useCallback } from 'react'
import { Mic, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { summarizeVoice } from '../api/voice'
import { useVoiceIntent } from '../hooks/useVoiceIntent'
import { useVoicePlayback } from '../hooks/useVoicePlayback'
import { VoiceFeedback } from './VoiceFeedback'

const SUMMARY_MIN_CHARS = 80

export interface VoiceButtonProps {
  variant?: 'default' | 'outline' | 'ghost'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  className?: string
  showFeedback?: boolean
  enablePolish?: boolean
  enableSummary?: boolean
}

export function VoiceButton({
  variant = 'ghost',
  size = 'icon',
  className,
  showFeedback = true,
  enablePolish = true,
  enableSummary = true,
}: VoiceButtonProps): JSX.Element {
  const [feedback, setFeedback] = useState<string | null>(null)
  const [feedbackVariant, setFeedbackVariant] = useState<'success' | 'error' | 'info'>('success')
  const [rawPreview, setRawPreview] = useState<string | null>(null)
  const [polishedPreview, setPolishedPreview] = useState<string | null>(null)
  const [summaryPreview, setSummaryPreview] = useState<string | null>(null)
  const [estimatedSeconds, setEstimatedSeconds] = useState<number | undefined>(undefined)
  const { playText, playing } = useVoicePlayback()

  const onResolved = useCallback((actionId: string) => {
    setFeedbackVariant('success')
    setFeedback(`Befehl ausgeführt: ${actionId}`)
  }, [])

  const onPolished = useCallback(
    async (raw: string, polished: string) => {
      setRawPreview(raw)
      setPolishedPreview(polished)
      setSummaryPreview(null)
      setEstimatedSeconds(undefined)

      if (polished !== raw) {
        setFeedbackVariant('info')
        setFeedback('Transkript poliert')
      }

      if (!enableSummary) return

      const source = polished.length >= raw.length ? polished : raw
      if (source.length < SUMMARY_MIN_CHARS) return

      const summary = await summarizeVoice({ text: source })
      if (summary?.summary_text) {
        setSummaryPreview(summary.summary_text)
        setEstimatedSeconds(summary.estimated_seconds)
      }
    },
    [enableSummary]
  )

  const onError = useCallback((msg: string) => {
    setFeedbackVariant('error')
    setFeedback(msg)
  }, [])

  const dismissFeedback = useCallback(() => {
    setFeedback(null)
    setRawPreview(null)
    setPolishedPreview(null)
    setSummaryPreview(null)
    setEstimatedSeconds(undefined)
  }, [])

  const handlePlaySummary = useCallback(async () => {
    if (!summaryPreview?.trim()) return
    await playText(summaryPreview)
  }, [summaryPreview, playText])

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
        title="Sprachbefehl (Polish + optional Zusammenfassung via Ollama)"
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
          summaryText={summaryPreview}
          estimatedSeconds={estimatedSeconds}
          onPlaySummary={summaryPreview ? handlePlaySummary : undefined}
          playingSummary={playing}
          variant={feedbackVariant}
          onDismiss={dismissFeedback}
        />
      )}
    </>
  )
}
