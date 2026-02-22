import { useEffect, useRef, useState } from 'react'
import { type User, auth } from '@/lib/auth'

interface AuthHook {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: () => Promise<void>
  logout: () => void
  handleCallback: (_code: string, _state: string) => Promise<void>
  hasScope: (_scope: string) => boolean
  hasRole: (_role: string) => boolean
}

const DASHBOARD_PATH = '/'
const LOGIN_PATH = '/login'

const safeRedirect = (target: string): void => {
  window.location.href = target
}

export function useAuth(): AuthHook {
  const [user, setUser] = useState<User | null>(auth.getUser())
  const [loading, setLoading] = useState<boolean>(false)
  const isMountedRef = useRef(true)

  useEffect(() => {
    setUser(auth.getUser())
    return () => {
      isMountedRef.current = false
    }
  }, [])

  const setSafeUser = (next: User | null): void => {
    if (isMountedRef.current) {
      setUser(next)
    }
  }

  const setSafeLoading = (next: boolean): void => {
    if (isMountedRef.current) {
      setLoading(next)
    }
  }

  const login = async (): Promise<void> => {
    setSafeLoading(true)
    try {
      await auth.login()
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    } finally {
      setSafeLoading(false)
    }
  }

  const logout = (): void => {
    setSafeLoading(false)
    // Check if OIDC is actually configured (not just placeholder)
    const discoveryUrl = (import.meta.env.VITE_OIDC_DISCOVERY_URL ?? '')
    const placeholderPatterns = ['your-oidc-provider.com', 'example.com', 'keycloak.example.com', '{tenant-id}', '{domain}', '{application-id}', '{client-id}']
    const oidcConfigured = discoveryUrl.length > 0 && !placeholderPatterns.some(pattern => discoveryUrl.includes(pattern))
    auth.logout()
    setSafeUser(null)
    // Only redirect to login if OIDC is configured
    if (oidcConfigured) {
      safeRedirect(LOGIN_PATH)
    }
  }

  const handleCallback = async (_code: string, _state: string): Promise<void> => {
    setSafeLoading(true)
    try {
      await auth.handleCallback(_code, _state)
      setSafeUser(auth.getUser())
      safeRedirect(DASHBOARD_PATH)
    } catch (error) {
      console.error('Callback failed:', error)
      throw error
    } finally {
      setSafeLoading(false)
    }
  }

  return {
    user,
    loading,
    isAuthenticated: auth.isAuthenticated(),
    login,
    logout,
    handleCallback,
    hasScope: (_scope: string): boolean => auth.hasScope(_scope),
    hasRole: (_role: string): boolean => auth.hasRole(_role),
  }
}
