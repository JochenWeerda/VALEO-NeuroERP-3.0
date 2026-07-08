import { describe, expect, it } from 'vitest'
import { NAV_SECTIONS } from '@/app/navigation/manifest'
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
})
