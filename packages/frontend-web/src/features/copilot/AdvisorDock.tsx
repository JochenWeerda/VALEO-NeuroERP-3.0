import * as React from 'react'
import { useState } from 'react'
import { CopilotDockPanel } from './CopilotDockPanel'
import { useCopilotChat } from './useCopilotChat'

export function AdvisorDock(): JSX.Element {
  const { messages, sendMessage, loading, connected, sessionId } = useCopilotChat()
  const [open, setOpen] = useState<boolean>(false)
  const [text, setText] = useState<string>('')

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
    <CopilotDockPanel
      open={open}
      onToggleOpen={() => setOpen((prev) => !prev)}
      text={text}
      onTextChange={(value) => setText(value)}
      onSubmit={handleSubmit}
      messages={messages}
      loading={loading}
      connected={connected}
      sessionId={sessionId}
    />
  )
}
