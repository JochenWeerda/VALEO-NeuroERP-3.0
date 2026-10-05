import { describe, expect, it } from 'vitest'
import { mapEinkaufLsPositions, type EinkaufLSResponse } from '@/pages/einkauf/lieferschein-erfassung'

const sample: EinkaufLSResponse = {
  id: 'ls-1',
  tenant_id: 'system',
  lieferschein_nr: 'E2026-ABC',
  liefer_nr: 'L-9',
  lieferschein_datum: '2026-09-17',
  niederlassung: 'Hof',
  bediener: 'JD',
  lieferant_id: 'sup-1',
  lieferant_name: 'Saatgut GmbH',
  zahlungsbedingung: null,
  texte: null,
  zwischenhaendler: null,
  wie_vom_ls: false,
  erledigt: false,
  netto_betrag: '10.00',
  mwst_betrag: '1.90',
  brutto_betrag: '11.90',
  summe_gewicht: null,
  created_at: '2026-09-17T10:00:00',
  updated_at: '2026-09-17T10:00:00',
  positionen: [
    {
      id: 'p-1',
      pos_nr: 10,
      artikel_nr: 'ART-1',
      lieferant_artikel_nr: 'L-ART',
      bezeichnung: 'Weizen',
      gebinde_nr: null,
      gebinde: null,
      menge: '2',
      einheit: 't',
      einzelpreis: '5',
      nettobetrag: '10',
      lagerhalle: null,
      lagerfach: null,
      charge: 'C-1',
      serien_nr: null,
      kontakt: null,
      prozent: '0',
      master_nr: null,
    },
  ],
}

describe('mapEinkaufLsPositions', () => {
  it('rechnet Brutto aus Netto und Menge', () => {
    const rows = mapEinkaufLsPositions(sample)
    expect(rows).toHaveLength(1)
    expect(rows[0].artikelNr).toBe('ART-1')
    expect(rows[0].menge).toBe(2)
    expect(rows[0].bruttoPreis).toBeCloseTo(5.95, 2)
    expect(rows[0].bruttoBetrag).toBeCloseTo(11.9, 2)
    expect(rows[0].charge).toBe('C-1')
  })

  it('liefert leere Liste ohne Positionen', () => {
    expect(mapEinkaufLsPositions({ ...sample, positionen: [] })).toEqual([])
  })
})
