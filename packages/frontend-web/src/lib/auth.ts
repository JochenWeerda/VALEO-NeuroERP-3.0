/**
 * Authentication Library
 * OIDC/OAuth2 Flow für Production
 */

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
  oidc: {
    discoveryUrl: string
    clientId: string
    redirectUri: string
    scopes: string[]
  }
}

// Auth-Config aus ENV
const config: AuthConfig = {
  oidc: {
    discoveryUrl: import.meta.env.VITE_OIDC_DISCOVERY_URL ?? '',
    clientId: import.meta.env.VITE_OIDC_CLIENT_ID ?? '',
    redirectUri: import.meta.env.VITE_OIDC_REDIRECT_URI ?? `${window.location.origin}/callback`,
    scopes: ['openid', 'profile', 'email', 'offline_access'],
  },
}

const RANDOM_STRING_LENGTH = 32

class AuthService {
  private accessToken: string | null = null
  private refreshToken: string | null = null
  private user: User | null = null

  constructor() {
    // Load from localStorage
    this.accessToken = localStorage.getItem('access_token')
    this.refreshToken = localStorage.getItem('refresh_token')
    
    if (this.accessToken != null) {
      try {
        this.user = jwtDecode<User>(this.accessToken)
        
        // Check if expired
        if (this.user.exp * 1000 < Date.now()) {
          this.logout()
        }
      } catch (e) {
        this.logout()
      }
    }
  }

  /**
   * Startet OIDC-Login-Flow
   */
  async login(): Promise<void> {
    if (config.oidc.discoveryUrl.length === 0) {
      throw new Error('OIDC not configured. Set VITE_OIDC_DISCOVERY_URL')
    }

    // Fetch OIDC discovery document
    const discoveryResponse = await fetch(config.oidc.discoveryUrl)
    const discovery = await discoveryResponse.json()

    // Generate state & nonce
    const state = this.generateRandomString(RANDOM_STRING_LENGTH)
    const nonce = this.generateRandomString(RANDOM_STRING_LENGTH)

    sessionStorage.setItem('auth_state', state)
    sessionStorage.setItem('auth_nonce', nonce)

    // Build authorization URL
    const params = new URLSearchParams({
      client_id: config.oidc.clientId,
      redirect_uri: config.oidc.redirectUri,
      response_type: 'code',
      scope: config.oidc.scopes.join(' '),
      state,
      nonce,
    })

    const authUrl = `${discovery.authorization_endpoint}?${params.toString()}`

    // Redirect to OIDC provider
    window.location.href = authUrl
  }

  /**
   * Callback-Handler nach OIDC-Redirect
   */
  async handleCallback(code: string, state: string): Promise<void> {
    // Verify state
    const savedState = sessionStorage.getItem('auth_state')
    if (state !== savedState) {
      throw new Error('Invalid state parameter')
    }

    // Exchange code for tokens
    const discoveryResponse = await fetch(config.oidc.discoveryUrl)
    const discovery = await discoveryResponse.json()

    const tokenResponse = await fetch(discovery.token_endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code,
        redirect_uri: config.oidc.redirectUri,
        client_id: config.oidc.clientId,
      }),
    })

    if (!tokenResponse.ok) {
      throw new Error('Token exchange failed')
    }

    const tokens = await tokenResponse.json()

    // Save tokens
    this.setTokens(tokens.access_token, tokens.refresh_token)

    // Clear session storage
    sessionStorage.removeItem('auth_state')
    sessionStorage.removeItem('auth_nonce')
  }

  /**
   * Speichert Tokens und decoded User
   */
  private setTokens(accessToken: string, refreshToken?: string): void {
    this.accessToken = accessToken
    this.refreshToken = refreshToken ?? null

    localStorage.setItem('access_token', accessToken)
    if (typeof refreshToken === 'string') {
      localStorage.setItem('refresh_token', refreshToken)
    }

    // Decode JWT
    try {
      this.user = jwtDecode<User>(accessToken)
    } catch (e) {
      console.error('Failed to decode JWT:', e)
      this.logout()
    }
  }

  /**
   * Refresh Access-Token mit Refresh-Token
   */
  async refreshAccessToken(): Promise<boolean> {
    if (this.refreshToken == null) {
      return false
    }

    try {
      const discoveryResponse = await fetch(config.oidc.discoveryUrl)
      const discovery = await discoveryResponse.json()

      const tokenResponse = await fetch(discovery.token_endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'refresh_token',
          refresh_token: this.refreshToken,
          client_id: config.oidc.clientId,
        }),
      })

      if (!tokenResponse.ok) {
        return false
      }

      const tokens = await tokenResponse.json()
      this.setTokens(tokens.access_token, tokens.refresh_token)

      return true
    } catch (e) {
      console.error('Token refresh failed:', e)
      return false
    }
  }

  /**
   * Logout (lokale Tokens löschen)
   */
  clearTokens(): void {
    this.logout()
  }

  /**
   * Logout (alias)
   */
  logout(): void {
    this.accessToken = null
    this.refreshToken = null
    this.user = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')

    // Optional: OIDC-Logout
    // window.location.href = `${discovery.end_session_endpoint}?...`
  }

  /**
   * Gibt aktuellen User zurück
   */
  getUser(): User | null {
    return this.user
  }

  /**
   * Gibt Access-Token zurück
   */
  getAccessToken(): string | null {
    return this.accessToken
  }

  /**
   * Prüft ob User authenticated ist
   */
  isAuthenticated(): boolean {
    return this.accessToken !== null && this.user !== null
  }

  /**
   * Prüft ob User bestimmte Scope hat
   */
  hasScope(scope: string): boolean {
    return (this.user?.scopes?.includes(scope)) ?? false
  }

  /**
   * Prüft ob User bestimmte Rolle hat
   */
  hasRole(role: string): boolean {
    const hasRole = (this.user?.roles?.includes(role)) ?? false
    const hasAdminScope = (this.user?.scopes?.includes('admin:all')) ?? false
    return hasRole || hasAdminScope
  }

  /**
   * Helper: Generate random string
   */
  private generateRandomString(length: number): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let result = ''
    const randomArray = new Uint8Array(length)
    crypto.getRandomValues(randomArray)
    
    for (let i = 0; i < length; i++) {
      result += chars[randomArray[i] % chars.length]
    }
    
    return result
  }
}

// Singleton
export const auth = new AuthService()

export function getAccessToken(): string | null {
  return auth.getAccessToken()
}

export function clearAuthSession(): void {
  auth.logout()
}

export function handleUnauthorized(): void {
  auth.logout()
  if (typeof window !== 'undefined') {
    window.location.assign('/login')
  }
}
