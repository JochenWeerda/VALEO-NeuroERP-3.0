import { useEffect, useState } from 'react'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command'

export type Field = {
  name: string
  label: string
  type: 'string' | 'number' | 'date' | 'text' | 'select' | 'lookup' | 'lines'
  required?: boolean
  options?: Array<{ value: string; label: string }>
  placeholder?: string
  min?: number
  max?: number
  lookup?: string
}

export type FieldRendererProps = {
  field: Field
  value: unknown
  onChange: (_value: unknown) => void
}

const DEFAULT_DEBOUNCE_MS = 350

type LookupResultItem = {
  id: string
  label?: string
  name?: string
  hint?: string
}

type LookupProps = {
  value: string
  onChange: (_value: string) => void
  field: Field
}

function LookupField({ value, onChange, field }: LookupProps): JSX.Element {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounced(query)
  const [items, setItems] = useState<LookupResultItem[]>([])

  const entity = field.lookup?.split('/').pop() ?? (field.name.toLowerCase().includes('customer') ? 'customers' : 'articles')
  const baseEndpoint = field.lookup ?? `/api/mcp/lookup/${entity}`

  useEffect(() => {
    let cancelled = false

    const fetchItems = async (): Promise<void> => {
      if (debouncedQuery.trim().length === 0) {
        setItems([])
        return
      }
      try {
        const response = await fetch(`${baseEndpoint}?q=${encodeURIComponent(debouncedQuery)}`)
        const payload = (await response.json()) as { ok: boolean; data?: LookupResultItem[] }
        if (!cancelled) {
          setItems(Array.isArray(payload.data) ? payload.data : [])
        }
      } catch {
        if (!cancelled) {
          setItems([])
        }
      }
    }

    void fetchItems()

    return () => {
      cancelled = true
    }
  }, [baseEndpoint, debouncedQuery])

  const placeholderText = field.placeholder ?? `Suche ${entity}...`

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <div className="flex gap-2">
          <Input
            id={field.name}
            value={value}
            onChange={(event) => onChange(event.target.value)}
            placeholder={placeholderText}
          />
          <Input
            className="max-w-[40%]"
            placeholder="Suche..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
      </PopoverTrigger>
      <PopoverContent className="p-0 w-[var(--radix-popover-trigger-width)]">
        <Command>
          <CommandInput placeholder={`Suchen in ${entity}...`} value={query} onValueChange={setQuery} />
          <CommandList>
            <CommandEmpty>Nichts gefunden</CommandEmpty>
            <CommandGroup>
              {items.map((item) => (
                <CommandItem
                  key={item.id}
                  value={item.id}
                  onSelect={() => {
                    onChange(item.id)
                    setOpen(false)
                  }}
                >
                  <div className="flex flex-col">
                    <span className="font-medium">{item.label ?? item.name ?? item.id}</span>
                    {typeof item.hint === 'string' && item.hint.length > 0 && (
                      <span className="text-xs opacity-70">{item.hint}</span>
                    )}
                  </div>
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

function useDebounced<T>(value: T, delay: number = DEFAULT_DEBOUNCE_MS): T {
  const [debounced, setDebounced] = useState<T>(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debounced
}

export function FieldRenderer({ field, value, onChange }: FieldRendererProps): JSX.Element {
  switch (field.type) {
    case 'text':
      return (
        <Textarea
          id={field.name}
          value={String(value ?? '')}
          onChange={(event) => onChange(event.target.value)}
          placeholder={field.placeholder}
        />
      )
    case 'number':
      return (
        <Input
          id={field.name}
          type="number"
          value={Number(value ?? 0)}
          onChange={(event) => onChange(Number(event.target.value))}
          placeholder={field.placeholder}
          min={field.min}
          max={field.max}
        />
      )
    case 'date':
      return (
        <Input
          id={field.name}
          type="date"
          value={String(value ?? '')}
          onChange={(event) => onChange(event.target.value)}
        />
      )
    case 'select':
      return (
        <Select value={String(value ?? '')} onValueChange={(selected) => onChange(selected)}>
          <SelectTrigger id={field.name}>
            <SelectValue placeholder={field.placeholder ?? 'Bitte waehlen'} />
          </SelectTrigger>
          <SelectContent>
            {field.options?.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )
    case 'lookup':
      return (
        <LookupField
          value={String(value ?? '')}
          onChange={(next) => onChange(next)}
          field={field}
        />
      )
    case 'string':
    default:
      return (
        <Input
          id={field.name}
          value={String(value ?? '')}
          onChange={(event) => onChange(event.target.value)}
          placeholder={field.placeholder}
        />
      )
  }
}
