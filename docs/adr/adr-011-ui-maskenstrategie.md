# ADR-011 UI-Maskenstrategie

**Status:** Accepted
**Date:** 2026-03-11

## Context
VALEO NeuroERP nutzt bereits generische Patterns, Builder-Ansätze und fachspezifische Seiten. Ohne klare Strategie drohen zwei Fehlentwicklungen: zu viel generische UI in fachlich komplexen Prozessen oder zu viele Einzellösungen trotz wiederkehrender Muster. Beides erhöht langfristig Kosten, Inkonsistenz und UX-Drift.

Das Zielbild verlangt deshalb eine explizite Regel, wann generische Mask-/Process-Builder Pflicht sind und wann fachliche Spezialmasken bewusst zulässig bleiben.

## Decision
VALEO NeuroERP führt eine verbindliche UI-Maskenstrategie mit drei Klassen ein.

Klasse A: Generische Standardmasken
- für strukturierte Objektseiten, einfache Listen, Standardformulare und Routine-Workflows
- bevorzugt auf Basis gemeinsamer Builder, Patterns und Felddefinitionen

Klasse B: Prozessmasken mit erweitertem Pattern-Rahmen
- für fachlich reichere Kernprozesse mit Commands, Freigaben, Explainability, Workflow-Status und Read-Models
- basieren auf gemeinsamen Prozesspatterns, dürfen aber prozessspezifische Kompositionen enthalten

Klasse C: Fachliche Spezialmasken
- nur für stark domänenspezifische Bedienlogik wie Waage, Ernteannahme, visuelle Disposition, Silo-/IoT- oder hochverdichtete Operator-UIs
- müssen ihre Abweichung vom generischen Standard explizit begründen

Verbindliche Grundsätze:
1. Neue Standardobjekte starten in Klasse A.
2. Abweichungen in Klasse B oder C müssen mit Prozesskomplexität, Interaktionsdichte oder Geräte-/Rollenlogik begründet werden.
3. Auch Spezialmasken binden auf Canonical Domain Model, Command-/Action-Layer und Workflow-/Policy-Kern.
4. Gemeinsame Patterns für Fehler, Freigabe, Explainability, Audit und Quick Actions bleiben verbindlich.
5. Builder und Spezialmasken dürfen keine konkurrierenden Fachmodelle etablieren.

### Erweiterung 2026-06-28: Universal Mask Generator

VALEO fuehrt einen langfristigen Universal Mask Generator als Zielarchitektur ein.
Der Generator ersetzt bestehende Masken nicht per Big Bang, sondern startet als
Skelett mit temporaerer Uebersetzungsschicht.

Verbindliche Schichten:

1. `ScreenDefinition` / `MaskSchema` beschreibt Fachstruktur, Datenquellen,
   Felder, Tabs, Tabellen, Aktionen, Rechte, Workflows, Audit und Dokumente.
2. Adapter uebersetzen bestehende `MaskConfig`, CRM-Mask-JSONs, Form-Schemas
   und Spezialmasken temporaer in diese neutrale Beschreibung.
3. Der Visualisierungslayer rendert die Beschreibung ueber gemeinsame Bausteine
   wie `UniversalMaskRenderer`, `LazyTabs`, `VirtualDataTable`, Lookup-, Workflow-,
   Audit- und Document-Renderer.
4. Direkte React-, CSS-, Tailwind- oder Pixelentscheidungen gehoeren nicht in das
   Schema.

Performance-Vertrag:

- Shell und kompakte Screen-Summary werden zuerst geladen.
- Tabs laden Details erst bei Aktivierung.
- Tabellen nutzen serverseitige Pagination/Filter/Sortierung und bei grossen
  Datenmengen Virtualisierung.
- Lookups laden keine vollstaendigen Stammdatenlisten, sondern suchen ab zwei
  Zeichen mit begrenztem Ergebnis.
- Mobile Darstellung wird als eigener Layoutmodus behandelt (`desktopDense`,
  `tabletTouch`, `mobileStack`) und nicht aus Desktop-Layouts abgeleitet.

Interferenzregeln:

- Der abgeschlossene UX-Baukasten-Rollout wird nicht neu gestartet.
- Spezialmasken wie Waage, POS, Ernteannahme und visuelle Disposition bleiben
  zulaessig, muessen aber Daten-, Action- und Workflow-Vertraege kompatibel
  halten.
