import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/psm/sachkunde-register.tsx'),
  'utf8',
)

describe('PSM-Sachkunde UIX', () => {
  it('stellt Nachweise 44 px und blendet KPI auf Touch aus', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Suche Sachkundenachweise')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-orange-50')
  })
})
