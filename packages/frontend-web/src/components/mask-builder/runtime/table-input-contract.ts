import type { ScreenFieldDefinition } from '../schema'

const CELL_TYPES = new Set(['text', 'number', 'currency', 'percentage', 'date', 'datetime', 'boolean', 'select', 'textarea'])
const RESERVED_KEYS = new Set(['__proto__', 'constructor', 'prototype'])

export function validTableInputStructure(field: ScreenFieldDefinition, value: unknown): boolean {
  const columns = field.rowFields
  const options = field.tableEditing
  if (options !== undefined && (!options || typeof options !== 'object' || Array.isArray(options) ||
    ['allowAdd', 'allowDelete'].some(key => options[key as keyof typeof options] !== undefined && typeof options[key as keyof typeof options] !== 'boolean') ||
    options.maxRows !== undefined && (!Number.isInteger(options.maxRows) || options.maxRows < 1 || options.maxRows > 200))) return false
  if (!Array.isArray(columns) || !columns.length || columns.length > 30 || columns.some(column => !column ||
    typeof column !== 'object' || typeof column.key !== 'string' || !column.key || RESERVED_KEYS.has(column.key) ||
    !CELL_TYPES.has(column.type) || column.rowFields !== undefined)) return false
  if (new Set(columns.map(column => column.key)).size !== columns.length) return false
  const rows = value == null ? [] : value
  return Array.isArray(rows) && rows.length <= (options?.maxRows ?? 200) &&
    Array.from(rows).every(row => row !== null && typeof row === 'object' && !Array.isArray(row))
}

export function validTableInputValues(field: ScreenFieldDefinition, value: unknown): boolean {
  if (!validTableInputStructure(field, value)) return false
  return ((value ?? []) as Record<string, unknown>[]).every(row => (field.rowFields ?? []).every(column => {
    const cell = row[column.key]
    const empty = cell == null || typeof cell === 'string' && !cell.trim()
    if (column.required && empty) return false
    return empty || !['number', 'currency', 'percentage'].includes(column.type) ||
      (typeof cell === 'number' || typeof cell === 'string') && Number.isFinite(Number(cell))
  }))
}
