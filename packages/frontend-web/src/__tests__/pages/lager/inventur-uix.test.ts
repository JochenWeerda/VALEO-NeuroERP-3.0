import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/lager/inventur.tsx'),
  'utf8',
)

describe('Inventur UIX (Disposition)', () => {
  it('stellt Tabelle und Abschluss vor dem Fallkopf und nutzt 44-px-Ziele', () => {
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<DataTable')).toBeLessThan(src.indexOf('Inventur-Status:'))
    expect(src).toContain('min-h-touch min-w-touch')
    expect(src).toContain('stornierenPendingId')
    expect(src).toContain('border-status-warning/40')
    expect(src).not.toContain('text-green-700')
    expect(src).not.toContain('text-amber-700')
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
  })
})
