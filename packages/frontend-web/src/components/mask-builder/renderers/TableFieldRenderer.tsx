import type { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import type { ScreenFieldDefinition } from '../schema'

import { validTableInputStructure } from '../runtime/table-input-contract'

/** Structured form values only. Domain calculations and persistence stay server-side. */
export function TableFieldRenderer({ field, value, onChange, renderCell }: {
  field: ScreenFieldDefinition
  value: unknown
  onChange?: (value: unknown) => void
  renderCell: (field: ScreenFieldDefinition, value: unknown, onChange?: (value: unknown) => void) => ReactNode
}) {
  const columns = field.rowFields ?? []
  const rows = value == null ? [] : value
  const limit = field.tableEditing?.maxRows ?? 200
  if (!validTableInputStructure(field, value)) return <div role="alert" className="text-destructive">{field.label}: Tabellenstruktur oder Zeilenlimit ist ungültig.</div>
  const records = rows as Record<string, unknown>[]
  const editable = !field.readOnly && Boolean(onChange)
  const changeCell = (index: number, column: ScreenFieldDefinition, next: unknown) => {
    if (!editable || column.readOnly) return
    let parsed = next
    if (['number', 'currency', 'percentage'].includes(column.type) && typeof next === 'string') {
      parsed = next.trim() === '' ? null : Number.isFinite(Number(next)) ? Number(next) : next
    }
    onChange?.(records.map((row, i) => i === index ? { ...row, [column.key]: parsed } : row))
  }
  return <fieldset className="col-span-full min-w-0 space-y-2" data-table-field={field.key}>
    <legend className="text-sm font-medium">{field.label}</legend>
    <div className="overflow-x-auto rounded border border-border bg-background">
      <table className="w-full text-sm" aria-label={field.label}>
        <thead className="bg-muted"><tr>{columns.map(column => <th key={column.key} scope="col" className="px-2 py-2 text-left font-medium">{column.label}</th>)}
          {field.tableEditing?.allowDelete ? <th scope="col"><span className="sr-only">Zeile entfernen</span></th> : null}</tr></thead>
        <tbody>{records.map((row, index) => <tr key={index} className="border-t border-border">
          {columns.map(column => <td key={column.key} className="min-w-28 p-1 [&_label]:sr-only">
            {renderCell({ ...column, key: `${field.key}-${index}-${column.key}`, label: `${column.label}, Zeile ${index + 1}`,
              readOnly: !editable || column.readOnly }, row[column.key], editable && !column.readOnly
              ? next => changeCell(index, column, next) : undefined)}
          </td>)}
          {field.tableEditing?.allowDelete ? <td className="p-1"><Button type="button" variant="ghost" disabled={!editable}
            aria-label={`Zeile ${index + 1} entfernen`} onClick={() => editable && onChange?.(records.filter((_, i) => i !== index))}>Entfernen</Button></td> : null}
        </tr>)}</tbody>
      </table>
    </div>
    {!records.length ? <p className="text-sm text-muted-foreground">Noch keine Zeilen erfasst.</p> : null}
    {field.tableEditing?.allowAdd ? <Button type="button" variant="outline" disabled={!editable || records.length >= limit}
      onClick={() => editable && records.length < limit && onChange?.([...records, {}])}>Zeile hinzufügen</Button> : null}
    {field.helpText ? <p className="text-xs text-muted-foreground">{field.helpText}</p> : null}
  </fieldset>
}
