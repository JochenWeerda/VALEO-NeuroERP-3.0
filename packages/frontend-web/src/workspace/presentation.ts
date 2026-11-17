/** Human-facing labels; technical identifiers remain in command targets and audit data. */
import type { RankedWorkItem } from './types'

const UUID_PREFIX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}:\s*/i
export function workspaceActionLabel(label: string): string {
  return UUID_PREFIX.test(label) ? `Kontrakt · ${label.replace(UUID_PREFIX, '')}` : label
}
export function workspaceActionHint(item: RankedWorkItem): string {
  if (item.reasonCodes.includes('overdue')) return 'Überfällig – bitte prüfen'
  if (item.reasonCodes.includes('due-today')) return 'Heute fällig'
  if (item.action.id.startsWith('agrar.chain.')) return 'Nächsten Schritt im Kontrakt bearbeiten'
  if (item.reasonCodes.includes('pinned')) return 'Angehefteter Einstieg'
  if (item.reasonCodes.some(code => code.startsWith('signal:'))) return 'Für Ihren aktuellen Arbeitsbereich empfohlen'
  return 'Arbeitsbereich öffnen'
}

/** Group matching technical task labels without losing any command target. */
export function groupWorkspaceItems(items: RankedWorkItem[]): RankedWorkItem[][] {
  const groups = new Map<string, RankedWorkItem[]>()
  for (const item of items) {
    const key = UUID_PREFIX.test(item.action.label)
      ? `${item.action.businessDomain}:${workspaceActionLabel(item.action.label)}`
      : item.action.id
    const group = groups.get(key) ?? []
    group.push(item)
    groups.set(key, group)
  }
  return [...groups.values()]
}
