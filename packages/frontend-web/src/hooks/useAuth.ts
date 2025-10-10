/**
 * useAuth Hook
 * React-Hook für Authentication
 */

import { useState, useEffect } from 'react'
import { auth, type User } from '@/lib/auth'

export function useAuth() {
  const [user, setUser] = useState<User | null>(auth.getUser())
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    // Check auth status on mount
    setUser(auth.getUser())
  }, [])

  const login = async () => {
    setLoading(true)
    try {
      await auth.login()
      // Will redirect to OIDC provider
    } catch (e) {
      console.error('Login failed:', e)
      setLoading(false)
    }
  }

  const logout = () => {
    auth.logout()
    setUser(null)
    // Redirect to login page
    window.location.href = '/login'
  }

  const handleCallback = async (code: string, state: string) => {
    setLoading(true)
    try {
      await auth.handleCallback(code, state)
      setUser(auth.getUser())
      // Redirect to dashboard
      window.location.href = '/dashboard'
    } catch (e) {
      console.error('Callback failed:', e)
      setLoading(false)
      throw e
    }
  }

  return {
    user,
    loading,
    isAuthenticated: auth.isAuthenticated(),
    login,
    logout,
    handleCallback,
    hasScope: (scope: string) => auth.hasScope(scope),
    hasRole: (role: string) => auth.hasRole(role),
  }
}

