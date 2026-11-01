import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { ScreenFieldDefinition } from '../schema'
import { readTextFile, validTextFileContract, validTextFileValue } from '../runtime/text-file-contract'

/** Reads a bounded local text file; the form submits only after successful decoding. */
export function TextFileField({ field, value, onChange }: {
  field: ScreenFieldDefinition
  value: unknown
  onChange?: (value: unknown) => void
}): JSX.Element {
  const [error, setError] = useState('')
  const [reading, setReading] = useState(false)
  const sequence = useRef(0)
  const pending = useRef(false)
  const input = useRef<HTMLInputElement>(null)
  const readOnly = Boolean(field.readOnly || !onChange)
  const contract = field.fileContent
  const signature = JSON.stringify(contract)
  useEffect(() => {
    sequence.current += 1
    pending.current = false
    setReading(false)
    setError('')
    return () => { sequence.current += 1 }
  }, [signature, readOnly, field.key])
  useEffect(() => {
    // A reset replaces the transient null marker; its late read must not win.
    if (pending.current && value !== null) {
      sequence.current += 1
      pending.current = false
      setReading(false)
      setError('')
    }
  }, [value])
  if (!validTextFileContract(contract, field.type)) return <p role="alert">{field.label}: Die Dateivorgaben sind ungültig.</p>

  function clear(): void {
    sequence.current += 1
    pending.current = false
    setReading(false)
    setError('')
    if (input.current) input.current.value = ''
    onChange?.('')
  }

  async function select(file: File | undefined): Promise<void> {
    if (readOnly || !onChange) return
    if (!validTextFileContract(contract, field.type)) return
    if (!file) { clear(); return }
    const current = ++sequence.current
    pending.current = true
    setError('')
    setReading(true)
    onChange(null)
    try {
      const text = await readTextFile(file, contract)
      if (current === sequence.current) {
        pending.current = false
        onChange(text)
      }
    } catch (reason) {
      if (current === sequence.current) setError(reason instanceof Error ? reason.message : 'Die Datei konnte nicht gelesen werden.')
    } finally {
      if (current === sequence.current) {
        pending.current = false
        setReading(false)
      }
    }
  }

  return <div className="space-y-2">
    <Label htmlFor={field.key}>{field.label}{field.required ? ' *' : ''}</Label>
    <Input ref={input} id={field.key} type="file" accept={contract.accept.join(',')} disabled={readOnly}
      aria-label={field.label} aria-invalid={Boolean(error)} aria-describedby={`${field.key}-file-help${error ? ` ${field.key}-file-error` : ''}`}
      onChange={event => { void select(event.target.files?.[0]) }} />
    <p id={`${field.key}-file-help`} className="text-sm text-muted-foreground">UTF-8 · {contract.accept.join(', ')} · maximal {contract.maxBytes} Bytes{field.helpText ? ` · ${field.helpText}` : ''}</p>
    {reading && <p role="status">Datei wird gelesen…</p>}
    {!reading && typeof value === 'string' && value.length > 0 && validTextFileValue(field, value) && <p role="status">Textdatei geladen.</p>}
    {error && <p id={`${field.key}-file-error`} role="alert" className="text-sm text-status-error">{error}</p>}
    {!readOnly && <Button type="button" variant="outline" onClick={clear}>Dateiauswahl leeren</Button>}
  </div>
}
