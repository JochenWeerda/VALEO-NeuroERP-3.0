import { useCallback, useEffect, useRef, useState } from 'react'
import type { SttError, SttProvider, VoiceTelemetry } from './stt-provider'

/**
 * Diktat-Zustand (UIX-072). Kapselt einen SttProvider: Aufnahme starten/stoppen,
 * partielle Transkripte live anzeigen, finalen Text editierbar halten und erst
 * bei Bestaetigung uebernehmen. Kein Audio-Persist; Telemetrie ohne Inhalt.
 */
export interface UseVoiceDictationResult {
  available: boolean
  listening: boolean
  /** Aktuelles (partielles oder finales) Transkript — editierbar vor Uebernahme. */
  transcript: string
  error: SttError | null
  start: () => void
  stop: () => void
  /** Editiert das Transkript vor der Uebernahme. */
  setTranscript: (text: string) => void
  /** Uebernimmt den aktuellen Text (onCommit) und setzt zurueck. */
  commit: () => void
  cancel: () => void
}

export function useVoiceDictation(
  provider: SttProvider | null,
  options: {
    target: VoiceTelemetry['target']
    onCommit: (text: string) => void
    onTelemetry?: (t: VoiceTelemetry) => void
  },
): UseVoiceDictationResult {
  const [listening, setListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState<SttError | null>(null)
  const startedAt = useRef<number | null>(null)
  const boundProvider = useRef<SttProvider | null>(null)

  // Listener nur einmal je Provider binden.
  useEffect(() => {
    if (!provider || boundProvider.current === provider) return
    boundProvider.current = provider
    provider.onPartial((text) => setTranscript(text))
    provider.onFinal((text) => setTranscript((prev) => (text.length >= prev.length ? text : prev)))
    provider.onError((err) => {
      setError(err)
      setListening(false)
    })
  }, [provider])

  const start = useCallback(() => {
    if (!provider || !provider.isAvailable()) return
    setError(null)
    setTranscript('')
    startedAt.current = Date.now()
    setListening(true)
    provider.start({ lang: 'de-DE', interim: true })
  }, [provider])

  const stop = useCallback(() => {
    if (!provider) return
    provider.stop()
    setListening(false)
  }, [provider])

  const finishTelemetry = useCallback(
    (used: boolean) => {
      if (!provider || startedAt.current === null) return
      options.onTelemetry?.({
        used,
        provider: provider.id,
        duration_s: Math.max(0, (Date.now() - startedAt.current) / 1000),
        target: options.target,
      })
      startedAt.current = null
    },
    [provider, options],
  )

  const commit = useCallback(() => {
    const text = transcript.trim()
    stop()
    if (text.length > 0) options.onCommit(text)
    finishTelemetry(text.length > 0)
    setTranscript('')
  }, [transcript, stop, options, finishTelemetry])

  const cancel = useCallback(() => {
    stop()
    finishTelemetry(false)
    setTranscript('')
    setError(null)
  }, [stop, finishTelemetry])

  return {
    available: Boolean(provider?.isAvailable()),
    listening,
    transcript,
    error,
    start,
    stop,
    setTranscript,
    commit,
    cancel,
  }
}
