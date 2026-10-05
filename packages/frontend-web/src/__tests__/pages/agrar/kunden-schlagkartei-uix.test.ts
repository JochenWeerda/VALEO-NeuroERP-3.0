import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/kunden-schlagkartei.tsx'),
  'utf8',
)

describe('Kunden-Schlagkartei UIX', () => {
  it('stellt Lohnspritz 44 px und blendet KPI auf Touch aus', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch touch-manipulation')
    expect(src).toContain('Lohnspritz')
    expect(src).toContain('Zurück')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-amber-50')
  })
})
