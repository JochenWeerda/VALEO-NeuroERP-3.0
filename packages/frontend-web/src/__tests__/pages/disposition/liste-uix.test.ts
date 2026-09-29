import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/disposition/liste.tsx'),
  'utf8',
)

describe('Disposition-Liste UIX', () => {
  it('stellt die Tabelle vor den KPI-Karten und macht den CTA 44 px', () => {
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<DataTable')).toBeLessThan(src.indexOf('Artikel in Dispo'))
    expect(src).toContain('min-h-touch touch-manipulation')
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).not.toContain('bg-red-50')
  })
})
