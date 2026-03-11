/**
 * Form Validator
 * Validiert Werte direkt gegen FormSchema ohne Zod im Shared-Form-Pfad.
 */

import type { FormSchema } from "./FormBuilder"

type ValidationResult = {
  ok: boolean
  errs: Record<string, string>
  parsed: unknown
  summary: string[]
}

export function validateValues(
  schema: FormSchema,
  values: Record<string, unknown>
): ValidationResult {
  const errs: Record<string, string> = {}
  const summary = new Set<string>()
  const parsed: Record<string, unknown> = {}

  for (const field of schema.fields) {
    const value = values[field.name]
    const fieldResult = validateField(field, value)
    if (fieldResult.ok) {
      parsed[field.name] = fieldResult.value
      continue
    }

    const message = explainValidationIssue(schema, field.name, fieldResult.message)
    errs[field.name] = message
    summary.add(message)
  }

  if (schema.lines !== undefined) {
    const rawRows = Array.isArray(values[schema.lines.name]) ? (values[schema.lines.name] as unknown[]) : []
    const parsedRows: Record<string, unknown>[] = []

    rawRows.forEach((row, rowIndex) => {
      const inputRow = isRecord(row) ? row : {}
      const nextRow: Record<string, unknown> = {}

      schema.lines?.columns.forEach((column) => {
        const path = `${schema.lines?.name}.${rowIndex}.${column.name}`
        const columnResult = validateLineColumn(column, inputRow[column.name])
        if (columnResult.ok) {
          nextRow[column.name] = columnResult.value
          return
        }

        const message = explainValidationIssue(schema, path, columnResult.message)
        errs[path] = message
        summary.add(message)
      })

      parsedRows.push(nextRow)
    })

    parsed[schema.lines.name] = parsedRows
  }

  if (Object.keys(errs).length > 0) {
    return { ok: false, errs, parsed: null, summary: Array.from(summary) }
  }

  return { ok: true, errs: {}, parsed, summary: [] }
}

type FieldValidationResult =
  | { ok: true; value: unknown }
  | { ok: false; message: string }

function validateField(
  field: FormSchema["fields"][number],
  value: unknown
): FieldValidationResult {
  if (field.type === "number") {
    return validateNumberValue(field.label, value, field.required === true, field.min, field.max)
  }

  if (field.type === "date") {
    return validateDateValue(field.label, value, field.required === true)
  }

  return validateStringValue(field.label, value, field.required === true)
}

function validateLineColumn(
  column: NonNullable<FormSchema["lines"]>["columns"][number],
  value: unknown
): FieldValidationResult {
  if (column.type === "number") {
    return validateNumberValue(column.label, value, column.required === true)
  }

  return validateStringValue(column.label, value, column.required === true)
}

function validateStringValue(
  label: string,
  value: unknown,
  required: boolean
): FieldValidationResult {
  if (typeof value !== "string") {
    if (value === undefined || value === null || value === "") {
      return required
        ? { ok: false, message: `${label} ist erforderlich` }
        : { ok: true, value: undefined }
    }
    return { ok: false, message: `${label} ist ungueltig` }
  }

  const trimmed = value.trim()
  if (trimmed.length === 0) {
    return required
      ? { ok: false, message: `${label} ist erforderlich` }
      : { ok: true, value: undefined }
  }

  return { ok: true, value: trimmed }
}

function validateNumberValue(
  label: string,
  value: unknown,
  required: boolean,
  min?: number,
  max?: number
): FieldValidationResult {
  if (value === undefined || value === null || value === "") {
    return required
      ? { ok: false, message: `${label} ist erforderlich` }
      : { ok: true, value: undefined }
  }

  if (typeof value !== "number" || Number.isNaN(value)) {
    return { ok: false, message: `${label} ist ungueltig` }
  }

  if (typeof min === "number" && value < min) {
    return { ok: false, message: `${label} muss mindestens ${min} sein` }
  }

  if (typeof max === "number" && value > max) {
    return { ok: false, message: `${label} darf hoechstens ${max} sein` }
  }

  return { ok: true, value }
}

function validateDateValue(
  label: string,
  value: unknown,
  required: boolean
): FieldValidationResult {
  const stringResult = validateStringValue(label, value, required)
  if (!stringResult.ok || stringResult.value === undefined) {
    return stringResult
  }

  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(stringResult.value))) {
    return { ok: false, message: `${label} muss im Format JJJJ-MM-TT vorliegen` }
  }

  return stringResult
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null
}

function explainValidationIssue(
  formSchema: FormSchema | undefined,
  path: string,
  fallbackMessage: string
): string {
  if (formSchema === undefined) {
    return fallbackMessage
  }

  const fieldMeta = resolveFieldMeta(formSchema, path)
  if (fieldMeta === null) {
    return fallbackMessage
  }

  const detail = getDomainSpecificHint(formSchema.id, fieldMeta.name)
  if (detail === null) {
    return fallbackMessage
  }

  return `${fallbackMessage} ${detail}`
}

function resolveFieldMeta(
  schema: FormSchema,
  path: string
): { name: string; label: string; isLine: boolean; rowIndex?: number } | null {
  const directField = schema.fields.find((field) => field.name === path)
  if (directField !== undefined) {
    return { name: directField.name, label: directField.label, isLine: false }
  }

  const lineName = schema.lines?.name
  if (typeof lineName !== "string" || !path.startsWith(`${lineName}.`)) {
    return null
  }

  const [, rowIndexRaw, columnName] = path.split(".")
  const column = schema.lines?.columns.find((entry) => entry.name === columnName)
  if (column === undefined) {
    return null
  }

  return {
    name: column.name,
    label: column.label,
    isLine: true,
    rowIndex: Number(rowIndexRaw) + 1,
  }
}

function getDomainSpecificHint(schemaId: string, fieldName: string): string | null {
  if (schemaId === "sales_invoice") {
    const hints: Record<string, string> = {
      number: "Die Rechnungsnummer wird fuer Belegfluss, OP und Druck verwendet.",
      date: "Das Rechnungsdatum steuert Buchungsperiode und steuerliche Einordnung.",
      customerId: "Ohne Kunden kann die Forderung keinem Debitor zugeordnet werden.",
      paymentTerms: "Die Zahlungsbedingung steuert Faelligkeit und Mahnwesen.",
      dueDate: "Das Faelligkeitsdatum wird fuer Offene Posten und Mahnlaeufe benoetigt.",
      article: "Jede Position braucht einen Artikel fuer Preis-, Steuer- und Belegbezug.",
      qty: "Die Menge bestimmt Umsatz, Steuerbasis und Mengenbezug der Position.",
      price: "Der Preis bestimmt den Nettowert der Rechnungsposition.",
      vatRate: "Der Steuersatz ist fuer die korrekte Umsatzsteuerberechnung erforderlich.",
    }

    return hints[fieldName] ?? null
  }

  return null
}
