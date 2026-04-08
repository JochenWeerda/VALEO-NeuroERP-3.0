import { useState, useMemo, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { apiClient } from '@/lib/api-client'

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(handler)
  }, [value, delay])
  return debouncedValue
}

export type Customer = {
  id: string
  customerNumber: string
  name: string
  debitorAccount: string
  representative?: string
  postalCode?: string
  city?: string
  customerGroup?: string
  creditLimit?: string
  paymentTerms?: number    // Zahlungsziel in Tagen
  address?: {
    street?: string
    postalCode?: string
    city?: string
    phone?: string
    fax?: string
  }
  // Backend fields (for mapping)
  company_name?: string
  customer_number?: string
  contact_person?: string
  phone?: string
  email?: string
  address_backend?: string | { street?: string; postal_code?: string; city?: string; phone?: string; fax?: string }
  // Status fields for filtering
  is_active?: boolean
  customer_type?: string
  // Chefanweisung aus Kunden-Stammdaten
  chefanweisung?: string
  executiveNote?: string
}

type CustomerSelectionDialogProps = {
  open: boolean
  onClose: () => void
  onSelect: (customer: Customer) => void
  title?: string
}

export function CustomerSelectionDialog({
  open,
  onClose,
  onSelect,
  title = 'AUSWAHL KUNDEN',
}: CustomerSelectionDialogProps): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const debouncedSearch = useDebounce(searchTerm, 300)
  const [extendedSearch, setExtendedSearch] = useState(true)
  const [activeTab, setActiveTab] = useState<'all' | 'prospects' | 'active' | 'former'>('active')
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)

  const { data: customers = [], isLoading, error: fetchError } = useQuery({
    queryKey: ['crm', 'customers', 'search', debouncedSearch],
    queryFn: async () => {
      const response = await apiClient.get<any>('/api/v1/crm/customers/', {
        params: { search: debouncedSearch, limit: 50 },
      })
      let items: any[] = []
      if (Array.isArray(response)) {
        items = response
      } else if (response?.items && Array.isArray(response.items)) {
        items = response.items
      }
      return items.map((c: any): Customer => ({
        id: c.id,
        customerNumber: c.customer_number || c.customerNumber || '',
        name: (c.company_name || c.name || '').trim(),
        debitorAccount: c.customer_number || c.customerNumber || '',
        representative: c.contact_person || c.representative,
        postalCode: c.postal_code || c.postalCode,
        city: c.city,
        customerGroup: c.customer_group || c.customerGroup,
        creditLimit: c.credit_limit?.toString() || c.creditLimit,
        paymentTerms: c.payment_terms !== undefined ? Number(c.payment_terms) : undefined,
        address: typeof c.address === 'string'
          ? { street: c.address, postalCode: c.postal_code, city: c.city, phone: c.phone, fax: c.fax }
          : c.address || { postalCode: c.postal_code, city: c.city },
        company_name: c.company_name,
        customer_number: c.customer_number,
        contact_person: c.contact_person,
        phone: c.phone,
        email: c.email,
        is_active: c.is_active ?? true,
        customer_type: c.customer_type,
        chefanweisung: c.chefanweisung || c.executive_note,
        executiveNote: c.executive_note || c.chefanweisung,
      }))
    },
    enabled: open && debouncedSearch.length >= 2,
    staleTime: 30_000,
  })

  const filteredCustomers = useMemo(() => {
    let result = customers

    // Filter by tab (lightweight client-side filter on server results)
    if (activeTab === 'prospects') {
      result = result.filter((c) => c.customer_type === 'prospect' || !c.is_active)
    } else if (activeTab === 'active') {
      result = result.filter((c) => c.is_active !== false)
    } else if (activeTab === 'former') {
      result = result.filter((c) => c.is_active === false)
    }

    // Sort alphabetically descending by name
    return result.sort((a, b) => b.name.localeCompare(a.name, 'de', { sensitivity: 'base' }))
  }, [customers, activeTab])

  const handleSelect = (): void => {
    if (selectedCustomer) {
      onSelect(selectedCustomer)
      setSelectedCustomer(null)
      setSearchTerm('')
      onClose()
    }
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 flex-1 overflow-hidden flex flex-col">
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <Label htmlFor="customer-search">Suche:</Label>
              <Input
                id="customer-search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Kunde suchen..."
                autoFocus
              />
            </div>
            <div className="flex items-center space-x-2">
              <Checkbox
                id="extended-search"
                checked={extendedSearch}
                onCheckedChange={(checked) => setExtendedSearch(checked === true)}
              />
              <Label
                htmlFor="extended-search"
                className="text-sm font-normal cursor-pointer"
              >
                Erweitert (Suche zusätzlich nach Vertreter, Plz, Ort, Kundengruppe)
              </Label>
            </div>
          </div>

          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as typeof activeTab)}>
            <TabsList>
              <TabsTrigger value="all">ALLE</TabsTrigger>
              <TabsTrigger value="prospects">INTERESSENTEN</TabsTrigger>
              <TabsTrigger value="active">AKTIVE KUNDEN</TabsTrigger>
              <TabsTrigger value="former">EHEMALIGE KUNDEN</TabsTrigger>
            </TabsList>
          </Tabs>

          <div className="flex-1 overflow-auto border rounded">
            {debouncedSearch.length < 2 ? (
              <div className="p-4 text-center text-muted-foreground">
                Mindestens 2 Zeichen eingeben, um Kunden zu suchen...
              </div>
            ) : isLoading ? (
              <div className="p-4 text-center text-muted-foreground">Lade Kunden...</div>
            ) : fetchError ? (
              <div className="p-4 text-center text-red-600">
                <p>Fehler beim Laden: {fetchError instanceof Error ? fetchError.message : 'Unbekannter Fehler'}</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Kunden-Nr.</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Debitor-Kto.</TableHead>
                    <TableHead>Vertreter</TableHead>
                    <TableHead>Plz</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredCustomers.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-muted-foreground">
                        {`Keine Kunden gefunden für "${debouncedSearch}"`}
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredCustomers.map((customer) => (
                      <TableRow
                        key={customer.id}
                        className={selectedCustomer?.id === customer.id ? 'bg-muted' : 'cursor-pointer'}
                        onClick={() => setSelectedCustomer(customer)}
                      >
                        <TableCell>{customer.customerNumber}</TableCell>
                        <TableCell>{customer.name}</TableCell>
                        <TableCell>{customer.debitorAccount}</TableCell>
                        <TableCell>{customer.representative || '-'}</TableCell>
                        <TableCell>{customer.postalCode || '-'}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            )}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Checkbox id="search-delivery-address" />
              <Label htmlFor="search-delivery-address" className="text-sm font-normal cursor-pointer">
                Suche nach Lief.-Adresse
              </Label>
              <Button variant="outline" size="sm">
                Neu
              </Button>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Abbrechen
          </Button>
          <Button onClick={handleSelect} disabled={!selectedCustomer}>
            OK
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

