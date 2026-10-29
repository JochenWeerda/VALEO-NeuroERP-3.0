import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ProcessStatusPanel } from '@/components/workflow/ProcessStatusPanel'

const context = vi.hoisted(() => ({ roles: ['user'], tenantId: 'tenant-density-test' }))
vi.mock('@/lib/auth', () => ({ auth: { getUser: () => ({ roles: context.roles }) } }))
vi.mock('@/hooks/useTenant', () => ({
  useTenant: () => ({ tenantId: context.tenantId, setTenantId: vi.fn() }),
}))

const view = {
  statusLabel: 'Freigegeben',
  statusClassName: 'bg-blue-50 text-blue-800 border-blue-300',
  summary: 'Aktion ist zulaessig.',
  details: ['Detail A', 'Detail B'],
}

async function renderPanelForRoles(roles: string[]) {
  context.roles = roles
  render(<ProcessStatusPanel view={view} title="Prozessstatus" />)
}

describe('ProcessStatusPanel role density', () => {
  beforeEach(() => {
    context.roles = ['user']
    context.tenantId = 'tenant-density-test'
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
    context.tenantId = 'tenant-finance-01'

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
