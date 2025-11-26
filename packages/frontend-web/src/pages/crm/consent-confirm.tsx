import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react'

// API Client
const apiClient = createApiClient('/api/crm-consent')

export default function ConsentConfirmPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState<string>('')

  const consentId = searchParams.get('id')
  const token = searchParams.get('token')

  useEffect(() => {
    const confirmConsent = async () => {
      if (!consentId || !token) {
        setStatus('error')
        setMessage(t('crud.messages.invalidConfirmationLink'))
        return
      }

      try {
        const response = await apiClient.post(`/consents/${consentId}/confirm`, null, {
          params: { token }
        })

        if (response.success) {
          setStatus('success')
          setMessage(t('crud.messages.consentConfirmed'))
        } else {
          setStatus('error')
          setMessage(response.error || t('crud.messages.consentConfirmError'))
        }
      } catch (error: any) {
        setStatus('error')
        setMessage(error.message || t('crud.messages.consentConfirmError'))
      }
    }

    confirmConsent()
  }, [consentId, token, t])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">
            {t('crud.consent.confirmationTitle')}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {status === 'loading' && (
            <div className="flex flex-col items-center justify-center py-8">
              <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
              <p className="text-muted-foreground">{t('crud.messages.processing')}</p>
            </div>
          )}

          {status === 'success' && (
            <Alert className="border-green-500 bg-green-50">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              <AlertDescription className="text-green-800">
                {message}
              </AlertDescription>
            </Alert>
          )}

          {status === 'error' && (
            <Alert variant="destructive">
              <XCircle className="h-5 w-5" />
              <AlertDescription>
                {message}
              </AlertDescription>
            </Alert>
          )}

          {status !== 'loading' && (
            <div className="flex justify-center">
              <Button onClick={() => navigate('/')}>
                {t('crud.actions.close')}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

