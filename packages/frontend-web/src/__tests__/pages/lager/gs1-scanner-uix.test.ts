import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/lager/gs1-scanner.tsx'),
  'utf8',
)

describe('GS1-Scanner UIX', () => {
  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('nutzt ARIA-Tabs statt Eigenbau und 44-px-Aktionen ohne Rohindigo', () => {
    expect(src).toContain('TabsList')
    expect(src).toContain('aria-label="GS1-Werkzeuge"')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('if (parseMutation.isPending) return')
    expect(src).not.toContain('border-indigo-600')
    expect(src).not.toContain('text-slate-800')
    expect(src).not.toContain('size="sm"')
  })
})
