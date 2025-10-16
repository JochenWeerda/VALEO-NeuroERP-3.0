import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Loader2 } from 'lucide-react'
import { queryKeys } from '@/lib/query'
import { crmService, type Contact } from '@/lib/services/crm-service'

export default function KontakteListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const { data: contactsData, isLoading, error } = useQuery({
    queryKey: queryKeys.crm.contacts.listFiltered({ search: searchTerm || undefined }),
    queryFn: () => crmService.getContacts({ search: searchTerm || undefined }),
  })

  const contacts = contactsData?.data || []
  const totalContacts = contactsData?.total || 0

  const columns = [
    {
      key: 'name' as const,
      label: 'Name',
      render: (contact: Contact) => (
        <button
          onClick={() => navigate(`/crm/kontakt/${contact.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {contact.name}
        </button>
      ),
    },
    { key: 'company' as const, label: 'Unternehmen' },
    { key: 'email' as const, label: 'E-Mail' },
    { key: 'phone' as const, label: 'Telefon' },
    {
      key: 'type' as const,
      label: 'Typ',
      render: (contact: Contact) => (
        <Badge variant="outline">
          {contact.type === 'customer' ? 'Kunde' :
           contact.type === 'supplier' ? 'Lieferant' : 'Landwirt'}
        </Badge>
      ),
    },
  ]

  if (error) {
    return (
      <div className="space-y-4 p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Fehler beim Laden der Kontakte</h1>
          <p className="text-muted-foreground">
            {error instanceof Error ? error.message : 'Unbekannter Fehler'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kontakte</h1>
          <p className="text-muted-foreground">
            {isLoading ? 'Lade Kontakte...' : `${totalContacts} CRM-Kontakte`}
          </p>
        </div>
        <Button onClick={() => navigate('/crm/kontakt/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Kontakt
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalContacts}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kunden</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {contacts.filter(c => c.type === 'customer').length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Lieferanten</CardTitle>
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
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Suche nach Name, Unternehmen oder E-Mail..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">Lade Kontakte...</span>
            </div>
          ) : (
            <DataTable data={contacts} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
