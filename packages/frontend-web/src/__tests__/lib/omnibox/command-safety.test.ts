/**
 * UIX-070: Sicherheitsmatrix-Tabelle + Slot-Filling.
 * Spiegelt tests/test_uix070_conversational_safety.py auf der Frontend-Seite.
 */
import { describe, it, expect } from 'vitest'
import {
  classifyOmniboxAction,
  fillPayloadDraft,
  buildCommandIntent,
  type OmniboxActionInput,
  type OmniboxActionDisposition,
} from '@/lib/omnibox/command-safety'
import type { ActionDangerLevel } from '@/components/mask-builder/schema'

type Row = {
  danger: ActionDangerLevel
  forbidden: boolean
  confirm: boolean
  confidence: number
  expected: OmniboxActionDisposition
}

const MATRIX: Row[] = [
  // forbiddenForAgents → immer unsichtbar
  { danger: 'safe', forbidden: true, confirm: false, confidence: 1, expected: 'unavailable' },
  { danger: 'moderate', forbidden: true, confirm: true, confidence: 1, expected: 'unavailable' },
  { danger: 'critical', forbidden: true, confirm: true, confidence: 1, expected: 'unavailable' },
  // high/critical → nur Navigation
  { danger: 'high', forbidden: false, confirm: true, confidence: 1, expected: 'navigateOnly' },
  { danger: 'critical', forbidden: false, confirm: false, confidence: 1, expected: 'navigateOnly' },
  // moderate → immer Ritual (bei hoher Konfidenz)
  { danger: 'moderate', forbidden: false, confirm: false, confidence: 1, expected: 'ritual' },
  { danger: 'moderate', forbidden: false, confirm: true, confidence: 0.9, expected: 'ritual' },
  // safe → Ritual nur mit Confirmation, sonst Prefill
  { danger: 'safe', forbidden: false, confirm: true, confidence: 1, expected: 'ritual' },
  { danger: 'safe', forbidden: false, confirm: false, confidence: 1, expected: 'formPrefill' },
  // Konfidenz < 0.75 → degradiert (ausser unsichtbar/navigateOnly)
  { danger: 'moderate', forbidden: false, confirm: true, confidence: 0.74, expected: 'formPrefill' },
  { danger: 'safe', forbidden: false, confirm: true, confidence: 0.5, expected: 'formPrefill' },
  { danger: 'high', forbidden: false, confirm: true, confidence: 0.1, expected: 'navigateOnly' },
  { danger: 'critical', forbidden: true, confirm: true, confidence: 0.1, expected: 'unavailable' },
]

describe('classifyOmniboxAction — Sicherheitsmatrix', () => {
  for (const row of MATRIX) {
    it(`${row.danger}/forbidden=${row.forbidden}/confirm=${row.confirm}@${row.confidence} → ${row.expected}`, () => {
      expect(
        classifyOmniboxAction(
          { dangerLevel: row.danger, requiresConfirmation: row.confirm, forbiddenForAgents: row.forbidden },
          row.confidence,
        ),
      ).toBe(row.expected)
    })
  }

  it('umgeht nie eine Masken-Confirmation: moderate/safe+confirm ergeben bei hoher Konfidenz Ritual', () => {
    for (const danger of ['safe', 'moderate'] as ActionDangerLevel[]) {
      const d = classifyOmniboxAction({ dangerLevel: danger, requiresConfirmation: true, forbiddenForAgents: false }, 1)
      expect(d).toBe('ritual')
    }
  })
})

describe('fillPayloadDraft — type-aware Slot-Filling', () => {
  it('mappt Datum/Zahl/Text auf passende Feldtypen', () => {
    const { payloadDraft, missingFields } = fillPayloadDraft(
      [
        { key: 'datum', type: 'date', required: true },
        { key: 'menge', type: 'number' },
        { key: 'betreff', type: 'text', required: true },
        { key: 'notiz', type: 'textarea' },
      ],
      { date: '2026-07-10', number: 42, text: 'Rueckruf Folkerts' },
    )
    expect(payloadDraft).toMatchObject({ datum: '2026-07-10', menge: 42, betreff: 'Rueckruf Folkerts', notiz: 'Rueckruf Folkerts' })
    expect(missingFields).toEqual([])
  })

  it('listet Pflichtfelder ohne Wert als missingFields', () => {
    const { missingFields } = fillPayloadDraft(
      [{ key: 'datum', type: 'date', required: true }, { key: 'betreff', type: 'text', required: true }],
      { text: 'nur Text' },
    )
    expect(missingFields).toEqual(['datum'])
  })

  it('bevorzugt eindeutig aufgeloeste Lookups', () => {
    const { payloadDraft } = fillPayloadDraft(
      [{ key: 'kunde_id', type: 'lookup', required: true }],
      { lookups: { kunde_id: 'K-10233' } },
    )
    expect(payloadDraft.kunde_id).toBe('K-10233')
  })
})

describe('buildCommandIntent', () => {
  const navCommand = { id: 'nav-x', label: 'X', keywords: [], icon: (() => null) as never, actionId: 'nav-x', category: 'x' }

  function input(overrides: Partial<OmniboxActionInput['action']> = {}): OmniboxActionInput {
    return {
      screenId: 'crm/customer-360',
      routePath: '/verkauf/kunden-liste',
      action: { key: 'create_activity', label: 'Aktivitaet anlegen', dangerLevel: 'safe', requiresConfirmation: false, forbiddenForAgents: false, fields: [{ key: 'betreff', type: 'text', required: true }], ...overrides },
    }
  }

  it('forbiddenForAgents → null (unsichtbar)', () => {
    expect(buildCommandIntent(input({ forbiddenForAgents: true }), {}, 1, navCommand)).toBeNull()
  })

  it('high/critical → NavigateIntent', () => {
    const plan = buildCommandIntent(input({ dangerLevel: 'high' }), {}, 1, navCommand)
    expect(plan?.kind).toBe('navigate')
  })

  it('moderate → commandDraft mit Payload + missingFields', () => {
    const plan = buildCommandIntent(input({ dangerLevel: 'moderate' }), { text: 'Anruf' }, 1, navCommand)
    expect(plan?.kind).toBe('commandDraft')
    if (plan?.kind === 'commandDraft') {
      expect(plan.payloadDraft).toMatchObject({ betreff: 'Anruf' })
      expect(plan.missingFields).toEqual([])
    }
  })

  it('safe ohne Confirmation → formPrefill', () => {
    const plan = buildCommandIntent(input(), { text: 'Notiz' }, 1, navCommand)
    expect(plan?.kind).toBe('formPrefill')
  })

  it('Konfidenz < 0.75 → formPrefill statt Ritual', () => {
    const plan = buildCommandIntent(input({ dangerLevel: 'moderate', requiresConfirmation: true }), { text: 'x' }, 0.6, navCommand)
    expect(plan?.kind).toBe('formPrefill')
  })
})
