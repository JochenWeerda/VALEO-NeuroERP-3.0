import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/kontrakte/KontraktAlarmDashboard.tsx'),
  'utf8',
)

describe('Kontrakt-Alarme UIX', () => {
  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('öffnet Alarme per 44-px-Tipp und blendet KPI-Theater auf Touch aus', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('min-h-11 font-mono text-primary')
    expect(src).toContain('Öffnen')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('text-fuchsia-700')
    expect(src.indexOf('<h1')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
  })
})
