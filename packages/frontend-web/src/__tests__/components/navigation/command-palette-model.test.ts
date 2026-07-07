import { describe, expect, it } from 'vitest'
import { FileText } from 'lucide-react'
import {
  buildPaletteCommands,
  enrichCommandsWithOmniboxCatalog,
  type PaletteCommand,
} from '@/components/navigation/command-palette-model'
import type { OmniboxCatalogEntry } from '@/lib/api/mask-registry'

function makeCommand(overrides: Partial<PaletteCommand> = {}): PaletteCommand {
  return {
    id: 'nav-op-debitoren',
    label: 'Offene Posten Debitoren',
    keywords: ['offene posten', 'op'],
    icon: FileText,
    actionId: 'nav-op-debitoren',
    actionParams: { path: '/finance/op-debitoren' },
    category: 'Finance',
    ...overrides,
  }
}

function catalogEntry(overrides: Partial<OmniboxCatalogEntry> = {}): OmniboxCatalogEntry {
  return {
    screen_id: 'finance/ar-open-item',
    title: 'Offene Posten Debitoren',
    domain: 'finance',
    floorplan: 'listReport',
    route: '/finance/op-debitoren',
    synonyms: ['debitoren-op', 'forderungen'],
    example_prompts: ['offene posten folkerts'],
    filterable_fields: [],
    ...overrides,
  }
}

describe('buildPaletteCommands', () => {
  it('haengt Klasse-A/B-Masken aus der Mask Registry an die Palette an', () => {
    const commands = buildPaletteCommands({
      agrarEnabled: true,
      navigationShortcuts: [],
      maskRegistry: [
        {
          mask_id: 'finance/abschluss',
          route: '/finance/abschluss',
          label: 'Periodenabschluss-Arbeitsplatz',
          domain: 'finance',
          mask_class: 'A',
          process_key: 'closing_checklist',
          explainability: 'required',
          requires_approval_ui: true,
          gobd_relevant: true,
          wave1_contract: true,
          schema_version: 1,
        },
        {
          mask_id: 'finance/index',
          route: '/finance',
          label: 'Finance Uebersicht',
          domain: 'finance',
          mask_class: 'C',
          process_key: null,
          explainability: 'optional',
          requires_approval_ui: false,
          gobd_relevant: false,
          wave1_contract: true,
          schema_version: 1,
        },
      ],
    })

    const processCommand = commands.find((command) => command.id === 'mask:finance/abschluss')

    expect(processCommand).toBeDefined()
    expect(processCommand?.category).toBe('Kernprozesse')
    expect(processCommand?.actionParams).toMatchObject({
      path: '/finance/abschluss',
      maskClass: 'A',
      processKey: 'closing_checklist',
    })
    expect(commands.some((command) => command.id === 'mask:finance/index')).toBe(false)
  })

  it('filtert Agrar-Masken heraus wenn das Feature deaktiviert ist', () => {
    const commands = buildPaletteCommands({
      agrarEnabled: false,
      navigationShortcuts: [],
      maskRegistry: [
        {
          mask_id: 'annahme/abrechnung',
          route: '/annahme/abrechnung',
          label: 'Ernte-Annahme Abrechnung',
          domain: 'agrar',
          mask_class: 'A',
          process_key: 'harvest_acceptance',
          explainability: 'required',
          requires_approval_ui: true,
          gobd_relevant: true,
          wave1_contract: true,
          schema_version: 1,
        },
      ],
    })

    expect(commands.some((command) => command.id === 'mask:annahme/abrechnung')).toBe(false)
  })
})

describe('enrichCommandsWithOmniboxCatalog', () => {
  it('haengt Katalog-Synonyme + Beispiel-Prompts an einen bestehenden Command mit gleicher Route', () => {
    const result = enrichCommandsWithOmniboxCatalog([makeCommand()], [catalogEntry()], true)
    const op = result.find((command) => command.id === 'nav-op-debitoren')
    expect(op?.keywords).toEqual(
      expect.arrayContaining(['offene posten', 'op', 'debitoren-op', 'forderungen', 'offene posten folkerts']),
    )
    // keine Synthese, wenn der Command schon existiert
    expect(result.some((command) => command.id === 'omnibox:finance/ar-open-item')).toBe(false)
  })

  it('dedupliziert Synonyme case-insensitive und mutiert die Eingabe nicht', () => {
    const original = makeCommand({ keywords: ['Offene Posten'] })
    const result = enrichCommandsWithOmniboxCatalog(
      [original],
      [catalogEntry({ synonyms: ['offene posten', 'forderungen'], example_prompts: [] })],
      true,
    )
    const op = result.find((command) => command.id === 'nav-op-debitoren')
    expect(op?.keywords.filter((k) => k.toLowerCase() === 'offene posten')).toHaveLength(1)
    expect(original.keywords).toEqual(['Offene Posten']) // Original unveraendert
  })

  it('matcht Routen unabhaengig von Query-String und Trailing-Slash', () => {
    const command = makeCommand({ actionParams: { path: '/finance/op-debitoren/?tab=1' } })
    const result = enrichCommandsWithOmniboxCatalog([command], [catalogEntry()], true)
    const op = result.find((c) => c.id === 'nav-op-debitoren')
    expect(op?.keywords).toContain('forderungen')
  })

  it('synthetisiert einen Command fuer Katalog-Routen ohne passenden Command', () => {
    const result = enrichCommandsWithOmniboxCatalog(
      [],
      [catalogEntry({ screen_id: 'qualitaet/reklamation', domain: 'qualitaet', title: 'Reklamationen', route: '/qualitaet/reklamationen', synonyms: ['beanstandung'] })],
      true,
    )
    const synth = result.find((command) => command.id === 'omnibox:qualitaet/reklamation')
    expect(synth).toBeDefined()
    expect(synth?.actionParams).toMatchObject({ path: '/qualitaet/reklamationen', screenId: 'qualitaet/reklamation' })
    expect(synth?.keywords).toEqual(expect.arrayContaining(['qualitaet/reklamation', 'beanstandung']))
  })

  it('unterdrueckt Agrar-Katalogeintraege wenn das Feature deaktiviert ist', () => {
    const result = enrichCommandsWithOmniboxCatalog(
      [],
      [catalogEntry({ screen_id: 'agrar/duenger', domain: 'agrar', route: '/agrar/duenger' })],
      false,
    )
    expect(result.some((command) => command.id === 'omnibox:agrar/duenger')).toBe(false)
  })

  it('ueberspringt Eintraege ohne Route und gibt bei leerem Katalog die Eingabe zurueck', () => {
    const base = [makeCommand()]
    expect(enrichCommandsWithOmniboxCatalog(base, undefined, true)).toBe(base)
    const result = enrichCommandsWithOmniboxCatalog([], [catalogEntry({ route: '' })], true)
    expect(result).toHaveLength(0)
  })
})
