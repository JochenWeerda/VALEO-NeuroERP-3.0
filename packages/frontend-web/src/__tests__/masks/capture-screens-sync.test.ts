import { describe, expect, it } from 'vitest'
import * as kopien from '@/masks/capture-screens'
import abbild from '@/masks/screen-registry.snapshot.json'

/** Both frontend projections must match the authored Python registry exactly.
 * The backend generator checks reject stale checked-in copies; this frontend check
 * also catches omitted exports and runtime value differences after TypeScript compilation.
 */
const BEKANNTE_ABWEICHUNG: Record<string, string[]> = {}

type Definition = Record<string, unknown>

function geordnet(wert: unknown): unknown {
  if (Array.isArray(wert)) return wert.map(geordnet)
  if (wert && typeof wert === 'object') {
    return Object.fromEntries(
      Object.keys(wert as Definition).sort((a, b) => a.localeCompare(b)).map((k) => [k, geordnet((wert as Definition)[k])]),
    )
  }
  return wert
}

function abweichendeTeile(kopie: Definition, quelle: Definition): string[] {
  const teile = new Set([...Object.keys(kopie), ...Object.keys(quelle)])
  teile.delete('agentContract') // gehoert dem Server und den Agenten
  return [...teile]
    .filter((teil) => JSON.stringify(geordnet(kopie[teil])) !== JSON.stringify(geordnet(quelle[teil])))
    .sort((a, b) => a.localeCompare(b))
}

const exporte = abbild.exports as Record<string, string>
const quellen = abbild.screens as Record<string, Definition>
const kopierte = Object.entries(kopien as Record<string, unknown>)
  .filter(([, wert]) => wert !== null && typeof wert === 'object' && 'id' in (wert as Definition)) as Array<[string, Definition]>

describe('ScreenDefinitions: die Kopie im Frontend gegen die Registry', () => {
  it('kennt jede Kopie — eine neue Handkopie gibt es nicht', () => {
    expect(kopierte.map(([name]) => name).sort((a, b) => a.localeCompare(b))).toEqual(Object.keys(exporte).sort((a, b) => a.localeCompare(b)))
  })

  it.each(kopierte)('%s weicht nur dort ab, wo es bekannt ist', (name, kopie) => {
    const kennung = exporte[name]
    expect(kopie.id).toBe(kennung)
    expect(abweichendeTeile(kopie, quellen[kennung])).toEqual(BEKANNTE_ABWEICHUNG[kennung] ?? [])
  })

  it('fuehrt keine Abweichung fuer eine Maske, die es als Kopie nicht gibt', () => {
    const kennungen = new Set(Object.values(exporte))
    expect(Object.keys(BEKANNTE_ABWEICHUNG).filter((k) => !kennungen.has(k))).toEqual([])
  })
})
