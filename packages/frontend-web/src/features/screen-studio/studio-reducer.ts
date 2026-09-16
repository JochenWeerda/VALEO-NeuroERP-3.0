import type { ScreenDefinition, ScreenFieldDefinition, ScreenTableColumn, ScreenTableDefinition } from '@/components/mask-builder/schema'

export type StudioAction =
  | { type: 'replace'; definition: ScreenDefinition }
  | { type: 'setTitle'; title: string }
  | { type: 'setFloorplan'; floorplan: NonNullable<ScreenDefinition['layout']>['floorplan'] }
  | { type: 'setColumnNavigation'; columnNavigation: NonNullable<ScreenDefinition['layout']>['columnNavigation'] }
  | { type: 'setDensity'; density: NonNullable<ScreenDefinition['layout']>['density'] }
  | { type: 'addField'; field: ScreenFieldDefinition }
  | { type: 'addTable'; table: ScreenTableDefinition }
  | { type: 'addColumn'; tableKey: string; column: ScreenTableColumn }

export function studioReducer(state: ScreenDefinition, action: StudioAction): ScreenDefinition {
  switch (action.type) {
    case 'replace':
      return action.definition
    case 'setTitle':
      return { ...state, title: action.title }
    case 'setFloorplan':
      return { ...state, layout: { ...state.layout, floorplan: action.floorplan } }
    case 'setColumnNavigation':
      return { ...state, layout: { ...state.layout, columnNavigation: action.columnNavigation } }
    case 'setDensity':
      return { ...state, layout: { ...state.layout, density: action.density } }
    case 'addField':
      return { ...state, fields: [...(state.fields ?? []), action.field] }
    case 'addTable':
      return { ...state, tables: [...(state.tables ?? []), action.table] }
    case 'addColumn':
      return {
        ...state,
        tables: (state.tables ?? []).map((table) => (
          table.key === action.tableKey
            ? { ...table, columns: [...table.columns, action.column] }
            : table
        )),
      }
    default:
      return state
  }
}

export function mockRowsFor(definition: ScreenDefinition): Record<string, Record<string, unknown>[]> {
  const tables = [...(definition.tables ?? [])]
  for (const tab of definition.tabs ?? []) tables.push(...(tab.tables ?? []))
  return Object.fromEntries(tables.map((table) => [
    table.key,
    [0, 1, 2].map((index) => {
      const row: Record<string, unknown> = { id: `${table.key}-${index + 1}` }
      for (const column of table.columns) {
        row[column.key] = column.numeric ? (index + 1) * 10 : `${column.label} ${index + 1}`
      }
      return row
    }),
  ]))
}
