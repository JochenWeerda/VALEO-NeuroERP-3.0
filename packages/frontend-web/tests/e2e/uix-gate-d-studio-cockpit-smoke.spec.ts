/**
 * Gate D (Browser) — Made-by-Studio Sichtnachweis fuer Studio-Cockpits
 * aus den Open-Routes-Hebungen (Batch 24–28).
 *
 * Mockt ScreenDefinition + flache Listen/Overview-APIs; prueft Routing,
 * native-cockpit Runtime-Shell und sichtbaren Titel (publizierte Route).
 */
import { expect, test, type Page } from '@playwright/test'
import { setzeUiTestsitzung } from './helpers/ui-testsitzung'

type CockpitCase = {
  label: string
  path: string
  screenId: string
  testId: string
  title: string
  listEndpoint?: string
  overviewEndpoint?: string
  /** Specialized workbench contract — mounts Fach-Surface inside native-cockpit. */
  specializedType?:
    | 'pricing_workbench'
    | 'fleet_workbench'
    | 'lager_workbench'
    | 'agrar_workbench'
    | 'finance_workbench'
    | 'feed_workbench'
    | 'admin_workbench'
    | 'weighing'
    | 'intake'
  specializedFields?: Array<{ key: string; label: string }>
  /** ARIA tablist name inside the specialized surface (Studio Tabs-Invariante). */
  specializedTablist?: string
  /** Accessible name / text proving the specialized surface mounted. */
  specializedLandmark?: string
}

