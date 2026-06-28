import type { Resolver } from 'react-hook-form'
import type { Field, MaskConfig, WizardStep } from './types'

type ValidationErrors = Record<string, string>

type SchemaLike = {
  safeParse?: (_data: unknown) =>
    | { success: true; data: unknown }
    | { success: false; error?: { errors?: Array<{ path?: Array<string | number>; message?: string }> } }
  parse?: (_data: unknown) => unknown
  shape?: Record<string, unknown>
}

function isEmptyValue(value: unknown) {
  return value === undefined || value === null || value === ''
}

export function getFieldName(field: Pick<Field, 'name'> & { key?: string }) {
  return typeof field.name === 'string' && field.name.length > 0 ? field.name : String(field.key ?? '')
}

function toNumber(value: unknown) {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null
  }
  if (typeof value === 'string' && value.trim() !== '') {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}

function getFieldError(field: Field, value: unknown): string | null {
  if (field.required && isEmptyValue(value)) {
    return `${field.label} ist erforderlich`
  }

  if (isEmptyValue(value)) {
    return null
  }

  if (field.type === 'number') {
    const numericValue = toNumber(value)
    if (numericValue === null) {
      return `${field.label} muss eine Zahl sein`
    }
    if (typeof (field as Record<string, unknown>).min === 'number' && numericValue < (field as Record<string, unknown>).min as number) {
      return `${field.label} muss mindestens ${String((field as Record<string, unknown>).min)} sein`
    }
    if (typeof (field as Record<string, unknown>).max === 'number' && numericValue > (field as Record<string, unknown>).max as number) {
      return `${field.label} darf hoechstens ${String((field as Record<string, unknown>).max)} sein`
    }
    return null
  }

  if (field.type === 'multiselect' && Array.isArray(value) && field.required && value.length === 0) {
    return `${field.label} ist erforderlich`
  }

  if (typeof value !== 'string') {
    return null
  }

  const trimmedValue = value.trim()

  if (field.required && trimmedValue.length === 0) {
    return `${field.label} ist erforderlich`
  }

  const minLength = (field as Record<string, unknown>).minLength
  if (typeof minLength === 'number' && trimmedValue.length < minLength) {
    return `${field.label} muss mindestens ${minLength} Zeichen haben`
  }

  const maxLength = (field as Record<string, unknown>).maxLength
  if (typeof maxLength === 'number' && trimmedValue.length > maxLength) {
    return `${field.label} darf hoechstens ${maxLength} Zeichen haben`
  }

  const pattern = (field as Record<string, unknown>).pattern
  if (typeof pattern === 'string' && !(new RegExp(pattern).test(trimmedValue))) {
    return `${field.label} hat ein ungueltiges Format`
  }
  if (pattern instanceof RegExp && !pattern.test(trimmedValue)) {
    return `${field.label} hat ein ungueltiges Format`
  }

  return null
}

export function validateFields(fields: Field[], values: Record<string, unknown>): ValidationErrors {
  const errors: ValidationErrors = {}

  for (const field of fields) {
    const fieldName = getFieldName(field)
    const error = getFieldError(field, values[fieldName])
    if (error) {
      errors[fieldName] = error
    }
  }

  return errors
}

export function createMaskResolver(fields: Field[]): Resolver<Record<string, unknown>> {
  return async (values) => {
    const errors = validateFields(fields, values)
    if (Object.keys(errors).length === 0) {
      return { values, errors: {} }
    }

    return {
      values: {},
      errors: Object.fromEntries(
        Object.entries(errors).map(([name, message]) => [
          name,
          { type: 'validate', message },
        ]),
      ),
    }
  }
}

export function getFieldsFromMaskConfig(config: MaskConfig) {
  return config.tabs.flatMap((tab) => tab.fields)
}

export function getFieldsFromWizardStep(step?: WizardStep) {
  return step?.fields ?? []
}

function normalizeSchemaErrors(error: unknown): ValidationErrors {
  const issues = (error as { errors?: Array<{ path?: Array<string | number>; message?: string }> })?.errors
  if (!Array.isArray(issues)) {
    return { general: 'Validation failed' }
  }

  const result: ValidationErrors = {}
  for (const issue of issues) {
    const path = Array.isArray(issue.path) && issue.path.length > 0 ? issue.path.join('.') : 'general'
    result[path] = issue.message || 'Invalid value'
  }

  return Object.keys(result).length > 0 ? result : { general: 'Validation failed' }
}

export function validateSchemaLike(schema: unknown, data: unknown): { isValid: boolean; errors: ValidationErrors } {
  if (!schema) {
    return { isValid: true, errors: {} }
  }

  if (typeof schema === 'function') {
    const result = schema(data) as { isValid?: boolean; errors?: ValidationErrors }
    if (result && typeof result === 'object' && typeof result.isValid === 'boolean') {
      return { isValid: result.isValid, errors: result.errors ?? {} }
    }
  }

  const schemaLike = schema as SchemaLike

  if (typeof schemaLike.safeParse === 'function') {
    const result = schemaLike.safeParse(data)
    if (result.success) {
      return { isValid: true, errors: {} }
    }
    return { isValid: false, errors: normalizeSchemaErrors(result.error) }
  }

  if (typeof schemaLike.parse === 'function') {
    try {
      schemaLike.parse(data)
      return { isValid: true, errors: {} }
    } catch (error) {
      return { isValid: false, errors: normalizeSchemaErrors(error) }
    }
  }

  return { isValid: true, errors: {} }
}

export function validateSchemaField(schema: unknown, field: string, value: unknown): string | null {
  const schemaLike = schema as SchemaLike | undefined
  const fieldSchema = schemaLike?.shape?.[field] as SchemaLike | undefined
  if (!fieldSchema) {
    return null
  }

  if (typeof fieldSchema.safeParse === 'function') {
    const result = fieldSchema.safeParse(value)
    if (result.success) {
      return null
    }
    const errors = normalizeSchemaErrors(result.error)
    return errors[field] ?? errors.general ?? 'Invalid value'
  }

  if (typeof fieldSchema.parse === 'function') {
    try {
      fieldSchema.parse(value)
      return null
    } catch (error) {
      const errors = normalizeSchemaErrors(error)
      return errors[field] ?? errors.general ?? 'Invalid value'
    }
  }

  return null
}
