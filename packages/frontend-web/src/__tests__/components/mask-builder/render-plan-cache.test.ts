import { describe, expect, it } from 'vitest'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { financeSteuerschluesselScreen } from '@/masks/capture-screens'

// Der Bauplan liegt im Cache. Was eine Seite zur Laufzeit an der ScreenDefinition aendert, muss im
// Cache-Schluessel stehen — sonst zeichnet der Builder den vorigen Zustand.
describe('Bauplan-Cache', () => {
  const offen: ScreenDefinition = financeSteuerschluesselScreen
  const feld = (schema: ScreenDefinition, key: string) => {
    const plan = compileRenderPlanFromScreenDefinition(schema, { permissions: [] })
    return Object.values(plan.fieldsByKey).find((f) => f.key === key)
  }

  it('uebernimmt einen zur Laufzeit gesetzten Schreibschutz', () => {
    expect(feld(offen, 'code')?.readOnly).toBe(false)
    const gesperrt: ScreenDefinition = {
      ...offen,
      fields: offen.fields.map((f) => ({ ...f, readOnly: f.key === 'code' })),
    }
    expect(feld(gesperrt, 'code')?.readOnly).toBe(true)
    expect(feld(gesperrt, 'bezeichnung')?.readOnly).toBe(false)
    expect(feld(offen, 'code')?.readOnly).toBe(false)
  })

  it('uebernimmt einen geaenderten Untertitel', () => {
    const plan = compileRenderPlanFromScreenDefinition({ ...offen, subtitle: 'Schlüssel 3 bearbeiten' }, { permissions: [] })
    expect(JSON.stringify(plan)).toContain('Schlüssel 3 bearbeiten')
  })
})
