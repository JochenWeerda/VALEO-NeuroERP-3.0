/** Universal form state types for mask edit mode (Phase 025). */

export type ValidationSeverity = 'blocking' | 'warning' | 'info'

export interface ValidationRule {
  fieldKey: string
  /** Human-readable message shown in field error or warning chip */
  message: string
  /** 'blocking' prevents submit; 'warning' shows but allows submit; 'info' is informational */
  severity: ValidationSeverity
  /** Validate function — return true if rule is violated (i.e. invalid) */
  validate: (_value: unknown, _allValues: Record<string, unknown>) => boolean
}

export interface ValidationPlan {
  rules: ValidationRule[]
  /** True if any blocking rule is violated */
  hasBlockingErrors: boolean
}

export interface FieldError {
  fieldKey: string
  message: string
  severity: ValidationSeverity
}

export interface DirtyState {
  isDirty: boolean
  dirtyFields: Set<string>
}

export type SubmitState = 'idle' | 'submitting' | 'success' | 'error'

export interface UniversalFormState {
  values: Record<string, unknown>
  dirtyState: DirtyState
  fieldErrors: Record<string, FieldError[]>
  /**
   * Was die Maske anzeigt: Fehler bearbeiteter Felder sofort, alle erst nach einem
   * Absendeversuch oder `revealErrors()`. Die Sperre (`validationPlan`) gilt immer
   * fuer alle Felder — nur die Meldung wartet.
   */
  visibleFieldErrors?: Record<string, FieldError[]>
  /** Fuer Seiten mit eigenen Aktionen statt `submit()`: alle Fehler zeigen. */
  revealErrors?: () => void
  submitState: SubmitState
  submitError: string | null
  validationPlan: ValidationPlan
  setValue: (_fieldKey: string, _value: unknown) => void
  resetForm: (_values?: Record<string, unknown>) => void
  submit: () => Promise<void>
  canSubmit: boolean
}
