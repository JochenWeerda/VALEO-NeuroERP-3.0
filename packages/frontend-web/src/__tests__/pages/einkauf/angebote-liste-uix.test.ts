import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/einkauf/angebote-liste.tsx'),
  'utf8',
)

describe('Einkauf-Angebotsliste UIX', () => {
  it('stellt ListReport vor dem DS-Theater und blendet Theater auf Touch aus', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('<ListReport')
    expect(src.indexOf('<ListReport')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-11')
    expect(src).toContain('text-primary')
  })
})
