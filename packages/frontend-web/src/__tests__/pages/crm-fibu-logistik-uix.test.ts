import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('CRM/FIBU/Logistik UIX', () => {
  it('stellt Fuhrpark 44 px und blendet Theater auf Touch aus', () => {
    const src = read('../../pages/fuhrpark/fahrzeuge.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-11 font-mono font-medium text-primary')
    expect(src).toContain('Suche Fahrzeuge')
    expect(src).toContain('handleExport')
    expect(src).not.toContain('text-blue-600')
  })

  it('stellt Warengruppen beschriftet 44 px', () => {
    const src = read('../../pages/einkauf/warengruppen.tsx')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Bearbeiten')
    expect(src).toContain('Deaktivieren')
    expect(src).toContain('Speichern')
    expect(src).not.toContain('text-blue-600')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Debitoren-Liste 44 px ohne Rohorange', () => {
    const src = read('../../pages/fibu/debitoren.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('min-h-11 font-mono font-medium text-primary')
    expect(src).toContain('Suche Debitoren')
    expect(src).not.toContain('bg-orange-50')
    expect(src).not.toContain('text-blue-600')
  })

  it('stellt Benachrichtigungen lokal als gelesen', () => {
    const src = read('../../pages/benachrichtigungen/liste.tsx')
    expect(src).toContain('gelesenIds')
    expect(src).toContain('Als gelesen markieren')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('{!isTouch ? (')
  })

  it('stellt Bankkonten-Export und 44 px', () => {
    const src = read('../../pages/banken/konten.tsx')
    expect(src).toContain('handleExport')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Suche Bankkonten')
  })

  it('stellt Kunden-mailto ohne Hover-Blau', () => {
    const src = read('../../pages/crm/kunden-liste.tsx')
    expect(src).toContain('text-primary touch-manipulation')
    expect(src).not.toContain('text-blue-600 hover:underline')
  })

  it('stellt Kampagnen 44 px mit Export', () => {
    const src = read('../../pages/marketing/kampagnen.tsx')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Suche Kampagnen')
    expect(src).not.toContain('text-blue-600')
  })

  it('stellt Schulungen mit wirkenden Filtern', () => {
    const src = read('../../pages/personal/schulungen.tsx')
    expect(src).toContain('nurPsm')
    expect(src).toContain('nurAblaufende')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).not.toContain('bg-orange-50')
  })

  it('stellt Verbindlichkeiten NativeSelect und 44 px', () => {
    const src = read('../../pages/fibu/verbindlichkeiten.tsx')
    expect(src).toContain('NativeSelect')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('Suche Verbindlichkeiten')
  })

  it('stellt Kreditoren Arbeit zuerst und 44 px', () => {
    const src = read('../../pages/fibu/kreditoren.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Suche Kreditoren')
    expect(src).toContain('min-h-11 font-mono font-medium text-primary')
    expect(src).not.toContain('bg-green-50')
    expect(src).not.toContain('border-green-500')
  })

  it('stellt Zahlungsvorschlaege Arbeit zuerst mit 44-px-Auswahl', () => {
    const src = read('../../pages/fibu/zahlungsvorschlaege.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Suche Zahlungsvorschlaege')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Zahlungslauf erstellen')
  })

  it('stellt Anlieferavis Liste zuerst und echten Export', () => {
    const src = read('../../pages/einkauf/anlieferavis-liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('exportToCSV')
    expect(src).toContain('Import nicht am Server')
  })

  it('stellt Zahlungslaeufe Wizard zuerst mit 44-px-Auswahl', () => {
    const src = read('../../pages/fibu/zahlungslaeufe.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<Wizard')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Bitte eine Bezeichnung erfassen.')
    expect(src).toContain('onStepValidationError')
  })

  it('stellt OP-Verwaltung Arbeit zuerst mit 44-px-Oeffnen', () => {
    const src = read('../../pages/fibu/op-verwaltung.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('Offene Posten Verwaltung')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Debitoren oeffnen')
    expect(src).toContain('Kreditoren oeffnen')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('text-orange-900')
    expect(src).not.toContain('text-blue-900')
  })

  it('stellt Auftragsbestaetigungen Liste zuerst und echten Export', () => {
    const src = read('../../pages/einkauf/auftragsbestaetigungen-liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('exportToCSV')
    expect(src.indexOf('<ListReport')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
  })

  it('stellt Einkaufsanfragen Liste zuerst und echten Export', () => {
    const src = read('../../pages/einkauf/anfragen-liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('exportToCSV')
    expect(src.indexOf('<ListReport')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
  })

  it('stellt FIBU Offene Posten Arbeit zuerst mit Mahnlauf', () => {
    const src = read('../../pages/fibu/offene-posten.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('Mahnlauf starten')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('/finance/mahnwesen')
    expect(src).toContain('/verkauf/rechnungen')
    expect(src).not.toContain('/sales/invoice-editor')
    expect(src).toContain('NativeSelect')
    expect(src).toContain('data-global-button-handler="ignore"')
  })

  it('stellt Buchungsjournal Suche zuerst mit 44 px', () => {
    const src = read('../../pages/fibu/buchungsjournal.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('Buchungen suchen')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('data-global-button-handler="ignore"')
  })

  it('stellt Hauptbuch Arbeit zuerst mit DATEV-Navigation', () => {
    const src = read('../../pages/fibu/hauptbuch.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('Hauptbuch suchen')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('/fibu/schnittstelle-fibu?context=hauptbuch')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('data-global-button-handler="ignore"')
    expect(src).toContain('searchTerm.trim()')
  })

  it('stellt FIBU-Schnittstelle Arbeit zuerst mit 44-px-Filtern', () => {
    const src = read('../../pages/fibu/schnittstelle-fibu.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('Schnittstelle Finanzbuchhaltung')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('text-blue-800')
    expect(src).not.toContain('className="h-8 text-sm"')
  })

  it('stellt Buchungsimport Arbeit zuerst mit 44-px-Schritten', () => {
    const src = read('../../pages/finance/buchungsimport.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<StepIndicator')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Vorschau fehlgeschlagen')
    expect(src).not.toContain('bg-red-50')
  })

  it('stellt BWA Arbeit zuerst ohne Rohblau', () => {
    const src = read('../../pages/fibu/bwa.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('Betriebswirtschaftliche Auswertung')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('bg-blue-50')
    expect(src).not.toContain('bg-amber-50')
  })

  it('stellt Bilanz Arbeit zuerst mit CSV-Export', () => {
    const src = read('../../pages/fibu/bilanz.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('Bilanz-Periode')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('data-global-button-handler="ignore"')
    expect(src).not.toContain('text-blue-900')
    expect(src).not.toContain('bg-amber-50')
  })

  it('stellt GuV Arbeit zuerst ohne Rohgruen', () => {
    const src = read('../../pages/fibu/guv.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('GuV-Periode')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('border-status-success')
    expect(src).not.toContain('border-green-500')
  })

  it('stellt Lastschriften 44 px ohne Rohblau', () => {
    const src = read('../../pages/finance/lastschriften-debitoren.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<ObjectPage')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('bg-blue-600')
    expect(src).not.toContain('bg-red-600')
  })

  it('stellt ELSTER Arbeit zuerst mit 44-px-Periode', () => {
    const src = read('../../pages/fibu/elster-online.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('UStVA aus Sachkonten berechnen')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('aria-label="UStVA-Periode"')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Bankabgleich Arbeit zuerst und Theater nur Desktop', () => {
    const src = read('../../pages/finance/bank-abgleich.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src.indexOf('<ObjectPage')).toBeLessThan(src.indexOf('<OperationalCaseHeader'))
    expect(src).toContain('{!isTouch ? (')
  })

  it('stellt Fahrer 44 px ohne Hover-Blau', () => {
    const src = read('../../pages/transporte/fahrer-liste.tsx')
    expect(src).toContain('min-h-11 font-medium text-primary')
    expect(src).toContain('{!isTouch ? (')
    expect(src).not.toContain('text-blue-600')
  })
})
