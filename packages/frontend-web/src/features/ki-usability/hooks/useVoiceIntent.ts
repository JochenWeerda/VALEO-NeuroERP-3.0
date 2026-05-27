/**
 * Microphone → transcribe (Web Speech API) → polish (Ollama) → resolve → dispatch
 */

import { useCallback, useState } from 'react'
import { polishVoice, resolveVoice } from '../api/voice'
import { useActionDispatchOptional } from '../context/ActionDispatchHooks'

export interface UseVoiceIntentOptions {
  /** Min confidence to dispatch (default 0.7) */
  minConfidence?: number
  /** Polish transcript via Ollama before intent resolve (default true) */
  enablePolish?: boolean
  /** Callback when intent resolved (before dispatch) */
  onResolved?: (actionId: string, params: Record<string, unknown>, confidence: number) => void
  /** Callback after polish step with raw and polished text */
  onPolished?: (raw: string, polished: string) => void
  /** Callback on error or no match */
  onError?: (message: string) => void
}

export function useVoiceIntent(options: UseVoiceIntentOptions = {}) {
  const { minConfidence = 0.7, enablePolish = true, onResolved, onPolished, onError } = options
  const dispatchContext = useActionDispatchOptional()
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState<string | null>(null)
  const [polishedTranscript, setPolishedTranscript] = useState<string | null>(null)
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
      const raw = (e.results?.[0]?.[0]?.transcript ?? '').trim()
      setTranscript(raw)
      setPolishedTranscript(null)
      if (!raw) return

      let textForResolve = raw
      if (enablePolish) {
        const polished = await polishVoice({ text: raw, tone: 'business' })
        if (polished?.polished_text) {
          textForResolve = polished.polished_text
          setPolishedTranscript(polished.polished_text)
          onPolished?.(raw, polished.polished_text)
        }
      }

      const result = await resolveVoice({ text: textForResolve, context: {} })
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
  }, [minConfidence, enablePolish, onResolved, onPolished, onError, dispatchContext])

  const reset = useCallback(() => {
    setTranscript(null)
    setPolishedTranscript(null)
    setResolvedAction(null)
  }, [])

  return {
    startListening,
    listening,
    transcript,
    polishedTranscript,
    resolvedAction,
    reset,
  }
}
