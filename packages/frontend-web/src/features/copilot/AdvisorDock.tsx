import * as React from 'react'
import { useEffect, useState } from 'react'
import { useLocation } from '@/app/routing/typed-router'
import { CopilotDockPanel } from './CopilotDockPanel'
import { useCopilotChat } from './useCopilotChat'
import { useVoiceCopilotSummary } from './useVoiceCopilotSummary'

export function AdvisorDock(): JSX.Element {
  const { pathname } = useLocation()
  const { summary, playSummary, playing, clearSummary } = useVoiceCopilotSummary()
  const [open, setOpen] = useState<boolean>(false)
  const [text, setText] = useState<string>('')
  const { messages, sendMessage, loading, connected, sessionId } = useCopilotChat({ enabled: open })

  React.useEffect(() => {
    const handleOpen = (): void => setOpen(true)
    window.addEventListener('open-copilot-dock', handleOpen)
    return () => window.removeEventListener('open-copilot-dock', handleOpen)
  }, [])

  useEffect(() => {
    setOpen(false)
  }, [pathname])

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
      voiceSummary={summary}
      onPlayVoiceSummary={() => {
        void playSummary()
      }}
      playingVoiceSummary={playing}
      onDismissVoiceSummary={clearSummary}
    />
  )
}
