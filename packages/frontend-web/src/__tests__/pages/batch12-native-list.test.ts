import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const pages = resolve(__dirname, '../../pages')
const kontrolleBatch12 = readFileSync(
  resolve(__dirname, '../../../../../app/core/screen_definitions_kontrolle_batch12.py'),
  'utf8',
)

function read(rel: string): string {
  return readFileSync(resolve(pages, rel), 'utf8')
}

/** Batch 12 (83 pages) — NativeListPage / UniversalNativeCockpitPage + screenId. */
const BATCH12: Array<[string, string, string]> = [
  ['admin/compliance-dashboard.tsx', 'admin/compliance-dashboard', 'UniversalNativeCockpitPage'],
  ['admin/control-center/ai-approvals.tsx', 'admin/control-center/ai-approvals', 'NativeListPage'],
  ['admin/control-center/incident-response.tsx', 'admin/control-center/incident-response', 'NativeListPage'],
  ['admin/control-center/index.tsx', 'admin/control-center', 'NativeListPage'],
  ['admin/control-center/operations.tsx', 'admin/control-center/operations', 'NativeListPage'],
  ['admin/control-center/security.tsx', 'admin/control-center/security', 'NativeListPage'],
  ['admin/core/audit-governance.tsx', 'admin/core/audit-governance', 'NativeListPage'],
  ['admin/data-quality.tsx', 'admin/data-quality', 'NativeListPage'],
  ['admin/devices/index.tsx', 'admin/devices', 'NativeListPage'],
  ['admin/dms-integration.tsx', 'admin/dms-integration', 'NativeListPage'],
  ['admin/erntepeak-stabilitaet.tsx', 'admin/erntepeak-stabilitaet', 'NativeListPage'],
  ['admin/forst/kalkulation.tsx', 'admin/forst/kalkulation', 'NativeListPage'],
  ['admin/integrationen-quarantaene.tsx', 'admin/integrationen-quarantaene', 'NativeListPage'],
  ['admin/monitoring/alerting.tsx', 'admin/monitoring/alerting', 'NativeListPage'],
  ['admin/monitoring/historie.tsx', 'admin/monitoring/historie', 'NativeListPage'],
  ['admin/monitoring/regeln.tsx', 'admin/monitoring/regeln', 'NativeListPage'],
  ['admin/omnichannel-handelskonflikt.tsx', 'admin/omnichannel-handelskonflikt', 'NativeListPage'],
  ['admin/AuditLogPage.tsx', 'admin/audit-log', 'NativeListPage'],
  ['admin/BelegfolgekonfigPage.tsx', 'admin/belegfolgekonfig', 'NativeListPage'],
  ['agrar/daily-prices.tsx', 'agrar/daily-prices', 'NativeListPage'],
  ['agrar/duenger-rechner.tsx', 'agrar/duenger-rechner', 'NativeListPage'],
  ['agrar/ernte/kampagnenabschluss.tsx', 'agrar/ernte/kampagnenabschluss', 'NativeListPage'],
  ['agrar/ernte-kampagne-erfassung.tsx', 'agrar/ernte-kampagne-erfassung', 'NativeListPage'],
  ['agrar/ernte-qualitaetsfreigabe.tsx', 'agrar/ernte-qualitaetsfreigabe', 'NativeListPage'],
  ['agrar/futter/mischfutter-optimierung.tsx', 'agrar/futter/mischfutter-optimierung', 'NativeListPage'],
  ['agrar/kalkulation/deckungsbeitrag.tsx', 'agrar/kalkulation/deckungsbeitrag', 'NativeListPage'],
  ['agrar/maschinen/wartung.tsx', 'agrar/maschinen/wartung', 'NativeListPage'],
  ['agrar/nawaro-erntemeldung.tsx', 'agrar/nawaro-erntemeldung', 'NativeListPage'],
  ['agrar/nawaro-kaskade.tsx', 'agrar/nawaro-kaskade', 'NativeListPage'],
  ['agrar/nawaro-vertraege.tsx', 'agrar/nawaro-vertraege', 'NativeListPage'],
  ['agrar/pflanzenschutz-liste.tsx', 'agrar/pflanzenschutz-liste', 'NativeListPage'],
  ['agrar/planung/duengeplanung.tsx', 'agrar/planung/duengeplanung', 'NativeListPage'],
  ['agrar/planung/fruchtfolge.tsx', 'agrar/planung/fruchtfolge', 'NativeListPage'],
  ['agrar/psm/anwendungsprotokoll.tsx', 'agrar/psm/anwendungsprotokoll', 'NativeListPage'],
  ['agrar/psm/tankmischung.tsx', 'agrar/psm/tankmischung', 'NativeListPage'],
  ['agrar/qualitaet/ausnahmen.tsx', 'agrar/qualitaet/ausnahmen', 'NativeListPage'],
  ['agrar/qualitaet/laborwerte.tsx', 'agrar/qualitaet/laborwerte', 'NativeListPage'],
  ['agrar/qualitaet/mykotoxine.tsx', 'agrar/qualitaet/mykotoxine', 'NativeListPage'],
  ['agrar/saatgut/prognose.tsx', 'agrar/saatgut/prognose', 'NativeListPage'],
  ['agrar/saatgut/vermehrung.tsx', 'agrar/saatgut/vermehrung', 'NativeListPage'],
  ['agrar/sektion-auswahl.tsx', 'agrar/sektion-auswahl', 'NativeListPage'],
  ['agrar/silo-belegung.tsx', 'agrar/silo-belegung', 'NativeListPage'],
  ['agrar/silo-qualitaet.tsx', 'agrar/silo-qualitaet', 'NativeListPage'],
  ['agrar/silo-trocknung.tsx', 'agrar/silo-trocknung', 'NativeListPage'],
  ['agrar/soil-samples.tsx', 'agrar/soil-samples', 'NativeListPage'],
  ['agrar/sorten.tsx', 'agrar/sorten', 'NativeListPage'],
  ['agrar/trocknungsregeln.tsx', 'agrar/trocknungsregeln', 'NativeListPage'],
  ['agrar/umwelt/nitrat.tsx', 'agrar/umwelt/nitrat', 'NativeListPage'],
  ['agrar/wetter.tsx', 'agrar/wetter', 'NativeListPage'],
  ['charge/chargen-verfolgung.tsx', 'charge/chargen-verfolgung', 'NativeListPage'],
  ['charge/qualitaets-freigabe.tsx', 'charge/qualitaets-freigabe', 'NativeListPage'],
  ['charge/rueckruf.tsx', 'charge/rueckruf', 'NativeListPage'],
  ['charge/stamm.tsx', 'charge/stamm', 'NativeListPage'],
  ['compliance/audit-trail.tsx', 'compliance/audit-trail', 'NativeListPage'],
  ['compliance/cross-compliance.tsx', 'compliance/cross-compliance', 'NativeListPage'],
  ['compliance/duenge-bilanz.tsx', 'compliance/duenge-bilanz', 'NativeListPage'],
  ['compliance/eudr-meldungen.tsx', 'compliance/eudr-meldungen', 'NativeListPage'],
  ['compliance/gefahrstoff-verzeichnis.tsx', 'compliance/gefahrstoff-verzeichnis', 'NativeListPage'],
  ['compliance/lksg-lieferkette.tsx', 'compliance/lksg-lieferkette', 'NativeListPage'],
  ['compliance/meldewesen-konsole.tsx', 'compliance/meldewesen-konsole', 'NativeListPage'],
  ['compliance/pflanzenschutz-nachweis.tsx', 'compliance/pflanzenschutz-nachweis', 'NativeListPage'],
  ['compliance/qs-audits.tsx', 'compliance/qs-audits', 'NativeListPage'],
  ['compliance/schadstoff-monitoring.tsx', 'compliance/schadstoff-monitoring', 'NativeListPage'],
  ['compliance/stichtagsmeldung-bestaende.tsx', 'compliance/stichtagsmeldung-bestaende', 'NativeListPage'],
  ['compliance/tierwohl-dokumentation.tsx', 'compliance/tierwohl-dokumentation', 'NativeListPage'],
  ['compliance/usp-konformitaet.tsx', 'compliance/usp-konformitaet', 'NativeListPage'],
  ['compliance/wasserschutz-auflagen.tsx', 'compliance/wasserschutz-auflagen', 'NativeListPage'],
  ['compliance/zertifikate.tsx', 'compliance/zertifikate', 'NativeListPage'],
  ['contracts/ContractPage.tsx', 'contracts/contract', 'NativeListPage'],
  ['controlling/abweichungsanalyse.tsx', 'controlling/abweichungsanalyse', 'NativeListPage'],
  ['controlling/agrarkalkulation.tsx', 'controlling/agrarkalkulation', 'NativeListPage'],
  ['controlling/benchmark-cockpit.tsx', 'controlling/benchmark-cockpit', 'UniversalNativeCockpitPage'],
  ['controlling/berichtswesen.tsx', 'controlling/berichtswesen', 'NativeListPage'],
  ['controlling/bwa.tsx', 'controlling/bwa', 'NativeListPage'],
  ['controlling/cashflow-prognose.tsx', 'controlling/cashflow-prognose', 'NativeListPage'],
  ['controlling/deckungsbeitragsrechnung.tsx', 'controlling/deckungsbeitragsrechnung', 'NativeListPage'],
  ['controlling/investitionsrechnung.tsx', 'controlling/investitionsrechnung', 'NativeListPage'],
  ['controlling/kampagnen-controlling.tsx', 'controlling/kampagnen-controlling', 'NativeListPage'],
  ['controlling/kennzahlen.tsx', 'controlling/kennzahlen', 'NativeListPage'],
  ['controlling/kostentraegerrechnung.tsx', 'controlling/kostentraegerrechnung', 'NativeListPage'],
  ['controlling/liquiditaetsplanung.tsx', 'controlling/liquiditaetsplanung', 'NativeListPage'],
  ['controlling/standort-vergleich.tsx', 'controlling/standort-vergleich', 'NativeListPage'],
  ['controlling/unternehmensplanung.tsx', 'controlling/unternehmensplanung', 'NativeListPage'],
]

/** Screen-Definitionen liegen in Cockpit- bzw. Batch-8-Modul, nicht in batch12.py. */
const KONTROLLE_DEF_EXCLUDE = new Set([
  'admin/compliance-dashboard',
  'controlling/benchmark-cockpit',
  'compliance/meldewesen-konsole',
])

describe('Batch 12 NativeListPage migration', () => {
  it('deckt 83 Seiten ab', () => {
    expect(BATCH12).toHaveLength(83)
  })

  it.each(BATCH12)('%s → %s', (file, screenId, component) => {
    const src = read(file)
    expect(src).toContain(component)
    expect(src).toContain(`screenId="${screenId}"`)
    expect(src).toContain(`testId="screen-${screenId}"`)
    if (component === 'NativeListPage' && !KONTROLLE_DEF_EXCLUDE.has(screenId)) {
      expect(kontrolleBatch12).toContain(`"${screenId}"`)
    }
  })

  it('Quarantäne-Row-Actions mit permission in batch12', () => {
    expect(kontrolleBatch12).toContain('admin.mobile.connector.retry')
    expect(kontrolleBatch12).toContain('admin.mobile.connector.resolve')
  })
})
