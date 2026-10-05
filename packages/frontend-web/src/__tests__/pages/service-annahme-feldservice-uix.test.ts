import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const read = (rel: string) => readFileSync(resolve(__dirname, rel), 'utf8')

describe('Service/Annahme/Feldservice UIX', () => {
  it('stellt Service-Anfragen Arbeit zuerst und 44 px', () => {
    const src = read('../../pages/service/anfragen.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Suche Service-Anfragen')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Neue Anfrage')
  })

  it('stellt Wareneingang-Theater nur am Desktop', () => {
    const src = read('../../pages/einkauf/wareneingang.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('CrudCapabilityChecklist')
  })

  it('stellt Klaerung gesperrt mit Arbeit zuerst', () => {
    const src = read('../../pages/annahme/klaerung-gesperrt.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Klaerung speichern')
    expect(src).toContain('Queue-Kontext')
    expect(src).toContain('NativeSelect')
  })

  it('stellt Retouren beschriftet 44 px ohne Rohblau', () => {
    const src = read('../../pages/einkauf/retouren.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('text-blue-800')
  })

  it('stellt Service-Rueckmeldung ohne Icon-Zurueck', () => {
    const src = read('../../pages/service/rueckmeldung.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Zur Anfragenliste')
    expect(src).toContain('NativeSelect')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="icon"')
  })

  it('stellt Feldservice mit h1 und 44-px-Aktionen', () => {
    const src = read('../../pages/agribusiness/field-service-tasks.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('<h1')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Opportunities-Theater nur am Desktop', () => {
    const src = read('../../pages/crm/opportunities-liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('ListReport')
  })

  it('stellt QS-Checkliste ohne toten Audit-Start', () => {
    const src = read('../../pages/compliance/qs-checkliste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('/qualitaet/ausnahmen')
    expect(src).toContain('QS-Ausnahmen')
    expect(src).toContain('{!isTouch ? (')
    expect(src).not.toContain('bg-red-50')
    expect(src).not.toContain('>Audit starten<')
  })

  it('stellt Zahlungslauf-Theater nur am Desktop', () => {
    const src = read('../../pages/finance/zahlungslauf-kreditoren.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('ObjectPage')
  })

  it('stellt UStVA-Theater nur am Desktop', () => {
    const src = read('../../pages/finance/ustva.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('ObjectPage')
  })

  it('stellt Abschluss-Theater nur am Desktop', () => {
    const src = read('../../pages/finance/abschluss.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('ObjectPage')
  })

  it('stellt Rechnungseingaenge-Liste zuerst', () => {
    const src = read('../../pages/einkauf/rechnungseingaenge-liste.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('ListReport')
  })

  it('stellt QS-Ausnahmen Arbeit zuerst ohne Rohrot', () => {
    const src = read('../../pages/qualitaet/ausnahmen.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('{!isTouch ? (')
    expect(src).not.toContain('bg-red-50')
  })

  it('stellt Gutschriften Theater nur am Desktop', () => {
    const src = read('../../pages/einkauf/gutschriften-belastungen.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
  })

  it('stellt Lieferantenstamm Theater nur am Desktop', () => {
    const src = read('../../pages/einkauf/lieferanten-stamm.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Tabs')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Löschen')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('text-orange-800')
  })

  it('stellt Dashboards ohne Theater auf Touch', () => {
    const sales = read('../../pages/dashboard/sales-dashboard.tsx')
    const einkauf = read('../../pages/dashboard/einkauf-dashboard.tsx')
    expect(sales).toContain('useTouchDevice')
    expect(sales).toContain('{!isTouch ? (')
    expect(einkauf).toContain('useTouchDevice')
    expect(einkauf).not.toContain('bg-red-50')
  })

  it('stellt EDI-Portal Arbeit zuerst und 44 px', () => {
    const src = read('../../pages/einkauf/edi-portal.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Bestaetigen')
  })

  it('stellt Lieferantenbewertung mit beschrifteten Scores', () => {
    const src = read('../../pages/einkauf/lieferantenbewertung.tsx')
    expect(src).toContain('Score senken')
    expect(src).toContain('Score erhoehen')
    expect(src).toContain('pendingScoreId')
    expect(src).toContain('{!isTouch ? (')
  })

  it('stellt Leistungsnachweise 44 px mit Freigabe-Guard', () => {
    const src = read('../../pages/einkauf/service-entry-sheets.tsx')
    expect(src).toContain('pendingApproveId')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('{!isTouch ? (')
  })

  it('stellt Benutzer- und Rollenlisten 44 px', () => {
    const users = read('../../pages/admin/benutzer-liste.tsx')
    const roles = read('../../pages/admin/rollen-verwaltung.tsx')
    expect(users).toContain('Suche Benutzer')
    expect(users).toContain('min-h-11 font-medium text-primary')
    expect(roles).toContain('Suche Rollen')
    expect(roles).toContain('{!isTouch ? (')
  })

  it('stellt Frachttarife ohne 5-px-Win32-Toolbar', () => {
    const src = read('../../pages/strecke/speditionen-fracht-preise.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('h-5 border border-[#9b9b9b]')
  })

  it('stellt Frachtdruck ohne toten 6-px-Druck auf Touch', () => {
    const src = read('../../pages/versand/frachtdokumente.tsx')
    expect(src).toContain('handlePrintUnavailable')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('{!isTouch ? (')
  })

  it('stellt HRM-Gates ohne SAP-Blau und mit Arbeit zuerst', () => {
    const src = read('../../pages/personal/hrm-operations-gates.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('NativeSelect')
    expect(src).not.toContain('#005ca5')
    expect(src).not.toContain('bg-red-50')
    expect(src).toContain('Neue Pruefpunkte kommen aus dem HRM-Katalog')
  })

  it('stellt QM-Dokumente mit Suche 44 px und Theater nur Desktop', () => {
    const src = read('../../pages/document.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Suche QM-Dokumente')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('pendingDocKey')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Mischfutter-Produktion mit Wizard zuerst auf Touch', () => {
    const src = read('../../pages/produktion/mischfutter-produktion.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('title="Mischfutter-Produktion"')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Meldewesen-Konsole mit Tabs zuerst auf Touch', () => {
    const src = read('../../pages/compliance/meldewesen-konsole.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('AgentProcessPanel')
  })

  it('stellt Monitoring-Regeln mit Formular zuerst und beschriftetem Loeschen', () => {
    const src = read('../../pages/admin/monitoring/regeln.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('pendingDeleteKey')
    expect(src).toContain('NativeSelect')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Annahme-QR mit 44-px-Zurueck', () => {
    const src = read('../../pages/annahme/annahme-qr.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Zur Warteschlange')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Wiegeschein-MCP-Liste auf Deutsch und 44 px', () => {
    const src = read('../../pages/weighing.tsx')
    expect(src).toContain('Wiegescheine')
    expect(src).toContain('Abschließen')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('pendingFinalizeId')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Bestands-MCP-Liste auf Deutsch und 44 px', () => {
    const src = read('../../pages/inventory.tsx')
    expect(src).toContain('Bestand')
    expect(src).toContain('Korrigieren')
    expect(src).toContain('Einlagern')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Kontrakt-V2-Theater nur am Desktop', () => {
    const src = read('../../pages/contracts-v2.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('statusKey')
    expect(src).toContain('qty?.contracted')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Kontrakt-Engagement mit 44-px-Mahnen', () => {
    const src = read('../../pages/agrar/kontrakt-engagement.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('pending')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Kontrakt-Erfuellung mit Tokens und 44 px', () => {
    const src = read('../../pages/agrar/kontrakt-erfuellung.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('bg-status-error')
    expect(src).toContain('ariaLabel="Kontrakttyp"')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-red-500')
  })

  it('stellt Kontrakt-Fixierung ohne Sky-Blau und 44 px', () => {
    const src = read('../../pages/agrar/kontrakt-fixierung.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('bg-primary')
    expect(src).toContain('Fixieren')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-sky-')
  })

  it('stellt Kontrakt-Settlement mit beschriftetem Abrechnen und Storno', () => {
    const src = read('../../pages/agrar/kontrakt-settlement.tsx')
    expect(src).toContain('Abrechnen')
    expect(src).toContain('Storno')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('variant="ghost"')
  })

  it('stellt Ernte neu ohne Icon-Zurueck', () => {
    const src = read('../../pages/agrar/ernte/neu.tsx')
    expect(src).toContain('Zur Ernteliste')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="icon"')
  })

  it('stellt Field-Service neu mit NativeSelect und 44 px', () => {
    const src = read('../../pages/agribusiness/field-service-task-neu.tsx')
    expect(src).toContain('NativeSelect')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain("from '@/components/ui/select'")
  })

  it('stellt Field-Service edit mit NativeSelect und 44 px', () => {
    const src = read('../../pages/agribusiness/field-service-task-edit.tsx')
    expect(src).toContain('NativeSelect')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain("from '@/components/ui/select'")
  })

  it('stellt PSM-Beratung ohne Rohblau', () => {
    const src = read('../../pages/agrar/psm/beratung.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('text-blue-900')
    expect(src).not.toContain('bg-blue-600')
    expect(src).not.toContain('bg-gray-200')
  })

  it('stellt PSM-Wasserschutz mit Status-Tokens', () => {
    const src = read('../../pages/agrar/psm/wasserschutz.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('bg-status-error/10')
    expect(src).not.toContain('bg-red-50')
    expect(src).not.toContain('bg-green-50')
    expect(src).not.toContain('text-blue-900')
  })

  it('stellt Aktivitaet-Detail ohne Icon-Entfernen', () => {
    const src = read('../../pages/crm/aktivitaet-detail.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Entfernen')
    expect(src).not.toContain('size="icon"')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Kontakt-Detail mit 44-px-Zurueck', () => {
    const src = read('../../pages/crm/kontakt-detail.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Wiedervorlagen mit Tokens und 44-px-Erledigen', () => {
    const src = read('../../pages/crm/wiedervorlagen.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Erledigen')
    expect(src).toContain('bg-status-error/10')
    expect(src).not.toContain('bg-red-50')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Saatgut-Stamm mit 44-px-Zurueck', () => {
    const src = read('../../pages/agrar/saatgut-stamm.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Duenger-Stamm mit 44-px-Zurueck', () => {
    const src = read('../../pages/agrar/duenger-stamm.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Landwirte-Liste mit 44-px-Zeilenaktionen', () => {
    const src = read('../../pages/agribusiness/farmers.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Erntefenster mit keyed Backfill', () => {
    const src = read('../../pages/agrar/erntefenster-konfig.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('backfillMutation.variables === campaign.id')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Maschinen-Auslastung Arbeit zuerst am Touch', () => {
    const src = read('../../pages/agrar/maschinenauslastung.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('bg-orange-50')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt CRM-Kundenstamm-Aktionen 44 px', () => {
    const src = read('../../pages/crm/kunden-stamm.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Dubletten mit 44-px-Zusammenfuehren', () => {
    const src = read('../../pages/crm/dubletten.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Zusammenführen')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Klaerfall-Inbox mit 44-px-Zuordnen', () => {
    const src = read('../../pages/crm/klaerfall-inbox.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Zuordnen')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Bestell-Inbox ohne Rohblau und mit keyed pending', () => {
    const src = read('../../pages/crm/bestell-inbox.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('bestaetigen.variables?.id === it.id')
    expect(src).not.toContain('bg-blue-100')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Vertreterstamm ohne Icon-only Loeschen', () => {
    const src = read('../../pages/crm/vertreterstamm.tsx')
    expect(src).toContain('Deaktivieren')
    expect(src).toContain('Bearbeiten')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Vertreterprovisionen ohne Icon-only Entfernen', () => {
    const src = read('../../pages/crm/vertreterprovisionen.tsx')
    expect(src).toContain('Entfernen')
    expect(src).toContain('Deaktivieren')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="icon"')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Kunden-Zuordnung mit 44-px-Zuordnen', () => {
    const src = read('../../pages/crm/kunden-zuordnung.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Zuordnen')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Betriebsprofil-Detail mit 44-px-Speichern', () => {
    const src = read('../../pages/crm/betriebsprofil-detail.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Entfernen')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Lead-Generierung mit 44-px-Vorschau', () => {
    const src = read('../../pages/crm/lead-generierung.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Potential-Analyse Arbeit zuerst am Touch', () => {
    const src = read('../../pages/crm/potential-analyse.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch && data ? (')
    expect(src).toContain('/crm/kunden-liste?q=')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Bedarfsdeckung mit keyed Reklass und Tokens', () => {
    const src = read('../../pages/crm/bedarfsdeckung-cockpit.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain("reklass.variables?.modus === 'ki'")
    expect(src).toContain("reklass.variables?.modus === 'belege'")
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Durchdringungs-Pipeline mit nativem Select', () => {
    const src = read('../../pages/crm/durchdringungs-pipeline.tsx')
    expect(src).toContain('NativeSelect')
    expect(src).toContain('ariaLabel="Sparte"')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Mahnlauf mit 44-px-Start', () => {
    const src = read('../../pages/finance/mahnlauf.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Kommissionierung mit 44-px-Bestaetigen', () => {
    const src = read('../../pages/lager/kommissionierung.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Scanner mit ehrlichem Buchen und 44 px', () => {
    const src = read('../../pages/mobile/scanner.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('/artikel/liste?q=')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Bestellvorschlag Lager ohne SAP-Grau', () => {
    const src = read('../../pages/einkauf/bestellvorschlag-lager.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? <AgentProcessPanel')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Suche ist in dieser Maske nicht angebunden')
    expect(src).toContain('pendingAction')
    expect(src).not.toContain('bg-gray-700')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('MoreHorizontal')
  })

  it('stellt Bestellvorschlag Rohware ohne SAP-Grau', () => {
    const src = read('../../pages/einkauf/bestellvorschlag-rohware.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('pendingAction')
    expect(src).not.toContain('bg-gray-700')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('MoreHorizontal')
  })

  it('stellt Bestellvorschlag Verkauf ohne SAP-Grau', () => {
    const src = read('../../pages/einkauf/bestellvorschlag-verkauf.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('pendingAction')
    expect(src).not.toContain('bg-gray-700')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('MoreHorizontal')
  })

  it('stellt Kreditoren-OP Arbeit zuerst und beschriftete Aktionen', () => {
    const src = read('../../pages/finance/op-kreditoren.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Bearbeiten')
    expect(src).toContain('Löschen')
    expect(src).toContain('deleteMutation.variables === op.id')
    expect(src).not.toContain('size="icon"')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt OP-Cockpit Arbeit zuerst und Tokens', () => {
    const src = read('../../pages/finance/offene-posten-cockpit.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('ariaLabel="Kontotyp"')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('border-red-300')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Zahlungseingang mit 44-px-Ausziffern', () => {
    const src = read('../../pages/finance/zahlungseingang.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('text-2xs')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Payment-Matching Arbeit zuerst am Touch', () => {
    const src = read('../../pages/finance/payment-matching.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Perioden mit 44-px-Sperren und keyed pending', () => {
    const src = read('../../pages/finance/periods.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('pendingPeriodId')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Silo-Uebersicht mit Tokens und 44-px-Transfer', () => {
    const src = read('../../pages/lager/silo-uebersicht.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('bg-status-error')
    expect(src).toContain('ariaLabel="Lager"')
    expect(src).not.toContain('bg-red-500')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt FIBU-Zahlungseingaenge Arbeit zuerst am Touch', () => {
    const src = read('../../pages/fibu/zahlungseingaenge.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Periodenabschluss mit Tokens und 44 px', () => {
    const src = read('../../pages/finance/periodenabschluss.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('bg-red-100')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt QS-Leitstand mit 44-px-Freigabe', () => {
    const src = read('../../pages/lager/qs-leitstand.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Freigeben')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt AP-Rechnungen mit 44-px-Zeilenaktionen', () => {
    const src = read('../../pages/finance/ap-invoices-list.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Frachtauftraege ohne SAP-Grau', () => {
    const src = read('../../pages/einkauf/frachtauftraege-eingang.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Suche ist in dieser Maske nicht angebunden')
    expect(src).not.toContain('bg-gray-700')
    expect(src).not.toContain('MoreHorizontal')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt FIBU-Uebersicht Arbeit zuerst und 44 px', () => {
    const src = read('../../pages/fibu/buchhaltungsuebersicht.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Anfrage-Erfassung ohne SAP-Gruen und mit beschrifteter Suche', () => {
    const src = read('../../pages/einkauf/anfrage-erfassung.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Suchen')
    expect(src).not.toContain('bg-green-600')
    expect(src).not.toContain('MoreHorizontal')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Materialfluss mit 44-px-Speichern', () => {
    const src = read('../../pages/lager/materialfluss.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Artikel-Stamm ohne Icon-only Aktionen', () => {
    const src = read('../../pages/artikel/stamm.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Herunterladen')
    expect(src).toContain('Bearbeiten')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Zeiterfassung Arbeit zuerst und 44 px', () => {
    const src = read('../../pages/personal/zeiterfassung.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('text-[10px]')
    expect(src).not.toContain('bg-amber-50')
  })

  it('stellt POS-Terminal beschriftet 44 px ohne SAP-Grau', () => {
    const src = read('../../pages/pos/terminal.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Einstellungen')
    expect(src).toContain('Leeren')
    expect(src).toContain('Rabatt')
    expect(src).toContain('useTouchDevice')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-gray-50')
    expect(src).not.toContain('bg-green-50')
  })

  it('stellt Monatswerte Theater nur am Desktop', () => {
    const src = read('../../pages/fibu/monatswerte.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('<h1')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-amber-50')
  })

  it('stellt Ernte-Annahme Lookups beschriftet', () => {
    const src = read('../../pages/agrar/ernte-annahme-erfassung.tsx')
    expect(src).toContain('Suchen')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('MoreHorizontal')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Materialfluss-Visualisierung 44 px ohne Rohrot', () => {
    const src = read('../../pages/lager/materialfluss-visualisierung.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('ariaLabel="Lager"')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('border-red-600')
    expect(src).not.toContain('text-[10px]')
  })

  it('stellt Portal-Feldbuch Arbeit zuerst und beschriftete Zeilen', () => {
    const src = read('../../pages/portal/feldbuch.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Bearbeiten')
    expect(src).toContain('Löschen')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-purple-100')
  })

  it('stellt Wareneingangsabgleich 44 px', () => {
    const src = read('../../pages/einkauf/wareneingangsabgleich.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Gutschrift erzeugen')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt POS-Retoure ohne SAP-Rot und 44 px', () => {
    const src = read('../../pages/pos/retoure.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Entfernen')
    expect(src).toContain('Zurück zum POS')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-red-600')
    expect(src).not.toContain('bg-gray-50')
  })

  it('stellt Annahme-Warteschlange ohne size=sm', () => {
    const src = read('../../pages/annahme/warteschlange.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('{!isTouch ?')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Tour-Fracht-Arbeitsraum 44 px', () => {
    const src = read('../../pages/logistik/tour-fracht-arbeitsraum.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Kassen-Uebernahme 44 px', () => {
    const src = read('../../pages/pos/uebernahme-kasse.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Deckungsmonitor auf Deutsch und 44 px', () => {
    const src = read('../../pages/disposition/FrmCoverageMonitor.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('Deckungsmonitor')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('bg-status-error/10')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-red-100')
  })

  it('stellt Warenpositionsmatrix Theater nur am Desktop', () => {
    const src = read('../../pages/disposition/LstCommodityPositionMatrix.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? <AgentProcessPanel')
    expect(src).toContain('Warenpositionsmatrix')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-green-50')
  })

  it('stellt Nebenbuch-Abstimmung Arbeit zuerst', () => {
    const src = read('../../pages/finance/nebenbuch-abstimmung.tsx')
    expect(src).toContain('useTouchDevice')
    expect(src).toContain('{!isTouch ? (')
    expect(src).toContain('Details')
    expect(src).toContain('min-h-touch')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('Flow-Spine:')
  })

  it('stellt Stundenzettel mit beschriftetem Loeschen 44 px', () => {
    const src = read('../../pages/personal/stundenzettel.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Löschen')
    expect(src).toContain('Tour hinzufügen')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Leitungs-Dashboard auf Deutsch und 44 px', () => {
    const src = read('../../pages/management/executive-dashboard.tsx')
    expect(src).toContain('Leitungs-Dashboard')
    expect(src).toContain('Aktualisieren')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Export nicht angebunden')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('size="icon"')
  })

  it('stellt permanente Inventur mit keyed Zaehl-Pending', () => {
    const src = read('../../pages/lager/permanente-inventur.tsx')
    expect(src).toContain('pendingZaehlId')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('bg-status-success/10')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-emerald-50')
  })

  it('stellt Kostenstellenrechnung Loeschen beschriftet', () => {
    const src = read('../../pages/fibu/kostenstellenrechnung.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Löschen')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('<Trash2')
  })

  it('stellt Portal-Start ohne Icon-Download', () => {
    const src = read('../../pages/portal/index.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Herunterladen')
    expect(src).toContain('Download nicht angebunden')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('text-gray-500')
  })

  it('stellt ELSTER-Online 44 px', () => {
    const src = read('../../pages/fibu/elster-online.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('ELSTER-XML')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt FIBU-Schnittstelle 44 px', () => {
    const src = read('../../pages/fibu/schnittstelle-fibu.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Übertragung starten')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Anlagen-Suite 44 px', () => {
    const src = read('../../pages/fibu/anlagen-suite.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Validieren')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Raps-Profil Loeschen beschriftet 44 px', () => {
    const src = read('../../pages/nawaro/raps-profil.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Löschen')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('size="icon"')
  })

  it('stellt DATEV-Export 44 px', () => {
    const src = read('../../pages/finance/datev-export.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Export erstellen')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('text-[11px]')
  })

  it('stellt Bankstamm Bearbeiten beschriftet', () => {
    const src = read('../../pages/finance/bank-stamm.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Bearbeiten')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt GuV Aktualisieren beschriftet ohne Rohamber', () => {
    const src = read('../../pages/fibu/guv.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Aktualisieren')
    expect(src).not.toContain('size="sm"')
    expect(src).not.toContain('bg-amber-50')
  })

  it('stellt Bilanz Aktualisieren und Export 44 px', () => {
    const src = read('../../pages/fibu/bilanz.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Aktualisieren')
    expect(src).toContain('Export CSV')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Kontenplan Bearbeiten/Deaktivieren beschriftet', () => {
    const src = read('../../pages/finance/chart-of-accounts.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Bearbeiten')
    expect(src).toContain('Deaktivieren')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Wechselkurse Loeschen beschriftet', () => {
    const src = read('../../pages/finance/wechselkurse.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Löschen')
    expect(src).not.toContain('size="sm"')
  })

  it('stellt Sachkonto Aktualisieren beschriftet', () => {
    const src = read('../../pages/fibu/sachkonto.tsx')
    expect(src).toContain('min-h-touch')
    expect(src).toContain('Aktualisieren')
    expect(src).not.toContain('size="sm"')
  })
})
