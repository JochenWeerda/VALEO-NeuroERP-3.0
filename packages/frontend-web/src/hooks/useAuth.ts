import { useEffect, useRef, useState } from 'react'
import { type User, auth } from '@/lib/auth'

interface AuthHook {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: () => Promise<void>
  logout: () => void
  handleCallback: (code: string, state: string) => Promise<void>
  hasScope: (scope: string) => boolean
  hasRole: (role: string) => boolean
}

const DASHBOARD_PATH = '/dashboard'
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
    auth.logout()
    setSafeUser(null)
    safeRedirect(LOGIN_PATH)
  }

  const handleCallback = async (code: string, state: string): Promise<void> => {
    setSafeLoading(true)
    try {
      await auth.handleCallback(code, state)
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
    hasScope: (scope: string): boolean => auth.hasScope(scope),
    hasRole: (role: string): boolean => auth.hasRole(role),
  }
}