const COCKPIT_CASES: CockpitCase[] = [
  {
    label: 'admin/externe-gates',
    path: '/admin/externe-gates',
    screenId: 'admin/externe-gates',
    testId: 'screen-admin/externe-gates',
    title: 'Externe Gates',
    overviewEndpoint: '/api/v1/external-gates/overview',
    listEndpoint: '/api/v1/external-gates/items',
  },
  {
    label: 'admin/command-monitor',
    path: '/admin/command-monitor',
    screenId: 'admin/command-monitor',
    testId: 'screen-admin/command-monitor',
    title: 'Command-Monitor',
  },
  {
    label: 'agrar/milchvieh-crosssell',
    path: '/agrar/milchvieh-crosssell',
    screenId: 'agrar/milchvieh-crosssell',
    testId: 'screen-agrar/milchvieh-crosssell',
    title: 'Milchvieh Cross-Sell',
  },
  // Specialized workbenches (Batches 28–38): native-cockpit shell + specialized surface
  {
    label: 'lager/materialfluss',
    path: '/lager/materialfluss',
    screenId: 'lager/materialfluss',
    testId: 'screen-lager/materialfluss',
    title: 'Materialfluss',
    specializedType: 'lager_workbench',
    specializedFields: [
      { key: 'warehouse_id', label: 'Lager' },
      { key: 'node_count', label: 'Knoten' },
      { key: 'edge_count', label: 'Kanten' },
    ],
  },
  {
    label: 'konditionen/konditionssystem',
    path: '/konditionen/konditionssystem',
    screenId: 'konditionen/konditionssystem',
    testId: 'screen-konditionen/konditionssystem',
    title: 'Konditionssystem',
    specializedType: 'pricing_workbench',
    specializedFields: [
      { key: 'preisliste_count', label: 'Preislisten' },
      { key: 'rabattgruppe_count', label: 'Rabattgruppen' },
      { key: 'individualpreis_count', label: 'Individualpreise' },
    ],
    specializedTablist: 'Konditionssystem',
  },
  {
    label: 'fuhrpark/fahrzeug-vertiefung',
    path: '/fuhrpark/fahrzeug-vertiefung',
    screenId: 'fuhrpark/fahrzeug-vertiefung',
    testId: 'screen-fuhrpark/fahrzeug-vertiefung',
    title: 'Fahrzeug-Vertiefung',
    specializedType: 'fleet_workbench',
    specializedFields: [
      { key: 'fahrzeug_id', label: 'Fahrzeug' },
      { key: 'status', label: 'Status' },
      { key: 'schaden_offen', label: 'Offene Schäden' },
      { key: 'bussgeld_offen', label: 'Offene Bußgelder' },
    ],
    specializedTablist: 'Fahrzeug-Vertiefung',
  },
  {
    label: 'agrar/kunden-schlagkartei',
    path: '/agrar/kunden-schlagkartei',
    screenId: 'agrar/kunden-schlagkartei',
    testId: 'screen-agrar/kunden-schlagkartei',
    title: 'Kundenschlagkartei',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'kunden_nr', label: 'Kunde' },
      { key: 'schlag_count', label: 'Schläge' },
      { key: 'massnahme_count', label: 'Maßnahmen' },
      { key: 'gesamt_flaeche_ha', label: 'Fläche ha' },
    ],
    specializedTablist: 'Schlagkartei',
  },
  {
    label: 'agrar/ernte-annahme-erfassung',
    path: '/agrar/ernte-annahme-erfassung',
    screenId: 'agrar/ernte-annahme-erfassung',
    testId: 'screen-agrar/ernte-annahme-erfassung',
    title: 'Ernte-Annahme-Erfassung',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'acceptance_number', label: 'Annahmenummer' },
      { key: 'customer_id', label: 'Kunde' },
      { key: 'release_status', label: 'Freigabe' },
      { key: 'delivery_date', label: 'Lieferdatum' },
    ],
    // Ohne Annahme-ID erscheint oft die Listen-/Ansichts-Registerleiste zuerst.
    specializedTablist: 'Annahme-Ansichten',
  },
  {
    label: 'finance/bank-abgleich',
    path: '/finance/bank-abgleich',
    screenId: 'finance/bank-abgleich',
    testId: 'native-cockpit-finance-bank-abgleich',
    title: 'Bankabgleich',
    specializedType: 'finance_workbench',
    specializedFields: [
      { key: 'kontoId', label: 'Bankkonto' },
      { key: 'camtFile', label: 'Kontoauszug' },
      { key: 'statementId', label: 'Statement' },
      { key: 'startSaldo', label: 'Startsaldo' },
      { key: 'endSaldo', label: 'Endsaldo' },
      { key: 'gebuchteUmsaetze', label: 'Umsätze' },
      { key: 'zugeordnet', label: 'Zugeordnet' },
      { key: 'nichtZugeordnet', label: 'Nicht zugeordnet' },
      { key: 'abgleichsDifferenz', label: 'Differenz' },
      { key: 'accountingBalance', label: 'Hauptbuchsaldo' },
      { key: 'zuordnungData', label: 'Umsatzzeilen' },
      { key: 'importErrors', label: 'Importprotokoll' },
      { key: 'differences', label: 'Differenzen' },
      { key: 'comparisonState', label: 'Nachweisstatus' },
    ],
    specializedLandmark: 'Bankabgleich Arbeitsbereich',
  },
  {
    label: 'mahnwesen/mahnlauf',
    path: '/mahnwesen/mahnlauf',
    screenId: 'mahnwesen/mahnlauf',
    testId: 'native-cockpit-mahnwesen-mahnlauf',
    title: 'Mahnlauf',
    specializedType: 'finance_workbench',
    specializedFields: [
      { key: 'op_id', label: 'Posten' },
      { key: 'rechnungsnr', label: 'Rechnung' },
      { key: 'partner', label: 'Partner' },
      { key: 'tage_ueberfaellig', label: 'Überfällig' },
      { key: 'offen', label: 'Offen' },
      { key: 'aktuelle_stufe', label: 'Aktuelle Stufe' },
      { key: 'naechste_stufe', label: 'Nächste Stufe' },
      { key: 'dunning_fee', label: 'Gebühr' },
      { key: 'interest', label: 'Zinsen' },
      { key: 'total_amount', label: 'Gesamt' },
      { key: 'id', label: 'Mahnung' },
      { key: 'stufe', label: 'Stufe' },
      { key: 'gesamt', label: 'Gesamtbetrag' },
      { key: 'frist', label: 'Frist' },
      { key: 'datum', label: 'Datum' },
      { key: 'status', label: 'Status' },
      { key: 'versand_art', label: 'Versandart' },
      { key: 'empfaenger', label: 'Empfänger' },
      { key: 'auswahl', label: 'Auswahl' },
    ],
    specializedLandmark: 'Mahnlauf Arbeitsbereich',
  },
  {
    label: 'agrar/milchvieh-karte',
    path: '/agrar/milchvieh-karte',
    screenId: 'agrar/milchvieh-karte',
    testId: 'screen-agrar/milchvieh-karte',
    title: 'Milchvieh-Karte',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'feature_count', label: 'Betriebe' },
    ],
    specializedLandmark: 'Milchvieh-Karte Arbeitsbereich',
  },
  {
    label: 'futtermittel/fuetterungsdokumentation-mobil',
    path: '/futtermittel/fuetterungsdokumentation-mobil',
    screenId: 'futtermittel/fuetterungsdokumentation-mobil',
    testId: 'feed-mobile-documentation',
    title: 'Fütterungsdokumentation mobil',
    specializedType: 'feed_workbench',
    specializedFields: [
      { key: 'plan_version_id', label: 'Planversion' },
      { key: 'group_id', label: 'Gruppe' },
      { key: 'actual_kg', label: 'Ist-Menge' },
      { key: 'rest_kg', label: 'Restfutter' },
      { key: 'tm_pct', label: 'TM' },
    ],
    specializedLandmark: 'Mobile Fütterungsdokumentation Arbeitsbereich',
  },
  {
    label: 'futtermittel/rationseditor',
    path: '/futtermittel/rationseditor',
    screenId: 'futtermittel/rationseditor',
    testId: 'feed-ration-editor',
    title: 'Rationseditor',
    specializedType: 'feed_workbench',
    specializedFields: [
      { key: 'ration_id', label: 'Ration' },
      { key: 'group_id', label: 'Gruppe' },
      { key: 'version_no', label: 'Version' },
      { key: 'status', label: 'Status' },
    ],
    specializedLandmark: 'Rationseditor Arbeitsbereich',
  },
  {
    label: 'waage/liste',
    path: '/waage/liste',
    screenId: 'waage/liste',
    testId: 'native-cockpit-waage-liste',
    title: 'Waagen',
    specializedType: 'weighing',
    specializedFields: [
      { key: 'id', label: 'Waage' },
      { key: 'standort', label: 'Standort' },
      { key: 'typ', label: 'Typ' },
      { key: 'maxKapazitaet', label: 'Max. Kapazität' },
      { key: 'letzteEichung', label: 'Letzte Eichung' },
      { key: 'naechsteEichung', label: 'Nächste Eichung' },
      { key: 'status', label: 'Status' },
      { key: 'letztes_eichdatum', label: 'Eichdatum' },
      { key: 'naechste_eichfaelligkeit', label: 'Eichfälligkeit' },
      { key: 'eichamt', label: 'Eichamt' },
      { key: 'zertifikat_nr', label: 'Zertifikat' },
      { key: 'importScaleId', label: 'Import-Waage' },
      { key: 'importFile', label: 'Import-Datei' },
      { key: 'fehlerToleranz', label: 'Fehlertoleranz' },
      { key: 'importRaw', label: 'Import roh' },
      { key: 'importError', label: 'Importfehler' },
      { key: 'importRetryCount', label: 'Import-Retries' },
    ],
    specializedLandmark: 'Waagenliste Arbeitsbereich',
  },
  {
    label: 'annahme/warteschlange',
    path: '/annahme/warteschlange',
    screenId: 'annahme/warteschlange',
    testId: 'native-cockpit-annahme-warteschlange',
    title: 'Annahme-Warteschlange',
    specializedType: 'intake',
    specializedFields: [
      { key: 'kennzeichen', label: 'Kennzeichen' },
      { key: 'lieferant', label: 'Lieferant' },
      { key: 'artikel', label: 'Artikel' },
      { key: 'status', label: 'Status' },
      { key: 'ankunft', label: 'Ankunft' },
      { key: 'wartezeit', label: 'Wartezeit' },
      { key: 'lieferschein_nr', label: 'Lieferschein' },
    ],
    specializedLandmark: 'Annahme-Warteschlange Arbeitsbereich',
  },
  {
    label: 'annahme/lkw-registrierung',
    path: '/annahme/lkw-registrierung',
    screenId: 'annahme/lkw-registrierung',
    testId: 'native-cockpit-annahme-lkw-registrierung',
    title: 'LKW-Registrierung',
    specializedType: 'intake',
    specializedFields: [
      { key: 'kennzeichen', label: 'Kennzeichen' },
      { key: 'lieferant', label: 'Lieferant' },
      { key: 'lieferscheinNr', label: 'Lieferschein' },
      { key: 'articleId', label: 'Artikel-ID' },
      { key: 'artikel', label: 'Artikel' },
      { key: 'ankunftszeit', label: 'Ankunft' },
      { key: 'prioritaet', label: 'Priorität' },
      { key: 'attachmentIds', label: 'Anhänge' },
    ],
    specializedLandmark: 'LKW-Registrierung Arbeitsbereich',
  },
  {
    label: 'annahme/qualitaets-check',
    path: '/annahme/qualitaets-check',
    screenId: 'annahme/qualitaets-check',
    testId: 'native-cockpit-annahme-qualitaets-check',
    title: 'Qualitätsprüfung',
    specializedType: 'intake',
    specializedFields: [
      { key: 'lieferscheinNr', label: 'Lieferschein' },
      { key: 'artikel', label: 'Artikel' },
      { key: 'feuchtigkeit', label: 'Feuchtigkeit' },
      { key: 'protein', label: 'Protein' },
      { key: 'verunreinigung', label: 'Verunreinigung' },
      { key: 'fremdgeruch', label: 'Fremdgeruch' },
      { key: 'schaedlinge', label: 'Schädlinge' },
      { key: 'farbe', label: 'Farbe' },
      { key: 'bemerkungen', label: 'Bemerkungen' },
      { key: 'ergebnis', label: 'Ergebnis' },
    ],
    specializedLandmark: 'Qualitätsprüfung Arbeitsbereich',
  },
  {
    label: 'annahme/rohware',
    path: '/annahme/rohware',
    screenId: 'annahme/rohware',
    testId: 'native-cockpit-annahme-rohware',
    title: 'Rohware-Annahme',
    specializedType: 'intake',
    specializedFields: [
      { key: 'lieferant', label: 'Lieferant' },
      { key: 'kennzeichen', label: 'Kennzeichen' },
      { key: 'lieferscheinNr', label: 'Lieferschein' },
      { key: 'datum', label: 'Datum' },
      { key: 'artikel', label: 'Artikel' },
      { key: 'bruttoKg', label: 'Brutto' },
      { key: 'taraKg', label: 'Tara' },
      { key: 'lagerZiel', label: 'Lagerziel' },
      { key: 'feuchtePct', label: 'Feuchte' },
      { key: 'besatzPct', label: 'Besatz' },
      { key: 'fallzahl', label: 'Fallzahl' },
      { key: 'customer_id', label: 'Kunde' },
    ],
    specializedLandmark: 'Rohware-Annahme Arbeitsbereich',
  },
  {
    label: 'waage/wiegungen',
    path: '/waage/wiegungen',
    screenId: 'waage/wiegungen',
    testId: 'native-cockpit-waage-wiegungen',
    title: 'Wiegungen',
    specializedType: 'weighing',
    specializedFields: [
      { key: 'ticketNumber', label: 'Wiegeschein' },
      { key: 'scaleId', label: 'Waage' },
      { key: 'vehiclePlate', label: 'Kennzeichen' },
      { key: 'grossWeight', label: 'Brutto' },
      { key: 'tareWeight', label: 'Tara' },
      { key: 'moisturePct', label: 'Feuchte' },
      { key: 'impuritiesPct', label: 'Besatz' },
      { key: 'selectedTicketId', label: 'Ticket' },
      { key: 'selectedContractId', label: 'Kontrakt' },
    ],
    specializedLandmark: 'Wiegungen Arbeitsbereich',
  },
  {
    label: 'annahme/abrechnung',
    path: '/annahme/abrechnung',
    screenId: 'annahme/abrechnung',
    testId: 'screen-annahme/abrechnung',
    title: 'Annahme-Abrechnung',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'settlement_count', label: 'Abrechnungen' },
    ],
    specializedLandmark: 'Annahme-Abrechnung Arbeitsbereich',
  },
  {
    label: 'admin/voice-channel',
    path: '/admin/voice-channel',
    screenId: 'admin/voice-channel',
    testId: 'native-cockpit-admin-voice-channel',
    title: 'Voice-Kanal',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'enabled', label: 'Aktiv' },
      { key: 'last_utterance', label: 'Letzte Äußerung' },
    ],
    specializedLandmark: 'Voice-Kanal Arbeitsbereich',
  },
  {
    label: 'admin/vordruck-editor',
    path: '/admin/vordruck-editor',
    screenId: 'admin/vordruck-editor',
    testId: 'native-cockpit-admin-vordruck-editor',
    title: 'Belegformular-Vordruck-Editor',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'id', label: 'ID' },
      { key: 'name', label: 'Name' },
      { key: 'kategorie', label: 'Kategorie' },
    ],
    specializedLandmark: 'Vordruck-Editor Arbeitsbereich',
  },
  {
    label: 'admin/screen-studio',
    path: '/admin/screen-studio',
    screenId: 'admin/screen-studio',
    testId: 'native-cockpit-admin-screen-studio',
    title: 'Masken-Studio',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'screen_id', label: 'Maske' },
      { key: 'status', label: 'Status' },
    ],
    specializedLandmark: 'Masken-Studio Arbeitsbereich',
  },
  {
    label: 'admin/GapPipelineConsole',
    path: '/admin/GapPipelineConsole',
    screenId: 'admin/GapPipelineConsole',
    testId: 'native-cockpit-admin-GapPipelineConsole',
    title: 'GAP-Pipeline Konsole',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'year', label: 'Jahr' },
      { key: 'pipeline_complete', label: 'Pipeline fertig' },
      { key: 'gap_payments_count', label: 'GAP-Zahlungen' },
    ],
    specializedLandmark: 'GAP-Pipeline Arbeitsbereich',
  },
  {
    label: 'admin/agenten-integration',
    path: '/admin/agenten-integration',
    screenId: 'admin/agenten-integration',
    testId: 'native-cockpit-admin-agenten-integration',
    title: 'Agenten-Integration',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'tenant_id', label: 'Mandant' },
      { key: 'section', label: 'Abschnitt' },
    ],
    specializedLandmark: 'Agenten-Integration Arbeitsbereich',
  },
  {
    label: 'admin/setup/dms-integration',
    path: '/admin/setup/dms-integration',
    screenId: 'admin/setup/dms-integration',
    testId: 'native-cockpit-admin-setup-dms-integration',
    title: 'DMS-Integration',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'status', label: 'Status' },
      { key: 'connected', label: 'Verbunden' },
    ],
    specializedLandmark: 'DMS-Integration Arbeitsbereich',
  },
  {
    label: 'admin/control-center',
    path: '/admin/control-center',
    screenId: 'admin/control-center',
    testId: 'native-cockpit-admin-control-center',
    title: 'Admin Kontroll- und Ueberwachungszentrum',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'tenant_id', label: 'Mandant' },
      { key: 'incident_id', label: 'Vorfall' },
      { key: 'source', label: 'Quelle' },
      { key: 'severity', label: 'Priorität' },
      { key: 'status', label: 'Status' },
      { key: 'title', label: 'Titel' },
      { key: 'owner', label: 'Verantwortlich' },
      { key: 'recommended_action', label: 'Empfehlung' },
      { key: 'scheduled_for', label: 'Geplant' },
      { key: 'plan_id', label: 'Plan' },
      { key: 'kind', label: 'Art' },
      { key: 'calendar_window', label: 'Kalender' },
      { key: 'open_quarantine_count', label: 'Quarantäne' },
      { key: 'journal_error_count', label: 'Journalfehler' },
    ],
    specializedLandmark: 'Admin Kontroll- und Ueberwachungszentrum Arbeitsbereich',
  },
  {
    label: 'admin/setup',
    path: '/admin/setup',
    screenId: 'admin/setup',
    testId: 'native-cockpit-admin-setup',
    title: 'Ersteinrichtung',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'step', label: 'Schritt' },
      { key: 'status', label: 'Status' },
    ],
    specializedLandmark: 'Ersteinrichtung Arbeitsbereich',
  },
  {
    label: 'studio/workspace-composition-preview',
    path: '/studio/workspace-composition-preview',
    screenId: 'studio/workspace-composition-preview',
    testId: 'native-cockpit-studio-workspace-composition-preview',
    title: 'WorkspaceComposition Studio',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'draft_id', label: 'Entwurf' },
      { key: 'status', label: 'Status' },
    ],
    specializedLandmark: 'WorkspaceComposition Studio Arbeitsbereich',
  },
  {
    label: 'admin/control-center/agent-ops',
    path: '/admin/control-center/agent-ops',
    screenId: 'admin/control-center/agent-ops',
    testId: 'native-cockpit-admin-control-center-agent-ops',
    title: 'Admin Kontrollzentrum: Agent Ops',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'persisted', label: 'Persistiert' },
      { key: 'history_count', label: 'Historie' },
      { key: 'state_path', label: 'State-Pfad' },
    ],
    specializedLandmark: 'Admin Kontrollzentrum: Agent Ops Arbeitsbereich',
  },
  {
    label: 'admin/control-center/superglue',
    path: '/admin/control-center/superglue',
    screenId: 'admin/control-center/superglue',
    testId: 'native-cockpit-admin-control-center-superglue',
    title: 'Admin Kontrollzentrum: Superglue',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'tenant_id', label: 'Mandant' },
      { key: 'storage_path', label: 'Storage' },
    ],
    specializedLandmark: 'Admin Kontrollzentrum: Superglue Arbeitsbereich',
  },
  // Prefixe, die vor Batch 41 an page-module-loader scheiterten
  {
    label: 'dms/archiv-suche',
    path: '/dms/archiv-suche',
    screenId: 'dms/archiv-suche',
    testId: 'dms-archiv-suche',
    title: 'Archiv-Suche',
  },
  {
    label: 'betrieb/maschinen-stamm',
    path: '/betrieb/maschinen-stamm',
    screenId: 'betrieb/maschinen-stamm',
    testId: 'betrieb-maschinen-stamm',
    title: 'Maschinen-Stamm',
  },
]

