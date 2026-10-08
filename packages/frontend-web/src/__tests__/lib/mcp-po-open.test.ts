import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  callPoStatusOpen,
  isSafePoRoutePath,
  pickSafePoRoutePath,
} from '@/lib/mcp-po-open'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

import { apiClient } from '@/lib/api-client'

describe('mcp-po-open route guard', () => {
  it('accepts canonical relative purchase-order paths', () => {
    expect(isSafePoRoutePath('/einkauf/bestellung/po-uuid-1')).toBe(true)
    expect(isSafePoRoutePath('/einkauf/bestellung/a1b2c3d4-e5f6-7890-abcd-ef1234567890')).toBe(true)
  })

  it('rejects open redirects and non-PO einkauf paths', () => {
    expect(isSafePoRoutePath('https://evil.example/einkauf/bestellung/x')).toBe(false)
    expect(isSafePoRoutePath('//evil.example/einkauf/bestellung/x')).toBe(false)
    expect(isSafePoRoutePath('/einkauf/bestellung/x?next=https://evil')).toBe(false)
    expect(isSafePoRoutePath('/einkauf/bestellung/x#tab')).toBe(false)
    expect(isSafePoRoutePath('/einkauf/bestellungen')).toBe(false)
    expect(isSafePoRoutePath('/einkauf/bestellungen/po-1')).toBe(false)
    expect(isSafePoRoutePath('/sales/order-editor/o1')).toBe(false)
    expect(pickSafePoRoutePath('/einkauf/bestellung/ok')).toBe('/einkauf/bestellung/ok')
    expect(pickSafePoRoutePath('/einkauf/bestellung/ok?x=1')).toBeNull()
  })
})

describe('callPoStatusOpen', () => {
  beforeEach(() => {
    vi.mocked(apiClient.post).mockReset()
  })

  it('returns the safe route from MCP dryRun', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        bestellung_id: 'po-uuid-1',
        bestellnummer: 'BE-100',
        status: 'offen',
        route_path: '/einkauf/bestellung/po-uuid-1',
        screen_id: 'einkauf/purchase-order',
      },
    } as never)

    const result = await callPoStatusOpen('BE-100')
    expect(result.route_path).toBe('/einkauf/bestellung/po-uuid-1')
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/mcp/tools/call', {
      tool_name: 'einkauf.bestellung.status',
      parameters: { bestellung_id: 'BE-100' },
      mode: 'dryRun',
    })
  })

  it('rejects unsafe MCP route_path', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        bestellung_id: 'po-uuid-1',
        bestellnummer: 'BE-100',
        status: 'offen',
        route_path: 'https://evil.example/x',
        screen_id: 'einkauf/purchase-order',
      },
    } as never)

    await expect(callPoStatusOpen('BE-100')).rejects.toThrow(/unsafe or incomplete route/)
  })
})
