import { useState, useMemo } from 'react'
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
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { apiClient } from '@/lib/axios'
import { queryKeys } from '@/lib/query'

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
}

export function CustomerSelectionDialog({
  open,
  onClose,
  onSelect,
}: CustomerSelectionDialogProps): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [extendedSearch, setExtendedSearch] = useState(true)
  const [activeTab, setActiveTab] = useState<'all' | 'prospects' | 'active' | 'former'>('active')
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null)

  const { data: customersData, isLoading, error } = useQuery({
    queryKey: ['customers', 'all'], // Load all customers once, filter client-side
    queryFn: async () => {
      const params = new URLSearchParams()
      // Always load ALL customers without search filter
      // We'll do client-side filtering for better UX (no API calls on every keystroke)
      // Note: API only supports: tenant_id, skip, limit, search
      // - No is_active filter (we'll filter in frontend)
      // - No customer_type filter (we'll filter in frontend)
      // - No sort/order parameters (we'll sort in frontend)
      
      // Get enough results for filtering and sorting
      params.append('limit', '200')
      
      // eslint-disable-next-line no-console
      console.log('[CustomerSelectionDialog] Fetching customers with params:', params.toString())
      
      try {
        const response = await apiClient.get<any>('/api/v1/crm/customers', { params })
        // eslint-disable-next-line no-console
        console.log('[CustomerSelectionDialog] API Response (raw):', response)
        
        // Handle different response structures
        // apiClient.get already returns response.data, so response is already the PaginatedResponse
        let items: any[] = []
        if (Array.isArray(response)) {
          // Direct array response (unlikely but possible)
          items = response
        } else if (response?.items && Array.isArray(response.items)) {
          // PaginatedResponse structure: { items: [...], total: ..., page: ..., ... }
          // This is the expected structure from /api/v1/crm/customers
          items = response.items
        } else if (response?.data) {
          // Nested structure: { data: { items: [...] } } or { data: [...] }
          if (Array.isArray(response.data)) {
            items = response.data
          } else if (response.data.items && Array.isArray(response.data.items)) {
            items = response.data.items
          }
        }
        
        // If still no items, try to find any array in the response
        if (items.length === 0 && response) {
          // eslint-disable-next-line no-console
          console.warn('[CustomerSelectionDialog] No items found in expected structure, searching response:', Object.keys(response))
          // Try to find any array property
          for (const key of Object.keys(response)) {
            if (Array.isArray((response as any)[key])) {
              // eslint-disable-next-line no-console
              console.warn(`[CustomerSelectionDialog] Found array in key "${key}":`, (response as any)[key])
              items = (response as any)[key]
              break
            }
          }
        }
        
        // eslint-disable-next-line no-console
        console.log('[CustomerSelectionDialog] Extracted items:', {
          itemsCount: items.length,
          firstItem: items[0],
          allItems: items,
        })
        
        // Map backend customer format to frontend format
        const mapped = items.map((c: any) => ({
        id: c.id,
        customerNumber: c.customer_number || c.customerNumber || '',
        name: (c.company_name || c.name || '').trim(), // Prefer company_name (backend field) over name, trim whitespace
        debitorAccount: c.customer_number || c.customerNumber || '', // Use customer_number as debitor account
        representative: c.contact_person || c.representative,
        postalCode: c.postal_code || c.postalCode,
        city: c.city,
        customerGroup: c.customer_group || c.customerGroup,
        creditLimit: c.credit_limit?.toString() || c.creditLimit,
        address: typeof c.address === 'string' 
          ? { street: c.address, postalCode: c.postal_code, city: c.city, phone: c.phone, fax: c.fax }
          : c.address || { street: c.address_backend, postalCode: c.postal_code, city: c.city, phone: c.phone, fax: c.fax },
        // Keep backend fields for reference
        company_name: c.company_name,
        customer_number: c.customer_number,
        contact_person: c.contact_person,
        phone: c.phone,
        email: c.email,
        address_backend: c.address,
        // Add status fields for filtering
        is_active: c.is_active ?? true,
        customer_type: c.customer_type,
        // Chefanweisung aus Backend
        chefanweisung: c.chefanweisung || c.executive_note || c.executiveNote,
        executiveNote: c.executive_note || c.executiveNote || c.chefanweisung,
      }))
        
        // eslint-disable-next-line no-console
        console.log('[CustomerSelectionDialog] Mapped customers:', mapped.length, 'items', mapped.slice(0, 3))
        return mapped
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('[CustomerSelectionDialog] Error fetching customers:', err)
        throw err
      }
    },
    enabled: open,
    staleTime: 30_000,
    retry: (failureCount, error: any) => {
      // Don't retry on 401 errors
      if (error?.response?.status === 401) {
        return false
      }
      return failureCount < 3
    },
    // Don't throw errors - handle them gracefully
    throwOnError: false,
  })

  const customers = customersData || []
  
  // eslint-disable-next-line no-console
  console.log('[CustomerSelectionDialog] State:', {
    customersData,
    customersCount: customers.length,
    isLoading,
    error,
    activeTab,
    searchTerm,
  })

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
    
    // eslint-disable-next-line no-console
    console.log('[CustomerSelectionDialog] Filtered customers:', {
      inputCount: customers.length,
      afterTabFilter: result.length,
      afterSearchFilter: sorted.length,
      firstThree: sorted.slice(0, 3),
    })
    
    return sorted
  }, [customers, searchTerm, extendedSearch, activeTab])

  const columns = [
    {
      key: 'customerNumber' as const,
      label: 'Kunden-Nr.',
    },
    {
      key: 'name' as const,
      label: 'Name',
    },
    {
      key: 'debitorAccount' as const,
      label: 'Debitor-Kto.',
    },
    {
      key: 'representative' as const,
      label: 'Vertreter',
    },
    {
      key: 'postalCode' as const,
      label: 'Plz',
    },
  ]

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
          <DialogTitle>AUSWAHL KUNDEN</DialogTitle>
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
            ) : error ? (
              <div className="p-4 text-center text-red-600">
                <p>Fehler beim Laden: {error instanceof Error ? error.message : 'Unbekannter Fehler'}</p>
                {/* eslint-disable-next-line no-console */}
                {console.error('[CustomerSelectionDialog] Query error:', error)}
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
                          <div>
                            <p>Keine Kunden in der Datenbank gefunden.</p>
                            <p className="text-xs mt-2">
                              Debug: customersData={customersData ? 'exists' : 'undefined'}, 
                              customers.length={customers.length}
                            </p>
                          </div>
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

