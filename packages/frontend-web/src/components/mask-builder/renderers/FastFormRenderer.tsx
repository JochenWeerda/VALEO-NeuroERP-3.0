import { memo } from 'react'
import { LookupField } from './LookupField'
import type { RenderFieldPlan, RenderPerformancePlan } from '../render-plan/types'
import { useLookupBindingContext } from '../runtime/LookupBindingContext'
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
  if (!field.visible) return null
  if (field.componentKind === 'lookup') {
    const lookupEndpoint = lookupBindings[field.key]?.lookupEndpoint
    return (
      <LookupField
        field={field}
        value={getValue(payload, field.dataPath)}
        lookupEndpoint={lookupEndpoint}
        performance={performance}
      />
    )
  }
  return <FieldRenderer field={toScreenField(field)} value={getValue(payload, field.dataPath)} />
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
