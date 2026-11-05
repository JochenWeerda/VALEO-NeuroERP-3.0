import { describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({ get: vi.fn(), useQuery: vi.fn((config: { queryFn: () => Promise<unknown> }) => config) }))
vi.mock('@tanstack/react-query', () => ({ useQuery: mocks.useQuery }))
vi.mock('../api-client', () => ({ apiClient: { get: mocks.get } }))

import { useZulassungenRegister } from './betrieb'

describe('PSM-Zulassungen Hook', () => {
  it('liefert den paginierten Wrapper einschliesslich mandantenweiter Ablaufzahl', async () => {
    const payload = { items: [], total: 51, abgelaufen: 4, page: 1, size: 25, pages: 3, has_next: true, has_prev: false }
    mocks.get.mockResolvedValue({ data: payload })
    useZulassungenRegister()
    const options = mocks.useQuery.mock.calls.at(-1)?.[0]
    expect(options).toBeDefined()
    await expect(options!.queryFn()).resolves.toEqual(payload)
    expect(mocks.get).toHaveBeenCalledWith('/api/v1/agrar/psm/zulassungen')
  })
})
