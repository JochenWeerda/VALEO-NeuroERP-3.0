import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Save, Loader2, ArrowLeft, User, Trash2 } from 'lucide-react'
import { queryKeys, mutationKeys } from '@/lib/query'
import { crmService, type Contact } from '@/lib/services/crm-service'
import { useToast } from '@/components/ui/toast-provider'
import { getEntityTypeLabel, getDetailTitle, getSuccessMessage, getErrorMessage } from '@/features/crud/utils/i18n-helpers'

export default function KontaktDetailPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const queryClient = useQueryClient()
  const toast = useToast()
  const isNew = !id || id === 'neu'
  const entityType = 'contact'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kontakt')

  const [contact, setContact] = useState<Partial<Contact>>({
    name: '',
    company: '',
    email: '',
    phone: '',
    type: 'customer',
    address: undefined,
    notes: '',
  })

  const { data: existingContact, isLoading } = useQuery({
    queryKey: queryKeys.crm.contacts.detail(id ?? ''),
    queryFn: () => crmService.getContact(id ?? ''),
    enabled: !isNew && !!id,
  })

  useEffect(() => {
    if (existingContact && !isNew) {
      setContact(existingContact)
    }
  }, [existingContact, isNew])

  const createMutation = useMutation({
    mutationKey: mutationKeys.crm.contacts.create,
    mutationFn: (data: Omit<Contact, 'id' | 'createdAt' | 'updatedAt'>) => crmService.createContact(data),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'create', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.contacts.all })
      navigate('/crm/kontakte-liste')
    },
    onError: (error) => {
      toast.push(getErrorMessage(t, 'create', entityType))
      console.error('Create error:', error)
    },
  })

  const updateMutation = useMutation({
    mutationKey: mutationKeys.crm.contacts.update,
    mutationFn: (data: Partial<Omit<Contact, 'id' | 'createdAt' | 'updatedAt'>>) =>
      crmService.updateContact(id ?? '', data),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'update', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.contacts.detail(id ?? '') })
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.contacts.all })
    },
    onError: (error) => {
      toast.push(getErrorMessage(t, 'update', entityType))
      console.error('Update error:', error)
    },
  })

  const deleteMutation = useMutation({
    mutationKey: mutationKeys.crm.contacts.delete,
    mutationFn: () => crmService.deleteContact(id ?? ''),
    onSuccess: () => {
      toast.push(getSuccessMessage(t, 'delete', entityType))
      queryClient.invalidateQueries({ queryKey: queryKeys.crm.contacts.all })
      navigate('/crm/kontakte-liste')
    },
    onError: (error) => {
      toast.push(getErrorMessage(t, 'delete', entityType))
      console.error('Delete error:', error)
    },
  })

  const handleSave = () => {
    if (!contact.name || !contact.company || !contact.email) {
      toast.push(t('crud.messages.fillRequiredFields'))
      return
    }

    if (isNew) {
      createMutation.mutate(contact as Omit<Contact, 'id' | 'createdAt' | 'updatedAt'>)
    } else {
      updateMutation.mutate(contact)
    }
  }

  const handleDelete = () => {
    if (window.confirm(t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeLabel }))) {
      deleteMutation.mutate()
    }
  }

  const updateField = (field: keyof Contact, value: any) => {
    setContact(prev => ({ ...prev, [field]: value }))
  }

  const updateAddress = (field: string, value: string) => {
    setContact(prev => ({
      ...prev,
      address: {
        ...(prev.address || { street: '', city: '', zipCode: '', country: '' }),
        [field]: value,
      },
    }))
  }

  if (isLoading && !isNew) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">{t('crud.list.loading', { entityType: entityTypeLabel })}</span>
      </div>
    )
  }

  const pageTitle = isNew 
    ? `${t('crud.actions.create')} ${entityTypeLabel}`
    : getDetailTitle(t, entityTypeLabel, contact.name || entityTypeLabel)
  const pageSubtitle = isNew 
    ? t('crud.detail.createNew', { entityType: entityTypeLabel })
    : contact.company || t('crud.detail.details', { entityType: entityTypeLabel })

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="sm" onClick={() => navigate('/crm/kontakte-liste')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            {t('common.back')}
          </Button>
          <div className="flex items-center gap-3">
            <User className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold">{pageTitle}</h1>
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
          <Button variant="outline" onClick={() => navigate('/crm/kontakte-liste')}>
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
            <CardTitle>{t('crud.fields.contactData')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="name">{t('crud.fields.name')} *</Label>
              <Input
                id="name"
                value={contact.name || ''}
                onChange={(e) => updateField('name', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.name')}
              />
            </div>
            <div>
              <Label htmlFor="company">{t('crud.fields.company')} *</Label>
              <Input
                id="company"
                value={contact.company || ''}
                onChange={(e) => updateField('company', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.companyName')}
              />
            </div>
            <div>
              <Label htmlFor="email">{t('crud.fields.email')} *</Label>
              <Input
                id="email"
                type="email"
                value={contact.email || ''}
                onChange={(e) => updateField('email', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.email')}
              />
            </div>
            <div>
              <Label htmlFor="phone">{t('crud.fields.phone')}</Label>
              <Input
                id="phone"
                value={contact.phone || ''}
                onChange={(e) => updateField('phone', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.phone')}
              />
            </div>
            <div>
              <Label htmlFor="type">{t('crud.fields.type')}</Label>
              <Select value={contact.type || 'customer'} onValueChange={(value) => updateField('type', value)}>
                <SelectTrigger>
                  <SelectValue placeholder={t('crud.tooltips.placeholders.selectType')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="customer">{getEntityTypeLabel(t, 'customer', 'Kunde')}</SelectItem>
                  <SelectItem value="supplier">{getEntityTypeLabel(t, 'supplier', 'Lieferant')}</SelectItem>
                  <SelectItem value="farmer">{getEntityTypeLabel(t, 'farmer', 'Landwirt')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('crud.fields.addressAndNotes')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="street">{t('crud.fields.street')}</Label>
              <Input
                id="street"
                value={contact.address?.street || ''}
                onChange={(e) => updateAddress('street', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.street')}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="zipCode">{t('crud.fields.postalCode')}</Label>
                <Input
                  id="zipCode"
                  value={contact.address?.zipCode || ''}
                  onChange={(e) => updateAddress('zipCode', e.target.value)}
                  placeholder={t('crud.tooltips.placeholders.postalCode')}
                />
              </div>
              <div>
                <Label htmlFor="city">{t('crud.fields.city')}</Label>
                <Input
                  id="city"
                  value={contact.address?.city || ''}
                  onChange={(e) => updateAddress('city', e.target.value)}
                  placeholder={t('crud.tooltips.placeholders.city')}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="country">{t('crud.fields.country')}</Label>
              <Input
                id="country"
                value={contact.address?.country || ''}
                onChange={(e) => updateAddress('country', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.country')}
              />
            </div>
            <div>
              <Label htmlFor="notes">{t('crud.fields.notes')}</Label>
              <Textarea
                id="notes"
                value={contact.notes || ''}
                onChange={(e) => updateField('notes', e.target.value)}
                placeholder={t('crud.tooltips.placeholders.notes')}
                rows={4}
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

