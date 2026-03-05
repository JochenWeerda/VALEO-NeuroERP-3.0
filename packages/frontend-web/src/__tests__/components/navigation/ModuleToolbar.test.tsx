/**
 * Test: ModuleToolbar – Verdrahtung Zurück/Schließen/Startseite
 * Stellt sicher, dass Klick auf Zurück navigate(backTarget) auslöst.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'

const mockNavigate = vi.fn()

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>()
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('ModuleToolbar', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
  })

  it('rendert Zurück-Button wenn backTarget gesetzt', () => {
    render(
      <MemoryRouter>
        <ModuleToolbar backTarget="/agrar/ernte" closeTarget="/agrar/ernte" />
      </MemoryRouter>,
    )
    const backButton = screen.getByRole('button', { name: /zurück/i })
    expect(backButton).toBeInTheDocument()
  })

  it('ruft navigate(backTarget) auf bei Klick auf Zurück', () => {
    render(
      <MemoryRouter>
        <ModuleToolbar backTarget="/agrar/ernte" closeTarget="/agrar/ernte" />
      </MemoryRouter>,
    )
    const backButton = screen.getByRole('button', { name: /zurück/i })
    fireEvent.click(backButton)
    expect(mockNavigate).toHaveBeenCalledTimes(1)
    expect(mockNavigate).toHaveBeenCalledWith('/agrar/ernte')
  })

  it('ruft navigate(closeTarget) auf bei Klick auf Schließen wenn closeTarget !== backTarget', () => {
    render(
      <MemoryRouter>
        <ModuleToolbar backTarget="/einkauf" closeTarget="/einkauf/lieferschein-liste" />
      </MemoryRouter>,
    )
    const closeButton = screen.getByRole('button', { name: /schließen/i })
    fireEvent.click(closeButton)
    expect(mockNavigate).toHaveBeenCalledWith('/einkauf/lieferschein-liste')
  })

  it('rendert Startseite-Link wenn showHome true', () => {
    render(
      <MemoryRouter>
        <ModuleToolbar backTarget="/finance/debitoren" showHome />
      </MemoryRouter>,
    )
    const homeLink = screen.getByRole('link', { name: /zur startseite/i })
    expect(homeLink).toBeInTheDocument()
    expect(homeLink).toHaveAttribute('href', '/')
  })

  it('rendert nichts wenn weder backTarget noch closeTarget noch showHome', () => {
    const { container } = render(
      <MemoryRouter>
        <ModuleToolbar showHome={false} />
      </MemoryRouter>,
    )
    const toolbar = container.querySelector('[role="toolbar"]')
    expect(toolbar).toBeNull()
  })
})
