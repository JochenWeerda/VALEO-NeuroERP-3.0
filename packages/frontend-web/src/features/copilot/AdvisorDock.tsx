import * as React from "react"
import { useState } from "react"
import { useCopilotChat } from "./useCopilotChat"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

const DOCK_WIDTH = 384
const BUTTON_SIZE = 48
const BUTTON_BOTTOM_OFFSET = 24
const BUTTON_RIGHT_OFFSET = 24

export function AdvisorDock(): JSX.Element {
  const { messages, sendMessage, loading } = useCopilotChat()
  const [open, setOpen] = useState<boolean>(false)
  const [text, setText] = useState<string>("")

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>): void => {
    e.preventDefault()
    const trimmedText = text.trim()
    if (trimmedText.length === 0 || loading) {
      return
    }
    void sendMessage(trimmedText)
    setText("")
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setText(e.target.value)
  }

  return (
    <>
      <Button
        onClick={() => setOpen((prev) => !prev)}
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
          open ? "translate-x-0" : "translate-x-full"
        }`}
        style={{ width: `${DOCK_WIDTH}px` }}
        aria-hidden={!open}
      >
        <div className="flex items-center justify-between border-b bg-emerald-50 p-3">
          <span className="font-semibold text-emerald-700">Copilot Advisor</span>
          <Button size="sm" variant="ghost" onClick={() => setOpen(false)} aria-label="Chat schliessen">
            x
          </Button>
        </div>

        <div className="flex-1 space-y-2 overflow-y-auto p-3">
          {messages.length === 0 ? (
            <div className="mt-8 text-center text-sm text-gray-500">
              Stelle eine Frage zu KPIs, Lager, Preisen oder Prognosen.
            </div>
          ) : null}
          {messages.map((msg, index): JSX.Element => (
            <div
              key={index}
              className={`max-w-[85%] rounded-xl p-2 ${
                msg.role === "user" ? "ml-auto bg-emerald-600 text-white" : "bg-emerald-100 text-gray-800"
              }`}
            >
              {msg.content}
            </div>
          ))}
          {loading ? <div className="text-sm italic text-gray-500">Copilot denkt ...</div> : null}
        </div>

        <form className="flex gap-2 border-t p-3" onSubmit={handleSubmit}>
          <Input
            value={text}
            onChange={handleInputChange}
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
