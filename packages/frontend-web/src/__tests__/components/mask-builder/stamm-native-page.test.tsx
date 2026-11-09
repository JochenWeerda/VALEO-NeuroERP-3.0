import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import { TypedParamsContext } from '@/app/routing/typed-router'
import { createStammNativeDetailPage } from '@/components/mask-builder/StammNativeDetailRoute'

vi.mock('@/components/mask-builder/UniversalNativeCreatePage', () => ({
  UniversalNativeCreatePage: ({ screenId, testId }: { screenId: string; testId?: string }) =>
    <div data-testid="create">{`${screenId}|${testId}`}</div>,
}))
vi.mock('@/components/mask-builder/UniversalNativeDetailPage', () => ({
  UniversalNativeDetailPage: ({ screenId, entityId, testId }: { screenId: string; entityId?: string; testId?: string }) =>
    <div data-testid="detail">{`${screenId}|${entityId}|${testId}`}</div>,
}))

function mount(Page: ReturnType<typeof createStammNativeDetailPage>, id?: string) {
  return render(<MemoryRouter initialEntries={['/stamm']}>
    <TypedParamsContext.Provider value={id === undefined ? {} : { id }}><Page /></TypedParamsContext.Provider>
  </MemoryRouter>)
}

describe('createStammNativeDetailPage ohne Legacy-Anlage', () => {
  const Page = createStammNativeDetailPage('crm/customer-360', 'crm-kunden-stamm')

  it.each([undefined, '', 'new', 'neu'])('legt bei %s ueber die creation der ScreenDefinition an', (id) => {
    mount(Page, id)
    expect(screen.getByTestId('create').textContent).toBe('crm/customer-360|crm-kunden-stamm-create')
    expect(screen.queryByTestId('detail')).toBeNull()
  })

  it('zeigt eine bestehende Entitaet im nativen Detail', () => {
    mount(Page, 'K-4711')
    expect(screen.getByTestId('detail').textContent).toBe('crm/customer-360|K-4711|crm-kunden-stamm')
    expect(screen.queryByTestId('create')).toBeNull()
  })

  it('nutzt eine eigene Anlage-ScreenDefinition, wenn angegeben', () => {
    mount(createStammNativeDetailPage('finance/debitor', 'finance-debitoren-stamm', undefined, 'finance/debitoren/new'), 'neu')
    expect(screen.getByTestId('create').textContent).toBe('finance/debitoren/new|finance-debitoren-stamm-create')
  })
})
