import * as React from 'react'
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
}: CopilotDockPanelProps): JSX.Element {
  return (
    <>
      <Button
        onClick={onToggleOpen}
        className="fixed z-40 rounded-full bg-emerald-600 shadow-lg hover:bg-emerald-700"
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
        className={`fixed right-0 top-0 z-50 flex h-full flex-col border-l border-emerald-200 bg-white shadow-2xl transition-transform duration-300 ease-out ${
          open ? 'translate-x-0' : 'translate-x-full'
        }`}
        style={{ width: `${DOCK_WIDTH}px` }}
        aria-hidden={!open}
      >
        <div className="border-b bg-gradient-to-r from-emerald-50 to-teal-50 p-3">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-emerald-700">Copilot Advisor</span>
            <Button size="sm" variant="ghost" onClick={onToggleOpen} aria-label="Chat schliessen">
              x
            </Button>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
            <Badge variant={connected ? 'outline' : 'secondary'} className={connected ? 'border-emerald-300 text-emerald-700' : ''}>
              {connected ? 'Stream verbunden' : 'Offline'}
            </Badge>
            {sessionId ? <Badge variant="secondary">Session {sessionId.slice(0, 8)}</Badge> : null}
          </div>
        </div>

        <div className="flex-1 space-y-2 overflow-y-auto p-3">
          {messages.length === 0 ? (
            <div className="mt-8 rounded-xl border border-dashed border-emerald-200 bg-emerald-50/50 p-4 text-sm text-gray-600">
              Stelle eine Frage zu KPIs, Lager, Preisen oder Prognosen.
            </div>
          ) : null}
          {messages.map((msg): JSX.Element => (
            <div
              key={msg.id}
              className={`max-w-[88%] rounded-xl p-2 ${
                msg.role === 'user' ? 'ml-auto bg-emerald-600 text-white' : 'bg-emerald-100 text-gray-800'
              }`}
            >
              {msg.content.length > 0 ? msg.content : '...'}
            </div>
          ))}
          {loading ? <div className="text-sm italic text-gray-500">Copilot denkt ...</div> : null}
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
