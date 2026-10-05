import type { LaunchpadAppTile, LaunchpadPage, LaunchpadSpace } from '@/app/navigation/launchpad-spaces'

export const LAUNCHPAD_OVERLAY_STORAGE_KEY = 'valeo.launchpad.overlay'
export const CUSTOM_PAGE_PLACEHOLDER = 'Neue Gruppe'

export type LaunchpadOverlay = {
  version: 1
  hiddenPageIds: string[]
  pageOrder: Record<string, string[]>
  pageLabels: Record<string, string>
  tileOrder: Record<string, string[]>
  removedTiles: Record<string, string[]>
  tileLabels: Record<string, string>
  tileDescriptions: Record<string, string>
  customPages: Array<{
    id: string
    spaceId: string
    label: string
    tileIds: string[]
  }>
}

export const EMPTY_LAUNCHPAD_OVERLAY: LaunchpadOverlay = {
  version: 1,
  hiddenPageIds: [],
  pageOrder: {},
  pageLabels: {},
  tileOrder: {},
  removedTiles: {},
  tileLabels: {},
  tileDescriptions: {},
  customPages: [],
}

export function pageKey(spaceId: string, pageId: string): string {
  return `${spaceId}:${pageId}`
}

export function createCustomPageId(): string {
  const suffix = globalThis.crypto?.randomUUID?.() ?? `t${Date.now()}`
  return `grp-${suffix}`
}

export function parseLaunchpadOverlay(raw: unknown): LaunchpadOverlay {
  if (!raw || typeof raw !== 'object') {
    return { ...EMPTY_LAUNCHPAD_OVERLAY }
  }
  const value = raw as Record<string, unknown>
  return {
    version: 1,
    hiddenPageIds: stringList(value.hiddenPageIds),
    pageOrder: stringRecordList(value.pageOrder),
    pageLabels: stringRecord(value.pageLabels),
    tileOrder: stringRecordList(value.tileOrder),
    removedTiles: stringRecordList(value.removedTiles),
    tileLabels: stringRecord(value.tileLabels),
    tileDescriptions: stringRecord(value.tileDescriptions),
    customPages: parseCustomPages(value.customPages),
  }
}

export function catalogTileIndex(spaces: LaunchpadSpace[]): Map<string, LaunchpadAppTile> {
  const index = new Map<string, LaunchpadAppTile>()
  for (const space of spaces) {
    for (const page of space.pages) {
      for (const tile of page.tiles) {
        if (!index.has(tile.id)) {
          index.set(tile.id, tile)
        }
      }
    }
  }
  return index
}

export function applyLaunchpadOverlay(
  spaces: LaunchpadSpace[],
  overlay: LaunchpadOverlay,
  options: { includeHidden?: boolean } = {},
): LaunchpadSpace[] {
  const tilesById = catalogTileIndex(spaces)
  const includeHidden = options.includeHidden === true

  return spaces
    .map((space) => {
      const catalogPages = space.pages.map((page, index) =>
        decoratePage(space.id, page, overlay, tilesById, index === 0),
      )
      const customPages = overlay.customPages
        .filter((page) => page.spaceId === space.id)
        .map((page) => decorateCustomPage(page, overlay, tilesById))
      const merged = orderPages(space.id, [...catalogPages, ...customPages], overlay)
      const visible = includeHidden ? merged : merged.filter((page) => page.hidden !== true)
      const pages = visible.length > 0 ? visible : merged.filter((page) => page.locked)
      return { ...space, pages }
    })
    .filter((space) => space.pages.length > 0)
}

export function hidePage(overlay: LaunchpadOverlay, spaceId: string, page: LaunchpadPage): LaunchpadOverlay {
  if (page.locked) {
    return overlay
  }
  const key = pageKey(spaceId, page.id)
  if (overlay.hiddenPageIds.includes(key)) {
    return overlay
  }
  return { ...overlay, hiddenPageIds: [...overlay.hiddenPageIds, key] }
}

export function showPage(overlay: LaunchpadOverlay, spaceId: string, pageId: string): LaunchpadOverlay {
  const key = pageKey(spaceId, pageId)
  return { ...overlay, hiddenPageIds: overlay.hiddenPageIds.filter((entry) => entry !== key) }
}

