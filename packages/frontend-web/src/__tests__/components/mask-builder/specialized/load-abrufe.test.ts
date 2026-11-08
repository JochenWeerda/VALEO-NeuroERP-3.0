import { describe, expect, it, vi, afterEach } from 'vitest'
import { AxiosError } from 'axios'
import { apiClient } from '@/lib/api-client'
import {
  ABRUFE_AUTH_ERROR,
  DISPOSITIONEN_PATH,
  KONTRAKTE_LIST_ENDPOINT,
  fetchOpenAbrufe,
} from '@/components/mask-builder/specialized/load-abrufe'

afterEach(() => {
  vi.restoreAllMocks()
})

function axiosError(status: number): AxiosError {
  const error = new AxiosError('request failed')
  error.response = {
    status,
    statusText: 'Error',
    headers: {},
    config: {} as never,
    data: { detail: 'denied' },
  }
  return error
}

describe('fetchOpenAbrufe', () => {
  it('liest Abrufe über GET /api/v1/kontrakte/{id}/dispositionen', async () => {
    const get = vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (url === KONTRAKTE_LIST_ENDPOINT) {
        return { data: { items: [{ contract_id: 'c1' }], total: 1 } } as never
      }
      if (url === DISPOSITIONEN_PATH('c1')) {
        return {
          data: [
            {
              id: 'abruf-1',
              kontrakt_id: 'c1',
              kontrakt_nr: 'K-100',
              disposition_nr: 1,
              menge: 12,
              status: 'FREIGEGEBEN',
            },
            {
              id: 'abruf-old',
              kontrakt_id: 'c1',
              kontrakt_nr: 'K-100',
              disposition_nr: 2,
              menge: 4,
              status: 'GELIEFERT',
            },
          ],
        } as never
      }
      throw new Error(`unerwarteter GET ${url}`)
    })

    const cards = await fetchOpenAbrufe()
    expect(get).toHaveBeenCalledWith(KONTRAKTE_LIST_ENDPOINT, expect.objectContaining({
      params: expect.objectContaining({ status: 'OFFEN', limit: 20 }),
    }))
    expect(get).toHaveBeenCalledWith(DISPOSITIONEN_PATH('c1'))
    expect(cards).toEqual([
      { id: 'abruf-1', label: 'K-100 Abruf 1', quantity: 12, contractId: 'c1', abrufId: 'abruf-1' },
    ])
  })

  it('wirft bei 403 einen ehrlichen Fehler und liefert kein leeres Mock', async () => {
    vi.spyOn(apiClient, 'get').mockRejectedValue(axiosError(403))
    await expect(fetchOpenAbrufe()).rejects.toThrow(ABRUFE_AUTH_ERROR)
  })
})
