import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../components/mask-builder/specialized/intake/registration-renderer.tsx'),
  'utf8',
)
const controller = readFileSync(resolve(__dirname, '../../../components/mask-builder/specialized/intake/registration-controller.ts'), 'utf8')
const entry = readFileSync(resolve(__dirname, '../../../pages/annahme/lkw-registrierung.tsx'), 'utf8')

describe('LKW-Registrierung UIX (Waage)', () => {
  it('stellt den Wizard vor dem Theater und blendet Tastaturleiste auf Touch aus', () => {
    expect(entry).toContain('IntakeWeighingPage screenId="annahme/lkw-registrierung"')
    expect(controller).toContain('useTouchDevice')
    expect(src.indexOf('<Wizard')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).toContain('text-status-info')
    expect(src).not.toContain('text-blue-700')
    expect(src).toContain('min-h-touch touch-manipulation')
    expect(controller).toContain("if (submitting || !canDomainAction(plan, 'register')")
    expect(controller).toContain('fieldsEditable(plan')
  })
})
