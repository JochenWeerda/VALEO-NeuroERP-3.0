import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Loader2 } from 'lucide-react'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { queryKeys } from '@/lib/query'
import { crmService, type Contact } from '@/lib/services/crm-service'
import { getEntityTypeLabel, getListTitle } from '@/features/crud/utils/i18n-helpers'

const EMPTY_CONTACTS_RESPONSE: { data: Contact[]; total: number } = {
  data: [],
  total: 0,
}

export default function KontakteListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const entityType = 'contact'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kontakt')

  const { data: contactsData, isLoading, error } = useQuery({
    queryKey: queryKeys.crm.contacts.listFiltered({ search: searchTerm || undefined }),
    queryFn: () => crmService.getContacts({ search: searchTerm || undefined }),
    initialData: EMPTY_CONTACTS_RESPONSE,
    // Sofort veraltet: Sonst gilt der Platzhalter als frisch geladen und
    // `staleTime` verhindert den Mount-Fetch (Nutzermeldung 17.07.2026).
    initialDataUpdatedAt: 0,
  })

  const contacts = contactsData.data
  const totalContacts = contactsData.total

  const columns = [
    {
      key: 'name' as const,
      label: t('crud.fields.name'),
      render: (contact: Contact) => (
        <button
          type="button"
          onClick={() => navigate(`/crm/kontakt/${contact.id}`)}
          className="min-h-11 font-medium text-primary touch-manipulation"
        >
          {contact.name}
        </button>
      ),
    },
    { key: 'company' as const, label: t('crud.fields.company') },
    { key: 'email' as const, label: t('crud.fields.email') },
    { key: 'phone' as const, label: t('crud.fields.phone') },
    {
      key: 'type' as const,
      label: t('crud.fields.type'),
      render: (contact: Contact) => (
        <Badge variant="outline">
          {getEntityTypeLabel(t, contact.type, contact.type)}
        </Badge>
      ),
    },
  ]

  if (error) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-status-error">{t('crud.messages.loadError')}</h1>
          <p className="text-muted-foreground">
            {error instanceof Error ? error.message : t('crud.messages.unknownError')}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">{getListTitle(t, entityTypeLabel)}</h1>
          <p className="text-muted-foreground">
            {isLoading ? t('crud.list.loading', { entityType: entityTypeLabel }) : t('crud.list.total', { count: totalContacts, entityType: entityTypeLabel })}
          </p>
        </div>
        <Button onClick={() => navigate('/crm/kontakt/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          {t('crud.actions.new')} {entityTypeLabel}
        </Button>
      </div>

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.fields.total')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalContacts}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{getEntityTypeLabel(t, 'customer', 'Kunde')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {contacts.filter(c => c.type === 'customer').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{getEntityTypeLabel(t, 'supplier', 'Lieferant')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-status-success">
              {contacts.filter(c => c.type === 'supplier').length}
            </div>
          </CardContent>
        </Card>
      </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>{t('common.search')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label={t('common.search')}
                placeholder={t('crud.list.searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation">
              <FileDown className="h-4 w-4" />
              {t('crud.actions.export')}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">{t('crud.list.loading', { entityType: entityTypeLabel })}</span>
            </div>
          ) : (
            <DataTable data={contacts} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
