type Row = Record<string, unknown>
export async function readCompleteList(readPage: (page: number) => Promise<{ items: Row[]; total: number }>, signal?: AbortSignal): Promise<{ items: Row[]; total: number }> {
  const items: Row[] = []
  const identities = new Set<string>()
  const guard = () => { if (signal?.aborted) throw new DOMException('Listenabruf abgebrochen.', 'AbortError') }
  let expected: number | undefined
  for (let page = 1; page <= 50; page += 1) {
    guard()
    const data = await readPage(page)
    guard()
    if (!Array.isArray(data.items) || data.items.some(row => !row || typeof row !== 'object' || Array.isArray(row))
      || !Number.isInteger(data.total) || data.total < 0 || data.total > 5000
      || (expected !== undefined && data.total !== expected)) throw new Error('Listenquelle ist unvollständig oder während des Abrufs geändert.')
    expected = data.total
    for (const row of data.items) {
      if (row.id != null) {
        const identity = JSON.stringify(row.id)
        if (identities.has(identity)) throw new Error('Listenquelle wiederholt einen Datensatz.')
        identities.add(identity)
      }
    }
    items.push(...data.items)
    if (items.length > expected || items.length > 5000) throw new Error('Inkonsistente Listenquelle.')
    if (items.length === expected) return { items, total: expected }
    if (!data.items.length) throw new Error('Listenquelle lieferte eine unvollständige Seite.')
  }
  throw new Error('Listenquelle benötigt serverseitige Auswertung.')
}
