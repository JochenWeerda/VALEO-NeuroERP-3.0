/**
 * Voice-Kanal Konfiguration & Test (GAP-104-I)
 *
 * Feature-Flag: ki-usability — partiell aktiv.
 * Ermöglicht das Testen von Sprachbefehlen, zeigt Erkennungsergebnis
 * und erlaubt die Konfiguration der Mindest-Konfidenz.
 */

import { useState, useCallback } from 'react'
import { Mic, MicOff, Volume2, Settings2, CheckCircle2, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useVoiceIntent } from '@/features/ki-usability/hooks/useVoiceIntent'

interface HistoryEntry {
  ts: string
  transcript: string
  action: string | null
  ok: boolean
  message: string
}

export default function VoiceChannelPage() {
  const [minConfidence, setMinConfidence] = useState(0.7)
  const [history, setHistory] = useState<HistoryEntry[]>([])

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
      // transcript is set via state in the hook; we use actionId here
      addEntry('…', actionId, true, `Konfidenz ${Math.round(confidence * 100)} %`)
    },
    [addEntry],
  )

  const onError = useCallback(
    (message: string) => {
      addEntry('…', null, false, message)
    },
    [addEntry],
  )

  const { startListening, listening, transcript, resolvedAction, reset } = useVoiceIntent({
    minConfidence,
    onResolved,
    onError,
  })

  const handleStart = () => {
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

      {/* Einstellungen */}
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

      {/* Sprachtest */}
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

          {transcript && (
            <div className="rounded border bg-muted/40 p-3 text-sm space-y-1">
              <span className="text-xs text-muted-foreground">Transkript</span>
              <p className="font-medium">{transcript}</p>
              {resolvedAction && (
                <Badge variant="secondary" className="mt-1">
                  Aktion: {resolvedAction}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Verlauf */}
      {history.length > 0 && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Erkennungsverlauf</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {history.map((entry, i) => (
                <div
                  key={i}
                  className="flex items-start gap-3 text-sm border-b last:border-0 pb-2 last:pb-0"
                >
                  {entry.ok ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 shrink-0" />
                  ) : (
                    <XCircle className="h-4 w-4 text-destructive mt-0.5 shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    {entry.transcript && entry.transcript !== '…' && (
                      <p className="truncate font-medium">{entry.transcript}</p>
                    )}
                    {entry.action && (
                      <p className="text-xs text-muted-foreground">→ {entry.action}</p>
                    )}
                    <p className="text-xs text-muted-foreground">{entry.message}</p>
                  </div>
                  <span className="text-xs text-muted-foreground shrink-0">{entry.ts}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <p className="text-xs text-muted-foreground">
        Voraussetzung: HTTPS-Kontext und Browser-Berechtigung für das Mikrofon.
        Derzeit unterstützte Browser: Chrome, Edge (Web Speech API).
      </p>
    </div>
  )
}
