import { StrictMode } from 'react'
import { cleanup, render, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import CallbackPage from '@/pages/auth/Callback'

const fixture = vi.hoisted(() => ({ callback: vi.fn(), params: new URLSearchParams() }))
vi.mock('@/hooks/useAuth', () => ({
  // Intentionally unstable reference, as returned by the existing hook.
  useAuth: () => ({ handleCallback: (code: string, state: string) => fixture.callback(code, state) }),
}))
vi.mock('@/app/routing/typed-router', () => ({ useSearchParams: () => [fixture.params] }))

beforeEach(() => {
  fixture.callback.mockReset().mockResolvedValue(undefined)
  fixture.params = new URLSearchParams({ code: 'synthetic-code', state: 'synthetic-state' })
})
afterEach(cleanup)

describe('real callback page lifecycle', () => {
  it('exchanges the callback once under React StrictMode', async () => {
    render(<StrictMode><CallbackPage /></StrictMode>)
    await waitFor(() => expect(fixture.callback).toHaveBeenCalledTimes(1))
    expect(fixture.callback).toHaveBeenCalledWith('synthetic-code', 'synthetic-state')
  })

  it('does not consume the callback again after a parent rerender', async () => {
    const view = render(<CallbackPage />)
    view.rerender(<CallbackPage />)
    await waitFor(() => expect(fixture.callback).toHaveBeenCalledTimes(1))
  })

  it.each(['error=access_denied', 'state=synthetic-state'])('shows provider or incomplete response errors without exchange: %s', async query => {
    fixture.params = new URLSearchParams(query)
    const view = render(<StrictMode><CallbackPage /></StrictMode>)
    await waitFor(() => expect(view.getByText('Anmeldung fehlgeschlagen')).toBeTruthy())
    expect(fixture.callback).not.toHaveBeenCalled()
  })
})
