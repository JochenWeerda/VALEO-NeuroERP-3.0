import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Target, Loader2 } from 'lucide-react'
import { queryKeys } from '@/lib/query'
import { crmService, type Lead } from '@/lib/services/crm-service'

export default function LeadsPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const { data: leadsData, isLoading, error } = useQuery({
    queryKey: queryKeys.crm.leads.listFiltered({ search: searchTerm || undefined }),
    queryFn: () => crmService.getLeads({ search: searchTerm || undefined }),
  })

  const leads = leadsData?.data || []
  const totalLeads = leadsData?.total || 0
  const totalPotential = leads.reduce((sum, lead) => sum + lead.potential, 0)
  const qualifiedLeads = leads.filter(lead => lead.status === 'qualified').length
  const highPriorityLeads = leads.filter(lead => lead.priority === 'high').length

  const columns = [
    {
      key: 'company' as const,
      label: 'Unternehmen',
      render: (lead: Lead) => (
        <div>
          <button
            onClick={() => navigate(`/crm/lead/${lead.id}`)}
            className="font-medium text-blue-600 hover:underline"
          >
            {lead.company}
          </button>
          <div className="text-sm text-muted-foreground">{lead.contactPerson}</div>
        </div>
      ),
    },
    { key: 'source' as const, label: 'Quelle' },
    {
      key: 'potential' as const,
      label: 'Potenzial',
      render: (lead: Lead) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(lead.potential),
    },
    {
      key: 'priority' as const,
      label: 'Priorität',
      render: (lead: Lead) => (
        <Badge variant={lead.priority === 'high' ? 'destructive' : lead.priority === 'medium' ? 'secondary' : 'outline'}>
          {lead.priority === 'high' ? 'Hoch' : lead.priority === 'medium' ? 'Mittel' : 'Niedrig'}
        </Badge>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (lead: Lead) => (
        <Badge variant={lead.status === 'qualified' ? 'default' : 'outline'}>
          {lead.status === 'new' ? 'Neu' : lead.status === 'contacted' ? 'Kontaktiert' : lead.status === 'qualified' ? 'Qualifiziert' : 'Verloren'}
        </Badge>
      ),
    },
  ]

  if (error) {
    return (
      <div className="space-y-4 p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Fehler beim Laden der Leads</h1>
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
          <h1 className="text-3xl font-bold">Leads</h1>
          <p className="text-muted-foreground">
            {isLoading ? 'Lade Leads...' : `${totalLeads} Verkaufschancen`}
          </p>
        </div>
        <Button onClick={() => navigate('/crm/lead/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Lead
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Leads Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{totalLeads}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtpotenzial</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(totalPotential)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Qualifiziert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{qualifiedLeads}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Hohe Priorität</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{highPriorityLeads}</span>
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
                placeholder="Suche nach Unternehmen, Kontakt oder Quelle..."
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
              <span className="ml-2">Lade Leads...</span>
            </div>
          ) : (
            <DataTable data={leads} columns={columns} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
