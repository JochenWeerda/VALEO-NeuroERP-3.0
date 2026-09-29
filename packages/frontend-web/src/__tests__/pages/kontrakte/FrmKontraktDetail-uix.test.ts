import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/kontrakte/FrmKontraktDetail.tsx'),
  'utf8',
)

describe('Kontrakt-Detail UIX', () => {
  it('zeigt Operator-h1 und 44-px-Speichern vor dem DS-Theater', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Neuer Kontrakt')
    expect(src).not.toContain('>FrmKontraktDetail<')
    expect(src).toContain('min-h-touch touch-manipulation')
    expect(src).toContain('variant="register"')
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).not.toContain('bg-red-50')
    expect(src).not.toContain('size="sm"')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('<OperationalCaseHeader')
  })
})
