import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Users, Loader2, AlertCircle, FileText } from 'lucide-react'
import { useCustomers } from '@/lib/api/crm'
import { useListActions } from '@/hooks/useListActions'

export default function KundenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  
  // Live API
  const { data, isLoading, error } = useCustomers({ 
    search: searchTerm || undefined,
    is_active: true 
  })

  const customers = data?.items ?? []
  
  const exportData = customers.map(c => ({
    Kundennummer: c.customer_number,
    Name: c.name,
    Email: c.email || '-',
    Telefon: c.phone || '-',
    Zahlungsziel: `${c.payment_terms} Tage`,
    Status: c.is_active ? 'Aktiv' : 'Inaktiv',
  }))

  const { handleExport, handlePrint } = useListActions({
    data: exportData,
    entityName: 'kunden',
  })
  
  const columns = [
    {
      key: 'name' as const,
      label: 'Kunde',
      render: (customer: typeof customers[0]) => (
        <button 
          onClick={() => navigate(`/verkauf/kunde/${customer.id}`)} 
          className="font-medium text-blue-600 hover:underline"
        >
          {customer.name}
        </button>
      ),
    },
    {
      key: 'customer_number' as const,
      label: 'Kundennr',
    },
    {
      key: 'email' as const,
      label: 'E-Mail',
    },
    {
      key: 'phone' as const,
      label: 'Telefon',
    },
    { 
      key: 'payment_terms' as const, 
      label: 'Zahlungsziel', 
      render: (customer: typeof customers[0]) => `${customer.payment_terms} Tage` 
    },
    {
      key: 'is_active' as const,
      label: 'Status',
      render: (customer: typeof customers[0]) => (
        <Badge variant={customer.is_active ? 'outline' : 'destructive'}>
          {customer.is_active ? 'Aktiv' : 'Inaktiv'}
        </Badge>
      ),
    },
  ]

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="p-6 max-w-md">
          <div className="flex items-center gap-3 text-destructive">
            <AlertCircle className="h-6 w-6" />
            <div>
              <h3 className="font-semibold">Fehler beim Laden</h3>
              <p className="text-sm text-muted-foreground">
                {error instanceof Error ? error.message : 'Unbekannter Fehler'}
              </p>
            </div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kunden</h1>
          <p className="text-muted-foreground">Kundenverwaltung</p>
        </div>
        <Button onClick={() => navigate('/verkauf/kunde/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Kunde
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Kunden Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{data?.total ?? 0}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktive Kunden</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {customers.filter(c => c.is_active).length}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auf dieser Seite</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{customers.length}</span>
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
                placeholder="Suche nach Name, E-Mail, Telefon..." 
                value={searchTerm} 
                onChange={(e) => setSearchTerm(e.target.value)} 
                className="pl-10" 
              />
            </div>
            <Button variant="outline" className="gap-2" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              Export
            </Button>
            <Button variant="outline" className="gap-2" onClick={handlePrint}>
              <FileText className="h-4 w-4" />
              Drucken
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={customers} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
