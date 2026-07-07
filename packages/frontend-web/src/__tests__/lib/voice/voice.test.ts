/**
 * UIX-072: STT-Adapter-Contract + Voice-Navigations-Gate ("Danger nie per Stimme").
 */
import { describe, it, expect, vi } from 'vitest'
import { FakeSttProvider, selectSttProvider, type SttProvider } from '@/lib/voice/stt-provider'
import { compileVoiceNavigation, stripNavPrefix } from '@/lib/voice/voice-navigation'
import type { PaletteCommand } from '@/components/navigation/command-palette-model'

const icon = (() => null) as unknown as PaletteCommand['icon']

const COMMANDS: PaletteCommand[] = [
  { id: 'op', label: 'Offene Posten Debitoren', keywords: ['offene posten', 'op', 'debitoren'], icon, actionId: 'op', actionParams: { path: '/finance/op-debitoren' }, category: 'Finance' },
  { id: 'kunden', label: 'Kunden', keywords: ['kunde', 'kunden'], icon, actionId: 'kunden', actionParams: { path: '/verkauf/kunden-liste' }, category: 'Verkauf' },
]

describe('FakeSttProvider', () => {
  it('start/stop + partial/final/error-Sequenz', () => {
    const p = new FakeSttProvider()
    const partials: string[] = []
    const finals: Array<[string, number | undefined]> = []
    const errors: string[] = []
    p.onPartial((t) => partials.push(t))
    p.onFinal((t, c) => finals.push([t, c]))
    p.onError((e) => errors.push(e.code))

    p.start({ lang: 'de-DE', interim: true })
    expect(p.started).toBe(true)
    p.emitPartial('offene')
    p.emitPartial('offene posten')
    p.emitFinal('offene posten', 0.92)
    p.emitError({ code: 'no-speech', message: 'x' })
    p.stop()

    expect(partials).toEqual(['offene', 'offene posten'])
    expect(finals).toEqual([['offene posten', 0.92]])
    expect(errors).toEqual(['no-speech'])
    expect(p.stopped).toBe(true)
  })
})

describe('selectSttProvider — Fallback-Kette', () => {
  const web = () => new FakeSttProvider({ id: 'webspeech', available: true })
  const webOff = () => new FakeSttProvider({ id: 'webspeech', available: false })
  const server = () => new FakeSttProvider({ id: 'server', available: true })

  it('disabled → null', () => {
    expect(selectSttProvider({ enabled: false, provider: 'webspeech' }, { webspeech: web })).toBeNull()
  })

  it('webspeech verfuegbar → webspeech', () => {
    const p = selectSttProvider({ enabled: true, provider: 'webspeech' }, { webspeech: web, server })
    expect(p?.id).toBe('webspeech')
  })

  it('webspeech nicht verfuegbar → server-Fallback', () => {
    const p = selectSttProvider({ enabled: true, provider: 'webspeech' }, { webspeech: webOff, server })
    expect(p?.id).toBe('server')
  })

  it('kein Provider verfuegbar → null (disabled)', () => {
    const p = selectSttProvider({ enabled: true, provider: 'webspeech' }, { webspeech: webOff })
    expect(p).toBeNull()
  })

  it('provider=server bevorzugt server zuerst', () => {
    const order: string[] = []
    const track = (id: 'webspeech' | 'server', avail: boolean) => (): SttProvider => {
      order.push(id)
      return new FakeSttProvider({ id, available: avail })
    }
    selectSttProvider({ enabled: true, provider: 'server' }, { server: track('server', true), webspeech: track('webspeech', true) })
    expect(order[0]).toBe('server')
  })
})

describe('stripNavPrefix', () => {
  it('entfernt fuehrendes Navigations-Verb', () => {
    expect(stripNavPrefix('zeige offene posten')).toBe('offene posten')
    expect(stripNavPrefix('öffne kunden')).toBe('kunden')
    expect(stripNavPrefix('filtere überfällige rechnungen')).toBe('ueberfaellige rechnungen')
  })
  it('laesst Text ohne Verb unveraendert', () => {
    expect(stripNavPrefix('offene posten')).toBe('offene posten')
  })
})

describe('compileVoiceNavigation — Voice-Gate (nur navigate|none)', () => {
  it('navigiert bei getroffener Maske', () => {
    const plan = compileVoiceNavigation('zeige offene posten', COMMANDS)
    expect(plan.kind).toBe('navigate')
    if (plan.kind === 'navigate') expect(plan.routePath).toContain('/finance/op-debitoren')
  })

  it('none bei keinem Treffer', () => {
    expect(compileVoiceNavigation('qwertz unsinn xyz', COMMANDS).kind).toBe('none')
  })

  it('SICHERHEIT: liefert fuer JEDE Eingabe nur navigate|none — nie ein Command', () => {
    const inputs = [
      'aktivität anlegen kunde',
      'mahnen offene posten',
      'zahlungslauf starten',
      'freigeben rechnung',
      'lösche kunde folkerts',
    ]
    for (const input of inputs) {
      const plan = compileVoiceNavigation(input, COMMANDS)
      expect(['navigate', 'none']).toContain(plan.kind)
    }
  })

  it('leere Eingabe → none', () => {
    expect(compileVoiceNavigation('   ', COMMANDS).kind).toBe('none')
  })
})
