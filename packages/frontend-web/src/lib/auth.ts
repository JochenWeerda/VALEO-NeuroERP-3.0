/** Canonical provider login with PKCE, explicit logout and no development identity. */
import { jwtDecode } from 'jwt-decode'

export interface User {
  sub: string
  email: string
  name: string
  scopes: string[]
  roles: string[]
  exp: number
}
export interface AuthConfig {
  oidc: { discoveryUrl: string; clientId: string; redirectUri: string; scopes: string[] }
}
interface Discovery {
  issuer: string
  authorization_endpoint: string
  token_endpoint: string
  revocation_endpoint?: string
}
const localHost = ['localhost', '127.0.0.1', '[::1]'].includes(window.location.hostname)
const config: AuthConfig = {
  oidc: {
    discoveryUrl: import.meta.env.VITE_OIDC_DISCOVERY_URL || (localHost ? 'http://localhost:8080/realms/valeo-neuro-erp/.well-known/openid-configuration' : ''),
    clientId: import.meta.env.VITE_OIDC_CLIENT_ID || 'valeo-neuro-erp-frontend',
    redirectUri: import.meta.env.VITE_OIDC_REDIRECT_URI || `${window.location.origin}/auth/callback`,
    scopes: ['openid', 'profile', 'email'],
  },
}
const strings = (value: unknown): string[] => Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : []

export class AuthService {
  private accessToken: string | null = null
  private refreshToken: string | null = null
  private user: User | null = null
  private generation = 0
  private refreshPending: Promise<boolean> | null = null

  constructor(private readonly settings: AuthConfig = config,
    private readonly navigate: (url: string) => void = url => window.location.assign(url)) {
    const token = localStorage.getItem('access_token')
    if (token) {
      try { this.setTokens(token, localStorage.getItem('refresh_token') ?? undefined) }
      catch { this.clearTokens() }
    }
  }

  private async discovery(): Promise<Discovery> {
    const location = this.settings.oidc.discoveryUrl
    if (!location) throw new Error('Der Anmeldedienst ist noch nicht konfiguriert.')
    const response = await fetch(location)
    if (!response.ok) throw new Error('Der Anmeldedienst ist nicht erreichbar.')
    const metadata = await response.json() as Discovery
    const expected = location.replace(/\/\.well-known\/openid-configuration\/?$/, '')
    if (metadata.issuer !== expected) throw new Error('Unerwarteter Anmeldedienst.')
    for (const endpoint of [metadata.authorization_endpoint, metadata.token_endpoint, metadata.revocation_endpoint].filter((value): value is string => typeof value === 'string')) {
      const url = new URL(endpoint)
      if (url.origin !== new URL(expected).origin) throw new Error('Unerwarteter Anmelde-Endpunkt.')
    }
    return metadata
  }

  private random(length: number): string {
    const bytes = crypto.getRandomValues(new Uint8Array(length))
    return btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
  }

