import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { CheckCircle2, XCircle, Loader2, FileText, ShieldCheck } from 'lucide-react'
import { toast } from '@/hooks/use-toast'

// API Client
const apiClient = createApiClient('/api/crm-gdpr')

export default function GDPRRequestPublicPage(): JSX.Element {
  const { t } = useTranslation()
  const [step, setStep] = useState<'request' | 'status' | 'download'>('request')
  const [loading, setLoading] = useState(false)
  const [requestId, setRequestId] = useState<string>('')
  const [statusData, setStatusData] = useState<any>(null)
  
  const [formData, setFormData] = useState({
    contact_id: '',
    request_type: '',
    email: '',
    notes: '',
  })

  const handleSubmitRequest = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const response = await apiClient.post('/gdpr/requests', {
        tenant_id: '00000000-0000-0000-0000-000000000001', // TODO: Get from context
        request_type: formData.request_type,
        contact_id: formData.contact_id,
        requested_by: formData.email,
        is_self_request: true,
        notes: formData.notes,
      })

      if (response.success) {
        setRequestId(response.data.id)
        toast({
          title: t('crud.messages.requestCreated'),
          description: t('crud.gdpr.verificationEmailSent'),
        })
        setStep('status')
      } else {
        throw new Error(response.error || 'Request failed')
      }
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.requestError'),
        description: error.message,
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCheckStatus = async () => {
    if (!requestId) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.requestIdRequired'),
      })
      return
    }

    setLoading(true)
    try {
      const response = await apiClient.get(`/gdpr/requests/${requestId}`)
      if (response.success) {
        setStatusData(response.data)
        if (response.data.status === 'completed' && response.data.response_file_path) {
          setStep('download')
        }
      } else {
        throw new Error('Request not found')
      }
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.requestNotFound'),
      })
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    if (!requestId) return

    try {
      const response = await fetch(`/api/crm-gdpr/gdpr/requests/${requestId}/download`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `gdpr-export-${requestId}.${statusData?.response_file_format || 'json'}`
        link.click()
        window.URL.revokeObjectURL(url)
        toast({
          title: t('crud.messages.downloadStarted'),
        })
      } else {
        throw new Error('Download failed')
      }
    } catch (error) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.downloadError'),
      })
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <div className="flex items-center gap-2 mb-2">
            <ShieldCheck className="h-6 w-6 text-primary" />
            <CardTitle>{t('crud.gdpr.publicTitle')}</CardTitle>
          </div>
          <CardDescription>{t('crud.gdpr.publicDescription')}</CardDescription>
        </CardHeader>
        <CardContent>
          {step === 'request' && (
            <form onSubmit={handleSubmitRequest} className="space-y-4">
              <div>
                <Label htmlFor="contact_id">{t('crud.fields.contactId')} *</Label>
                <Input
                  id="contact_id"
                  type="text"
                  value={formData.contact_id}
                  onChange={(e) => setFormData({ ...formData, contact_id: e.target.value })}
                  required
                  placeholder={t('crud.tooltips.placeholders.contactId')}
                />
              </div>

              <div>
                <Label htmlFor="email">{t('crud.fields.email')} *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  placeholder={t('crud.tooltips.placeholders.email')}
                />
              </div>

              <div>
                <Label htmlFor="request_type">{t('crud.fields.requestType')} *</Label>
                <Select
                  value={formData.request_type}
                  onValueChange={(value) => setFormData({ ...formData, request_type: value })}
                  required
                >
                  <SelectTrigger>
                    <SelectValue placeholder={t('crud.tooltips.placeholders.selectRequestType')} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="access">{t('crud.gdpr.requestTypes.access')}</SelectItem>
                    <SelectItem value="deletion">{t('crud.gdpr.requestTypes.deletion')}</SelectItem>
                    <SelectItem value="portability">{t('crud.gdpr.requestTypes.portability')}</SelectItem>
                    <SelectItem value="objection">{t('crud.gdpr.requestTypes.objection')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="notes">{t('crud.fields.notes')}</Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  placeholder={t('crud.tooltips.placeholders.optionalNotes')}
                  rows={4}
                />
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    {t('crud.messages.processing')}
                  </>
                ) : (
                  t('crud.actions.submit')
                )}
              </Button>
            </form>
          )}

          {step === 'status' && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="request_id">{t('crud.fields.requestId')}</Label>
                <div className="flex gap-2">
                  <Input
                    id="request_id"
                    value={requestId}
                    onChange={(e) => setRequestId(e.target.value)}
                    placeholder={t('crud.tooltips.placeholders.requestId')}
                  />
                  <Button onClick={handleCheckStatus} disabled={loading}>
                    {loading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      t('crud.actions.checkStatus')
                    )}
                  </Button>
                </div>
              </div>

              {statusData && (
                <Alert className={statusData.status === 'completed' ? 'border-green-500 bg-green-50' : ''}>
                  {statusData.status === 'completed' ? (
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5" />
                  )}
                  <AlertDescription>
                    <div className="font-medium mb-2">{t('crud.fields.status')}: {t(`status.${statusData.status}`)}</div>
                    {statusData.status === 'completed' && statusData.response_file_path && (
                      <Button onClick={handleDownload} className="mt-2">
                        <FileText className="h-4 w-4 mr-2" />
                        {t('crud.actions.downloadExport')}
                      </Button>
                    )}
                  </AlertDescription>
                </Alert>
              )}

              <Button variant="outline" onClick={() => setStep('request')} className="w-full">
                {t('crud.actions.back')}
              </Button>
            </div>
          )}

          {step === 'download' && statusData && (
            <div className="space-y-4">
              <Alert className="border-green-500 bg-green-50">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <AlertDescription>
                  <div className="font-medium mb-2">{t('crud.messages.exportReady')}</div>
                  <Button onClick={handleDownload} className="mt-2">
                    <FileText className="h-4 w-4 mr-2" />
                    {t('crud.actions.downloadExport')}
                  </Button>
                </AlertDescription>
              </Alert>

              <Button variant="outline" onClick={() => setStep('request')} className="w-full">
                {t('crud.actions.newRequest')}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

