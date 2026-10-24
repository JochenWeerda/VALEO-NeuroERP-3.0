import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import PartyNativePage from '@/pages/crm/party-native'

vi.mock('@/components/mask-builder/UniversalNativeDetailPage', () => ({
  UniversalNativeDetailPage: (props: {
    screenId: string
    entityId?: string
    requestedSectionKey?: string
    testId?: string
  }) => <div data-testid="detail-contract" data-screen={props.screenId}
    data-entity={props.entityId} data-section={props.requestedSectionKey} data-custom-id={props.testId} />,
}))

describe('CRM native adapter render contract', () => {
  it.each([
    ['lead', 'crm/lead'],
    ['customer', 'crm/customer-360'],
    [undefined, 'crm/customer-360'],
  ] as const)('routes %s to the correct definition and preserves the selected entity', (kind, expected) => {
    const view = render(<PartyNativePage kind={kind} entityId="synthetic-entity"
      requestedSectionKey="finance" testId="synthetic-detail" />)
    const detail = screen.getByTestId('detail-contract')
    expect(detail.getAttribute('data-screen')).toBe(expected)
    expect(detail.getAttribute('data-entity')).toBe('synthetic-entity')
    expect(detail.getAttribute('data-section')).toBe('finance')
    expect(detail.getAttribute('data-custom-id')).toBe('synthetic-detail')
    view.unmount()
  })
})
