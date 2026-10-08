import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  callCellStatusOpen,
  isSafeCellRoutePath,
  pickSafeCellRoutePath,
} from '@/lib/mcp-cell-open'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

import { apiClient } from '@/lib/api-client'

describe('mcp-cell-open route guard', () => {
  it('accepts canonical relative silo cell paths', () => {
    expect(isSafeCellRoutePath('/lager/silo-zellen/cell-uuid-1')).toBe(true)
    expect(isSafeCellRoutePath('/lager/silo-zellen/a1b2c3d4-e5f6-7890-abcd-ef1234567890')).toBe(true)
  })

  it('rejects open redirects and non-cell lager paths', () => {
    expect(isSafeCellRoutePath('https://evil.example/lager/silo-zellen/x')).toBe(false)
    expect(isSafeCellRoutePath('//evil.example/lager/silo-zellen/x')).toBe(false)
    expect(isSafeCellRoutePath('/lager/silo-zellen/x?next=https://evil')).toBe(false)
    expect(isSafeCellRoutePath('/lager/silo-zellen/x#tab')).toBe(false)
    expect(isSafeCellRoutePath('/lager/silo-uebersicht')).toBe(false)
    expect(isSafeCellRoutePath('/charge/stamm/lot-1')).toBe(false)
    expect(pickSafeCellRoutePath('/lager/silo-zellen/ok')).toBe('/lager/silo-zellen/ok')
    expect(pickSafeCellRoutePath('/lager/silo-zellen/ok?x=1')).toBeNull()
  })
})

describe('callCellStatusOpen', () => {
  beforeEach(() => {
    vi.mocked(apiClient.post).mockReset()
  })

  it('returns the safe route from MCP dryRun', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        cell_id: 'cell-uuid-1',
        cell_code: 'ZELLE-A1',
        qs_status: 'frei',
        route_path: '/lager/silo-zellen/cell-uuid-1',
        screen_id: 'lager/silo-cell',
      },
    } as never)

    const result = await callCellStatusOpen('ZELLE-A1')
    expect(result.route_path).toBe('/lager/silo-zellen/cell-uuid-1')
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/mcp/tools/call', {
      tool_name: 'wms.cell.status',
      parameters: { cell_code: 'ZELLE-A1' },
      mode: 'dryRun',
    })
  })

  it('rejects unsafe MCP route_path', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        cell_id: 'cell-uuid-1',
        cell_code: 'ZELLE-A1',
        qs_status: 'frei',
        route_path: 'https://evil.example/x',
        screen_id: 'lager/silo-cell',
      },
    } as never)

    await expect(callCellStatusOpen('ZELLE-A1')).rejects.toThrow(/unsafe or incomplete route/)
  })
})
