import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  callStockBestandOpen,
  isSafeStockRoutePath,
  pickSafeStockRoutePath,
} from '@/lib/mcp-stock-open'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

import { apiClient } from '@/lib/api-client'

describe('mcp-stock-open route guard', () => {
  it('accepts canonical relative stock article paths', () => {
    expect(isSafeStockRoutePath('/lager/artikel/a1')).toBe(true)
    expect(isSafeStockRoutePath('/lager/artikel/ART-WEIZEN')).toBe(true)
  })

  it('rejects open redirects and non-stock lager paths', () => {
    expect(isSafeStockRoutePath('https://evil.example/lager/artikel/x')).toBe(false)
    expect(isSafeStockRoutePath('/lager/artikel/x?next=1')).toBe(false)
    expect(isSafeStockRoutePath('/lager/artikel/x#tab')).toBe(false)
    expect(isSafeStockRoutePath('/lager/bestandsuebersicht')).toBe(false)
    expect(isSafeStockRoutePath('/lager/silo-zellen/z1')).toBe(false)
    expect(pickSafeStockRoutePath('/lager/artikel/ok')).toBe('/lager/artikel/ok')
    expect(pickSafeStockRoutePath('/lager/artikel/ok?x=1')).toBeNull()
  })
})

describe('callStockBestandOpen', () => {
  beforeEach(() => {
    vi.mocked(apiClient.post).mockReset()
  })

  it('returns the safe route from MCP dryRun', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        artikel_id: 'a1',
        verfuegbar: 35,
        route_path: '/lager/artikel/a1',
        screen_id: 'lager/article-stock',
      },
    } as never)

    const result = await callStockBestandOpen('ART-1')
    expect(result.route_path).toBe('/lager/artikel/a1')
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/mcp/tools/call', {
      tool_name: 'lager.bestand.get',
      parameters: { artikel_id: 'ART-1' },
      mode: 'dryRun',
    })
  })

  it('rejects unsafe MCP route_path', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        artikel_id: 'a1',
        verfuegbar: 35,
        route_path: 'https://evil.example/x',
        screen_id: 'lager/article-stock',
      },
    } as never)

    await expect(callStockBestandOpen('ART-1')).rejects.toThrow(/unsafe or incomplete route/)
  })
})
