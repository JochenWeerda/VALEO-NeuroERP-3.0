import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, useLocation } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { ActionDispatchProvider } from '@/features/ki-usability/context/ActionDispatchContext'
import { useActionDispatch } from '@/features/ki-usability/context/ActionDispatchHooks'

function LocationProbe(): JSX.Element {
  const location = useLocation()
  return <div data-testid="location">{location.pathname}</div>
}

function TriggerButton(): JSX.Element {
  const { dispatch } = useActionDispatch()

  return (
    <button
      type="button"
      onClick={() => {
        void dispatch('wave22-test-route', { path: '/finance/abschluss' })
      }}
    >
      Dispatch
    </button>
  )
}

describe('ActionDispatchProvider', () => {
  it('faellt fuer unbekannte Action-IDs auf dynamische Navigation zurueck', async () => {
    render(
      <MemoryRouter initialEntries={['/']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <ActionDispatchProvider>
          <TriggerButton />
          <LocationProbe />
        </ActionDispatchProvider>
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Dispatch' }))

    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/finance/abschluss')
    })
  })

  it('faellt fuer unbekannte Action-IDs auf Browser-Events zurueck', async () => {
    const listener = vi.fn()
    window.addEventListener('wave22-open-ai', listener)

    function EventTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()

      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('wave22-test-event', { eventName: 'wave22-open-ai' })
          }}
        >
          Dispatch event
        </button>
      )
    }

    render(
      <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <ActionDispatchProvider>
          <EventTrigger />
        </ActionDispatchProvider>
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Dispatch event' }))

    await waitFor(() => {
      expect(listener).toHaveBeenCalledTimes(1)
    })

    window.removeEventListener('wave22-open-ai', listener)
  })
})
