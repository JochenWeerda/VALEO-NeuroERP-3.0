import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Loader2 } from 'lucide-react'
import { queryKeys } from '@/lib/query'
import { crmService, type Contact } from '@/lib/services/crm-service'
import { getEntityTypeLabel, getListTitle } from '@/features/crud/utils/i18n-helpers'

export default function KontakteListePage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const entityType = 'contact'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Kontakt')

  const { data: contactsData, isLoading, error } = useQuery({
    queryKey: queryKeys.crm.contacts.listFiltered({ search: searchTerm || undefined }),
    queryFn: () => crmService.getContacts({ search: searchTerm || undefined }),
  })

  const contacts = contactsData?.data || []
  const totalContacts = contactsData?.total || 0

  const columns = [
    {
      key: 'name' as const,
      label: t('crud.fields.name'),
      render: (contact: Contact) => (
        <button
          onClick={() => navigate(`/crm/kontakt/${contact.id}`)}
          className="font-medium text-blue-600 hover:underline"
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
      <div className="space-y-4 p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">{t('crud.messages.loadError')}</h1>
          <p className="text-muted-foreground">
            {error instanceof Error ? error.message : t('crud.messages.unknownError')}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{getListTitle(t, entityTypeLabel)}</h1>
          <p className="text-muted-foreground">
            {isLoading ? t('crud.list.loading', { entityType: entityTypeLabel }) : t('crud.list.total', { count: totalContacts, entityType: entityTypeLabel })}
          </p>
        </div>
        <Button onClick={() => navigate('/crm/kontakt/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          {t('crud.actions.new')} {entityTypeLabel}
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.list.total')}</CardTitle>
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
            <div className="text-2xl font-bold text-blue-600">
              {contacts.filter(c => c.type === 'customer').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{getEntityTypeLabel(t, 'supplier', 'Lieferant')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {contacts.filter(c => c.type === 'supplier').length}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('common.search')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder={t('crud.list.searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" className="gap-2">
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
