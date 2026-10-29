import { describe, expect, it } from 'vitest'
import * as kopien from '@/masks/capture-screens'
import abbild from '@/masks/screen-registry.snapshot.json'

/**
 * Die eine Quelle der ScreenDefinitions ist die Python-Registry. `capture-screens.ts` wiederholt 31 davon
 * von Hand. Das Abbild `screen-registry.snapshot.json` kommt aus der Registry
 * (`scripts/generate_screen_registry_snapshot.py`, im Backend-Lauf auf Aktualitaet geprueft).
 *
 * Am 13.10.2026 wichen 26 Kopien ab. Diese Liste friert den Stand ein:
 *  - eine neue Kopie oder eine neue Abweichung macht den Test rot;
 *  - eine behobene Abweichung muss hier ausgetragen werden.
 * Ziel ist die leere Liste. Umgestellt wird je Maske mit Sichtpruefung: Die Registry verlangt in elf Masken
 * ein Recht an der Aktion und nennt den Kommando-Weg; die Seiten zeichnen heute ohne Rechte.
 */
const BEKANNTE_ABWEICHUNG: Record<string, string[]> = {
  'admin/postfaecher': ['performance'],
  'fuhrpark/ausgehende-dokumente': ['actions', 'performance'],
  'fuhrpark/fahrzeug-stamm': ['actions', 'performance'],
  'fuhrpark/fahrzeuge': ['performance'],
  'fuhrpark/rechnungen': ['actions', 'performance'],
  'fuhrpark/terminarten': ['actions', 'performance'],
  'logistik/frachtbrief': ['performance'],
  'logistik/frachttabellen': ['actions', 'performance'],
  'logistik/tour-fracht-arbeitsraum': ['performance'],
  'logistik/tourenplanung': ['actions', 'performance'],
  'logistik/verladung': ['performance'],
  'logistik/versandprofile': ['performance'],
  'personal/bewerbung-einwilligung': ['noProcessChainReason', 'performance'],
  'personal/bewerbungen': ['actions', 'performance'],
  'personal/einwilligungserklaerungen': ['actions', 'performance'],
  'personal/onboarding': ['actions', 'performance'],
  'personal/qualifikationen': ['actions', 'performance'],
  'personal/schulungen': ['actions', 'performance'],
  'strecke/disposition': ['performance'],
  'strecke/nawaro-lieferungen': ['performance'],
  'strecke/qualitaets-abweichung': ['performance'],
  'strecke/streckengeschaeft': ['performance'],
  'strecke/vorlaeufig': ['performance'],
  'transporte/fahrer': ['performance'],
  'verkauf/betriebsauftrag': ['performance'],
  'versand/versand-avis': ['performance'],
}

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
