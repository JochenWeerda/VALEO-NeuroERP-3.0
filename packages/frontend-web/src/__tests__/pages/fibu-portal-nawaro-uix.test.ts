import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('FIBU / Portal / NaWaRo UIX', () => {
  it('stellt BWA-Aktualisieren auf 44 px', () => {
    const src = read('../../pages/fibu/bwa.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Aktualisieren')
    expect(src).not.toMatch(/size="sm"/)
  })

  it('stellt Journal-Storno und Abschluss-Details auf 44 px', () => {
    expect(read('../../pages/fibu/buchungsjournal.tsx')).toContain('min-h-touch gap-1')
    expect(read('../../pages/fibu/abschluss-cockpit.tsx')).toContain('min-h-touch')
    const check = read('../../pages/fibu/abschluss-checklist-detail.tsx')
    expect(check).toContain('min-h-touch')
    expect(check).toContain('Erledigen')
    expect(check).not.toContain('Instanz ')
  })

  it('beschriftet FIBU-Stammaktionen 44 px', () => {
    expect(read('../../pages/fibu/periodische-buchungen.tsx')).toContain('Sperren')
    expect(read('../../pages/fibu/erloeskennziffern.tsx')).toContain('Bearbeiten')
    expect(read('../../pages/fibu/erloeskontenzuordnung.tsx')).toContain('Bearbeiten')
    expect(read('../../pages/fibu/forderungsgruppen.tsx')).toContain('Löschen')
    expect(read('../../pages/fibu/lohn-connector.tsx')).toContain('Löschen')
    expect(read('../../pages/fibu/atlas.tsx')).toContain('min-h-touch')
  })

  it('stellt Portal-Self-Service 44 px mit beschrifteten Zeilen', () => {
    const bestellungen = read('../../pages/portal/bestellungen.tsx')
    expect(bestellungen).toContain('min-h-touch')
    expect(bestellungen).toContain('Details')
    expect(read('../../pages/portal/rechnungen.tsx')).toContain('Download')
    expect(read('../../pages/portal/vertraege.tsx')).toContain('Details')
    expect(read('../../pages/portal/anfragen.tsx')).toContain('Details')
    expect(read('../../pages/portal/shop.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../pages/portal/empfehlungen.tsx')).not.toContain('text-gray-900')
  })

  it('stellt NaWaRo-Erfassung 44 px', () => {
    expect(read('../../pages/nawaro/anbauflaechen.tsx')).toContain('min-h-touch')
    expect(read('../../pages/nawaro/vertraege.tsx')).toContain('min-h-touch')
    expect(read('../../pages/nawaro/mitteilung-drucken.tsx')).toContain('min-h-touch')
    expect(read('../../pages/nawaro/anbauflaechen.tsx')).not.toMatch(/size="sm"/)
  })

  it('beschriftet Einkauf-Stamm und Rechnungs-Toolbar 44 px', () => {
    const zabd = read('../../pages/einkauf/zahlungsbedingungen.tsx')
    expect(zabd).toContain('Bearbeiten')
    expect(zabd).toContain('min-h-touch')
    expect(zabd).not.toMatch(/size="sm"/)
    const eingang = read('../../pages/einkauf/rechnung-eingang-erfassung.tsx')
    expect(eingang).toContain('Speichern')
    expect(eingang).toContain('aria-label="Kostenstelle suchen"')
    expect(eingang).toContain('Bediener:')
    expect(eingang).not.toMatch(/size="sm"/)
    expect(read('../../pages/einkauf/gutschriften-belastungen.tsx')).toContain('Entfernen')
    expect(read('../../pages/einkauf/reports.tsx')).not.toMatch(/size="sm"/)
  })

  it('beschriftet Stammdaten- und Partie-Aktionen 44 px', () => {
    expect(read('../../pages/stammdaten/hausbanken.tsx')).toContain('Bearbeiten')
    expect(read('../../pages/stammdaten/betriebsstaetten.tsx')).toContain('Löschen')
    expect(read('../../pages/stammdaten/mengeneinheiten.tsx')).not.toMatch(/size="sm"/)
    expect(read('../../pages/lager/partiestamm.tsx')).toContain('Löschen')
    expect(read('../../pages/logistik/frachttabellen.tsx')).toContain('min-h-touch')
    expect(read('../../pages/benachrichtigungen/liste.tsx')).not.toMatch(/size="sm"/)
  })
})
