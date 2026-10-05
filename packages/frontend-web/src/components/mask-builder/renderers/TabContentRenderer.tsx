import type { ScreenFieldDefinition, ScreenTableDefinition } from '../schema'
import { FieldRenderer } from './FieldRenderer'
import { TableRenderer } from './TableRenderer'
import { getValue, repeatsCaption } from './render-utils'

export function TabContentRenderer({
  fields,
  tables,
  fieldsClassName,
  payload,
  tableRows,
  screenTitle,
}: {
  fields?: ScreenFieldDefinition[]
  tables?: ScreenTableDefinition[]
  screenTitle?: string
  fieldsClassName: string
  payload: Record<string, unknown>
  tableRows: Record<string, Record<string, unknown>[]>
}): JSX.Element {
  return (
    <div className="space-y-4">
      {(fields?.length ?? 0) > 0 ? (
        <div className={fieldsClassName}>
          {fields?.map((field) => (
            <FieldRenderer key={field.key} field={field} value={getValue(payload, field.key)} />
          ))}
        </div>
      ) : null}
      {(tables ?? []).map((table) => (
        <TableRenderer key={table.key} table={table} rows={tableRows[table.key] ?? []} suppressHeading={repeatsCaption(table.label, screenTitle)} />
      ))}
    </div>
  )
}
