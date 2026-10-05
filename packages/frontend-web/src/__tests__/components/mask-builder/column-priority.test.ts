import { describe, expect, it } from 'vitest'
import { columnsForWidth } from '@/components/mask-builder/renderers/column-priority'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { fuhrparkFahrzeugeScreen } from '@/masks/capture-screens'

describe('Spaltenpriorität', () => {
  const plan = compileRenderPlanFromScreenDefinition(fuhrparkFahrzeugeScreen)
  const columns = plan.tablesByKey.list.columns

  it('lässt Kennzeichen und Status bei schmaler Breite stehen', () => {
    expect(columnsForWidth(columns, 640).map((column) => column.key)).toEqual(['kennzeichen', 'status'])
  })

  it('blendet die Inspektion vor Typ und km-Stand aus', () => {
    expect(columnsForWidth(columns, 800).map((column) => column.key)).toEqual([
      'kennzeichen', 'status', 'typ', 'kilometerstand',
    ])
    expect(columnsForWidth(columns, 1200).map((column) => column.key)).toContain('naechste_inspektion')
  })

  it('behält Spalten ohne Priorität', () => {
    expect(columnsForWidth([{ key: 'offen' }], 400).map((column) => column.key)).toEqual(['offen'])
  })
})
