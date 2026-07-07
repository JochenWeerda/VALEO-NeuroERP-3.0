/**
 * UIX-070: NL-Command-Erkennung aus der Omnibox (detectCommandIntent).
 */
import { describe, it, expect } from 'vitest'
import { detectCommandIntent } from '@/lib/omnibox/command-compiler'
import type { OmniboxAction } from '@/lib/api/mask-registry'

const navCommand = { id: 'nav-x', label: 'X', keywords: [], icon: (() => null) as never, actionId: 'nav-x', category: 'x' }

const createActivity: OmniboxAction = {
  key: 'create_activity',
  label: 'Aktivitaet anlegen',
  dangerLevel: 'safe',
  requiresConfirmation: false,
  forbiddenForAgents: false,
  verbs: ['aktivitaet', 'anlegen', 'create', 'activity'],
  fields: [{ key: 'betreff', type: 'text', required: true }],
}

const wareneingang: OmniboxAction = {
  key: 'wareneingang',
  label: 'Wareneingang buchen',
  dangerLevel: 'moderate',
  requiresConfirmation: true,
  forbiddenForAgents: false,
  verbs: ['wareneingang', 'buchen'],
  fields: [],
}

const forbidden: OmniboxAction = {
  key: 'stornieren',
  label: 'Stornieren',
  dangerLevel: 'high',
  requiresConfirmation: true,
  forbiddenForAgents: true,
  verbs: ['stornieren', 'storno'],
  fields: [],
}

function input(actions: OmniboxAction[]) {
  return { screenId: 'crm/customer-360', route: '/verkauf/kunden-liste', actions, navigateCommand: navCommand }
}

describe('detectCommandIntent', () => {
  it('erkennt safe-Aktion ohne Confirmation als formPrefill + Freitext', () => {
    const plan = detectCommandIntent('aktivitaet anlegen folkerts', input([createActivity]), { confidence: 0.9 })
    expect(plan?.kind).toBe('formPrefill')
    if (plan?.kind === 'formPrefill') {
      expect(plan.actionKey).toBe('create_activity')
      expect(plan.payloadDraft).toMatchObject({ betreff: 'folkerts' })
    }
  })

  it('erkennt moderate-Aktion als commandDraft (Ritual)', () => {
    const plan = detectCommandIntent('wareneingang buchen', input([wareneingang]), { confidence: 0.9 })
    expect(plan?.kind).toBe('commandDraft')
  })

  it('forbiddenForAgents-Aktion bleibt unsichtbar (null)', () => {
    const plan = detectCommandIntent('stornieren', input([forbidden]), { confidence: 0.9 })
    expect(plan).toBeNull()
  })

  it('ohne Aktions-Verb → null (reiner Navigations-Plan bleibt)', () => {
    const plan = detectCommandIntent('offene posten folkerts', input([createActivity]), { confidence: 0.9 })
    expect(plan).toBeNull()
  })

  it('niedrige Konfidenz degradiert moderate-Aktion auf formPrefill', () => {
    const plan = detectCommandIntent('wareneingang buchen', input([wareneingang]), { confidence: 0.6 })
    expect(plan?.kind).toBe('formPrefill')
  })
})
