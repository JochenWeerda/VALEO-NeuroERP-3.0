import type { Meta, StoryObj } from '@storybook/react'
import type { FormEvent } from 'react'
import { CopilotDockPanel } from '../CopilotDockPanel'

const meta = {
  title: 'Copilot/CopilotDockPanel',
  component: CopilotDockPanel,
  args: {
    open: true,
    text: 'Welche Runs warten auf Freigabe?',
    loading: false,
    connected: true,
    sessionId: 'session-12345678',
    messages: [
      { id: '1', role: 'user', content: 'Welche Runs warten auf Freigabe?', state: 'complete' },
      {
        id: '2',
        role: 'assistant',
        content: 'Aktuell warten zwei Bestellvorschlaege und ein Ausnahmefall auf Human Oversight.',
        state: 'complete',
      },
    ],
    onToggleOpen: () => undefined,
    onTextChange: () => undefined,
    onSubmit: (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault()
    },
  },
} satisfies Meta<typeof CopilotDockPanel>

export default meta

type Story = StoryObj<typeof meta>

export const Connected: Story = {}

export const Streaming: Story = {
  args: {
    loading: true,
    messages: [
      { id: '1', role: 'user', content: 'Starte den Copilot-Check fuer den Event Bus.', state: 'complete' },
      { id: '2', role: 'assistant', content: 'Intent erkannt: event_bus_review ...', state: 'streaming' },
    ],
  },
}
