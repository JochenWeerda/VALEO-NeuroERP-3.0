import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { AxiosAdapter, InternalAxiosRequestConfig } from 'axios'
import { apiClient } from '@/lib/api-client'
import { api } from '@/lib/axios'

const fixture = vi.hoisted(() => ({ fresh: vi.fn(), clear: vi.fn() }))
vi.mock('@/lib/auth', () => ({ auth: { getFreshAccessToken: fixture.fresh, clearTokens: fixture.clear }, handleUnauthorized: fixture.clear }))
const token = `e30.${btoa(JSON.stringify({ tenant_id: 'synthetic-tenant' }))}.fixture`

beforeEach(() => { fixture.fresh.mockReset() })

describe.each(['canonical', 'traced'] as const)('%s HTTP client renewal', client => {
  it('waits for renewal and transports its token and tenant together', async () => {
    let finish!: (token: string | null) => void
    fixture.fresh.mockReturnValue(new Promise(resolve => { finish = resolve }))
    let transported: InternalAxiosRequestConfig | undefined
    const adapter: AxiosAdapter = async config => {
      transported = config
      return { config, data: {}, headers: {}, status: 200, statusText: 'OK' }
    }
    const request = client === 'canonical' ? apiClient.get('/fixture', { adapter }) : api.get('/fixture', { adapter })
    await vi.waitFor(() => expect(fixture.fresh).toHaveBeenCalledOnce())
    expect(transported).toBeUndefined()
    finish(token)
    await request
    expect(transported!.headers.get('Authorization')).toBe(`Bearer ${token}`)
    expect(transported!.headers.get('X-Tenant-ID')).toBe('synthetic-tenant')
  })

  it('does not invent authentication after failed renewal', async () => {
    fixture.fresh.mockResolvedValue(null)
    let transported: InternalAxiosRequestConfig | undefined
    const adapter: AxiosAdapter = async config => {
      transported = config
      return { config, data: {}, headers: {}, status: 200, statusText: 'OK' }
    }
    if (client === 'canonical') await apiClient.get('/fixture', { adapter })
    else await api.get('/fixture', { adapter })
    expect(transported!.headers.get('Authorization')).toBeUndefined()
    expect(transported!.headers.get('X-Tenant-ID')).toBeUndefined()
  })
})
