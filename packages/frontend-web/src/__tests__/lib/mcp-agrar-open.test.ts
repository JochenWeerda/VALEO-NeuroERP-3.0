import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  callAgrarContractOpen,
  callWeighingTicketOpen,
  isSafeAgrarContractRoutePath,
  isSafeAgrarRoutePath,
  isSafeWeighingRoutePath,
  pickSafeAgrarContractRoutePath,
} from '@/lib/mcp-agrar-open'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

import { apiClient } from '@/lib/api-client'

describe('mcp-agrar-open route guard', () => {
  it('accepts canonical agrar contract and weighing paths', () => {
    expect(isSafeAgrarContractRoutePath('/agrar/kontrakt/c1')).toBe(true)
    expect(isSafeWeighingRoutePath('/waage/wiegeschein/t1')).toBe(true)
    expect(isSafeAgrarRoutePath('/agrar/kontrakt/c1')).toBe(true)
    expect(isSafeAgrarRoutePath('/waage/wiegeschein/t1')).toBe(true)
  })

  it('rejects open redirects and non-agrar paths', () => {
    expect(isSafeAgrarRoutePath('https://evil.example/agrar/kontrakt/x')).toBe(false)
    expect(isSafeAgrarRoutePath('/agrar/kontrakt/x?next=1')).toBe(false)
    expect(isSafeAgrarRoutePath('/agrar/kontrakt/x#tab')).toBe(false)
    expect(isSafeAgrarContractRoutePath('/agrar/vertraege')).toBe(false)
    expect(isSafeAgrarContractRoutePath('/waage/wiegeschein/t1')).toBe(false)
    expect(isSafeWeighingRoutePath('/agrar/kontrakt/c1')).toBe(false)
    expect(pickSafeAgrarContractRoutePath('/agrar/kontrakt/ok')).toBe('/agrar/kontrakt/ok')
    expect(pickSafeAgrarContractRoutePath('/agrar/kontrakt/ok?x=1')).toBeNull()
  })
})

describe('callAgrarContractOpen / callWeighingTicketOpen', () => {
  beforeEach(() => {
    vi.mocked(apiClient.post).mockReset()
  })

  it('returns safe contract route from MCP dryRun', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        kontrakt_id: 'c1',
        status: 'open',
        route_path: '/agrar/kontrakt/c1',
        screen_id: 'agrar/kontrakte',
      },
    } as never)
    const result = await callAgrarContractOpen('K-1')
    expect(result.route_path).toBe('/agrar/kontrakt/c1')
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/mcp/tools/call', {
      tool_name: 'agrar.contract.get',
      parameters: { kontrakt_id: 'K-1' },
      mode: 'dryRun',
    })
  })

  it('returns safe weighing route from MCP list dryRun', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        items: [{
          ticket_id: 't1',
          partie_id: 'p1',
          route_path: '/waage/wiegeschein/t1',
          screen_id: 'waage/wiegeschein',
        }],
      },
    } as never)
    const result = await callWeighingTicketOpen('t1')
    expect(result.route_path).toBe('/waage/wiegeschein/t1')
  })

  it('rejects unsafe contract route_path', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        kontrakt_id: 'c1',
        status: 'open',
        route_path: 'https://evil.example/x',
        screen_id: 'agrar/kontrakte',
      },
    } as never)
    await expect(callAgrarContractOpen('K-1')).rejects.toThrow(/unsafe or incomplete route/)
  })
})
