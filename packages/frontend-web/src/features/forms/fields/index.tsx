import * as React from "react"
import { useEffect, useState } from "react"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"

type Field = {
  name: string
  label: string
  type: "string" | "number" | "date" | "text" | "select" | "lookup" | "lines"
  required?: boolean
  options?: Array<{ value: string; label: string }>
  placeholder?: string
  min?: number
  max?: number
  lookup?: string
}

type Props = {
  field: Field
  value: unknown
  onChange: (v: unknown) => void
}

export function FieldRenderer({ field, value, onChange }: Props): JSX.Element {
  // Textarea
  if (field.type === "text") {
    return (
      <Textarea
        id={field.name}
        value={String(value ?? "")}
        onChange={(e): void => {
          onChange(e.target.value)
        }}
        placeholder={field.placeholder}
      />
    )
  }

  // Number
  if (field.type === "number") {
    return (
      <Input
        id={field.name}
        type="number"
        value={Number(value ?? 0)}
        onChange={(e): void => {
          onChange(Number(e.target.value))
        }}
        placeholder={field.placeholder}
        min={field.min}
        max={field.max}
      />
    )
  }

  // Date
  if (field.type === "date") {
    return (
      <Input
        id={field.name}
        type="date"
        value={String(value ?? "")}
        onChange={(e): void => {
          onChange(e.target.value)
        }}
      />
    )
  }

  // Select (Dropdown)
  if (field.type === "select") {
    return (
      <Select
        value={String(value ?? "")}
        onValueChange={(v): void => {
          onChange(v)
        }}
      >
        <SelectTrigger id={field.name}>
          <SelectValue placeholder={field.placeholder ?? "Bitte wählen"} />
        </SelectTrigger>
        <SelectContent>
          {field.options?.map(
            (o): JSX.Element => (
              <SelectItem key={o.value} value={o.value}>
                {o.label}
              </SelectItem>
            )
          )}
        </SelectContent>
      </Select>
    )
  }

  // Lookup (mit Debounce-Suche)
  if (field.type === "lookup") {
    return (
      <LookupField
        id={field.name}
        value={String(value ?? "")}
        onChange={onChange}
        lookupUrl={field.lookup ?? ""}
        placeholder={field.placeholder}
        field={field}
      />
    )
  }

  // Default: String
  return (
    <Input
      id={field.name}
      value={String(value ?? "")}
      onChange={(e: React.ChangeEvent<HTMLInputElement>): void => {
        onChange(e.target.value)
      }}
      placeholder={field.placeholder}
    />
  )
}

const DEFAULT_DEBOUNCE_MS = 500
const LOOKUP_DEBOUNCE_MS = 400

/**
 * Debounce Hook
 */
function useDebounced<T>(val: T, delay = DEFAULT_DEBOUNCE_MS): T {
  const [v, setV] = useState(val)
  useEffect(() => {
    const t = setTimeout(() => {
      setV(val)
    }, delay)
    return (): void => {
      clearTimeout(t)
    }
  }, [val, delay])
  return v
}

/**
 * Lookup-Field mit Command/Popover und Debounce
 */
type LookupProps = {
  id: string
  value: string
  onChange: (v: unknown) => void
  lookupUrl: string
  placeholder?: string
  field: Field
}

function LookupField({ id, value, onChange, lookupUrl, placeholder, field }: LookupProps): JSX.Element {
  const [open, setOpen] = useState(false)
  const [q, setQ] = useState("")
  const dq = useDebounced(q, LOOKUP_DEBOUNCE_MS)
  const [items, setItems] = useState<
    Array<{ id: string; label?: string; name?: string; hint?: string }>
  >([])

  const entity =
    field.lookup?.split("/").pop() ??
    (field.name?.toLowerCase().includes("customer") ? "customers" : "articles")

  useEffect(() => {
    let ignore = false
    async function run(): Promise<void> {
      if (dq.length === 0) {
        setItems([])
        return
      }
      try {
        const res = await fetch(
          `/api/mcp/lookup/${entity}?q=${encodeURIComponent(dq)}`
        )
        const js = (await res.json()) as {
          ok: boolean
          data: Array<{ id: string; label?: string; name?: string; hint?: string }>
        }
        if (!ignore) {
          setItems(js?.data ?? [])
        }
      } catch {
        if (!ignore) {
          setItems([])
        }
      }
    }
    void run()
    return (): void => {
      ignore = true
    }
  }, [dq, entity])

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <div className="flex gap-2">
          <Input
            id={field.name}
            value={String(value ?? "")}
            onChange={(e): void => {
              onChange(e.target.value)
            }}
            placeholder={field.placeholder ?? `Suche ${entity}…`}
          />
          <Input
            className="max-w-[40%]"
            placeholder="Suche…"
            value={q}
            onChange={(e): void => {
              setQ(e.target.value)
            }}
          />
        </div>
      </PopoverTrigger>
      <PopoverContent className="p-0 w-[var(--radix-popover-trigger-width)]">
        <Command>
          <CommandInput placeholder={`Suchen in ${entity}…`} />
          <CommandList>
            <CommandEmpty>Nichts gefunden</CommandEmpty>
            <CommandGroup>
              {items.map(
                (it): JSX.Element => (
                  <CommandItem
                    key={it.id}
                    value={it.id}
                    onSelect={(): void => {
                      onChange(it.id)
                      setOpen(false)
                    }}
                  >
                    <div className="flex flex-col">
                      <span className="font-medium">
                        {it.label ?? it.name ?? it.id}
                      </span>
                      {it.hint !== undefined && (
                        <span className="text-xs opacity-70">{it.hint}</span>
                      )}
                    </div>
                  </CommandItem>
                )
              )}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

