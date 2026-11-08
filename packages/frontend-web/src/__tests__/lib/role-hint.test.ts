import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { rollenHinweis } from '@/lib/role-hint'

describe('rollenHinweis', () => {
  it('nennt die noetigen Rollen woertlich und laesst admin und manager weg', () => {
    const detail = "Insufficient role. Required: ('FINANCE_BEARBEITEN', 'FINANCE_ADMIN', 'admin', 'manager')"
    expect(rollenHinweis(detail)).toBe(
      'Dafür fehlt Ihnen die Berechtigung. Nötig ist eine dieser Rollen: FINANCE_BEARBEITEN, FINANCE_ADMIN. Bitte wenden Sie sich an Ihre Administration.',
    )
  })

  it('spricht bei einer einzigen Rolle von der Rolle', () => {
    expect(rollenHinweis("Insufficient role. Required: ('FINANCE_ADMIN', 'admin')")).toBe(
      'Dafür fehlt Ihnen die Berechtigung. Nötig ist die Rolle FINANCE_ADMIN. Bitte wenden Sie sich an Ihre Administration.',
    )
  })

  it('bleibt verstaendlich, wenn nur allgemeine Rollen verlangt sind', () => {
    expect(rollenHinweis("Insufficient role. Required: ('admin',)")).toBe(
      'Dafür fehlt Ihnen die Berechtigung. Bitte wenden Sie sich an Ihre Administration.',
    )
  })

  it('laesst jede andere Meldung in Ruhe', () => {
    expect(rollenHinweis('Dieses Konto gehoert zum gemeinsamen Kontenrahmen.')).toBeNull()
    expect(rollenHinweis('Der Mandant der Anfrage (X-Tenant-ID) ist nicht der Mandant der Anmeldung.')).toBeNull()
    expect(rollenHinweis(undefined)).toBeNull()
    expect(rollenHinweis([{ msg: 'field required' }])).toBeNull()
  })

  it('haengt am Antwort-Interceptor — eine Stelle fuer alle Masken', () => {
    const src = readFileSync(resolve(__dirname, '../../lib/api-client.ts'), 'utf8')
    expect(src).toContain("error.response?.status === 403")
    expect(src).toContain('rollenHinweis(')
    // Viele Abfragen einer Maske scheitern zugleich: eine Meldung, nicht zwanzig.
    expect(src).toContain("id: 'fehlende-berechtigung'")
  })
})
