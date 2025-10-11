import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Loader2, XCircle } from 'lucide-react'

const isNonEmptyString = (value: unknown): value is string => {
  return typeof value === 'string' && value.trim().length > 0
}

const LOGIN_PATH = '/login'

export default function CallbackPage(): JSX.Element {
  const [searchParams] = useSearchParams()
  const { handleCallback } = useAuth()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const processCallback = async (): Promise<void> => {
      const codeParam = searchParams.get('code')
      const stateParam = searchParams.get('state')
      const errorParam = searchParams.get('error')

      if (isNonEmptyString(errorParam)) {
        setError(`Authentication failed: ${errorParam}`)
        return
      }

      const code = isNonEmptyString(codeParam) ? codeParam : null
      const state = isNonEmptyString(stateParam) ? stateParam : null

      if (code == null || state == null) {
        setError('Missing code or state parameter')
        return
      }

      try {
        await handleCallback(code, state)
      } catch (callbackError) {
        setError(callbackError instanceof Error ? callbackError.message : 'Authentication failed')
      }
    }

    void processCallback()
  }, [handleCallback, searchParams])

  if (error != null) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md border-red-200">
          <CardHeader>
            <div className="flex items-center gap-3">
              <XCircle className="h-8 w-8 text-red-600" />
              <CardTitle className="text-red-900">Anmeldung fehlgeschlagen</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-red-600">{error}</p>
            <div className="mt-4">
              <a href={LOGIN_PATH} className="text-sm text-blue-600 hover:underline">
                Zurueck zur Anmeldung
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
            <p className="text-gray-600">Anmeldung wird abgeschlossen...</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
