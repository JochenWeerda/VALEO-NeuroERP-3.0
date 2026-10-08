import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  callCustomerOpen,
  isSafeCustomerRoutePath,
  pickSafeCustomerRoutePath,
} from '@/lib/mcp-customer-open'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

import { apiClient } from '@/lib/api-client'

describe('mcp-customer-open route guard', () => {
  it('accepts canonical relative customer paths', () => {
    expect(isSafeCustomerRoutePath('/crm/customers/cust-uuid-1')).toBe(true)
    expect(isSafeCustomerRoutePath('/crm/customers/a1b2c3d4-e5f6-7890-abcd-ef1234567890')).toBe(true)
  })

  it('rejects open redirects and query fragments', () => {
    expect(isSafeCustomerRoutePath('https://evil.example/crm/customers/x')).toBe(false)
    expect(isSafeCustomerRoutePath('//evil.example/crm/customers/x')).toBe(false)
    expect(isSafeCustomerRoutePath('/crm/customers/x?next=https://evil')).toBe(false)
    expect(isSafeCustomerRoutePath('/crm/customers/x#tab')).toBe(false)
    expect(isSafeCustomerRoutePath('/verkauf/kunden-liste')).toBe(false)
    expect(pickSafeCustomerRoutePath('/crm/customers/ok')).toBe('/crm/customers/ok')
    expect(pickSafeCustomerRoutePath('/crm/customers/ok?x=1')).toBeNull()
  })
})

describe('callCustomerOpen', () => {
  beforeEach(() => {
    vi.mocked(apiClient.post).mockReset()
  })

  it('returns the safe route from MCP dryRun', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        customer_id: 'cust-1',
        kunden_nr: 'TEST',
        name: 'Test GmbH',
        route_path: '/crm/customers/cust-1',
        screen_id: 'crm/customer-360',
      },
    } as never)

    const result = await callCustomerOpen('TEST')
    expect(result.route_path).toBe('/crm/customers/cust-1')
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/mcp/tools/call', {
      tool_name: 'crm.customer.open',
      parameters: { kunden_nr: 'TEST' },
      mode: 'dryRun',
    })
  })

  it('rejects unsafe MCP route_path', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        customer_id: 'cust-1',
        kunden_nr: 'TEST',
        name: 'Test',
        route_path: 'https://evil.example/x',
        screen_id: 'crm/customer-360',
      },
    } as never)

    await expect(callCustomerOpen('TEST')).rejects.toThrow(/unsafe or incomplete route/)
  })
})
