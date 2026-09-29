import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/lager/lagerplaetze.tsx'),
  'utf8',
)

describe('Lagerplätze UIX', () => {
  it('stellt WMS-Struktur zuerst und nutzt 44-px-Ziele ohne Rohfarben', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('NativeSelect')
    expect(src).toContain('Lager wählen')
    expect(src).toContain('min-h-touch touch-manipulation')
    expect(src).toContain('h-11 w-11')
    expect(src).toContain('{!isLoading && !isTouch ? (')
    expect(src).not.toContain('/api/v1/lager/wms')
    expect(src).not.toContain('border-orange-500')
    expect(src).not.toContain('bg-red-600')
    expect(src).not.toContain('size="sm"')
  })
})
