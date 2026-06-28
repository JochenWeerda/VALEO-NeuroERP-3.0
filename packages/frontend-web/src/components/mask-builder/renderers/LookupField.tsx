import { memo, useState } from 'react'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { useLookupSearch } from '../hooks/useLookupSearch'
import type { RenderFieldPlan } from '../render-plan/types'

export const LookupField = memo(function LookupField({
  field,
  value,
  lookupEndpoint,
  performance,
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
}): JSX.Element {
  const [query, setQuery] = useState('')
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

  const displayValue = value == null || value === '' ? '' : String(value)

  return (
    <div className="space-y-2">
      <Label htmlFor={field.key}>{field.label}</Label>
      <Input
        id={field.key}
        value={field.readOnly ? displayValue : query || displayValue}
        placeholder={field.placeholder}
        readOnly={field.readOnly}
        aria-label={field.label}
        onChange={(event) => {
          if (!field.readOnly) setQuery(event.target.value)
        }}
      />
      {!field.readOnly && query.length > 0 && query.length < minChars ? (
        <p className="text-xs text-muted-foreground">
          Mindestens {minChars} Zeichen fuer die Suche eingeben.
        </p>
      ) : null}
      {!field.readOnly && search.data && search.data.length > 0 ? (
        <ul className="max-h-40 overflow-y-auto rounded border text-sm" data-testid={`lookup-results-${field.key}`}>
          {search.data.map((item) => (
            <li key={item.value} className="border-b px-2 py-1 last:border-b-0">
              {item.label}
            </li>
          ))}
        </ul>
      ) : null}
      {field.helpText ? <p className="text-xs text-muted-foreground">{field.helpText}</p> : null}
    </div>
  )
})
