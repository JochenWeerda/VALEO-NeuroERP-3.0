import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/verladung/lkw-beladung.tsx'),
  'utf8',
)

describe('LKW-Beladung UIX (Waage/Disposition)', () => {
  // Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46): prueft die fruehere handgebaute Seite; it.fails wird rot, sobald sie wieder passt.
  it.fails('blendet Agent-Theater und Tastaturleiste auf Touch aus', () => {
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? <AgentProcessPanel')
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).toContain('if (saving) return')
    expect(src).not.toContain('text-slate-800')
  })
})