export function renamePage(overlay: LaunchpadOverlay, spaceId: string, page: LaunchpadPage, label: string): LaunchpadOverlay {
  const nextLabel = label.trim() || (page.origin === 'custom' ? CUSTOM_PAGE_PLACEHOLDER : page.label)
  if (page.origin === 'custom') {
    return {
      ...overlay,
      customPages: overlay.customPages.map((entry) =>
        entry.id === page.id && entry.spaceId === spaceId ? { ...entry, label: nextLabel } : entry,
      ),
    }
  }
  return {
    ...overlay,
    pageLabels: { ...overlay.pageLabels, [pageKey(spaceId, page.id)]: nextLabel },
  }
}

export function resetPage(overlay: LaunchpadOverlay, spaceId: string, page: LaunchpadPage): LaunchpadOverlay {
  if (page.origin !== 'catalog') {
    return overlay
  }
  const key = pageKey(spaceId, page.id)
  const { [key]: _order, ...tileOrder } = overlay.tileOrder
  const { [key]: _removed, ...removedTiles } = overlay.removedTiles
  const { [key]: _label, ...pageLabels } = overlay.pageLabels
  return {
    ...overlay,
    tileOrder,
    removedTiles,
    pageLabels,
    hiddenPageIds: overlay.hiddenPageIds.filter((entry) => entry !== key),
  }
}

export function deletePage(overlay: LaunchpadOverlay, spaceId: string, page: LaunchpadPage): LaunchpadOverlay {
  if (page.origin !== 'custom' || page.locked) {
    return overlay
  }
  const key = pageKey(spaceId, page.id)
  const { [key]: _order, ...tileOrder } = overlay.tileOrder
  const { [key]: _removed, ...removedTiles } = overlay.removedTiles
  return {
    ...overlay,
    customPages: overlay.customPages.filter((entry) => !(entry.id === page.id && entry.spaceId === spaceId)),
    tileOrder,
    removedTiles,
    hiddenPageIds: overlay.hiddenPageIds.filter((entry) => entry !== key),
    pageOrder: {
      ...overlay.pageOrder,
      [spaceId]: (overlay.pageOrder[spaceId] ?? []).filter((id) => id !== page.id),
    },
  }
}

export function addCustomPage(overlay: LaunchpadOverlay, spaceId: string, label?: string): { overlay: LaunchpadOverlay; pageId: string } {
  const pageId = createCustomPageId()
  const nextLabel = label?.trim() || CUSTOM_PAGE_PLACEHOLDER
  return {
    pageId,
    overlay: {
      ...overlay,
      customPages: [...overlay.customPages, { id: pageId, spaceId, label: nextLabel, tileIds: [] }],
      pageOrder: {
        ...overlay.pageOrder,
        [spaceId]: [...(overlay.pageOrder[spaceId] ?? []), pageId],
      },
    },
  }
}

export function movePage(overlay: LaunchpadOverlay, spaceId: string, pageIds: string[], fromIndex: number, toIndex: number): LaunchpadOverlay {
  const next = moveIndex(pageIds, fromIndex, toIndex)
  if (!next) {
    return overlay
  }
  return { ...overlay, pageOrder: { ...overlay.pageOrder, [spaceId]: next } }
}

export function removeTile(overlay: LaunchpadOverlay, spaceId: string, page: LaunchpadPage, tileId: string): LaunchpadOverlay {
  const key = pageKey(spaceId, page.id)
  if (page.origin === 'custom') {
    return {
      ...overlay,
      customPages: overlay.customPages.map((entry) =>
        entry.id === page.id && entry.spaceId === spaceId
          ? { ...entry, tileIds: entry.tileIds.filter((id) => id !== tileId) }
          : entry,
      ),
      tileOrder: { ...overlay.tileOrder, [key]: (overlay.tileOrder[key] ?? page.tiles.map((tile) => tile.id)).filter((id) => id !== tileId) },
    }
  }
  const removed = new Set(overlay.removedTiles[key] ?? [])
  removed.add(tileId)
  return {
    ...overlay,
    removedTiles: { ...overlay.removedTiles, [key]: [...removed] },
    tileOrder: {
      ...overlay.tileOrder,
      [key]: (overlay.tileOrder[key] ?? page.tiles.map((tile) => tile.id)).filter((id) => id !== tileId),
    },
  }
}

