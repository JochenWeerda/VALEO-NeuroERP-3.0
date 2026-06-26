// DOC-INAPP-HELP-002 — Route → Dokumentation Mapping
// Generiert via scripts/generate_inapp_help_map.py
// Stand: 2026-06-26
// Nicht manuell bearbeiten — aus route-inventory.gen.json + HELP_MAP generiert.

export interface HelpEntry {
  docPath: string;
  label: string;
  url: string;
}

/** Vollständige Docs-Basis-URL */
export const DOCS_BASE_URL = "https://jochenweerda.github.io/VALEO-NeuroERP-3.0";

/**
 * Mapping von Route-Pfad-Präfix → Hilfe-Seite.
 * Wird von useInAppHelp() verwendet um die passende Doku zur aktuellen Route zu finden.
 */
export const ROUTE_HELP_MAP: Record<string, HelpEntry> = {
  "export/umsatzsteuervoranmeldung": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "management/executive-dashboard": { docPath: "benutzerhandbuch/dashboard-workflows", label: "Dashboard und Workflows", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/" },
  "crm/vertreterprovisionen": { docPath: "benutzerhandbuch/vertreter-provisionen", label: "Vertreter und Provisionen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/vertreter-provisionen/" },
  "compliance/datenschutz": { docPath: "compliance/gdpr-checklist", label: "Datenschutz (DSGVO)", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/compliance/gdpr-checklist/" },
  "agrar/preisfixierung": { docPath: "benutzerhandbuch/agrar-kontrakte", label: "Agrar-Kontrakte", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-kontrakte/" },
  "agrar/pflanzenschutz": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "system/live-monitor": { docPath: "benutzerhandbuch/dashboard-workflows", label: "Dashboard und Workflows", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/" },
  "agrar/warteschlange": { docPath: "benutzerhandbuch/annahme", label: "Ernteannahme und Waage", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "inventory-dashboard": { docPath: "benutzerhandbuch/lager", label: "Lager und Bestände", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/lager/" },
  "admin/externe-gates": { docPath: "admin/monitoring-und-slo", label: "Externe Gate-Dashboards", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/monitoring-und-slo/" },
  "benachrichtigungen": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "agrar/ernteplanung": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/duengemittel": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "crm/vertreterstamm": { docPath: "benutzerhandbuch/vertreter-provisionen", label: "Vertreter und Provisionen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/vertreter-provisionen/" },
  "stammdaten/artikel": { docPath: "benutzerhandbuch/artikel-stammdaten", label: "Artikel und Stammdaten", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/artikel-stammdaten/" },
  "admin/ai-approvals": { docPath: "agent-docs/guardrails", label: "AI-Freigaben", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/agent-docs/guardrails/" },
  "inventory-reports": { docPath: "benutzerhandbuch/lager", label: "Lager und Bestände", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/lager/" },
  "agrar/settlement": { docPath: "benutzerhandbuch/agrar-kontrakte", label: "Agrar-Kontrakte", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-kontrakte/" },
  "agrar/bodenprobe": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/bestellung": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/naehrstoff": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "stock-management": { docPath: "benutzerhandbuch/lager", label: "Lager und Bestände", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/lager/" },
  "start-dashboard": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "errors/NotFound": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "agrar/kontrakte": { docPath: "benutzerhandbuch/agrar-kontrakte", label: "Agrar-Kontrakte", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-kontrakte/" },
  "agrar/fixierung": { docPath: "benutzerhandbuch/agrar-kontrakte", label: "Agrar-Kontrakte", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-kontrakte/" },
  "agrar/milchvieh": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/saatzucht": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "admin/mandanten": { docPath: "admin/mandanten-administration", label: "Mandanten-Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/mandanten-administration/" },
  "compliance/gobd": { docPath: "compliance/gobd-checklist", label: "GoBD-Prüfung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/compliance/gobd-checklist/" },
  "policy-manager": { docPath: "benutzerhandbuch/dashboard-workflows", label: "Dashboard und Workflows", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/" },
  "agrar/hofliste": { docPath: "benutzerhandbuch/annahme", label: "Ernteannahme und Waage", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/kontrakt": { docPath: "benutzerhandbuch/agrar-kontrakte", label: "Agrar-Kontrakte", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-kontrakte/" },
  "agrar/duengung": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/feldbuch": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/maschine": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "nachhaltigkeit": { docPath: "benutzerhandbuch/compliance-meldewesen", label: "Compliance und Meldewesen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/compliance-meldewesen/" },
  "kostenrechnung": { docPath: "benutzerhandbuch/controlling-kostenrechnung", label: "Controlling und Kostenrechnung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/controlling-kostenrechnung/" },
  "genossenschaft": { docPath: "benutzerhandbuch/genossenschaft", label: "Genossenschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/genossenschaft/" },
  "versicherungen": { docPath: "benutzerhandbuch/service-support", label: "Service und Support", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/service-support/" },
  "mobile/scanner": { docPath: "benutzerhandbuch/service-support", label: "Service und Support", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/service-support/" },
  "admin/benutzer": { docPath: "admin/rbac-und-rollen", label: "Benutzer & Rollen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/rbac-und-rollen/" },
  "einstellungen": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "public/verify": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "agrar/annahme": { docPath: "benutzerhandbuch/annahme", label: "Ernteannahme und Waage", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/saatgut": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/duenger": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/betrieb": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/flaeche": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "finanzplanung": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "agrar/partie": { docPath: "benutzerhandbuch/annahme", label: "Ernteannahme und Waage", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/wetter": { docPath: "benutzerhandbuch/annahme", label: "Ernteannahme und Waage", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "contracts-v2": { docPath: "benutzerhandbuch/agrar-kontrakte", label: "Agrar-Kontrakte", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-kontrakte/" },
  "agribusiness": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/futter": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/kultur": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "futtermittel": { docPath: "benutzerhandbuch/futtermittel-produktion", label: "Futtermittel und Produktion", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/futtermittel-produktion/" },
  "subventionen": { docPath: "benutzerhandbuch/compliance-meldewesen", label: "Compliance und Meldewesen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/compliance-meldewesen/" },
  "export/ustva": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "kostenstelle": { docPath: "benutzerhandbuch/controlling-kostenrechnung", label: "Controlling und Kostenrechnung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/controlling-kostenrechnung/" },
  "admin/module": { docPath: "admin/module-und-feature-flags", label: "Module & Feature-Flags", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/module-und-feature-flags/" },
  "setup/firma": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "agrar/waage": { docPath: "benutzerhandbuch/annahme", label: "Ernteannahme und Waage", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/lager": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/ernte": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/sorte": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "disposition": { docPath: "benutzerhandbuch/einkauf", label: "Einkauf und Beschaffung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einkauf/" },
  "prospecting": { docPath: "benutzerhandbuch/crm", label: "CRM und Marketing", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/crm/" },
  "kalkulation": { docPath: "benutzerhandbuch/preise-kalkulation", label: "Preise und Kalkulation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/preise-kalkulation/" },
  "mischfutter": { docPath: "benutzerhandbuch/futtermittel-produktion", label: "Futtermittel und Produktion", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/futtermittel-produktion/" },
  "zertifikate": { docPath: "benutzerhandbuch/compliance-meldewesen", label: "Compliance und Meldewesen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/compliance-meldewesen/" },
  "controlling": { docPath: "benutzerhandbuch/controlling-kostenrechnung", label: "Controlling und Kostenrechnung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/controlling-kostenrechnung/" },
  "schichtplan": { docPath: "benutzerhandbuch/personal-lohn", label: "Personal, Zeit und Lohn", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/personal-lohn/" },
  "admin-suite": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "dashboards": { docPath: "benutzerhandbuch/dashboard-workflows", label: "Dashboard und Workflows", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/" },
  "monitoring": { docPath: "benutzerhandbuch/dashboard-workflows", label: "Dashboard und Workflows", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/" },
  "agrar/silo": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "agrar/tier": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "stammdaten": { docPath: "benutzerhandbuch/artikel-stammdaten", label: "Artikel und Stammdaten", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/artikel-stammdaten/" },
  "produktion": { docPath: "benutzerhandbuch/futtermittel-produktion", label: "Futtermittel und Produktion", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/futtermittel-produktion/" },
  "compliance": { docPath: "benutzerhandbuch/compliance-meldewesen", label: "Compliance und Meldewesen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/compliance-meldewesen/" },
  "meldewesen": { docPath: "benutzerhandbuch/compliance-meldewesen", label: "Compliance und Meldewesen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/compliance-meldewesen/" },
  "foerderung": { docPath: "benutzerhandbuch/compliance-meldewesen", label: "Compliance und Meldewesen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/compliance-meldewesen/" },
  "transporte": { docPath: "benutzerhandbuch/logistik", label: "Logistik und Touren", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/logistik/" },
  "tankstelle": { docPath: "benutzerhandbuch/fuhrpark", label: "Fuhrpark", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/fuhrpark/" },
  "fibu-suite": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "auswertung": { docPath: "benutzerhandbuch/reports-analytics", label: "Reports und Analytics", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/reports-analytics/" },
  "workflows": { docPath: "benutzerhandbuch/dashboard-workflows", label: "Dashboard und Workflows", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/" },
  "dashboard": { docPath: "benutzerhandbuch/dashboard-workflows", label: "Dashboard und Workflows", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/" },
  "kontrakte": { docPath: "benutzerhandbuch/agrar-kontrakte", label: "Agrar-Kontrakte", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-kontrakte/" },
  "contracts": { docPath: "benutzerhandbuch/agrar-kontrakte", label: "Agrar-Kontrakte", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-kontrakte/" },
  "agrar/psm": { docPath: "benutzerhandbuch/agrar-warenwirtschaft", label: "Agrar-Warenwirtschaft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-warenwirtschaft/" },
  "marketing": { docPath: "benutzerhandbuch/crm", label: "CRM und Marketing", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/crm/" },
  "etiketten": { docPath: "benutzerhandbuch/artikel-stammdaten", label: "Artikel und Stammdaten", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/artikel-stammdaten/" },
  "inventory": { docPath: "benutzerhandbuch/lager", label: "Lager und Bestände", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/lager/" },
  "verladung": { docPath: "benutzerhandbuch/lager", label: "Lager und Bestände", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/lager/" },
  "qualitaet": { docPath: "benutzerhandbuch/qualitaetssicherung", label: "Qualitätssicherung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/qualitaetssicherung/" },
  "mahnwesen": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "dokumente": { docPath: "benutzerhandbuch/dokumente-belegarchiv", label: "Dokumente und Belegarchiv", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dokumente-belegarchiv/" },
  "analytics": { docPath: "benutzerhandbuch/reports-analytics", label: "Reports und Analytics", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/reports-analytics/" },
  "statistik": { docPath: "benutzerhandbuch/reports-analytics", label: "Reports und Analytics", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/reports-analytics/" },
  "workflow": { docPath: "benutzerhandbuch/dashboard-workflows", label: "Dashboard und Workflows", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/" },
  "policies": { docPath: "benutzerhandbuch/dashboard-workflows", label: "Dashboard und Workflows", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/" },
  "weighing": { docPath: "benutzerhandbuch/annahme", label: "Ernteannahme und Waage", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "vertrieb": { docPath: "benutzerhandbuch/verkauf", label: "Verkauf (Auftrag bis Rechnung)", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/verkauf/" },
  "lager/qs": { docPath: "benutzerhandbuch/qualitaetssicherung", label: "Qualitätssicherung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/qualitaetssicherung/" },
  "logistik": { docPath: "benutzerhandbuch/logistik", label: "Logistik und Touren", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/logistik/" },
  "fuhrpark": { docPath: "benutzerhandbuch/fuhrpark", label: "Fuhrpark", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/fuhrpark/" },
  "document": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "personal": { docPath: "benutzerhandbuch/personal-lohn", label: "Personal, Zeit und Lohn", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/personal-lohn/" },
  "projekte": { docPath: "benutzerhandbuch/service-support", label: "Service und Support", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/service-support/" },
  "schaeden": { docPath: "benutzerhandbuch/service-support", label: "Service und Support", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/service-support/" },
  "api-docs": { docPath: "schnittstellen/rest-api", label: "API-Dokumentation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/schnittstellen/rest-api/" },
  "copilot": { docPath: "benutzerhandbuch/dashboard-workflows", label: "Dashboard und Workflows", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dashboard-workflows/" },
  "annahme": { docPath: "benutzerhandbuch/annahme", label: "Ernteannahme und Waage", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "vertrag": { docPath: "benutzerhandbuch/agrar-kontrakte", label: "Agrar-Kontrakte", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/agrar-kontrakte/" },
  "verkauf": { docPath: "benutzerhandbuch/verkauf", label: "Verkauf (Auftrag bis Rechnung)", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/verkauf/" },
  "einkauf": { docPath: "benutzerhandbuch/einkauf", label: "Einkauf und Beschaffung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einkauf/" },
  "termine": { docPath: "benutzerhandbuch/crm", label: "CRM und Marketing", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/crm/" },
  "pricing": { docPath: "benutzerhandbuch/preise-kalkulation", label: "Preise und Kalkulation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/preise-kalkulation/" },
  "artikel": { docPath: "benutzerhandbuch/artikel-stammdaten", label: "Artikel und Stammdaten", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/artikel-stammdaten/" },
  "rezepte": { docPath: "benutzerhandbuch/futtermittel-produktion", label: "Futtermittel und Produktion", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/futtermittel-produktion/" },
  "strecke": { docPath: "benutzerhandbuch/strecke-handelsgeschaeft", label: "Streckengeschäft", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/strecke-handelsgeschaeft/" },
  "versand": { docPath: "benutzerhandbuch/logistik", label: "Logistik und Touren", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/logistik/" },
  "finance": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "payroll": { docPath: "benutzerhandbuch/personal-lohn", label: "Personal, Zeit und Lohn", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/personal-lohn/" },
  "docflow": { docPath: "benutzerhandbuch/dokumente-belegarchiv", label: "Dokumente und Belegarchiv", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dokumente-belegarchiv/" },
  "reports": { docPath: "benutzerhandbuch/reports-analytics", label: "Reports und Analytics", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/reports-analytics/" },
  "service": { docPath: "benutzerhandbuch/service-support", label: "Service und Support", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/service-support/" },
  "support": { docPath: "benutzerhandbuch/service-support", label: "Service und Support", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/service-support/" },
  "wartung": { docPath: "benutzerhandbuch/service-support", label: "Service und Support", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/service-support/" },
  "energie": { docPath: "benutzerhandbuch/service-support", label: "Service und Support", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/service-support/" },
  "alerts": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "verify": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "wissen": { docPath: "benutzerhandbuch/wissensbasis-kundenportal", label: "Wissensbasis und Kundenportal", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/wissensbasis-kundenportal/" },
  "portal": { docPath: "benutzerhandbuch/wissensbasis-kundenportal", label: "Wissensbasis und Kundenportal", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/wissensbasis-kundenportal/" },
  "preise": { docPath: "benutzerhandbuch/preise-kalkulation", label: "Preise und Kalkulation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/preise-kalkulation/" },
  "charge": { docPath: "benutzerhandbuch/artikel-stammdaten", label: "Artikel und Stammdaten", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/artikel-stammdaten/" },
  "futter": { docPath: "benutzerhandbuch/futtermittel-produktion", label: "Futtermittel und Produktion", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/futtermittel-produktion/" },
  "rezept": { docPath: "benutzerhandbuch/futtermittel-produktion", label: "Futtermittel und Produktion", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/futtermittel-produktion/" },
  "nawaro": { docPath: "benutzerhandbuch/nawaro", label: "NaWaRo", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/nawaro/" },
  "banken": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "elster": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "archiv": { docPath: "benutzerhandbuch/dokumente-belegarchiv", label: "Dokumente und Belegarchiv", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dokumente-belegarchiv/" },
  "ticket": { docPath: "benutzerhandbuch/service-support", label: "Service und Support", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/service-support/" },
  "hilfe": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "login": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "waage": { docPath: "benutzerhandbuch/annahme", label: "Ernteannahme und Waage", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "sales": { docPath: "benutzerhandbuch/verkauf", label: "Verkauf (Auftrag bis Rechnung)", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/verkauf/" },
  "inbox": { docPath: "benutzerhandbuch/einkauf", label: "Einkauf und Beschaffung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einkauf/" },
  "lager": { docPath: "benutzerhandbuch/lager", label: "Lager und Bestände", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/lager/" },
  "labor": { docPath: "benutzerhandbuch/qualitaetssicherung", label: "Qualitätssicherung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/qualitaetssicherung/" },
  "probe": { docPath: "benutzerhandbuch/qualitaetssicherung", label: "Qualitätssicherung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/qualitaetssicherung/" },
  "datev": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "ustva": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "atlas": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "kasse": { docPath: "benutzerhandbuch/pos-kasse", label: "POS und Kasse", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/pos-kasse/" },
  "beleg": { docPath: "benutzerhandbuch/dokumente-belegarchiv", label: "Dokumente und Belegarchiv", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dokumente-belegarchiv/" },
  "admin": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "auth": { docPath: "benutzerhandbuch/einstieg", label: "Einstieg und Navigation", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einstieg/" },
  "silo": { docPath: "benutzerhandbuch/lager", label: "Lager und Bestände", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/lager/" },
  "eudr": { docPath: "benutzerhandbuch/compliance-meldewesen", label: "Compliance und Meldewesen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/compliance-meldewesen/" },
  "epod": { docPath: "benutzerhandbuch/logistik", label: "Logistik und Touren", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/logistik/" },
  "fibu": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "bank": { docPath: "benutzerhandbuch/finanzbuchhaltung", label: "Finanzbuchhaltung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/finanzbuchhaltung/" },
  "lohn": { docPath: "benutzerhandbuch/personal-lohn", label: "Personal, Zeit und Lohn", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/personal-lohn/" },
  "zeit": { docPath: "benutzerhandbuch/personal-lohn", label: "Personal, Zeit und Lohn", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/personal-lohn/" },
  "rfq": { docPath: "benutzerhandbuch/einkauf", label: "Einkauf und Beschaffung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einkauf/" },
  "edi": { docPath: "benutzerhandbuch/einkauf", label: "Einkauf und Beschaffung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/einkauf/" },
  "crm": { docPath: "benutzerhandbuch/crm", label: "CRM und Marketing", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/crm/" },
  "esg": { docPath: "benutzerhandbuch/compliance-meldewesen", label: "Compliance und Meldewesen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/compliance-meldewesen/" },
  "bab": { docPath: "benutzerhandbuch/controlling-kostenrechnung", label: "Controlling und Kostenrechnung", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/controlling-kostenrechnung/" },
  "pos": { docPath: "benutzerhandbuch/pos-kasse", label: "POS und Kasse", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/pos-kasse/" },
  "tse": { docPath: "benutzerhandbuch/pos-kasse", label: "POS und Kasse", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/pos-kasse/" },
  "dms": { docPath: "benutzerhandbuch/dokumente-belegarchiv", label: "Dokumente und Belegarchiv", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/dokumente-belegarchiv/" },
  "hr": { docPath: "benutzerhandbuch/personal-lohn", label: "Personal, Zeit und Lohn", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/personal-lohn/" },
};

/**
 * Findet den passenden Hilfe-Eintrag für einen gegebenen Pfad.
 * Längster Präfix gewinnt.
 */
export function findHelpEntry(currentPath: string): HelpEntry | null {
  const normalised = currentPath.replace(/^\//, "").replace(/\/$/, "");
  // Längsten Präfix zuerst prüfen
  const entries = Object.entries(ROUTE_HELP_MAP).sort(
    ([a], [b]) => b.length - a.length
  );
  for (const [prefix, entry] of entries) {
    if (normalised === prefix || normalised.startsWith(prefix + "/")) {
      return entry;
    }
  }
  return null;
}

/** Route der eingebetteten Hilfeseite */
export const HELP_ROUTE = '/hilfe';

/** URL des Benutzerhandbuchs */
export const DOCS_USER_MANUAL_URL = `${DOCS_BASE_URL}/benutzerhandbuch/`;

/** Gibt die Hilfe-URL für einen gegebenen App-Pfad zurück. */
export function getEmbeddedHelpHref(currentPath: string): string {
  const entry = findHelpEntry(currentPath);
  return entry ? `${HELP_ROUTE}?ctx=${encodeURIComponent(entry.docPath)}` : HELP_ROUTE;
}

/** Löst einen doc-Pfad oder -Schlüssel zur vollständigen Hilfe-URL auf. */
export function resolveHelpUrl(docPath: string): string {
  return docPath.startsWith('http') ? docPath : `${DOCS_BASE_URL}/${docPath}`;
}

/** Öffnet eine Docs-URL im neuen Tab. */
export function openDocs(url: string): void {
  window.open(url, '_blank', 'noopener,noreferrer');
}
