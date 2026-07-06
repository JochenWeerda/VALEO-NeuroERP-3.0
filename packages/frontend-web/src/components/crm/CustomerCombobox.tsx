import { useEffect, useMemo, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Check, ChevronsUpDown, Loader2, Plus, Search, UserRoundPlus, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { apiClient } from '@/lib/api-client'
import { cn } from '@/lib/utils'

export type CustomerLite = {
  id: string
  customer_number: string
  company_name: string
  city?: string | null
  postal_code?: string | null
  is_active?: boolean
}

export type CustomerComboboxProps = {
  value: CustomerLite | null
  onChange: (customer: CustomerLite | null) => void
  onCreateNew?: (initialName: string) => void
  onOpenAdvanced?: () => void
  placeholder?: string
  disabled?: boolean
  autoFocus?: boolean
  id?: string
}

function useDebounced<T>(value: T, delay = 250): T {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debounced
}

async function fetchQuickSearch(q: string, signal?: AbortSignal): Promise<CustomerLite[]> {
  const response = await apiClient.get<CustomerLite[]>('/api/v1/crm/customers/quick-search', {
    params: { q, limit: 8 },
    signal,
  })
  return Array.isArray(response.data) ? response.data : []
}

async function fetchRecent(signal?: AbortSignal): Promise<CustomerLite[]> {
  const response = await apiClient.get<CustomerLite[]>('/api/v1/crm/customers/recent', {
    params: { limit: 8 },
    signal,
  })
  return Array.isArray(response.data) ? response.data : []
}

function formatLocation(customer: CustomerLite): string {
  const parts = [customer.postal_code, customer.city].filter(Boolean)
  return parts.join(' ')
}

export function CustomerCombobox({
  value,
  onChange,
  onCreateNew,
  onOpenAdvanced,
  placeholder = 'Kunde suchen (Name oder Nummer) ...',
  disabled,
  autoFocus,
  id,
}: CustomerComboboxProps): JSX.Element {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounced(query, 250)
  const triggerRef = useRef<HTMLButtonElement>(null)

  const recentQuery = useQuery({
    queryKey: ['crm', 'customers', 'recent'],
    queryFn: ({ signal }) => fetchRecent(signal),
    staleTime: 60_000,
    enabled: open && debouncedQuery.trim().length < 2,
  })

  const searchQuery = useQuery({
    queryKey: ['crm', 'customers', 'quick-search', debouncedQuery],
    queryFn: ({ signal }) => fetchQuickSearch(debouncedQuery, signal),
    staleTime: 30_000,
    enabled: open && debouncedQuery.trim().length >= 2,
  })

  const isSearching = debouncedQuery.trim().length >= 2
  const activeQuery = isSearching ? searchQuery : recentQuery
  const results = activeQuery.data ?? []
  const isLoading = activeQuery.isLoading || activeQuery.isFetching
  const loadError = activeQuery.error

  const groupHeading = useMemo(() => {
    if (isSearching) return `Treffer (${results.length})`
    return results.length > 0 ? 'Zuletzt verwendet' : 'Kunden'
  }, [isSearching, results.length])

  const emptyHint = useMemo(() => {
    if (isLoading) return 'Lade ...'
    if (loadError) return 'Fehler beim Laden.'
    if (isSearching) return `Kein Kunde zu "${debouncedQuery}" gefunden.`
    return 'Noch keine Kunden im Mandanten.'
  }, [debouncedQuery, isLoading, isSearching, loadError])

  const handleSelect = (customer: CustomerLite): void => {
    onChange(customer)
    setOpen(false)
    setQuery('')
  }

  const handleClear = (event: React.MouseEvent): void => {
    event.stopPropagation()
    onChange(null)
    setQuery('')
  }

  const displayLabel = value
    ? `${value.company_name}${value.customer_number ? ` - ${value.customer_number}` : ''}`
    : ''

  return (
    <div className="w-full">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            ref={triggerRef}
            id={id}
            type="button"
            variant="outline"
            role="combobox"
            aria-expanded={open}
            disabled={disabled}
            autoFocus={autoFocus}
            className={cn(
              'w-full justify-between font-normal hover:bg-muted hover:text-foreground',
              value ? 'text-foreground' : 'text-muted-foreground',
            )}
          >
            <span className="flex min-w-0 items-center gap-2 truncate">
              <Search className="h-4 w-4 shrink-0 opacity-60" />
              <span className="truncate">{value ? displayLabel : placeholder}</span>
            </span>
            <span className="flex items-center gap-1">
              {value ? (
                <span
                  role="button"
                  tabIndex={-1}
                  onClick={handleClear}
                  className="rounded p-0.5 text-muted-foreground hover:bg-muted hover:text-foreground"
                  aria-label="Auswahl entfernen"
                >
                  <X className="h-3.5 w-3.5" />
                </span>
              ) : null}
              <ChevronsUpDown className="h-4 w-4 shrink-0 opacity-50" />
            </span>
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-[--radix-popover-trigger-width] p-0" align="start">
          <Command shouldFilter={false}>
            <CommandInput
              value={query}
              onValueChange={setQuery}
              placeholder="Name oder Kundennummer eingeben ..."
              autoFocus
            />
            <CommandList>
              {results.length === 0 ? (
                <CommandEmpty>
                  <div className="flex flex-col items-center gap-2 px-3 py-4 text-sm text-muted-foreground">
                    {isLoading ? (
                      <span className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" /> Lade ...
                      </span>
                    ) : (
                      <span>{emptyHint}</span>
                    )}
                    {onCreateNew ? (
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => {
                          setOpen(false)
                          onCreateNew(debouncedQuery.trim())
                        }}
                      >
                        <UserRoundPlus className="mr-2 h-4 w-4" />
                        {isSearching ? `"${debouncedQuery}" als neuen Kunden anlegen` : 'Neuen Kunden anlegen'}
                      </Button>
                    ) : null}
                  </div>
                </CommandEmpty>
              ) : (
                <CommandGroup heading={groupHeading}>
                  {results.map((customer) => (
                    <CommandItem
                      key={customer.id}
                      value={`${customer.customer_number} ${customer.company_name}`}
                      onSelect={() => handleSelect(customer)}
                      className="gap-2"
                    >
                      <Check
                        className={cn(
                          'h-4 w-4 shrink-0',
                          value?.id === customer.id ? 'opacity-100' : 'opacity-0',
                        )}
                      />
                      <div className="flex min-w-0 flex-1 flex-col">
                        <div className="flex items-center gap-2 truncate">
                          <span className="truncate font-medium">{customer.company_name || '(ohne Name)'}</span>
                          {customer.is_active === false ? (
                            <span className="rounded bg-muted px-1 text-[10px] uppercase text-muted-foreground">
                              inaktiv
                            </span>
                          ) : null}
                        </div>
                        <div className="truncate text-xs text-muted-foreground">
                          {customer.customer_number}
                          {formatLocation(customer) ? ` - ${formatLocation(customer)}` : ''}
                        </div>
                      </div>
                    </CommandItem>
                  ))}
                </CommandGroup>
              )}

              {(onCreateNew || onOpenAdvanced) && results.length > 0 ? (
                <>
                  <CommandSeparator />
                  <CommandGroup>
                    {onCreateNew ? (
                      <CommandItem
                        value="__create_new__"
                        onSelect={() => {
                          setOpen(false)
                          onCreateNew(debouncedQuery.trim())
                        }}
                        className="gap-2 text-primary"
                      >
                        <Plus className="h-4 w-4" />
                        <span>
                          {isSearching && debouncedQuery
                            ? `"${debouncedQuery}" als neuen Kunden anlegen`
                            : 'Neuen Kunden anlegen'}
                        </span>
                      </CommandItem>
                    ) : null}
                    {onOpenAdvanced ? (
                      <CommandItem
                        value="__advanced_search__"
                        onSelect={() => {
                          setOpen(false)
                          onOpenAdvanced()
                        }}
                        className="gap-2"
                      >
                        <Search className="h-4 w-4" />
                        <span>Erweiterte Suche ...</span>
                      </CommandItem>
                    ) : null}
                  </CommandGroup>
                </>
              ) : null}
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  )
}

export default CustomerCombobox
