import { describe, expect, it } from 'vitest'
import { rechnungStatus, zuRechnung } from '@/lib/api/sales'

/**
 * FSX-RECHNUNGSMASKE — die Faktura-Liste liest jetzt echte Belege.
 *
 * Bis `GET /sales/invoices` existierte, lief der Abruf in einen 404 und das
 * `catch` machte daraus eine leere Liste. Seit es den Endpunkt gibt, ist die
 * Zuordnung der Feldnamen die Stelle, an der still Unsinn entstehen koennte:
 * `invoice_number` ist nicht `nummer`, und ein fehlendes Faelligkeitsdatum ist
 * kein 1.1.1970.
 */

describe('rechnungStatus', () => {
  it('haelt den Entwurf als Entwurf fest', () => {
    expect(rechnungStatus('entwurf')).toBe('entwurf')
  })

  it('liest eine gebuchte Rechnung als offene Forderung', () => {
    expect(rechnungStatus('gebucht')).toBe('offen')
  })

  it('erfindet weder Teilzahlung noch Ueberfaelligkeit', () => {
    // Beide haengen am Zahlungsstand, den der Beleg nicht fuehrt.
    expect(rechnungStatus('bezahlt')).toBe('bezahlt')
    expect(rechnungStatus('storniert')).toBe('storniert')
    expect(rechnungStatus(undefined)).toBe('entwurf')
  })
})

describe('zuRechnung', () => {
  it('bildet den Beleg auf die Listenzeile ab', () => {
    const zeile = zuRechnung({
      id: 'RE-ID',
      invoice_number: 'RE-0001',
      customer_id: 'K-100',
      invoice_date: '2026-09-15',
      due_date: '2026-10-15',
      status: 'gebucht',
      net_amount: '2500',
      gross_amount: '2675',
      line_count: 2,
    })

    expect(zeile).toEqual({
      id: 'RE-ID',
      nummer: 'RE-0001',
      datum: '2026-09-15',
      kunde: 'K-100',
      auftragsNr: '',
      betrag: 2675,
      faelligAm: '2026-10-15',
      status: 'offen',
      positionen: 2,
    })
  })

  it('macht aus einer fehlenden Faelligkeit kein Datum', () => {
    expect(zuRechnung({ id: 'x', due_date: null }).faelligAm).toBe('')
  })

  it('unterscheidet null Positionen von unbekannt', () => {
    expect(zuRechnung({ id: 'x', line_count: 0 }).positionen).toBe(0)
    expect(zuRechnung({ id: 'x' }).positionen).toBeUndefined()
  })

  it('nimmt den Bruttobetrag, und den Nettobetrag nur ersatzweise', () => {
    expect(zuRechnung({ id: 'x', net_amount: '100', gross_amount: '119' }).betrag).toBe(119)
    expect(zuRechnung({ id: 'x', net_amount: '100' }).betrag).toBe(100)
  })
})
