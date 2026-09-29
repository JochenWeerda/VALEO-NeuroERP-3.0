import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/kontrakte/KontraktPositionsmonitor.tsx'),
  'utf8',
)

describe('Positionsmonitor UIX', () => {
  it('öffnet Artikel per Tipp und stellt die Tabelle vor den KPI-Karten', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Positionsübersicht pro Artikel')
    expect(src).toContain('min-h-11 font-mono text-xs text-primary')
    expect(src).not.toContain('onDoubleClick')
    expect(src).not.toContain('bg-red-50')
    expect(src).toContain('className="h-11 w-11"')
    expect(src).not.toContain('bg-green-100')
    expect(src).not.toContain('bg-red-600')
    expect(src.indexOf('<h1')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
  })
})
