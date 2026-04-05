import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { FileDown, FileText, Loader2, Plus, Search, Users } from 'lucide-react'
import { useListActions } from '@/hooks/useListActions'
import { businessPartnerService, type BusinessPartnerEnvelope } from '@/lib/services/business-partner-service'
import { ErrorState } from '@/components/ErrorState'

type CustomerRow = {
  id: string
  customer_number: string
  name: string
  email: string
  phone: string
  payment_terms: string
  status: 'active' | 'inactive' | 'blocked'
}

function mapToRow(item: BusinessPartnerEnvelope): CustomerRow {
  const bp = item.business_partner
  return {
    id: String(bp.core_identity.partner_id ?? ''),
    customer_number: bp.core_identity.partner_number,
    name: bp.core_identity.name_1,
    email: String(bp.contact_data.email ?? ''),
    phone: String(bp.contact_data.phone ?? ''),
    payment_terms: String(bp.finance.payment_terms_id ?? '-'),
    status: bp.core_identity.status,
  }
}

export default function KundenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const searchFromUrl = searchParams.get('search') ?? ''
  const [searchTerm, setSearchTerm] = useState(searchFromUrl)
  const searchRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    setSearchTerm(searchFromUrl)
  }, [searchFromUrl])

  const customersQuery = useQuery({
    queryKey: ['business-partners', searchTerm],
    queryFn: async () => businessPartnerService.list({ search: searchTerm || undefined }),
  })

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => navigate('/verkauf/kunde/neu'),
    onSearch: () => searchRef.current?.focus(),
    onRefresh: () => { void customersQuery.refetch() },
  })
  useKeyboardShortcuts(shortcuts)

  const customers = useMemo(
    () => (customersQuery.data ?? []).filter((item) => item.business_partner.roles.is_customer).map(mapToRow),
    [customersQuery.data],
  )

  const exportData = customers.map((c) => ({
    Kundennummer: c.customer_number,
    Name: c.name,
    Email: c.email || '-',
    Telefon: c.phone || '-',
    Zahlungsziel: c.payment_terms,
    Status: c.status,
  }))

  const { handleExport, handlePrint } = useListActions({
    data: exportData,
    entityName: 'kunden',
  })

  const columns = [
    {
      key: 'name' as const,
      label: 'Kunde',
      render: (customer: CustomerRow) => (
        <button onClick={() => navigate(`/verkauf/kunde/${customer.id}`)} className="font-medium text-blue-600 hover:underline">
          {customer.name}
        </button>
      ),
    },
    { key: 'customer_number' as const, label: 'Kundennr' },
    { key: 'email' as const, label: 'E-Mail' },
    { key: 'phone' as const, label: 'Telefon' },
    { key: 'payment_terms' as const, label: 'Zahlungsziel' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (customer: CustomerRow) => (
        <Badge variant={customer.status === 'active' ? 'outline' : 'secondary'}>
          {customer.status === 'active' ? 'Aktiv' : customer.status === 'inactive' ? 'Inaktiv' : 'Gesperrt'}
        </Badge>
      ),
    },
  ]

  if (customersQuery.isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (customersQuery.isError) {
    return <ErrorState error={customersQuery.error as Error} onRetry={() => { void customersQuery.refetch() }} />
  }

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kunden</h1>
          <p className="text-muted-foreground">Business-Partner Stamm (Rolle Kunde)</p>
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
              <span className="text-2xl font-bold">{customers.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktive Kunden</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{customers.filter((c) => c.status === 'active').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesperrt/Inaktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{customers.filter((c) => c.status !== 'active').length}</span>
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
                ref={searchRef}
                placeholder="Suche nach Kundennummer oder Name..."
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
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
