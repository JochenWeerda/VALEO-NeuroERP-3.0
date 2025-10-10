/**
 * OIDC Callback Page
 * Handles redirect from OIDC provider
 */

import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Loader2, XCircle } from 'lucide-react'

export default function CallbackPage() {
  const [searchParams] = useSearchParams()
  const { handleCallback } = useAuth()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const processCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const errorParam = searchParams.get('error')

      // Check for error from OIDC provider
      if (errorParam) {
        setError(`Authentication failed: ${errorParam}`)
        return
      }

      // Validate parameters
      if (!code || !state) {
        setError('Missing code or state parameter')
        return
      }

      try {
        await handleCallback(code, state)
        // Will redirect to dashboard
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Authentication failed')
      }
    }

    processCallback()
  }, [searchParams, handleCallback])

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
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
              <a href="/login" className="text-sm text-blue-600 hover:underline">
                Zurück zur Anmeldung
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
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

