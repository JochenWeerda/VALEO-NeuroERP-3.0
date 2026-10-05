import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/kulturpflanzen/liste.tsx'),
  'utf8',
)

describe('Kulturpflanzen-Liste UIX', () => {
  it('öffnet Kulturen per 44-px-Tipp und stellt Suche vor KPI', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Suche Kulturpflanzen')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('{!isTouch ? (')
    expect(src).not.toContain('text-blue-600')
  })
})
