import { useState, useEffect } from 'react'
import { useNavigate, useParams } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { NativeSelect } from '@/components/ui/native-select'
import { Badge } from '@/components/ui/badge'
import { Save, Loader2, ArrowLeft, Calendar, Mail, Phone, Users, Trash2, Plus, Minus } from 'lucide-react'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { queryKeys, mutationKeys } from '@/lib/query'
import { crmService, type Activity } from '@/lib/services/crm-service'
import { useToast } from '@/components/ui/toast-provider'
import { getEntityTypeLabel, getDetailTitle, getSuccessMessage, getErrorMessage, getStatusLabel } from '@/features/crud/utils/i18n-helpers'

export default function AktivitaetDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const queryClient = useQueryClient()
  const toast = useToast()
  const isNew = !id || id === 'neu'
  const entityType = 'activity'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Aktivität')

  const [activity, setActivity] = useState<Partial<Activity>>({
    type: 'meeting',
    title: '',
    customer: '',
    contactPerson: '',
    date: new Date().toISOString().split('T')[0],
    status: 'planned',
    assignedTo: '',
    description: '',
    mainTopics: [''],
    ordersPlaced: [''],
    followUpActions: [''],
  })

  const { data: existingActivity, isLoading } = useQuery({
    queryKey: queryKeys.crm.activities.detail(id ?? ''),
    queryFn: () => crmService.getActivity(id ?? ''),
    enabled: !isNew && !!id,
  })

  useEffect(() => {
    if (existingActivity && !isNew) {
      setActivity(existingActivity)
    }
  }, [existingActivity, isNew])

  const createMutation = useMutation({
    mutationKey: mutationKeys.crm.activities.create,
    mutationFn: async (data: Omit<Activity, 'id' | 'createdAt' | 'updatedAt'>) => {
      const created = await crmService.createActivity(data)
      await crmService.syncActivitySubResources(created.id, {
        mainTopics: data.mainTopics,
        ordersPlaced: data.ordersPlaced,
        followUpActions: data.followUpActions,
      })
      return created
    },
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'create', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.activities.all })
      navigate('/crm/aktivitaeten')
    },
    onError: (error) => {
      toast.push(getErrorMessage(t, 'create', entityType))
    },
  })

  const updateMutation = useMutation({
    mutationKey: mutationKeys.crm.activities.update,
    mutationFn: async (data: Partial<Omit<Activity, 'id' | 'createdAt' | 'updatedAt'>>) => {
      const { mainTopics, ordersPlaced, followUpActions, ...baseData } = data
      const updated = await crmService.updateActivity(id ?? '', baseData)
      await crmService.syncActivitySubResources(id ?? '', {
        mainTopics,
        ordersPlaced,
        followUpActions,
      })
      return updated
    },
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'update', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.activities.detail(id ?? '') })
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.activities.all })
    },
    onError: (error) => {
      toast.push(getErrorMessage(t, 'update', entityType))
    },
  })

  const deleteMutation = useMutation({
    mutationKey: mutationKeys.crm.activities.delete,
    mutationFn: () => crmService.deleteActivity(id ?? ''),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'delete', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.activities.all })
      navigate('/crm/aktivitaeten')
    },
    onError: (error) => {
      toast.push(getErrorMessage(t, 'delete', entityType))
    },
  })

  const handleSave = () => {
    if (!activity.title || !activity.customer || !activity.contactPerson || !activity.date) {
      toast.push(t('crud.messages.fillRequiredFields'))
      return
    }

    const payload: Omit<Activity, 'id' | 'createdAt' | 'updatedAt'> = {
      ...(activity as Omit<Activity, 'id' | 'createdAt' | 'updatedAt'>),
      mainTopics: (activity.mainTopics || []).map((item) => item.trim()).filter(Boolean),
      ordersPlaced: (activity.ordersPlaced || []).map((item) => item.trim()).filter(Boolean),
      followUpActions: (activity.followUpActions || []).map((item) => item.trim()).filter(Boolean),
    }

    if (isNew) {
      createMutation.mutate(payload)
    } else {
      updateMutation.mutate(payload)
    }
  }

  const handleDelete = () => {
    if (window.confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
      deleteMutation.mutate()
    }
  }

  const updateField = (field: keyof Activity, value: unknown) => {
    setActivity(prev => ({ ...prev, [field]: value }))
  }

  const updateStringList = (field: 'mainTopics' | 'ordersPlaced' | 'followUpActions', index: number, value: string) => {
    setActivity((prev) => {
      const current = [...(prev[field] || [])]
      current[index] = value
      return { ...prev, [field]: current }
    })
  }

  const addStringListItem = (field: 'mainTopics' | 'ordersPlaced' | 'followUpActions') => {
    setActivity((prev) => ({ ...prev, [field]: [...(prev[field] || []), ''] }))
  }

  const removeStringListItem = (field: 'mainTopics' | 'ordersPlaced' | 'followUpActions', index: number) => {
    setActivity((prev) => ({ ...prev, [field]: (prev[field] || []).filter((_, i) => i !== index) }))
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'meeting':
        return Calendar
      case 'call':
        return Phone
      case 'email':
        return Mail
      default:
        return Users
    }
  }

  const TypeIcon = getTypeIcon(activity.type || 'meeting')

  if (isLoading && !isNew) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">{t('crud.list.loading', { entityType: entityTypeLabel })}</span>
      </div>
    )
  }

  const statusColor = activity.status === 'completed' ? 'outline' : activity.status === 'overdue' ? 'destructive' : 'secondary'
  const pageTitle = isNew 
    ? `${t('crud.actions.create')} ${entityTypeLabel}`
    : getDetailTitle(t, entityTypeLabel, activity.title || entityTypeLabel)

  return (
    <div className="space-y-6 p-6">
      <ModuleToolbar backTarget="/crm/aktivitaeten" closeTarget="/crm/aktivitaeten" title={pageTitle} />
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate('/crm/aktivitaeten')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('common.back')}
          </Button>
          <div className="flex items-center gap-3">
            <TypeIcon className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-2">
                {pageTitle}
                {!isNew && (
                  <Badge variant={statusColor}>
                    {getStatusLabel(t, activity.status || 'planned', activity.status || 'planned')}
                  </Badge>
                )}
              </h1>
              <p className="text-muted-foreground">
                {isNew ? t('crud.detail.createNew', { entityType: entityTypeLabel }) : `${activity.customer} - ${activity.contactPerson}`}
              </p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {!isNew && (
            <Button
              variant="outline"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="text-status-error hover:text-red-700"
            >
              {deleteMutation.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
              <Trash2 className="h-4 w-4 mr-2" />
              {t('common.delete')}
            </Button>
          )}
          <Button variant="outline" onClick={() => navigate('/crm/aktivitaeten')}>
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
            <CardTitle>{t('crud.fields.activityDetails')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="type">{t('crud.fields.type')} *</Label>
              <NativeSelect
                value={activity.type || 'meeting'}
                onValueChange={(value) => updateField('type', value)}
                options={[
                  { value: 'meeting', label: t('crud.fields.meeting') },
                  { value: 'call', label: t('crud.fields.call') },
                  { value: 'email', label: t('crud.fields.email') },
                  { value: 'note', label: t('crud.fields.note') },
                ]}
                placeholder={t('crud.tooltips.placeholders.selectType')}
              />
            </div>
            <div>
              <Label htmlFor="title">{t('crud.fields.title')} *</Label>
              <Input
                id="title"
                value={activity.title || ''}
                onChange={(e) => updateField('title', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.activityTitle')}
              />
            </div>
            <div>
              <Label htmlFor="customer">{t('crud.entities.customer')} *</Label>
              <Input
                id="customer"
                value={activity.customer || ''}
                onChange={(e) => updateField('customer', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.companyExample')}
              />
            </div>
            <div>
              <Label htmlFor="contactPerson">{t('crud.fields.contactPerson')} *</Label>
              <Input
                id="contactPerson"
                value={activity.contactPerson || ''}
                onChange={(e) => updateField('contactPerson', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.contactPersonName')}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('crud.fields.schedulingAndStatus')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="date">{t('crud.fields.date')} *</Label>
              <Input
                id="date"
                type="date"
                value={activity.date ? activity.date.split('T')[0] : ''}
                onChange={(e) => updateField('date', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="status">{t('crud.fields.status')}</Label>
              <NativeSelect
                value={activity.status || 'planned'}
                onValueChange={(value) => updateField('status', value)}
                options={[
                  { value: 'planned', label: t('status.planned') },
                  { value: 'completed', label: t('status.completed') },
                  { value: 'overdue', label: t('status.overdue') },
                ]}
                placeholder={t('crud.tooltips.placeholders.selectStatus')}
              />
            </div>
            <div>
              <Label htmlFor="assignedTo">{t('crud.fields.assignedTo')} *</Label>
              <Input
                id="assignedTo"
                value={activity.assignedTo || ''}
                onChange={(e) => updateField('assignedTo', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.assignedToExample')}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>{t('crud.fields.description')}</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea
              value={activity.description || ''}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder={t('crud.tooltips.placeholders.activityDescription')}
              rows={6}
            />
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Main Topics</CardTitle>
            <Button type="button" size="sm" variant="outline" onClick={() => addStringListItem('mainTopics')}>
              <Plus className="h-4 w-4 mr-2" />
              Hinzufügen
            </Button>
          </CardHeader>
          <CardContent className="space-y-2">
            {(activity.mainTopics || []).map((item, index) => (
              <div key={`topic-${index}`} className="flex items-center gap-2">
                <Input
                  value={item}
                  onChange={(e) => updateStringList('mainTopics', index, e.target.value)}
                  placeholder="Thema"
                />
                <Button type="button" size="icon" variant="outline" onClick={() => removeStringListItem('mainTopics', index)}>
                  <Minus className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Orders Placed</CardTitle>
            <Button type="button" size="sm" variant="outline" onClick={() => addStringListItem('ordersPlaced')}>
              <Plus className="h-4 w-4 mr-2" />
              Hinzufügen
            </Button>
          </CardHeader>
          <CardContent className="space-y-2">
            {(activity.ordersPlaced || []).map((item, index) => (
              <div key={`order-${index}`} className="flex items-center gap-2">
                <Input
                  value={item}
                  onChange={(e) => updateStringList('ordersPlaced', index, e.target.value)}
                  placeholder="Auftrag/Beleg"
                />
                <Button type="button" size="icon" variant="outline" onClick={() => removeStringListItem('ordersPlaced', index)}>
                  <Minus className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Follow-up Actions</CardTitle>
            <Button type="button" size="sm" variant="outline" onClick={() => addStringListItem('followUpActions')}>
              <Plus className="h-4 w-4 mr-2" />
              Hinzufügen
            </Button>
          </CardHeader>
          <CardContent className="space-y-2">
            {(activity.followUpActions || []).map((item, index) => (
              <div key={`followup-${index}`} className="flex items-center gap-2">
                <Input
                  value={item}
                  onChange={(e) => updateStringList('followUpActions', index, e.target.value)}
                  placeholder="Folgeaktion"
                />
                <Button type="button" size="icon" variant="outline" onClick={() => removeStringListItem('followUpActions', index)}>
                  <Minus className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

