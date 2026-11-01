import { useEffect, useMemo, useRef, useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { toast } from '@/hooks/use-toast'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { useUniversalMaskRuntime } from '@/components/mask-builder/runtime/useUniversalMaskRuntime'
import { loginScreen } from '@/masks/public-auth.generated'

export default function LoginPage(): JSX.Element {
  const { login, loading, isAuthenticated } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [redirecting, setRedirecting] = useState(false)
  const pending = useRef(false)
  const busy = loading || redirecting || isAuthenticated
  const schema = useMemo(() => ({ ...loginScreen, actions: loginScreen.actions.map(action => ({ ...action,
    label: busy ? 'Weiterleitung...' : action.label, disabled: busy })) }), [busy])
  const runtime = useUniversalMaskRuntime({ screenId: 'auth/login', schema })
  useEffect(() => { if (isAuthenticated) window.location.href = '/' }, [isAuthenticated])
  async function handleLogin(): Promise<void> {
    if (busy || pending.current) return
    pending.current = true
    setError(null)
    setRedirecting(true)
    try { await login() } catch (failure) {
      const message = failure instanceof Error ? failure.message : 'OIDC-Redirect konnte nicht gestartet werden.'
      setError(message)
      toast({ variant: 'destructive', title: 'Anmeldung fehlgeschlagen', description: message })
      setRedirecting(false)
      pending.current = false
    }
  }
  return <main className="mx-auto max-w-2xl" data-testid="auth-login">
    <UniversalMaskRenderer plan={runtime.plan} messages={error ? [{ key: 'login', severity: 'error', message: error }] : []}
      onAction={key => { if (key === 'login') void handleLogin() }} />
  </main>
}
