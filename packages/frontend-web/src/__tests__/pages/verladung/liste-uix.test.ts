import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/verladung/liste.tsx'),
  'utf8',
)

describe('Verladungen-Liste UIX', () => {
  it('zeichnet die Verladung ueber den Masken-Builder und oeffnet die Beladung', () => {
    expect(src).toContain('CaptureScreenHost')
    expect(src).toContain('logistik/verladung')
    expect(src).toContain("navigate('/verladung/lkw-beladung')")
    expect(src).not.toContain('Neuer Frachtbrief')
  })
})