function maskPath(screenId: string): string {
  return screenId.replace(/\//g, '__')
}

function minimalCockpitDefinition(c: CockpitCase) {
  const contractFields = (c.specializedFields ?? []).map((field) => ({
    key: field.key,
    label: field.label,
    type: 'number' as const,
    readOnly: true,
  }))
  return {
    schemaVersion: 1,
    id: c.screenId,
    domain: c.screenId.split('/')[0],
    mode: 'cockpit',
    title: c.title,
    adapter: { type: 'native', sourceId: c.screenId, temporary: false },
    fields: [
      { key: 'label', label: 'Name', type: 'text', readOnly: true },
      { key: 'status', label: 'Status', type: 'text', readOnly: true },
      ...contractFields,
    ],
    dataSources: [
      ...(c.overviewEndpoint
        ? [{ key: 'entity', endpoint: c.overviewEndpoint }]
        : [{ key: 'entity', endpoint: `/api/v1/masks/${maskPath(c.screenId)}/overview` }]),
      ...(c.listEndpoint
        ? [{ key: 'items', endpoint: c.listEndpoint, pageSize: 50 }]
        : [{ key: 'items', endpoint: `/api/v1/masks/${maskPath(c.screenId)}/items`, pageSize: 50 }]),
    ],
    summary: [
      { key: 'gesamt', label: 'Gesamt', tone: 'neutral' },
    ],
    tables: [
      {
        key: 'items',
        label: 'Eintraege',
        dataSourceKey: 'items',
        pageSize: 50,
        columns: [
          { key: 'label', label: 'Name', priority: 'primary' },
          { key: 'status', label: 'Status', priority: 'primary' },
        ],
        rowActions: [],
      },
    ],
    actions: [
      {
        key: 'refresh',
        label: 'Aktualisieren',
        kind: 'secondary',
        zone: 'header',
        dangerLevel: 'safe',
        localEffect: 'refetch',
      },
    ],
    permissions: ['*'],
    layout: {
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      touchTargetPx: 44,
      floorplan: 'cockpit',
      density: 'compact',
      contextRail: 'combined',
      tableProfile: 'audit',
    },
    performance: {
      initialPayloadBudgetKb: 48,
      requiresLazyTabs: false,
      requiresVirtualTables: true,
      lookupMinChars: 2,
    },
    noWorkflowReason: 'Gate-D-Smoke ohne Beleg-Lebenszyklus.',
    ...(c.specializedType
      ? {
          specialized: {
            type: c.specializedType,
            id: c.screenId,
          },
        }
      : {}),
  }
}

async function installCockpitMocks(page: Page, c: CockpitCase): Promise<void> {
  const encoded = maskPath(c.screenId)
  const sd = minimalCockpitDefinition(c)

  await page.route(new RegExp(`/api/v1/masks/${encoded}/screen-definition$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(sd),
    })
  })

  const overviewPath = c.overviewEndpoint ?? `/api/v1/masks/${encoded}/overview`
  await page.route(new RegExp(`${overviewPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?:\\?.*)?$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ gesamt: 1, ok_count: 1, problem_count: 0 }),
    })
  })

  const listPath = c.listEndpoint ?? `/api/v1/masks/${encoded}/items`
  await page.route(new RegExp(`${listPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?:\\?.*)?$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 'smoke-1', label: c.title, status: 'ok' }]),
    })
  })

  // Overlay ohne Backend — leeres Overlay, kein Crash in der Runtime.
  await page.route(new RegExp(`/api/v1/ux/overlays/${c.screenId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`), async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: 'null' })
  })

  // Specialized-Surface-Fetches: Arrays (nicht {items}), sonst crasht z. B. Konditionen-Map.
  if (c.specializedType === 'pricing_workbench') {
    await page.route(/\/api\/v1\/price-lists\/?(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
  if (c.specializedType === 'lager_workbench') {
    await page.route(/\/api\/v1\/inventory\/warehouses(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })
  }
  if (c.specializedType === 'finance_workbench') {
    await page.route(/\/api\/v1\/banken\/konten(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })
    await page.route(/\/api\/v1\/finance\/bank-accounts(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      })
    })
    await page.route(/\/api\/v1\/finance\/mahnlauf\/candidates(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      })
    })
    await page.route(/\/api\/v1\/finance\/mahnlauf\/notices(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      })
    })
  }
  if (c.screenId === 'agrar/milchvieh-karte') {
    await page.route(/\/api\/v1\/agrar\/milchvieh-crosssell\/map(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ type: 'FeatureCollection', features: [] }),
      })
    })
  }
  if (c.screenId === 'agrar/kunden-schlagkartei') {
    // PortalKontoGate: ein Konto → Auto-Wahl → Tabs der Specialized-Surface.
    await page.route(/\/api\/v1\/portal\/kundenkonten(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            customer_id: 'smoke-kunde-1',
            customer_number: 'K-1',
            name: 'Smoke-Hof',
            rolle: 'betreiber',
            rechte: ['*'],
          },
        ]),
      })
    })
    await page.route(/\/(?:api\/v1\/)?innendienst\/kunden\/[^/]+\/schlaege(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ schlaege: [], count: 0 }),
      })
    })
    await page.route(/\/(?:api\/v1\/)?innendienst\/kunden\/[^/]+\/massnahmen(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ massnahmen: [], count: 0 }),
      })
    })
  }
  if (c.specializedType === 'feed_workbench') {
    await page.route(
      /\/api\/v1\/agrar\/rations-optimization\/feeding\/plans\/current(?:\?.*)?$/,
      async (route) => {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      },
    )
    await page.route(
      /\/api\/v1\/agrar\/rations-optimization\/lifecycle\/rations(?:\?.*)?$/,
      async (route) => {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      },
    )
    await page.route(
      /\/api\/v1\/agrar\/rations-optimization\/feeding\/actuals(?:\?.*)?$/,
      async (route) => {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      },
    )
  }
  if (c.specializedType === 'weighing') {
    await page.route(/\/api\/v1\/waage\/waagen(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
    await page.route(/\/api\/v1\/weighing-tickets(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
    await page.route(/\/api\/v1\/contracts(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
  if (c.specializedType === 'intake') {
    await page.route(/\/api\/v1\/annahme\/warteschlange(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })
    await page.route(/\/api\/v1\/articles(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      })
    })
  }
  if (c.screenId === 'annahme/abrechnung') {
    await page.route(/\/api\/v1\/agrar\/settlements(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
  if (c.specializedType === 'admin_workbench') {
    // Nur Voice-Stack-API — nicht Masken-URLs mit "voice" im Screen-Id abfangen.
    await page.route(/\/api\/v1\/voice\/(?:status|resolve|polish|summary|synthesize|pipeline|transcribe)(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ enabled: false, ready: false, last_utterance: null }),
      })
    })
  }
  if (c.screenId === 'admin/vordruck-editor') {
    await page.route(/\/api\/v1\/admin\/vordrucke(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
  if (c.screenId === 'admin/screen-studio') {
    await page.route(/\/api\/v1\/studio\/catalog(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ semantic: null, domains: [] }),
      })
    })
    await page.route(/\/api\/v1\/studio\/drafts(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ drafts: [] }),
      })
    })
    await page.route(/\/api\/v1\/studio\/validate$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          definitionReady: true,
          violations: [],
          readiness: { generatorReady: true, errors: [], warnings: [] },
        }),
      })
    })
  }
  if (c.screenId === 'admin/GapPipelineConsole') {
    await page.route(/\/api\/v1\/gap\/pipeline\/status(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          year: new Date().getFullYear() - 1,
          gap_payments_count: 0,
          snapshot_count: 0,
          customers_with_analytics_count: 0,
          pipeline_complete: false,
        }),
      })
    })
  }
  if (c.screenId === 'admin/setup/dms-integration' || c.screenId === 'admin/setup') {
    await page.route(/\/api\/v1\/admin\/dms\/status(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ ok: false, configured: false, message: 'offline' }),
      })
    })
  }
  if (
    c.screenId === 'admin/control-center'
    || c.screenId === 'admin/control-center/agent-ops'
    || c.screenId === 'admin/control-center/superglue'
    || c.screenId === 'admin/agenten-integration'
  ) {
    const tenantId = '00000000-0000-0000-0000-000000000001'
    await page.route(/\/api\/v1\/admin\/agent-manifest(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          version: '1',
          generated_at: new Date().toISOString(),
          auth: {},
          headers: [],
          links: [],
          examples: [],
          notes: [],
        }),
      })
    })
    await page.route(/\/api\/v1\/commands\/catalog(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
    if (c.screenId === 'admin/control-center') {
      await page.route(/\/api\/v1\/agents\/neuroassist\/ops\/planning(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tenant_id: tenantId,
            storage_path: 'runtime/planning.json',
            calendar_window: 'week',
            suggested_items: [],
            planned_items: [],
            summary: {
              heartbeat_count: 0,
              planned_item_count: 0,
              blocked_connector_count: 0,
            },
          }),
        })
      })
      await page.route(/\/api\/v1\/agents\/neuroassist\/ops\/incidents(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tenant_id: tenantId,
            incident_count: 0,
            open_quarantine_count: 0,
            blocked_connector_count: 0,
            stale_ticket_count: 0,
            review_ticket_count: 0,
            journal_error_count: 0,
            incidents: [],
          }),
        })
      })
    }
    if (c.screenId === 'admin/control-center/agent-ops') {
      await page.route(/\/api\/v1\/agents\/neuroassist\/ops\/persistence(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tenant_id: tenantId,
            state_path: 'runtime/agent-ops/state.json',
            history_path: 'runtime/agent-ops/history.jsonl',
            persisted: false,
            history_count: 0,
            recent_events: [],
            snapshot_counts: {},
          }),
        })
      })
    }
    if (c.screenId === 'admin/control-center/superglue') {
      await page.route(/\/api\/v1\/agent\/integrations\/providers\/superglue\/tenants\/default\/admin-state(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tenant_id: 'default',
            storage_path: 'runtime/superglue/admin-state.json',
            connector_overrides: {},
            policy_overrides: {},
            wizard: { current_step: 'credentials', completed_steps: [] },
          }),
        })
      })
      await page.route(/\/api\/v1\/agent\/integrations\/providers\/superglue\/tenants\/default\/wizard(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tenant_id: 'default',
            current_step: 'credentials',
            completed_steps: [],
            recommended_actions: [],
            steps: [],
          }),
        })
      })
    }
  }
}

async function applyTheme(page: Page, theme: 'light' | 'dark'): Promise<void> {
  await page.addInitScript((mode) => {
    try {
      window.localStorage.setItem('theme', mode)
    } catch {
      /* storage may be blocked in locked-down browsers */
    }
    const root = document.documentElement
    root.classList.toggle('dark', mode === 'dark')
    root.classList.toggle('light', mode === 'light')
  }, theme)
}

test.describe('Gate D — Studio Cockpit Browser Smoke (Made-by-Studio)', () => {
  test.beforeEach(async ({ page }) => {
    // UI-Testsitzung: unsigniertes Token nur fuer Render/Routing (kein Live-SSO / keine API-Rechte).
    await setzeUiTestsitzung(page)
  })

  for (const c of COCKPIT_CASES) {
    for (const theme of ['light', 'dark'] as const) {
      test(`${c.label} — native-cockpit Runtime, Titel sichtbar (${theme})`, async ({ page }) => {
        await applyTheme(page, theme)
        await installCockpitMocks(page, c)
        const response = await page.goto(c.path, { waitUntil: 'domcontentloaded' })
        expect(response?.status() ?? 200).toBeLessThan(400)

        await expect(page.locator('html')).toHaveClass(
          theme === 'dark' ? /(?:^|\s)dark(?:\s|$)/ : /(?:^|\s)light(?:\s|$)/,
        )

        // Cockpit-Shell und Renderer teilen oft denselben testId — Runtime-Attribut ist eindeutig.
        const root = page.locator(`[data-testid="${c.testId}"][data-runtime="native-cockpit"]`)
        await expect(root).toBeVisible({ timeout: 30_000 })
        await expect(page.getByRole('heading', { name: c.title }).first()).toBeVisible({
          timeout: 30_000,
        })

        if (c.specializedTablist) {
          await expect(page.getByRole('tablist', { name: c.specializedTablist })).toBeVisible({
            timeout: 30_000,
          })
        } else if (c.specializedLandmark) {
          await expect(page.getByRole('region', { name: c.specializedLandmark })).toBeVisible({
            timeout: 30_000,
          })
        } else if (c.specializedType === 'lager_workbench') {
          await expect(page.getByText('Hinweis Prototyp')).toBeVisible({ timeout: 30_000 })
        }

        await page.screenshot({
          path: `test-results/gate-d-${c.screenId.replace(/\//g, '_')}-${theme}.png`,
          fullPage: true,
        })
      })
    }
  }
})
