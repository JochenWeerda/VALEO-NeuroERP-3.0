import type React from 'react'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { NativeSelect } from '@/components/ui/native-select'
import type { ScreenFieldDefinition } from '../schema'
import { renderValue } from './render-utils'

export function FieldRenderer({
  field,
  value,
  onChange,
}: {
  field: ScreenFieldDefinition
  value: unknown
  onChange?: (_value: unknown) => void
}): JSX.Element {
  const isReadOnly = field.readOnly || !onChange
  const commonProps = {
    id: field.key,
    value: renderValue(value),
    placeholder: field.placeholder,
    readOnly: isReadOnly,
    'aria-label': field.label,
    onChange: onChange
      ? (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => onChange(e.target.value)
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
        <Textarea {...commonProps} />
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
          type={field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : 'text'}
        />
      )}
      {field.helpText && <p className="text-xs text-muted-foreground">{field.helpText}</p>}
    </div>
  )
}
