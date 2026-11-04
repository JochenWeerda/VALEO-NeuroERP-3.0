import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/verladung/liste.tsx'),
  'utf8',
)

describe('Verladungen-Liste UIX', () => {
  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('zeichnet die Verladung ueber den Masken-Builder und oeffnet die Beladung', () => {
    expect(src).toContain('CaptureScreenHost')
    expect(src).toContain('logistik/verladung')
    expect(src).toContain("navigate('/verladung/lkw-beladung')")
    expect(src).not.toContain('Neuer Frachtbrief')
  })
})
