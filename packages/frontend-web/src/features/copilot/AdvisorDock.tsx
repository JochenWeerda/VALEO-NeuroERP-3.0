import * as React from "react"
import { useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { useCopilotChat } from "./useCopilotChat"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

const DOCK_WIDTH = 384 // w-96 = 384px
const ANIMATION_STIFFNESS = 90
const BUTTON_SIZE = 48 // h-12 w-12
const BUTTON_BOTTOM_OFFSET = 24 // bottom-6
const BUTTON_RIGHT_OFFSET = 24 // right-6

/**
 * Copilot Advisor Dock - Interaktives Chat-Fenster
 * Animiertes Panel am rechten Bildschirmrand für Live-Chat mit KI-Copilot
 */
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

  const toggleOpen = (): void => {
    setOpen((prev) => !prev)
  }

  const handleClose = (): void => {
    setOpen(false)
  }

  return (
    <>
      {/* Toggle-Button */}
      <Button
        onClick={toggleOpen}
        className="fixed z-40 rounded-full shadow-lg bg-emerald-600 hover:bg-emerald-700"
        style={{
          bottom: `${BUTTON_BOTTOM_OFFSET}px`,
          right: `${BUTTON_RIGHT_OFFSET}px`,
          height: `${BUTTON_SIZE}px`,
          width: `${BUTTON_SIZE}px`,
        }}
        aria-label="Copilot Chat öffnen"
      >
        💬
      </Button>

      {/* Dock-Panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ x: DOCK_WIDTH }}
            animate={{ x: 0 }}
            exit={{ x: DOCK_WIDTH }}
            transition={{ type: "spring", stiffness: ANIMATION_STIFFNESS }}
            className="fixed right-0 top-0 h-full bg-white border-l border-emerald-200 shadow-2xl flex flex-col z-50"
            style={{ width: `${DOCK_WIDTH}px` }}
          >
            {/* Header */}
            <div className="p-3 border-b bg-emerald-50 flex items-center justify-between">
              <span className="font-semibold text-emerald-700">
                Copilot Advisor
              </span>
              <Button
                size="sm"
                variant="ghost"
                onClick={handleClose}
                aria-label="Chat schließen"
              >
                ×
              </Button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {messages.length === 0 && (
                <div className="text-sm text-gray-500 text-center mt-8">
                  Stelle eine Frage zu KPIs, Lager, Preisen oder Prognosen.
                </div>
              )}
              {messages.map((msg, index): JSX.Element => (
                <div
                  key={index}
                  className={`p-2 rounded-xl max-w-[85%] ${
                    msg.role === "user"
                      ? "bg-emerald-600 text-white ml-auto"
                      : "bg-emerald-100 text-gray-800"
                  }`}
                >
                  {msg.content}
                </div>
              ))}
              {loading && (
                <div className="text-sm text-gray-500 italic">
                  Copilot denkt …
                </div>
              )}
            </div>

            {/* Input Form */}
            <form className="p-3 border-t flex gap-2" onSubmit={handleSubmit}>
              <Input
                value={text}
                onChange={handleInputChange}
                placeholder="Frage stellen …"
                className="flex-1"
                disabled={loading}
                aria-label="Chat-Nachricht eingeben"
              />
              <Button type="submit" disabled={loading || text.trim().length === 0}>
                Senden
              </Button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
