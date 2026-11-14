import type { ScreenActionDefinition } from '../schema'

export function isDocflowConvert(action?: ScreenActionDefinition): boolean {
  return action?.commandBinding?.adapter === 'docflow.v1' && action.commandBinding.command === 'convert'
}

export function docflowConversionOptionsUrl(action: ScreenActionDefinition, entityId: string): string {
  const target = action.commandBinding?.defaults?.target_doc_type
  if (!isDocflowConvert(action) || action.commandEndpoint !== '/api/v1/docflow/{entity_id}/convert' ||
    typeof target !== 'string' || !target || !entityId) throw new Error('Folgebelegbindung fehlt.')
  return `/api/v1/docflow/${encodeURIComponent(entityId)}/conversion-options?target_doc_type=${encodeURIComponent(target)}`
}

/** Complete server selection, not the currently visible/paginated position tab. */
export function docflowConvertInput(action: ScreenActionDefinition, response: unknown,
  entityId: string, version: number | undefined, docType: unknown): Record<string, unknown> {
  const data = response as Record<string, unknown> | null
  if (!isDocflowConvert(action) || !Number.isInteger(version) || data?.source_doc_id !== entityId ||
    data.version !== version || data.source_doc_type !== docType ||
    data.target_doc_type !== action.commandBinding?.defaults?.target_doc_type ||
    !Array.isArray(data.items) || !data.items.length || data.items.length > 200) {
    throw new Error('Positionsauswahl ist unvollstaendig oder veraltet. Bitte neu laden.')
  }
  const ids = new Set<string>()
  const rows = data.items.map((item: Record<string, unknown>) => {
    if (!item || typeof item.source_item_id !== 'string' || !item.source_item_id || ids.has(item.source_item_id) ||
      typeof item.remaining_quantity !== 'number' || !Number.isFinite(item.remaining_quantity) || item.remaining_quantity < 0) {
      throw new Error('Positionsauswahl ist ungueltig. Bitte neu laden.')
    }
    ids.add(item.source_item_id)
    return { source_item_id: item.source_item_id, line_number: item.line_number, article_number: item.article_number,
      description: item.description, unit: item.unit, remaining_quantity: item.remaining_quantity, quantity: 0 }
  })
  return { quantities_by_source_item_id: rows }
}

/** Transport shape only; the server remains authoritative for ownership and current remaining quantities. */
export function docflowConversionQuantities(value: unknown): Record<string, number> {
  const entries: Array<[string, number]> = []
  if (Array.isArray(value)) {
    if (!value.length || value.length > 200) throw new Error('Positionsauswahl fehlt oder ist zu gross.')
    for (const row of value) {
      if (!row || typeof row.source_item_id !== 'string' || !row.source_item_id ||
        typeof row.quantity !== 'number' || !Number.isFinite(row.quantity) || row.quantity < 0 ||
        typeof row.remaining_quantity !== 'number' || !Number.isFinite(row.remaining_quantity) ||
        row.quantity > row.remaining_quantity) throw new Error('Uebernahmemenge muss zwischen null und Restmenge liegen.')
      entries.push([row.source_item_id, row.quantity])
    }
  } else if (value && typeof value === 'object') {
    for (const [id, quantity] of Object.entries(value)) {
      if (!id || typeof quantity !== 'number' || !Number.isFinite(quantity) || quantity < 0) {
        throw new Error('Uebernahmemengen sind ungueltig.')
      }
      entries.push([id, quantity])
    }
  } else throw new Error('Positionsmengen fehlen.')
  if (new Set(entries.map(([id]) => id)).size !== entries.length) throw new Error('Doppelte Position in der Auswahl.')
  if (!entries.some(([, quantity]) => quantity > 0)) throw new Error('Mindestens eine positive Uebernahmemenge angeben.')
  return Object.fromEntries(entries)
}
