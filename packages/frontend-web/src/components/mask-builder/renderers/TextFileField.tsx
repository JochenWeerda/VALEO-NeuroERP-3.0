import { useEffect, useRef, useState } from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { ScreenFieldDefinition } from '../schema'

/** File contents, not a local path or an opaque File, enter the versioned command. */
export function TextFileField({ field, value, readOnly, onChange }: {
  field: ScreenFieldDefinition
  value: unknown
  readOnly: boolean
  onChange?: (value: unknown) => void
}): JSX.Element {
  const sequence = useRef(0)
  const [error, setError] = useState('')
  const [reading, setReading] = useState(false)
  useEffect(() => () => { sequence.current += 1 }, [])
  const policy = field.fileContent
  const valid = policy?.encoding === 'utf-8' && Number.isInteger(policy.maxBytes)
    && policy.maxBytes > 0 && policy.maxBytes <= 1048576 && ['.csv', '.txt', '.json'].includes(policy.accept)
  return <div className="space-y-2">
    <Label htmlFor={field.key}>{field.label}{field.required ? ' *' : ''}</Label>
    {!readOnly && <Input id={field.key} type="file" accept={policy?.accept} disabled={!valid}
      aria-label={field.label} aria-invalid={Boolean(error)} aria-describedby={`${field.key}-file-help`}
      onChange={async event => {
        const request = ++sequence.current
        const file = event.target.files?.[0]
        onChange?.(undefined)
        setError('')
        if (!file || !valid || !policy) { setReading(false); return }
        setReading(true)
        try {
          if (file.size === 0 || file.size > policy.maxBytes) throw new Error(`Datei muss zwischen 1 und ${policy.maxBytes} Bytes groß sein.`)
          const content = new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer())
          if (content.includes('\0')) throw new Error('Die Datei enthält ungültige Nullzeichen.')
          if (request === sequence.current) onChange?.(content)
        } catch (failure) {
          if (request === sequence.current) setError(failure instanceof Error ? failure.message : 'Datei konnte nicht gelesen werden.')
        } finally {
          if (request === sequence.current) setReading(false)
        }
      }} />}
    <p id={`${field.key}-file-help`} className="text-xs text-muted-foreground">{field.helpText ?? 'UTF-8-Textdatei. Inhalt vor der Ausführung prüfen.'}</p>
    {!valid && <p role="alert" className="text-sm text-destructive">Der Dateivertrag ist ungültig.</p>}
    {reading && <p role="status">Datei wird gelesen…</p>}
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    {typeof value === 'string' && <pre aria-label="Dateivorschau" className="max-h-48 overflow-auto whitespace-pre-wrap rounded border border-border bg-muted p-3 text-xs text-foreground">{value.slice(0, 4096)}{value.length > 4096 ? '\n… Vorschau gekürzt; der vollständige Inhalt wird geprüft.' : ''}</pre>}
  </div>
}
