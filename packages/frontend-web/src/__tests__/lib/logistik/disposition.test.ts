import { describe, expect, it } from 'vitest'
import { dispositionsstand, tourenHeuteFuerFahrer } from '@/lib/logistik/disposition'

const heute = '2026-10-02'
const bezug = new Date('2026-10-02T12:00:00Z')

describe('Dispositionsstand', () => {
  it('bleibt rot, solange Fahrzeug oder Fahrer fehlen', () => {
    const stand = dispositionsstand([
      { datum: heute, status: 'geplant', fahrzeug: 'F-1', fahrer: '—' },
    ], false, bezug)
    expect(stand.label).toBe('Disposition offen')
    expect(stand.status).toBe('offen')
  })

  it('wird grün, wenn die heutige Tour besetzt ist und keine Charge sperrt', () => {
    const stand = dispositionsstand([
      { datum: heute, status: 'geplant', fahrzeug: 'F-1', fahrer: 'DR-1' },
    ], false, bezug)
    expect(stand).toMatchObject({ status: 'disponierbar', label: 'Disponierbar', tone: 'success' })
  })

  it('meldet keine Tour und eine Sperre vor der Besetzung', () => {
    expect(dispositionsstand([], false, bezug).label).toBe('Keine Tour')
    expect(dispositionsstand([
      { datum: heute, status: 'geplant', fahrzeug: 'F-1', fahrer: 'DR-1' },
    ], true, bezug).label).toBe('Disposition offen')
  })

  it('zählt heutige Touren eines Fahrers und ignoriert das Speicherfeld', () => {
    const touren = [
      { datum: heute, status: 'geplant', fahrer: 'DR-1' },
      { datum: heute, status: 'storniert', fahrer: 'DR-1' },
      { datum: '2026-09-01', status: 'geplant', fahrer: 'DR-1' },
      { datum: heute, status: 'unterwegs', fahrer: 'DR-2' },
    ]
    expect(tourenHeuteFuerFahrer(touren, 'DR-1', bezug)).toBe(1)
  })
})
