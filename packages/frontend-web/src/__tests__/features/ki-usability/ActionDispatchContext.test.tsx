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

vi.mock('@/lib/mcp-order-open', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/mcp-order-open')>()
  return {
    ...actual,
    callOrderStatusOpen: vi.fn(),
  }
})

vi.mock('@/lib/mcp-lot-open', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/mcp-lot-open')>()
  return {
    ...actual,
    callLotTraceOpen: vi.fn(),
  }
})

vi.mock('@/lib/mcp-cell-open', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/mcp-cell-open')>()
  return {
    ...actual,
    callCellStatusOpen: vi.fn(),
  }
})

vi.mock('@/lib/mcp-po-open', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/mcp-po-open')>()
  return {
    ...actual,
    callPoStatusOpen: vi.fn(),
  }
})

vi.mock('@/lib/mcp-dms-open', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/mcp-dms-open')>()
  return {
    ...actual,
    callDocumentSearchOpen: vi.fn(),
  }
})

vi.mock('@/lib/mcp-agrar-open', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/mcp-agrar-open')>()
  return {
    ...actual,
    callAgrarContractOpen: vi.fn(),
    callWeighingTicketOpen: vi.fn(),
  }
})

vi.mock('@/lib/mcp-stock-open', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/mcp-stock-open')>()
  return {
    ...actual,
    callStockBestandOpen: vi.fn(),
  }
})

