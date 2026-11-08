import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import Customer from '@/pages/crm/customer-360-native'
import Lead from '@/pages/crm/lead-native'
import LeadDetail from '@/pages/crm/lead-detail'

const route = vi.hoisted(() => ({ params: {} as { id?: string }, search: '' }))
vi.mock('@/app/routing/typed-router', () => ({
  useParams: () => route.params,
  useSearchParams: () => [new URLSearchParams(route.search)],
}))
vi.mock('@/components/mask-builder/UniversalNativeDetailPage', () => ({
  UniversalNativeDetailPage: ({ screenId, entityId, requestedSectionKey }: {
    screenId: string; entityId?: string; requestedSectionKey?: string
  }) => <output data-testid="party" data-screen-id={screenId} data-entity-id={entityId} data-section={requestedSectionKey} />,
}))

describe('canonical native party entrypoints', () => {
  beforeEach(() => {
    route.params = {}
    route.search = ''
    window.history.replaceState(null, '', '/')
  })
  it.each([[Customer, 'crm/customer-360'], [Lead, 'crm/lead'], [LeadDetail, 'crm/lead']] as const)(
    'preserves route identity over a legacy query identity (%s)', (Page, screenId) => {
      route.params = { id: 'route-record' }
      route.search = 'id=other-record'
      render(<Page />)
      expect(screen.getByTestId('party')).toHaveAttribute('data-screen-id', screenId)
      expect(screen.getByTestId('party')).toHaveAttribute('data-entity-id', 'route-record')
    },
  )
  it.each([[Customer, 'crm/customer-360'], [Lead, 'crm/lead']] as const)(
    'preserves a query deep link and canonical section (%s)', (Page, screenId) => {
      route.search = 'id=legacy-record&tab=chef'
      render(<Page />)
      expect(screen.getByTestId('party')).toHaveAttribute('data-screen-id', screenId)
      expect(screen.getByTestId('party')).toHaveAttribute('data-entity-id', 'legacy-record')
      expect(screen.getByTestId('party')).toHaveAttribute('data-section', 'masterdata')
    },
  )
})
