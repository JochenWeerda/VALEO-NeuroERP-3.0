import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, ArrowRight, Check, Mail, Users, Calendar, BarChart3, Settings } from 'lucide-react'
import { createApiClient } from '@/components/mask-builder/utils/api'
import { toast } from '@/hooks/use-toast'
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers'

// API Client
const apiClient = createApiClient('/api/crm-marketing')

type CampaignBuilderStep = 'type' | 'template' | 'segment' | 'abtest' | 'schedule' | 'review'

interface CampaignData {
  name: string
  description: string
  type: string
  template_id: string | null
  segment_id: string | null
  sender_name: string
  sender_email: string
  subject: string
  scheduled_at: string
  budget: number | null
  enable_abtest: boolean
  abtest_variants: Array<{
    name: string
    subject: string
    percentage: number
  }>
}

export default function CampaignBuilderPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [currentStep, setCurrentStep] = useState<CampaignBuilderStep>('type')
  const [loading, setLoading] = useState(false)
  const [campaignData, setCampaignData] = useState<CampaignData>({
    name: '',
    description: '',
    type: 'email',
    template_id: null,
    segment_id: null,
    sender_name: '',
    sender_email: '',
    subject: '',
    scheduled_at: '',
    budget: null,
    enable_abtest: false,
    abtest_variants: [
      { name: 'A', subject: '', percentage: 50 },
      { name: 'B', subject: '', percentage: 50 }
    ]
  })
  const [templates, setTemplates] = useState<any[]>([])
  const [segments, setSegments] = useState<any[]>([])

  const steps: Array<{ key: CampaignBuilderStep; label: string; icon: any }> = [
    { key: 'type', label: t('crud.campaigns.builder.steps.type'), icon: Settings },
    { key: 'template', label: t('crud.campaigns.builder.steps.template'), icon: Mail },
    { key: 'segment', label: t('crud.campaigns.builder.steps.segment'), icon: Users },
    { key: 'abtest', label: t('crud.campaigns.builder.steps.abtest'), icon: BarChart3 },
    { key: 'schedule', label: t('crud.campaigns.builder.steps.schedule'), icon: Calendar },
    { key: 'review', label: t('crud.campaigns.builder.steps.review'), icon: Check }
  ]

  const currentStepIndex = steps.findIndex(s => s.key === currentStep)
  const isFirstStep = currentStepIndex === 0
  const isLastStep = currentStepIndex === steps.length - 1

  // Load templates and segments
  useEffect(() => {
    const loadData = async () => {
      try {
        const [templatesRes, segmentsRes] = await Promise.all([
          apiClient.get('/campaigns/templates', {
            params: { tenant_id: '00000000-0000-0000-0000-000000000001' }
          }),
          apiClient.get('/segments', {
            params: { tenant_id: '00000000-0000-0000-0000-000000000001' }
          })
        ])
        
        if (templatesRes.success || Array.isArray(templatesRes)) {
          setTemplates(Array.isArray(templatesRes) ? templatesRes : (templatesRes.data || []))
        }
        if (segmentsRes.success || Array.isArray(segmentsRes)) {
          setSegments(Array.isArray(segmentsRes) ? segmentsRes : (segmentsRes.data || []))
        }
      } catch (error) {
        console.error('Fehler beim Laden der Daten:', error)
      }
    }
    loadData()
  })

  const updateField = (field: keyof CampaignData, value: any) => {
    setCampaignData(prev => ({ ...prev, [field]: value }))
  }

  const nextStep = () => {
    if (currentStep === 'type' && !campaignData.name) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.fields.name') + ' ist erforderlich'
      })
      return
    }
    
    if (currentStep === 'template' && campaignData.type === 'email' && !campaignData.subject) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.fields.subject') + ' ist erforderlich'
      })
      return
    }

    if (currentStep === 'segment' && !campaignData.segment_id) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.validationError'),
        description: t('crud.fields.segment') + ' ist erforderlich'
      })
      return
    }

    if (!isLastStep) {
      const nextIndex = currentStepIndex + 1
      setCurrentStep(steps[nextIndex].key)
    }
  }

  const prevStep = () => {
    if (!isFirstStep) {
      const prevIndex = currentStepIndex - 1
      setCurrentStep(steps[prevIndex].key)
    }
  }

  const handleCreate = async () => {
    setLoading(true)
    try {
      const payload: any = {
        tenant_id: '00000000-0000-0000-0000-000000000001',
        name: campaignData.name,
        description: campaignData.description,
        type: campaignData.type,
        status: campaignData.scheduled_at ? 'scheduled' : 'draft',
        template_id: campaignData.template_id || null,
        segment_id: campaignData.segment_id || null,
        sender_name: campaignData.sender_name || null,
        sender_email: campaignData.sender_email || null,
        subject: campaignData.subject || null,
        scheduled_at: campaignData.scheduled_at || null,
        budget: campaignData.budget || null,
      }

      const response = await apiClient.post('/campaigns', payload)
      
      if (response.success || response.id) {
        const campaignId = response.success ? response.data?.id || response.data?.id : response.id
        
        toast({
          title: t('crud.messages.createSuccess', { entityType: t('crud.entities.campaign') }),
        })
        
        navigate(`/crm/campaign/${campaignId}`)
      }
    } catch (error: any) {
      console.error('Create error:', error)
      toast({
        variant: 'destructive',
        title: t('crud.messages.createError', { entityType: t('crud.entities.campaign') }),
        description: error.message || t('crud.messages.unknownError')
      })
    } finally {
      setLoading(false)
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 'type':
        return (
          <div className="space-y-6">
            <div>
              <Label htmlFor="name">{t('crud.fields.name')} *</Label>
              <Input
                id="name"
                value={campaignData.name}
                onChange={(e) => updateField('name', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.name')}
              />
            </div>
            <div>
              <Label htmlFor="description">{t('crud.fields.description')}</Label>
              <Textarea
                id="description"
                value={campaignData.description}
                onChange={(e) => updateField('description', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.description')}
                rows={4}
              />
            </div>
            <div>
              <Label htmlFor="type">{t('crud.fields.type')} *</Label>
              <Select value={campaignData.type} onValueChange={(value) => updateField('type', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="email">{t('crud.campaigns.types.email')}</SelectItem>
                  <SelectItem value="sms">{t('crud.campaigns.types.sms')}</SelectItem>
                  <SelectItem value="push">{t('crud.campaigns.types.push')}</SelectItem>
                  <SelectItem value="social">{t('crud.campaigns.types.social')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )

      case 'template':
        return (
          <div className="space-y-6">
            <div>
              <Label htmlFor="template_id">{t('crud.fields.template')}</Label>
              <Select 
                value={campaignData.template_id || ''} 
                onValueChange={(value) => updateField('template_id', value || null)}
              >
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.campaigns.builder.selectTemplate')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">{t('crud.campaigns.builder.noTemplate')}</SelectItem>
                  {templates.map((template) => (
                    <SelectItem key={template.id} value={template.id}>
                      {template.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {campaignData.type === 'email' && (
              <>
                <div>
                  <Label htmlFor="sender_name">{t('crud.fields.senderName')}</Label>
                  <Input
                    id="sender_name"
                    value={campaignData.sender_name}
                    onChange={(e) => updateField('sender_name', e.target.value)}
                    placeholder={t('crud.tooltips.placeholders.senderName')}
                  />
                </div>
                <div>
                  <Label htmlFor="sender_email">{t('crud.fields.senderEmail')}</Label>
                  <Input
                    id="sender_email"
                    type="email"
                    value={campaignData.sender_email}
                    onChange={(e) => updateField('sender_email', e.target.value)}
                    placeholder={t('crud.tooltips.placeholders.senderEmail')}
                  />
                </div>
                <div>
                  <Label htmlFor="subject">{t('crud.fields.subject')} *</Label>
                  <Input
                    id="subject"
                    value={campaignData.subject}
                    onChange={(e) => updateField('subject', e.target.value)}
                    placeholder={t('crud.tooltips.placeholders.subject')}
                  />
                </div>
              </>
            )}
          </div>
        )

      case 'segment':
        return (
          <div className="space-y-6">
            <div>
              <Label htmlFor="segment_id">{t('crud.fields.segment')} *</Label>
              <Select 
                value={campaignData.segment_id || ''} 
                onValueChange={(value) => updateField('segment_id', value || null)}
              >
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.campaigns.builder.selectSegment')} />
                </SelectTrigger>
                <SelectContent>
                  {segments.map((segment) => (
                    <SelectItem key={segment.id} value={segment.id}>
                      {segment.name} ({segment.member_count || 0} {t('crud.campaigns.builder.members')})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {campaignData.segment_id && (
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground">
                  {t('crud.campaigns.builder.segmentInfo')}
                </p>
              </div>
            )}
          </div>
        )

      case 'abtest':
        return (
          <div className="space-y-6">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="enable_abtest"
                checked={campaignData.enable_abtest}
                onCheckedChange={(checked) => updateField('enable_abtest', checked)}
              />
              <Label htmlFor="enable_abtest" className="cursor-pointer">
                {t('crud.campaigns.builder.enableAbtest')}
              </Label>
            </div>
            {campaignData.enable_abtest && (
              <div className="space-y-4 p-4 border rounded-lg">
                {campaignData.abtest_variants.map((variant, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{variant.name}</Badge>
                      <Label>{t('crud.campaigns.builder.variant')} {variant.name}</Label>
                    </div>
                    <Input
                      value={variant.subject}
                      onChange={(e) => {
                        const newVariants = [...campaignData.abtest_variants]
                        newVariants[index].subject = e.target.value
                        updateField('abtest_variants', newVariants)
                      }}
                      placeholder={t('crud.tooltips.placeholders.subject')}
                    />
                    <div className="flex items-center gap-2">
                      <Label className="text-sm">{t('crud.campaigns.builder.percentage')}</Label>
                      <Input
                        type="number"
                        min="0"
                        max="100"
                        value={variant.percentage}
                        onChange={(e) => {
                          const newVariants = [...campaignData.abtest_variants]
                          newVariants[index].percentage = parseInt(e.target.value) || 0
                          updateField('abtest_variants', newVariants)
                        }}
                        className="w-20"
                      />
                      <span className="text-sm text-muted-foreground">%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )

      case 'schedule':
        return (
          <div className="space-y-6">
            <div>
              <Label htmlFor="scheduled_at">{t('crud.fields.scheduledAt')}</Label>
              <Input
                id="scheduled_at"
                type="datetime-local"
                value={campaignData.scheduled_at}
                onChange={(e) => updateField('scheduled_at', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.scheduledAt')}
              />
              <p className="text-sm text-muted-foreground mt-1">
                {t('crud.campaigns.builder.scheduleInfo')}
              </p>
            </div>
            <div>
              <Label htmlFor="budget">{t('crud.fields.budget')}</Label>
              <Input
                id="budget"
                type="number"
                min="0"
                step="0.01"
                value={campaignData.budget || ''}
                onChange={(e) => updateField('budget', e.target.value ? parseFloat(e.target.value) : null)}
                placeholder={t('crud.tooltips.placeholders.budget')}
              />
            </div>
          </div>
        )

      case 'review':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>{t('crud.campaigns.builder.reviewTitle')}</CardTitle>
                <CardDescription>{t('crud.campaigns.builder.reviewDescription')}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label className="text-sm text-muted-foreground">{t('crud.fields.name')}</Label>
                  <p className="font-medium">{campaignData.name}</p>
                </div>
                <div>
                  <Label className="text-sm text-muted-foreground">{t('crud.fields.type')}</Label>
                  <p className="font-medium">{t(`crud.campaigns.types.${campaignData.type}`)}</p>
                </div>
                <div>
                  <Label className="text-sm text-muted-foreground">{t('crud.fields.segment')}</Label>
                  <p className="font-medium">
                    {segments.find(s => s.id === campaignData.segment_id)?.name || '-'}
                  </p>
                </div>
                {campaignData.type === 'email' && (
                  <>
                    <div>
                      <Label className="text-sm text-muted-foreground">{t('crud.fields.subject')}</Label>
                      <p className="font-medium">{campaignData.subject || '-'}</p>
                    </div>
                    <div>
                      <Label className="text-sm text-muted-foreground">{t('crud.fields.senderEmail')}</Label>
                      <p className="font-medium">{campaignData.sender_email || '-'}</p>
                    </div>
                  </>
                )}
                <div>
                  <Label className="text-sm text-muted-foreground">{t('crud.fields.scheduledAt')}</Label>
                  <p className="font-medium">
                    {campaignData.scheduled_at 
                      ? new Date(campaignData.scheduled_at).toLocaleString('de-DE')
                      : t('crud.campaigns.builder.immediate')}
                  </p>
                </div>
                {campaignData.budget && (
                  <div>
                    <Label className="text-sm text-muted-foreground">{t('crud.fields.budget')}</Label>
                    <p className="font-medium">{formatCurrency(campaignData.budget)}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <Button variant="ghost" onClick={() => navigate('/crm/campaigns')} className="mb-2">
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('crud.actions.back')}
          </Button>
          <h1 className="text-3xl font-bold">{t('crud.campaigns.builder.title')}</h1>
          <p className="text-muted-foreground">{t('crud.campaigns.builder.subtitle')}</p>
        </div>
      </div>

      {/* Step Indicator */}
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const StepIcon = step.icon
          const isActive = step.key === currentStep
          const isCompleted = currentStepIndex > index
          
          return (
            <div key={step.key} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : isCompleted
                      ? 'bg-primary/20 text-primary'
                      : 'bg-muted text-muted-foreground'
                  }`}
                >
                  {isCompleted ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    <StepIcon className="h-5 w-5" />
                  )}
                </div>
                <p className={`text-xs mt-2 ${isActive ? 'font-medium' : ''}`}>
                  {step.label}
                </p>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-1 mx-2 ${
                    isCompleted ? 'bg-primary' : 'bg-muted'
                  }`}
                />
              )}
            </div>
          )
        })}
      </div>

      {/* Step Content */}
      <Card>
        <CardHeader>
          <CardTitle>{steps[currentStepIndex].label}</CardTitle>
          <CardDescription>
            {t(`crud.campaigns.builder.stepDescriptions.${currentStep}`)}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {renderStepContent()}
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={isFirstStep}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          {t('crud.actions.back')}
        </Button>
        <div className="flex gap-2">
          {isLastStep ? (
            <Button
              onClick={handleCreate}
              disabled={loading}
            >
              {loading ? t('crud.messages.loading') : t('crud.actions.create')}
            </Button>
          ) : (
            <Button onClick={nextStep}>
              {t('crud.actions.next')}
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
