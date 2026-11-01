import { useEffect, useMemo, useRef, useState } from 'react'
import { useSearchParams } from '@/app/routing/typed-router'
import { useAuth } from '@/hooks/useAuth'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { useUniversalMaskRuntime } from '@/components/mask-builder/runtime/useUniversalMaskRuntime'
import { callbackScreen } from '@/masks/public-auth.generated'

const isNonEmptyString = (value: unknown): value is string => typeof value === 'string' && value.trim().length > 0

export default function CallbackPage(): JSX.Element {
  const [searchParams] = useSearchParams()
  const { handleCallback } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const started = useRef(false)
  const schema = useMemo(() => ({ ...callbackScreen, title: error ? 'Anmeldung fehlgeschlagen' : callbackScreen.title,
    subtitle: error ? 'Der Anmeldevorgang wurde nicht abgeschlossen.' : callbackScreen.subtitle }), [error])
  const runtime = useUniversalMaskRuntime({ screenId: 'auth/callback', schema })
  useEffect(() => {
    // PKCE/state consumption remains single-use under StrictMode and rerenders.
    if (started.current) return
    started.current = true
    async function finish(): Promise<void> {
      const code = searchParams.get('code'), state = searchParams.get('state'), providerError = searchParams.get('error')
      if (isNonEmptyString(providerError)) { setError(`Authentication failed: ${providerError}`); return }
      if (!isNonEmptyString(code) || !isNonEmptyString(state)) { setError('Missing code or state parameter'); return }
      try { await handleCallback(code, state) } catch (failure) {
        setError(failure instanceof Error ? failure.message : 'Authentication failed')
      }
    }
    void finish()
  }, [handleCallback, searchParams])
  return <main className="mx-auto max-w-2xl" data-testid="auth-callback">
    <UniversalMaskRenderer plan={runtime.plan} data={{ hasError: error !== null }}
      screenContext={{data: {hasError: error !== null}, permissions: {granted: []},
        state: {values: {}, policies: {}}, actions: {}, navigation: {push: route => { window.location.href = route }} }}
      messages={error ? [{ key: 'callback', severity: 'error', message: error }]
        : [{ key: 'callback', severity: 'info', message: 'Anmeldung wird abgeschlossen...' }]}
      onAction={key => { if (key === 'back' && error) window.location.href = '/login' }} />
  </main>
}
