/**
 * Betrieb (Operations) API Hooks
 * TanStack Query hooks for all smaller operational modules:
 * Banken, Benachrichtigungen, Chargen, Compliance, Disposition, Dokumente,
 * Fuhrpark, Förderung, Labor, Management, Marketing, Projekte, Qualität,
 * Service, Schäden, Tankstelle, Transporte, Verladung, Versicherungen,
 * Verträge, Waage, Wartung, Workflow, Zertifikate
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api-client'

// ── Types ──────────────────────────────────────────────────────────────

export type BankKonto = { id: string; iban: string; bank: string; kontoart: string; saldo: number; status: 'aktiv' | 'inaktiv' }
export type Benachrichtigung = { id: string; titel: string; nachricht: string; typ: 'info' | 'warnung' | 'fehler'; zeitstempel: string; gelesen: boolean }
export type Charge = { id: string; chargenId: string; artikel: string; menge: number; lagerort: string; eingang: string; status: 'freigegeben' | 'gesperrt' | 'in-pruefung' }
export type ComplianceItem = { id: string; bereich: string; anforderung: string; erfuellt: boolean; nachweis: string; frist: string }
export type ENNIMeldung = { id: string; typ: string; betrieb: string; vvvo: string; datum: string; status: 'entwurf' | 'gesendet' | 'bestaetigt'; naehrstoffe: { n: number; p: number; k: number } }
export type QSItem = { id: string; bereich: string; pruefpunkt: string; erfuellt: boolean; bemerkung: string; geprueftAm: string }
export type SaatgutNachbau = { id: string; betrieb: string; sorte: string; kultur: string; flaeche: number; erntejahr: number; gebuehr: number; status: 'offen' | 'bezahlt' | 'befreit' }
export type Sachkundenachweis = { id: string; kunde: string; kundennr: string; nachweisNr: string; ausstellungsdatum: string; gueltigBis: string; ausstellendeStelle: string; status: 'gueltig' | 'ablaufend' | 'abgelaufen' }
export type VVVOBetrieb = { id: string; betriebsname: string; vvvo: string; bundesland: string; tierart: string; status: 'aktiv' | 'inaktiv'; letzteAktualisierung: string }
export type Zulassung = { id: string; produkt: string; typ: string; nummer: string; behoerde: string; gueltigBis: string; status: 'aktiv' | 'auslaufend' | 'abgelaufen' }
export type DispoPosition = { id: string; artikel: string; bestand: number; mindestbestand: number; bedarf: number; empfehlung: string; prioritaet: 'hoch' | 'mittel' | 'niedrig' }
export type Dokument = { id: string; name: string; typ: string; kategorie: string; groesse: number; hochgeladen: string; benutzer: string }
export type Fahrzeug = { id: string; kennzeichen: string; typ: string; kilometerstand: number; naechsteInspektion: string; status: 'verfuegbar' | 'unterwegs' | 'werkstatt' }
export type Antrag = { id: string; nummer: string; programm: string; antragsdatum: string; flaeche: number; betrag: number; status: 'entwurf' | 'eingereicht' | 'bewilligt' | 'abgelehnt' }
export type Probe = { id: string; probennummer: string; typ: string; artikel: string; datum: string; labor: string; status: 'ausstehend' | 'in-bearbeitung' | 'abgeschlossen' }
export type Kampagne = { id: string; name: string; typ: string; zielgruppe: string; startdatum: string; enddatum: string; budget: number; status: 'geplant' | 'aktiv' | 'beendet' }
export type Projekt = { id: string; name: string; kunde: string; startdatum: string; enddatum: string; fortschritt: number; budget: number; status: 'aktiv' | 'pausiert' | 'abgeschlossen' }
export type LaborAuftrag = { id: string; chargenId: string; labor: string; analysen: number; auftragsdatum: string; status: 'offen' | 'in-bearbeitung' | 'abgeschlossen' }
export type ServiceAnfrage = { id: string; nummer: string; kunde: string; betreff: string; datum: string; prioritaet: 'hoch' | 'normal' | 'niedrig'; status: 'neu' | 'in-bearbeitung' | 'erledigt' }
export type Schaden = { id: string; nummer: string; art: string; datum: string; ort: string; schadenhoehe: number; status: 'gemeldet' | 'in-pruefung' | 'reguliert' | 'abgelehnt' }
export type Zapfung = { id: string; kennzeichen: string; artikel: string; menge: number; zeitstempel: string; fahrer: string }
export type Fahrer = { id: string; name: string; fuehrerschein: string; fahrzeug: string; status: 'verfuegbar' | 'unterwegs' | 'pause'; tourenHeute: number }
export type VerladungItem = { id: string; kennzeichen: string; artikel: string; menge: number; lieferscheinNr: string; datum: string; status: 'geplant' | 'in-verladung' | 'verladen' }
export type Versicherung = { id: string; art: string; versicherer: string; vertragsnummer: string; praemie: number; ablauf: string; status: 'aktiv' | 'auslaufend' | 'gekuendigt' }
export type Vertrag = { id: string; nummer: string; partner: string; typ: string; artikel: string; menge: number; restmenge: number; laufzeitBis: string; status: 'aktiv' | 'auslaufend' | 'beendet' }
export type Waage = { id: string; standort: string; typ: string; maxKapazitaet: number; letzteEichung: string; naechsteEichung: string; status: 'aktiv' | 'wartung' | 'geeicht' }
export type Wiegung = { id: string; kennzeichen: string; artikel: string; brutto: number; tara: number; netto: number; zeitstempel: string; waage: string }
export type WartungAnlage = { id: string; name: string; typ: string; standort: string; letzteWartung: string; naechsteWartung: string; status: 'aktiv' | 'wartung' | 'defekt' }
export type WorkflowExecution = { id: string; ruleId: string; triggerEntity: string; triggerAction: string; targetEntity: string; targetAction: string; status: 'SUCCESS' | 'FAILED' | 'PENDING'; startedAt: string; completedAt?: string; actorId: string }
export type WorkflowRule = { id: string; triggerEntity: string; triggerAction: string; targetEntity: string; targetAction: string; active: boolean }
export type Zertifikat = { id: string; art: string; standard: string; nummer: string; gueltigBis: string; audit: string; status: 'gueltig' | 'ablaufend' | 'abgelaufen' }

export type ManagementDashboard = {
  kpis: { label: string; value: string; trend: number; einheit?: string }[]
  alerts: { id: string; typ: 'warnung' | 'kritisch' | 'info'; text: string; datum: string }[]
  topProducts: { name: string; umsatz: number }[]
  topCustomers: { name: string; umsatz: number }[]
}

// ── Fallback Data ──────────────────────────────────────────────────────

const fb = {
  bankkonten: [
    { id: '1', iban: 'DE89 3704 0044 0532 0130 00', bank: 'Commerzbank', kontoart: 'Girokonto', saldo: 285000, status: 'aktiv' as const },
    { id: '2', iban: 'DE27 1007 0024 0652 3080 00', bank: 'Deutsche Bank', kontoart: 'Festgeld', saldo: 500000, status: 'aktiv' as const },
  ],
  benachrichtigungen: [
    { id: '1', titel: 'Neue Bestellung eingegangen', nachricht: 'PO-2026-042 von Saatgut AG', typ: 'info' as const, zeitstempel: '2026-02-10 14:32', gelesen: false },
    { id: '2', titel: 'MHD-Warnung', nachricht: '3 Artikel erreichen MHD in 30 Tagen', typ: 'warnung' as const, zeitstempel: '2026-02-10 09:00', gelesen: false },
    { id: '3', titel: 'Inventur abgeschlossen', nachricht: 'Halle B Inventur vollständig', typ: 'info' as const, zeitstempel: '2026-02-09 17:00', gelesen: true },
  ],
  chargen: [
    { id: '1', chargenId: '260210-WEI-001', artikel: 'Weizen Premium', menge: 25.0, lagerort: 'Silo 1', eingang: '2026-02-10', status: 'freigegeben' as const },
    { id: '2', chargenId: '260210-RAP-001', artikel: 'Raps', menge: 18.5, lagerort: 'Silo 3', eingang: '2026-02-10', status: 'in-pruefung' as const },
  ],
  compliance: [
    { id: '1', bereich: 'Gewässerschutz', anforderung: 'Gewässerrandstreifen 5m', erfuellt: true, nachweis: 'Feldprotokoll 2026', frist: '2026-12-31' },
    { id: '2', bereich: 'Düngeverordnung', anforderung: 'Nährstoffbilanz erstellt', erfuellt: true, nachweis: 'Bilanz 2025/26', frist: '2026-03-31' },
    { id: '3', bereich: 'PSM-Dokumentation', anforderung: 'Anwendungsprotokolle vollständig', erfuellt: false, nachweis: '', frist: '2026-03-15' },
  ],
  enni: [
    { id: '1', typ: 'DBE', betrieb: 'Landwirtschaft Müller', vvvo: '03-276-1234', datum: '2026-01-15', status: 'bestaetigt' as const, naehrstoffe: { n: 180, p: 60, k: 120 } },
    { id: '2', typ: 'WDE', betrieb: 'Agrar Schmidt', vvvo: '03-276-5678', datum: '2026-02-01', status: 'gesendet' as const, naehrstoffe: { n: 150, p: 45, k: 90 } },
  ],
  qs: [
    { id: '1', bereich: 'Wareneingangskontrolle', pruefpunkt: 'Lieferschein-Prüfung', erfuellt: true, bemerkung: 'Vollständig', geprueftAm: '2026-02-10' },
    { id: '2', bereich: 'Lagerung', pruefpunkt: 'Temperaturkontrolle Silo', erfuellt: true, bemerkung: '18°C', geprueftAm: '2026-02-10' },
  ],
  nachbau: [
    { id: '1', betrieb: 'Landwirtschaft Müller', sorte: 'Weichweizen Eltan', kultur: 'Weichweizen', flaeche: 45.5, erntejahr: 2025, gebuehr: 682.5, status: 'bezahlt' as const },
  ],
  sachkunde: [
    { id: '1', kunde: 'Landwirtschaft Müller', kundennr: 'K-10023', nachweisNr: 'SK-NDS-2022-4567', ausstellungsdatum: '2022-03-15', gueltigBis: '2025-03-15', ausstellendeStelle: 'LWK Niedersachsen', status: 'ablaufend' as const },
  ],
  vvvo: [
    { id: '1', betriebsname: 'Landwirtschaft Müller', vvvo: '03-276-123456', bundesland: 'Niedersachsen', tierart: 'Rind (Milch)', status: 'aktiv' as const, letzteAktualisierung: '2026-01-15' },
  ],
  zulassungen: [
    { id: '1', produkt: 'Roundup PowerFlex', typ: 'PSM', nummer: '024567-00', behoerde: 'BVL', gueltigBis: '2026-12-31', status: 'aktiv' as const },
  ],
  dispo: [
    { id: '1', artikel: 'Weizen Premium', bestand: 120, mindestbestand: 200, bedarf: 80, empfehlung: 'Nachbestellen: 100 t', prioritaet: 'hoch' as const },
    { id: '2', artikel: 'NPK 15-15-15', bestand: 85, mindestbestand: 100, bedarf: 50, empfehlung: 'Nachbestellen: 65 t', prioritaet: 'mittel' as const },
  ],
  dokumente: [
    { id: '1', name: 'Lieferschein LS-042.pdf', typ: 'PDF', kategorie: 'Lieferscheine', groesse: 125, hochgeladen: '2026-02-10', benutzer: 'admin@valeo.de' },
    { id: '2', name: 'Rechnung RE-2026-042.pdf', typ: 'PDF', kategorie: 'Rechnungen', groesse: 250, hochgeladen: '2026-02-10', benutzer: 'fibu@valeo.de' },
  ],
  fahrzeuge: [
    { id: '1', kennzeichen: 'AB-LH 101', typ: 'LKW 7,5t', kilometerstand: 125000, naechsteInspektion: '2026-03-15', status: 'unterwegs' as const },
    { id: '2', kennzeichen: 'AB-LH 102', typ: 'LKW 18t', kilometerstand: 89000, naechsteInspektion: '2026-05-01', status: 'verfuegbar' as const },
    { id: '3', kennzeichen: 'AB-LH 201', typ: 'Transporter', kilometerstand: 45000, naechsteInspektion: '2026-04-15', status: 'werkstatt' as const },
  ],
  antraege: [
    { id: '1', nummer: 'FA-2026-001', programm: 'Greening', antragsdatum: '2026-01-15', flaeche: 250, betrag: 21250, status: 'bewilligt' as const },
    { id: '2', nummer: 'FA-2026-002', programm: 'AUKM', antragsdatum: '2026-02-01', flaeche: 45, betrag: 5400, status: 'eingereicht' as const },
  ],
  proben: [
    { id: '1', probennummer: 'LB-2026-001', typ: 'Qualitätsprüfung', artikel: 'Weizen Premium', datum: '2026-02-09', labor: 'Lufa Nord-West', status: 'abgeschlossen' as const },
    { id: '2', probennummer: 'LB-2026-002', typ: 'Mykotoxin-Test', artikel: 'Sojaschrot', datum: '2026-02-10', labor: 'Lufa Nord-West', status: 'in-bearbeitung' as const },
  ],
  kampagnen: [
    { id: '1', name: 'Frühlings-Aktion Saatgut', typ: 'E-Mail', zielgruppe: 'Landwirte', startdatum: '2026-03-01', enddatum: '2026-04-30', budget: 3500, status: 'geplant' as const },
    { id: '2', name: 'Herbst-Dünger-Kampagne', typ: 'Print', zielgruppe: 'Bestandskunden', startdatum: '2026-08-01', enddatum: '2026-09-30', budget: 5000, status: 'geplant' as const },
  ],
  projekte: [
    { id: '1', name: 'Silo-Neubau', kunde: 'Eigenbau', startdatum: '2025-09-01', enddatum: '2026-03-31', fortschritt: 75, budget: 250000, status: 'aktiv' as const },
    { id: '2', name: 'Digitalisierung Feldbuch', kunde: 'Intern', startdatum: '2026-01-01', enddatum: '2026-06-30', fortschritt: 20, budget: 45000, status: 'aktiv' as const },
  ],
  laborAuftraege: [
    { id: 'LA-001', chargenId: '260210-WEI-001', labor: 'Labor Nord', analysen: 4, auftragsdatum: '2026-02-10', status: 'in-bearbeitung' as const },
  ],
  serviceAnfragen: [
    { id: '1', nummer: 'SR-2026-001', kunde: 'Landhandel Nord', betreff: 'Lieferverzögerung', datum: '2026-02-10', prioritaet: 'hoch' as const, status: 'neu' as const },
    { id: '2', nummer: 'SR-2026-002', kunde: 'Agrar Müller', betreff: 'Qualitätsreklamation', datum: '2026-02-09', prioritaet: 'normal' as const, status: 'in-bearbeitung' as const },
  ],
  schaeden: [
    { id: '1', nummer: 'SCH-2026-001', art: 'Hagelschaden', datum: '2025-07-15', ort: 'Schlag S-001', schadenhoehe: 12500, status: 'reguliert' as const },
  ],
  zapfungen: [
    { id: '1', kennzeichen: 'AB-LH 101', artikel: 'Diesel', menge: 120.5, zeitstempel: '2026-02-10 07:15', fahrer: 'Schmidt' },
    { id: '2', kennzeichen: 'AB-LH 102', artikel: 'Diesel', menge: 85.0, zeitstempel: '2026-02-10 06:45', fahrer: 'Müller' },
  ],
  fahrer: [
    { id: '1', name: 'Max Schmidt', fuehrerschein: 'C', fahrzeug: 'LKW-01', status: 'unterwegs' as const, tourenHeute: 2 },
    { id: '2', name: 'Peter Müller', fuehrerschein: 'CE', fahrzeug: 'LKW-02', status: 'verfuegbar' as const, tourenHeute: 1 },
  ],
  verladungen: [
    { id: '1', kennzeichen: 'AB-CD 1234', artikel: 'Weizen', menge: 25.0, lieferscheinNr: 'LS-2026-042', datum: '2026-02-10', status: 'in-verladung' as const },
  ],
  versicherungen: [
    { id: '1', art: 'Betriebshaftpflicht', versicherer: 'R+V Versicherung', vertragsnummer: 'RV-2024-1234', praemie: 3200, ablauf: '2026-12-31', status: 'aktiv' as const },
    { id: '2', art: 'Gebäudeversicherung', versicherer: 'Allianz', vertragsnummer: 'AL-2023-5678', praemie: 8500, ablauf: '2026-06-30', status: 'aktiv' as const },
  ],
  vertraege: [
    { id: '1', nummer: 'RV-2026-001', partner: 'Landhandel Nord', typ: 'Verkauf', artikel: 'Weizen', menge: 500, restmenge: 120, laufzeitBis: '2026-06-30', status: 'aktiv' as const },
    { id: '2', nummer: 'RV-2025-008', partner: 'Mühle Süd', typ: 'Verkauf', artikel: 'Roggen', menge: 200, restmenge: 0, laufzeitBis: '2026-03-31', status: 'auslaufend' as const },
  ],
  waagen: [
    { id: 'W-001', standort: 'Annahme 1', typ: 'LKW-Waage', maxKapazitaet: 60, letzteEichung: '2025-08-15', naechsteEichung: '2026-08-15', status: 'aktiv' as const },
    { id: 'W-002', standort: 'Verladung', typ: 'LKW-Waage', maxKapazitaet: 80, letzteEichung: '2025-06-01', naechsteEichung: '2026-06-01', status: 'aktiv' as const },
  ],
  wiegungen: [
    { id: '1', kennzeichen: 'AB-CD 1234', artikel: 'Weizen', brutto: 48.5, tara: 23.5, netto: 25.0, zeitstempel: '2026-02-10 14:32', waage: 'W-001' },
    { id: '2', kennzeichen: 'EF-GH 5678', artikel: 'Raps', brutto: 42.0, tara: 23.5, netto: 18.5, zeitstempel: '2026-02-10 13:45', waage: 'W-001' },
  ],
  wartung: [
    { id: '1', name: 'Silo 1', typ: 'Lagersilo', standort: 'Hauptstandort', letzteWartung: '2025-12-01', naechsteWartung: '2026-03-01', status: 'aktiv' as const },
    { id: '2', name: 'LKW-Waage W-001', typ: 'Wiegetechnik', standort: 'Annahme', letzteWartung: '2025-08-15', naechsteWartung: '2026-02-15', status: 'wartung' as const },
  ],
  workflowExecutions: [
    { id: '1', ruleId: '2', triggerEntity: 'Angebot', triggerAction: 'GENEHMIGT', targetEntity: 'Bestellung', targetAction: 'CREATE_FROM_ANGEBOT', status: 'SUCCESS' as const, startedAt: '2026-02-10T10:30:00Z', completedAt: '2026-02-10T10:30:05Z', actorId: 'user123' },
  ],
  workflowRules: [
    { id: '1', triggerEntity: 'Anfrage', triggerAction: 'FREIGEGEBEN', targetEntity: 'Anfrage', targetAction: 'ANGEBOTSPHASE', active: true },
    { id: '2', triggerEntity: 'Angebot', triggerAction: 'GENEHMIGT', targetEntity: 'Bestellung', targetAction: 'CREATE_FROM_ANGEBOT', active: true },
    { id: '3', triggerEntity: 'Bestellung', triggerAction: 'BESTELLT', targetEntity: 'Bestellung', targetAction: 'NOTIFY_LIEFERANT', active: true },
  ],
  zertifikate: [
    { id: '1', art: 'Bio-Zertifikat', standard: 'EU-Bio-Verordnung', nummer: 'BIO-2025-1234', gueltigBis: '2026-12-31', audit: '2026-02-15', status: 'gueltig' as const },
    { id: '2', art: 'QS-Zertifikat', standard: 'QS-GAP', nummer: 'QS-2025-5678', gueltigBis: '2026-06-30', audit: '2025-12-01', status: 'gueltig' as const },
  ],
  managementDashboard: {
    kpis: [
      { label: 'Umsatz MTD', value: '1.85M', trend: 12.5, einheit: 'EUR' },
      { label: 'Marge', value: '18.2%', trend: 2.1 },
      { label: 'Offene Aufträge', value: '42', trend: -5.3 },
      { label: 'Liquidität', value: '785K', trend: 8.7, einheit: 'EUR' },
    ],
    alerts: [
      { id: '1', typ: 'warnung' as const, text: 'Kreditlimit Schmidt GmbH zu 92% ausgeschöpft', datum: '2026-02-10' },
      { id: '2', typ: 'info' as const, text: 'Quartalsbericht Q4/2025 verfügbar', datum: '2026-02-08' },
    ],
    topProducts: [
      { name: 'Weizen', umsatz: 525000 }, { name: 'Raps', umsatz: 310000 }, { name: 'Dünger NPK', umsatz: 280000 },
    ],
    topCustomers: [
      { name: 'Agrar Schmidt GmbH', umsatz: 185000 }, { name: 'Landhandel Nord', umsatz: 142000 }, { name: 'Müller Agrar KG', umsatz: 98000 },
    ],
  } as ManagementDashboard,
}

// ── Helper ─────────────────────────────────────────────────────────────

function makeHook<T>(key: string[], endpoint: string, fallback: T, stale = 2 * 60 * 1000) {
  return () => useQuery({
    queryKey: key,
    queryFn: async () => {
      const r = await apiClient.get<unknown>(endpoint)
      const data = r.data as { items?: T } | T
      if (data && typeof data === 'object' && !Array.isArray(data) && 'items' in data) {
        if (data.items === undefined || data.items === null) {
          throw new Error(`Invalid API payload for ${endpoint}: missing items`)
        }
        return data.items as T
      }
      return data as T
    },
    initialData: fallback,
    staleTime: stale,
  })
}

// ── Hooks ──────────────────────────────────────────────────────────────

export const useBankkonten = makeHook<BankKonto[]>(['banken', 'konten'], '/api/v1/banken/konten', fb.bankkonten)
export const useBenachrichtigungen = makeHook<Benachrichtigung[]>(['benachrichtigungen'], '/api/v1/benachrichtigungen', fb.benachrichtigungen, 30 * 1000)
export const useChargen = makeHook<Charge[]>(['chargen'], '/api/v1/chargen', fb.chargen)
export const useCrossCompliance = makeHook<ComplianceItem[]>(['compliance', 'cross'], '/api/v1/compliance/cross-compliance', fb.compliance, 5 * 60 * 1000)
export const useENNIMeldungen = makeHook<ENNIMeldung[]>(['compliance', 'enni'], '/api/v1/compliance/enni-meldungen', fb.enni)
export const useQSCheckliste = makeHook<QSItem[]>(['compliance', 'qs'], '/api/v1/compliance/qs-checkliste', fb.qs)
export const useSaatgutNachbau = makeHook<SaatgutNachbau[]>(['compliance', 'nachbau'], '/api/v1/compliance/saatgut-nachbau', fb.nachbau)
export const useSachkundeRegister = makeHook<Sachkundenachweis[]>(['compliance', 'sachkunde'], '/api/v1/compliance/sachkunde-register', fb.sachkunde)
export const useVVVORegister = makeHook<VVVOBetrieb[]>(['compliance', 'vvvo'], '/api/v1/compliance/vvvo-register', fb.vvvo)
export const useZulassungenRegister = makeHook<Zulassung[]>(['compliance', 'zulassungen'], '/api/v1/compliance/zulassungen-register', fb.zulassungen)
export const useDisposition = makeHook<DispoPosition[]>(['disposition'], '/api/v1/disposition', fb.dispo)
export const useDokumenteAblage = makeHook<Dokument[]>(['dokumente'], '/api/v1/dokumente', fb.dokumente)
export const useFahrzeuge = makeHook<Fahrzeug[]>(['fuhrpark', 'fahrzeuge'], '/api/v1/fuhrpark/fahrzeuge', fb.fahrzeuge)
export const useFoerderAntraege = makeHook<Antrag[]>(['foerderung'], '/api/v1/foerderung/antraege', fb.antraege)
export const useLaborProben = makeHook<Probe[]>(['labor', 'proben'], '/api/v1/labor/proben', fb.proben)
export const useMarketingKampagnen = makeHook<Kampagne[]>(['marketing', 'kampagnen'], '/api/v1/marketing/kampagnen', fb.kampagnen)
export const useProjekte = makeHook<Projekt[]>(['projekte'], '/api/v1/projekte', fb.projekte)
export const useLaborAuftraege = makeHook<LaborAuftrag[]>(['qualitaet', 'labor'], '/api/v1/qualitaet/labor-auftraege', fb.laborAuftraege)
export const useServiceAnfragen = makeHook<ServiceAnfrage[]>(['service', 'anfragen'], '/api/v1/service/anfragen', fb.serviceAnfragen)
export const useSchaeden = makeHook<Schaden[]>(['schaeden'], '/api/v1/schaeden', fb.schaeden)
export const useZapfungen = makeHook<Zapfung[]>(['tankstelle', 'zapfungen'], '/api/v1/tankstelle/zapfungen', fb.zapfungen)
export const useFahrerListe = makeHook<Fahrer[]>(['transporte', 'fahrer'], '/api/v1/transporte/fahrer', fb.fahrer)
export const useVerladungen = makeHook<VerladungItem[]>(['verladung'], '/api/v1/verladung', fb.verladungen)
export const useVersicherungen = makeHook<Versicherung[]>(['versicherungen'], '/api/v1/versicherungen', fb.versicherungen)
export const useRahmenvertraege = makeHook<Vertrag[]>(['vertraege', 'rahmen'], '/api/v1/vertrag/rahmenvertraege', fb.vertraege)
export const useWaagen = makeHook<Waage[]>(['waage', 'liste'], '/api/v1/waage/waagen', fb.waagen)
export const useWiegungen = makeHook<Wiegung[]>(['waage', 'wiegungen'], '/api/v1/waage/wiegungen', fb.wiegungen, 30 * 1000)
export const useWartungAnlagen = makeHook<WartungAnlage[]>(['wartung', 'anlagen'], '/api/v1/wartung/anlagen', fb.wartung)
export const useWorkflowExecutions = makeHook<WorkflowExecution[]>(['workflow', 'executions'], '/api/v1/workflow/executions', fb.workflowExecutions, 30 * 1000)
export const useWorkflowRules = makeHook<WorkflowRule[]>(['workflow', 'rules'], '/api/v1/workflow/rules', fb.workflowRules, 5 * 60 * 1000)
export const useZertifikateListe = makeHook<Zertifikat[]>(['zertifikate'], '/api/v1/zertifikate', fb.zertifikate, 5 * 60 * 1000)
export const useManagementDashboard = makeHook<ManagementDashboard>(['management', 'dashboard'], '/api/v1/management/dashboard', fb.managementDashboard, 60 * 1000)
