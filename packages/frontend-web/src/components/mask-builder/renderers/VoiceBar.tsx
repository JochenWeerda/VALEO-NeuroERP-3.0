import { useEffect, useRef, useState } from 'react'
import { Mic, Check, X } from 'lucide-react'
import { useVoiceDictation } from '@/lib/voice/useVoiceDictation'
import type { SttProvider, VoiceTelemetry } from '@/lib/voice/stt-provider'

/**
 * VoiceBar (UIX-072): Push-to-talk-Diktat. Das Transkript ist immer sichtbar und
 * editierbar; Uebernahme erst bei Bestaetigung (kein Auto-Submit, keine Aktion).
 * Respektiert prefers-reduced-motion (kein pulsierendes Mikro).
 */
function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false)
  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReduced(mq.matches)
    const handler = (e: MediaQueryListEvent) => setReduced(e.matches)
    mq.addEventListener?.('change', handler)
    return () => mq.removeEventListener?.('change', handler)
  }, [])
  return reduced
}

export function VoiceBar({
  provider,
  target,
  onCommit,
  onTelemetry,
  label = 'Diktat',
  enableGlobalShortcut = true,
}: {
  provider: SttProvider | null
  target: VoiceTelemetry['target']
  onCommit: (text: string) => void
  onTelemetry?: (t: VoiceTelemetry) => void
  label?: string
  enableGlobalShortcut?: boolean
}): JSX.Element | null {
  const reducedMotion = usePrefersReducedMotion()
  const { available, listening, transcript, error, start, commit, cancel, setTranscript } = useVoiceDictation(provider, {
    target,
    onCommit,
    onTelemetry,
  })
  const inputRef = useRef<HTMLInputElement>(null)

  // Alt+V toggelt die Aufnahme (Tastatur-Bedienbarkeit).
  useEffect(() => {
    if (!enableGlobalShortcut) return
    const handler = (e: KeyboardEvent) => {
      if (e.altKey && e.key.toLowerCase() === 'v') {
        e.preventDefault()
        if (listening) commit()
        else start()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [enableGlobalShortcut, listening, start, commit])

  if (!available) return null

  const showTranscript = listening || transcript.length > 0

  return (
    <div data-testid="voice-bar" className="flex items-center gap-2" data-listening={listening}>
      <button
        type="button"
        data-testid="voice-ptt"
        aria-pressed={listening}
        aria-label={listening ? 'Diktat beenden (Alt+V)' : `${label} starten (Alt+V)`}
        // Push-to-talk: gedrueckt halten; Klick/Alt+V toggelt.
        onMouseDown={() => !listening && start()}
        onMouseUp={() => listening && commit()}
        onClick={() => (listening ? commit() : start())}
        className={`inline-flex h-9 w-9 items-center justify-center rounded-full border ${
          listening
            ? `bg-destructive text-destructive-foreground ${reducedMotion ? '' : 'animate-pulse'}`
            : 'bg-muted text-muted-foreground hover:bg-accent hover:text-accent-foreground'
        }`}
      >
        <Mic className="h-4 w-4" />
      </button>

      {showTranscript && (
        <div className="flex flex-1 items-center gap-1">
          <input
            ref={inputRef}
            data-testid="voice-transcript"
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Sprich jetzt…"
            aria-label="Transkript (editierbar)"
            className="flex-1 rounded border border-border bg-background px-2 py-1 text-sm"
          />
          <button type="button" data-testid="voice-commit" aria-label="Uebernehmen" onClick={() => commit()} className="inline-flex h-7 w-7 items-center justify-center rounded text-emerald-600 hover:bg-accent">
            <Check className="h-4 w-4" />
          </button>
          <button type="button" data-testid="voice-cancel" aria-label="Verwerfen" onClick={() => cancel()} className="inline-flex h-7 w-7 items-center justify-center rounded text-muted-foreground hover:bg-accent">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {error && (
        <span data-testid="voice-error" role="alert" className="text-xs text-destructive">
          Spracherkennung nicht verfuegbar
        </span>
      )}
    </div>
  )
}