export function addTile(overlay: LaunchpadOverlay, spaceId: string, page: LaunchpadPage, tileId: string): LaunchpadOverlay {
  const key = pageKey(spaceId, page.id)
  if (page.origin === 'custom') {
    const tileIds = overlay.customPages.find((entry) => entry.id === page.id && entry.spaceId === spaceId)?.tileIds ?? page.tiles.map((tile) => tile.id)
    if (tileIds.includes(tileId)) {
      return overlay
    }
    return {
      ...overlay,
      customPages: overlay.customPages.map((entry) =>
        entry.id === page.id && entry.spaceId === spaceId ? { ...entry, tileIds: [...tileIds, tileId] } : entry,
      ),
    }
  }
  const current = (overlay.tileOrder[key] ?? page.tiles.map((tile) => tile.id)).filter((id) => id !== tileId)
  const removed = (overlay.removedTiles[key] ?? []).filter((id) => id !== tileId)
  if (!current.includes(tileId) && !page.tiles.some((tile) => tile.id === tileId)) {
    current.push(tileId)
  }
  return {
    ...overlay,
    removedTiles: { ...overlay.removedTiles, [key]: removed },
    tileOrder: { ...overlay.tileOrder, [key]: current.includes(tileId) ? current : [...current, tileId] },
  }
}

export function moveTileToPage(
  overlay: LaunchpadOverlay,
  spaceId: string,
  fromPage: LaunchpadPage,
  toPage: LaunchpadPage,
  tileId: string,
): LaunchpadOverlay {
  if (fromPage.id === toPage.id) {
    return overlay
  }
  return addTile(removeTile(overlay, spaceId, fromPage, tileId), spaceId, toPage, tileId)
}

export function reorderTiles(
  overlay: LaunchpadOverlay,
  spaceId: string,
  page: LaunchpadPage,
  fromIndex: number,
  toIndex: number,
): LaunchpadOverlay {
  const key = pageKey(spaceId, page.id)
  const current = overlay.tileOrder[key] ?? page.tiles.map((tile) => tile.id)
  const next = moveIndex(current, fromIndex, toIndex)
  if (!next) {
    return overlay
  }
  if (page.origin === 'custom') {
    return {
      ...overlay,
      customPages: overlay.customPages.map((entry) =>
        entry.id === page.id && entry.spaceId === spaceId ? { ...entry, tileIds: next } : entry,
      ),
      tileOrder: { ...overlay.tileOrder, [key]: next },
    }
  }
  return { ...overlay, tileOrder: { ...overlay.tileOrder, [key]: next } }
}

export function setTileAppearance(
  overlay: LaunchpadOverlay,
  tileId: string,
  title: string,
  description: string,
): LaunchpadOverlay {
  const nextTitle = title.trim()
  const nextDescription = description.trim()
  const tileLabels = { ...overlay.tileLabels }
  const tileDescriptions = { ...overlay.tileDescriptions }
  if (nextTitle) {
    tileLabels[tileId] = nextTitle
  } else {
    delete tileLabels[tileId]
  }
  if (nextDescription) {
    tileDescriptions[tileId] = nextDescription
  } else {
    delete tileDescriptions[tileId]
  }
  return { ...overlay, tileLabels, tileDescriptions }
}

function decoratePage(
  spaceId: string,
  page: LaunchpadPage,
  overlay: LaunchpadOverlay,
  tilesById: Map<string, LaunchpadAppTile>,
  locked: boolean,
): LaunchpadPage {
  const key = pageKey(spaceId, page.id)
  const removed = new Set(overlay.removedTiles[key] ?? [])
  const remaining = page.tiles.filter((tile) => !removed.has(tile.id))
  const ordered = orderTiles(remaining, overlay.tileOrder[key], tilesById)
  return {
    ...page,
    label: overlay.pageLabels[key] ?? page.label,
    tiles: ordered.map((tile) => withAppearance(tile, overlay)),
    origin: 'catalog',
    locked,
    hidden: overlay.hiddenPageIds.includes(key),
  }
}

