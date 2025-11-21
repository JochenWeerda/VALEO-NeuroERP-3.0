import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchLeadCandidates } from '@/api/prospecting'
import { apiClient } from '@/lib/api-client'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(() => Promise.resolve({ data: [] })),
  },
}))

const mockedGet = vi.mocked(apiClient.get)

describe('fetchLeadCandidates', () => {
  beforeEach(() => {
    mockedGet.mockClear()
  })

  it('überträgt alle Query-Parameter korrekt', async () => {
    await fetchLeadCandidates({
      refYear: 2025,
      minPotential: 75000,
      region: 'my-region',
      source: 'gap_de',
      segment: 'A',
      onlyNewProspects: true,
      onlyHighPriority: true,
      limit: 50,
    })

    expect(mockedGet).toHaveBeenCalledTimes(1)
    const requestedUrl = mockedGet.mock.calls[0][0] as string
    const [, query] = requestedUrl.split('?')
    const params = new URLSearchParams(query)

    expect(params.get('ref_year')).toBe('2025')
    expect(params.get('min_potential')).toBe('75000')
    expect(params.get('region')).toBe('my-region')
    expect(params.get('source')).toBe('gap_de')
    expect(params.get('segment')).toBe('A')
    expect(params.get('only_new_prospects')).toBe('true')
    expect(params.get('only_high_priority')).toBe('true')
    expect(params.get('limit')).toBe('50')
  })
})
