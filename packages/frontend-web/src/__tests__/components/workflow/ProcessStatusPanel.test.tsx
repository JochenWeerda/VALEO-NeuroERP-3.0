import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'

const view = {
  statusLabel: 'Freigegeben',
  statusClassName: 'bg-blue-50 text-blue-800 border-blue-300',
  summary: 'Aktion ist zulaessig.',
  details: ['Detail A', 'Detail B'],
}

async function renderPanelForRoles(roles: string[]) {
  vi.resetModules()
  vi.doMock('@/lib/auth', () => ({
    auth: {
      getUser: () => ({ roles }),
    },
  }))
  vi.doMock('@/hooks/useTenant', () => ({
    useTenant: () => ({ tenantId: '00000000-0000-0000-0000-000000000001', setTenantId: vi.fn() }),
  }))

  const { ProcessStatusPanel } = await import('@/components/workflow/ProcessStatusPanel')

  render(<ProcessStatusPanel view={view} title="Prozessstatus" />)
}

describe('ProcessStatusPanel role density', () => {
  beforeEach(() => {
    vi.resetModules()
  })

  it('zeigt fuer fokussierte Rollen nur den ersten Detailpunkt', async () => {
    await renderPanelForRoles(['user'])

    expect(screen.getByText('Detail A')).toBeInTheDocument()
    expect(screen.queryByText('Detail B')).not.toBeInTheDocument()
  })

  it('zeigt fuer verdichtete Rollen alle Details', async () => {
    await renderPanelForRoles(['manager'])

    expect(screen.getByText('Detail A')).toBeInTheDocument()
    expect(screen.getByText('Detail B')).toBeInTheDocument()
  })

  it('zieht Approval-Kontexte auch fuer einfache Rollen auf mehr Details hoch', async () => {
    vi.resetModules()
    vi.doMock('@/lib/auth', () => ({
      auth: {
        getUser: () => ({ roles: ['user'] }),
      },
    }))
    vi.doMock('@/hooks/useTenant', () => ({
      useTenant: () => ({ tenantId: 'tenant-finance-01', setTenantId: vi.fn() }),
    }))

    const { ProcessStatusPanel } = await import('@/components/workflow/ProcessStatusPanel')

    render(
      <ProcessStatusPanel
        view={{
          ...view,
          details: ['Detail A', 'Detail B', 'Detail C'],
          requiresApproval: true,
          context: { pageDomain: 'finance-approval' },
        }}
        title="Prozessstatus"
      />,
    )

    expect(screen.getByText('Detail A')).toBeInTheDocument()
    expect(screen.getByText('Detail B')).toBeInTheDocument()
    expect(screen.getByText('Detail C')).toBeInTheDocument()
  })
})
