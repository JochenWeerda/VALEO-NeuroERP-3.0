import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, useLocation } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ActionDispatchProvider } from '@/features/ki-usability/context/ActionDispatchContext'
import { useActionDispatch } from '@/features/ki-usability/context/ActionDispatchHooks'

vi.mock('@/lib/mcp-customer-open', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/mcp-customer-open')>()
  return {
    ...actual,
    callCustomerOpen: vi.fn(),
  }
})

import { callCustomerOpen } from '@/lib/mcp-customer-open'

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
  beforeEach(() => {
    vi.mocked(callCustomerOpen).mockReset()
  })

  it('nav-customers ohne kunden_nr oeffnet die Kundenliste', async () => {
    function ListTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button type="button" onClick={() => { void dispatch('nav-customers') }}>
          Liste
        </button>
      )
    }

    render(
      <MemoryRouter initialEntries={['/']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <ActionDispatchProvider>
          <ListTrigger />
          <LocationProbe />
        </ActionDispatchProvider>
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Liste' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/verkauf/kunden-liste')
    })
    expect(callCustomerOpen).not.toHaveBeenCalled()
  })

  it('nav-customers mit kunden_nr navigiert auf MCP route_path', async () => {
    vi.mocked(callCustomerOpen).mockResolvedValue({
      customer_id: 'cust-1',
      kunden_nr: 'TEST',
      name: 'Test GmbH',
      route_path: '/crm/customers/cust-1',
      screen_id: 'crm/customer-360',
    })

    function OpenTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-customers', { kunden_nr: 'TEST' })
          }}
        >
          Open
        </button>
      )
    }

    render(
      <MemoryRouter initialEntries={['/']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <ActionDispatchProvider>
          <OpenTrigger />
          <LocationProbe />
        </ActionDispatchProvider>
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Open' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/crm/customers/cust-1')
    })
    expect(callCustomerOpen).toHaveBeenCalledWith('TEST')
  })

  it('nav-customers mit sicherem route_path navigiert ohne MCP', async () => {
    function DirectTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-customers', { route_path: '/crm/customers/direct-1' })
          }}
        >
          Direct
        </button>
      )
    }

    render(
      <MemoryRouter initialEntries={['/']} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <ActionDispatchProvider>
          <DirectTrigger />
          <LocationProbe />
        </ActionDispatchProvider>
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Direct' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/crm/customers/direct-1')
    })
    expect(callCustomerOpen).not.toHaveBeenCalled()
  })

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
