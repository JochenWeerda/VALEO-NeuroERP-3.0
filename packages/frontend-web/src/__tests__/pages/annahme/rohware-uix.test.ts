import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/annahme/rohware.tsx'),
  'utf8',
)

describe('Rohware-Annahme UIX', () => {
  it('stellt den Wizard vor dem Fallkopf und entfernt Rohblau', () => {
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<Wizard')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).toContain('if (createAcceptance.isPending) return')
    expect(src).not.toContain('text-blue-700')
    expect(src).not.toContain('text-slate-800')
  })
})