function decorateCustomPage(
  page: LaunchpadOverlay['customPages'][number],
  overlay: LaunchpadOverlay,
  tilesById: Map<string, LaunchpadAppTile>,
): LaunchpadPage {
  const key = pageKey(page.spaceId, page.id)
  const ordered = orderTiles(
    page.tileIds
      .map((id) => tilesById.get(id))
      .filter((tile): tile is LaunchpadAppTile => tile !== undefined),
    overlay.tileOrder[key],
    tilesById,
  )
  return {
    id: page.id,
    label: page.label || CUSTOM_PAGE_PLACEHOLDER,
    tiles: ordered.map((tile) => withAppearance(tile, overlay)),
    origin: 'custom',
    locked: false,
    hidden: overlay.hiddenPageIds.includes(key),
  }
}

function orderPages(spaceId: string, pages: LaunchpadPage[], overlay: LaunchpadOverlay): LaunchpadPage[] {
  const order = overlay.pageOrder[spaceId]
  if (!order?.length) {
    return pages
  }
  const byId = new Map(pages.map((page) => [page.id, page]))
  const next: LaunchpadPage[] = []
  const seen = new Set<string>()
  for (const id of order) {
    const page = byId.get(id)
    if (page && !seen.has(id)) {
      next.push(page)
      seen.add(id)
    }
  }
  for (const page of pages) {
    if (!seen.has(page.id)) {
      next.push(page)
    }
  }
  return next
}

function orderTiles(
  tiles: LaunchpadAppTile[],
  order: string[] | undefined,
  tilesById: Map<string, LaunchpadAppTile>,
): LaunchpadAppTile[] {
  if (!order?.length) {
    return tiles
  }
  const remaining = new Map(tiles.map((tile) => [tile.id, tile]))
  const next: LaunchpadAppTile[] = []
  for (const id of order) {
    const tile = remaining.get(id) ?? tilesById.get(id)
    if (tile && !next.some((entry) => entry.id === tile.id)) {
      next.push(tile)
      remaining.delete(tile.id)
    }
  }
  return [...next, ...remaining.values()]
}

function withAppearance(tile: LaunchpadAppTile, overlay: LaunchpadOverlay): LaunchpadAppTile {
  return {
    ...tile,
    label: overlay.tileLabels[tile.id] ?? tile.label,
    description: overlay.tileDescriptions[tile.id] ?? tile.description,
  }
}

function moveIndex(items: string[], fromIndex: number, toIndex: number): string[] | null {
  if (fromIndex < 0 || toIndex < 0 || fromIndex >= items.length || toIndex >= items.length || fromIndex === toIndex) {
    return null
  }
  const next = [...items]
  const [moved] = next.splice(fromIndex, 1)
  if (!moved) {
    return null
  }
  next.splice(toIndex, 0, moved)
  return next
}

function stringList(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return []
  }
  return value.filter((entry): entry is string => typeof entry === 'string')
}

function stringRecord(value: unknown): Record<string, string> {
  if (!value || typeof value !== 'object') {
    return {}
  }
  return Object.fromEntries(
    Object.entries(value as Record<string, unknown>).filter(
      (entry): entry is [string, string] => typeof entry[1] === 'string',
    ),
  )
}

function stringRecordList(value: unknown): Record<string, string[]> {
  if (!value || typeof value !== 'object') {
    return {}
  }
  return Object.fromEntries(
    Object.entries(value as Record<string, unknown>)
      .map(([key, entries]) => [key, stringList(entries)] as const)
      .filter((entry) => entry[1].length > 0),
  )
}

function parseCustomPages(value: unknown): LaunchpadOverlay['customPages'] {
  if (!Array.isArray(value)) {
    return []
  }
  return value.flatMap((entry) => {
    if (!entry || typeof entry !== 'object') {
      return []
    }
    const page = entry as Record<string, unknown>
    if (typeof page.id !== 'string' || typeof page.spaceId !== 'string') {
      return []
    }
    return [
      {
        id: page.id,
        spaceId: page.spaceId,
        label: typeof page.label === 'string' ? page.label : CUSTOM_PAGE_PLACEHOLDER,
        tileIds: stringList(page.tileIds),
      },
    ]
  })
}
