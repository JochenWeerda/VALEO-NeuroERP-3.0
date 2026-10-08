import type { ScreenFieldType } from '../schema'

/** Erlaubte Bausteine. Neue Varianten erweitern diesen Satz, sie stehen nicht neben ihm. */
export const PRIMITIVE_BY_FIELD_TYPE: Record<ScreenFieldType, string> = {
  text: 'TextField',
  textarea: 'TextField',
  number: 'NumberField',
  currency: 'NumberField',
  percentage: 'NumberField',
  password: 'TextField',
  date: 'DateField',
  datetime: 'DateTimeField',
  select: 'Select',
  lookup: 'EntityPicker',
  multiselect: 'MultiEntityPicker',
  boolean: 'Checkbox',
  file: 'FileField',
  table: 'DataTable',
}

export const PRIMITIVE_BY_RENDER_KIND = {
  text: 'TextField',
  number: 'NumberField',
  currency: 'NumberField',
  date: 'DateField',
  datetime: 'DateTimeField',
  status: 'StatusBadge',
  boolean: 'Checkbox',
} as const

export function primitiveForFieldType(type: string): string | null {
  return Object.prototype.hasOwnProperty.call(PRIMITIVE_BY_FIELD_TYPE, type)
    ? PRIMITIVE_BY_FIELD_TYPE[type as ScreenFieldType]
    : null
}
