import { describe, expect, it } from 'vitest'
import { NAV_SECTIONS, type NavItem } from '@/app/navigation/manifest'
import { findLabelInManifest } from '@/components/navigation/Breadcrumbs'

describe('Breadcrumb manifest matching', () => {
  it('prefers the Artikel-Stammdaten entry for article maintenance routes', () => {
    expect(findLabelInManifest(NAV_SECTIONS, 'artikel')).toEqual({
      sectionLabel: 'Artikel-Stammdaten',
      itemLabel: 'Artikelstamm',
    })

    expect(findLabelInManifest(NAV_SECTIONS, 'artikel/neu')).toEqual({
      sectionLabel: 'Artikel-Stammdaten',
      itemLabel: 'Artikel neu anlegen',
    })
  })

  it('keeps falling back when the manifest has no matching route', () => {
    expect(findLabelInManifest(NAV_SECTIONS, 'unbekannt/neu')).toEqual({})
  })

  it('prefers exact route matches across the full ERP navigation suite', () => {
    const entriesByPath = new Map<string, NavigationEntry[]>()

    for (const entry of collectNavigationEntries(NAV_SECTIONS)) {
      const entries = entriesByPath.get(entry.path) ?? []
      entries.push(entry)
      entriesByPath.set(entry.path, entries)
    }

    for (const [path, exactEntries] of entriesByPath) {
      const result = findLabelInManifest(NAV_SECTIONS, path)
      const exactLabels = exactEntries.map((entry) => entry.itemLabel)
      expect(exactLabels, `${path} must resolve to an exact nav item, not a shorter prefix`).toContain(result.itemLabel)

      const exactSectionLabels = exactEntries.map((entry) => entry.sectionLabel)
      if (result.sectionLabel) {
        expect(exactSectionLabels, `${path} must resolve inside the exact nav section`).toContain(result.sectionLabel)
      } else {
        expect(exactEntries.some((entry) => !entry.sectionLabel), `${path} must resolve as a top-level exact nav item`).toBe(true)
      }
    }
  })
})

type NavigationEntry = {
  path: string
  itemLabel: string
  sectionLabel?: string
}

function collectNavigationEntries(items: NavItem[]): NavigationEntry[] {
  return items.flatMap((section) => collectSectionEntries(section, section))
}

function collectSectionEntries(item: NavItem, section: NavItem): NavigationEntry[] {
  const isTopLevel = item.id === section.id
  const path = item.path?.replace(/^\/+|\/+$/g, '') ?? ''
  const current = path
    ? [{
        path,
        itemLabel: item.label,
        sectionLabel: isTopLevel ? undefined : section.label,
      }]
    : []

  return [
    ...current,
    ...(item.children ?? []).flatMap((child) => collectSectionEntries(child, section)),
  ]
}
