/**
 * Copilot-Dock: Voice-Summary aus WhisperBar (Slice-015d)
 */

import { useCallback, useEffect, useState } from 'react'
import { useVoicePlayback } from '@/features/ki-usability/hooks/useVoicePlayback'
import {
  VOICE_SUMMARY_READY_EVENT,
  type VoiceSummaryReadyDetail,
} from '@/features/ki-usability/hooks/useWhisperBarShortcuts'

export function useVoiceCopilotSummary(): {
  summary: VoiceSummaryReadyDetail | null
  playSummary: () => Promise<void>
  playing: boolean
  clearSummary: () => void
} {
  const [summary, setSummary] = useState<VoiceSummaryReadyDetail | null>(null)
  const { playText, playing } = useVoicePlayback()

  useEffect(() => {
    const handler = (event: Event): void => {
      const detail = (event as CustomEvent<VoiceSummaryReadyDetail>).detail
      if (typeof detail?.summaryText === 'string' && detail.summaryText.trim().length > 0) {
        setSummary({
          summaryText: detail.summaryText,
          estimatedSeconds: detail.estimatedSeconds,
        })
      }
    }
    window.addEventListener(VOICE_SUMMARY_READY_EVENT, handler)
    return () => window.removeEventListener(VOICE_SUMMARY_READY_EVENT, handler)
  }, [])

  const playSummary = useCallback(async (): Promise<void> => {
    const text = summary?.summaryText?.trim()
    if (!text) return
    await playText(text)
  }, [summary, playText])

  const clearSummary = useCallback((): void => {
    setSummary(null)
  }, [])

  return { summary, playSummary, playing, clearSummary }
}
