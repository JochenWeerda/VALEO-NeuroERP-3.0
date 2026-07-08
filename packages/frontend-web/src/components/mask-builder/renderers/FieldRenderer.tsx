import { type ChangeEvent, useMemo, useRef } from 'react'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { NativeSelect } from '@/components/ui/native-select'
import type { ScreenFieldDefinition } from '../schema'
import { renderValue } from './render-utils'
import { VoiceBar } from './VoiceBar'
import { createDefaultSttProvider, type SttProvider } from '@/lib/voice/stt-provider'

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
          placeholder={field.placeholder}
          options={(field.options ?? []).map((option) => ({ value: String(option.value), label: option.label }))}
          onValueChange={onChange ? (v) => onChange(v) : () => undefined}
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
