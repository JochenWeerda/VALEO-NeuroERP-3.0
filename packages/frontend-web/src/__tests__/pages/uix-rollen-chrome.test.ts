import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('UIX Rollen-Chrome 44 px', () => {
  it('stellt FIBU-Suite-Ribbon und Darstellung auf 44 px, deutsch', () => {
    const src = read('../../layouts/FibuSuiteLayout.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Karten')
    expect(src).toContain('Dunkle Darstellung')
    expect(src).not.toMatch(/size="sm"/)
    expect(src).not.toContain('aria-label="Dark"')
  })

  it('stellt Benachrichtigungen, Copilot und Waage-Freigabe auf 44 px', () => {
    const notes = read('../../components/ui/notification-center.tsx')
    expect(notes).toContain('min-h-touch px-2')
    expect(notes).toContain('Alle lesen')
    expect(notes).not.toMatch(/size="sm"/)
    expect(read('../../components/ai/AskVALEO.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../components/copilot/AskValeo.tsx')).not.toMatch(/size="sm"/)
    const weigh = read('../../features/weighing/Weighing.tsx')
    expect(weigh).toContain('Freigeben')
    expect(weigh).toContain('min-h-touch')
    expect(weigh).not.toMatch(/size="sm"/)
  })

  it('stellt Anruf, IntentBar und Dubletten ohne Hover-only-Label', () => {
    const call = read('../../components/cti/CallWidget.tsx')
    expect(call).toContain('Annehmen')
    expect(call).toContain('min-h-touch')
    expect(call).toContain('aria-label="Anruf halten"')
    expect(call).not.toMatch(/size="sm"/)
    const intent = read('../../components/crm/IntentBar.tsx')
    expect(intent).not.toContain('hidden sm:inline')
    expect(intent).toContain('min-h-touch')
    const dup = read('../../components/crm/DuplicateWarning.tsx')
    expect(dup).toContain('Auswählen')
    expect(dup).toContain('Kandidatenstamm öffnen')
    expect(dup).not.toMatch(/size="sm"/)
  })
})
