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
  /** Optional domain scope for intent resolution */
  domain?: string
  /** Callback when intent resolved (before dispatch) */
  onResolved?: (actionId: string, params: Record<string, unknown>, confidence: number) => void
  /** Callback after polish step with raw and polished text */
  onPolished?: (raw: string, polished: string) => void
  /** Callback on error or no match */
  onError?: (message: string) => void
}

export function useVoiceIntent(options: UseVoiceIntentOptions = {}) {
  const { minConfidence = 0.7, enablePolish = true, domain, onResolved, onPolished, onError } = options
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
    // vendor-prefixed experimental API — no stable TS types yet
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const Recognition = ((window as any).SpeechRecognition ?? (window as any).webkitSpeechRecognition) as new () => any
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const recognition: any = new Recognition()
    recognition.lang = 'de-DE'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => setListening(true)
    recognition.onend = () => setListening(false)
    recognition.onerror = (e: { error: string }) => {
      setListening(false)
      onError?.(e.error === 'no-speech' ? 'Keine Sprache erkannt.' : 'Spracherkennung fehlgeschlagen.')
    }
    recognition.onresult = async (e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => {
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

      const result = await resolveVoice({
        text: textForResolve,
        context: domain ? { domain } : {},
      })
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
  }, [minConfidence, enablePolish, domain, onResolved, onPolished, onError, dispatchContext])

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
