import { useEffect, useRef, useState } from 'react'
import { type User, auth } from '@/lib/auth'
import { toast } from 'sonner'

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
  const [loading, setLoading] = useState<boolean>(() => !auth.isAuthenticated() && auth.canRefresh())
  const isMountedRef = useRef(true)

  useEffect(() => {
    isMountedRef.current = true
    const sync = (): void => setUser(auth.getUser())
    sync()
    window.addEventListener('valeo-auth-changed', sync)
    let active = true
    if (!auth.isAuthenticated() && auth.canRefresh()) {
      setLoading(true)
      void auth.getFreshAccessToken().finally(() => {
        if (active) {
          sync()
          setLoading(false)
        }
      })
    }
    return () => {
      active = false
      window.removeEventListener('valeo-auth-changed', sync)
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
    setSafeUser(null)
    void auth.logout().catch(() => {
      toast.error('Lokal abgemeldet. Der vollstaendige Widerruf konnte nicht bestaetigt werden.', { id: 'session-revocation' })
    }).finally(() => safeRedirect(LOGIN_PATH))
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
