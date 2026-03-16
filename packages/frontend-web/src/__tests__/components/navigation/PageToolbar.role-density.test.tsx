import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'

vi.mock('@/features/ki-usability', () => ({
  useActionDispatchOptional: () => null,
}))

function createAction(id: string) {
  return {
    id,
    label: id,
    onClick: vi.fn(),
  }
}

async function renderToolbarForRoles(roles: string[]) {
  vi.resetModules()
  vi.doMock('@/lib/auth', () => ({
    auth: {
      getUser: () => ({ roles }),
    },
  }))
  vi.doMock('@/hooks/useTenant', () => ({
    useTenant: () => ({ tenantId: '00000000-0000-0000-0000-000000000001', setTenantId: vi.fn() }),
  }))

  const { PageToolbar } = await import('@/components/navigation/PageToolbar')

  render(
    <PageToolbar
      title="Toolbar"
      primaryActions={[createAction('a1'), createAction('a2'), createAction('a3')]}
      overflowActions={[createAction('o1')]}
    />,
  )
}

describe('PageToolbar role density', () => {
  beforeEach(() => {
    vi.resetModules()
  })

  it('reduziert fokussierte Rollen auf zwei Primary-Actions', async () => {
    await renderToolbarForRoles(['user'])

    expect(screen.getByRole('button', { name: 'a1' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'a2' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'a3' })).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: 'More actions' }))

    expect(screen.getByRole('button', { name: 'a3' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'o1' })).toBeInTheDocument()
  })

  it('hebt Finance-Kontext mit vielen Actions auf mehr sichtbare Primary-Actions an', async () => {
    vi.resetModules()
    vi.doMock('@/lib/auth', () => ({
      auth: {
        getUser: () => ({ roles: ['user'] }),
      },
    }))
    vi.doMock('@/hooks/useTenant', () => ({
      useTenant: () => ({ tenantId: 'tenant-finance-01', setTenantId: vi.fn() }),
    }))

    const { PageToolbar } = await import('@/components/navigation/PageToolbar')

    render(
      <PageToolbar
        title="Toolbar"
        primaryActions={[createAction('a1'), createAction('a2'), createAction('a3'), createAction('a4')]}
        overflowActions={[createAction('o1'), createAction('o2')]}
        mcpContext={{
          pageDomain: 'finance-approval',
          availableActions: ['a1', 'a2', 'a3', 'a4', 'o1', 'o2'],
        }}
      />,
    )

    expect(screen.getByRole('button', { name: 'a1' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'a2' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'a3' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'a4' })).toBeInTheDocument()
  })
})
