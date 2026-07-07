/**
 * UIX-072: VoiceBar — Diktat sichtbar/editierbar, Uebernahme erst bei Bestaetigung,
 * Telemetrie ohne Transkript-Inhalt, prefers-reduced-motion.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import { VoiceBar } from '@/components/mask-builder/renderers/VoiceBar'
import { FakeSttProvider, type VoiceTelemetry } from '@/lib/voice/stt-provider'

function mockMatchMedia(reduced: boolean) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    configurable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: reduced,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  })
}

beforeEach(() => mockMatchMedia(false))

describe('VoiceBar', () => {
  it('rendert nichts, wenn kein Provider verfuegbar ist', () => {
    const { container } = render(
      <VoiceBar provider={new FakeSttProvider({ available: false })} target="field" onCommit={vi.fn()} />,
    )
    expect(container.querySelector('[data-testid="voice-bar"]')).toBeNull()
  })

  it('zeigt live-Transkript und uebernimmt erst bei Bestaetigung', () => {
    const provider = new FakeSttProvider()
    const onCommit = vi.fn()
    render(<VoiceBar provider={provider} target="omnibox" onCommit={onCommit} />)

    fireEvent.click(screen.getByTestId('voice-ptt'))
    act(() => provider.emitPartial('offene'))
    act(() => provider.emitFinal('offene posten', 0.9))

    const input = screen.getByTestId('voice-transcript') as HTMLInputElement
    expect(input.value).toBe('offene posten')
    // noch NICHT uebernommen
    expect(onCommit).not.toHaveBeenCalled()

    fireEvent.click(screen.getByTestId('voice-commit'))
    expect(onCommit).toHaveBeenCalledWith('offene posten')
  })

  it('Transkript ist vor Uebernahme editierbar', () => {
    const provider = new FakeSttProvider()
    const onCommit = vi.fn()
    render(<VoiceBar provider={provider} target="field" onCommit={onCommit} />)
    fireEvent.click(screen.getByTestId('voice-ptt'))
    act(() => provider.emitFinal('offene posten'))
    fireEvent.change(screen.getByTestId('voice-transcript'), { target: { value: 'offene posten folkerts' } })
    fireEvent.click(screen.getByTestId('voice-commit'))
    expect(onCommit).toHaveBeenCalledWith('offene posten folkerts')
  })

  it('Verwerfen uebernimmt nichts', () => {
    const provider = new FakeSttProvider()
    const onCommit = vi.fn()
    render(<VoiceBar provider={provider} target="field" onCommit={onCommit} />)
    fireEvent.click(screen.getByTestId('voice-ptt'))
    act(() => provider.emitFinal('irgendwas'))
    fireEvent.click(screen.getByTestId('voice-cancel'))
    expect(onCommit).not.toHaveBeenCalled()
  })

  it('Telemetrie traegt Metadaten, aber NIE Transkript-Inhalt', () => {
    const provider = new FakeSttProvider({ id: 'webspeech' })
    const events: VoiceTelemetry[] = []
    render(<VoiceBar provider={provider} target="omnibox" onCommit={vi.fn()} onTelemetry={(t) => events.push(t)} />)
    fireEvent.click(screen.getByTestId('voice-ptt'))
    act(() => provider.emitFinal('geheimer inhalt'))
    fireEvent.click(screen.getByTestId('voice-commit'))
    expect(events).toHaveLength(1)
    expect(events[0]).toMatchObject({ used: true, provider: 'webspeech', target: 'omnibox' })
    expect(JSON.stringify(events[0])).not.toContain('geheimer')
  })

  it('kein pulsierendes Mikro bei prefers-reduced-motion', () => {
    mockMatchMedia(true)
    const provider = new FakeSttProvider()
    render(<VoiceBar provider={provider} target="field" onCommit={vi.fn()} />)
    fireEvent.click(screen.getByTestId('voice-ptt'))
    expect(screen.getByTestId('voice-ptt').className).not.toContain('animate-pulse')
  })
})
