import type { ScreenFieldDefinition, ScreenTableColumn } from '../schema'

type FeldZusatz = Pick<ScreenFieldDefinition, 'unit' | 'unitField' | 'format' | 'computed'>
type SpaltenZusatz = Pick<ScreenTableColumn, 'unit' | 'unitField' | 'computed' | 'aggregate'>

/** Einheit, Format und Rechenregel eines Felds; jede Abbildung Definition <-> Plan reicht sie gleich weiter. */
export function fieldExtras(field: FeldZusatz): FeldZusatz {
  return {
    ...(field.unit !== undefined ? { unit: field.unit } : {}),
    ...(field.unitField !== undefined ? { unitField: field.unitField } : {}),
    ...(field.format !== undefined ? { format: field.format } : {}),
    ...(field.computed !== undefined ? { computed: field.computed } : {}),
  }
}

export function columnExtras(column: SpaltenZusatz): SpaltenZusatz {
  return {
    ...(column.unit !== undefined ? { unit: column.unit } : {}),
    ...(column.unitField !== undefined ? { unitField: column.unitField } : {}),
    ...(column.computed !== undefined ? { computed: column.computed } : {}),
    ...(column.aggregate !== undefined ? { aggregate: column.aggregate } : {}),
  }
}
