/**
 * Headless WhisperBar host: global shortcuts, voice-intent events, clipboard summary.
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { runVoicePipeline } from '../api/voice'
import { useVoiceIntent } from '../hooks/useVoiceIntent'
import { useVoicePlayback } from '../hooks/useVoicePlayback'
import {
  useWhisperBarShortcuts,
  VOICE_INTENT_EVENT,
  VOICE_SUMMARY_READY_EVENT,
  WHISPERBAR_DICTATE_EVENT,
  WHISPERBAR_SUMMARY_EVENT,
} from '../hooks/useWhisperBarShortcuts'
import { VoiceFeedback } from './VoiceFeedback'

export interface VoiceWhisperBarHostProps {
  enabled?: boolean
}

export function VoiceWhisperBarHost({ enabled = true }: VoiceWhisperBarHostProps): JSX.Element | null {
  const [voiceDomain, setVoiceDomain] = useState<string | undefined>(undefined)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [feedbackVariant, setFeedbackVariant] = useState<'success' | 'error' | 'info'>('info')
  const [rawPreview, setRawPreview] = useState<string | null>(null)
  const [polishedPreview, setPolishedPreview] = useState<string | null>(null)
  const [summaryPreview, setSummaryPreview] = useState<string | null>(null)
  const [estimatedSeconds, setEstimatedSeconds] = useState<number | undefined>(undefined)
  const [summaryBusy, setSummaryBusy] = useState(false)
  const startRef = useRef<(() => void) | null>(null)

  const { playText, playing } = useVoicePlayback()
  useWhisperBarShortcuts(enabled)

  const dismissFeedback = useCallback(() => {
    setFeedback(null)
    setRawPreview(null)
    setPolishedPreview(null)
    setSummaryPreview(null)
    setEstimatedSeconds(undefined)
  }, [])

  const onResolved = useCallback((actionId: string) => {
    setFeedbackVariant('success')
    setFeedback(`Befehl ausgeführt: ${actionId}`)
  }, [])

  const onPolished = useCallback((raw: string, polished: string) => {
    setRawPreview(raw)
    setPolishedPreview(polished)
    if (polished !== raw) {
      setFeedbackVariant('info')
      setFeedback('Diktat poliert')
    }
  }, [])

  const onError = useCallback((message: string) => {
    setFeedbackVariant('error')
    setFeedback(message)
  }, [])

  const { startListening } = useVoiceIntent({
    minConfidence: 0.7,
    enablePolish: true,
    domain: voiceDomain,
    onResolved,
    onPolished,
    onError,
  })

  useEffect(() => {
    startRef.current = startListening
  }, [startListening])

  const handleDictateStart = useCallback(() => {
    dismissFeedback()
    startRef.current?.()
  }, [dismissFeedback])

  const handleSummaryClipboard = useCallback(async () => {
    dismissFeedback()
    setSummaryBusy(true)
    try {
      let text = ''
      try {
        text = (await navigator.clipboard.readText()).trim()
      } catch {
        toast.error('Zwischenablage nicht lesbar — Berechtigung prüfen.')
        return
      }
      if (!text) {
        toast.error('Zwischenablage ist leer.')
        return
      }

      const result = await runVoicePipeline({ mode: 'summary', text })
      if (!result?.summary_text) {
        toast.error(result?.error ?? 'Zusammenfassung fehlgeschlagen.')
        return
      }

      try {
        await navigator.clipboard.writeText(result.summary_text)
      } catch {
        // Clipboard write optional — UI still shows summary
      }

      setSummaryPreview(result.summary_text)
      setEstimatedSeconds(result.estimated_seconds)
      setFeedbackVariant('info')
      setFeedback('Zusammenfassung erstellt (in Zwischenablage)')

      window.dispatchEvent(
        new CustomEvent(VOICE_SUMMARY_READY_EVENT, {
          detail: {
            summaryText: result.summary_text,
            estimatedSeconds: result.estimated_seconds,
          },
        }),
      )
    } catch {
      toast.error('Summary-Pipeline fehlgeschlagen.')
    } finally {
      setSummaryBusy(false)
    }
  }, [dismissFeedback])

  const handleVoiceIntent = useCallback((event: Event) => {
    const detail = (event as CustomEvent<{ domain?: string }>).detail
    setVoiceDomain(typeof detail?.domain === 'string' ? detail.domain : undefined)
    handleDictateStart()
  }, [handleDictateStart])

  useEffect(() => {
    if (!enabled) return
    window.addEventListener(WHISPERBAR_DICTATE_EVENT, handleDictateStart)
    window.addEventListener(WHISPERBAR_SUMMARY_EVENT, handleSummaryClipboard)
    window.addEventListener(VOICE_INTENT_EVENT, handleVoiceIntent as EventListener)
    return () => {
      window.removeEventListener(WHISPERBAR_DICTATE_EVENT, handleDictateStart)
      window.removeEventListener(WHISPERBAR_SUMMARY_EVENT, handleSummaryClipboard)
      window.removeEventListener(VOICE_INTENT_EVENT, handleVoiceIntent as EventListener)
    }
  }, [enabled, handleDictateStart, handleSummaryClipboard, handleVoiceIntent])

  const handlePlaySummary = useCallback(async () => {
    if (!summaryPreview?.trim()) return
    await playText(summaryPreview)
  }, [summaryPreview, playText])

  if (!enabled || !feedback) return null

  return (
    <VoiceFeedback
      message={feedback}
      rawText={rawPreview}
      polishedText={polishedPreview}
      summaryText={summaryPreview}
      estimatedSeconds={estimatedSeconds}
      onPlaySummary={summaryPreview ? handlePlaySummary : undefined}
      playingSummary={playing || summaryBusy}
      variant={feedbackVariant}
      onDismiss={dismissFeedback}
      autoHideMs={8000}
    />
  )
}
