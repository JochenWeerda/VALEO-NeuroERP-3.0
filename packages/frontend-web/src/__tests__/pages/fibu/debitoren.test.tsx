import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DebitorenPage from '@/pages/fibu/debitoren'

// Mock useNavigate
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

describe('DebitorenPage', () => {
  it('sollte rendern', () => {
    render(
      <MemoryRouter>
        <DebitorenPage />
      </MemoryRouter>,
    )
    
    expect(screen.getByText('Debitorenbuchhaltung')).toBeInTheDocument()
    expect(screen.getByText('Offene Posten Kunden')).toBeInTheDocument()
  })

  it('sollte KPIs anzeigen', () => {
    render(
      <MemoryRouter>
        <DebitorenPage />
      </MemoryRouter>,
    )
    
    expect(screen.getByText('Offene Posten')).toBeInTheDocument()
    expect(screen.getByText('Gesamt Offen')).toBeInTheDocument()
    expect(screen.getByText('Überfällig')).toBeInTheDocument()
  })

  it('sollte Mock-Daten in Tabelle anzeigen', () => {
    render(
      <MemoryRouter>
        <DebitorenPage />
      </MemoryRouter>,
    )
    
    expect(screen.getByText('RE-2025-0123')).toBeInTheDocument()
    expect(screen.getByText('Agrar Schmidt GmbH')).toBeInTheDocument()
  })
})
