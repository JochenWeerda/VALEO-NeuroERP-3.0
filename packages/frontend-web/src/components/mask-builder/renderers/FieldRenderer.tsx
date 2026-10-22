import { type ChangeEvent, useMemo, useRef } from 'react'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { NativeSelect } from '@/components/ui/native-select'
import type { ScreenFieldDefinition } from '../schema'
import { renderValue } from './render-utils'
import { statusLabel } from './status-labels'
import { VoiceBar } from './VoiceBar'
import { createDefaultSttProvider, type SttProvider } from '@/lib/voice/stt-provider'

const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})/

/** Mehrfachauswahl-Wert als Liste (auch aus einem kommagetrennten Altwert). */
function alsListe(value: unknown): string[] {
  if (Array.isArray(value)) return value.map(String)
  return renderValue(value).split(',').map((teil) => teil.trim()).filter(Boolean)
}

/**
 * Anzeige eines Nur-Lese-Werts im deutschen Format. Ohne Formatregel oder bei
 * unlesbarem Wert bleibt der Rohwert stehen, damit nichts verschluckt wird.
 */
export function formatReadOnlyValue(type: ScreenFieldDefinition['type'], value: unknown): string {
  const raw = renderValue(value)
  if (raw === '') return ''
  const number = Number(raw)
  switch (type) {
    case 'currency':
      return Number.isFinite(number)
        ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(number)
        : raw
    case 'number':
      return Number.isFinite(number) ? new Intl.NumberFormat('de-DE').format(number) : raw
    case 'percentage':
      return Number.isFinite(number) ? `${new Intl.NumberFormat('de-DE').format(number)} %` : raw
    case 'date': {
      // Parsed by hand: `new Date('2026-09-15')` is UTC midnight and can shift a day in local time.
      const match = ISO_DATE.exec(raw)
      return match ? `${match[3]}.${match[2]}.${match[1]}` : raw
    }
    case 'datetime': {
      const date = new Date(raw)
      return Number.isNaN(date.getTime()) ? raw : date.toLocaleString('de-DE')
    }
    case 'boolean':
      if (raw === 'true') return 'Ja'
      if (raw === 'false') return 'Nein'
      return raw
    default:
      return raw
  }
}

export function FieldRenderer({
  field,
  value,
  onChange,
  voiceEnabled = true,
  voiceProvider,
}: {
  field: ScreenFieldDefinition
  value: unknown
  onChange?: (_value: unknown) => void
  voiceEnabled?: boolean
  voiceProvider?: SttProvider | null
}): JSX.Element {
  const isReadOnly = field.readOnly || !onChange
  const inputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const provider = useMemo(() => voiceProvider ?? createDefaultSttProvider(), [voiceProvider])
  const canDictate = voiceEnabled && !isReadOnly && (field.type === 'text' || field.type === 'textarea')

  function handleVoiceCommit(text: string): void {
    if (!onChange) return
    const current = renderValue(value)
    const element = textareaRef.current ?? inputRef.current
    const start = element?.selectionStart ?? current.length
    const end = element?.selectionEnd ?? start
    const next = `${current.slice(0, start)}${text}${current.slice(end)}`
    onChange(next)
    window.requestAnimationFrame(() => {
      const cursor = start + text.length
      element?.focus()
      element?.setSelectionRange(cursor, cursor)
    })
  }

  const commonProps = {
    id: field.key,
    value: renderValue(value),
    placeholder: field.placeholder,
    readOnly: isReadOnly,
    'aria-label': field.label,
    onChange: onChange
      ? (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => onChange(e.target.value)
      : undefined,
  }

  if (field.type === 'multiselect' && field.options?.length) {
    // Mehrfachauswahl: eine Checkbox je Option, Wert ist die Liste der gewaehlten
    // Schluessel. Bis 08.10.2026 fiel `multiselect` in das Textfeld durch.
    const gewaehlt = new Set(alsListe(value))
    const umschalten = (option: string, an: boolean) => {
      const neu = (field.options ?? [])
        .map((o) => String(o.value))
        .filter((o) => (o === option ? an : gewaehlt.has(o)))
      onChange?.(neu)
    }
    return (
      <fieldset className="space-y-2" aria-label={field.label}>
        <legend className="text-sm font-medium leading-none">
          {field.label}
          {field.required && <span className="ml-1 text-destructive">*</span>}
        </legend>
        <div className="flex flex-wrap gap-x-4 gap-y-2">
          {(field.options ?? []).map((option) => {
            const schluessel = String(option.value)
            const id = `${field.key}-${schluessel}`
            return (
              <div key={schluessel} className="flex min-h-touch items-center gap-2">
                <Checkbox
                  id={id}
                  checked={gewaehlt.has(schluessel)}
                  disabled={isReadOnly}
                  onCheckedChange={(an) => umschalten(schluessel, an === true)}
                />
                <Label htmlFor={id} className="font-normal">{option.label}</Label>
              </div>
            )
          })}
        </div>
        {field.helpText && <p className="text-xs text-muted-foreground">{field.helpText}</p>}
      </fieldset>
    )
  }

  if (field.type === 'lookup') {
    return (
      <div className="space-y-2">
        <Label htmlFor={field.key}>{field.label}</Label>
        <Input {...commonProps} />
        <p className="text-xs text-muted-foreground">
          Lookup: mindestens {field.minSearchChars ?? 2} Zeichen fuer Suche.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <Label htmlFor={field.key}>
        {field.label}
        {field.required && <span className="ml-1 text-destructive">*</span>}
      </Label>
      {field.type === 'textarea' ? (
        <Textarea {...commonProps} ref={textareaRef} />
      ) : field.type === 'select' ? (
        <NativeSelect
          id={field.key}
          value={renderValue(value)}
          disabled={isReadOnly}
          // Ohne leere Option zeigt der Browser die erste Option als gewaehlt,
          // waehrend der Wert leer ist — eine Auswahl, die niemand getroffen hat.
          placeholder={field.placeholder ?? 'Bitte wählen'}
          ariaLabel={field.label}
          options={(field.options ?? []).map((option) => ({ value: String(option.value), label: option.label }))}
          onValueChange={onChange ? (v) => onChange(v) : () => undefined}
        />
      ) : field.type === 'password' ? (
        // Geheimnisse werden nur geschrieben, nie zurueckgegeben oder angezeigt;
        // ein leeres Feld heisst "unveraendert lassen".
        <Input
          {...commonProps}
          ref={inputRef}
          type="password"
          autoComplete="new-password"
          readOnly={isReadOnly}
        />
      ) : isReadOnly ? (
        <Input
          {...commonProps}
          ref={inputRef}
          type="text"
          value={field.key === 'status' ? statusLabel(renderValue(value)) : formatReadOnlyValue(field.type, value)}
        />
      ) : field.type === 'boolean' ? (
        <Checkbox
          id={field.key}
          aria-label={field.label}
          checked={value === true || value === 'true' || value === 'JA'}
          onCheckedChange={(checked) => onChange?.(checked === true)}
        />
      ) : (
        <Input
          {...commonProps}
          ref={inputRef}
          type={field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : 'text'}
        />
      )}
      {canDictate ? (
        <VoiceBar
          provider={provider}
          target="field"
          onCommit={handleVoiceCommit}
          label={`${field.label} diktieren`}
          enableGlobalShortcut={false}
        />
      ) : null}
      {field.helpText && <p className="text-xs text-muted-foreground">{field.helpText}</p>}
    </div>
  )
}
