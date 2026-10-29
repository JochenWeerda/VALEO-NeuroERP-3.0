import { describe, expect, it, vi, afterEach } from 'vitest'
import type { AxiosAdapter } from 'axios'
import { assertTrustedApiDestination } from '@/lib/api-destination'
import { apiClient } from '@/lib/api-client'
import { auth } from '@/lib/auth'

afterEach(() => vi.restoreAllMocks())

describe('ERP identity destination boundary', () => {
  const page = 'https://erp.example.test/admin/studio'
  const trusted = 'https://api.example.test/backend'
  it.each(['/api/v1/items', 'https://api.example.test/api/v1/items', 'https://erp.example.test/api/v1/items'])('allows the trusted API/app destination %s', target => {
    expect(() => assertTrustedApiDestination(target, trusted, trusted, page)).not.toThrow()
  })
  it.each([
    'https://evil.example.test/api/v1/items', '//evil.example.test/api/v1/items',
    'https://api.example.test.evil.test/items', 'https://api.example.test@evil.test/items',
    'javascript:alert(1)', 'data:text/plain,test', 'file:///tmp/data',
    'https://user:password@api.example.test/items', 'https:\\evil.test\\items',
  ])('rejects the untrusted destination without echoing it: %s', target => {
    expect(() => assertTrustedApiDestination(target, trusted, trusted, page)).toThrow('API-Ziel ist nicht freigegeben.')
  })
  it('cannot redirect relative calls by overriding the request base', () => {
    expect(() => assertTrustedApiDestination('/items', 'https://evil.test', trusted, page)).toThrow()
  })
  it('rejects an unconfigured non-browser destination', () => {
    expect(() => assertTrustedApiDestination('/items', undefined, '', undefined)).toThrow()
  })
  it('blocks the actual Axios transport before token refresh or identity headers', async () => {
    const fresh = vi.spyOn(auth, 'getFreshAccessToken').mockResolvedValue('synthetic-test-token')
    const transport = vi.fn<AxiosAdapter>()
    await expect(apiClient.get('https://evil.test/portal/items', { adapter: transport })).rejects.toThrow('API-Ziel ist nicht freigegeben.')
    expect(fresh).not.toHaveBeenCalled()
    expect(transport).not.toHaveBeenCalled()
  })
  it('preserves authorized relative calls and their normal authentication', async () => {
    const fresh = vi.spyOn(auth, 'getFreshAccessToken').mockResolvedValue('synthetic-test-token')
    const transport = vi.fn<AxiosAdapter>(async config => ({ data: { ok: true }, status: 200, statusText: 'OK', headers: {}, config }))
    await apiClient.get('/api/v1/probe', { adapter: transport })
    expect(fresh).toHaveBeenCalledOnce()
    expect(transport).toHaveBeenCalledOnce()
    expect(transport.mock.calls[0][0].headers.Authorization).toBe('Bearer synthetic-test-token')
  })
})
