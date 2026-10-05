import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const src = readFileSync(
  resolve(__dirname, '../../../pages/waage/wiegeschein-detail.tsx'),
  'utf8',
)

describe('Wiegeschein-Detail UIX (Waage)', () => {
  it('nutzt Register statt Eigenbau-Reiter und blendet Theater auf Touch aus', () => {
    expect(src).toContain('variant="register"')
    expect(src).toContain('aria-label="Wiegeschein"')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(src).not.toMatch(/size="sm"/)
    expect(src).not.toContain('border-green-500')
    expect(src).not.toContain('allokieren')
  })
})
