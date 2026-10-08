import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  callDocumentSearchOpen,
  isSafeDmsDocumentRoutePath,
  isSafeDmsRoutePath,
  pickSafeDmsRoutePath,
} from '@/lib/mcp-dms-open'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

import { apiClient } from '@/lib/api-client'

describe('mcp-dms-open route guard', () => {
  it('accepts canonical DMS and GoBD relative paths', () => {
    expect(isSafeDmsDocumentRoutePath('/docflow/nachweisraum/doc-1')).toBe(true)
    expect(isSafeDmsRoutePath('/docflow/nachweisraum/doc-1')).toBe(true)
    expect(isSafeDmsRoutePath('/docflow/gobd-export/ex-1')).toBe(true)
  })

  it('rejects open redirects and non-DMS paths', () => {
    expect(isSafeDmsRoutePath('https://evil.example/docflow/nachweisraum/x')).toBe(false)
    expect(isSafeDmsRoutePath('//evil.example/docflow/nachweisraum/x')).toBe(false)
    expect(isSafeDmsRoutePath('/docflow/nachweisraum/x?next=https://evil')).toBe(false)
    expect(isSafeDmsRoutePath('/docflow/nachweisraum/x#tab')).toBe(false)
    expect(isSafeDmsRoutePath('/docflow/nachweisraum')).toBe(false)
    expect(isSafeDmsRoutePath('/einkauf/bestellung/po-1')).toBe(false)
    expect(isSafeDmsDocumentRoutePath('/docflow/gobd-export/ex-1')).toBe(false)
    expect(pickSafeDmsRoutePath('/docflow/nachweisraum/ok')).toBe('/docflow/nachweisraum/ok')
    expect(pickSafeDmsRoutePath('/docflow/nachweisraum/ok?x=1')).toBeNull()
  })
})

describe('callDocumentSearchOpen', () => {
  beforeEach(() => {
    vi.mocked(apiClient.post).mockReset()
  })

  it('returns the safe route from MCP dryRun search items', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        count: 1,
        items: [{
          dokument_id: 'doc-uuid-1',
          titel: 'LS',
          status: 'EINGEGANGEN',
          route_path: '/docflow/nachweisraum/doc-uuid-1',
          screen_id: 'docflow/nachweisraum',
        }],
      },
    } as never)

    const result = await callDocumentSearchOpen('doc-uuid-1')
    expect(result.route_path).toBe('/docflow/nachweisraum/doc-uuid-1')
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/mcp/tools/call', {
      tool_name: 'dms.document.search',
      parameters: { dokument_id: 'doc-uuid-1', limit: 1 },
      mode: 'dryRun',
    })
  })

  it('rejects unsafe MCP route_path', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        count: 1,
        items: [{
          dokument_id: 'doc-uuid-1',
          titel: 'LS',
          status: 'EINGEGANGEN',
          route_path: 'https://evil.example/x',
          screen_id: 'docflow/nachweisraum',
        }],
      },
    } as never)

    await expect(callDocumentSearchOpen('doc-uuid-1')).rejects.toThrow(/unsafe or incomplete route/)
  })
})
