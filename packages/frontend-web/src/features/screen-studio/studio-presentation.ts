import type { ScreenDefinition } from '@/components/mask-builder/schema'

type Path = Array<string | number>
export interface PresentationEntry { id: string; path: Path; group: string; label: string }

/** Only existing display labels, never a caller-supplied property path. */
export function presentationEntries(definition: ScreenDefinition): PresentationEntry[] {
  const entries: PresentationEntry[] = []
  const add = (path: Path, label: string, group: string) => entries.push({ id: path.join('.'), path, label, group })
  const fields = (items: NonNullable<ScreenDefinition['fields']>, path: Path, group: string) => {
    items.forEach((item, index) => add([...path, index], item.label, group))
  }
  const tables = (items: NonNullable<ScreenDefinition['tables']>, path: Path, group: string) => {
    items.forEach((table, index) => {
      const tablePath = [...path, index]
      add(tablePath, table.label, group)
      table.columns.forEach((column, columnIndex) => add([...tablePath, 'columns', columnIndex], column.label, `${group} / ${table.label}`))
    })
  }
  fields(definition.fields ?? [], ['fields'], 'Kopf')
  tables(definition.tables ?? [], ['tables'], 'Tabellen')
  definition.tabs?.forEach((tab, index) => {
    const path: Path = ['tabs', index]
    add(path, tab.label, 'Register')
    fields(tab.fields ?? [], [...path, 'fields'], tab.label)
    tables(tab.tables ?? [], [...path, 'tables'], tab.label)
  })
  return entries
}

export function renamePresentation(definition: ScreenDefinition, id: string, value: string): ScreenDefinition {
  const label = value.trim()
  const entry = presentationEntries(definition).find(item => item.id === id)
  if (!entry || !label || label.length > 160 || label === entry.label) return definition
  const replace = (node: unknown, remaining: Path): unknown => {
    if (!remaining.length) return { ...(node as object), label }
    const [key, ...rest] = remaining
    if (Array.isArray(node) && typeof key === 'number') return node.map((item, index) => index === key ? replace(item, rest) : item)
    const record = node as Record<string, unknown>
    return { ...record, [key]: replace(record[key], rest) }
  }
  return replace(definition, entry.path) as ScreenDefinition
}
