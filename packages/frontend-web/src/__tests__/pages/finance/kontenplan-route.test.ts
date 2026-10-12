import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

// Die Maske unter /finance/kontenplan ist am 12.10.2026 abgeloest: Speichern meldete
// „Gespeichert“ und sendete nichts, die Felder (Periode, Steuerschluessel, Anfangsbestand)
// kennt der Weg nicht. Der Pfad zeigt die Pflegemaske, die wirklich anlegt und aendert.
describe('Kontenplan: ein Weg, eine Pflegemaske', () => {
  it('fuehrt /finance/kontenplan zur Pflegemaske', () => {
    const { aliases } = JSON.parse(read('../../../app/route-aliases.json')) as { aliases: Array<{ module: string; path: string }> }
    const ziel = (pfad: string) => aliases.filter((e) => e.path === pfad).map((e) => e.module)
    expect(ziel('finance/kontenplan')).toEqual(['@/pages/finance/chart-of-accounts'])
    expect(ziel('finance/chart-of-accounts')).toEqual(['@/pages/finance/chart-of-accounts'])
  })

  it('kennt die Huelle nicht mehr', () => {
    expect(() => read('../../../pages/finance/kontenplan.tsx')).toThrow()
    expect(read('../../../app/routing/route-tree.gen.tsx')).not.toContain('@/pages/finance/kontenplan')
  })

  it('die Pflegemaske speichert ueber den Finanzdienst, nicht ueber eine Erfolgsmeldung', () => {
    const src = read('../../../pages/finance/chart-of-accounts.tsx')
    expect(src).toContain('financeService.createAccount')
    expect(src).toContain('financeService.updateAccount')
    expect(src).toContain('financeService.deleteAccount')
  })
})
