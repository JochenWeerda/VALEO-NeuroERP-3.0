import { memo, useEffect, useState } from 'react'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { useLookupSearch } from '../hooks/useLookupSearch'
import type { RenderFieldPlan } from '../render-plan/types'

export const LookupField = memo(function LookupField({
  field,
  value,
  lookupEndpoint,
  performance,
  onSelect,
}: {
  field: RenderFieldPlan
  value: unknown
  lookupEndpoint?: string
  performance?: {
    lookupMinChars?: number
    lookupResultLimit?: number
    lookupCacheTtlMs?: number
    lookupDebounceMs?: number
  }
  onSelect?: (_value: string, _item: { value: string; label: string }) => void
}): JSX.Element {
  const [query, setQuery] = useState('')
  const [picked, setPicked] = useState<{ value: string; label: string; endpoint?: string } | null>(null)
  const displayValue = value == null || value === '' ? '' : String(value)
  useEffect(() => {
    setQuery('')
    setPicked(current => current?.value === displayValue && current.endpoint === lookupEndpoint ? current : null)
  }, [displayValue, lookupEndpoint])
  const minChars = field.minSearchChars ?? performance?.lookupMinChars ?? 2
  const search = useLookupSearch({
    endpoint: lookupEndpoint,
    query,
    minChars,
    limit: performance?.lookupResultLimit ?? 25,
    cacheTtlMs: performance?.lookupCacheTtlMs ?? 900_000,
    debounceMs: performance?.lookupDebounceMs ?? 300,
    enabled: !field.readOnly && Boolean(lookupEndpoint),
  })

  const inputValue = field.readOnly
    ? displayValue
    : query.length > 0
      ? query
      : (picked?.label ?? displayValue)

  return (
    <div className="space-y-2">
      <Label htmlFor={field.key}>{field.label}</Label>
      <Input
        id={field.key}
        value={inputValue}
        placeholder={field.placeholder}
        readOnly={field.readOnly}
        aria-label={field.label}
        aria-autocomplete="list"
        aria-controls={!field.readOnly ? `lookup-results-${field.key}` : undefined}
        onChange={(event) => {
          if (field.readOnly) return
          setPicked(null)
          setQuery(event.target.value)
        }}
      />
      {!field.readOnly && query.length > 0 && query.length < minChars ? (
        <p className="text-xs text-muted-foreground">
          Mindestens {minChars} Zeichen fuer die Suche eingeben.
        </p>
      ) : null}
      {!field.readOnly && search.data && search.data.length > 0 ? (
        <ul
          id={`lookup-results-${field.key}`}
          role="listbox"
          aria-label={`${field.label} Treffer`}
          className="max-h-56 overflow-y-auto rounded border border-border"
          data-testid={`lookup-results-${field.key}`}
        >
          {search.data.map((item) => (
            <li key={item.value} role="none">
              <button
                type="button"
                role="option"
                className="flex min-h-touch w-full items-center px-3 py-2 text-left text-sm hover:bg-accent"
                onClick={() => {
                  setQuery('')
                  setPicked({ ...item, endpoint: lookupEndpoint })
                  onSelect?.(item.value, item)
                }}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      {field.helpText ? <p className="text-xs text-muted-foreground">{field.helpText}</p> : null}
    </div>
  )
})