- Alte Visualisierungen bleiben aktiv, bis eine Maske ueber Adapter-Paritaet,
  Performance und Tests als generatorfaehig nachgewiesen ist.
- Die Uebersetzungsschicht ist temporaer; sie wird je migrierter Maske entfernt,
  sobald direkte `ScreenDefinition`-Lieferung moeglich ist.

### Pilotregel 2026-06-28: CRM Customer Generator

Der erste produktive Generator-Pilot ist die CRM-Kundenmaske. Der Pilot ist
additiv und wird ueber `VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER=true` aktiviert.

Verbindliche Pilotregeln:

- Legacy bleibt Default und Fallback, solange der Feature Flag nicht aktiv ist.
- Die bestehende Customer `MaskConfig` wird ueber den temporaeren Adapter in
  `ScreenDefinition` uebersetzt; direkte Backend-ScreenDefinition ist noch nicht
  Pflicht.
- `screen-summary` muss vor der Customer-Detailquery geladen werden; Details
  werden erst nach erfolgreichem Summary-Vertrag aktiviert.
- Actions werden nur gerendert, wenn die zugehoerige Permission im
  Screen-Kontext vorhanden ist.
- Desktop und Mobile muessen per Unit- und Playwright-Smoke nachgewiesen sein,
  bevor weitere CRM-Masken in den Generator-Pilot aufgenommen werden.

### Nachzug 2026-06-25: Waves 27–30

- **Parity (27):** Lazy Tab-Listendaten ueber `tab_endpoints` und
  `GET /api/v1/crm/customers/{id}/tabs/{tab_key}`; Paritaetsmatrix in
  `docs/architecture/domains/crm/mask-parity-customer-360.md`.
- **Renderer-Lib (28):** Visualisierung unter `mask-builder/renderers/`; kein Verhaltenswechsel.
- **Data Contract (29):** `GET /api/v1/masks/{mask_id}/screen-definition` als native Quelle;
  Adapter bleibt Fallback fuer Feldinhalte.
- **Perf Gate (30):** `scripts/check_mask_performance_contract.ts` prueft
  `requires_lazy_tabs`, `lookup_min_chars >= 2`, `initial_payload_budget_kb`.

### Erweiterung 2026-06-28: RenderPlan Engine (Waves 33–40)

Der Universal Mask Generator darf MaskSchema nicht bei jedem Render neu interpretieren.
Stattdessen gilt:

1. `SchemaCompiler` uebersetzt `ScreenDefinition` + Summary/Auth-Kontext in einen
   flachen, immutable `RenderPlan`.
2. `RenderPlanCache` (LRU) keyed by `screenId`, `schemaVersion`, `tenant`, `role`,
   `permissions`, `featureFlags`.
3. `UniversalMaskRenderer` konsumiert den Plan ueber spezialisierte Fast-Renderer
   (kein generischer Meta-Renderer).
4. Bundle- und Render-Budgets werden in CI gemessen (`check_mask_bundle_budget.ts`,
   Playwright perf smoke).

Referenz: `docs/architecture/uix/render-plan-architecture.md`.

## Consequences
Positiv:
- Klarere Entscheidung zwischen Wiederverwendung und Spezial-UI
- Weniger Wildwuchs bei neuen Masken
- Bessere Balance zwischen Liefergeschwindigkeit und fachlicher UX-Qualität
- Langfristig eine gemeinsame Plattform fuer Desktop-, Tablet-, Mobile- und
  Print-/Sonderrenderer

Negativ:
- Mehr Architekturdisziplin vor UI-Implementierung
- Diskussionen über Klassifizierung neuer Seiten müssen explizit geführt werden
- Bestehende Mischformen müssen schrittweise eingeordnet und bereinigt werden
- Adapterpflege bleibt temporaere technische Schuld, bis genug Masken direkt auf
  `ScreenDefinition` liefern.

## References
- [Target State Landhandel ERP](../architecture/target-state-landhandel-erp.md)
- [ADR-003 Canonical Domain Model](adr-003-canonical-domain-model.md)
- [ADR-004 Command-/Action-Layer](adr-004-command-action-layer.md)
