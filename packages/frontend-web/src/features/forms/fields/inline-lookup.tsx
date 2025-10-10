import React, { useEffect, useState } from "react"
import { Input } from "@/components/ui/input"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"

export function useDebounced<T>(val: T, delay = 350): T {
  const [v, setV] = React.useState(val)
  React.useEffect(() => {
    const t = setTimeout(() => setV(val), delay)
    return () => clearTimeout(t)
  }, [val, delay])
  return v
}

export function InlineArticleLookup({ value, onPick }: { value: string; onPick: (it: any) => void }) {
  const [open, setOpen] = useState(false)
  const [q, setQ] = useState("")
  const dq = useDebounced(q)
  const [items, setItems] = useState<any[]>([])

  useEffect(() => {
    let ig = false
    ;(async () => {
      if (!dq) {
        setItems([])
        return
      }
      const r = await fetch(`/api/mcp/lookup/articles?q=${encodeURIComponent(dq)}`)
      const j = await r.json()
      if (!ig) setItems(j?.data ?? [])
    })()
    return () => { ig = true }
  }, [dq])

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Input
          value={q || value || ""}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Artikel suchen…"
        />
      </PopoverTrigger>
      <PopoverContent className="p-0 w-[var(--radix-popover-trigger-width)]">
        <Command>
          <CommandInput placeholder="Suchen…" />
          <CommandList>
            <CommandEmpty>Nichts gefunden</CommandEmpty>
            <CommandGroup>
              {items.map((it: any) => (
                <CommandItem
                  key={it.id}
                  value={it.id}
                  onSelect={() => {
                    onPick(it)
                    setOpen(false)
                  }}
                >
                  <div className="flex flex-col">
                    <span className="font-medium">
                      {it.label ?? it.id}
                    </span>
                    <span className="text-xs opacity-70">
                      EK {it.cost}{it.price ? ` · Preis ${it.price}` : ''}
                    </span>
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