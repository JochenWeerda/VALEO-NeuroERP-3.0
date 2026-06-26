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
  "admin/agenten-integration": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/ai-approvals": { docPath: "agent-docs/guardrails", label: "AI-Freigaben", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/agent-docs/guardrails/" },
  "admin/externe-gates": { docPath: "admin/monitoring-und-slo", label: "Externe Gate-Dashboards", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/monitoring-und-slo/" },
  "admin/audit-log": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/benutzer": { docPath: "admin/rbac-und-rollen", label: "Benutzer & Rollen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/rbac-und-rollen/" },
  "admin/benutzer-liste": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/benutzer/:id": { docPath: "admin/rbac-und-rollen", label: "Benutzer & Rollen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/rbac-und-rollen/" },
  "admin/benutzer/neu": { docPath: "admin/rbac-und-rollen", label: "Benutzer & Rollen", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/rbac-und-rollen/" },
  "admin/command-monitor": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/compliance": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/compliance-dashboard": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/control-center": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/control-center/agent-ops": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/control-center/superglue": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/data-quality": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/gap-pipeline": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/GapPipelineConsole": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/integrationen-quarantaene": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/monitoring/alerts": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/monitoring/regeln": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/nummernkreise": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/report-berechtigungen": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/rolle/:id": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/rolle/neu": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/rollen-verwaltung": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/setup": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/setup/dms-integration": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/terminologie": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/voice-channel": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/webhooks": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "admin/webshop": { docPath: "admin/index", label: "Administration", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/admin/index/" },
  "agrar": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/aussaat": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/aussaat/:id": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/aussaat/liste": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/aussaat/neu": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/biostimulanzien": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/biostimulanzien-liste": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/biostimulanzien-stamm": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/biostimulanzien-stamm/:id": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/bodenprobe/:id": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/bodenprobe/neu": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/bodenproben": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/bodenproben/liste": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/duenger": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/duenger-liste": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/duenger-stamm": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/duenger-stamm/:id": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/duenger/bedarfsrechner": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
  "agrar/duenger/liste": { docPath: "benutzerhandbuch/annahme", label: "Agrar-Modul", url: "https://jochenweerda.github.io/VALEO-NeuroERP-3.0/benutzerhandbuch/annahme/" },
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
