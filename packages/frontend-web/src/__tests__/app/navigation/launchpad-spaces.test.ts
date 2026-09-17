import { describe, expect, it } from 'vitest'
import { Truck } from 'lucide-react'
import type { NavItem } from '@/app/navigation/types'
import {
  canonicalizeLaunchpadSpaceId,
  isLaunchpadHiddenNavId,
  launchpadTileKind,
  launchpadTileSurface,
  matchesLaunchpadCatalogQuery,
  resolveLaunchpadSpaces,
} from '@/app/navigation/launchpad-spaces'
import { loadNavSections } from '@/app/navigation/nav-runtime'

const mcp = { businessDomain: 'logistics', scope: 'logistics:read' }

describe('launchpad-spaces', () => {
  it('blendet Flow-Spine-Prozessräume aus dem Launchpad aus', () => {
    expect(isLaunchpadHiddenNavId('workflow-flow-spine-order-to-cash')).toBe(true)
    expect(isLaunchpadHiddenNavId('warteschlange')).toBe(false)
  })

  it('färbt Kacheln über Chart-Slots, nicht über Statusgrün', () => {
    expect(launchpadTileSurface(0).backgroundColor).toContain('--chart-1-hsl')
    expect(launchpadTileSurface(2).borderColor).toContain('--chart-3-hsl')
    expect(launchpadTileSurface(8).backgroundColor).toContain('--chart-other-hsl')
    expect(launchpadTileSurface('kunden').borderLeftColor).toMatch(/--chart-[1-6]-hsl/)
    expect(launchpadTileSurface('kunden')).toEqual(launchpadTileSurface('kunden'))
    expect(launchpadTileSurface('meine-aufgaben', 'task').backgroundColor).toContain('0.4')
    expect(launchpadTileKind('kim-cockpit')).toBe('task')
    expect(launchpadTileKind('kunden')).toBe('app')
    expect(launchpadTileKind('leitstand')).toBe('alert')
    expect(launchpadTileSurface('leitstand', 'alert').backgroundColor).toContain('0.4')
    expect(matchesLaunchpadCatalogQuery({ id: 'waage', label: 'Annahme', path: '/x', description: 'Waage und Hofliste' }, 'waage')).toBe(true)
    expect(matchesLaunchpadCatalogQuery({ id: 'waage', label: 'Annahme', path: '/x' }, 'waage')).toBe(false)
    expect(matchesLaunchpadCatalogQuery({ id: 'warteschlange', label: 'Annahme', path: '/x', keywords: ['waage', 'hofliste'] }, 'waage')).toBe(true)
    expect(matchesLaunchpadCatalogQuery({ id: 'hofliste', label: 'Hofliste', path: '/waage/hofliste' }, 'waage')).toBe(true)
  })

  it('mappt alte Space-IDs auf die Arbeitswelten', () => {
    expect(canonicalizeLaunchpadSpaceId('erfassung')).toBe('ernte')
    expect(canonicalizeLaunchpadSpaceId('maerkte')).toBe('handel')
    expect(canonicalizeLaunchpadSpaceId('organisation')).toBe('steuerung')
    expect(canonicalizeLaunchpadSpaceId('handel')).toBe('handel')
  })

  it('ordnet Annahme nach Ernte und lässt leere Spaces weg', () => {
    const annahme: NavItem = {
      id: 'annahme',
      label: 'Annahme & Waage',
      icon: Truck,
      mcp,
      children: [
        {
          id: 'warteschlange',
          label: 'Warteschlange',
          icon: Truck,
          path: '/annahme/warteschlange',
          mcp,
        },
        {
          id: 'workflow-flow-spine-order-to-cash',
          label: 'Auftrag bis Zahlung',
          icon: Truck,
          path: '/workflow/flow-spine-order-to-cash',
          mcp: { businessDomain: 'workflow', scope: 'workflow:read' },
        },
      ],
    }

    const spaces = resolveLaunchpadSpaces([annahme], 'de')
    const ernte = spaces.find((space) => space.id === 'ernte')
    const steuerung = spaces.find((space) => space.id === 'steuerung')

    expect(spaces.find((space) => space.id === 'erfassung')).toBeUndefined()
    expect(ernte?.pages.map((page) => page.id)).toEqual(['waage'])
    expect(ernte?.pages[0]?.tiles.map((tile) => tile.label)).toEqual(['Warteschlange'])
    expect(spaces.some((space) => space.pages.some((page) => page.tiles.some((tile) => tile.label === 'Auftrag bis Zahlung')))).toBe(false)
    expect(steuerung?.pages.some((page) => page.tiles.some((tile) => tile.path === '/workflow/leitstand'))).toBe(true)
  })

  it('lässt denselben Beleg in mehreren Arbeitswelten stehen', async () => {
    const sections = await loadNavSections()
    const spaces = resolveLaunchpadSpaces(sections, 'de')
    const tileIdsIn = (spaceId: string) =>
      new Set(
        spaces
          .find((space) => space.id === spaceId)
          ?.pages.flatMap((page) => page.tiles.map((tile) => tile.id)) ?? [],
      )

    const handel = tileIdsIn('handel')
    const ernte = tileIdsIn('ernte')
    const finanzen = tileIdsIn('finanzen')
    const logistik = tileIdsIn('logistik')

    expect(handel.has('kontrakt-uebersicht') && ernte.has('kontrakt-settlement')).toBe(true)
    expect(handel.has('kunden') && finanzen.has('kunden') && logistik.has('kunden')).toBe(true)
  })

  it('löst echte Nav-Pfade für die sechs Arbeitswelten auf', async () => {
    const sections = await loadNavSections()
    const spaces = resolveLaunchpadSpaces(sections, 'de')
    const ids = spaces.map((space) => space.id)

    expect(ids).toEqual(['handel', 'ernte', 'logistik', 'betriebsmittel', 'finanzen', 'steuerung'])
    expect(spaces.flatMap((space) => space.pages).every((page) => page.tiles.length > 0 && page.tiles.length <= 10)).toBe(true)
    const kunden = spaces.find((space) => space.id === 'handel')?.pages.find((page) => page.id === 'kunden')
    expect(kunden?.tiles.map((tile) => tile.id)).toEqual(['kunden', 'kim-cockpit', 'meine-aufgaben'])
    expect(kunden?.tiles.some((tile) => tile.id === 'kunden-cockpit' || tile.id === 'kontakte' || tile.id === 'kunden-schnellauswahl')).toBe(false)
    const warteschlange = spaces
      .flatMap((space) => space.pages)
      .flatMap((page) => page.tiles)
      .find((tile) => tile.id === 'warteschlange')
    expect(warteschlange).toBeDefined()
    expect(matchesLaunchpadCatalogQuery(warteschlange!, 'waage')).toBe(true)
    expect(
      spaces
        .flatMap((space) => space.pages)
        .flatMap((page) => page.tiles)
        .some((tile) => tile.id.includes('flow-spine')),
    ).toBe(false)
  })
})