  async login(): Promise<void> {
    const metadata = await this.discovery()
    const state = this.random(24), nonce = this.random(24), verifier = this.random(48)
    const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier))
    const challenge = btoa(String.fromCharCode(...new Uint8Array(digest))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
    sessionStorage.setItem('auth_state', state)
    sessionStorage.setItem('auth_nonce', nonce)
    sessionStorage.setItem('auth_code_verifier', verifier)
    const params = new URLSearchParams({ client_id: this.settings.oidc.clientId,
      redirect_uri: this.settings.oidc.redirectUri, response_type: 'code', scope: this.settings.oidc.scopes.join(' '),
      state, nonce, code_challenge: challenge, code_challenge_method: 'S256' })
    this.navigate(`${metadata.authorization_endpoint}?${params.toString()}`)
  }

  async handleCallback(code: string, state: string): Promise<void> {
    const saved = sessionStorage.getItem('auth_state'), nonce = sessionStorage.getItem('auth_nonce')
    const verifier = sessionStorage.getItem('auth_code_verifier')
    if (!code || !state || !saved || state !== saved || !nonce || !verifier) throw new Error('Ungueltige Anmeldeantwort.')
    const generation = this.generation
    // A callback is consumed once, including failed code exchanges.
    for (const key of ['auth_state', 'auth_nonce', 'auth_code_verifier']) sessionStorage.removeItem(key)
    const metadata = await this.discovery()
    const response = await fetch(metadata.token_endpoint, { method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ grant_type: 'authorization_code', code, code_verifier: verifier,
        redirect_uri: this.settings.oidc.redirectUri, client_id: this.settings.oidc.clientId }) })
    if (!response.ok) throw new Error('Die Anmeldung konnte nicht abgeschlossen werden.')
    const tokens = await response.json()
    if (typeof tokens.id_token !== 'string') throw new Error('Identitaetsbestaetigung fehlt.')
    const identity = jwtDecode<{ nonce?: string; iss?: string; aud?: string | string[]; exp?: number }>(tokens.id_token)
    const audience = typeof identity.aud === 'string' ? [identity.aud] : identity.aud ?? []
    if (identity.nonce !== nonce || identity.iss !== metadata.issuer || !audience.includes(this.settings.oidc.clientId)
      || typeof identity.exp !== 'number' || identity.exp * 1000 <= Date.now()) throw new Error('Ungueltige Identitaetsbestaetigung.')
    if (generation !== this.generation) throw new Error('Die Anmeldung wurde abgebrochen.')
    this.setTokens(tokens.access_token, tokens.refresh_token)
  }

  private setTokens(token: unknown, refresh?: unknown): void {
    if (typeof token !== 'string') throw new Error('Zugriffstoken fehlt.')
    const user = this.decodeUser(token)
    this.accessToken = token
    this.refreshToken = typeof refresh === 'string' ? refresh : null
    this.user = user
    localStorage.setItem('access_token', token)
    if (this.refreshToken) localStorage.setItem('refresh_token', this.refreshToken)
    else localStorage.removeItem('refresh_token')
    window.dispatchEvent(new Event('valeo-auth-changed'))
  }

  async refreshAccessToken(): Promise<boolean> {
    if (!this.refreshToken) return false
    if (this.refreshPending) return this.refreshPending
    const token = this.refreshToken, generation = this.generation
    this.refreshPending = (async () => {
      try {
        const metadata = await this.discovery()
        const response = await fetch(metadata.token_endpoint, { method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ grant_type: 'refresh_token', refresh_token: token, client_id: this.settings.oidc.clientId }) })
        if (!response.ok) throw new Error('Token refresh failed')
        const tokens = await response.json()
        if (generation !== this.generation) return false
        this.setTokens(tokens.access_token, tokens.refresh_token)
        return true
      } catch {
        if (generation === this.generation) this.clearTokens()
        return false
      } finally { this.refreshPending = null }
    })()
    return this.refreshPending
  }

  async logout(): Promise<void> {
    const token = this.accessToken, refresh = this.refreshToken
    this.clearTokens()
    const results = await Promise.allSettled([
      token ? fetch('/api/v1/identity/session/logout', { method: 'POST', keepalive: true,
        headers: { Authorization: `Bearer ${token}` } }).then(response => {
        if (!response.ok && response.status !== 401) throw new Error('Session revocation failed')
      }) : Promise.resolve(),
      refresh ? this.discovery().then(metadata => {
        if (!metadata.revocation_endpoint) throw new Error('Provider revocation unavailable')
        return fetch(metadata.revocation_endpoint, { method: 'POST', keepalive: true,
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({ token: refresh, token_type_hint: 'refresh_token', client_id: this.settings.oidc.clientId }) })
      }).then(response => { if (!response.ok) throw new Error('Provider revocation failed') }) : Promise.resolve(),
    ])
    if (results.some(result => result.status === 'rejected')) throw new Error('Lokal abgemeldet; der vollstaendige Widerruf konnte nicht bestaetigt werden.')
  }

  clearTokens(): void {
    this.generation += 1
    this.accessToken = this.refreshToken = null
    this.user = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    window.dispatchEvent(new Event('valeo-auth-changed'))
  }

  private decodeUser(token: string): User {
    const claims = jwtDecode<User & { scope?: string; erp_scopes?: string[]; realm_access?: { roles?: string[] } }>(token)
    if (typeof claims.sub !== 'string' || !claims.sub || typeof claims.exp !== 'number'
      || !Number.isFinite(claims.exp) || claims.exp * 1000 <= Date.now()) throw new Error('Ungueltiges Zugriffstoken.')
    const names = claims as User & { preferred_username?: string }
    return { ...claims, name: names.name || names.preferred_username || claims.sub, email: typeof claims.email === 'string' ? claims.email : '', roles: strings(claims.roles ?? claims.realm_access?.roles),
      scopes: [...new Set([...strings(claims.scopes), ...(typeof claims.scope === 'string' ? claims.scope.split(' ').filter(Boolean) : []), ...strings(claims.erp_scopes)])] }
  }
  getUser(): User | null { return this.isAuthenticated() ? this.user : null }
  getAccessToken(): string | null { return this.isAuthenticated() ? this.accessToken : null }
  isAuthenticated(): boolean { return this.accessToken !== null && this.user !== null && this.user.exp * 1000 > Date.now() }
  hasScope(scope: string): boolean { const user = this.getUser(); return Boolean(user && (user.scopes.includes(scope) || user.scopes.includes('admin:all'))) }
  hasRole(role: string): boolean { const user = this.getUser(); return Boolean(user && (user.roles.includes(role) || user.roles.includes('admin'))) }
}
export const auth = new AuthService()
export function getAccessToken(): string | null { return auth.getAccessToken() }
export function clearAuthSession(): void { auth.clearTokens() }
export function handleUnauthorized(): void { auth.clearTokens(); window.location.assign('/login') }
