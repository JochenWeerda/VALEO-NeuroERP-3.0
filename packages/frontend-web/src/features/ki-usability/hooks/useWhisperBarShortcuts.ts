/**
 * WhisperBar keyboard shortcuts (Strg+Shift+1 Diktat, Strg+Shift+2 Summary)
 */

import { useEffect } from 'react'

export const WHISPERBAR_DICTATE_EVENT = 'whisperbar-dictate-start'
export const WHISPERBAR_SUMMARY_EVENT = 'whisperbar-summary-clipboard'
export const VOICE_INTENT_EVENT = 'voice-intent'
export const VOICE_SUMMARY_READY_EVENT = 'voice-summary-ready'

export type VoiceSummaryReadyDetail = {
  summaryText: string
  estimatedSeconds?: number
}

export function useWhisperBarShortcuts(enabled = true): void {
  useEffect(() => {
    if (!enabled) return

    const onKeyDown = (event: KeyboardEvent): void => {
      if (!event.ctrlKey || !event.shiftKey || event.altKey) return
      if (event.key === '1') {
        event.preventDefault()
        event.stopPropagation()
        window.dispatchEvent(new CustomEvent(WHISPERBAR_DICTATE_EVENT))
      }
      if (event.key === '2') {
        event.preventDefault()
        event.stopPropagation()
        window.dispatchEvent(new CustomEvent(WHISPERBAR_SUMMARY_EVENT))
      }
    }

    window.addEventListener('keydown', onKeyDown, true)
    return () => window.removeEventListener('keydown', onKeyDown, true)
  }, [enabled])
}
