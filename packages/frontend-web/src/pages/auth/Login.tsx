import { useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-react'

const DASHBOARD_PATH = '/dashboard'

export default function LoginPage(): JSX.Element {
  const { login, loading, isAuthenticated } = useAuth()

  useEffect(() => {
    if (isAuthenticated) {
      window.location.href = DASHBOARD_PATH
    }
  }, [isAuthenticated])

  const handleLogin = async (): Promise<void> => {
    try {
      await login()
    } catch (error) {
      console.error('Login failed:', error)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">VALEO NeuroERP</CardTitle>
          <CardDescription>Melden Sie sich mit Ihrem Unternehmens-Account an.</CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <Button onClick={() => { void handleLogin() }} disabled={loading} className="w-full" size="lg">
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
            <p>Sichere Anmeldung ueber Ihren Identity-Provider.</p>
            <p className="mt-2 text-xs">Unterstuetzt: Azure AD, Keycloak, Okta, Auth0.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
