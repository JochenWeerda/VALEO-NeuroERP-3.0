/**
 * Login Page
 * OIDC/OAuth2 Login-Flow (Production)
 */

import { useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-react'

export default function LoginPage() {
  const { login, loading, isAuthenticated } = useAuth()

  useEffect(() => {
    // Redirect if already authenticated
    if (isAuthenticated) {
      window.location.href = '/dashboard'
    }
  }, [isAuthenticated])

  const handleLogin = async () => {
    try {
      await login()
      // Will redirect to OIDC provider
    } catch (e) {
      console.error('Login failed:', e)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">VALEO NeuroERP</CardTitle>
          <CardDescription>
            Melden Sie sich mit Ihrem Unternehmens-Account an
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <Button
            onClick={handleLogin}
            disabled={loading}
            className="w-full"
            size="lg"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Weiterleitung...
              </>
            ) : (
              'Mit SSO anmelden'
            )}
          </Button>

          <div className="text-center text-sm text-muted-foreground">
            <p>
              Sichere Anmeldung über Ihren Identity-Provider
            </p>
            <p className="mt-2 text-xs">
              Unterstützt: Azure AD, Keycloak, Okta, Auth0
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

