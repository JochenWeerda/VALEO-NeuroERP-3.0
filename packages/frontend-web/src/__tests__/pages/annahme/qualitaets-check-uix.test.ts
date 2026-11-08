import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../components/mask-builder/specialized/intake/quality-renderer.tsx'),
  'utf8',
)
const controller = readFileSync(resolve(__dirname, '../../../components/mask-builder/specialized/intake/quality-controller.tsx'), 'utf8')
const entry = readFileSync(resolve(__dirname, '../../../pages/annahme/qualitaets-check.tsx'), 'utf8')

describe('Qualitätsprüfung UIX (Waage/QS)', () => {
  it('stellt den Wizard vor dem Theater und macht Zur Abrechnung 44 px', () => {
    expect(entry).toContain('IntakeWeighingPage screenId="annahme/qualitaets-check"')
    expect(controller).toContain('useTouchDevice')
    expect(src.indexOf('<Wizard')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).toContain('finishDisabled={!canDomainAction')
    expect(controller).toContain("billing: goToAbrechnung")
    expect(src).not.toMatch(/size="sm"/)
  })
})
