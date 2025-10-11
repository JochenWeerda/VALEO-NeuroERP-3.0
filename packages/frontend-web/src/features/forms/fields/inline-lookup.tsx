import { useEffect, useMemo, useState } from 'react'
import { Input } from '@/components/ui/input'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'

const DEFAULT_DEBOUNCE_MS = 350

export function useDebounced<T>(value: T, delay: number = DEFAULT_DEBOUNCE_MS): T {
  const [debounced, setDebounced] = useState<T>(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debounced
}

interface InlineArticleLookupProps {
  value: string
  onPick: (item: ArticleLookupItem) => void
}

interface ArticleLookupResponse {
  data?: ArticleLookupItem[]
}

export interface ArticleLookupItem {
  id: string
  label?: string
  cost?: number
  price?: number
}

export function InlineArticleLookup({ value, onPick }: InlineArticleLookupProps): JSX.Element {
  const [open, setOpen] = useState<boolean>(false)
  const [query, setQuery] = useState<string>('')
  const debouncedQuery = useDebounced(query)
  const [items, setItems] = useState<ArticleLookupItem[]>([])

  useEffect(() => {
    let cancelled = false

    const fetchItems = async (): Promise<void> => {
      if (debouncedQuery.trim().length === 0) {
        setItems([])
        return
      }

      const response = await fetch(`/api/mcp/lookup/articles?q=${encodeURIComponent(debouncedQuery)}`)
      const payload = (await response.json()) as ArticleLookupResponse
      if (!cancelled) {
        setItems(Array.isArray(payload.data) ? payload.data : [])
      }
    }

    void fetchItems()

    return () => {
      cancelled = true
    }
  }, [debouncedQuery])

  const inputValue = useMemo(() => {
    if (query.length > 0) {
      return query
    }
    return value
  }, [query, value])

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Input
          value={inputValue}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Artikel suchen..."
        />
      </PopoverTrigger>
      <PopoverContent className="w-[var(--radix-popover-trigger-width)] p-0">
        <Command>
          <CommandInput placeholder="Suchen..." value={query} onValueChange={setQuery} />
          <CommandList>
            <CommandEmpty>Nichts gefunden</CommandEmpty>
            <CommandGroup>
              {items.map((item) => {
                const label = item.label ?? item.id
                const costInfo = item.cost != null ? `EK ${item.cost}` : 'EK n/a'
                const priceInfo = item.price != null ? `VK ${item.price}` : ''

                return (
                  <CommandItem
                    key={item.id}
                    value={item.id}
                    onSelect={() => {
                      onPick(item)
                      setOpen(false)
                    }}
                  >
                    <div className="flex flex-col">
                      <span className="font-medium">{label}</span>
                      <span className="text-xs opacity-70">
                        {costInfo}
                        {priceInfo ? ` - ${priceInfo}` : ''}
                      </span>
                    </div>
                  </CommandItem>
                )
              })}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}
