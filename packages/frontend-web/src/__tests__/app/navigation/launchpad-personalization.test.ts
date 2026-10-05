import { describe, expect, it } from 'vitest'
import {
  EMPTY_LAUNCHPAD_OVERLAY,
  addCustomPage,
  addTile,
  applyLaunchpadOverlay,
  deletePage,
  hidePage,
  moveTileToPage,
  parseLaunchpadOverlay,
  removeTile,
  renamePage,
  reorderTiles,
  resetPage,
  setTileAppearance,
} from '@/app/navigation/launchpad-personalization'
import type { LaunchpadSpace } from '@/app/navigation/launchpad-spaces'

const catalog: LaunchpadSpace[] = [
  {
    id: 'ernte',
    label: 'Ernte & Warenannahme',
    pages: [
      {
        id: 'waage',
        label: 'Annahme & Waage',
        origin: 'catalog',
        locked: true,
        tiles: [
          { id: 'warteschlange', label: 'Warteschlange', path: '/annahme/warteschlange' },
          { id: 'wiegungen', label: 'Wiegungen', path: '/annahme/wiegungen' },
        ],
      },
      {
        id: 'labor',
        label: 'Qualität & Labor',
        origin: 'catalog',
        locked: false,
        tiles: [{ id: 'proben', label: 'Proben', path: '/qs/proben' }],
      },
    ],
  },
]

describe('launchpad-personalization', () => {
  it('blendet Katalogseiten aus, aber nicht die gesperrte Startgruppe', () => {
    const hiddenLabor = hidePage(EMPTY_LAUNCHPAD_OVERLAY, 'ernte', catalog[0]!.pages[1]!)
    const hiddenLocked = hidePage(hiddenLabor, 'ernte', catalog[0]!.pages[0]!)
    const applied = applyLaunchpadOverlay(catalog, hiddenLocked)

    expect(applied[0]?.pages.map((page) => page.id)).toEqual(['waage'])
    expect(hiddenLocked.hiddenPageIds).toEqual(['ernte:labor'])
  })

  it('entfernt Kacheln und setzt die Kataloggruppe zurück', () => {
    const removed = removeTile(EMPTY_LAUNCHPAD_OVERLAY, 'ernte', catalog[0]!.pages[0]!, 'wiegungen')
    expect(applyLaunchpadOverlay(catalog, removed)[0]?.pages[0]?.tiles.map((tile) => tile.id)).toEqual(['warteschlange'])

    const reset = resetPage(removed, 'ernte', catalog[0]!.pages[0]!)
    expect(applyLaunchpadOverlay(catalog, reset)[0]?.pages[0]?.tiles.map((tile) => tile.id)).toEqual([
      'warteschlange',
      'wiegungen',
    ])
  })

  it('legt Nutzergruppen an und löscht nur diese', () => {
    const created = addCustomPage(EMPTY_LAUNCHPAD_OVERLAY, 'ernte', '')
    expect(created.overlay.customPages[0]?.label).toBe('Neue Gruppe')
    const withTile = addTile(created.overlay, 'ernte', {
      id: created.pageId,
      label: 'Neue Gruppe',
      origin: 'custom',
      locked: false,
      tiles: [],
    }, 'warteschlange')
    const applied = applyLaunchpadOverlay(catalog, withTile)
    const custom = applied[0]?.pages.find((page) => page.id === created.pageId)
    expect(custom?.tiles.map((tile) => tile.id)).toEqual(['warteschlange'])

    const catalogDelete = deletePage(withTile, 'ernte', catalog[0]!.pages[1]!)
    expect(catalogDelete.customPages).toHaveLength(1)
    const deleted = deletePage(withTile, 'ernte', custom!)
    expect(deleted.customPages).toHaveLength(0)
  })

  it('verschiebt und benennt Kacheln, verwirft Drift', () => {
    const moved = moveTileToPage(
      EMPTY_LAUNCHPAD_OVERLAY,
      'ernte',
      catalog[0]!.pages[0]!,
      catalog[0]!.pages[1]!,
      'wiegungen',
    )
    const labeled = setTileAppearance(moved, 'wiegungen', 'Waagenbuch', 'Tageswiegungen')
    const reordered = reorderTiles(labeled, 'ernte', {
      ...catalog[0]!.pages[1]!,
      tiles: [
        { id: 'proben', label: 'Proben', path: '/qs/proben' },
        { id: 'wiegungen', label: 'Waagenbuch', path: '/annahme/wiegungen' },
      ],
    }, 1, 0)
    const applied = applyLaunchpadOverlay(catalog, reordered)
    const labor = applied[0]?.pages.find((page) => page.id === 'labor')
    expect(labor?.tiles.map((tile) => tile.id)).toEqual(['wiegungen', 'proben'])
    expect(labor?.tiles[0]?.label).toBe('Waagenbuch')

    const drifted = parseLaunchpadOverlay({
      version: 1,
      tileOrder: { 'ernte:waage': ['ghost', 'warteschlange'] },
      customPages: [{ id: 1 }],
    })
    expect(applyLaunchpadOverlay(catalog, drifted)[0]?.pages[0]?.tiles.map((tile) => tile.id)).toEqual([
      'warteschlange',
      'wiegungen',
    ])
  })

  it('benennt Gruppen um', () => {
    const renamed = renamePage(EMPTY_LAUNCHPAD_OVERLAY, 'ernte', catalog[0]!.pages[1]!, 'Labor')
    expect(applyLaunchpadOverlay(catalog, renamed)[0]?.pages[1]?.label).toBe('Labor')
  })
})
