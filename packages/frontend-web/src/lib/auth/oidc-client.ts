/**
 * OIDC Client for VALEO NeuroERP
 * Handles authentication with Keycloak/Azure AD/Auth0
 */

import { UserManager, User, WebStorageStateStore } from 'oidc-client-ts'

const OIDC_CONFIG = {
  authority: import.meta.env.VITE_OIDC_DISCOVERY_URL?.replace('/.well-known/openid-configuration', '') || 'http://localhost:8080/realms/valeo-neuro-erp',
  client_id: import.meta.env.VITE_OIDC_CLIENT_ID || 'valeo-neuro-erp-frontend',
  redirect_uri: import.meta.env.VITE_OIDC_REDIRECT_URI || `${window.location.origin}/auth/callback`,
  post_logout_redirect_uri: window.location.origin,
  response_type: 'code',
  scope: 'openid profile email roles',
  userStore: new WebStorageStateStore({ store: window.localStorage }),
  automaticSilentRenew: true,
  silent_redirect_uri: `${window.location.origin}/auth/silent-callback.html`,
  loadUserInfo: true,
  monitorSession: true,
}

const userManager = new UserManager(OIDC_CONFIG)

// Event handlers
userManager.events.addUserLoaded((user: User) => {
  console.log('✅ User loaded:', user.profile.email)
})

userManager.events.addUserUnloaded(() => {
  console.log('👋 User logged out')
})

userManager.events.addAccessTokenExpiring(() => {
  console.log('⏰ Access token expiring, renewing...')
})

userManager.events.addAccessTokenExpired(() => {
  console.log('⚠️ Access token expired')
  // Auto-logout on token expiry
  userManager.signoutRedirect()
})

userManager.events.addSilentRenewError((error) => {
  console.error('❌ Silent renew error:', error)
})

export class OIDCClient {
  private userManager: UserManager

  constructor() {
    this.userManager = userManager
  }

  /**
   * Initiate login flow (redirects to IdP)
   */
  async login(): Promise<void> {
    await this.userManager.signinRedirect()
  }

  /**
   * Handle callback from IdP after login
   */
  async handleCallback(): Promise<User> {
    const user = await this.userManager.signinRedirectCallback()
    return user
  }

  /**
   * Get current user
   */
  async getUser(): Promise<User | null> {
    return await this.userManager.getUser()
  }

  /**
   * Check if user is logged in
   */
  async isAuthenticated(): Promise<boolean> {
    const user = await this.getUser()
    return user !== null && !user.expired
  }

  /**
   * Get access token for API calls
   */
  async getAccessToken(): Promise<string | null> {
    const user = await this.getUser()
    return user?.access_token ?? null
  }

  /**
   * Get user roles from token claims
   */
  async getUserRoles(): Promise<string[]> {
    const user = await this.getUser()
    if (!user) return []

    // Try different claim locations
    const profile = user.profile as any
    const roles = 
      profile.roles || 
      profile.realm_access?.roles ||
      profile['https://valeo-erp.com/roles'] ||
      []

    return Array.isArray(roles) ? roles : [roles]
  }

  /**
   * Check if user has a specific role
   */
  async hasRole(role: string): Promise<boolean> {
    const roles = await this.getUserRoles()
    return roles.includes(role)
  }

  /**
   * Get tenant ID from token claims
   */
  async getTenantId(): Promise<string | null> {
    const user = await this.getUser()
    if (!user) return null

    const profile = user.profile as any
    return profile.tenant_id || profile.tid || 'system'
  }

  /**
   * Logout
   */
  async logout(): Promise<void> {
    await this.userManager.signoutRedirect()
  }

  /**
   * Silent renew (refresh token in background)
   */
  async renewToken(): Promise<User> {
    const user = await this.userManager.signinSilent()
    if (!user) throw new Error('Failed to renew token')
    return user
  }

  /**
   * Remove user session
   */
  async removeUser(): Promise<void> {
    await this.userManager.removeUser()
  }
}

// Singleton instance
export const oidcClient = new OIDCClient()

// Helper hook for React
export function useAuth() {
  const [user, setUser] = React.useState<User | null>(null)
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    oidcClient.getUser().then((user) => {
      setUser(user)
      setLoading(false)
    })

    const onUserLoaded = (user: User) => setUser(user)
    const onUserUnloaded = () => setUser(null)

    userManager.events.addUserLoaded(onUserLoaded)
    userManager.events.addUserUnloaded(onUserUnloaded)

    return () => {
      userManager.events.removeUserLoaded(onUserLoaded)
      userManager.events.removeUserUnloaded(onUserUnloaded)
    }
  }, [])

  return {
    user,
    loading,
    isAuthenticated: user !== null && !user.expired,
    login: () => oidcClient.login(),
    logout: () => oidcClient.logout(),
    getAccessToken: () => oidcClient.getAccessToken(),
    hasRole: (role: string) => oidcClient.hasRole(role),
  }
}

// Import React for hook
import React from 'react'