import { callAgrarContractOpen, callWeighingTicketOpen } from '@/lib/mcp-agrar-open'
import { callCellStatusOpen } from '@/lib/mcp-cell-open'
import { callCustomerOpen } from '@/lib/mcp-customer-open'
import { callDocumentSearchOpen } from '@/lib/mcp-dms-open'
import { callLotTraceOpen } from '@/lib/mcp-lot-open'
import { callOrderStatusOpen } from '@/lib/mcp-order-open'
import { callPoStatusOpen } from '@/lib/mcp-po-open'
import { callStockBestandOpen } from '@/lib/mcp-stock-open'

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
    vi.mocked(callOrderStatusOpen).mockReset()
    vi.mocked(callLotTraceOpen).mockReset()
    vi.mocked(callCellStatusOpen).mockReset()
    vi.mocked(callPoStatusOpen).mockReset()
    vi.mocked(callDocumentSearchOpen).mockReset()
    vi.mocked(callAgrarContractOpen).mockReset()
    vi.mocked(callWeighingTicketOpen).mockReset()
    vi.mocked(callStockBestandOpen).mockReset()
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

  it('nav-orders ohne auftrag_nr oeffnet die Auftragsliste', async () => {
    function ListTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button type="button" onClick={() => { void dispatch('nav-orders') }}>
          Orders
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

    fireEvent.click(screen.getByRole('button', { name: 'Orders' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/sales/auftraege-liste')
    })
    expect(callOrderStatusOpen).not.toHaveBeenCalled()
  })

  it('nav-orders mit auftrag_nr navigiert auf MCP route_path', async () => {
    vi.mocked(callOrderStatusOpen).mockResolvedValue({
      order_id: 'ord-1',
      auftrag_nr: 'SO-100',
      status: 'confirmed',
      route_path: '/sales/order-editor/ord-1',
      screen_id: 'sales/sales-order',
    })

    function OpenTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-orders', { auftrag_nr: 'SO-100' })
          }}
        >
          Open order
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

    fireEvent.click(screen.getByRole('button', { name: 'Open order' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/sales/order-editor/ord-1')
    })
    expect(callOrderStatusOpen).toHaveBeenCalledWith('SO-100')
  })

  it('nav-orders mit sicherem route_path navigiert ohne MCP', async () => {
    function DirectTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-orders', { route_path: '/sales/order-editor/direct-1' })
          }}
        >
          Direct order
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

    fireEvent.click(screen.getByRole('button', { name: 'Direct order' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/sales/order-editor/direct-1')
    })
    expect(callOrderStatusOpen).not.toHaveBeenCalled()
  })

  it('nav-lot ohne lot_id oeffnet die Lot-Rueckverfolgung', async () => {
    function ListTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button type="button" onClick={() => { void dispatch('nav-lot') }}>
          Lots
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

    fireEvent.click(screen.getByRole('button', { name: 'Lots' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/charge/rueckverfolgung')
    })
    expect(callLotTraceOpen).not.toHaveBeenCalled()
  })

  it('nav-lot mit lot_id navigiert auf MCP route_path', async () => {
    vi.mocked(callLotTraceOpen).mockResolvedValue({
      lot_id: 'lot-uuid-1',
      status: 'active',
      route_path: '/charge/stamm/lot-uuid-1',
      screen_id: 'charge/stamm',
    })

    function OpenTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-lot', { lot_id: 'LOT-42' })
          }}
        >
          Open lot
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

    fireEvent.click(screen.getByRole('button', { name: 'Open lot' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/charge/stamm/lot-uuid-1')
    })
    expect(callLotTraceOpen).toHaveBeenCalledWith('LOT-42')
  })

  it('nav-lot mit sicherem route_path navigiert ohne MCP', async () => {
    function DirectTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-lot', { route_path: '/charge/stamm/direct-1' })
          }}
        >
          Direct lot
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

    fireEvent.click(screen.getByRole('button', { name: 'Direct lot' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/charge/stamm/direct-1')
    })
    expect(callLotTraceOpen).not.toHaveBeenCalled()
  })

  it('nav-silo-cell ohne cell_code oeffnet die Silo-Uebersicht', async () => {
    function ListTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button type="button" onClick={() => { void dispatch('nav-silo-cell') }}>
          Cells
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

    fireEvent.click(screen.getByRole('button', { name: 'Cells' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/lager/silo-uebersicht')
    })
    expect(callCellStatusOpen).not.toHaveBeenCalled()
  })

  it('nav-silo-cell mit cell_code navigiert auf MCP route_path', async () => {
    vi.mocked(callCellStatusOpen).mockResolvedValue({
      cell_id: 'cell-uuid-1',
      cell_code: 'ZELLE-A1',
      qs_status: 'frei',
      route_path: '/lager/silo-zellen/cell-uuid-1',
      screen_id: 'lager/silo-cell',
    })

    function OpenTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-silo-cell', { cell_code: 'ZELLE-A1' })
          }}
        >
          Open cell
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

    fireEvent.click(screen.getByRole('button', { name: 'Open cell' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/lager/silo-zellen/cell-uuid-1')
    })
    expect(callCellStatusOpen).toHaveBeenCalledWith('ZELLE-A1')
  })

  it('nav-silo-cell mit sicherem route_path navigiert ohne MCP', async () => {
    function DirectTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-silo-cell', { route_path: '/lager/silo-zellen/direct-1' })
          }}
        >
          Direct cell
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

    fireEvent.click(screen.getByRole('button', { name: 'Direct cell' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/lager/silo-zellen/direct-1')
    })
    expect(callCellStatusOpen).not.toHaveBeenCalled()
  })

  it('nav-einkauf ohne bestellung_id oeffnet die Bestellliste', async () => {
    function ListTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button type="button" onClick={() => { void dispatch('nav-einkauf') }}>
          Einkauf
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

    fireEvent.click(screen.getByRole('button', { name: 'Einkauf' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/einkauf/bestellungen')
    })
    expect(callPoStatusOpen).not.toHaveBeenCalled()
  })

  it('nav-einkauf mit bestellung_id navigiert auf MCP route_path', async () => {
    vi.mocked(callPoStatusOpen).mockResolvedValue({
      bestellung_id: 'po-uuid-1',
      bestellnummer: 'BE-100',
      status: 'offen',
      route_path: '/einkauf/bestellung/po-uuid-1',
      screen_id: 'einkauf/purchase-order',
    })

    function OpenTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-einkauf', { bestellung_id: 'BE-100' })
          }}
        >
          Open PO
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

    fireEvent.click(screen.getByRole('button', { name: 'Open PO' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/einkauf/bestellung/po-uuid-1')
    })
    expect(callPoStatusOpen).toHaveBeenCalledWith('BE-100')
  })

  it('nav-einkauf mit sicherem route_path navigiert ohne MCP', async () => {
    function DirectTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-einkauf', { route_path: '/einkauf/bestellung/direct-1' })
          }}
        >
          Direct PO
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

    fireEvent.click(screen.getByRole('button', { name: 'Direct PO' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/einkauf/bestellung/direct-1')
    })
    expect(callPoStatusOpen).not.toHaveBeenCalled()
  })

  it('nav-nachweisraum ohne dokument_id oeffnet den Nachweisraum', async () => {
    function ListTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button type="button" onClick={() => { void dispatch('nav-nachweisraum') }}>
          DMS
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

    fireEvent.click(screen.getByRole('button', { name: 'DMS' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/docflow/nachweisraum')
    })
    expect(callDocumentSearchOpen).not.toHaveBeenCalled()
  })

  it('nav-nachweisraum mit dokument_id navigiert auf MCP route_path', async () => {
    vi.mocked(callDocumentSearchOpen).mockResolvedValue({
      dokument_id: 'doc-uuid-1',
      titel: 'LS',
      status: 'EINGEGANGEN',
      route_path: '/docflow/nachweisraum/doc-uuid-1',
      screen_id: 'docflow/nachweisraum',
    })

    function OpenTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-nachweisraum', { dokument_id: 'doc-uuid-1' })
          }}
        >
          Open doc
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

    fireEvent.click(screen.getByRole('button', { name: 'Open doc' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/docflow/nachweisraum/doc-uuid-1')
    })
    expect(callDocumentSearchOpen).toHaveBeenCalledWith('doc-uuid-1')
  })

  it('nav-nachweisraum mit sicherem route_path navigiert ohne MCP', async () => {
    function DirectTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-nachweisraum', { route_path: '/docflow/nachweisraum/direct-1' })
          }}
        >
          Direct doc
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

    fireEvent.click(screen.getByRole('button', { name: 'Direct doc' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/docflow/nachweisraum/direct-1')
    })
    expect(callDocumentSearchOpen).not.toHaveBeenCalled()
  })

  it('nav-agrar-vertraege mit kontrakt_id navigiert auf MCP route_path', async () => {
    vi.mocked(callAgrarContractOpen).mockResolvedValue({
      kontrakt_id: 'c1',
      status: 'open',
      route_path: '/agrar/kontrakt/c1',
      screen_id: 'agrar/kontrakte',
    })

    function OpenTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-agrar-vertraege', { kontrakt_id: 'K-1' })
          }}
        >
          Open contract
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

    fireEvent.click(screen.getByRole('button', { name: 'Open contract' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/agrar/kontrakt/c1')
    })
    expect(callAgrarContractOpen).toHaveBeenCalledWith('K-1')
  })

  it('nav-wiegeschein mit ticket_id navigiert auf MCP route_path', async () => {
    vi.mocked(callWeighingTicketOpen).mockResolvedValue({
      ticket_id: 't1',
      partie_id: 'p1',
      route_path: '/waage/wiegeschein/t1',
      screen_id: 'waage/wiegeschein',
    })

    function OpenTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-wiegeschein', { ticket_id: 't1' })
          }}
        >
          Open ticket
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

    fireEvent.click(screen.getByRole('button', { name: 'Open ticket' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/waage/wiegeschein/t1')
    })
    expect(callWeighingTicketOpen).toHaveBeenCalledWith('t1')
  })

  it('nav-lager mit artikel_id navigiert auf MCP route_path', async () => {
    vi.mocked(callStockBestandOpen).mockResolvedValue({
      artikel_id: 'a1',
      verfuegbar: 35,
      route_path: '/lager/artikel/a1',
      screen_id: 'lager/article-stock',
    })

    function OpenTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button
          type="button"
          onClick={() => {
            void dispatch('nav-lager', { artikel_id: 'ART-1' })
          }}
        >
          Open stock
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

    fireEvent.click(screen.getByRole('button', { name: 'Open stock' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/lager/artikel/a1')
    })
    expect(callStockBestandOpen).toHaveBeenCalledWith('ART-1')
  })

  it('nav-lager ohne artikel_id oeffnet die Bestandsuebersicht', async () => {
    function ListTrigger(): JSX.Element {
      const { dispatch } = useActionDispatch()
      return (
        <button type="button" onClick={() => { void dispatch('nav-lager') }}>
          Lager
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

    fireEvent.click(screen.getByRole('button', { name: 'Lager' }))
    await waitFor(() => {
      expect(screen.getByTestId('location').textContent).toBe('/lager/bestandsuebersicht')
    })
    expect(callStockBestandOpen).not.toHaveBeenCalled()
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
