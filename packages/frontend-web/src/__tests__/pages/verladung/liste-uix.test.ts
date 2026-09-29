import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/verladung/liste.tsx'),
  'utf8',
)

describe('Verladungen-Liste UIX', () => {
  it('stellt Suche und Tabelle vor den KPI-Karten und macht CTAs 44 px', () => {
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('Suche Verladungen')).toBeLessThan(src.indexOf('Verladungen Heute'))
    expect(src).toContain('min-h-touch gap-2 touch-manipulation')
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).not.toContain('border-indigo-500')
  })
})
