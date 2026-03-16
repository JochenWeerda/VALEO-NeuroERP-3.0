import { describe, expect, it } from 'vitest'
import { buildPaletteCommands } from '@/components/navigation/command-palette-model'

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
