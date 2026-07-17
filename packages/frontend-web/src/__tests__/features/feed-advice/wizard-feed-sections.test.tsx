/**
 * FEED-WIZ-051 (TDD-Red-Welle 2, FE): Wizard-Futterliste als Bereichsansicht —
 * Rauhfutter / Feuchtfutter / Mehl- & Eiweissschrote / Mineralfutter /
 * Sonstige Ergaenzer / Wasser; je Bereich gefuellte Zeilen mit Nummern-Spalte
 * und eine permanente leere Picker-Zeile (Auswahl fuellt die Zeile, die
 * naechste leere Zeile bleibt). Vor der Implementierung geschrieben.
 */
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  WizardFeedSections,
  sectionForFeed,
  type SectionFeed,
} from '@/features/feed-advice/WizardFeedSections'

function feed(overrides: Partial<SectionFeed>): SectionFeed {
  return {
    id: 'f-x', name: 'Feed', nummer: null, futterart: '',
    tmPct: 35, me: 10.5, selected: false, ...overrides,
  }
}

describe('sectionForFeed (DLG-FUTTERART → Bereich)', () => {
  it.each([
    ['Grundfutter, Grobfutter', 'rauhfutter'],
    ['Grundfutter, Saftfutter', 'feuchtfutter'],
    ['Konzentratfutter, Feuchtkonzentrate', 'feuchtfutter'],
    ['Konzentratfutter, Trockenkonzentrate, Einzelfutter', 'schrote'],
    ['Konzentratfutter, Trockenkonzentrate, Zusatzstoffe', 'ergaenzer'],
  ])('%s → %s', (futterart, expected) => {
    expect(sectionForFeed(feed({ futterart }))).toBe(expected)
  })

  it('erkennt Mineralfutter und Wasser am Namen/der Klasse', () => {
    expect(sectionForFeed(feed({ name: 'Mineralfutter Universal', futterart: 'mineral' }))).toBe('mineralfutter')
    expect(sectionForFeed(feed({ name: 'Viehsalz', futterart: 'Zusatz' }))).toBe('mineralfutter')
    expect(sectionForFeed(feed({ name: 'Wasser', futterart: '' }))).toBe('wasser')
  })
})

describe('WizardFeedSections', () => {
  const onSelect = vi.fn()
  const onRemove = vi.fn()
  const onMinChange = vi.fn()
  const onMaxChange = vi.fn()

  const FEEDS: SectionFeed[] = [
    feed({ id: 'dlg_1', name: 'Ackergras, Herbst', nummer: '10010010',
           futterart: 'Grundfutter, Grobfutter', selected: true }),
    feed({ id: 'dlg_2', name: 'Maissilage', nummer: '20050020',
           futterart: 'Grundfutter, Saftfutter', selected: false }),
    feed({ id: 'cat_1', name: 'Energiekraftfutter 18/3', nummer: 'KF-0815',
           futterart: 'Konzentratfutter, Trockenkonzentrate, Einzelfutter', selected: false }),
  ]

  beforeEach(() => {
    onSelect.mockReset(); onRemove.mockReset()
    onMinChange.mockReset(); onMaxChange.mockReset()
  })

  function renderSections(feeds: SectionFeed[] = FEEDS): void {
    render(<WizardFeedSections feeds={feeds} unit="FM"
      minFm={{}} maxFm={{}}
      onSelect={onSelect} onRemove={onRemove}
      onMinChange={onMinChange} onMaxChange={onMaxChange} />)
  }

  it('zeigt alle sechs Bereiche mit leerer Picker-Zeile', () => {
    renderSections()
    for (const label of ['Rauhfutter', 'Feuchtfutter', 'Mehl- & Eiweißschrote',
                         'Mineralfutter', 'Sonstige Ergänzer', 'Wasser']) {
      const section = screen.getByRole('region', { name: label })
      expect(within(section).getByPlaceholderText(/Futtermittel wählen/)).toBeInTheDocument()
    }
  })

  it('rendert gewaehlte Zeilen im richtigen Bereich mit Nummern-Spalte', () => {
    renderSections()
    const rauhfutter = screen.getByRole('region', { name: 'Rauhfutter' })
    expect(within(rauhfutter).getByText('Ackergras, Herbst')).toBeInTheDocument()
    expect(within(rauhfutter).getByText('10010010')).toBeInTheDocument()
    // nicht gewaehlte Futter erscheinen nicht als Zeile
    const feucht = screen.getByRole('region', { name: 'Feuchtfutter' })
    expect(within(feucht).queryByText('Maissilage')).not.toBeInTheDocument()
  })

  it('Picker: Fokus zeigt Bereichs-Futter, Auswahl fuellt die Zeile', async () => {
    renderSections()
    const feucht = screen.getByRole('region', { name: 'Feuchtfutter' })
    const picker = within(feucht).getByPlaceholderText(/Futtermittel wählen/)

    await userEvent.click(picker)
    const option = await within(feucht).findByRole('option', { name: /Maissilage/ })
    await userEvent.click(option)

    expect(onSelect).toHaveBeenCalledWith('dlg_2')
    expect(picker).toHaveValue('')
  })

  it('Picker filtert nach Suchtext und zeigt die Nummer in der Option', async () => {
    renderSections()
    const schrote = screen.getByRole('region', { name: 'Mehl- & Eiweißschrote' })
    const picker = within(schrote).getByPlaceholderText(/Futtermittel wählen/)
    await userEvent.type(picker, 'KF-08')
    const option = await within(schrote).findByRole('option', { name: /Energiekraftfutter/ })
    expect(option).toHaveTextContent('KF-0815')
  })

  it('gewaehlte Zeile hat Min/Max-Eingaben und Entfernen', async () => {
    renderSections()
    const rauhfutter = screen.getByRole('region', { name: 'Rauhfutter' })
    await userEvent.type(within(rauhfutter).getByLabelText(/Min .*Ackergras/), '5')
    expect(onMinChange).toHaveBeenCalledWith('dlg_1', 5)
    await userEvent.click(within(rauhfutter).getByRole('button', { name: /Ackergras.*entfernen/i }))
    expect(onRemove).toHaveBeenCalledWith('dlg_1')
  })

  it('leerer Wasser-Bereich benennt die Luecke statt still leer zu sein', () => {
    renderSections()
    const wasser = screen.getByRole('region', { name: 'Wasser' })
    expect(within(wasser).getByText(/keine Position im Katalog/i)).toBeInTheDocument()
  })
})
