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
export type LaborAuftrag = {
  id: string
  chargenId: string
  labor: string
  analysen: number
  auftragsdatum: string
  status: 'offen' | 'in-bearbeitung' | 'abgeschlossen'
  befund?: {
    id: string
    probennummer: string
    entscheidung: 'freigeben' | 'sperren' | 'nachpruefung' | null
    datum?: string | null
    labor: string
  } | null
  qs_entscheidung?: 'freigeben' | 'sperren' | 'nachpruefung' | null
  folgeaktion?: 'qs_freigeben' | 'charge_sperren' | 'nachpruefung_anlegen' | 'befund_erfassen'
}
export type ServiceAnfrage = { id: string; nummer: string; kunde: string; betreff: string; datum: string; prioritaet: 'hoch' | 'normal' | 'niedrig'; status: 'neu' | 'in-bearbeitung' | 'erledigt' }
/**
 * Eine Schadenmeldung, wie `/api/v1/schaeden/meldungen` sie liefert.
 *
 * Bis zum 06.10.2026 zeigte `useSchaeden` auf `/api/v1/schaeden` — eine Route,
 * die es nicht gibt — und `makeHook` hielt mit `initialData` eine erfundene
 * Hagelschadenmeldung ueber 12.500 EUR sichtbar. Die Maske zeigte also dauerhaft
 * eine Attrappe, und der Fehlschlag der Abfrage fiel nicht auf.
 */
export type Schaden = {
  id: string
  meldungsnummer: string
  art: string
  schadendatum?: string | null
  ort?: string | null
  beschreibung: string
  schadenhoehe: number | string
  status: 'ENTWURF' | 'GEMELDET' | 'IN_BEARBEITUNG' | 'REGULIERT' | 'ABGELEHNT'
  melden_bis?: string | null
  frist_ueberschritten?: boolean
}
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

// Bis 20.10.2026 standen hier erfundene Fallback-Daten (Bankkonten mit Salden, Compliance-Stand,
// Management-Kennzahlen, Top-Kunden …) als initialData: Nutzer sahen sie, bis die Antwort kam, und bei Fehlern
// dauerhaft. Jetzt beginnt jede Abfrage leer; Fehler- und Leerzustand zeigt die Seite.
const LEERES_DASHBOARD: ManagementDashboard = { kpis: [], alerts: [], topProducts: [], topCustomers: [] }

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
    // Sofort veraltet: Sonst gilt der Platzhalter als frisch geladen und
    // `staleTime` verhindert den Mount-Fetch (Nutzermeldung 17.07.2026).
    initialDataUpdatedAt: 0,
    staleTime: stale,
  })
}

// ── Hooks ──────────────────────────────────────────────────────────────

