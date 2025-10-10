import { useState } from "react"

type MessageRole = "user" | "assistant"

type Message = {
  role: MessageRole
  content: string
}

type ChatResponse = {
  ok?: boolean
  reply?: string
}

/**
 * Custom Hook für Copilot-Chat-Funktionalität
 * Verwaltet Chat-Verlauf und kommuniziert mit Backend
 */
export function useCopilotChat(): {
  messages: Message[]
  sendMessage: (text: string) => Promise<void>
  loading: boolean
} {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState<boolean>(false)

  /**
   * Sendet eine Nachricht an den Copilot-Service
   */
  async function sendMessage(text: string): Promise<void> {
    const userMessage: Message = { role: "user", content: text }
    setMessages((prevMessages) => [...prevMessages, userMessage])
    setLoading(true)

    try {
      const resp = await fetch("/api/mcp/copilot/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history: messages }),
      })

      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`)
      }

      const data = (await resp.json()) as ChatResponse

      if (data?.reply !== undefined && data.reply.length > 0) {
        const assistantMessage: Message = {
          role: "assistant",
          content: data.reply,
        }
        setMessages((prevMessages) => [...prevMessages, assistantMessage])
      } else {
        const errorMessage: Message = {
          role: "assistant",
          content: "⚠️ Keine Antwort vom Copilot erhalten.",
        }
        setMessages((prevMessages) => [...prevMessages, errorMessage])
      }
    } catch (err) {
      const errorMessage: Message = {
        role: "assistant",
        content: "⚠️ Fehler bei der Analyse. Bitte versuche es erneut.",
      }
      setMessages((prevMessages) => [...prevMessages, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return { messages, sendMessage, loading }
}
