import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ObjectPage } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Save, Loader2, ArrowLeft, Target, Trash2 } from 'lucide-react'
import { queryKeys, mutationKeys } from '@/lib/query'
import { crmService, type Lead } from '@/lib/services/crm-service'
import { useToast } from '@/components/ui/toast-provider'
import {
  ENABLE_LEAD_MASK_BUILDER_FORM,
  LEAD_MASK_OBJECT_PAGE_CONFIG,
  mapLeadToMask,
  mapMaskToLead,
  type MaskLeadData,
  validateLeadPayload,
} from '@/features/crm-masks/lead-mask-support'
import { getEntityTypeLabel, getDetailTitle, getSuccessMessage, getErrorMessage, getStatusLabel } from '@/features/crud/utils/i18n-helpers'

export default function LeadDetailPage(): JSX.Element {
  if (ENABLE_LEAD_MASK_BUILDER_FORM) {
    return <LeadMaskDetailPage />
  }
  return <LegacyLeadDetailPage />
}

function LeadMaskDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const queryClient = useQueryClient()
  const toast = useToast()
  const isNew = !id || id === 'neu'
  const leadId = !isNew ? id ?? '' : ''
  const entityType = 'lead'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Lead')

  const { data: existingLead, isLoading, error } = useQuery({
    queryKey: queryKeys.crm.leads.detail(leadId),
    queryFn: () => crmService.getLead(leadId),
    enabled: Boolean(leadId),
  })

  const [maskData, setMaskData] = useState<MaskLeadData>(() => mapLeadToMask(null))
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    if (existingLead) {
      setMaskData(mapLeadToMask(existingLead))
    } else if (isNew) {
      setMaskData(mapLeadToMask(null))
    }
  }, [existingLead, isNew])

  const createMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.create,
    mutationFn: (data: Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>) => crmService.createLead(data),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'create', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
      navigate('/crm/leads')
    },
    onError: (err) => {
      toast.push(getErrorMessage(t, 'create', entityType))
      console.error('Create error:', err)
    },
  })

  const updateMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.update,
    mutationFn: (data: Partial<Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>>) =>
      crmService.updateLead(leadId, data),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'update', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.detail(leadId) })
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
    },
    onError: (err) => {
      toast.push(getErrorMessage(t, 'update', entityType))
      console.error('Update error:', err)
    },
  })

  const deleteMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.delete,
    mutationFn: () => crmService.deleteLead(leadId),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'delete', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
      navigate('/crm/leads')
    },
    onError: (err) => {
      toast.push(getErrorMessage(t, 'delete', entityType))
      console.error('Delete error:', err)
    },
  })

  const handleMaskSave = async (data: MaskLeadData): Promise<void> => {
    const payload = mapMaskToLead(data)
    const validationError = validateLeadPayload(payload)
    if (validationError) {
      setFormError(validationError)
      toast.push(validationError)
      return
    }

    setFormError(null)

    if (isNew) {
      await createMutation.mutateAsync(payload as Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>)
    } else {
      await updateMutation.mutateAsync(payload)
    }
  }

  const handleDelete = () => {
    if (!leadId) {
      return
    }
    if (window.confirm('Möchten Sie diesen Lead wirklich löschen?')) {
      deleteMutation.mutate()
    }
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-sm text-destructive">Fehler beim Laden des Leads.</p>
      </div>
    )
  }

  if (isLoading && !isNew) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Lead wird geladen...</span>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground mb-1">CRM &gt; Leads</p>
          <h1 className="text-3xl font-bold">
            {existingLead?.company ?? (isNew ? 'Neuen Lead anlegen' : 'Lead bearbeiten')}
          </h1>
          <p className="text-muted-foreground">Mask Builder Formular (Beta)</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate(-1)} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Zurück
          </Button>
          {!isNew && (
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
              Löschen
            </Button>
          )}
      </div>
    </div>

      {formError ? (
        <p className="text-sm text-destructive">{formError}</p>
      ) : null}

      <ObjectPage
        config={LEAD_MASK_OBJECT_PAGE_CONFIG}
        data={maskData}
        onChange={setMaskData}
        onSave={handleMaskSave}
        onCancel={() => navigate(-1)}
        isLoading={isLoading && !isNew}
      />
    </div>
  )
}
function LegacyLeadDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const queryClient = useQueryClient()
  const toast = useToast()
  const isNew = !id || id === 'neu'
  const entityType = 'lead'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Lead')

  const [lead, setLead] = useState<Partial<Lead>>({
    company: '',
    contactPerson: '',
    email: '',
    phone: '',
    source: '',
    potential: 0,
    priority: 'medium',
    status: 'new',
    assignedTo: '',
    expectedCloseDate: '',
    notes: '',
  })

  const { data: existingLead, isLoading } = useQuery({
    queryKey: queryKeys.crm.leads.detail(id ?? ''),
    queryFn: () => crmService.getLead(id ?? ''),
    enabled: !isNew && !!id,
  })

  useEffect(() => {
    if (existingLead && !isNew) {
      setLead(existingLead)
    }
  }, [existingLead, isNew])

  const createMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.create,
    mutationFn: (data: Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>) => crmService.createLead(data),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'create', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
      navigate('/crm/leads')
    },
    onError: (error) => {
      toast.push(getErrorMessage(t, 'create', entityType))
      console.error('Create error:', error)
    },
  })

  const updateMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.update,
    mutationFn: (data: Partial<Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>>) =>
      crmService.updateLead(id ?? '', data),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'update', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.detail(id ?? '') })
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
    },
    onError: (error) => {
      toast.push(getErrorMessage(t, 'update', entityType))
      console.error('Update error:', error)
    },
  })

  const deleteMutation = useMutation({
    mutationKey: mutationKeys.crm.leads.delete,
    mutationFn: () => crmService.deleteLead(id ?? ''),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'delete', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.leads.all })
      navigate('/crm/leads')
    },
    onError: (error) => {
      toast.push(getErrorMessage(t, 'delete', entityType))
      console.error('Delete error:', error)
    },
  })

  const handleSave = () => {
    if (!lead.company || !lead.contactPerson || !lead.source) {
      toast.push(t('crud.messages.fillRequiredFields'))
      return
    }

    if (isNew) {
      createMutation.mutate(lead as Omit<Lead, 'id' | 'createdAt' | 'updatedAt'>)
    } else {
      updateMutation.mutate(lead)
    }
  }

  const handleDelete = () => {
    if (window.confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
      deleteMutation.mutate()
    }
  }

  const updateField = (field: keyof Lead, value: any) => {
    setLead(prev => ({ ...prev, [field]: value }))
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0,
    }).format(value)
  }

  if (isLoading && !isNew) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">{t('crud.list.loading', { entityType: entityTypeLabel })}</span>
      </div>
    )
  }

  const priorityColor = lead.priority === 'high' ? 'destructive' : lead.priority === 'medium' ? 'secondary' : 'outline'
  const statusColor = lead.status === 'qualified' ? 'default' : 'outline'
  const priorityLabel = getStatusLabel(t, lead.priority || 'medium', lead.priority || 'medium')
  const statusLabel = getStatusLabel(t, lead.status || 'new', lead.status || 'new')

  const pageTitle = isNew 
    ? t('crud.actions.create') + ' ' + entityTypeLabel
    : lead.company 
      ? getDetailTitle(t, entityTypeLabel, lead.company)
      : entityTypeLabel
  const pageSubtitle = isNew 
    ? t('crud.detail.createNew', { entityType: entityTypeLabel })
    : lead.contactPerson || t('crud.detail.details', { entityType: entityTypeLabel })

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate('/crm/leads')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('common.back')}
          </Button>
          <div className="flex items-center gap-3">
            <Target className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                {pageTitle}
                {!isNew && (
                  <>
                    <Badge variant={priorityColor}>{priorityLabel}</Badge>
                    <Badge variant={statusColor}>{statusLabel}</Badge>
                  </>
                )}
              </h1>
              <p className="text-muted-foreground">{pageSubtitle}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {!isNew && (
            <Button
              variant="outline"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="text-red-600 hover:text-red-700"
            >
              {deleteMutation.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              <Trash2 className="h-4 w-4 mr-2" />
              {t('common.delete')}
            </Button>
          )}
          <Button variant="outline" onClick={() => navigate('/crm/leads')}>
            {t('common.cancel')}
          </Button>
          <Button
            onClick={handleSave}
            disabled={createMutation.isPending || updateMutation.isPending}
            className="gap-2"
          >
            {(createMutation.isPending || updateMutation.isPending) && (
              <Loader2 className="h-4 w-4 animate-spin" />
            )}
            <Save className="h-4 w-4" />
            {isNew ? t('crud.actions.create') : t('crud.actions.save')}
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t('crud.fields.leadInformation')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="company">{t('crud.fields.company')} *</Label>
              <Input
                id="company"
                value={lead.company || ''}
                onChange={(e) => updateField('company', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.companyName')}
              />
            </div>
            <div>
              <Label htmlFor="contactPerson">{t('crud.fields.contactPerson')} *</Label>
              <Input
                id="contactPerson"
                value={lead.contactPerson || ''}
                onChange={(e) => updateField('contactPerson', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.name')}
              />
            </div>
            <div>
              <Label htmlFor="email">{t('crud.fields.email')}</Label>
              <Input
                id="email"
                type="email"
                value={lead.email || ''}
                onChange={(e) => updateField('email', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.email')}
              />
            </div>
            <div>
              <Label htmlFor="phone">{t('crud.fields.phone')}</Label>
              <Input
                id="phone"
                value={lead.phone || ''}
                onChange={(e) => updateField('phone', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.phone')}
              />
            </div>
            <div>
              <Label htmlFor="source">{t('crud.fields.source')} *</Label>
              <Select value={lead.source || ''} onValueChange={(value) => updateField('source', value)}>
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.tooltips.placeholders.selectSource')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Website">{t('crud.fields.sourceWebsite')}</SelectItem>
                  <SelectItem value="Messe">{t('crud.fields.sourceTradeShow')}</SelectItem>
                  <SelectItem value="Empfehlung">{t('crud.fields.sourceReferral')}</SelectItem>
                  <SelectItem value="Kaltakquise">{t('crud.fields.sourceColdCall')}</SelectItem>
                  <SelectItem value="Social Media">{t('crud.fields.sourceSocialMedia')}</SelectItem>
                  <SelectItem value="Sonstiges">{t('crud.dialogs.amend.types.other')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('crud.fields.statusAndRating')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="potential">{t('crud.fields.potential')} (EUR)</Label>
              <Input
                id="potential"
                type="number"
                value={lead.potential || ''}
                onChange={(e) => updateField('potential', parseFloat(e.target.value) || 0)}
                placeholder={t('crud.tooltips.placeholders.potential')}
              />
              {lead.potential && lead.potential > 0 && (
                <p className="text-sm text-muted-foreground mt-1">
                  {formatCurrency(lead.potential)}
                </p>
              )}
            </div>
            <div>
              <Label htmlFor="priority">{t('crud.fields.priority')}</Label>
              <Select value={lead.priority || 'medium'} onValueChange={(value) => updateField('priority', value)}>
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.tooltips.placeholders.selectPriority')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">{getStatusLabel(t, 'low', 'Niedrig')}</SelectItem>
                  <SelectItem value="medium">{getStatusLabel(t, 'medium', 'Mittel')}</SelectItem>
                  <SelectItem value="high">{getStatusLabel(t, 'high', 'Hoch')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="status">{t('crud.fields.status')}</Label>
              <Select value={lead.status || 'new'} onValueChange={(value) => updateField('status', value)}>
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.tooltips.placeholders.selectStatus')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new">{getStatusLabel(t, 'new', 'Neu')}</SelectItem>
                  <SelectItem value="contacted">{getStatusLabel(t, 'contacted', 'Kontaktiert')}</SelectItem>
                  <SelectItem value="qualified">{getStatusLabel(t, 'qualified', 'Qualifiziert')}</SelectItem>
                  <SelectItem value="lost">{getStatusLabel(t, 'lost', 'Verloren')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="assignedTo">{t('crud.fields.assignedTo')}</Label>
              <Input
                id="assignedTo"
                value={lead.assignedTo || ''}
                onChange={(e) => updateField('assignedTo', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.assignedTo')}
              />
            </div>
            <div>
              <Label htmlFor="expectedCloseDate">{t('crud.fields.expectedCloseDate')}</Label>
              <Input
                id="expectedCloseDate"
                type="date"
                value={lead.expectedCloseDate ? lead.expectedCloseDate.split('T')[0] : ''}
                onChange={(e) => updateField('expectedCloseDate', e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>{t('crud.fields.notes')}</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={lead.notes || ''}
              onChange={(e) => updateField('notes', e.target.value)}
              placeholder={t('crud.tooltips.placeholders.leadNotes')}
              rows={6}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

