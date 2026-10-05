import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/lager/einlagerung.tsx'),
  'utf8',
)

describe('Einlagerung UIX (Disposition)', () => {
  it('stellt den Wizard vor dem Fallkopf und nutzt Status-Tokens', () => {
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<Wizard')).toBeLessThan(src.indexOf('Einlagerung: {fallkopf.status}'))
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).toContain('border-status-success/40')
    expect(src).not.toContain('text-green-700')
    expect(src).not.toContain('text-blue-700')
  })
})
