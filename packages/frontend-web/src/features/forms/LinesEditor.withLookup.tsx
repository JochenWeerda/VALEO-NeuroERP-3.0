import { Fragment } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ArticleLookupItem, InlineArticleLookup } from '@/features/forms/fields/inline-lookup'

type ColumnType = 'string' | 'number' | 'article'

type LineColumn<ColumnName extends string> = {
  name: ColumnName
  label: string
  type: ColumnType
  required?: boolean
}

type RowValue = string | number

type RowRecord<ColumnName extends string> = Record<ColumnName, RowValue>

interface LinesEditorWithLookupProps<ColumnName extends string> {
  columns: LineColumn<ColumnName>[]
  value: Array<RowRecord<ColumnName>>
  onChange: (_rows: Array<RowRecord<ColumnName>>) => void
}

const DEFAULT_NUMERIC_VALUE = 0
const ARTICLE_COLUMN_NAME = 'article'
const VAT_MULTIPLIER = 1.2

export function LinesEditorWithLookup<ColumnName extends string>({
  columns,
  value,
  onChange,
}: LinesEditorWithLookupProps<ColumnName>): JSX.Element {
  const rows = value ?? []

  const handleSetCell = (rowIndex: number, columnName: ColumnName, nextValue: RowValue): void => {
    const nextRows = rows.map((row, idx) => (idx === rowIndex ? { ...row, [columnName]: nextValue } : row))
    onChange(nextRows)
  }

  const handleAddRow = (): void => {
    const defaultRow = columns.reduce<RowRecord<ColumnName>>((accumulator, column) => {
      const defaultValue = column.type === 'number' ? DEFAULT_NUMERIC_VALUE : ''
      return { ...accumulator, [column.name]: defaultValue }
    }, {} as RowRecord<ColumnName>)
    onChange([...rows, defaultRow])
  }

  const handleDeleteRow = (rowIndex: number): void => {
    onChange(rows.filter((_, idx) => idx !== rowIndex))
  }

  const handleArticlePick = (rowIndex: number, item: ArticleLookupItem): void => {
    const price = typeof item.price === 'number'
      ? item.price
      : typeof item.cost === 'number'
        ? Number((item.cost * VAT_MULTIPLIER).toFixed(2))
        : DEFAULT_NUMERIC_VALUE

    const nextRows = rows.map((row, idx) => {
      if (idx !== rowIndex) {
        return row
      }
      return {
        ...row,
        [ARTICLE_COLUMN_NAME as ColumnName]: item.id,
        cost: item.cost ?? (row as any).cost,
        price: (row as any).price ?? price,
      } as any
    })

    onChange(nextRows)
  }

  const renderCell = (row: RowRecord<ColumnName>, rowIndex: number, column: LineColumn<ColumnName>): JSX.Element => {
    const rawValue = row[column.name]

    if (column.type === 'article' || column.name === ARTICLE_COLUMN_NAME) {
      return (
        <InlineArticleLookup
          value={String(rawValue ?? '')}
          onPick={(item) => handleArticlePick(rowIndex, item)}
        />
      )
    }

    if (column.type === 'number') {
      return (
        <Input
          type="number"
          value={Number(rawValue ?? DEFAULT_NUMERIC_VALUE)}
          onChange={(event) => handleSetCell(rowIndex, column.name, Number(event.target.value))}
        />
      )
    }

    return (
      <Input
        value={String(rawValue ?? '')}
        onChange={(event) => handleSetCell(rowIndex, column.name, event.target.value)}
      />
    )
  }

  return (
    <div className="grid gap-2" style={{ gridTemplateColumns: `40px repeat(${columns.length}, 1fr) 80px` }}>
      <div className="font-medium">#</div>
      {columns.map((column) => (
        <div key={column.name} className="font-medium">
          {column.label}
        </div>
      ))}
      <div />

      {rows.map((row, rowIndex) => (
        <Fragment key={rowIndex}>
          <div className="text-sm text-muted-foreground">{rowIndex + 1}</div>
          {columns.map((column) => (
            <div key={column.name}>{renderCell(row, rowIndex, column)}</div>
          ))}
          <Button type="button" variant="ghost" size="sm" onClick={() => handleDeleteRow(rowIndex)}>
            Loeschen
          </Button>
        </Fragment>
      ))}

      <div className="col-span-full mt-2">
        <Button type="button" variant="outline" onClick={handleAddRow}>
          Position hinzufuegen
        </Button>
      </div>
    </div>
  )
}
