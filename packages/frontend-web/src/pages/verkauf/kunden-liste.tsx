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
import { FileDown, FileText, Loader2, MapPin, Plus, Search, Users } from 'lucide-react'
import { useListActions } from '@/hooks/useListActions'
import { businessPartnerService, type BusinessPartnerEnvelope } from '@/lib/services/business-partner-service'
import { apiClient } from '@/lib/api-client'
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

// Operativer Kundenstamm (public.kunden via kunden_lookup) -> CustomerRow.
function mapLookupToRow(k: Record<string, unknown>): CustomerRow {
  return {
    id: String((k.business_partner_id as string) || (k.kunden_nr as string) || ''),
    customer_number: String(k.kunden_nr ?? ''),
    name: String(k.name ?? ''),
    email: '',
    phone: '',
    payment_terms: '-',
    status: k.aktiv ? 'active' : (k.sperrgrund ? 'blocked' : 'inactive'),
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

  // Konsolidierter Kundenstamm: Business Partner (Rolle Kunde) + operativer
  // Kundenstamm (public.kunden via kunden_lookup), dedupliziert über die ID.
  const customersQuery = useQuery({
    queryKey: ['kunden-konsolidiert', searchTerm],
    queryFn: async (): Promise<CustomerRow[]> => {
      // BP-Abruf (crm-core) best-effort mit Timeout — der operative Lookup ist
      // die Hauptquelle und darf nicht durch ein langsames crm-core blockiert werden.
      const bpPromise = Promise.race<BusinessPartnerEnvelope[]>([
        businessPartnerService.list({ search: searchTerm || undefined }).catch(() => []),
        new Promise<BusinessPartnerEnvelope[]>((resolve) => setTimeout(() => resolve([]), 4000)),
      ])
      const [bpEnvelopes, lookupRows] = await Promise.all([
        bpPromise,
        apiClient
          .get<Array<Record<string, unknown>>>('/api/v1/crm/customers/lookup', { params: { q: searchTerm || '', limit: 1000 } })
          .then((r) => r.data ?? [])
          .catch(() => [] as Array<Record<string, unknown>>),
      ])
      const bpRows = (bpEnvelopes ?? [])
        .filter((item) => item.business_partner.roles.is_customer)
        .map(mapToRow)
      const seen = new Set(bpRows.map((r) => r.id))
      const lookup = (Array.isArray(lookupRows) ? lookupRows : []).map(mapLookupToRow).filter((r) => !seen.has(r.id))
      return [...bpRows, ...lookup]
    },
  })

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => navigate('/verkauf/kunde/neu'),
    onSearch: () => searchRef.current?.focus(),
    onRefresh: () => { void customersQuery.refetch() },
  })
  useKeyboardShortcuts(shortcuts)

  const customers = useMemo(() => customersQuery.data ?? [], [customersQuery.data])

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
        <button
          onClick={() => navigate(customer.id.includes('-') ? `/verkauf/kunden-stamm/${customer.id}` : '/crm/kunden-schnellauswahl')}
          className="font-medium text-blue-600 hover:underline"
        >
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
          <p className="text-muted-foreground">Konsolidierter Kundenstamm — Business Partner (Rolle Kunde) + operativer Stamm</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/crm/kunden-karte')} className="gap-2">
            <MapPin className="h-4 w-4" />
            Karte
          </Button>
          <Button onClick={() => navigate('/verkauf/kunde/neu')} className="gap-2">
            <Plus className="h-4 w-4" />
            Neuer Kunde
          </Button>
        </div>
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
