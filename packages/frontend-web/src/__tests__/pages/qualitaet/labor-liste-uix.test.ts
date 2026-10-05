import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/qualitaet/labor-liste.tsx'),
  'utf8',
)

describe('Labor-Liste UIX', () => {
  it('stellt Suche und Tabelle vor dem Theater und öffnet per 44-px-Tipp', () => {
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<h1')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('Suche Laboraufträge')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('text-blue-600')
    expect(src).toContain('min-h-touch gap-2 touch-manipulation')
  })
})