export const useBankkonten = makeHook<BankKonto[]>(['banken', 'konten'], '/api/v1/banken/konten', [])
export const useBenachrichtigungen = makeHook<Benachrichtigung[]>(['benachrichtigungen'], '/api/v1/benachrichtigungen', [], 30 * 1000)
export const useChargen = makeHook<Charge[]>(['chargen'], '/api/v1/chargen', [])
export const useCrossCompliance = makeHook<ComplianceItem[]>(['compliance', 'cross'], '/api/v1/compliance/cross-compliance', [], 5 * 60 * 1000)
export const useENNIMeldungen = makeHook<ENNIMeldung[]>(['compliance', 'enni'], '/api/v1/compliance/enni-meldungen', [])
export const useQSCheckliste = makeHook<QSItem[]>(['compliance', 'qs'], '/api/v1/compliance/qs-checkliste', [])
export const useSaatgutNachbau = makeHook<SaatgutNachbau[]>(['compliance', 'nachbau'], '/api/v1/compliance/saatgut-nachbau', [])
export const useSachkundeRegister = makeHook<Sachkundenachweis[]>(['compliance', 'sachkunde'], '/api/v1/compliance/sachkunde-register', [])
export const useVVVORegister = makeHook<VVVOBetrieb[]>(['compliance', 'vvvo'], '/api/v1/compliance/vvvo-register', [])
export const useZulassungenRegister = makeHook<Zulassung[]>(['compliance', 'zulassungen'], '/api/v1/compliance/zulassungen-register', [])
export const useDisposition = makeHook<DispoPosition[]>(['disposition'], '/api/v1/disposition', [])
export const useDokumenteAblage = makeHook<Dokument[]>(['dokumente'], '/api/v1/dokumente', [])
export const useFahrzeuge = makeHook<Fahrzeug[]>(['fuhrpark', 'fahrzeuge'], '/api/v1/fuhrpark/fahrzeuge', [])
export const useFoerderAntraege = makeHook<Antrag[]>(['foerderung'], '/api/v1/foerderung/antraege', [])
export const useLaborProben = makeHook<Probe[]>(['labor', 'proben'], '/api/v1/labor/proben', [])
export const useMarketingKampagnen = makeHook<Kampagne[]>(['marketing', 'kampagnen'], '/api/v1/marketing/kampagnen', [])
export const useProjekte = makeHook<Projekt[]>(['projekte'], '/api/v1/projekte', [])
export const useLaborAuftraege = makeHook<LaborAuftrag[]>(['qualitaet', 'labor'], '/api/v1/qualitaet/labor-auftraege', [])
export const useServiceAnfragen = makeHook<ServiceAnfrage[]>(['service', 'anfragen'], '/api/v1/service/anfragen', [])
// Ohne Vorbefuellung: Eine leere Liste ist die Wahrheit, wenn nichts erfasst
// ist, und ein Fehlschlag soll als Fehler sichtbar werden.
export const useSchaeden = makeHook<Schaden[]>(
  ['schaeden'], '/api/v1/schaeden/meldungen', [],
)
export const useZapfungen = makeHook<Zapfung[]>(['tankstelle', 'zapfungen'], '/api/v1/tankstelle/zapfungen', [])
type FahrerApi = {
  id: string
  name?: string
  vorname?: string | null
  fuehrerschein?: string | null
  fahrzeug?: string | null
  status?: string | null
  touren_heute?: number | null
  tourenHeute?: number | null
}

export function mapFahrerZeile(row: FahrerApi): Fahrer {
  const status = row.status === 'unterwegs' || row.status === 'pause' ? row.status : 'verfuegbar'
  return {
    id: row.id,
    name: [row.vorname, row.name].filter(Boolean).join(' '),
    fuehrerschein: row.fuehrerschein || '',
    fahrzeug: row.fahrzeug || '',
    status,
    tourenHeute: Number(row.tourenHeute ?? row.touren_heute ?? 0),
  }
}

export function useFahrerListe() {
  return useQuery({
    queryKey: ['transporte', 'fahrer'],
    queryFn: async () => {
      const { data } = await apiClient.get<FahrerApi[]>('/api/v1/transporte/fahrer')
      return (Array.isArray(data) ? data : []).map(mapFahrerZeile)
    },
  })
}
export const useVerladungen = makeHook<VerladungItem[]>(['verladung'], '/api/v1/verladung', [])
export const useVersicherungen = makeHook<Versicherung[]>(['versicherungen'], '/api/v1/versicherungen', [])
export const useRahmenvertraege = makeHook<Vertrag[]>(['vertraege', 'rahmen'], '/api/v1/vertrag/rahmenvertraege', [])
export const useWaagen = makeHook<Waage[]>(['waage', 'liste'], '/api/v1/waage/waagen', [])
export const useWiegungen = makeHook<Wiegung[]>(['waage', 'wiegungen'], '/api/v1/waage/wiegungen', [], 30 * 1000)
export const useWartungAnlagen = makeHook<WartungAnlage[]>(['wartung', 'anlagen'], '/api/v1/wartung/anlagen', [])
export const useWorkflowExecutions = makeHook<WorkflowExecution[]>(['workflow', 'executions'], '/api/v1/workflow/executions', [], 30 * 1000)
export const useWorkflowRules = makeHook<WorkflowRule[]>(['workflow', 'rules'], '/api/v1/workflow/rules', [], 5 * 60 * 1000)
export const useZertifikateListe = makeHook<Zertifikat[]>(['zertifikate'], '/api/v1/zertifikate', [], 5 * 60 * 1000)
export const useManagementDashboard = makeHook<ManagementDashboard>(['management', 'dashboard'], '/api/v1/management/dashboard', LEERES_DASHBOARD, 60 * 1000)
