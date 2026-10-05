import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from '@/app/routing/test-router'
import { describe, expect, it, vi } from 'vitest'
import i18n from '@/i18n/config'
import { TopBar } from '@/components/navigation/TopBar'

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    i18n,
    t: (value: string) => value,
  }),
}))

vi.mock('@/hooks/useFeature', () => ({
  useFeature: () => true,
}))

vi.mock('@/hooks/useTheme', () => ({
  useTheme: () => ({ isDark: false, toggleTheme: vi.fn() }),
}))

vi.mock('@/hooks/useTouchDevice', () => ({
  useTouchDevice: () => true,
}))

vi.mock('@/features/ki-usability', () => ({
  VoiceButton: () => (
    <button type="button" aria-label="Sprachbefehl starten">
      Mic
    </button>
  ),
}))

vi.mock('@/components/ui/notification-center', () => ({
  NotificationCenter: () => (
    <button type="button" aria-label="Benachrichtigungen">
      Bell
    </button>
  ),
}))

describe('TopBar touch chrome', () => {
  it('öffnet die Suche ohne Ctrl+K-Beschriftung und zeigt Sprache', async () => {
    const onCommandOpen = vi.fn()
    render(
      <MemoryRouter>
        <TopBar onCommandOpen={onCommandOpen} commandPaletteEnabled onMobileMenuToggle={() => undefined} />
      </MemoryRouter>,
    )

    const search = screen.getByRole('button', { name: 'Suche öffnen' })
    expect(search).toBeInTheDocument()
    expect(search).not.toHaveTextContent('Ctrl+K')
    expect(await screen.findByRole('button', { name: 'Sprachbefehl starten' })).toBeInTheDocument()

    await userEvent.click(search)
    expect(onCommandOpen).toHaveBeenCalledTimes(1)
  })

  it('legt Aufgaben ins Benutzermenü, wenn die Icon-Leiste kompakt ist', async () => {
    render(
      <MemoryRouter>
        <TopBar commandPaletteEnabled onMobileMenuToggle={() => undefined} />
      </MemoryRouter>,
    )

    await userEvent.click(screen.getByRole('button', { name: 'Benutzermenü' }))
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Aufgaben' })).toBeInTheDocument()
    })
    expect(screen.getByRole('button', { name: 'Copilot' })).toBeInTheDocument()
  })
})
