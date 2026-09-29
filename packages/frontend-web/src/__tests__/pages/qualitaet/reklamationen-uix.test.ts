import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/qualitaet/reklamationen.tsx'),
  'utf8',
)

describe('Reklamationen-Liste UIX', () => {
  it('stellt Suche und Tabelle vor dem Fallkopf und öffnet per 44-px-Tipp', () => {
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('Suche Reklamationen')).toBeLessThan(src.indexOf('Reklamationen: {fallkopf.status}'))
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('bg-red-50')
    expect(src).not.toContain('text-red-700')
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).toContain('pendingPath')
  })
})
