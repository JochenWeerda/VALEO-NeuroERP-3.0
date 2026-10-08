import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  callLotTraceOpen,
  isSafeLotRoutePath,
  pickSafeLotRoutePath,
} from '@/lib/mcp-lot-open'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

import { apiClient } from '@/lib/api-client'

describe('mcp-lot-open route guard', () => {
  it('accepts canonical relative lot paths', () => {
    expect(isSafeLotRoutePath('/charge/stamm/lot-uuid-1')).toBe(true)
    expect(isSafeLotRoutePath('/charge/stamm/a1b2c3d4-e5f6-7890-abcd-ef1234567890')).toBe(true)
  })

  it('rejects open redirects and non-lot lager paths', () => {
    expect(isSafeLotRoutePath('https://evil.example/charge/stamm/x')).toBe(false)
    expect(isSafeLotRoutePath('//evil.example/charge/stamm/x')).toBe(false)
    expect(isSafeLotRoutePath('/charge/stamm/x?next=https://evil')).toBe(false)
    expect(isSafeLotRoutePath('/charge/stamm/x#tab')).toBe(false)
    expect(isSafeLotRoutePath('/lager/bestandsuebersicht')).toBe(false)
    expect(isSafeLotRoutePath('/lager/silo-zellen/ZELLE-A1')).toBe(false)
    expect(isSafeLotRoutePath('/charge/rueckverfolgung')).toBe(false)
    expect(pickSafeLotRoutePath('/charge/stamm/ok')).toBe('/charge/stamm/ok')
    expect(pickSafeLotRoutePath('/charge/stamm/ok?x=1')).toBeNull()
  })
})

describe('callLotTraceOpen', () => {
  beforeEach(() => {
    vi.mocked(apiClient.post).mockReset()
  })

  it('returns the safe route from MCP dryRun', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        lot_id: 'lot-uuid-1',
        status: 'active',
        route_path: '/charge/stamm/lot-uuid-1',
        screen_id: 'charge/stamm',
      },
    } as never)

    const result = await callLotTraceOpen('LOT-42')
    expect(result.route_path).toBe('/charge/stamm/lot-uuid-1')
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/mcp/tools/call', {
      tool_name: 'wms.lot.trace',
      parameters: { lot_id: 'LOT-42' },
      mode: 'dryRun',
    })
  })

  it('rejects unsafe MCP route_path', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        lot_id: 'lot-uuid-1',
        status: 'active',
        route_path: 'https://evil.example/x',
        screen_id: 'charge/stamm',
      },
    } as never)

    await expect(callLotTraceOpen('LOT-42')).rejects.toThrow(/unsafe or incomplete route/)
  })
})
