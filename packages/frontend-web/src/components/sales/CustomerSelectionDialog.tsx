import { useState, useMemo, useEffect } from 'react'
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
import { apiClient } from '@/lib/axios'

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
  const [extendedSearch, setExtendedSearch] = useState(true)
  const [activeTab, setActiveTab] = useState<'all' | 'prospects' | 'active' | 'former'>('active')
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)

  const [customers, setCustomers] = useState<Customer[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [fetchError, setFetchError] = useState<string | null>(null)

  useEffect(() => {
    if (!open) return
    setIsLoading(true)
    setFetchError(null)
    setCustomers([])
    apiClient.get<any>('/api/v1/crm/customers/', { params: { limit: 200 } })
      .then((response) => {
        // axios.ts unwraps response.data directly, so response = { items: [...], total: N }
        let items: any[] = []
        if (Array.isArray(response)) {
          items = response
        } else if (response?.items && Array.isArray(response.items)) {
          items = response.items
        }
        const mapped: Customer[] = items.map((c: any) => ({
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
        setCustomers(mapped)
      })
      .catch((err) => {
        console.error('[CustomerSelectionDialog] Fehler beim Laden:', err)
        setFetchError(err?.message || 'Unbekannter Fehler')
      })
      .finally(() => setIsLoading(false))
  }, [open])

  // Helper function to check if a string matches a pattern (supports * wildcard)
  const matchesPattern = (text: string, pattern: string): boolean => {
    if (!pattern) return true
    // Convert * wildcard to regex pattern
    const regexPattern = pattern
      .replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // Escape special regex chars
      .replace(/\*/g, '.*') // Replace * with .* for regex
    const regex = new RegExp(regexPattern, 'i')
    return regex.test(text)
  }

  const filteredCustomers = useMemo(() => {
    let result = customers

    // Filter by tab (if backend didn't filter already)
    if (activeTab === 'prospects') {
      result = result.filter((c) => c.customer_type === 'prospect' || !c.is_active)
    } else if (activeTab === 'active') {
      result = result.filter((c) => c.is_active !== false)
    } else if (activeTab === 'former') {
      result = result.filter((c) => c.is_active === false)
    }
    // 'all' tab: no additional filtering

    // Apply search filter
    if (!searchTerm) {
      // No search term: return first 10, sorted alphabetically descending
      return result
        .sort((a, b) => b.name.localeCompare(a.name, 'de', { sensitivity: 'base' }))
        .slice(0, 10)
    }

    // Has search term: filter and sort
    const term = searchTerm.toLowerCase()
    const hasWildcard = searchTerm.includes('*')

    if (hasWildcard) {
      // Wildcard search: use pattern matching
      if (extendedSearch) {
        result = result.filter(
          (c) =>
            matchesPattern(c.name, searchTerm) ||
            matchesPattern(c.customerNumber, searchTerm) ||
            matchesPattern(c.debitorAccount, searchTerm) ||
            matchesPattern(c.representative || '', searchTerm) ||
            matchesPattern(c.postalCode || '', searchTerm) ||
            matchesPattern(c.city || '', searchTerm) ||
            matchesPattern(c.customerGroup || '', searchTerm)
        )
      } else {
        result = result.filter(
          (c) =>
            matchesPattern(c.name, searchTerm) ||
            matchesPattern(c.customerNumber, searchTerm) ||
            matchesPattern(c.debitorAccount, searchTerm)
        )
      }
    } else {
      // Normal search: contains match
      if (extendedSearch) {
        result = result.filter(
          (c) => {
            const name = (c.name || c.company_name || '').toLowerCase()
            const customerNumber = (c.customerNumber || '').toLowerCase()
            const debitorAccount = (c.debitorAccount || '').toLowerCase()
            const representative = (c.representative || '').toLowerCase()
            const postalCode = (c.postalCode || '').toLowerCase()
            const city = (c.city || '').toLowerCase()
            const customerGroup = (c.customerGroup || '').toLowerCase()
            
            return name.includes(term) ||
              customerNumber.includes(term) ||
              debitorAccount.includes(term) ||
              representative.includes(term) ||
              postalCode.includes(term) ||
              city.includes(term) ||
              customerGroup.includes(term)
          }
        )
      } else {
        result = result.filter(
          (c) => {
            const name = (c.name || c.company_name || '').toLowerCase()
            const customerNumber = (c.customerNumber || '').toLowerCase()
            const debitorAccount = (c.debitorAccount || '').toLowerCase()
            
            return name.includes(term) ||
              customerNumber.includes(term) ||
              debitorAccount.includes(term)
          }
        )
      }
    }

    // Sort alphabetically descending by name
    const sorted = result.sort((a, b) => b.name.localeCompare(a.name, 'de', { sensitivity: 'base' }))
    
    console.log('[CustomerSelectionDialog] Filtered customers:', {
      inputCount: customers.length,
      afterTabFilter: result.length,
      afterSearchFilter: sorted.length,
      firstThree: sorted.slice(0, 3),
    })
    
    return sorted
  }, [customers, searchTerm, extendedSearch, activeTab])

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
            {isLoading ? (
              <div className="p-4 text-center text-muted-foreground">Lade Kunden...</div>
            ) : fetchError ? (
              <div className="p-4 text-center text-red-600">
                <p>Fehler beim Laden: {fetchError}</p>
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
                        {isLoading ? (
                          'Lade Kunden...'
                        ) : customers.length === 0 ? (
                          <p>Keine Kunden in der Datenbank gefunden.</p>
                        ) : searchTerm ? (
                          `Keine Kunden gefunden für "${searchTerm}"`
                        ) : (
                          <div>
                            <p>Keine Kunden für diesen Filter gefunden.</p>
                            <p className="text-xs mt-2">
                              Tab: {activeTab}, Total: {customers.length} Kunden
                            </p>
                          </div>
                        )}
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

