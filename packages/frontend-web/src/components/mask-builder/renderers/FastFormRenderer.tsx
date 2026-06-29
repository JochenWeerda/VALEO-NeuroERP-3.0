import { memo } from 'react'
import { LookupField } from './LookupField'
import type { RenderFieldPlan, RenderPerformancePlan } from '../render-plan/types'
import { useLookupBindingContext } from '../runtime/LookupBindingContext'
import { useFormStateContext } from '../runtime/FormStateContext'
import { FieldRenderer } from './FieldRenderer'
import { getValue } from './render-utils'
import type { ScreenFieldDefinition } from '../schema'

function toScreenField(field: RenderFieldPlan): ScreenFieldDefinition {
  return {
    key: field.key,
    label: field.label,
    type: field.componentKind,
    required: field.required,
    readOnly: field.readOnly,
    placeholder: field.placeholder,
    helpText: field.helpText,
    options: field.options,
    dataSourceKey: field.dataSourceKey,
    minSearchChars: field.minSearchChars,
    renderHint: field.renderHint,
  }
}

const FastFieldItem = memo(function FastFieldItem({
  field,
  payload,
  performance,
}: {
  field: RenderFieldPlan
  payload: Record<string, unknown>
  performance?: RenderPerformancePlan
}): JSX.Element | null {
  const lookupBindings = useLookupBindingContext()
  const formState = useFormStateContext()
  if (!field.visible) return null

  const value = getValue(payload, field.dataPath)
  const fieldErrors = formState?.fieldErrors[field.key] ?? []
  const hasBlockingError = fieldErrors.some((e) => e.severity === 'blocking')
  const isEditable = formState !== undefined && !field.readOnly

  function handleChange(newValue: unknown) {
    formState?.setValue(field.key, newValue)
  }

  if (field.componentKind === 'lookup') {
    const lookupEndpoint = lookupBindings[field.key]?.lookupEndpoint
    return (
      <div>
        <LookupField
          field={field}
          value={value}
          lookupEndpoint={lookupEndpoint}
          performance={performance}
        />
        {fieldErrors.map((err) => (
          <p
            key={err.message}
            className={`text-xs ${hasBlockingError ? 'text-destructive' : 'text-yellow-600'}`}
            role="alert"
            data-field-error={field.key}
          >
            {err.message}
          </p>
        ))}
      </div>
    )
  }

  return (
    <div>
      <FieldRenderer
        field={toScreenField(field)}
        value={value}
        onChange={isEditable ? handleChange : undefined}
      />
      {fieldErrors.map((err) => (
        <p
          key={err.message}
          className={`text-xs ${hasBlockingError ? 'text-destructive' : 'text-yellow-600'}`}
          role="alert"
          data-field-error={field.key}
        >
          {err.message}
        </p>
      ))}
    </div>
  )
})

export const FastFormRenderer = memo(function FastFormRenderer({
  fieldKeys,
  fieldsByKey,
  payload,
  className,
  performance,
}: {
  fieldKeys: string[]
  fieldsByKey: Record<string, RenderFieldPlan>
  payload: Record<string, unknown>
  className: string
  performance?: RenderPerformancePlan
}): JSX.Element | null {
  const fields = fieldKeys.map((key) => fieldsByKey[key]).filter(Boolean)
  if (fields.length === 0) return null

  return (
    <div className={className}>
      {fields.map((field) => (
        <FastFieldItem key={field.key} field={field} payload={payload} performance={performance} />
      ))}
    </div>
  )
})
