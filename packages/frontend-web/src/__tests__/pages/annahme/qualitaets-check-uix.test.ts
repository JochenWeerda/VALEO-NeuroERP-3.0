import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/annahme/qualitaets-check.tsx'),
  'utf8',
)

describe('Qualitätsprüfung UIX (Waage/QS)', () => {
  it('stellt den Wizard vor dem Theater und macht Zur Abrechnung 44 px', () => {
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<Wizard')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).toContain('className="min-h-touch touch-manipulation"')
    expect(src).not.toMatch(/size="sm"/)
  })
})
