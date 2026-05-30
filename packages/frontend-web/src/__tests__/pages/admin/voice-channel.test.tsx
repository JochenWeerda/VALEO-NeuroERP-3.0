import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import VoiceChannelPage from '@/pages/admin/voice-channel'

vi.mock('@/features/ki-usability/hooks/useVoiceIntent', () => ({
  useVoiceIntent: () => ({
    startListening: vi.fn(),
    listening: false,
    transcript: null,
    resolvedAction: null,
    reset: vi.fn(),
  }),
}))

const mockStatus = {
  stt_provider: 'faster-whisper',
  stt_ready: true,
  tts_provider: 'piper',
  tts_ready: false,
  ollama_base_url: 'http://localhost:11434',
  ollama_reachable: true,
  voice_polish_enabled: true,
  voice_summary_enabled: true,
  kokoro_configured: false,
  piper_configured: false,
  faster_whisper_model: 'small',
}

vi.mock('@/features/ki-usability/api/voice', () => ({
  fetchVoiceStatus: vi.fn(async () => mockStatus),
}))

function renderPage(): void {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <VoiceChannelPage />
    </QueryClientProvider>,
  )
}

describe('VoiceChannelPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('zeigt Voice-Stack-Status-Badges', async () => {
    renderPage()

    await waitFor(() => {
      expect(screen.getByTestId('voice-status-badges')).toBeInTheDocument()
    })

    expect(screen.getByText(/STT: faster-whisper/)).toBeInTheDocument()
    expect(screen.getByText(/TTS: piper \(nicht bereit\)/)).toBeInTheDocument()
    expect(screen.getByText('Ollama erreichbar')).toBeInTheDocument()
  })
})
