/**
 * UIX-072: STT-Adapter-Contract + Voice-Navigations-Gate ("Danger nie per Stimme").
 */
import { describe, it, expect, vi } from 'vitest'
import { FakeSttProvider, selectSttProvider, type SttProvider } from '@/lib/voice/stt-provider'
import { compileVoiceNavigation, stripNavPrefix } from '@/lib/voice/voice-navigation'
import type { PaletteCommand } from '@/components/navigation/command-palette-model'
import { buildPaletteCommands } from '@/components/navigation/command-palette-model'

const icon = (() => null) as unknown as PaletteCommand['icon']

const COMMANDS: PaletteCommand[] = [
  { id: 'op', label: 'Offene Posten Debitoren', keywords: ['offene posten', 'op', 'debitoren'], icon, actionId: 'op', actionParams: { path: '/finance/op-debitoren' }, category: 'Finance' },
  { id: 'kunden', label: 'Kunden', keywords: ['kunde', 'kunden'], icon, actionId: 'kunden', actionParams: { path: '/verkauf/kunden-liste' }, category: 'Verkauf' },
  { id: 'warteschlange', label: 'Warteschlange', keywords: ['warteschlange', 'waage', 'annahme', 'lkw'], icon, actionId: 'nav-warteschlange', actionParams: { path: '/annahme/warteschlange' }, category: 'Annahme' },
  { id: 'wiegungen', label: 'Wiegungen', keywords: ['wiegung', 'wiegen', 'waage'], icon, actionId: 'nav-wiegungen', actionParams: { path: '/waage/wiegungen' }, category: 'Annahme' },
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

  it('navigiert Annahme/Waage, armert kein Wiegen', () => {
    const queue = compileVoiceNavigation('oeffne warteschlange', COMMANDS)
    expect(queue.kind).toBe('navigate')
    if (queue.kind === 'navigate') expect(queue.routePath).toBe('/annahme/warteschlange')
    const weigh = compileVoiceNavigation('zeige wiegungen', COMMANDS)
    expect(weigh.kind).toBe('navigate')
    if (weigh.kind === 'navigate') expect(weigh.routePath).toBe('/waage/wiegungen')
    expect(compileVoiceNavigation('wiegen lkw', COMMANDS).kind).not.toBe('commandDraft')
  })

  it('oeffnet Rechnungen als Worklist, nicht den Editor', () => {
    const commands = buildPaletteCommands({
      agrarEnabled: false,
      navigationShortcuts: [],
    })
    const plan = compileVoiceNavigation('oeffne rechnungen', commands)
    expect(plan.kind).toBe('navigate')
    if (plan.kind === 'navigate') {
      expect(plan.routePath).toBe('/verkauf/rechnungen')
      expect(plan.routePath).not.toContain('/sales/invoice')
    }
  })

  it('navigiert Kreditoren, Zahlungsvorschlaege und Anlieferavis', () => {
    const commands = buildPaletteCommands({
      agrarEnabled: false,
      navigationShortcuts: [],
    })
    const kreditoren = compileVoiceNavigation('oeffne kreditorenbuchhaltung', commands)
    expect(kreditoren.kind).toBe('navigate')
    if (kreditoren.kind === 'navigate') expect(kreditoren.routePath).toBe('/fibu/kreditoren')
    const vorschlaege = compileVoiceNavigation('oeffne zahlungsvorschlaege', commands)
    expect(vorschlaege.kind).toBe('navigate')
    if (vorschlaege.kind === 'navigate') expect(vorschlaege.routePath).toBe('/fibu/zahlungsvorschlaege')
    const avis = compileVoiceNavigation('oeffne anlieferavis', commands)
    expect(avis.kind).toBe('navigate')
    if (avis.kind === 'navigate') expect(avis.routePath).toBe('/einkauf/anlieferavis-liste')
    const opVerwaltung = compileVoiceNavigation('oeffne op verwaltung', commands)
    expect(opVerwaltung.kind).toBe('navigate')
    if (opVerwaltung.kind === 'navigate') expect(opVerwaltung.routePath).toBe('/fibu/op-verwaltung')
    const auftrag = compileVoiceNavigation('oeffne auftragsbestaetigungen', commands)
    expect(auftrag.kind).toBe('navigate')
    if (auftrag.kind === 'navigate') expect(auftrag.routePath).toBe('/einkauf/auftragsbestaetigungen')
    const lauf = compileVoiceNavigation('oeffne zahlungslaeufe', commands)
    expect(lauf.kind).toBe('navigate')
    if (lauf.kind === 'navigate') expect(lauf.routePath).toBe('/fibu/zahlungslaeufe')
    const anfragen = compileVoiceNavigation('oeffne einkaufsanfragen', commands)
    expect(anfragen.kind).toBe('navigate')
    if (anfragen.kind === 'navigate') expect(anfragen.routePath).toBe('/einkauf/anfragen')
    const opListe = compileVoiceNavigation('oeffne forderungsmanagement', commands)
    expect(opListe.kind).toBe('navigate')
    if (opListe.kind === 'navigate') expect(opListe.routePath).toBe('/fibu/offene-posten')
    const journal = compileVoiceNavigation('oeffne buchungsjournal', commands)
    expect(journal.kind).toBe('navigate')
    if (journal.kind === 'navigate') expect(journal.routePath).toBe('/fibu/buchungsjournal')
    const hauptbuch = compileVoiceNavigation('oeffne hauptbuch', commands)
    expect(hauptbuch.kind).toBe('navigate')
    if (hauptbuch.kind === 'navigate') expect(hauptbuch.routePath).toBe('/fibu/hauptbuch')
    const schnittstelle = compileVoiceNavigation('oeffne buchungsuebergabe', commands)
    expect(schnittstelle.kind).toBe('navigate')
    if (schnittstelle.kind === 'navigate') expect(schnittstelle.routePath).toBe('/fibu/schnittstelle-fibu')
    const buchungsimport = compileVoiceNavigation('oeffne massen-buchungsimport', commands)
    expect(buchungsimport.kind).toBe('navigate')
    if (buchungsimport.kind === 'navigate') expect(buchungsimport.routePath).toBe('/finance/buchungsimport')
    const bwa = compileVoiceNavigation('oeffne bwa-auswertung', commands)
    expect(bwa.kind).toBe('navigate')
    if (bwa.kind === 'navigate') expect(bwa.routePath).toBe('/fibu/bwa')
    const guv = compileVoiceNavigation('oeffne guv-rechnung', commands)
    expect(guv.kind).toBe('navigate')
    if (guv.kind === 'navigate') expect(guv.routePath).toBe('/fibu/guv')
    const lastschriften = compileVoiceNavigation('oeffne lastschriften-debitoren', commands)
    expect(lastschriften.kind).toBe('navigate')
    if (lastschriften.kind === 'navigate') expect(lastschriften.routePath).toBe('/finance/lastschriften-debitoren')
    const elster = compileVoiceNavigation('oeffne elster-online', commands)
    expect(elster.kind).toBe('navigate')
    if (elster.kind === 'navigate') expect(elster.routePath).toBe('/fibu/elster-online')
    const bank = compileVoiceNavigation('oeffne bankabgleich', commands)
    expect(bank.kind).toBe('navigate')
    if (bank.kind === 'navigate') expect(bank.routePath).toBe('/finance/bank-abgleich')
    const bilanz = compileVoiceNavigation('oeffne bilanz', commands)
    expect(bilanz.kind).toBe('navigate')
    if (bilanz.kind === 'navigate') expect(bilanz.routePath).toBe('/fibu/bilanz')
  })
})
