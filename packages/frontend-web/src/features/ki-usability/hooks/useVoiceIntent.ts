/**
 * Microphone → transcribe (Web Speech API) → resolve (ki-usability-api) → dispatch
 */

import { useCallback, useState } from 'react'
import { resolveVoice } from '../api/voice'
import { useActionDispatchOptional } from '../context/ActionDispatchContext'

export interface UseVoiceIntentOptions {
  /** Min confidence to dispatch (default 0.7) */
  minConfidence?: number
  /** Callback when intent resolved (before dispatch) */
  onResolved?: (actionId: string, params: Record<string, unknown>, confidence: number) => void
  /** Callback on error or no match */
  onError?: (message: string) => void
}

export function useVoiceIntent(options: UseVoiceIntentOptions = {}) {
  const { minConfidence = 0.7, onResolved, onError } = options
  const dispatchContext = useActionDispatchOptional()
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState<string | null>(null)
  const [resolvedAction, setResolvedAction] = useState<string | null>(null)

  const startListening = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      onError?.('Spracherkennung wird in diesem Browser nicht unterstützt.')
      return
    }
    const Recognition = (window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition
    const recognition = new Recognition()
    recognition.lang = 'de-DE'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => setListening(true)
    recognition.onend = () => setListening(false)
    recognition.onerror = (e: any) => {
      setListening(false)
      onError?.(e.error === 'no-speech' ? 'Keine Sprache erkannt.' : 'Spracherkennung fehlgeschlagen.')
    }
    recognition.onresult = async (e: any) => {
      const text = e.results?.[0]?.[0]?.transcript ?? ''
      setTranscript(text)
      if (!text.trim()) return

      const result = await resolveVoice({ text: text.trim(), context: {} })
      if (!result) {
        onError?.('Befehl nicht erkannt.')
        setResolvedAction(null)
        return
      }
      setResolvedAction(result.action_id)
      onResolved?.(result.action_id, result.params, result.confidence)

      if (result.confidence >= minConfidence && dispatchContext) {
        const ok = await dispatchContext.dispatch(result.action_id, result.params)
        if (!ok) onError?.('Aktion konnte nicht ausgeführt werden.')
      } else if (result.confidence < minConfidence) {
        onError?.('Befehl unsicher erkannt. Bitte wiederholen.')
      } else {
        onError?.('Dispatcher nicht verfügbar.')
      }
    }

    recognition.start()
  }, [minConfidence, onResolved, onError, dispatchContext])

  const reset = useCallback(() => {
    setTranscript(null)
    setResolvedAction(null)
  }, [])

  return { startListening, listening, transcript, resolvedAction, reset }
}
