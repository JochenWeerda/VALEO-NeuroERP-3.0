import { webcrypto } from 'node:crypto'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AuthService, type AuthConfig } from './auth'

const issuer = 'https://provider.invalid/realms/fixture'
const config: AuthConfig = { oidc: { discoveryUrl: `${issuer}/.well-known/openid-configuration`,
  clientId: 'fixture-browser', redirectUri: 'https://erp.invalid/auth/callback', scopes: ['openid'] } }
const discovery = { issuer, authorization_endpoint: `${issuer}/auth`, token_endpoint: `${issuer}/token`, revocation_endpoint: `${issuer}/revoke` }
const jwt = (claims: object): string => `e30.${btoa(JSON.stringify(claims))}.fixture`
const access = (): string => jwt({ sub: 'synthetic-person', exp: Math.floor(Date.now() / 1000) + 300, realm_access: { roles: ['USER_LESEN'] } })
const response = (body: unknown, ok = true): Response => ({ ok, status: ok ? 200 : 503, json: async () => body }) as Response

beforeEach(() => {
  localStorage.clear()
  sessionStorage.clear()
  vi.restoreAllMocks()
  vi.stubGlobal('crypto', webcrypto)
})

describe('provider authentication', () => {
  it('creates a PKCE S256 challenge and consumes state and nonce once', async () => {
    const navigate = vi.fn()
    const fetcher = vi.fn().mockResolvedValue(response(discovery))
    vi.stubGlobal('fetch', fetcher)
    const auth = new AuthService(config, navigate)
    await auth.login()
    const url = new URL(navigate.mock.calls[0][0])
    expect(url.searchParams.get('code_challenge_method')).toBe('S256')
    const verifier = sessionStorage.getItem('auth_code_verifier')!
    const digest = await webcrypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier))
    const challenge = Buffer.from(digest).toString('base64url')
    expect(url.searchParams.get('code_challenge')).toBe(challenge)
    const state = url.searchParams.get('state')!
    const nonce = url.searchParams.get('nonce')!
    fetcher.mockResolvedValueOnce(response(discovery)).mockResolvedValueOnce(response({
      access_token: access(), refresh_token: 'synthetic-refresh',
      id_token: jwt({ iss: issuer, aud: 'fixture-browser', nonce, exp: Math.floor(Date.now() / 1000) + 300 }),
    }))
    await auth.handleCallback('synthetic-code', state)
    expect(auth.isAuthenticated()).toBe(true)
    const exchange = fetcher.mock.calls.at(-1)![1] as RequestInit
    expect((exchange.body as URLSearchParams).get('code_verifier')).toBe(verifier)
    await expect(auth.handleCallback('synthetic-code', state)).rejects.toThrow()
  })

  it('rejects mismatched discovery and never accepts a development token', async () => {
    localStorage.setItem('access_token', 'dev-token')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response({ ...discovery, issuer: 'https://foreign.invalid' })))
    const navigate = vi.fn(), auth = new AuthService(config, navigate)
    expect(auth.isAuthenticated()).toBe(false)
    await expect(auth.login()).rejects.toThrow()
    expect(navigate).not.toHaveBeenCalled()
  })

  it('rejects an identity nonce mismatch without storing access tokens', async () => {
    sessionStorage.setItem('auth_state', 'synthetic-state')
    sessionStorage.setItem('auth_nonce', 'synthetic-nonce')
    sessionStorage.setItem('auth_code_verifier', 'synthetic-verifier')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(response(discovery)).mockResolvedValueOnce(response({
      access_token: access(), id_token: jwt({ iss: issuer, aud: 'fixture-browser', nonce: 'different', exp: 9999999999 }),
    })))
    const auth = new AuthService(config)
    await expect(auth.handleCallback('synthetic-code', 'synthetic-state')).rejects.toThrow()
    expect(localStorage.getItem('access_token')).toBeNull()
  })

  it('shares refresh and prevents its completion from reviving a logged-out session', async () => {
    localStorage.setItem('access_token', access())
    localStorage.setItem('refresh_token', 'synthetic-refresh')
    let finish!: (value: Response) => void
    const pending = new Promise<Response>(resolve => { finish = resolve })
    const fetcher = vi.fn((url: string) => url === discovery.token_endpoint ? pending : Promise.resolve(response(discovery)))
    vi.stubGlobal('fetch', fetcher)
    const auth = new AuthService(config)
    const first = auth.refreshAccessToken(), second = auth.refreshAccessToken()
    await vi.waitFor(() => expect(fetcher).toHaveBeenCalledWith(discovery.token_endpoint, expect.anything()))
    await auth.logout()
    finish(response({ access_token: access(), refresh_token: 'replacement-refresh' }))
    expect(await first).toBe(false)
    expect(await second).toBe(false)
    expect(auth.isAuthenticated()).toBe(false)
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(fetcher.mock.calls.filter(([url]) => url === discovery.token_endpoint)).toHaveLength(1)
    expect(fetcher).toHaveBeenCalledWith(discovery.revocation_endpoint, expect.anything())
  })

  it('clears local state and reports a failed server revocation', async () => {
    localStorage.setItem('access_token', access())
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(response({}, false)))
    const auth = new AuthService(config)
    await expect(auth.logout()).rejects.toThrow('Widerruf')
    expect(auth.isAuthenticated()).toBe(false)
  })
})


