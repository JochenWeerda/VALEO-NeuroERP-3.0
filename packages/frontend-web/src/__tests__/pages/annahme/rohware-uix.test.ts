import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const entry = readFileSync(resolve(__dirname, '../../../pages/annahme/rohware.tsx'), 'utf8')
const renderer = readFileSync(
  resolve(__dirname, '../../../components/mask-builder/specialized/intake/rohware-renderer.tsx'),
  'utf8',
)
const controller = readFileSync(
  resolve(__dirname, '../../../components/mask-builder/specialized/intake/rohware-controller.ts'),
  'utf8',
)

describe('Rohware-Annahme UIX', () => {
  it('verdrahtet IntakeWeighingPage mit Screen-ID', () => {
    expect(entry).toContain('IntakeWeighingPage screenId="annahme/rohware"')
  })

  it('stellt den Wizard vor dem Fallkopf und entfernt Rohblau', () => {
    expect(controller).toContain('useTouchDevice')
    expect(renderer.indexOf('<Wizard')).toBeLessThan(renderer.indexOf('<OperationalCaseHeader'))
    expect(renderer).toContain('{!isTouch ? <KeyboardShortcutBar')
    expect(controller).toContain('if (submitting) return')
    expect(renderer).not.toContain('text-blue-700')
    expect(renderer).not.toContain('text-slate-800')
  })

  it('postet auf den Compat-Endpunkt rohware', () => {
    expect(controller).toContain('/api/v1/agrar/harvest-acceptance/rohware')
  })
})
