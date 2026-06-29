import { useCallback, useMemo, useRef, useState } from 'react'
import type { ScreenDefinition, ScreenFieldDefinition } from '../schema'
import type { DirtyState, FieldError, SubmitState, UniversalFormState, ValidationPlan, ValidationRule } from './FormState'

function buildValidationRules(fields: ScreenFieldDefinition[]): ValidationRule[] {
  const rules: ValidationRule[] = []
  for (const field of fields) {
    if (field.required) {
      rules.push({
        fieldKey: field.key,
        message: `${field.label} ist ein Pflichtfeld.`,
        severity: 'blocking',
        validate: (value) => value == null || value === '' || (Array.isArray(value) && value.length === 0),
      })
    }
  }
  return rules
}

function collectFields(screen: ScreenDefinition): ScreenFieldDefinition[] {
  const fields: ScreenFieldDefinition[] = [...(screen.fields ?? [])]
  for (const tab of screen.tabs ?? []) {
    fields.push(...(tab.fields ?? []))
  }
  return fields
}

export interface UseUniversalFormStateOptions {
  screen: ScreenDefinition | undefined
  initialValues?: Record<string, unknown>
  onSubmit?: (_values: Record<string, unknown>) => Promise<void>
}

export function useUniversalFormState({
  screen,
  initialValues = {},
  onSubmit,
}: UseUniversalFormStateOptions): UniversalFormState {
  const [values, setValues] = useState<Record<string, unknown>>(() => ({ ...initialValues }))
  const [dirtyFields, setDirtyFields] = useState<Set<string>>(new Set())
  const [submitState, setSubmitState] = useState<SubmitState>('idle')
  const [submitError, setSubmitError] = useState<string | null>(null)
  const initialRef = useRef<Record<string, unknown>>(initialValues)
  const submittingRef = useRef(false)

  const rules = useMemo<ValidationRule[]>(() => {
    if (!screen) return []
    return buildValidationRules(collectFields(screen))
  }, [screen])

  const fieldErrors = useMemo<Record<string, FieldError[]>>(() => {
    const errors: Record<string, FieldError[]> = {}
    for (const rule of rules) {
      if (rule.validate(values[rule.fieldKey], values)) {
        if (!errors[rule.fieldKey]) errors[rule.fieldKey] = []
        errors[rule.fieldKey].push({
          fieldKey: rule.fieldKey,
          message: rule.message,
          severity: rule.severity,
        })
      }
    }
    return errors
  }, [rules, values])

  const validationPlan = useMemo<ValidationPlan>(() => ({
    rules,
    hasBlockingErrors: Object.values(fieldErrors).some((errs) =>
      errs.some((e) => e.severity === 'blocking'),
    ),
  }), [rules, fieldErrors])

  const setValue = useCallback((fieldKey: string, value: unknown) => {
    setValues((prev) => ({ ...prev, [fieldKey]: value }))
    setDirtyFields((prev) => new Set(prev).add(fieldKey))
  }, [])

  const resetForm = useCallback((newValues?: Record<string, unknown>) => {
    const next = newValues ?? { ...initialRef.current }
    setValues(next)
    setDirtyFields(new Set())
    setSubmitState('idle')
    setSubmitError(null)
    if (newValues) initialRef.current = { ...newValues }
  }, [])

  const submit = useCallback(async () => {
    if (submittingRef.current || validationPlan.hasBlockingErrors || !onSubmit) return
    submittingRef.current = true
    setSubmitState('submitting')
    setSubmitError(null)
    try {
      await onSubmit(values)
      setSubmitState('success')
      setDirtyFields(new Set())
      initialRef.current = { ...values }
    } catch (err) {
      setSubmitState('error')
      setSubmitError(err instanceof Error ? err.message : 'Unbekannter Fehler')
    } finally {
      submittingRef.current = false
    }
  }, [validationPlan.hasBlockingErrors, onSubmit, values])

  const dirtyState: DirtyState = useMemo(() => ({
    isDirty: dirtyFields.size > 0,
    dirtyFields,
  }), [dirtyFields])

  return {
    values,
    dirtyState,
    fieldErrors,
    submitState,
    submitError,
    validationPlan,
    setValue,
    resetForm,
    submit,
    canSubmit: !validationPlan.hasBlockingErrors && submitState !== 'submitting' && dirtyState.isDirty,
  }
}
