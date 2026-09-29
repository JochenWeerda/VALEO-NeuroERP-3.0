import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/agrar/saatgut-liste.tsx'),
  'utf8',
)

describe('Saatgut-Liste UIX', () => {
  it('zeigt Anzeigen und Bearbeiten als 44-px-Text, KPI nur Desktop', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Anzeigen')
    expect(src).toContain('Bearbeiten')
    expect(src).toContain('min-h-touch touch-manipulation')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('title="Anzeigen"')
  })
})
