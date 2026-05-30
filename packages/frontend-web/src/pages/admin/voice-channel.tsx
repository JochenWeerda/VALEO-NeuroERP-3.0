/**
 * Voice-Kanal Konfiguration & Test (GAP-104-I)
 *
 * Feature-Flag: ki-usability — partiell aktiv.
 * Ermöglicht das Testen von Sprachbefehlen, zeigt Erkennungsergebnis
 * und erlaubt die Konfiguration der Mindest-Konfidenz.
 * Slice-016: Voice-Stack-Readiness via GET /voice/status.
 */

import { useState, useCallback, useRef, useEffect } from 'react'
import {
  Mic,
  MicOff,
  Volume2,
  Settings2,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Server,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useVoiceIntent } from '@/features/ki-usability/hooks/useVoiceIntent'
import { useVoiceStackStatus } from '@/features/ki-usability/hooks/useVoiceStackStatus'

interface HistoryEntry {
  ts: string
  transcript: string
  action: string | null
  ok: boolean
  message: string
}

function readinessBadge(ready: boolean, readyLabel: string, fallbackLabel: string): JSX.Element {
  return (
    <Badge variant={ready ? 'success' : 'secondary'}>
      {ready ? readyLabel : fallbackLabel}
    </Badge>
  )
}

export default function VoiceChannelPage(): JSX.Element {
  const [minConfidence, setMinConfidence] = useState(0.7)
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const transcriptRef = useRef('')

  const { status, loading: statusLoading, error: statusError, refetch } = useVoiceStackStatus()

  const addEntry = useCallback(
    (transcript: string, action: string | null, ok: boolean, message: string) => {
      setHistory((prev) => [
        {
          ts: new Date().toLocaleTimeString('de-DE'),
          transcript,
          action,
          ok,
          message,
        },
        ...prev.slice(0, 19),
      ])
    },
    [],
  )

  const onResolved = useCallback(
    (actionId: string, _params: Record<string, unknown>, confidence: number) => {
      addEntry(
        transcriptRef.current || '—',
        actionId,
        true,
        `Konfidenz ${Math.round(confidence * 100)} %`,
      )
    },
    [addEntry],
  )

  const onError = useCallback(
    (message: string) => {
      addEntry(transcriptRef.current || '—', null, false, message)
    },
    [addEntry],
  )

  const { startListening, listening, transcript, resolvedAction, reset } = useVoiceIntent({
    minConfidence,
    onResolved,
    onError,
  })

  useEffect(() => {
    if (transcript?.trim()) {
      transcriptRef.current = transcript
    }
  }, [transcript])

  const handleStart = (): void => {
    reset()
    startListening()
  }

  return (
    <div className="p-6 space-y-6 max-w-3xl">
      <div className="flex items-center gap-3">
        <Volume2 className="h-6 w-6 text-muted-foreground" />
        <div>
          <h1 className="text-xl font-semibold">Voice-Kanal</h1>
          <p className="text-sm text-muted-foreground">
            Sprachbefehle testen und Kanal-Einstellungen konfigurieren
          </p>
        </div>
      </div>

      <Card data-testid="voice-stack-status">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center justify-between gap-2">
            <span className="flex items-center gap-2">
              <Server className="h-4 w-4" />
              Voice-Stack Readiness
            </span>
            <Button
              type="button"
              size="sm"
              variant="ghost"
              className="h-7 gap-1"
              disabled={statusLoading}
              aria-label="Status aktualisieren"
              onClick={refetch}
            >
              <RefreshCw className={`h-3.5 w-3.5 ${statusLoading ? 'animate-spin' : ''}`} />
              Aktualisieren
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {statusError ? (
            <p className="text-sm text-destructive" data-testid="voice-status-error">
              ki-usability nicht erreichbar — Voice-Stack prüfen (Port 5200 / Docker).
            </p>
          ) : null}
          {status ? (
            <div className="flex flex-wrap gap-2" data-testid="voice-status-badges">
              {readinessBadge(
                status.stt_ready,
                `STT: ${status.stt_provider}`,
                `STT: ${status.stt_provider} (nicht bereit)`,
              )}
              {readinessBadge(
                status.tts_ready,
                `TTS: ${status.tts_provider}`,
                `TTS: ${status.tts_provider} (nicht bereit)`,
              )}
              {readinessBadge(
                status.ollama_reachable,
                'Ollama erreichbar',
                'Ollama offline',
              )}
              {status.voice_polish_enabled ? (
                <Badge variant="secondary">Polish aktiv</Badge>
              ) : null}
              {status.voice_summary_enabled ? (
                <Badge variant="secondary">Summary aktiv</Badge>
              ) : null}
            </div>
          ) : statusLoading ? (
            <p className="text-sm text-muted-foreground">Status wird geladen …</p>
          ) : null}
          {status ? (
            <p className="text-xs text-muted-foreground">
              Modell STT: {status.faster_whisper_model} · Ollama: {status.ollama_base_url}
            </p>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Settings2 className="h-4 w-4" />
            Einstellungen
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-4">
            <label className="text-sm w-52">
              Mindest-Konfidenz:{' '}
              <span className="font-mono font-semibold">{Math.round(minConfidence * 100)} %</span>
            </label>
            <input
              type="range"
              min={0.5}
              max={1.0}
              step={0.05}
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              className="flex-1"
            />
          </div>
          <p className="text-xs text-muted-foreground">
            Befehle unterhalb dieser Schwelle werden nicht automatisch ausgeführt.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Mic className="h-4 w-4" />
            Sprachbefehl testen
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            onClick={handleStart}
            disabled={listening}
            variant={listening ? 'secondary' : 'default'}
            className="gap-2"
          >
            {listening ? (
              <>
                <MicOff className="h-4 w-4 animate-pulse" />
                Höre zu…
              </>
            ) : (
              <>
                <Mic className="h-4 w-4" />
                Sprachbefehl starten
              </>
            )}
          </Button>

          {transcript ? (
            <div className="rounded border bg-muted/40 p-3 text-sm space-y-1">
              <span className="text-xs text-muted-foreground">Transkript</span>
              <p className="font-medium">{transcript}</p>
              {resolvedAction ? (
                <Badge variant="secondary" className="mt-1">
                  Aktion: {resolvedAction}
                </Badge>
              ) : null}
            </div>
          ) : null}
        </CardContent>
      </Card>

      {history.length > 0 ? (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Erkennungsverlauf</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {history.map((entry, i) => (
                <div
                  key={`${entry.ts}-${i}`}
                  className="flex items-start gap-3 text-sm border-b last:border-0 pb-2 last:pb-0"
                >
                  {entry.ok ? (
                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[hsl(var(--color-semantic-success-700-hsl))]" />
                  ) : (
                    <XCircle className="h-4 w-4 text-destructive mt-0.5 shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    {entry.transcript && entry.transcript !== '—' ? (
                      <p className="truncate font-medium">{entry.transcript}</p>
                    ) : null}
                    {entry.action ? (
                      <p className="text-xs text-muted-foreground">→ {entry.action}</p>
                    ) : null}
                    <p className="text-xs text-muted-foreground">{entry.message}</p>
                  </div>
                  <span className="text-xs text-muted-foreground shrink-0">{entry.ts}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      <p className="text-xs text-muted-foreground">
        STT: Local faster-whisper (Docker) oder Browser Web Speech API. TTS und Polish/Summary
        über ki-usability — Status oben prüfen.
      </p>
    </div>
  )
}
