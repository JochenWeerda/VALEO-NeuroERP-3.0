import { useEffect, useRef, useState } from 'react'
import { useTenant } from '@/hooks/useTenant'
import { getAccessToken } from '@/lib/auth'
import { useCopilotStream } from './useCopilotStream'

export type MessageRole = 'user' | 'assistant'

export type ChatMessage = {
  id: string
  role: MessageRole
  content: string
  state?: 'streaming' | 'complete' | 'error'
}

export interface UseCopilotChatOptions {
  enabled?: boolean
}

export function useCopilotChat({ enabled = false }: UseCopilotChatOptions = {}): {
  messages: ChatMessage[]
  sendMessage: (_text: string) => Promise<void>
  loading: boolean
  connected: boolean
  sessionId: string | null
  pipelineResult: Record<string, unknown> | null
} {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const currentAssistantIdRef = useRef<string | null>(null)
  const { tenantId } = useTenant()
  const accessToken =
    getAccessToken()
    ?? window.localStorage.getItem('token')
    ?? import.meta.env.VITE_API_DEV_TOKEN
    ?? undefined

  const { connect, disconnect, send, connected, sessionId, pipelineResult } = useCopilotStream({
    token: accessToken,
    tenantId,
    onMessage: (message) => {
      switch (message.type) {
        case 'stream_start':
          setLoading(true)
          break
        case 'stream_chunk':
          setMessages((prevMessages) =>
            prevMessages.map((entry) =>
              entry.id === currentAssistantIdRef.current
                ? {
                    ...entry,
                    content: `${entry.content}${message.chunk ?? ''}`,
                    state: 'streaming',
                  }
                : entry,
            ),
          )
          break
        case 'stream_end':
          setMessages((prevMessages) =>
            prevMessages.map((entry) =>
              entry.id === currentAssistantIdRef.current
                ? {
                    ...entry,
                    content: message.full_text ?? entry.content,
                    state: 'complete',
                  }
                : entry,
            ),
          )
          currentAssistantIdRef.current = null
          setLoading(false)
          break
      }
    },
  })

  useEffect(() => {
    if (!enabled) {
      disconnect()
      return undefined
    }
    connect()
    return () => {
      disconnect()
    }
  }, [connect, disconnect, enabled])

  async function sendMessage(text: string): Promise<void> {
    const trimmedText = text.trim()
    if (trimmedText.length === 0 || loading) {
      return
    }

    const userMessage: ChatMessage = {
      id: `user-${crypto.randomUUID()}`,
      role: 'user',
      content: trimmedText,
      state: 'complete',
    }
    const assistantMessageId = `assistant-${crypto.randomUUID()}`
    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      state: 'streaming',
    }

    setMessages((prevMessages) => [...prevMessages, userMessage, assistantMessage])
    currentAssistantIdRef.current = assistantMessageId
    setLoading(true)

    if (!connected) {
      connect()
      setMessages((prevMessages) =>
        prevMessages.map((entry) =>
          entry.id === assistantMessageId
            ? {
                ...entry,
                content: 'Copilot-Verbindung wird aufgebaut. Bitte erneut senden.',
                state: 'error',
              }
            : entry,
        ),
      )
      currentAssistantIdRef.current = null
      setLoading(false)
      return
    }

    send(trimmedText)
  }

  return {
    messages,
    sendMessage,
    loading,
    connected,
    sessionId,
    pipelineResult,
  }
}
