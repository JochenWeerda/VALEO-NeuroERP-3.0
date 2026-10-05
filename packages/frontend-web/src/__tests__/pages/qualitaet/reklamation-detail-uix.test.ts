import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/qualitaet/reklamation-detail.tsx'),
  'utf8',
)

describe('Reklamation-Detail UIX', () => {
  it('stellt Identität und Statuswechsel vor dem Theater und macht Ziele 44 px', () => {
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<h1')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('variant="register"')
    expect(src).toContain('min-h-touch min-w-touch')
    expect(src).toContain('transitioning')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('size="icon"')
  })
})
