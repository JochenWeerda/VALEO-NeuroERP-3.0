import * as React from 'react'
import { Loader2, Volume2, X } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { ChatMessage } from './useCopilotChat'

const DOCK_WIDTH = 384
const BUTTON_SIZE = 48
const BUTTON_BOTTOM_OFFSET = 24
const BUTTON_RIGHT_OFFSET = 24

type CopilotDockPanelProps = {
  open: boolean
  onToggleOpen: () => void
  text: string
  onTextChange: (_value: string) => void
  onSubmit: (_event: React.FormEvent<HTMLFormElement>) => void
  messages: ChatMessage[]
  loading: boolean
  connected: boolean
  sessionId: string | null
  voiceSummary?: { summaryText: string; estimatedSeconds?: number } | null
  onPlayVoiceSummary?: () => void
  playingVoiceSummary?: boolean
  onDismissVoiceSummary?: () => void
}

export function CopilotDockPanel({
  open,
  onToggleOpen,
  text,
  onTextChange,
  onSubmit,
  messages,
  loading,
  connected,
  sessionId,
  voiceSummary,
  onPlayVoiceSummary,
  playingVoiceSummary = false,
  onDismissVoiceSummary,
}: CopilotDockPanelProps): JSX.Element {
  return (
    <>
      <Button
        onClick={onToggleOpen}
        className="fixed z-40 rounded-full font-semibold shadow-lg"
        style={{
          bottom: `${BUTTON_BOTTOM_OFFSET}px`,
          right: `${BUTTON_RIGHT_OFFSET}px`,
          height: `${BUTTON_SIZE}px`,
          width: `${BUTTON_SIZE}px`,
        }}
        aria-label="Copilot Chat oeffnen"
      >
        Chat
      </Button>

      <div
        className={`fixed right-0 top-0 z-50 flex h-full flex-col border-l bg-card shadow-2xl transition-transform duration-300 ease-out ${
          open ? 'translate-x-0' : 'translate-x-full'
        }`}
        style={{ width: `${DOCK_WIDTH}px` }}
        {...(!open ? { inert: true as const } : { role: 'dialog' as const, 'aria-modal': true as const, 'aria-label': 'Copilot Advisor' })}
      >
        <div className="border-b bg-muted/50 p-3">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-primary">Copilot Advisor</span>
            <Button size="sm" variant="ghost" onClick={onToggleOpen} aria-label="Chat schliessen">
              x
            </Button>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
            <Badge variant={connected ? 'success' : 'secondary'}>
              {connected ? 'Stream verbunden' : 'Offline'}
            </Badge>
            {sessionId ? <Badge variant="secondary">Session {sessionId.slice(0, 8)}</Badge> : null}
          </div>
        </div>

        <div className="flex-1 space-y-2 overflow-y-auto p-3">
          {voiceSummary?.summaryText ? (
            <div
              data-testid="copilot-voice-summary"
              className="rounded-xl border border-primary/30 bg-primary/5 p-3 text-sm"
            >
              <div className="mb-1 flex items-center justify-between gap-2">
                <span className="text-xs font-semibold text-primary">
                  Voice-Zusammenfassung
                  {voiceSummary.estimatedSeconds ? ` (~${voiceSummary.estimatedSeconds}s)` : ''}
                </span>
                <div className="flex items-center gap-1">
                  {onPlayVoiceSummary ? (
                    <Button
                      type="button"
                      size="icon"
                      variant="ghost"
                      className="h-7 w-7"
                      disabled={playingVoiceSummary}
                      aria-label="Zusammenfassung vorlesen"
                      onClick={onPlayVoiceSummary}
                    >
                      {playingVoiceSummary ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Volume2 className="h-3.5 w-3.5" />
                      )}
                    </Button>
                  ) : null}
                  {onDismissVoiceSummary ? (
                    <Button
                      type="button"
                      size="icon"
                      variant="ghost"
                      className="h-7 w-7"
                      aria-label="Voice-Zusammenfassung schliessen"
                      onClick={onDismissVoiceSummary}
                    >
                      <X className="h-3.5 w-3.5" />
                    </Button>
                  ) : null}
                </div>
              </div>
              <p className="text-xs leading-snug text-foreground">{voiceSummary.summaryText}</p>
            </div>
          ) : null}
          {messages.length === 0 ? (
            <div className="mt-8 rounded-xl border border-dashed bg-muted/50 p-4 text-sm text-muted-foreground">
              Stelle eine Frage zu KPIs, Lager, Preisen oder Prognosen.
            </div>
          ) : null}
          {messages.map((msg): JSX.Element => (
            <div
              key={msg.id}
              className={`max-w-[88%] rounded-xl p-2 ${
                msg.role === 'user' ? 'ml-auto bg-primary text-primary-foreground' : 'bg-muted text-foreground'
              }`}
            >
              {msg.content.length > 0 ? msg.content : '...'}
            </div>
          ))}
          {loading ? <div className="text-sm italic text-muted-foreground">Copilot denkt ...</div> : null}
        </div>

        <form className="flex gap-2 border-t p-3" onSubmit={onSubmit}>
          <Input
            value={text}
            onChange={(event) => onTextChange(event.target.value)}
            placeholder="Frage stellen ..."
            className="flex-1"
            disabled={loading}
            aria-label="Chat-Nachricht eingeben"
          />
          <Button type="submit" disabled={loading || text.trim().length === 0}>
            Senden
          </Button>
        </form>
      </div>
    </>
  )
}
