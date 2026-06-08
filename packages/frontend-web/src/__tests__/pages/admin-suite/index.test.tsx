import { MemoryRouter } from '@/app/routing/test-router'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import AdminSuiteHomePage from '@/pages/admin-suite/index'

const refetchMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/admin-suite', () => ({
  useAdminSuiteReadiness: () => ({
    data: {
      status: 'warning',
      score: 0,
      ready_count: 0,
      warning_count: 3,
      blocked_count: 0,
      unchecked_count: 5,
      evaluated_count: 3,
      checked_at: '2026-05-30T12:00:00Z',
      evidence: [
        {
          key: 'setup',
          label: 'Ersteinrichtung',
          status: 'unchecked',
          source: '/admin/setup',
          evidence: 'Persistierter Abschlussnachweis fehlt.',
          details: [],
          checked_at: '2026-05-30T12:00:00Z',
        },
        {
          key: 'connectors',
          label: 'Schnittstellen',
          status: 'warning',
          source: 'app.services.integration_bootstrap',
          evidence: 'Produktive Live-Evidenz steht noch aus.',
          details: ['Live-Probes wurden nicht ausgefuehrt.'],
          checked_at: '2026-05-30T12:00:00Z',
        },
      ],
    },
    isLoading: false,
    isError: false,
    error: null,
    refetch: refetchMock,
  }),
}))

describe('AdminSuiteHomePage', () => {
  it('shows honest readiness status, evidence and existing admin links', () => {
    render(
      <MemoryRouter>
        <AdminSuiteHomePage />
      </MemoryRouter>,
    )

    expect(screen.getByText('VALEO Admin Suite')).toBeInTheDocument()
    expect(screen.getByText('Go-Live Readiness: 0%')).toBeInTheDocument()
    expect(screen.getByText('Nicht geprueft')).toBeInTheDocument()
    expect(screen.getByText('Produktive Live-Evidenz steht noch aus.')).toBeInTheDocument()
    expect(screen.getAllByRole('link', { name: 'Bereich oeffnen' })[0]).toHaveAttribute('href', '/admin-suite/setup')
  })
})