describe('session renewal before transport', () => {
  it('restores expired access only after provider renewal succeeds', async () => {
    localStorage.setItem('access_token', jwt({ sub: 'synthetic-person', exp: Math.floor(Date.now() / 1000) - 1 }))
    localStorage.setItem('refresh_token', 'synthetic-refresh')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(response(discovery)).mockResolvedValueOnce(response({ access_token: access(), refresh_token: 'rotated-refresh' })))
    const auth = new AuthService(config)
    expect(auth.isAuthenticated()).toBe(false)
    expect(auth.getAccessToken()).toBeNull()
    expect(await auth.getFreshAccessToken()).toBeTruthy()
    expect(auth.isAuthenticated()).toBe(true)
    expect(localStorage.getItem('refresh_token')).toBe('rotated-refresh')
  })

  it('renews once for simultaneous requests near expiry', async () => {
    localStorage.setItem('access_token', jwt({ sub: 'synthetic-person', exp: Math.floor(Date.now() / 1000) + 5 }))
    localStorage.setItem('refresh_token', 'synthetic-refresh')
    const fresh = access()
    const fetcher = vi.fn().mockResolvedValueOnce(response(discovery)).mockResolvedValueOnce(response({ access_token: fresh, refresh_token: 'rotated-refresh' }))
    vi.stubGlobal('fetch', fetcher)
    const auth = new AuthService(config)
    expect(await Promise.all([auth.getFreshAccessToken(), auth.getFreshAccessToken()])).toEqual([fresh, fresh])
    expect(fetcher.mock.calls.filter(([url]) => url === discovery.token_endpoint)).toHaveLength(1)
  })

  it('avoids a provider call while sufficient token lifetime remains', async () => {
    const token = access()
    localStorage.setItem('access_token', token)
    const fetcher = vi.fn()
    vi.stubGlobal('fetch', fetcher)
    const auth = new AuthService(config)
    expect(await auth.getFreshAccessToken()).toBe(token)
    expect(fetcher).not.toHaveBeenCalled()
  })

  it('denies access after provider renewal fails', async () => {
    localStorage.setItem('access_token', jwt({ sub: 'synthetic-person', exp: Math.floor(Date.now() / 1000) - 1 }))
    localStorage.setItem('refresh_token', 'synthetic-refresh')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(response(discovery)).mockResolvedValueOnce(response({}, false)))
    const auth = new AuthService(config)
    expect(await auth.getFreshAccessToken()).toBeNull()
    expect(auth.isAuthenticated()).toBe(false)
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })
})
