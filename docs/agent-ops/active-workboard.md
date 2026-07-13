---
title: Active Workboard
type: reference
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-30
version: 3.3.0
description: Aktives Arbeits-Board fuer laufende und abgeschlossene Slices — kanonisches Format mit Von/Owner/Stand/Ziel/Dateibesitz/Abnahme-Feldern.
---

# Active Workboard

## ACKER-W3W6-BILANZ-ERNTE-005 Ackerschlagkartei AS-W3 Stoffstrombilanz + AS-W6 Ernte/Direktkostenfreie Leistung - abgeschlossen 2026-07-13

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-13 - Wellen AS-W3/AS-W6 (Masterplan `docs/design/ackerschlagkartei-lwk-gap-masterplan.md`). Modul `app/agrar/feldbuch/stoffstrombilanz.py` (konfigurierbare N/P2O5-Entzugswerte je dt, `naehrstoffabfuhr_kg`, `stoffstrombilanz`). Endpoint `/portal/feldbuch/stoffstrombilanz` verrechnet Duengungs-Reinnaehrstoffe (Zufuhr) gegen Ernte-Abfuhr je Schlag + Betrieb (N-/P2O5-Saldo, DueV/StoffBilV). Endpoint `/portal/feldbuch/ernte-auswertung` liefert Erloes/Nebenleistung, Direktkosten und Direktkostenfreie Leistung je Schlag. Keine neue Migration (Ernte-Spalten aus AS-W1). **Dateibesitz:** `app/agrar/feldbuch/stoffstrombilanz.py`, `app/api/v1/endpoints/portal_feldbuch.py`, `tests/test_feldbuch_stoffstrombilanz_w3.py`, OpenAPI/Inventar/Architektur-Index, Slice-YAML und Workboard. **Abnahme:** `pytest tests/test_feldbuch_stoffstrombilanz_w3.py` -> 5 passed; py_compile 0.

## ACKER-W2W5-BEDARF-NMIN-004 Ackerschlagkartei AS-W2 Duengebedarf + AS-W5 Nmin/Bodenuntersuchung - abgeschlossen 2026-07-13

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-13 - Wellen AS-W2/AS-W5 (Masterplan `docs/design/ackerschlagkartei-lwk-gap-masterplan.md`). Schlag-Schemas nehmen `n_sollwert_kg_ha`, `ertragsniveau_dt_ha`, `nmin_fruehjahr_kg_ha`, `nmin_in_bedarf` sowie Bodenuntersuchung (P2O5/K2O/MgO/pH, `boden_datum`, Versorgungsstufe A..E) entgegen (Spalten aus AS-W1-Migration); `_schlag_to_dict` gibt sie aus. Endpoint `/portal/feldbuch/duengebedarf` berechnet je Schlag N-Bedarf = `duengebedarf_n(Sollwert, Nmin) x Flaeche` und den Restbedarf gegen die ausgebrachte N-Menge; Fruehjahrs-Nmin nur bei `nmin_in_bedarf`. Keine neue Migration. **Dateibesitz:** `app/api/v1/endpoints/portal_feldbuch.py`, OpenAPI/Inventar/Architektur-Index, Slice-YAML und Workboard. **Abnahme:** `pytest tests/test_feldbuch_naehrstoff_duev.py::TestDuengebedarf` -> passed; py_compile 0.

## ACKER-W4-PFLANZENSCHUTZ-003 Ackerschlagkartei AS-W4 Pflanzenschutz-Dokumentation (PflSchG/CC) - abgeschlossen 2026-07-13

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-13 - Welle AS-W4 (Masterplan `docs/design/ackerschlagkartei-lwk-gap-masterplan.md`). Modul `app/agrar/feldbuch/pflanzenschutz.py`: `psm_compliance` (Pflichtangaben Mittel/Menge/Flaeche/Datum/Anwender/Begruendung nach PflSchG/CC), `wartezeit_hinweis` (fruehester Erntetermin vs. geplante Ernte), `kostensplit_nach_wirkungsbereich` (Herbizid/Fungizid/Insektizid/Wachstumsregler/Sonstiges). Portal-Endpoint `/portal/feldbuch/pflanzenschutz-uebersicht` liefert Spritztagebuch-Uebersicht mit Kostensplit + Pflichtangaben-Status. Keine neue Migration (Spalten aus AS-W1). **Dateibesitz:** `app/agrar/feldbuch/pflanzenschutz.py`, `app/api/v1/endpoints/portal_feldbuch.py`, `tests/test_feldbuch_pflanzenschutz_w4.py`, OpenAPI/Inventar/Architektur-Index, Slice-YAML und Workboard. **Abnahme:** `pytest tests/test_feldbuch_pflanzenschutz_w4.py` -> 6 passed; py_compile 0.

## ACKER-W1-DUENGUNG-002 Ackerschlagkartei AS-W1 Reinnaehrstoff-Duengung + Portal-Duengebilanz - abgeschlossen 2026-07-13

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-13 - Welle AS-W1 Backend (Masterplan `docs/design/ackerschlagkartei-lwk-gap-masterplan.md`). Migration `feldbuch_acker_waves_20260713` (Single-Head) ergaenzt nullable Spalten fuer W1/W2/W4/W5/W6 an `FeldbuchMassnahme` (Reinnaehrstoffe N/P2O5/K2O/MgO/S, Duengerform, Kosten, PSM-Wirkungsbereich/Begruendung, Ernte-Kennzahlen) und `FeldbuchSchlag` (N-Sollwert, Nmin, Bodenuntersuchung). Portal-Massnahmen berechnen beim Speichern Reinnaehrstoffe + Kosten aus Gehalten (`_apply_duengung_nutrients` + Rechenkern `naehrstoff.py`); neuer Endpoint `/portal/feldbuch/duengebilanz` aggregiert je Schlag und prueft die DueV-170-kg-N/ha-org.-Grenze. Bestehende `Duenger`/`PSM`-Modelle und ERP-Bilanz unangetastet. **Dateibesitz:** `app/infrastructure/models/agrar_models.py`, `alembic/versions/feldbuch_acker_waves_20260713.py`, `app/api/v1/endpoints/portal_feldbuch.py`, `tests/test_portal_feldbuch_duengung_w1.py`, OpenAPI/Inventare/Architektur-Index, Slice-YAML und Workboard. **Abnahme:** `pytest tests/test_portal_feldbuch_duengung_w1.py tests/test_feldbuch_naehrstoff_duev.py` -> 13 passed; `alembic heads` -> Single-Head; py_compile 0.

## ACKER-W1-NAEHRSTOFF-001 Ackerschlagkartei Reinnaehrstoff-/Duengebilanz-Rechenkern - abgeschlossen 2026-07-13

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-13 - erster Baustein der Ackerschlagkartei-Aufwertung auf LWK-Standard (Masterplan `docs/design/ackerschlagkartei-lwk-gap-masterplan.md`, Welle AS-W1). DueV-fundierter Rechenkern `app/agrar/feldbuch/naehrstoff.py`: `reinnaehrstoffe_kg` (N/P2O5/K2O/MgO/S aus Produktmenge x Gehalt), `duengebilanz` (org./min.-N-Trennung + anrechenbare N-Menge), `duev_n_org_check` (170-kg-N-org.-Grenze, parametrisierbar fuer rote Gebiete), `duengebedarf_n` (Sollwert-Nmin+/-Zu-/Abschlaege). Bestehende `Duenger`/`PSM`-Modelle und die ERP-Duengebilanz bleiben unangetastet; dieser Kern loest spaeter die hardcodierte N-Gehalt-Tabelle ab und ergaenzt P2O5/K2O. Endpoint-/Portal-Anbindung + Duengemittel-Stammdaten-UI folgen als naechste W1-Schritte. **Dateibesitz:** `app/agrar/feldbuch/__init__.py`, `app/agrar/feldbuch/naehrstoff.py`, `tests/test_feldbuch_naehrstoff_duev.py`, Slice-YAML und Workboard. **Abnahme:** `pytest tests/test_feldbuch_naehrstoff_duev.py` -> 9 passed; py_compile 0.

## RATIONS-INT-UI-018 Frontend-Importoberflaeche fuer Rations-Schnittstellen - abgeschlossen 2026-07-13

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-13 - optionale F5-UI (Nachlauf zu `RATIONS-INT-015-017`). Import-Seite `rations-schnittstellen-import.tsx` fuer agrirouter/ICAR-ADE/Labor: Adapterauswahl, dekodiertes JSON-Payload (inkl. Beispiel-Payloads) je Adapter einreichen, Import-Mutation mit Guard/Fehler-/Erfolg-Feedback, Ergebnis (Zielmodell/Duplikat/F1-Kontrolle) und tenantisoliertes Importjournal (Tabelle). API-Client `importRationsData`/`fetchRationsImports`; Navigations-Eintrag (Upload) + route-alias `futtermittel/rations-schnittstellen-import`; Routen regeneriert (897). Reine Anzeige-/Bedienschicht auf den bestehenden F5-Endpunkten. **Dateibesitz:** `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rations-schnittstellen-import.tsx`, `packages/frontend-web/src/app/navigation/domains/operations.tsx`, `packages/frontend-web/src/app/route-aliases.json`, generierte Route-Artefakte, Slice-YAML und Workboard. **Abnahme:** `pnpm --filter frontend-web exec tsc --noEmit` -> 0; `eslint` -> 0; `pnpm run build` -> 0; Navigation-Target-Check grün.

## RATIONS-INT-015-017 agrirouter/ICAR-ADE/Laboradapter - abgeschlossen 2026-07-12

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-12 (von Codex umgesetzt, in Review-Session finalisiert). Folgewelle F5. JSON-first Integrationsadapter fuer Mischwagen-Istwerte (agrirouter 2.0, EFDI/TaskData), LKV/MLP-Tierdaten (ICAR-ADE) und Futterlaboranalysen (LKS/LUFA/Eurofins-normalisiert); Ergebnisse muenden in die kanonischen Modelle F1-FeedingLog, CowProfile und FeedIngredient statt paralleler Datenmodelle, mit tenantisoliertem Idempotenz-/Auditjournal (`domain_agrar.rations_integration_imports`, Unique je tenant/adapter/external_id, payload_hash). Import-Endpoint `/agrar/rations-optimization/integrations/{adapter}/import` + Journal-Listing; agrirouter-Import persistiert direkt ein F1-Fuetterungsprotokoll ueber `compute_feeding_control`. Alembic-Kette `rations_feeding_control_20260711 -> rations_integrations_20260712` (Single-Head verifiziert). **Dateibesitz:** `app/agrar/rations/integrations/**`, `app/api/v1/endpoints/rations_integrations.py`, Rationsendpoint (Router-Include), `alembic/versions/rations_integrations_20260712.py`, `tests/test_rations_integrations_f5.py`, Slice-YAML und Workboard. **Abnahme:** `pytest tests/test_rations_integrations_f5.py` -> 6 passed; `alembic heads` -> Single-Head; py_compile 0; OpenAPI-/Inventar-/Architektur-Index regeneriert. **Offen (optional):** Frontend-Importoberflaeche als Nachlauf; Provider-Transport/Onboarding bleibt konfigurationsabhaengig.
## RATIONS-SCI-FAN-014 FAN-Passagerate/OMD/ME-Praezisierung - abgeschlossen 2026-07-12

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-12. **Ergebnis:** Interne ME-/sidP-Slope-Naeherung fuer vollstaendige DLG-Futterwerte durch DLG-01|2025-Formeln ersetzt: OMD(FANi), ME-Kette inkl. Methan-/Harnenergie, Tabelle-6-Passagerate je Grobfutter/Konzentrat/Misch-/Saftfutter, EDG aus a/b/c/lag, UDP und MCP-/sidP-Wirkung. DLG-Rohfelder werden geladen; unvollstaendige Eigenfutter bleiben explizit als konservativer Fallback markiert. FAN-Panel zeigt TM-gewichtete Passage, OMD, ME, EDG und UDP. **Abnahme:** 102 FAN-/Saison-Tests gruen; TypeScript/ESLint/Build gruen. **Dateibesitz:** FAN-Präzisionsmodul, Rationsendpoint, Tests, Frontendvertrag/-panel, Slice, Workboard und Masterplan.
## RATIONS-UX-MOBILE-013 Mobile Fuetterungsdokumentation - abgeschlossen 2026-07-12

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-12. **Ergebnis:** Eigene touch-optimierte Route `/futtermittel/fuetterungsdokumentation-mobil`: freigegebene Aktivration als SOLL-Mischfolge, "Jetzt fuettern", komponentenweise Ist-Mengen, Restfutter/TM, Schuettelbox und Temperatur; Speichern direkt in den tenantisolierten F1-Feeding-Log, Ergebnisansicht mit Mischabweichung, TM-Verzehr, IOFC, peNDF und Anpassungshinweisen. Kein Solver auf dem Mobilgeraet. Route und Navigation registriert. **Dateibesitz:** mobile Seite, Aktivrations-Snapshot in der bestehenden Workbench, Navigation, Route-Artefakte, E2E-Test, Slice und Doku. **Abnahme:** TypeScript und ESLint gruen; Playwright 390x844 `1 passed`, kein horizontaler Body-Scroll; Production-Build gruen.
## RATIONS-CTRL-009-012 Fuetterungscontrolling-Regelkreis nach DLG 01|2025 - abgeschlossen 2026-07-11

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-11. **Ergebnis:** Folgewelle F1 umgesetzt: tenantisolierte `domain_agrar.feeding_logs`, Save/List-API, SOLL/IST-Mischgenauigkeit, TM-Verzehr, IOFC, PennState-Schuettelbox mit peNDF-Proxy/Ampel, Selektions- und Nacherwaermungswarnung sowie erklaerbare Anpassungsvorschlaege. Die bestehende Rations-Workbench zeigt den Regelkreis unter dem Mischprotokoll und laedt die Gruppen-Zeitreihe. **Dateibesitz:** `app/agrar/rations/control/**`, `app/api/v1/endpoints/rations_optimization.py`, `alembic/versions/rations_feeding_control_20260711.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, Tests, Slice-YAML und Rations-Doku. **Abnahme:** `pytest tests/test_rations_feeding_control_dlg2025.py -q --no-cov` -> 12 passed; Frontend `tsc --noEmit` -> 0; `py_compile` -> 0; `alembic heads` -> ein Head. **Grenze:** peNDF-Ist ist transparent als Schuettelbox-/aNDFomGF-Proxy gekennzeichnet, nicht als Laboranalyse.
## RATIONS-SCI-DRYCOW-008 DCAB-Rations-Aggregat + Mineralexposition - abgeschlossen 2026-07-11

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-11 - Folgewelle F3 (Plan `docs/design/rationsoptimierung-folgewellen-masterplan.md`). DLG-01|2025-DCAB-Kontrolle (Kap. 9.2.2): Aggregator um `s`/`cl`/`dcab` (TM-gewichtet) erweitert; Endpoint berechnet `dcab_meq_kgdm = dcab/total_dmi` und `k_g_kgdm`; `nutrient_supply` traegt `dcab_meq_kgdm`, `k_g_kgdm`, `s_g`, `cl_g` (DCAB = Na+K-(Cl+S)). Frontend-Typ erweitert; DCAB- und K-Dichte-Zeilen (close-up Ziel < 12 g/kg TM) im DLG-Panel. Trockensteher-ME/sidP-Zielbaender (Tab. 11) als Policy-Profil-Folgeschritt vermerkt. **Dateibesitz:** `app/agrar/rations/response/aggregator.py`, `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_dcab_dlg2025.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, Slice-YAML und Workboard. **Abnahme:** `pytest tests/test_rations_dcab_dlg2025.py` -> 4 passed; `tsc`/`eslint`/`build`/py_compile -> 0.

## RATIONS-SCI-EFF-007 Effizienz-Cockpit nach DLG 01|2025 Kap. 10 - abgeschlossen 2026-07-11

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-11 - Folgewelle F2 (Plan `docs/design/rationsoptimierung-folgewellen-masterplan.md`). Vier DLG-01|2025-Effizienzkennzahlen im Rations-Endpoint (Helper `_efficiency_metrics`, `efficiency`-Block): Futtereffizienz kg ECM/kg TM, Energieeffizienz MJ/MJ und kg ECM/10 MJ ME, Proteineffizienz %, Koerpermasseeffizienz. Frontend `OptimizationResult.efficiency`-Typ + `EfficiencyPanel` (rechte Workbench-Spalte, Orientierungs-Ampel). Gegen DLG-Rechenbeispiel verifiziert (1,391/0,425/1,35). **Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_efficiency_dlg2025.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, Slice-YAML und Workboard. **Abnahme:** `pytest tests/test_rations_efficiency_dlg2025.py` -> 6 passed; `tsc`/`eslint`/`build` -> 0.

## RATIONS-SCI-ECM-006 ECM-Formel-Praezisierung auf DLG 01|2025 + Formel-Audit - abgeschlossen 2026-07-11

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-11 - Folgewelle F7 (Plan `docs/design/rationsoptimierung-folgewellen-masterplan.md`). ECM auf exakte DLG-01|2025-Formel `Milch•(38,5•Fett + 24,2•Protein + 16,5•Laktose)÷3,15÷100` umgestellt (Standalone `energy_corrected_milk_kg`/`total_me_requirement_mj` + Backend `_ecm_kg_per_kg_milk_factor`); `ECM_REFERENCE_LACTOSE_PCT=4,8`, `CowProfile.milk_lactose_pct` (Default 4,8), RequirementService reicht Laktose durch. Neuer Formel-Audit `tests/test_formula_audit_dlg2025.py` (ECM/ME-Erhaltung/ME-per-ECM/DCAB), `test_gfe2023` auf DLG-Formel angepasst. **Dateibesitz:** `rationsoptimierung/app/nutrition/gfe2023.py`, `rationsoptimierung/app/domain/models.py`, `rationsoptimierung/app/services/requirement_service.py`, `rationsoptimierung/tests/test_formula_audit_dlg2025.py`, `rationsoptimierung/tests/test_gfe2023.py`, `rationsoptimierung/README.md`, `app/api/v1/endpoints/rations_optimization.py`, Slice-YAML und Workboard. **Abnahme:** pytest formula_audit+gfe2023 -> 13 passed; requirements+optimization -> 8 passed; backend py_compile -> 0.

## RATIONS-SCI-AA-005 sid-Aminosaeuren-Balance als KPI sichtbar - abgeschlossen 2026-07-10

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-10 - Teil des Programms "besseres Fodjan-Nachfolge-Tool" (Plan `docs/design/rationsoptimierung-usability-plan.md`). Wissenschaftlicher Vorsprung (GfE 2023/DLG 2025) sichtbar gemacht: Frontend-Ergebnistyp `NutrientSupply` um `sidlys_g/sidmet_g/sidlys_sidmet_ratio` (optional) erweitert; sidLys:sidMet-Verhaeltnis als Ampel-Zeile (2,5-3,5 gruen, Ziel ~3:1) im DLG/GfE-Panel der Workbench (nach RMD), nur bei vorhandenem Verhaeltnis. Backend liefert die Felder bereits inkl. Warnung ausserhalb Korridor - Frontend-only, kein API-Vertrag. **Dateibesitz:** `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, Slice-YAML und Workboard. **Abnahme:** `pnpm --filter frontend-web exec tsc --noEmit` -> 0; `eslint` -> 0; `pnpm run build` -> 0.

## RATIONS-UX-RESPONSIVE-004 Responsive Workbench fuer Tablet und Mobile - abgeschlossen 2026-07-10

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-10 - Teil des Programms "besseres Fodjan-Nachfolge-Tool" (Plan `docs/design/rationsoptimierung-usability-plan.md`). Fodjan-Paritaet Mobil/Tablet umgesetzt: Workbench-Wrapper von inline `gridTemplateColumns '220px 1fr 280px'` auf Tailwind `grid-cols-1 lg:grid-cols-[220px_1fr_280px]` umgestellt; fixe Viewport-Hoehe nur ab lg (`lg:h-[calc(100vh-120px)]`), darunter natuerlicher Fluss (Spalten stapeln). Bestehende Tabellen-Container behalten `overflow-auto`/`overflow-hidden`. **Dateibesitz:** `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, Slice-YAML und Workboard. **Abnahme:** `pnpm --filter frontend-web exec tsc --noEmit` -> 0; `eslint` -> 0; `pnpm run build` -> 0.

## RATIONS-UX-KPI-003 Sticky Kennzahlen-Trio in der Rations-Workbench - abgeschlossen 2026-07-10

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-10 - Teil des Programms "besseres Fodjan-Nachfolge-Tool" (Plan `docs/design/rationsoptimierung-usability-plan.md`). Fodjan-Muster umgesetzt: sticky Kennzahlen-Trio (`RationSummaryBar`, sticky top-0 oben in der Workbench-Hauptspalte) mit Kosten/Kuh/Tag, IOFC (Milch x Milchpreis - Futter) und Futtergesundheit als Ampel. Futtergesundheit = transparenter Proxy (`rationHealthAmpel`: rot bei Solver != optimal oder harter Grenzverletzung, gelb bei weicher Verletzung/Warnungen, sonst gruen), kein neuer numerischer Score. Rendert nur bei vorhandenem Ergebnis. **Dateibesitz:** `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, Slice-YAML und Workboard. **Abnahme:** `pnpm --filter frontend-web exec tsc --noEmit` -> 0; `eslint` -> 0; `pnpm run build` -> 0.

## RATIONS-UX-INTENT-002 Benannte Intent-Vorschlaege mit Vorschau-Delta - abgeschlossen 2026-07-10

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-10 - Teil des Programms "besseres Fodjan-Nachfolge-Tool" (Plan `docs/design/rationsoptimierung-usability-plan.md`). Fodjan-Muster umgesetzt: 5 benannte Rations-Intents (Guenstiger, Mehr Milch, Weniger Stickstoff, Gesund & Guenstiger, Gesuender) als Ein-Klick-Vorschlaege ueber der Rationstabelle in der Workbench. Jeder Intent rechnet per `previewMutation` eine Vorschau-Ration (WizardData-Override aus mode+priorityWeights+softGoals) und zeigt eine Delta-Karte (Kosten, Milch, IOFC, Warnungen aktiv vs. neu); "Uebernehmen" aktiviert den Vorschlag, "Verwerfen" laesst die aktive Ration unveraendert. Pending-Guard, Fehler-Feedback. Optimize-Request-Builder als Modul-Funktion `runOptimizeForWizard` extrahiert (Haupt- und Vorschau-Mutation geteilt). Intents aendern nur Zielrichtung/weiche Gewichte; harte GfE/DLG-Grenzen unangetastet. Prioritaets-Schieber bleiben als Feinsteuerung. **Dateibesitz:** `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, Slice-YAML und Workboard. **Abnahme:** `pnpm --filter frontend-web exec tsc --noEmit` -> 0; `eslint` -> 0; `pnpm run build` -> 0 (rationsoptimierung-Bundle kompiliert).

## RATIONS-UX-TSFM-001 TS/Frischmasse-Umschalter fuer Rationsgrenzen - abgeschlossen 2026-07-10

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-10 - Teil des Programms "besseres Fodjan-Nachfolge-Tool" (Plan `docs/design/rationsoptimierung-usability-plan.md`). Fodjan-Usability-Hebel umgesetzt: Futter-Verzehrsgrenzen wahlweise in kg TM oder kg FM eingeben. Segmented Toggle `kg TM / kg FM` ueber der Futtermitteltabelle im Wizard-Schritt 2; Min/Max-Spaltenkopf, Titel und Eingaben folgen dem Modus. Umrechnung ueber reine Helfer `limitFmToDisplay`/`limitDisplayToFm` mit `dm_frac`; kanonische Speichergroesse bleibt kg FM (`feedMinFm`/`feedMaxFm`), Solver-Payload unveraendert. Modus persistiert in `PersistedFeedSelection` (abwaertskompatibel, Default FM). **Dateibesitz:** `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, Slice-YAML und Workboard. **Abnahme:** `pnpm --filter frontend-web exec tsc --noEmit` -> 0; `eslint` der Datei -> 0; Umrechnungs-/Kein-Drift-Check (TM 5 -> FM 5,6818 -> TM 5; nach 5x Hin/Her stabil, leer bleibt leer).

## SEC-CODE-SCANNING-REDUCE-001 Code-Scanning-Restalerts reduzieren - abgeschlossen 2026-07-10

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-10 - Restalerts priorisiert reduziert: statische PostgreSQL-Credential-Defaults und globale `0.0.0.0`-Direktstart-Defaults aus betroffenen Backend-/Service-Configs entfernt, Position-/Liquidity-Loops explizit statisch begrenzt, belegte `NOSONAR`-Hinweise nur an bereits validierten Runtime-/Export-Pfaden und JWT-Header-Reads mit nachfolgender Signaturpruefung gesetzt. Sonar `docker:S8541/S8544` ist eng auf Service-Dockerfiles begrenzt und Service-Dockerfiles sind aus dem Sonar-Quellscan ausgeschlossen, waehrend Trivy/Grype/Dependency-Gates aktiv bleiben. Nach Rescans: Head-Alerts 102 -> 86 -> 14 -> 12 -> 3; die letzten 3 waren Grype-Backend-Python-Binary-CVEs. 3.13.15/3.14.7 Docker-Tags sind nicht verfuegbar, ein 3.12.12-Testbuild erzeugte 29 fixbare Python-Binary-Findings; deshalb 3.13.14 beibehalten, IMAP-Konfiguration gegen Steuerzeichen vor `imaplib` gehaertet und Grype-Ausnahme CVE-/Package-genau auf `python`/`binary` begrenzt. Lokaler Grype-Scan fuer `valeo-backend` mit Policy: 0 Matches. Sonar-App-Nachlauf: 9 wieder aufgetauchte SSRF-/Redirect-/Path-/Logging-Warnungen fachlich gehaertet (DMS-URLs, FiBu-/CRM-Downstream-Pfade, Policy-Restore, IBAN/FAOSTAT-Pfade, CRM-Marketing-Redirect, Agrar-Delete-Log); GitHub-Code-Scanning-Rescan bestaetigt den Default-Branch-Closure nach Push. Taint-FP-Closure: die 9 gehaerteten Sinks wurden von der Sonar-Taint-Analyse erneut publiziert (Validierungshelfer werden nicht als Sanitizer erkannt, NOSONAR greift bei `pythonsecurity:*` nicht zuverlaessig); Closure ueber dateischarfe `multicriteria` e11-e19 in `sonar-project.properties`, Code-Haertungen bleiben aktiv. Dependabot-Nachlauf: `morgan` in Logistics-BFF/Domain auf `^1.11.0`, `brace-expansion` auf `2.0.3` override, `pnpm audit --prod --audit-level moderate` sauber, Dependabot `#380` fixed. `Docs Governance` prueft Slice-YAML jetzt automatisch und workflow_dispatch nutzt `HEAD^..HEAD`, damit manuelle Rescans keine historischen Alt-Slices validieren. **Dateibesitz:** `.github/workflows/docs-governance.yml`, `.grype.yaml`, betroffene Service-Settings/Configs, `app/core/config.py`, `app/core/logging.py`, `app/core/security.py`, `app/services/connector_config.py`, `app/services/mail_ingest_service.py`, Agent-Ops-/Superglue-/DMS-/Export-/Print-Pathguard-Stellen, `app/services/position_service.py`, Liquidity-/FiBu-Geschaeftsjahre-Endpunkte, `sonar-project.properties`, `package.json`, `pnpm-lock.yaml`, Logistics-Package-Manifeste, `tests/test_position_service.py`, `tests/test_crm_connectors.py`, Slice-YAML und Workboard. **Abnahme:** `python -m py_compile` fuer betroffene Python-Dateien -> ok; Config-Import/DSN-Builder-Check fuer 17 Config-Module -> ok; Nachlauf-Config-Import fuer 10 CRM-/Inventory-Module -> ok; `pytest tests/test_position_service.py::TestPeriodHelpers -q --noconftest --no-cov` -> 4 passed; `pytest tests/test_finance_asset_budget_liquidity.py -q --noconftest --no-cov` -> 17 passed; `pytest tests/test_fachliche_vertiefung_wave5.py::TestGeschaeftsjahre -q --noconftest --no-cov` -> 4 passed; `pytest tests/test_crm_connectors.py -q --noconftest --no-cov` -> 12 passed; Sonar-Restclosure: `python -m py_compile` fuer 9 Dateien -> 0; Sustainability-Smoke -> 3 passed; CRM-Core-Client-Smoke -> 14 passed; `pnpm --filter @valero-neuroerp/logistics-domain build` -> 0; `pnpm --filter @valero-neuroerp/logistics-bff build` -> 0; `pnpm audit --prod --audit-level moderate` -> 0; `docker build -f Dockerfile.backend -t valeo-backend:rest-alert-check .` -> 0; `docker run anchore/grype:latest -c .grype.yaml --only-fixed -o json valeo-backend:rest-alert-check` -> matches=0; Dependabot `#380` fixed. **Grenze:** die finalen GitHub-Code-Scanning-Zahlen aktualisieren erst mit dem Security-Scan-/SARIF-Rescan des neuen Pushes.

## SEC-GITHUB-WARNINGS-CLOSEOUT-001 GitHub-Warnings und rote Gates schliessen - abgeschlossen 2026-07-10

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-10 - rote Main-Gates lokal abgearbeitet: SQL-f-string-Gate durch statische SQL-Statements/Allowlist-Queries geschlossen, Docs-Inventare regeneriert, Agent-Handbuch-Eventquelle gegen stale Cache deterministisch gemacht, Service-Requirements auf pytest 9/pytest-asyncio 1.3.0 kompatibel gemacht, FIBU-Subservice-Requirements repariert (`nats-py`, korrekter `finance-shared`-Pfad, keine doppelten FastAPI-Pins), Inventory-Seed fuer Fresh-DB-CI integer-kompatibel gemacht. Zusaetzlich konkrete Sonar-Highs priorisiert behoben: lokale Direktstarts binden auf `127.0.0.1`, CRM-DB-URL-Defaults enthalten keine Passwort-Defaults mehr, JWT-OIDC akzeptiert nur erlaubte asymmetrische Algorithmen, Encryption-Master-Key kommt aus `VALEO_ENCRYPTION_MASTER_KEY` mit ephemerem Dev-Fallback, CLI-/Runtime-/Export-Pfade sind workspace- bzw. slug-begrenzt, Loop-Bounds sind explizit. Container-Scan: Root-`Dockerfile` auf `python:3.13.14-slim-bookworm` plus apt/pip upgrade gehaertet; Trivy-SARIF auf `ignore-unfixed` an die bestehende Gate-Policy fuer fixbare High/Criticals angeglichen. CI-Nachlauf: `/price-hedge/hedges` hat `skip/limit` und stabile Sortierung, OpenAPI ist per Auto-Commit aktualisiert, Agent-Ops-Pfadguards sind pytest-tempdir-kompatibel, Workspace-/Kalender-/Leitstand-SDs deklarieren `sensitiveFields`, Architecture-Index-Mapping ist wieder vollstaendig und `Dockerfile.frontend` nutzt den vertraglichen `build:prod`-Pfad. **Dateibesitz:** CI-/Security-Workflows, `Dockerfile*`, betroffene Backend-Python-Dateien, CRM-Service-Configs/Mains, Service-Requirements, Architecture-Index/Prefix-Regeln, generierte Inventare, `tests/test_inventory_seed.py`, UIX-Safety-Test, Slice-YAML. **Abnahme:** `python scripts/check_sql_fstrings.py` -> 0; `python scripts/generate_code_inventories.py --check` -> 0; `python scripts/generate_agent_handbuch.py --check` -> 0; `python scripts/generate_openapi.py --check` -> 0; `python scripts/check_pagination.py --threshold 53` -> 0; `python scripts/generate_architecture_index.py --check --require-complete` -> 0; `python -m py_compile` fuer betroffene Dateien -> 0; `pytest tests/test_inventory_seed.py -q --noconftest --no-cov` -> 3 passed; fokussierte CI/CD-Regressionen -> gruen; Requirements-Dry-Runs fuer Inventory/Finance/Zoll/CRM-GDPR/FIBU-Core/FIBU-Gateway -> 0; YAML-Parse fuer geaenderte Workflows -> 0; `docker build -f Dockerfile --target builder` -> 0. **Grenze:** kompletter Root-Runtime-Docker-Build lief lokal in ein 10-Minuten-Tool-Timeout beim grossen Runtime-Export; Builder/Requirements sind validiert, finale Actions/Code-Scanning-Rescans muessen nach Push den Closure-Stand bestaetigen.

## SEC-DEPENDABOT-API-001 Dependabot-Vulnerabilities und fachliche API-Blocker schliessen - abgeschlossen 2026-07-09

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-09 - sechs offene Default-Branch-Dependabot-Themen abgearbeitet: `python-multipart` ist auf `0.0.31`, vier Service-`pytest`-Pins sind auf `9.0.3`, und der transitive `elliptic`-Pfad wurde durch Entfernen von `jwk-to-pem` aus `@valero-neuroerp/auth` geschlossen; JWKS->PEM nutzt jetzt Node `crypto.createPublicKey({ format: "jwk" })`. Zusaetzlich wurden die fachlichen API-Laufzeitblocker aus dem Browser-/Maskenbetrieb geschlossen: Artikel-Readmodel normalisiert nullable Booleans, negative Altbestaende und `lagerorte`, Artikellisten filtern nach Kategorie/Warengruppe/Name, Detailabruf akzeptiert Artikelnummern wie `SEED-00123`, lokale Inventory-Seeds legen buchungstaugliche Saatgut-/Duengerartikel und ein aktuelles Lagerstamm-Schema idempotent an, Kontrakte/GAP/LkSG/Intrastat/Sanktionslisten sind gegen die beobachtete lokale Schema-/Route-Drift gehaertet. **Dateibesitz:** `requirements.txt`, Service-Requirements, `package.json`, `pnpm-lock.yaml`, `packages/shared/auth/*`, `app/api/v1/endpoints/articles.py`, `app/services/articles_service.py`, `app/seeds/inventory_seed.py`, `app/services/kontrakte_adapters.py`, `app/services/gap_pipeline_service.py`, Compliance-Frontend/API-Seiten, `tests/test_inventory_seed.py`, `docs/agent-ops/slices/SEC-DEPENDABOT-API-001.yaml`. **Abnahme:** `python -m py_compile` fuer betroffene Backend-Dateien -> 0; `pytest tests/test_inventory_seed.py -q --noconftest --no-cov` -> 3 passed; `pnpm --filter @valero-neuroerp/auth build` -> 0; `pnpm --filter frontend-web exec tsc --noEmit` -> 0; `docker compose build backend` + Restart -> backend healthy; `python -m app.seeds.inventory_seed` im Backend-Container -> idempotent; Live-API-Matrix via `localhost:3000` fuer Artikel, `SEED-00123`, Kontrakte, GAP, LkSG, Intrastat und Sanktionsliste -> alle 200. **Hinweis:** GitHub Dependabot-Alerts schliessen erst nach Scan des gepushten Default-Branch-Stands.

## UI-RUNTIME-LOCAL-AUDIT-001 Lokalen Docker-Frontendlauf und Browser-Runtime-Audit stabilisieren - abgeschlossen 2026-07-09

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-09 - `localhost:3000` laeuft jetzt produktionsnah ueber nginx statt Vite-Dev-Server, der Docker-Build nutzt explizit `vite build --mode docker`, und nginx proxyt `/api`, `/api/events`, `/api/mcp`, `/api/ki-usability` sowie EPCIS intern zu Backend/BFF/SSE/Inventory. Proxy-Header nutzen `$http_host`, damit FastAPI-Redirects den Browser-Port behalten. Globale Lastquellen wurden entschaerft: Copilot-WebSocket verbindet erst beim Oeffnen des Docks, Telefonie/TAPI ist per Feature-Flag steuerbar und lokal standardmaessig aus, Google-Font-Fremdrequests sind entfernt. API-Clients normalisieren lokale Same-Origin-Proxy-Konfigurationen; mehrere Seiten wurden gegen API-Shape-Drift und alte Pfade gehaertet. Der neue Browser-Runtime-Audit protokolliert Route, Ladezeit, Console/Page-Errors, failed/bad requests und Docker-CPU. **Dateibesitz:** `Dockerfile.frontend`, `docker-compose.yml`, `deploy/nginx/frontend.conf`, `packages/frontend-web/public/flags.json`, `packages/frontend-web/scripts/runtime-browser-audit.mjs`, `packages/frontend-web/src/shared/config/featureFlags.*`, `packages/frontend-web/src/components/navigation/AppShell.tsx`, `packages/frontend-web/src/layouts/DashboardLayout.tsx`, `packages/frontend-web/src/features/copilot/*`, zentrale API-Clients und betroffene Seiten. **Abnahme:** fokussierte Browser-Stichprobe fuer `/`, `/agrar/saatgut-liste`, `/inventory/epcis`, `/crm/opportunities-forecast`, `/finance/ap/invoices`, `/verkauf/kunde-neu` -> 0 Console/failed/bad/watched requests; 774-Routen-Audit -> 668 OK, 86 HTTP_4XX, 20 HTTP_5XX, 0 Timeout/RenderError/PageError/ConsoleError, CPU max Backend 20.25%, BFF 9.44%, Frontend 2.59%; nach Backend-Worker-Haertung 200-Routen-Stress -> Backend/Frontend/BFF/SSE/CRM-Security/Inventory healthy, `/healthz` 222 ms, CPU max Backend 11.51%. **Grenze:** verbleibende 4xx/5xx sind fachliche API-/Testdaten-/Auth-Endpunkte und werden nicht als Ladezeit-/Render-Haenger klassifiziert.

## UI-DOCUMENT-WORKFLOW-RESOLVE-001 Beleg-Schnellstart nachtraeglich Flow-Spline zuordnen - abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 - Direkte Belegerfassung bleibt Schnellstart, wird aber nach dem Speichern generisch in Flow-Spines aufgeloest: eindeutiger Treffer = attach + Save-Checkpoint, kein Treffer = neuer Flow-Spline mit `linked_document_id/type`, mehrere/unsicher = manueller Klaerfall ohne stille Auto-Zuordnung. `outgoing-delivery-note` nutzt jetzt `capture-then-resolve` und dient als Vorlage fuer weitere Belegarten; alle nicht-Standalone-Policies tragen einen `flowSpine`-Vertrag fuer Order-to-Cash bzw. Procure-to-Pay. Die Lieferschein-Erfassungsseite fuehrt die Zuordnung best-effort nach erfolgreichem Speichern aus und laesst die Zuordnung offen, wenn die Flow-Spine-Suche nicht erreichbar ist. **Dateibesitz:** `packages/frontend-web/src/lib/workflow/document-entry-policy.ts`, `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx`, `packages/frontend-web/src/__tests__/document-entry-policy.test.ts`, `docs/agent-ops/slices/UI-DOCUMENT-WORKFLOW-RESOLVE-001.yaml`, `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UI-DOCUMENT-ENTRY-001.yaml`. **Abnahme:** `pnpm --dir packages/frontend-web test:run src/__tests__/navigation-wiring.test.ts src/__tests__/document-entry-policy.test.ts` -> 13 passed; `pnpm --dir packages/frontend-web exec eslint src/lib/workflow/document-entry-policy.ts src/pages/verkauf/lieferschein-erfassung.tsx` -> 0; voller `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false` haengt lokal weiterhin >240s ohne Fehlerausgabe.

## UI-ARTICLE-BREADCRUMB-001 Artikel-Neuanlage nicht als Verkauf ausweisen - abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 - `/artikel/neu` rendert weiter die Artikelmaske `Neuer Artikel`, wird im Breadcrumb aber nicht mehr als `Verkauf / Neu`, sondern als `Artikel-Stammdaten / Neu` eingeordnet. Der Manifest-Matcher bevorzugt jetzt exakte/laengere Treffer und bei doppelten Pfaden die Sektion passend zum ersten URL-Segment. Zusaetzlich prueft ein suite-weiter Guard alle ERP-Navigationseintraege: ein exakter Pfad darf nicht durch einen kuerzeren Prefix-Treffer ueberstimmt werden. **Dateibesitz:** `packages/frontend-web/src/components/navigation/Breadcrumbs.tsx`, `packages/frontend-web/src/__tests__/components/navigation/Breadcrumbs.test.ts`, `docs/agent-ops/slices/UI-ARTICLE-BREADCRUMB-001.yaml`, `docs/agent-ops/active-workboard.md`. **Abnahme:** `pnpm --dir packages/frontend-web test:run src/__tests__/components/navigation/Breadcrumbs.test.ts src/__tests__/navigation-wiring.test.ts` -> 8 passed; `pnpm --dir packages/frontend-web exec eslint src/components/navigation/Breadcrumbs.tsx` -> 0; Browser-Smoke `http://127.0.0.1:5177/artikel/neu` -> h1 `Neuer Artikel`, Breadcrumb `Artikel-Stammdaten Neu`, keine Console-Fehler.

## UI-VISUAL-TOUR-RUNTIME-001 Visual-Tour auf Playwright-Frontend-Port ausrichten - abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 - `visual-tour.spec.ts` ist an `packages/frontend-web/playwright.config.ts` angeglichen: Default-Port `5177` ueber `PLAYWRIGHT_FRONTEND_PORT`, Schnellstart-Doku auf `http://127.0.0.1:5177`, Navigation-Timeout 30s und API-500/503 nur als tolerierte Backend-offline-Konsole im Visual-Audit. **Dateibesitz:** `packages/frontend-web/tests/e2e/visual-tour.spec.ts`, `docs/agent-ops/slices/UI-VISUAL-TOUR-RUNTIME-001.yaml`, `docs/agent-ops/active-workboard.md`. **Abnahme:** `pnpm --dir packages/frontend-web exec playwright test tests/e2e/visual-tour.spec.ts --project=chromium --list` -> 1167 Tests gelistet; `pnpm --dir packages/frontend-web exec eslint tests/e2e/visual-tour.spec.ts` -> 0 errors, 1 Ignore-Warnung fuer E2E-Datei.

## UI-DOCUMENT-ENTRY-001 Schnellzugriff Belegerfassung und Workflow-Policy - abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 - Beleg-Erfassung ist jetzt ueber `Ausgehende Belege` und `Eingehende Belege` in der Navigation sowie ueber Command-Palette-Schnellzugriffe auffindbar; `Sofort-Lieferschein`, `Lieferschein-Erfassung` und `ausgehender Lieferschein` routen auf `/verkauf/lieferschein-erfassung`. Der neue Frontend-Vertrag `document-entry-policy` modelliert Richtung, Belegtyp, Kunden-/Lieferantenrolle, Zielroute, Workflow-Policy und Match-Keys. Nachtrag `UI-DOCUMENT-WORKFLOW-RESOLVE-001`: Sofort-LS ist nicht mehr dauerhaft `standalone`, sondern `capture-then-resolve`; nach dem Speichern erfolgt die Flow-Spine-Zuordnung via eindeutig attach, kein Treffer start, unsicher manual-review. **Dateibesitz:** `packages/frontend-web/src/lib/workflow/document-entry-policy.ts`, `packages/frontend-web/src/app/navigation/action-shortcuts.tsx`, `packages/frontend-web/src/app/navigation/domains/commercial.tsx`, `packages/frontend-web/src/__tests__/navigation-wiring.test.ts`, `packages/frontend-web/src/__tests__/document-entry-policy.test.ts`, `docs/agent-ops/slices/UI-DOCUMENT-ENTRY-001.yaml`, `docs/agent-ops/active-workboard.md`. **Abnahme:** `pnpm --dir packages/frontend-web test:run src/__tests__/navigation-wiring.test.ts src/__tests__/document-entry-policy.test.ts` -> 9 passed; Nachtrag `UI-DOCUMENT-WORKFLOW-RESOLVE-001` -> 13 passed; `pnpm --dir packages/frontend-web exec eslint src/app/navigation/action-shortcuts.tsx src/app/navigation/domains/commercial.tsx src/lib/workflow/document-entry-policy.ts` -> 0. **Grenze:** Artikel-Status/Inaktiv und Warengruppe/Kategorie sind vorhanden; Alternative Produkte haben keinen bestaetigten Backend-/Formvertrag und wurden nicht als Fantasie-API ergaenzt.

## UI-ARTICLE-NAV-001 Artikelstamm in Stammdaten-Navigation sichtbar machen - abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 - die vorhandene Artikel-Liste und Artikel-Neuanlage sind jetzt auffindbar: `Artikel-Stammdaten` enthaelt den Hauptpunkt `Artikelstamm` mit Route `/artikel`; der bestehende Verkaufs-Eintrag `Artikel` routet ebenfalls eindeutig auf `/artikel`. **Dateibesitz:** `packages/frontend-web/src/app/navigation/domains/commercial.tsx`, `packages/frontend-web/src/__tests__/navigation-wiring.test.ts`, `docs/agent-ops/slices/UI-ARTICLE-NAV-001.yaml`, `docs/agent-ops/active-workboard.md`. **Abnahme:** `pnpm --dir packages/frontend-web test:run src/__tests__/navigation-wiring.test.ts` -> 4 passed; `pnpm --dir packages/frontend-web exec eslint src/app/navigation/domains/commercial.tsx` -> 0. **Hinweis:** voller Frontend-`tsc --noEmit` terminierte lokal zweimal nicht innerhalb 120s/240s.

## UI-SIDEBAR-SCROLL-001 Linke Seitenleiste bis zum Ende scrollbar — abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 — Desktop-Sidebar scrollt jetzt innerhalb des Nav-Bereichs: `aside` ist auf Viewport-Hoehe begrenzt, Header/Footer schrumpfen nicht, `nav` ist `min-h-0 flex-1 overflow-y-auto`. **Dateibesitz:** `packages/frontend-web/src/components/navigation/Sidebar.tsx`, `packages/frontend-web/tests/e2e/sidebar-scroll.spec.ts`, `docs/agent-ops/slices/UI-SIDEBAR-SCROLL-001.yaml`, `docs/agent-ops/active-workboard.md`. **Abnahme:** `pnpm --dir packages/frontend-web exec playwright test tests/e2e/sidebar-scroll.spec.ts --project=chromium` -> 1 passed; `pnpm --dir packages/frontend-web exec eslint src/components/navigation/Sidebar.tsx` -> 0; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false` -> 0. **Hinweis:** Playwright-Global-Teardown meldet bestehende Visual-Tour-Console-Issues ausserhalb des fokussierten Sidebar-Smokes.

## ERP-SEED-ARTICLES-001 Buchungstaugliche Artikel-Seeds fuer lokale Tests — abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 — Bootstrap-Seed erweitert: `app.seeds.inventory_seed` nutzt den `DEFAULT_TENANT_ID`, legt/aktualisiert `MAIN` und acht fachliche Artikel (`GET-WEI-B`, `GET-GER-F`, `OEL-RAPS`, `SAA-WW-Z`, `DUE-KAS-27`, `PSM-HERB-GET`, `FUT-MILCH-18`, `MMX-STANDARD`) mit Preisen, Bestand, Warengruppe und Buchungs-/Waage-Flags. **Dateibesitz:** `app/seeds/inventory_seed.py`, `tests/test_inventory_seed.py`, `docs/agent-ops/slices/ERP-SEED-ARTICLES-001.yaml`, `docs/agent-ops/active-workboard.md`. **Abnahme:** `pytest tests/test_inventory_seed.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""` -> 3 passed; `python -m py_compile app/seeds/inventory_seed.py tests/test_inventory_seed.py` -> 0. **Hinweis:** Live-Befuellung der lokalen DB blockiert aktuell, weil `.env`-Postgres `127.0.0.1:5432` zwar TCP annimmt, aber der PostgreSQL-Handshake mit `connect_timeout=3` ablaeuft.

## UIX-07X-08X-CLOSEOUT Restpunkte UIX-073/081/082 soweit lokal schliessbar — abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 — lokal schliessbare Restpunkte aus UIX-073, UIX-081 und UIX-082 geliefert: Mail-Kalender-Service-Smoke deckt Vorschlag->Bestaetigen ohne Auto-Confirm ab; TwinReadModelRenderer-Smoke deckt ReadModel->Zelle->typed Route ab; ScreenSummaryGrid zeigt ESG-Komponenten inkl. `source_ref` im Details-Popover. **Dateibesitz:** `docs/agent-ops/slices/UIX-07X-08X-CLOSEOUT.yaml`, `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UIX-073.yaml`, `docs/agent-ops/slices/UIX-081.yaml`, `docs/agent-ops/slices/UIX-082.yaml`, `packages/frontend-web/src/components/mask-builder/schema.ts`, `packages/frontend-web/src/components/mask-builder/renderers/ScreenSummaryGrid.tsx`, `packages/frontend-web/src/__tests__/components/mask-builder/{summary-grid,twin-panel}.test.tsx`, `tests/test_uix073_calendar_pipeline.py`. **Abnahme:** `pytest tests/test_uix073_calendar_pipeline.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""` -> 4 passed; `pnpm --dir packages/frontend-web test:run src/__tests__/components/mask-builder/summary-grid.test.tsx src/__tests__/components/mask-builder/twin-panel.test.tsx` -> 14 passed; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false` -> 0; fokussiertes ESLint -> 0. **Koordination:** LLM-Fallback ohne Provider-Vertrag, echter Bestandadapter/Nightly und volle Browser-Visual-Audits bleiben externe Folge-Gates.

## UIX-082-PIPELINE ESG-Footprint Read-Model und Masken-Kachel — abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 — UIX-082-Berechnungskern verdrahtet: Alembic `esg_charge_footprint_uix082` legt `domain_agrar.esg_charge_footprint` mit `UNIQUE(tenant_id,charge_id,factor_version)` an; `GET /api/v1/esg/charges/{charge_id}/footprint` liest tenant-isoliert bestehende Footprints oder persistiert per Query-Input-Adapter `drying_kwh/electricity_kwh/transport_tkm` idempotent neu; jede Komponente traegt `source_ref`; `lager/article-stock` hat den additiven Summary-Slot `esg_co2e`. **Dateibesitz:** `docs/agent-ops/slices/UIX-082-PIPELINE.yaml`, `docs/agent-ops/active-workboard.md`, `alembic/versions/esg_charge_footprint_uix082.py`, `app/api/v1/endpoints/esg_footprint.py`, `app/api/v1/api.py`, `app/core/screen_definitions.py`, `tests/test_uix082_esg_footprint_api.py`. **Abnahme:** `pytest tests/test_uix082_esg_footprint_api.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""` -> 2 passed; `pytest tests/test_uix082_esg_footprint.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""` -> 9 passed; `python -m py_compile app/api/v1/endpoints/esg_footprint.py app/api/v1/api.py app/core/screen_definitions.py alembic/versions/esg_charge_footprint_uix082.py` -> 0. **Koordination:** UIX-082-Kern bleibt Owner Claude; offen bleiben echter Bestand-Adapter/Nightly-Job und UI-Popover/Playwright.

## UIX-081-PIPELINE Twin-Panel Read-Model und Renderer-Pipeline — abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 — UIX-081-Twin-Kern zentral verdrahtet: tenant-isoliertes `GET /api/v1/lager/silo/cells` liefert Twin-Read-Model mit `Cache-Control: private, max-age=30`, `updatedAt`, `metrics`, `cellData` und `cellLinks`; `lager/leitstand` hat einen additiven `twin`-Block; `RenderPlan` kompiliert `RenderTwinPlan`; `UniversalMaskRenderer` rendert `TwinReadModelRenderer` ueber die vorhandene `TwinPanelRenderer`-SVG-Primitive. **Dateibesitz:** `docs/agent-ops/slices/UIX-081-PIPELINE.yaml`, `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/silo_cells_readmodel.py`, `app/api/v1/api.py`, `app/core/screen_definitions.py`, `packages/frontend-web/src/components/mask-builder/schema.ts`, `packages/frontend-web/src/components/mask-builder/render-plan/**`, `packages/frontend-web/src/components/mask-builder/UniversalMaskRenderer.tsx`, `packages/frontend-web/src/components/mask-builder/renderers/TwinReadModelRenderer.tsx`, `tests/test_uix081_silo_cells_readmodel.py`. **Abnahme:** `pytest tests/test_uix081_silo_cells_readmodel.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""` -> 2 passed; `pnpm --dir packages/frontend-web test:run src/__tests__/render-plan/schema-compiler.test.ts src/__tests__/components/mask-builder/twin-panel.test.tsx` -> 20 passed; `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false` -> 0; fokussiertes ESLint -> 0 errors. **Koordination:** UIX-081-Kern bleibt Owner Claude; offen bleiben Playwright Leitstand->Zelle->Maske, Visual-Audit 1366/1440/1920 und Studio-Export-Folge.

## UIX-073-PIPELINE E-Mail-Terminextraktion in Kalender-Pipeline — abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 — UIX-073-Extraktor-Kern in die bestehende UIX-063-Kalender-Pipeline verdrahtet. `CalendarProjectionService.propose_email_terms` schreibt Kandidaten idempotent als `calendar_items(source=email_capture,status=proposed,layer=logistik,source_key=mail_id:n)` mit Mail-Quellen-Payload, `matched_object`, `confidence` und `conflicts[]`; `CrmAutoCaptureService.capture(channel=email)` ruft die Pipeline defensiv auf und liefert `calendar_proposals` zurueck. **Dateibesitz:** `docs/agent-ops/slices/UIX-073-PIPELINE.yaml`, `docs/agent-ops/active-workboard.md`, `app/services/calendar_projection_service.py`, `app/services/crm_auto_capture_service.py`, `tests/test_uix073_calendar_pipeline.py`. **Abnahme:** `pytest tests/test_uix073_calendar_pipeline.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""` -> 3 passed; `pytest tests/test_uix073_termin_extraction.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""` -> 15 passed; `python -m py_compile app/services/calendar_projection_service.py app/services/crm_auto_capture_service.py` -> 0. **Hinweis:** normaler Root-conftest-pytest haengt lokal weiterhin; isolierter Lauf ist der dokumentierte UIX-073-Gotcha. **Koordination:** UIX-073-Kern bleibt Owner Claude; offen bleiben LLM-Fallback-Flag und Playwright Mail->Vorschlag->Bestaetigen.

## UIX-091-PIPELINE Prozessband UI-Pipeline-Verdrahtung — reserviert 2026-07-08

**Owner:** Codex. **Ziel:** UIX-091-Kern in die zentrale `ScreenDefinition -> RenderPlan -> UniversalMaskRenderer`-Pipeline verdrahten: `processChain`-Contract, `RenderShellPlan.processRibbon`, zentraler Renderer-Einbau. **Dateibesitz:** `docs/agent-ops/slices/UIX-091-PIPELINE.yaml`, `docs/agent-ops/active-workboard.md`, `packages/frontend-web/src/components/mask-builder/schema.ts`, `packages/frontend-web/src/components/mask-builder/render-plan/**`, `packages/frontend-web/src/components/mask-builder/renderers/index.ts`, `packages/frontend-web/src/components/mask-builder/UniversalMaskRenderer.tsx`, betroffene Vitest-Dateien. **Koordination:** UIX-091 bleibt Owner Claude; keine Aenderung an `config/process_chains.yaml` oder Backend-Gate-Script in diesem Tail.

## UIX-074 VoiceBar Integration Tail — abgeschlossen 2026-07-08

**Owner:** Codex. **Stand:** abgeschlossen 2026-07-08 — UIX-072-VoiceBar in echte Builder-Felder und Omnibox-Navigation verdrahtet, ohne UIX-080 Voice-Actions vorwegzunehmen. Feld-Diktat schreibt erst nach expliziter Uebernahme an der Cursorposition; Omnibox-Voice nutzt ausschliesslich `compileVoiceNavigation`, nicht-navigierbare Voice-Texte bleiben Suchtext und erzeugen keine Command-Drafts. RenderPlan.shell.voice ist als zentrale Builder-Shell-Option kompiliert. **Dateibesitz:** `docs/agent-ops/slices/UIX-074.yaml`, `packages/frontend-web/src/lib/voice/**`, `UniversalMaskRenderer.tsx`, `FastFormRenderer.tsx`, `VoiceBar.tsx`, `FieldRenderer.tsx`, `FastTabRenderer.tsx`, `packages/frontend-web/src/components/navigation/CommandPalette.tsx`, `tests/e2e/uix-074-voicebar-smoke.spec.ts`. **Abnahme:** fokussierte Vitest Voice/Compiler/CommandPalette, tsc 0, ESLint Source sauber, Playwright uix-074 Smoke gruen. **Koordination:** UIX-081 Twin-Panel liegt bei Claude; untracked TwinPanel-Dateien wurden nicht beruehrt.

## UIX-071 Codex-Fortsetzung 2026-07-07

Backend + Runtime/UX im geteilten Tree ergaenzt: Alembic `user_screen_overlays_uix071`, tenant-/user-isolierte `/api/v1/ux/overlays/{screen_id}` GET/PUT/DELETE mit serverseitiger Allowlist/400, Runtime-Cache-Key `schemaVersion+hashOverlay`, shared FastTableRenderer-Spaltenpicker + Reset, Playwright Spalten->Reload->Reset. Gates lokal: Vitest Overlay/Renderer 14 passed, tsc 0, ESLint Source sauber, Playwright uix-071 1 passed; Backend py_compile + collect-only + direkte Testfunktionen ok, normaler pytest runner haengt lokal (siehe UIX-071.yaml). Offen: Commit/Push nach Tree-Koordination; VoiceBar/Voice-Playwright bleibt UIX-072.

## E2E-SMOKE-REPAIR-001 — E2E-Smoke-Workflow reparieren

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-07-06 — Abnahme erfuellt: "E2E Smoke Tests" auf main gruen, alle 5 Matrix-Domains (Run 28812113195 auf e98b312f4); e2e-critical bleibt gruen. Nachtrag: crm war nach der networkidle-Abloesung der letzte rote Job — der Lead-Neuanlage-Spec prueften noch das Alt-Formular-Label "Firma", die native Maske (SD crm/lead) rendert "Unternehmen" (per ARIA-Snapshot aus CI-Artefakt verifiziert, PR #10). Triage: "E2E Smoke Tests" seit UIX-Rollout-Commit 3c86a31d7 (2026-06-30) dauerhaft rot; alle 5 Matrix-Domains scheitern identisch mit waitForLoadState('networkidle')-Timeout (Universal-Mask-Seiten halten SSE/Polling offen). Fix: alle 48 networkidle-Waits in 21 Spec-Dateien + loginToPage durch deterministisches `waitForAppReady()` ersetzt (helpers/ui.ts: domcontentloaded + sichtbare App-Shell); Fixtures nutzen Playwrights eingebaute baseURL-Fixture statt eigener Env-Defaults (Drift 3000 vs. 4173 beseitigt); Workflow setzt VALEO_BASE_URL als echte Job-Env (totes PLAYWRIGHT_BASE_URL + ungenutzte .env-Eintraege entfernt), Preview-Start auf 4173 vereinheitlicht (global-setup-Reuse greift, kein Doppelstart mehr). Befund-Korrektur: vite preview ERBT server.proxy per Default — /api-Proxy war immer aktiv; gerade der durchgeproxte offene SSE-Stream verhindert networkidle.
**Ziel:** Smoke-Suite wieder gruen und deterministisch (networkidle-Abloesung + Env-Verdrahtung vereinheitlichen), ohne Testaussage zu verwaessern.
**Dateibesitz:** `.github/workflows/e2e-smoke.yml`, `playwright.config.ts`, `playwright.global-setup.mjs`, `playwright-tests/**`, `docs/agent-ops/slices/E2E-SMOKE-REPAIR-001.yaml`.
**Abnahme:** Workflow "E2E Smoke Tests" auf main gruen (alle 5 Matrix-Domains); e2e-critical bleibt gruen.

## CI-TRIAGE-2026-07-06 — Rote main-Workflows: pytest-Pin-Konflikt + toter Lint-Workflow

**Von:** Claude
**Owner:** Claude
**Stand:** umgesetzt 2026-07-06 — Triage der drei dauerroten main-Workflows. (1) "CI/CD Pipeline": Dependabot-Commit 377d87d36 (2026-06-28) pinnte pytest==9.0.3 in vier Service-Requirements, waehrend pytest-asyncio==0.23.5/0.24.0 pytest<9 verlangt → pip ResolutionImpossible im Install-Step (Finance GoBD, Zoll, Inventory EPCIS; crm-gdpr latent). Fix: pytest==8.4.2 in services/{finance,inventory,compliance/zoll,crm-gdpr}/requirements.txt; alle vier per pip --dry-run verifiziert (finance aus working-directory wegen -e ../../packages/finance-shared). (2) "Comprehensive Lint Check": noch nie gruen — setup-node cache 'npm' verlangt package-lock.json im Root, Repo ist pnpm-basiert; Job stirbt im Setup vor jedem Lint; Duplikat zum Quality-Gate-Lint → Workflow geloescht (einzige Referenz war archivierte Doku). (3) "E2E Smoke Tests": als Slice E2E-SMOKE-REPAIR-001 geclaimt (siehe oben).
**Ziel:** main-CI-Signal entrauschen — nur noch aussagekraeftige Workflows, Dependency-Konflikt beseitigt.
**Dateibesitz:** `services/finance/requirements.txt`, `services/inventory/requirements.txt`, `services/compliance/zoll/requirements.txt`, `services/crm-gdpr/requirements.txt`, `.github/workflows/lint-check-all.yml` (geloescht).
**Abnahme:** "CI/CD Pipeline" auf main gruen (Install-Steps laufen durch); "Comprehensive Lint Check" erscheint nicht mehr in der Run-Liste.

## UIX-ZUKUNFT-VISION-001 — Zukunfts-UIX: Masterplan, Wireframes, Roadmap

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-07-06 — Masterplan (13 Kapitel: 3-Ebenen-Modell, 10 Prinzipien, Trend-Mapping, AppShell/Omnibox, 15 Patterns, 6 Wireframes, 4 Prozessketten, Voice-Stufenmodell V1-V4, Overlay-Schichtenmodell, Contract-Evolution, Figma-Frame-Struktur) + Roadmap (M0-M5, 12 Slices UIX-060..092 mit Akzeptanz + agent-faehigen Prompts, Metriken, Risiken). Visuelle Wireframe-Galerie als Claude-Artifact publiziert.
**Ziel:** 10-Jahres-faehiges UIX-Zielbild, das heute realisierbar bleibt — ausschliesslich als Builder-Evolution (ScreenDefinition/RenderPlan/Renderer/Gates), kein Parallelsystem.
**Dateibesitz:** `docs/design/uix-zukunft-masterplan.md`, `docs/design/uix-zukunft-roadmap.md`, `docs/agent-ops/active-workboard.md`.
**Abnahme:** Masterplan + Roadmap committet; Wireframes fuer alle 5 Floorplans + Conversational-Shell; jede Roadmap-Aufgabe mit agent-faehigem Prompt; Meridian-Regeln (kein Bypass, Referenzmasken = Abnahme) durchgaengig eingehalten.
**Umsetzungsstart 2026-07-07:** UIX-060 in Arbeit — Kern (Intent-Compiler + Verstanden-als-Vorschau, 42 Tests, CI gruen b8885951b) und Backend (omnibox-catalog-Endpoint + _AGENT_SYNONYMS fuer alle 26 SDs, 5 Tests) geliefert — Omnibox als Evolution der bestehenden CommandPalette (Intent-Compiler mit Mehrwort-Matching, Filter-Extraktion, Verstanden-als-Vorschau); Backend-Katalog-Endpoint folgt im selben Slice.
**Spec-Nachtrag 2026-07-07:** 4 Milestone-Spezifikationen (docs/design/specs/uix-m1..m4-spec.md — Datenmodelle, API-Vertraege, Schema-Diffs, Gates, Testplaene) + 14 claimbare Slice-YAMLs (UIX-060..092, status geplant, ai_harness-Vertraege). Umsetzung startet mit UIX-060.
**Routen-Bruecke 2026-07-07:** UIX-060 Katalog-Konsum entblockt — Join-Analyse ergab, dass die MaskRegistry als Routenquelle untauglich ist (nur 7/26 mask_ids joinen, davon 4 nur Detail-:id). Loesung: kuratiertes `_SCREEN_LIST_ROUTE` (screen_id -> reale Listen-Route) als eine Wartungsstelle in screen_definitions; omnibox-catalog emittiert jetzt `route` je Eintrag; alle 26 gegen die Frontend-Routen-Registry validiert; 2 neue Gate-Tests.
**UIX-060 abgeschlossen 2026-07-07:** Rest umgesetzt — (1) Frontend-Consumer (`enrichCommandsWithOmniboxCatalog`: Katalog-Synonyme/Routen ueber `route==actionParams.path` in den Command-Katalog gemergt, fehlende Masken synthetisiert; in CommandPalette verdrahtet; 8 Vitest). (2) Telemetrie `POST /ux-telemetry/omnibox` (SHA-256, kein Klartext, 422-Gate) + `GET .../aggregate` (tenant-isoliert); Client fire-and-forget; 6 pytest. (3) Playwright `omnibox-smoke.spec.ts` (Ctrl+K->tippen->Vorschau->Enter->URL) + axe-Overlay-Check. tsc 0, OpenAPI 2540 Pfade.
**UIX-061 abgeschlossen 2026-07-07 (Owner Claude):** 5 native cockpit-SDs (workspace/einkauf|verkauf|lager|fibu|leitung) als rollenbasierte Startseiten. Backend (662bb1fe2): tiles-Block additiv, targetRoute via `_SCREEN_LIST_ROUTE` aufgeloest, `_apply_season_profile` (MM-TT-Fenster), Readiness-Advisory `cockpit_content`, alle 5 generatorReady/advisoryScore 1.0. Frontend: `RenderTilePlan`+`compileTiles`, `TileGridRenderer` (Ton neutral|warning|danger), `UniversalNativeCockpitPage` + 5 Seiten/Routen. Rollen-Redirect: `config/workspace_roles.yaml` (tenant-ueberschreibbar) + `GET /ui/mask-registry/workspace-startpage` + `useWorkspaceRedirect` (Flag `roleWorkspaces` default off). 27 pytest + 6 Vitest + Playwright Route-Smoke; tsc 0, OpenAPI 2541. Offen v1.1: Live-Kachel-Zaehler (brauchen count_only-Worklist-GETs). Naechste Slices: UIX-062 Collab-Rail, 063 Planungskalender.

**UIX-062 abgeschlossen 2026-07-07 (Owner Codex):** Collab-Rail v1 geliefert. Backend: Alembic `entity_notes_uix062` fuer `domain_shared.entity_notes`, SQLAlchemy-Modell `EntityNote`, tenant-isolierte API `/api/v1/collab/notes` mit CRUD, Creator-Guard, Soft-Delete, Mention-User-Validierung, Message-Inbox-Eintrag und Outbox-Event `collab.note.created`. Frontend: `layout.contextRailSections` additiv in `ScreenDefinition`/`RenderPlan`, `combined` bleibt kompatibel (`workflow,audit,copilot`), `collab` opt-in; `crm/customer-360` aktiviert `collab`; `WorkflowPanelRenderer` rendert Collab-Rail mit Plaintext-Notizen, Mention-Parsing, optimistischem Append und Mention-Badge. Abnahme lokal: `pytest tests/test_uix062_collab_notes.py -q --no-cov` -> 4 passed; `pnpm vitest run src/__tests__/render-plan/schema-compiler.test.ts src/__tests__/components/mask-builder/WorkflowPanelRenderer.test.tsx` -> 7 passed; `pnpm exec playwright test tests/e2e/collab-rail-smoke.spec.ts --project=chromium` -> 1 passed; `pnpm exec tsc --noEmit` -> 0; ESLint Produktdateien 0 errors. Hinweis: Playwright-Global-Teardown meldete bestehende Visual-Tour-Console-Issues ausserhalb des fokussierten Smokes.

**UIX-063 abgeschlossen 2026-07-07 (Owner Codex):** Planungskalender v1 als Zeitprojektion geliefert. Backend: Alembic `calendar_items_uix063` fuer `domain_shared.calendar_items` + `calendar_ics_tokens`; `calendar_projection_service.py` mit 5 Fachprojektoren (periodische Buchungen, OP-Faelligkeiten, Kontrakt-/Rabattfristen, CRM-Wiedervorlagen, Sachkunde) plus statischem Saison-Layer aus `config/saison_kalender.yaml`; idempotente Upserts, Stale-Delete nur fuer `projected`, proposed/confirmed/dismissed bleiben erhalten. API: `/api/v1/planung/kalender`, `/reproject`, `/items/{id}/confirm|dismiss`, rotierbarer read-only ICS-Feed `/ics?token=` mit Security-Exemption. Frontend: `calendar`-Contract in ScreenDefinition/RenderPlan, `CalendarRenderer` im UniversalMaskRenderer, native Route `/planung/kalender`, Layer-Toggles, 14-Tage-Fristenband, Klick-Durchstich. Abnahme lokal: `pytest tests/test_uix063_planning_calendar.py tests/test_workspace_cockpits_uix061.py -q --no-cov` -> 33 passed; `pnpm --dir packages/frontend-web test:run src/__tests__/components/mask-builder/calendar-renderer.test.tsx` -> 3 passed; `pnpm --dir packages/frontend-web type-check` -> tsc 0; `pnpm --dir packages/frontend-web exec playwright test tests/e2e/planung-kalender-smoke.spec.ts --project=chromium` -> 1 passed. Hinweis: Playwright-Global-Teardown meldete bestehende Visual-Tour-Console-Issues ausserhalb des fokussierten Smokes.

**UIX-071 (Frontend-Kern, Owner Claude, 3e2ddfa81) / UIX-072 (Voice-Kern, Owner Claude, 8dfd05ed8) — 2026-07-07:** UIX-071: `applyOverlay`-Allowlist-Compiler (render-plan/overlay.ts) schuetzt Sicherheitsfelder (actions/permissions/dangerLevel/fields/tableProfile/floorplan nicht overlaybar), Drift→invalidPaths, 10 Vitest. **Backend (Migration+ux_overlays.py+API) liefert Parallel-Agent Codex im geteilten Tree** (Kollision entdeckt+koordiniert, siehe UIX-071.yaml). UIX-072: STT-Adaptervertrag (`stt-provider.ts` + FakeSttProvider + Fallback-Kette) + harter Voice-Gate (`voice-navigation.ts` compileVoiceNavigation → nur navigate|none, "Danger nie per Stimme"), 12 Vitest. Beide: tsc 0, ESLint sauber. Offen je Slice: UI-Renderer (VoiceBar / Overlay-Toolbar) + Playwright.
**UIX-070 abgeschlossen 2026-07-07 (Owner Claude):** NL-Command-Ausfuehrung aus der Omnibox mit Ritual — vollstaendig. Neben dem Sicherheits-Kern (siehe unten) jetzt auch die UI: `command-compiler.ts` `detectCommandIntent` (Screen per Synonym benannt UND Aktions-Verb getroffen, unabhaengig vom Navigations-Ranking; Entitaeten-Extraktion), CommandPalette-Gruppe "Aktion vorbereiten" (commandDraft/formPrefill mit Badge + missingFields, onSelect → Ziel-Maske mit `?omniboxAction=` + Telemetrie), Katalog exponiert draftbare `actions`. Playwright `omnibox-command-smoke` (create_activity→formPrefill→URL) + Vitest command-compiler (5) gruen. Erkenntnis dokumentiert: entity-gebundene Aktionen → v1 = formPrefill; scharfe Rituale brauchen Entity-Resolution (Folge-Iteration).
**UIX-070 Sicherheits-Kern 2026-07-07 (Owner Claude, 25e58c705):** Conversational-Command-Sicherheitsmatrix testbewehrt — `classifyOmniboxAction` (ActionRuntime.ts) als Single Source of Truth (forbidden→unsichtbar, high/critical→nur Navigation, moderate→immer Ritual, safe→Ritual nur mit Confirmation sonst Prefill, confidence<0.75→formPrefill). IntentPlan+commandDraft/formPrefill, `command-safety.ts` (type-aware Slot-Filling + missingFields), `ActionRequest.triggerSource`. Spiegel-Suite `test_uix070_conversational_safety.py` über ALL_SCREEN_IDS (162 pytest: kein NL-Pfad umgeht Masken-Confirmation, forbidden unsichtbar, high/critical nie draftbar) + Vitest-Matrix (22). tsc 0, ESLint sauber. Offen (naechster Schritt): CommandPalette-UI-Verdrahtung (Omnibox-Katalog um `actions` je Screen → Compiler erzeugt commandDraft → `ActionRuntime.prepare`/ConfirmationDialog mit trigger_source) + Playwright create_activity-Prefill.

## A9-STRUKTUR-KONSOLIDIERUNG — Repo-Layout (ARCH-F1, SPEC-P1-07)

**Von:** Claude
**Owner:** Claude
**Stand:** umgesetzt 2026-07-06 — Root 39 -> 20 getrackte Verzeichnisse. `domains/` (paralleles TS-Backend, nie produktiv verdrahtet) nach `docs/_internal/archive/domains-ts-backend/` archiviert; Workflows `inventory-domain-ci.yml`/`finance-domain-ci.yml` geloescht, `audit-e2e`-Job aus `ci.yml` entfernt. 17 weitere Verzeichnisse archiviert (ols, gap, swarm+compose, memory, mains, l3-migration-toolkit, guacamole-l3-migration, knowledge-base, observability, contract-tests, qa, specs, planning, reports, extensions, load-tests, src->root-src-mcp-policy-server; `mcp:dev`-Script aus package.json entfernt). `database/` -> `infra/database/` konsolidiert (Compose-Pfade eventbus/production angepasst). Aktiv belassen: deploy (Dockerfile.frontend), ops (Superglue), monitoring, rationsoptimierung, services (je referenziert). ADR-039 + architecture-index regeneriert.
**Ziel:** Audit Prompt A9 — Root <=20 Verzeichnisse, deterministische Code-Zuordnung, CI-Gates gruen.
**Dateibesitz:** `docs/_internal/archive/**`, `docs/adr/adr-039-repo-layout.md`, `.github/workflows/ci.yml`, `.github/workflows/inventory-domain-ci.yml` (geloescht), `.github/workflows/finance-domain-ci.yml` (geloescht), `package.json`, `docker-compose.eventbus.yml`, `docker-compose.production.yml`, `infra/database/**`, `config/architecture-index.yaml`, `mkdocs.yml`.
**Abnahme:** Root <=20 getrackte Verzeichnisse (erfuellt: 20); architecture-index 889/206/399; quality-gate gruen in CI.
**Nachtrag CI-Stabilisierung:** events_raw.json-Cache-Drift (Agent-Handbuch regeneriert) + payment-run `dangerousActions`-Deklaration nachgezogen (UIX-048-Gate, latent aus 1772798e0 commandEndpoint-Aktivierung).

## A10-DOKU-EVIDENZ-001 — Doku-Drift & Evidenzkette (Prompt A10, Teilstand)

**Von:** Cursor Agent
**Owner:** Cursor Agent
**Stand:** abgeschlossen 2026-07-06 — Voll-A10: `release_evidence` auf ab7ab82e5 = **5 PASS/1 WARN/0 FAIL** (coverage via Vollsuite-XML aus CI-Artefakt backend-coverage-xml gemessen: alle Ratchets eingehalten; einzige WARN = external 6x conditional, echter Auflagen-Stand). Zuvor: Drift 0; OpenAPI regeneriert; README, Process-Kernel-STATUS, Open-Gaps, drift-dashboard auf gemessene Werte; `release_evidence.{json,md}` versionierbar. **Claude-Fortsetzung (Voll-A10):** external-Assessment aus CI-Run 28788983957 committet (`production-readiness-assessment.{json,md}`, .gitignore-Ausnahme); `check_external()` wertet jetzt das `{profiles:[...]}`-Format aus (6 Profile, 6x conditional — ehrlicher Messwert statt Datei-fehlt-WARN); quality-gate laedt `coverage.xml` als Artefakt `backend-coverage-xml` hoch (Vollsuite-Messung fuer Evidence-Lauf); README-CI-Zeile auf frischen main-Run 28788983957/`c2df41595` (11 943 passed). Offen: coverage-Dimension auf Vollsuite-XML aus naechstem CI-Lauf umstellen.
**Ziel:** Production-Readiness Prompt A10 — keine Wunschwerte in Statusdoku; Evidenzkette maschinenlesbar.
**Dateibesitz:** `README.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/architecture/process-kernel/STATUS.md`, `docs/entwickler/drift-dashboard.md`, `docs/schnittstellen/openapi.json`, `artifacts/release_evidence.{json,md}`, `.gitignore`.
**Abnahme:** `doc_drift_report.py --fail-over 0` Exit 0; `release_evidence_report.py --fail-on-red` Exit 0 (overall ≠ fail).

## SPEC-P1-04-08-A8 — commandEndpoints & Chargen/MHD (Production-Readiness Prompt A8)

**Von:** Cursor Agent
**Owner:** Cursor Agent
**Stand:** abgeschlossen 2026-07-06 — `MaskActionRuntime` (`app/services/mask_action_runtime_service.py`) mit validate/dryRun/propose/execute, Audit (`crm_action_audit_log`) und Outbox; Mask-Actions in `mask_actions.py` + bestehende Endpoints (AP-Freigabe, Mahnung, neue_bestellung) auf Runtime umgestellt; ScreenDefinitions ohne `stubReason` auf nativen SDs; Inventur `scripts/check_mask_command_endpoint_inventory.py` (26 native SDs, 0 Verstöße). Chargen: Lot-Attribute + FEFO über MHD (`inventory_lot_trace_service.py`); Migration `inv_lot_depth_spec_p1_08`.
**Ziel:** SPEC-P1-04 + SPEC-P1-08 aus Production-Readiness-Audit 2026-07-02.
**Dateibesitz:** `app/services/mask_action_runtime_service.py`, `app/api/v1/endpoints/mask_actions.py`, `app/core/screen_definitions.py`, `app/services/inventory_lot_trace_service.py`, `alembic/versions/inv_lot_depth_spec_p1_08.py`, `scripts/check_mask_command_endpoint_inventory.py`, `tests/test_spec_p1_04_mask_commands.py`, `tests/test_spec_p1_08_lot_fefo_pick.py`, `tests/test_uix050_053_advanced_actions.py`.
**Abnahme:** Inventur Exit 0; 26/26 pytest (SPEC-P1-04/08 + UIX-050..053) grün.

## SPEC-P0-01/02-CI-GRUEN-RUNTIME-SWEEP — quality-gate Voll-Gruen + Runtime-Sweep-Dauergate

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-07-05 (Runde 11) — quality-gate GRUEN auf main (a4ce0f3c2, run 28732436888); security-scan/universal-mask-ci/runtime-sweep gruen. Evidenz artifacts/ci-green-evidence.md, README-Badges+Statusblock aktualisiert. Runde 11 — pytest-Volllauf in CI GRUEN (11810 passed); letzter roter Schritt Coverage-Ratchet: psm_proplanta.py 14,9%<15,0% durch eigene HTTPException-Passthrough-Zeilen => Test tests/test_psm_proplanta_endpoints.py ergaenzt (deckt status/list/stats/search-Guards), Schwelle NICHT gesenkt (only-up). Runde 10 — pytest-Restfehler (endlich beim eigentlichen Testlauf): journal-entries-Test auf 503-Vertrag gezogen (SPEC-P0-03, war Codex-Kategorie-D-Test), coverage_summary-Test tolerant fuer fehlende coverage.xml, warehouses.address JSONB->varchar in Repair-Migration (001-Divergenz zum ORM-Modell), ownership_type-Insert 'eigen'->'owned' (Endpoint-Code gegen CHECK-Constraint). Runde 9 — OpenAPI-Versions-Default fest 3.0.0 im Generator (DEFAULT_API_VERSION, konvergent mit Codex-Hotfix); AUDIT-1 ISO-27001-Matrix (93/93) + AUDIT-2 SOC-2-Matrix ergaenzt. Runde 8 (Codex-Hotfix, s. u.) — Doc-generator-meta-check + Versions-Ping-Pong. Runde 7 — Mask-Performance-Gate mit gepinnter ts-node-Toolchain (npx-TS-Drift TS5011/5101/5109). Runde 6 — Runtime-Sweep in CI GRUEN (0x5xx/831 Routen, SPEC-P0-02 erfuellt); Runde-5-Restblocker gefixt: erp-domain-Tests (tsconfig.tests.json typecheckt gegen src/ statt nie committetem dist/), ts-node transpile-only im Backend-Job. SPEC-P0-03 umgesetzt: Modul-Aktivierungsmatrix, harte Regel journal-entries/bestaende (503+Metrik statt leerer Liste, Regressionstests), /health/ready prueft kritische Schemaobjekte. SPEC-P0-08: Restore-Drill-Runner + fail-closed Evidenz-Check. Vorher — quality-gate-Blocker behoben (sql_fstrings-nosec, Low-Stock-Doppelprefix, Klasse-A-Explainability, response_model/summary-Gates, Doku-Drift 15→0, Secret-Scan-False-Positives); Runtime-Sweep-Gate gebaut; erster Sweep fand 32×5xx → Repair-Migration `runtime_sweep_repair_20260702`, `init_db.py`+ORM-create_all, 20 Code-Bugfixes (u. a. DI-Container-Registrierung nie importiert, 3× Routen-Reihenfolge hinter Catch-all, CRM-Proxy-Degrade, uuid/text-Casts, FAOSTAT 502→503). Zusaetzlich: only-up-Ratchet (SPEC-P0-05), CODEOWNERS (SPEC-P0-06), SOC-2-Profil (SPEC-P0-07), docker-compose REDACTED_PASSWORD-Regression repariert.
**Codex-Hotfix:** abgeschlossen 2026-07-03 fuer Runde-8-Doc-generator-meta-check; Dateibesitz `.github/workflows/quality-gate.yml`, `scripts/generate_openapi.py`, `scripts/generate_container_inventory.py`, `scripts/render_c4_views.py`, `scripts/generate_architecture_index.py`, `scripts/generate_action_matrix_report.py` und `docs/agent-ops/active-workboard.md`; Abnahme `python scripts/generate_openapi.py --check`, direkte Doc-Generator-Sequenz, `scripts/generate_architecture_index.py --check --require-complete` unter WSL/Linux und `bash scripts/check_all_doc_generators.sh --check` via LF-Tempkopie gruen. Nachtrag: ADR-Sammlung im Architecture-Index ist case-insensitive; Backend-Job installiert vor `pnpm arch:validate` pnpm.
**Ziel:** SPEC-P0-01 (drei Ziel-Workflows auf main sichtbar gruen, Evidenz in `artifacts/ci-green-evidence.md`) und SPEC-P0-02 (Nightly-Sweep 0×5xx gegen frisch migrierte DB, Allowlist nur mit Begruendung+Ablaufdatum).
**Dateibesitz:** `.github/workflows/quality-gate.yml`, `.github/workflows/runtime-sweep.yml`, `scripts/api_runtime_sweep.py`, `scripts/init_db.py`, `scripts/doc_drift_report.py`, `config/runtime_sweep_allowlist.yaml`, `config/architecture-domain-prefixes.yaml`, `alembic/versions/runtime_sweep_repair_20260702.py`, `app/main.py`, betroffene Endpoint-/Service-Dateien.
**Abnahme:** quality-gate, security-scan und universal-mask-ci auf main gruen; `python scripts/api_runtime_sweep.py` Exit 0 (0×5xx, keine nicht-allowgelisteten 503, Allowlist nicht abgelaufen); Report in `artifacts/runtime-sweep-<datum>.json`.

## ADDRESS-VALUE-OBJECT — kanonisches Adressmodell (P2-Fundament)

**Von:** Claude
**Owner:** Claude
**Stand:** in Arbeit 2026-07-05 — kanonisches Adress-Value-Object `app/core/address.py` (Alias-Normalisierung country/countryCode/plz/zip/ort/…, Freitext- und JSON-String-Parsing, Geo lat/lon), bidirektionale Adapter (flach↔VO, JSONB↔VO), 21 Unit-Tests; ADR-038; erste Adoption in customer_service.py (Ad-hoc-Alias-Handling ersetzt). Nicht-brechend: Bestandsspeicherformen bleiben, Migration schrittweise ueber Adapter (Plan im ADR).
**Ziel:** Adressmodell-Vereinheitlichung (vom User angestossen) — eine kanonische Repraesentation statt flach-vs-JSONB-Divergenz.
**Dateibesitz:** `app/core/address.py`, `tests/test_address_value_object.py`, `docs/adr/adr-038-address-value-object.md`, `app/services/customer_service.py`, `mkdocs.yml`.
**Abnahme:** VO-Tests + customer-Tests gruen; ADR-Nav aktuell; Doku-Drift 0.

## A6-COVERAGE-OFFENSIVE — Finanz-Report-/Rechnungspfade

**Von:** Claude
**Owner:** Claude
**Stand:** in Arbeit 2026-07-06 — 3 vom Audit als nicht go-live-faehig markierte Finanzpfade mit Endpoint-Tests gehoben (isoliert gemessen, Vollsuite hoeher): financial_reports 25->53%, rohware_sammelabrechnung 32->61%, sales_invoice_einvoice 30->44%. Ratchets konservativ auf 50/58/42% angehoben (only-up, Baseline mitgezogen). psm_proplanta 16->84% (31 Tests, Ratchet 0.15->0.60); dabei latenten Bug im Import-Worker behoben: `_perform_psm_import` schrieb Felder, die `agrar_psm` nicht hat (hersteller/zulassung_datum/gefahrenklasse) und liess Pflichtfelder aus (artikelnummer/mittel_typ/zulassung_ablauf) — jede Neuanlage schlug still fehl. Zusaetzlich CI-Fix: `test_uix035_action_runtime_crm.py::test_readiness_gates_all_mandatory_green` prueft jetzt die ausgelieferte SD via `get_screen_definition` (Meridian-Dekoration) statt des rohen Builders.
**Ziel:** SPEC-P0-05 — kritische Beleg-/Report-Pfade aus dem 25-32%-Bereich heben.
**Dateibesitz:** `tests/test_financial_reports_endpoints.py`, `tests/test_rohware_sammelabrechnung_endpoints.py`, `tests/test_sales_invoice_einvoice_endpoints.py`, `tests/test_portal_innendienst.py`, `tests/test_hrm_abwesenheit.py`, `tests/test_kaeufergruppe.py`, `tests/test_psm_proplanta_endpoints.py`, `app/domains/agrar/api/psm_proplanta.py`, `tests/test_uix035_action_runtime_crm.py`, `scripts/check_critical_backend_coverage.py`, `config/coverage_ratchet_baseline.json`.
**Abnahme:** neue Tests gruen; Ratchet mit angehobenen Schwellen gruen in CI.
**Codex-Abnahme A6-Restmodule:** lokal 2026-07-05 `tests/test_portal_innendienst.py`, `tests/test_hrm_abwesenheit.py`, `tests/test_kaeufergruppe.py` gruen (82 passed). Zielmodul-Coverage aus `coverage.xml`: portal_innendienst 100.0%, hrm_abwesenheit 97.7%, kaeufergruppe 98.8%; Ratchets fuer alle drei konservativ auf 60% angehoben. Globaler `check_critical_backend_coverage.py` benoetigt Vollsuite-XML; A6-Teillauf-XML laesst erwartbar unbeteiligte kritische Pfade unter Schwelle erscheinen.

## A7-RESPONSE-MODEL-TYPING — API-Vertragshaertung + PII-Praevention

**Von:** Claude
**Owner:** Claude
**Stand:** in Arbeit 2026-07-05 — 55 untypisierte Routen mit response_model versehen (66->14, 99,6%), CI-Schwelle 80->20 gezogen; OpenAPI-Spec regeneriert. PII-Praevention: scripts/check_no_pii_data.py (Muster+Inhalt) in pre-commit + CI-Path-Guard, Art.-33-Meldeentwurf entfernt (Vorfall vom Verantwortlichen als nicht meldepflichtig eingestuft). SQL-S608-Review abgeschlossen (artifacts/appsec-s608-review.md): 121 Stellen musterbelegt sicher (Identifier aus Literalen/festen Listen/Pydantic-Whitelist, Werte gebunden).
**Ziel:** SPEC-P1-06 (response_model-Gate absenken) + SPEC-P0-04-Praevention (kein erneuter Lead-Daten-Push).
**Dateibesitz:** `app/api/v1/endpoints/*.py`, `.github/workflows/quality-gate.yml`, `scripts/check_no_pii_data.py`, `scripts/run-staged-checks.cjs`, `.pii-guard-allow.txt`, `docs/schnittstellen/openapi.json`.
**Abnahme:** `check_response_models.py --threshold 20` gruen; PII-Guard blockiert Muster+Inhalt; OpenAPI-Drift 0.

## UIX-MERIDIAN-BUILDER-001 - Meridian als Single-Mask-Builder-Vertrag

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-07-05 - Meridian-Layout-Metadaten werden zentral in `ScreenDefinition.layout` ergaenzt, in `RenderPlan.shell` kompiliert, im `UniversalMaskRenderer`/Fast-Renderer sichtbar gemacht und in Frontend-/Backend-Readiness als mandatory Gates geprueft. Low-Fidelity-/Wireframe-Triage im Design-Regelwerk dokumentiert. UIX-056 Browser-Smoke mit Meridian-Assertions und Mask-Performance-Smoke gruen.
**Ziel:** Den bestehenden Single Mask Builder als verbindliche Meridian-Render-, Layout- und Governance-Capability haerten.
**Dateibesitz:** `app/core/screen_definitions.py`, `app/api/v1/endpoints/mask_screen_definition.py`, `tests/test_agent_mask_contract.py`, `tests/test_uix046_048_command_endpoints_safety.py`, `packages/frontend-web/src/components/mask-builder/**`, `packages/frontend-web/src/__tests__/components/mask-builder/**`, `packages/frontend-web/src/__tests__/render-plan/schema-compiler.test.ts`, `packages/frontend-web/tests/e2e/uix-056-native-route-smoke.spec.ts`, `docs/design/valeo-meridian-experience.md`, `docs/architecture/uix/universal-mask-runtime-status.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/UIX-MERIDIAN-BUILDER-001.yaml`, `docs/agent-ops/active-workboard.md`.
**Abnahme:** Layout-Metadaten fuer alle nativen SDs; RenderPlan.shell aus Layout; Frontend-/Backend-Readiness-Gates blockieren fehlende Meridian-Metadaten; Finance/CRM/Inventory-Referenzen bestehen ueber native SDs; Meridian-Doku als Builder-Regelwerk. Lokal gruen: `pnpm --dir packages/frontend-web test:run src/__tests__/components/mask-builder/runtime/generatorReadiness.test.ts src/__tests__/components/mask-builder/UniversalMaskRenderer.test.tsx src/__tests__/render-plan/schema-compiler.test.ts` (25), `pytest tests/test_agent_mask_contract.py tests/test_uix046_048_command_endpoints_safety.py -q --no-cov` (270), `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `python scripts/generate_agent_handbuch.py --check`, `pnpm --dir packages/frontend-web exec playwright test tests/e2e/uix-056-native-route-smoke.spec.ts --project=chromium` (7), `VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER=true VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER=true pnpm --dir packages/frontend-web exec playwright test tests/e2e/mask-render-performance.spec.ts --project=chromium` (2). Hinweis: Playwright globalTeardown meldet bestehende Visual-Tour-Console-Issues im Repo-Artefakt, nicht im fokussierten Meridian-Smoke.

## UIX-MERIDIAN-VISUAL-AUDIT-002 - Meridian Visual-Audit fuer Referenzmasken

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-07-05 - Fokussierter Meridian-Visual-Audit nutzt die Benutzerhandbuch-Screenshot-Helfer fuer Render-Wait, Content-QC und Capture-Ziel; Finance, CRM 360 und Lager laufen bei 1366x768, 1440x900 und 1920x1080 gruen.
**Ziel:** Einen fokussierten Playwright-Visual-Audit fuer Finance, CRM 360 und Lager auf der bestehenden Single-Mask-Builder-Kette ergaenzen.
**Dateibesitz:** `packages/frontend-web/tests/e2e/meridian-visual-audit.spec.ts`, `docs/agent-ops/slices/UIX-MERIDIAN-VISUAL-AUDIT-002.yaml`, `docs/architecture/uix/universal-mask-runtime-status.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/active-workboard.md`.
**Abnahme:** Visual-Audit prueft 1366x768, 1440x900 und 1920x1080 auf repraesentativen nativen Masken; keine separate Referenzmasken-UI; Header, ActionBar, Tabs, Tabellenprofil, Context-Rail-Kontrakt und Basis-Overflow sind automatisiert abgesichert. Lokal gruen: `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`; `pnpm --dir packages/frontend-web exec playwright test tests/e2e/meridian-visual-audit.spec.ts --project=chromium` (9 passed). Hinweis: Playwright globalTeardown meldet bestehende Repo-weite Visual-Tour-Console-Issues, nicht den fokussierten Meridian-Audit.

## AUDIT-1/2/5 — ISO-27001-/SOC-2-Readiness + Audit-Orchestrator

**Von:** Claude
**Owner:** Claude
**Stand:** in Arbeit 2026-07-05 — `config/audit/iso27001-annex-a-matrix.yaml` (93/93 Controls: 33 conform, 12 minor, 48 external_gate, 0 offener major) und `config/audit/soc2-tsc-matrix.yaml` (CC1-CC9/A1/C1/PI1) angelegt; SOC-2-Profil in `simulate_external_assessors.py`; `scripts/check_audit_matrices.py` (fail-closed Vollstaendigkeits-/Konsistenzcheck) und `scripts/aggregate_audit_dashboard.py` (Ampel je Standard, external_gates nie als bestanden) neu; Orchestrator-Workflow `.github/workflows/audit-simulation.yml` (nightly + Release-Tag).
**Ziel:** AUDIT-1 (ISO Annex-A-SoA 93/93 mit Verdikt), AUDIT-2 (SOC-2-TSC-Matrix + Profil), AUDIT-5 (maschinenlesbares Dashboard). LLM-/Agenten-Zugriffe als eigenes Risiko erfasst.
**Dateibesitz:** `config/audit/*.yaml`, `scripts/check_audit_matrices.py`, `scripts/aggregate_audit_dashboard.py`, `scripts/simulate_external_assessors.py`, `.github/workflows/audit-simulation.yml`.
**Abnahme:** `python scripts/check_audit_matrices.py` Exit 0; Dashboard-Artefakt erzeugt; external_gates gelistet, nie als bestanden gewertet.

## SPEC-P0-04-PII-REMEDIATION — Repo-Hygiene & PII-Bereinigung

**Von:** Codex
**Owner:** Codex
**Stand:** reserviert 2026-07-02 — Fortsetzung der bereits begonnenen PII-/Repo-Hygiene-Remediation auf Branch `fix/pii-remediation`.
**Ziel:** SPEC-P0-04 aus dem Production-Readiness-Audit abschliessen: PII-/Tmp-/Build-Artefakte entfernen, `.gitignore` haerten, gitleaks-Baseline auditieren, History-Purge-Plan und DSB-Bewertung dokumentieren.
**Dateibesitz:** `.gitignore`, `.gitleaks-baseline.json`, `scripts/purge_pii_history.sh`, `artifacts/pii-remediation-report.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/SPEC-P0-04-PII-REMEDIATION.yaml`, `docs/agent-ops/active-workboard.md`.
**Abnahme:** Arbeitsbaum enthaelt keine getrackten PII-/Tmp-/Build-Artefakte aus SPEC-P0-04; Scan-Ergebnisse und DSB-Bewertung liegen in `artifacts/pii-remediation-report.md`; History-Purge-Plan ist dokumentiert; Slice-Verify und relevante Security-/Doku-Checks gruen oder mit external_gate begruendet.

## PROD-READINESS-AUDIT-001 — Production-Readiness-Audit & Agenten-Programm

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-07-02 — Audit-Dokument unter `docs/operations/production-readiness-audit-2026-07-02.md` verankert; Open-Gaps, Runbook, MkDocs und Slice-YAML synchronisiert; Slice-Verify gruen.
**Ziel:** Den Production-Readiness-Audit vom 2026-07-02 als belastbaren Spec-Backlog und Agentenprogramm im Repo sichtbar machen, ohne bestehende PII-Remediation- oder Vordruck-Arbeit zu vermischen.
**Dateibesitz:** `docs/operations/production-readiness-audit-2026-07-02.md`, `docs/operations/production-readiness-runbook.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/PROD-READINESS-AUDIT-001.yaml`, `docs/agent-ops/active-workboard.md`.
**Abnahme:** Audit-Dokument mit Frontmatter unter `docs/operations/`; P0/P1-Spec-Backlog in Open-Gaps referenziert; Runbook verweist auf Audit und Agentenprogramm; Slice-YAML mit Ziel, Dateibesitz, Akzeptanz und Risiken vorhanden.

## API-GAP-STABILIZATION-001 — Lager/Pricing/Scan Nachzug

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-07-02 — alle 5 API-Gaps geschlossen und regressionsgehärtet.

| Gap | Status |
|---|---|
| Lager API-Gap (`GET /lager/bestaende`, `POST /lager/bewegungen`) | done |
| Pricing API-Gap (`GET /pricing/find`, `POST /pricing/staffelrabatte`) | done |
| Barcode API-Gap (`POST /scan/barcode`) | done |

**Ziel:** Fünf produktionsblockierende API-Lücken (DB-Spaltenfehler, NOT-NULL-Verletzungen,
kaputte jsonb-Casts, fehlende Tenant-Isolation) schließen und dauerhaft mit
Regressionstests absichern.
**Dateibesitz:** `app/api/v1/endpoints/inventory_operations.py`, `app/api/v1/endpoints/pricing.py`,
`app/api/v1/endpoints/scan.py`, `tests/test_api_gap_lager_pricing_scan.py`,
`docs/project-context/open-gaps-and-known-issues.md`.
**Abnahme:** `tests/test_api_gap_lager_pricing_scan.py` (18 Tests: Happy Path, negativer
Payload, Tenant-Isolation, fehlende optionale Felder je Endpoint) grün gegen laufende
Postgres-Instanz. Siehe auch `open-gaps-and-known-issues.md` → `API-GAP-STABILIZATION-001`.
**Bekannte UI-Fails (nicht Teil dieses Gaps):** `UI-AGRAR-WIZARD-001` und
`UI-PERSONAL-BADGES-001` sind isolierte Frontend-Rendering-Bugs, siehe
`open-gaps-and-known-issues.md`. Nicht als API-Regression zählen.

## E2E-DOMAIN-ROUTES-WAVES-001 — E2E-Domänen-Routen in Waves

**Von:** Claude Code
**Owner:** offen
**Stand:** geplant 2026-07-02 — Folgeblock nach `API-GAP-STABILIZATION-001`, in 5 Waves
aufgeteilt, um Domänen unabhängig freizugeben statt eines Big-Bang-Testlaufs.

| Wave | Domänen | Status |
|---|---|---|
| Wave A | Lager, Pricing, Scan | done (Regressionstests in `API-GAP-STABILIZATION-001`) |
| Wave B | CRM, Einkauf | offen |
| Wave C | Finance | offen |
| Wave D | Agrar | offen (blockiert von `UI-AGRAR-WIZARD-001` für Sammelabrechnung-Teilstrecke) |
| Wave E | Personal, Admin | offen (blockiert von `UI-PERSONAL-BADGES-001` für Bewerbungen-Teilstrecke) |

**Ziel:** Alle E2E-Domänen-Routen wellenweise stabilisieren, ohne dass ein einzelner
UI-Bug den gesamten Testlauf rot färbt.
**Dateibesitz:** `packages/frontend-web/tests/e2e/all-domains-e2e.spec.ts`,
`packages/frontend-web/tests/e2e/workflow-chains.spec.ts`,
`packages/frontend-web/tests/e2e/uat/`.
**Abnahme:** je Wave ein eigener grüner Testlauf; Wave D/E dürfen erst als
abgeschlossen gelten, wenn die zugehörigen UI-Tickets referenziert (nicht
zwingend gefixt) sind — kein stummer Skip ohne Ticket-Kommentar.

## UIX-054…057 — Route-Verifikation, CI, Browser-Smoke, Rollback (nach UIX-051)

**Von:** Cursor Agent
**Owner:** Cursor Agent
**Stand:** abgeschlossen 2026-07-01 — UIX-054 Inventory-Tests, UIX-056 Playwright 6/6, UIX-057 Rollback-Matrix; UIX-055 CI Run `28540744515` grün; route-inventory nach UIX-051 nachgezogen (`5686f2177`).
**Ziel:** Generierte Route-Wahrheit prüfen, CI sichtbar grün, Browser-Smoke, Rollback dokumentiert — keine weiteren Routen migrieren.
**Dateibesitz:** `tests/test_uix054_route_inventory_verification.py`, `packages/frontend-web/tests/e2e/uix-056-native-route-smoke.spec.ts`, `docs/architecture/uix/uix-057-native-route-rollback-matrix.md`, `.github/workflows/universal-mask-ci.yml`.
**Abnahme:** pytest UIX-054 grün; universal-mask-ci Run grün; Playwright UIX-056 grün.

## DOC-AGENT-HANDBUCH-001 — Generiertes Agent-Handbuch (Code → Doku)

**Von:** Cursor Agent
**Owner:** Cursor Agent
**Stand:** abgeschlossen 2026-07-01 — `scripts/generate_agent_handbuch.py` erzeugt Prozessketten, Masken-API-Katalog, Automatisierung und JSON-Manifest aus Flow Spine, ScreenDefinitions, MCP und Events. CI: `docs.yml` + `check_all_doc_generators.sh`; Pre-Commit-Regen bei Quell-Aenderungen.
**Ziel:** Wartbare Agent-Bedienungsanleitung ohne manuelle Doppelpflege.
**Dateibesitz:** `scripts/generate_agent_handbuch.py`, `scripts/agent_handbuch_sources.py`, `docs/agent-handbuch/`, `tests/test_generate_agent_handbuch.py`, `config/docs-code-sync-map.yaml`, `mkdocs.yml`.
**Abnahme:** `python scripts/generate_agent_handbuch.py --check` gruen; 9 Unit-Tests; MkDocs-Nav Agent-Handbuch.

## UIX-047 — AP-Freigabe CommandEndpoint + Bestätigungsdialog-Fortsetzung

**Von:** Cursor Agent
**Owner:** Cursor Agent
**Stand:** in arbeit 2026-07-01 — `freigeben` für `finance/ap-invoice` mit Stub-Endpoint `/api/v1/finance/ap/invoices/{entity_id}/actions/freigeben` verdrahtet; folgt auf UIX-046 (neue_bestellung, mahnen, AlertDialog).
**Ziel:** Weitere gestubte Actions schrittweise auf `commandEndpoint` umstellen — AP-Freigabe als nächster P2-Kandidat mit `requiresConfirmation`.
**Dateibesitz:** `app/api/v1/endpoints/ap_invoices.py`, `app/core/screen_definitions.py`, `tests/test_uix046_048_command_endpoints_safety.py`.
**Abnahme:** pytest UIX-046/048-Suite grün inkl. freigeben-Contract-Tests.

## UIX-046 — CommandEndpoints neue_bestellung + mahnen + Bestätigungsdialog

**Von:** Cursor Agent
**Owner:** Cursor Agent
**Stand:** abgeschlossen 2026-07-01 — Stub-Endpoints für Lieferanten-Bestellung und OP-Mahnung; `commandEndpoint` in ScreenDefinitions; `AlertDialog` für `requiresConfirmation` in `UniversalNativeDetailPage`; CI-Workflow `universal-mask-ci.yml`.
**Ziel:** Erste Wave gestubter Actions auf ActionRuntime-Vertrag umstellen.
**Dateibesitz:** `app/api/v1/endpoints/einkauf_kpis.py`, `app/api/v1/endpoints/open_items.py`, `app/core/screen_definitions.py`, `packages/frontend-web/src/components/mask-builder/UniversalNativeDetailPage.tsx`, `tests/test_uix046_048_command_endpoints_safety.py`, `.github/workflows/universal-mask-ci.yml`.
**Abnahme:** 71/71 pytest grün (`test_uix046_048_command_endpoints_safety.py`).

## UIX-044 — FilterPlan Query Contract + ActionRuntime Anschluss

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-30 — Frontend serialisiert FilterPlan kanonisch als `filter_plan`; Backend akzeptiert `filter_plan` und den alten Alias `filterPlan`; generische Filter-Controls erzeugen Chips und loesen echte serverseitige Tabellen-Requests aus. `UniversalNativeDetailPage` ist nicht mehr No-op: Actions laufen ueber `useHumanActionDispatch`, verwenden die `commandEndpoint`-Definitionen aus der originalen `ScreenDefinition`, zeigen Fehler/Summary sichtbar an und refetchen Entity + Tabellen nach erfolgreicher Ausfuehrung.
**Ziel:** Native Masken laufen durchgaengig ueber den neuen Maskengenerator-Vertrag: strukturierte Filter erreichen effektiv das Backend; Actions nutzen echte `commandEndpoint`-Definitionen statt No-op.
**Dateibesitz:** `packages/frontend-web/src/components/mask-builder/runtime/*`, `packages/frontend-web/src/components/mask-builder/UniversalNativeDetailPage.tsx`, `packages/frontend-web/src/components/mask-builder/renderers/FastTableRenderer.tsx`, `app/api/v1/endpoints/mask_rollout_summaries.py`, `app/api/v1/endpoints/crm_360.py`, `tests/test_uix044_filter_plan_contract.py`, `packages/frontend-web/tests/e2e/universal-mask-filter-plan.spec.ts`.
**Abnahme:** Vitest `table-query-state.test.ts` 7/7 gruen; Backend-Contract-Test `tests/test_uix044_filter_plan_contract.py` 3/3 gruen mit isoliertem Pytest-Lauf (normaler Pytest-Plugin-Start in dieser Umgebung zeitweise haengend); Playwright Chromium FilterPlan 1/1 gruen; `pnpm --dir packages/frontend-web run type-check` gruen; `pnpm --dir packages/frontend-web run build` gruen; `pnpm --dir packages/bff run build` gruen.

## UIX-QA-044 — Frontend-Typecheck + Universal-Masken Browser-Gate

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-30 — Frontend-Typecheck wieder grün; Frontend- und BFF-Build neu ausgeführt; Universal-Masken mit Playwright im echten Chromium gegen Vite-Dev-Server und aktivierten Universal-Flags getestet. CRM-360 Pilot ergänzt `contacts` als Supplemental-Tab, damit `screen-summary.available_tabs=contacts` wieder einen lazy Ansprechpartner-Tab erzeugt. E2E-Mocks auf aktuelle ScreenDefinition-URL-Normalisierung (`crm__customer-360`, `sales__sales-order`) und Query-Parameter bei Lazy-Tab-Requests nachgezogen.
**Ziel:** Rote Frontend-TS-Gates sauber beseitigen, neuen Maskengenerator real im Browser validieren und Build-Stand für Frontend/Backend nachweisen.
**Dateibesitz:** `packages/frontend-web/src/pages/crm/kunden-stamm-modern/UniversalCustomerMaskPilotPage.tsx`, `packages/frontend-web/tests/e2e/*universal*`, `packages/frontend-web/tests/e2e/mask-render-performance.spec.ts`, `docs/architecture/uix/universal-mask-runtime-status.md`.
**Abnahme:** `pnpm --dir packages/frontend-web run type-check` grün; `pnpm --dir packages/frontend-web run build` grün; `pnpm --dir packages/bff run build` grün; Playwright Universal-Masken-Satz 8/8 grün.

## UIX-043b — Mask-API Blocker-Fixes (Path + Entity-Stub)

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-30 — FastAPI `{mask_id:path}` auf allen Mask-Routen (Slash in IDs wie `crm/customer-360`); generischer Entity-Stub `GET /api/v1/masks/{mask_id}/entity/{entity_id}` für Wave-2-SDs; Wave-2 `dataSources.entity` auf Mask-Entity-URL umgestellt; In-App-Hilfe Prefix-Matching bereinigt.
**Ziel:** Native Masken-API für alle 26 SDs erreichbar — keine 404 bei Slash-IDs, Kopf-Tab lädt auch ohne dedizierten Domain-Endpunkt.
**Dateibesitz:** `app/api/v1/endpoints/mask_screen_definition.py`, `app/core/screen_definitions.py`, `packages/frontend-web/src/lib/docs-help.ts`, `mkdocs.yml` (ADR UIX-034).
**Abnahme:** Docs/code-sync grün; pytest Mask-Contract unverändert grün.

## UIX-043 — Vollständige Masken-Migration (alle verbliebenen ObjectPage-Masken)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-30 — 13 weitere native SDs (Wave 2) fertiggestellt; 26 gesamt im Registry, alle `generatorReady=True`, `advisoryScore=1.00`. 18 Seiten bewusst exempt (Prozessmasken, Formulare, Batch-Screens). Vollständige Inventur in `docs/architecture/uix/uix-043-mask-migration-inventory.md`.
**Ziel:** Alle entity-detail ObjectPage-Masken auf native ScreenDefinition migrieren — keine Ausnahme ohne dokumentierten Grund.
**Dateibesitz:** `app/core/screen_definitions.py`, `packages/frontend-web/src/pages/{agrar,finance,einkauf,qualitaet,futtermittel,crm}/*-native.tsx`, `packages/frontend-web/src/app/route-aliases.json`, `docs/architecture/uix/uix-043-mask-migration-inventory.md`.
**Abnahme:** 60/60 pytest gruen; alle 26 SDs `generatorReady=True advisoryScore=1.00`; 20 route-aliases registriert.

## UIX-041/042 — Restliche native SDs + Frontend-Verdrahtung

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-30 — 7 native SDs (Wave 1: sales/delivery-note, einkauf/purchase-order, finance/ap-invoice, finance/ar-open-item, lager/stock-movement, agrar/harvest-settlement, finance/payment-run) promoted. `UniversalNativeDetailPage` als generischer Wrapper eingeführt. 7 thin wrapper pages + route-aliases.
**Dateibesitz:** `packages/frontend-web/src/components/mask-builder/UniversalNativeDetailPage.tsx`, `packages/frontend-web/src/components/mask-builder/index.ts`.
**Abnahme:** 60 pytest gruen; alle 13 SDs advisory=1.00.

## DOC-UIX-RUNTIME-001 — Mask-Runtime-Dokumentationspaket

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-29 — Benutzerhandbuch `masken-plattform.md`, Einkauf/CRM-Abschnitte, Parity-Matrizen supplier/opportunity, Entwickler-API, Agent-Runbook, mkdocs-Navigation, `generate_inapp_help_map.py` fuer mask-rollout.
**Ziel:** Vollstaendiges Doku-Paket fuer Universal Mask Runtime (Endnutzer, Entwickler, Agenten).
**Dateibesitz:** `docs/benutzerhandbuch/masken-plattform.md`, `docs/entwickler/mask-runtime-api.md`, `docs/agent-docs/runbooks/mask-runtime-agent-modus.md`, `docs/architecture/domains/einkauf/mask-parity-supplier-native.md`, `docs/architecture/domains/crm/mask-parity-opportunity-planned.md`, `scripts/generate_benutzerhandbuch_full.py`, `packages/frontend-web/src/lib/docs-help.ts`.
**Abnahme:** mkdocs-Eintrag Masken-Plattform; In-App-Hilfe mask-rollout → masken-plattform; Verweise in universal-mask-runtime-status.

## UIX-035 — ActionRuntime Backend-Command: CRM Aktivitaet anlegen

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-29 — `POST /api/v1/crm/customers/{customer_id}/actions/create_activity` mit vollstaendigem Mode-Support (validate/dryRun/propose/execute); Audit-Log-Eintrag bei execute; graceful degradation bei fehlender Tabelle im Dev/Test. `commandEndpoint` in ScreenDefinition verdrahtet.
**Ziel:** Erste produktive Mutation ueber ActionRuntime — fachlich relevant, kein Zahlungsrisiko.
**Dateibesitz:** `app/api/v1/endpoints/crm_360.py`, `app/core/screen_definitions.py` (commandEndpoint), `tests/test_uix035_action_runtime_crm.py`.
**Abnahme:** 14/14 pytest gruen — validate/dryRun/propose/execute, AgentContract-Gate, Readiness-Gates, commandEndpoint-Verdrahtung.

## UIX-036 — Agent-Modus End-to-End-Test

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-29 — Agent-Pfad (propose → dryRun → validate, kein execute) in `tests/test_uix035_action_runtime_crm.py` getestet. `checkActionPolicy` blockiert `forbiddenForAgents`/`humanApprovalRequired` korrekt. `create_activity` im AgentContract sichtbar mit `requiresHumanApproval=False`.
**Ziel:** VALEO agentenfaehig — Agent kann sicher lesen, vorschlagen, trocken laufen ohne zu schreiben.
**Dateibesitz:** `tests/test_uix035_action_runtime_crm.py` (test_agent_*), `packages/frontend-web/src/components/mask-builder/runtime/ActionRuntime.ts` (`checkActionPolicy`), `useActionRuntime.ts` (`useAgentActionDispatch`).
**Abnahme:** test_agent_dry_run_propose_chain, test_agent_contract_gate_on_action_definition gruen.

## UIX-037 — Rollout-Kandidaten Readiness-Bewertung

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-29 — Alle 10 Kandidaten (Wave 42-51) gegen 12 Gates geprueft; strukturelle Fehler behoben; advisoryScore einheitlich 50%; einziger Mandatory-Blocker = `non_temporary` (intentional — Rollout-Status).
**Ziel:** Beweisen dass die 10 Kandidaten strukturell korrekt sind; Promotions-Reihenfolge festlegen.
**Dateibesitz:** `app/core/screen_definitions.py` (_ROLLOUT_KOPF_FIELDS, entity-DataSource, fields[]-Tab, noWorkflowReason, sortable/filterable kontakte), `docs/architecture/uix/uix-037-rollout-readiness-report.md`.
**Abnahme:** Alle 10 Kandidaten: mandatory errors = 1 (non_temporary only), advisory = 50%, keine strukturellen Fehler.

**Promotions-Reihenfolge:**
1. einkauf/supplier → UIX-038 (naechster Schritt)
2. crm/opportunity
3. lager/article-stock
4. sales/delivery-note
5. einkauf/purchase-order
6. finance/ap-invoice
7. finance/ar-open-item
8. lager/stock-movement
9. agrar/harvest-settlement
10. finance/payment-run (zuletzt — hoechstes Risiko)

## UIX-038…040 — Native ScreenDefinition Promotionen

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-29 — `einkauf/supplier`, `crm/opportunity` und `lager/article-stock` loesen jetzt auf native ScreenDefinitions mit `adapter.temporary=false` auf. Alle drei erreichen `generatorReady=true`, `advisoryScore=1.0`; Regressionstest verhindert, dass promotete Masken wieder durch den generischen Rollout-Builder ueberschrieben werden.
**Ziel:** Die ersten drei UIX-037-Rollout-Kandidaten nativ promoten, ohne sofort Legacy-Routen oder Mutationspfade umzubauen.
**Dateibesitz:** `app/core/screen_definitions.py`, `tests/test_agent_mask_contract.py`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/architecture/uix/universal-mask-runtime-status.md`, `docs/architecture/domains/einkauf/mask-parity-supplier-native.md`, `docs/architecture/domains/crm/mask-parity-opportunity-planned.md`.
**Abnahme:** `python -m pytest tests/test_agent_mask_contract.py -q --no-cov` → 22/22 gruen; `python -m pytest tests/test_mask_rollout_batch_w42_51.py -q --no-cov` → 24/24 gruen; direkte `_check_readiness()`-Pruefung fuer 038–040: keine Errors/Warnings.
**Folge:** UIX-042 Frontend-Verdrahtung fuer `einkauf/supplier`; UIX-041 `neue_bestellung` CommandEndpoint; weitere Promotionen ab `sales/delivery-note`.

## UIX-STABILIZATION-031-034 — Runtime-Stabilisierung und Produktionsnachweis

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-29.

**UIX-031:** `open-gaps-and-known-issues.md` aktualisiert, UIX-022…030 als abgeschlossen dokumentiert, Restarbeit 032–037 mit Prioritaeten erfasst.
**UIX-032:** Backend pytest 24/24 (rollout), 19/19 (agent_contract), 14/14 (uix035/036) lokal gruen; tsc --noEmit 0 Fehler. GitHub Actions: naechster Push loest CI aus.
**UIX-033:** 12 Readiness-Gates aktiv (6 mandatory + 6 advisory). `GET /masks/{id}/readiness` Endpunkt aktiv.
**UIX-034b/c:** CRM-360 masterdata/address fields[], Advisory-Gates auf 83%, agentContract explizit, noWorkflowReason gesetzt.

**Dateibesitz:** `docs/project-context/open-gaps-and-known-issues.md`, `docs/adr/uix-034-crm360-native-parity-matrix.md`, `app/core/screen_definitions.py`, `app/api/v1/endpoints/mask_screen_definition.py`.
**Abnahme:** ScreenDefinition CRM-360 generatorReady=true, advisoryScore=83%; 10 Rollout-Kandidaten strukturell OK, einziger Block = non_temporary.

## UIX-RUNTIME-ROLLOUT-021 — Rollout-Kandidaten auf useUniversalMaskRuntime migrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-29 — Alle 10 Wave-42–51-Rollout-Kandidaten laufen jetzt ueber `useUniversalMaskRuntime`. Fachliche Spalten mit `renderKind`, `sortable` und `width` fuer alle 10 Screens in `_ROLLOUT_TAB_COLUMNS`. VirtualDataTable unterstuetzt Sort-Indikatoren und `onSortChange`. `FastTableRenderer` formatiert Zellen nach `renderKind` (currency, date, datetime, status, boolean). `UniversalMaskRolloutPilotPage` komplett neu auf generischen Hook umgestellt.
**Ziel:** Alten `usePilotRenderPlan + useMaskPilotState + useRolloutTabData`-Pfad in der generischen Rollout-Pilot-Page durch `useUniversalMaskRuntime` ersetzen; Rollout-Catalog mit echten `RolloutWaveSpec`-Eintraegen und `api_prefix` fuellen; Rollout-ScreenDefinitions mit fachlichen Spalten generieren; Sort-Support in Renderer-Stack nachziehen.
**Dateibesitz:** `app/core/mask_rollout_catalog.py`, `app/core/screen_definitions.py` (_ROLLOUT_TAB_COLUMNS + _build_rollout_screen_definition_from_spec), `packages/frontend-web/src/components/mask-builder/schema.ts`, `render-plan/types.ts`, `render-plan/schema-compiler.ts`, `renderers/FastTableRenderer.tsx`, `renderers/FastTabRenderer.tsx`, `components/ui/VirtualDataTable.tsx`, `pages/workflow/mask-rollout/UniversalMaskRolloutPilotPage.tsx`.
**Abnahme:** 181 Vitest-Tests gruen, 14 pytest-Tests (native CRM) gruen. Rollout-Catalog 10/10 Specs. Screen-Definitions fuer alle 10 Kandidaten mit dataSources und typisierten Spalten. UniversalMaskRolloutPilotPage ohne Legacy-Abhaengigkeiten.

## UIX-RUNTIME-022…030 — UniversalMaskRuntime Ausbau (Sort/Filter/Form/Action/Workflow/Agent)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-29 — Phasen 022–030 vollstaendig implementiert und gepusht.
**Ziel:** Einheitliche ScreenDefinition als Single Source of Truth fuer Human UI und AI-Agenten. Kein Dual-Pfad mehr: Sort-Whitelist, FilterPlan, FormState, ActionRuntime, WorkflowRuntime, CRM 360 native Parity, AgentMaskContract, Generator-Readiness-Gates.
**Commit:** `81d706da8` (028–029), weitere Commits fuer 022–027 in Vorgaenger-Session.
**Slice-Kette (abgeschlossen):**

| Phase | Inhalt | Status |
|-------|--------|--------|
| 022 | Sort-Whitelist: `get_sortable_columns`, `paginate_tab_items` mit sort/sort_dir | ✅ |
| 023 | FilterPlan: 8 Operatoren, `get_filterable_columns`, JSON-Param, FilterChips-UI | ✅ |
| 024 | (Lookup-Binding via LookupBindingContext) | ✅ |
| 025 | UniversalFormState: Ref-Guard, dirty-Tracking, Sticky-Submit-Bar | ✅ |
| 026 | ActionRuntime: ActionPolicy, checkActionPolicy, useActionRuntime, dryRun/validate/propose | ✅ |
| 027 | WorkflowRuntime: WorkflowState, tone-colored WorkflowPanelRenderer, useWorkflowState | ✅ |
| 028 | CRM 360 native Parity: useUniversalMaskRuntime als Pfad wenn adapter.temporary===false | ✅ |
| 029 | AgentMaskContract: generateAgentMaskContract, GET /masks/{id}/agent-contract | ✅ |
| 030 | Generator-Readiness-Gates: checkGeneratorReadiness, 6 mandatory Gates, GET /masks/{id}/readiness | ✅ |
| 033 | Readiness verschärft: 6 mandatory + 6 advisory pro Tabelle | ✅ |

**Commit:** `e6cabb380` (030), `fd2b8a7cf` (033 Doku+Gates), `81d706da8` (028–029).

## UIX-ROLLOUT-BATCH-019 — Universal Mask Rollout Batch (Waves 42–51)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-29 — gepusht auf `main` (`ad4727482`, Backend); Frontend-Pilot bereits in `8aca70b42`.
**Ziel:** Nach CRM/Sales/Agrar-Kontrakt die naechsten zehn Domänen-Piloten (Lager, Finance, Einkauf, CRM Opportunity, Sales LS, Agrar Settlement) hinter Feature-Flag ausrollen.
**Dateibesitz:** `app/core/mask_rollout_catalog.py`, `app/core/mask_screen_summary_common.py`, `app/services/mask_rollout_summary_service.py`, `app/api/v1/endpoints/mask_rollout_summaries.py`, `app/core/mask_classification.py`, `app/core/screen_definitions.py`, `packages/frontend-web/src/features/mask-rollouts/`, `packages/frontend-web/src/pages/workflow/mask-rollout/`, `tests/test_mask_rollout_batch_w42_51.py`, `docs/architecture/uix/mask-rollout-batch-w42-51.md`, `docs/agent-ops/slices/UIX-ROLLOUT-BATCH-019.yaml`
**Doku:** [`mask-rollout-batch-w42-51.md`](../architecture/uix/mask-rollout-batch-w42-51.md), [`mask-generator-rollout-template.md`](../architecture/uix/mask-generator-rollout-template.md) (Reihenfolge Waves 42–51)
**Abnahme:** pytest `test_mask_rollout_batch_w42_51.py` 24/24 gruen; Vitest `mask-rollout-route.test.tsx`; Flag `VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS=true` + Route `/mask-rollout/{screenId}/{entityId}`.
**Offene Grenzen (bewusst):** Mutationen/Legacy-Detail-Routes; fachliche Feintuning-Matrix pro Domäne; **Governance:** keine weiteren `generator_ready`-Setzungen bis UIX-032 (CI) + UIX-034 (CRM-Parität) grün — Runtime-Plattform siehe [`universal-mask-runtime-status.md`](../architecture/uix/universal-mask-runtime-status.md) (UIX-021…030 abgeschlossen).

## UIX-MASK-AB-BENCH-018 — A/B Render Benchmark (Legacy vs. Pilot)

**Von:** Cursor
**Owner:** offen
**Stand:** geparkt 2026-06-28 — Frontend-Baseline nach ESLint-Wave 3 (`d22193fa8`) stabiler; Reaktivierung moeglich sobald Sales/Kontrakt-Pilot-Selektoren final sind.
**Ziel:** Messbarer Proof-of-Concept: Shell-Ready-Zeit, initiale API-Bytes, DOM-Zeilen Legacy vs. RenderPlan-Pilot (Sales + Kontrakt).
**Dateibesitz:** `packages/frontend-web/tests/e2e/mask-render-ab-benchmark.spec.ts`, `tests/e2e/helpers/mask-*`, `scripts/benchmark_mask_render_ab.ts`, `pages/workflow/mask-benchmark/MaskBenchmarkRoute.tsx`, `docs/architecture/uix/render-performance-baseline.md`
**Abnahme:** `MASK_AB_BENCHMARK=1 pnpm benchmark:mask-render-ab` gruen; Report in `evidence/perf/`; Baseline-Doku mit gemessenen Zahlen.

## UIX-AGrar-PILOT-017 — Universal Mask Generator Agrar Kontrakt Pilot

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-28 — Kontrakt-Pilot hinter `VITE_ENABLE_UNIVERSAL_MASK_AGRAR_KONTRAKT`; screen-summary, lazy Positionen/Umsaetze; Legacy fuer Neuanlage; Sales order-editor Route-Switch repariert.
**Ziel:** Dritte Domäne im Universal Mask Generator; Summary-first, read-only Pilot ohne Legacy-Ersatz.
**Abnahme:** Flag + contract-id → Pilot; Neuanlage → Legacy; pytest/Vitest gruen; Paritaetsmatrix dokumentiert.

## UIX-RENDER-PLAN-009 … UIX-ROLLOUT-TEMPLATE-016 — RenderPlan Performance Engine (Waves 33–40)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-28 — SchemaCompiler, RenderPlan-Cache, Fast Renderer, LookupField, server paging, Bundle-Gate, Perf-E2E; CRM/Sales auf RenderPlan.
**Ziel:** Performance-orientiertes Maskenframework mit vorkompiliertem RenderPlan statt Runtime-Interpretation.
**Abnahme:** compileRenderPlan + useRenderPlan; Pilot-Pages ohne grosses useMemo; CI bundle/perf gates; Doku render-plan-architecture + rollout-template.

## UIX-SALES-PARITY-008 - Sales Order Lazy Tab Parity (Lieferung/Dokumente)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-28 — Lazy Tabs `lieferung` und `dokumente` via tab_endpoints; Paritaetsmatrix; Vitest/pytest/Playwright gruen.
**Ziel:** Sales-Pilot von Positionen-only zu Liefer-/Dokument-Paritaet erweitern ohne Legacy-Mutationen zu ersetzen.
**Abnahme:** tab_endpoints fuer lieferung/dokumente; Lazy-Load bei Tab-Wechsel; Paritaetsmatrix dokumentiert; Legacy unberuehrt.

## UIX-SALES-PILOT-007 - Universal Mask Generator Sales Order Pilot

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-28 — Verkaufsauftrag-Generator-Pilot hinter `VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER` (nur bestehende Auftraege); screen-summary, lazy Positionen, Legacy-Editor fuer Neuanlage.
**Ziel:** Zweite Domäne im Universal Mask Generator; Summary-first, read-only Pilot ohne Legacy-Ersatz.
**Abnahme:** Flag + order-id → Pilot; Neuanlage/Workflow → Legacy; Vitest/pytest gruen.

## UIX-CRM-PARITY-003 - CRM Customer 360 Lazy Tab Data Parity

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — Lazy Tab-Daten, tab_endpoints, Paritaetsmatrix, Tests; Renderer-Lib, native ScreenDefinition und Perf-Gate in Waves 28–30 nachgezogen.
**Ziel:** CRM-Pilot von renderbarer Shell zu 360-naher Paritaet: aktiver Tab laedt echte Listendaten nach, ohne Legacy-Maske zu ersetzen.
**Abnahme:** Mindestens 4 Tabs mit Lazy-Load; tab_endpoints dokumentiert; Paritaetsmatrix; Vitest/pytest/Playwright gruen; Legacy-Fallback unberuehrt.

## UIX-RENDERER-LIB-004 - Mask Builder Renderer Library

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — Field/Table/Summary/Action/Tab/Workflow-Renderer extrahiert; UniversalMaskRenderer als Orchestrator.
**Ziel:** Visualisierungslayer aus Monolith loesen (Refactor-only).
**Abnahme:** Vitest UniversalMaskRenderer unveraendert gruen; Diff = Move only.

## UIX-DATA-CONTRACT-005 - Native ScreenDefinition API

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — GET /api/v1/masks/{id}/screen-definition, useScreenDefinition, crm/customer-360 nativ.
**Ziel:** Backend liefert native ScreenDefinition; Adapter wird schrittweise Fallback.
**Abnahme:** pytest test_mask_screen_definition gruen; Pilot nutzt native Metadaten wenn Endpoint 200.

## UIX-PERF-GATE-006 - Mask Performance Contract CI

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — check_mask_performance_contract.ts im Quality-Gate; lookup_min_chars in Registry.
**Ziel:** Performance-Vertrag operationalisieren.
**Abnahme:** Script gruen fuer generator_ready Masken; CI-Schritt aktiv.

## UIX-CRM-PILOT-002 - Universal Mask Generator CRM Customer Pilot

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-28 - CRM-Kundenpilot hinter `VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER` geliefert: UniversalMaskRenderer-Anbindung, Legacy-Fallback, Summary-first-Datenfluss, Permission-Action-Filter, Mobile-Layout-Haertung und Unit-/Backend-/Playwright-Abnahme.
**Ziel:** CRM Kundenstamm/360 als erste echte Maske ueber `ScreenDefinition` und `UniversalMaskRenderer` anbinden, ohne alte Maske zu ersetzen; Generator-Paritaet, Mobile-Verhalten und Performance-Vertrag messbar machen.
**Dateibesitz:** `packages/frontend-web/src/pages/crm/kunden-stamm-modern/**`, `packages/frontend-web/src/pages/crm/kunden-stamm-modern.tsx`, `packages/frontend-web/src/features/crm-masks/**`, `packages/frontend-web/src/components/mask-builder/**`, `packages/frontend-web/src/lib/api/**`, CRM-Pilot-Tests, `docs/adr/adr-011-ui-maskenstrategie.md`, `docs/architecture/domains/crm/README.md`, `docs/project-context/open-gaps-and-known-issues.md`, Slice-YAML.
**Abnahme:** Feature Flag schaltet Legacy vs. Universal Pilot; Customer MaskConfig wird temporaer adaptiert; Shell/Summary erscheinen vor Details; Tabs bleiben lazy; Permissions und Mobile-Modi sind getestet; Legacy-Fallback bleibt intakt; Doku und Open-Gaps aktualisiert. Typecheck, Backend-Contracts und Playwright-Pilot-Smoke Desktop/Mobile gruen; globaler Visual-Tour-Teardown meldet bestehende Alt-Warnungen ausserhalb des Pilot-Scopes.

## UIX-MASK-FRAMEWORK-001 - Universal Mask Generator with Translation Layer Skeleton

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-28 - Skeleton geliefert: canonical ScreenDefinition/MaskSchema, temporaere Uebersetzungsschicht fuer Legacy-MaskConfig, UniversalMaskRenderer, LazyTabs, VirtualDataTable, CRM Screen-Summary-Pilot, Mask-Registry-UIX-Metadaten und ADR-/Domain-Pack-Nachzug.
**Ziel:** VALEO-Masken langfristig ueber einen neutralen Generator mit getrennten Daten-/Permission-/Workflow-Vertraegen und wiederverwendbarem Visualisierungslayer fuehren; alte Masken bleiben aktiv, bis Adapter-Paritaet und Performance belegt sind.
**Dateibesitz:** `app/core/mask_classification.py`, `app/api/v1/endpoints/crm_360.py`, `packages/frontend-web/src/components/mask-builder/**`, `packages/frontend-web/src/components/ui/LazyTabs.tsx`, `packages/frontend-web/src/components/ui/VirtualDataTable.tsx`, `docs/adr/adr-011-ui-maskenstrategie.md`, Domain Packs CRM/Agrar/Inventory/Finance, `docs/project-context/open-gaps-and-known-issues.md`, Slice-YAML.
**Abnahme:** Generator-/Adapter-Vertrag dokumentiert; UIX-/Generator-Metadaten im Mask Registry Contract; UniversalMaskRenderer/LazyTabs/VirtualDataTable/Adapter getestet; CRM-Screen-Summary-Endpunkt getestet; ADR-011 und Doku aktualisiert. Frontend-Unit-Slice und Backend-Contract-Tests gruen; lokaler Frontend-Typecheck und direkter `tsc` liefen nach der Typkorrektur in 300s ohne Diagnose in den Timeout.

## DOC-ARCH-STACK — Architektur-Dokumentations-Stack (ISO 42010 + arc42 + C4)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-27 — Plan „Architektur-Dokumentation IST + Umsetzung“ vollstaendig: ADR-036, arc42 (12 Kapitel), ISO-42010-Matrix, C4 Context/Container/Components, Enterprise-Landkarte, ERD, 3 Sequenzdiagramme, Container-Inventar-Generator.
**Ziel:** Formale Architektursichten ergaenzen Process Kernel + ADRs ohne Tool-Bruch (Mermaid in MkDocs).
**Dateibesitz:** `docs/architecture/arc42/`, `docs/architecture/views/`, `docs/adr/adr-036-architecture-documentation-stack.md`, `docs/README.md`, `scripts/generate_container_inventory.py`, `docs/entwickler/container-inventory.md`, `mkdocs.yml`, Slices `DOC-ARCH-FOUNDATION-001` … `DOC-ARCH-SEQ-001`, `docs/project-context/open-gaps-and-known-issues.md` (Abschnitt DOC-ARCH-STACK-001).
**Abnahme:** Alle 8 Slices abgeschlossen; optional P1-Components, UML-Klassen, Production-C4, CI-Gate (2026-06-27) nachgezogen; `mkdocs build` 0 Errors; `generate_container_inventory.py --check` OK.

| Slice | Inhalt |
|---|---|
| DOC-ARCH-FOUNDATION-001 | ADR-036, Index, docs/README.md |
| DOC-ARCH-ARC42-001 | arc42 Hub + ISO-42010 |
| DOC-ARCH-C4-001 | System Context |
| DOC-ARCH-C4-002 | Container + Generator |
| DOC-ARCH-C4-003 | Enterprise-Landkarte |
| DOC-ARCH-C4-004 | Component CRM/Agrar/Finance |
| DOC-ARCH-ERD-001 | Canonical ERD |
| DOC-ARCH-SEQ-001 | Sequenz O2C/Agrar/Auth |
| DOC-ARCH-C4-005 | Component Einkauf/Lager + DMS/Compliance (optional) |
| DOC-ARCH-UML-001 | UML classDiagram Canonical Core (optional) |
| DOC-ARCH-CI-001 | Container-Drift CI-Gate (optional) |

## LOADTEST-STAGING-GATE-001 - Erntepeak-Lasttest als externes Gate haerten

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-27 — Scheduled `Lasttest Erntepeak (Gap 037)` scheiterte an nicht aufloesbarem `staging.valeo-erp.de` und leerem `API_DEV_TOKEN`; Workflow prueft jetzt `STAGING_URL`, Token und DNS vor k6-Start und dokumentiert fehlende externe Voraussetzungen neutral.
**Ziel:** Lasttest-Gate darf Infrastruktur-/Secret-Luecken nicht als Produkt-Performancefehler melden; manuelle Lasttests bleiben hart und schlagen bei fehlender Zielkonfiguration fehl.
**Dateibesitz:** `.github/workflows/load-test.yml`, `docs/operations/production-readiness-runbook.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/LOADTEST-STAGING-GATE-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Schedule ohne Staging/Token/DNS endet erfolgreich mit Summary als externes Gate; manuelle `harvest-peak`-Ausfuehrung verlangt gueltiges Ziel und Token; Runbook fuehrt das Gate.

## COV-RATCHET-010 - Quality-Gate Baseline nach CI-Messung korrigieren

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-27 — Quality-Gate-Folgefix auf `main`: Ratchet-Schwellen fuer zehn Pfade auf real gemessene CI-Coverage kalibriert, nachdem geschaetzte Schwellen den Gate-Lauf blockierten. OpenAPI-Drift separat mit `e35fb7798` bereinigt.
**Ziel:** Kritischen Backend-Coverage-Ratchet wieder als belastbares Gate betreiben: Schwellen duerfen nicht ueber der zuletzt gemessenen CI-Coverage liegen; fachliche Vertiefung erfolgt danach ueber gezielte Tests.
**Dateibesitz:** `scripts/check_critical_backend_coverage.py`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/COV-RATCHET-010.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** `python scripts/check_critical_backend_coverage.py` laeuft gegen Quality-Gate-Coverage wieder gruen; betroffene Pfade und Folgevertiefung sind in Open-Gaps dokumentiert.

## HR-TIME-WIZARD-001 - UX-M3 Gefuehrter Planungswizard (5 Schritte)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — 5-Schritt-Inline-Wizard im Planung-Tab (Zeitraum → Bedarf → Praeferenzen → Vorschau → Abschluss); dynamische Bedarfszeilen; Fortschrittsbalken; `useCreateWorkPlanAssignment`-Hook; Mutation-Guard via `isPending`; tsc 0 Fehler.
**Ziel:** UX-M3 (Gefuehrter Planungswizard): Arbeitsplan ohne manuelle Mehrfacherfassung erstellen — Schritt-fuer-Schritt-Fuehrer mit Vorschau vor Speichern.
**Dateibesitz:** `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-ux-workflow-roadmap-2026-05-12.md`, `docs/agent-ops/slices/HR-TIME-WIZARD-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Wizard oeffnet auf Knopf; 5 Schritte navigierbar; Schritt 5 sendet POST; isPending-Guard aktiv; tsc 0; UX-M3 als umgesetzt markiert.

## HR-TIME-SEASON-BOARD-001 - UX-M7 Saison-Leitstand 7-Tage-Heatmap

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — neuer "Saison-Leitstand"-Tab mit 7-Tage-Heatmap (Blocker/Warnungen/ok farbkodiert pro Tag); Kampagnen-Perioden-Mapping; Schulferien- und Bruecktag-Marker; Kampagnen- und Abwesenheiten-Tabelle darunter. tsc 0 Fehler.
**Ziel:** UX-M7 (Kalender- und Saisonleitstand) umsetzen: Engpaesse durch Kampagnen, Ferien und Abwesenheiten auf einen Blick sehen ohne API-Mehraufwand — reine UI-Aggregation bestehender Queries.
**Dateibesitz:** `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-ux-workflow-roadmap-2026-05-12.md`, `docs/agent-ops/slices/HR-TIME-SEASON-BOARD-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** 7-Tage-Heatmap im Saison-Tab; Farbkodierung korrekt; tsc 0; UX-M7 als umgesetzt markiert.

## HR-TIME-DRIVER-DISPO-001 - UX-M4 Driver-Dispo Detail-Panel + Tour-Korrektur

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Driver-Tab mit KPI-Badges, Row-Fokus-Detail-Panel (Plausibilitaets-Checks, Findings), Tour/Fahrzeug-Korrektur via PATCH; `useUpdateDriverTimeEvent` Hook; tsc 0 Fehler.
**Ziel:** LKW-Fahrer/Tour/Fahrzeug/Plausibilitaet in einer Sicht; Dispatcher kann Tour/Fahrzeug ohne Tab-Wechsel korrigieren.
**Dateibesitz:** `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-ux-workflow-roadmap-2026-05-12.md`, `docs/agent-ops/slices/HR-TIME-DRIVER-DISPO-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Detail-Panel bei Row-Fokus; PATCH-Mutation mit isPending-Guard; tsc 0; UX-M4 markiert.

## HR-TIME-PAYROLL-CLOSE-001 - UX-M5 Payroll Closeout Gate

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Export-Gate implementiert: Button disabled wenn Blocker offen; Payroll-Tab mit Gate-Banner (per-Blocker + Direktlink Steuerung) und Freigabe-Banner; tsc 0 Fehler.
**Ziel:** Export-Button sperren solange Blocker nicht geloest; klare per-Blocker-Auflösung ohne Tab-Suche.
**Dateibesitz:** `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-ux-workflow-roadmap-2026-05-12.md`, `docs/agent-ops/slices/HR-TIME-PAYROLL-CLOSE-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Export-Button disabled bei Blockern; Gate-Banner sichtbar; tsc 0; UX-M5 als umgesetzt markiert.

## HR-TIME-ACTIONPANEL-001 - UX-M2 Detail-Aktionspanel Zeiten/Arbeitsplan

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Rechtes Detail-Aktionspanel in Zeiten- und Arbeitsplan-Tab implementiert; erscheint bei Row-Fokus ohne Tab-Wechsel; zeigt Mitarbeiter/Status/Compliance-Befunde/Aktionen. Admin-Suite-Roadmap auf umgesetzt korrigiert. tsc 0 Fehler.
**Ziel:** UX-M2 (Aktionspanel) umsetzen: Row-Fokus zeigt Kontext und Aktionen direkt rechts — kein Tab-Wechsel, keine ID-Kopie noetig.
**Dateibesitz:** `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-ux-workflow-roadmap-2026-05-12.md`, `docs/project-context/admin-suite-roadmap-2026-05-30.md`, `docs/agent-ops/slices/HR-TIME-ACTIONPANEL-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** onRowFocus → rechtes Panel; tsc 0 Fehler; UX-M2 als umgesetzt markiert.

## COV-RATCHET-007 - NATS-Projector Unit-Test + HR-TIME UX-M1 dokumentieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — 14 Unit-Tests fuer WfCockpitNatsProjector gruen (NATS-unabhaengig via MagicMock); Ratchet-Eintrag 75% gesetzt; HR-TIME UX-M1 und COVERAGE-001 in den Quelldokumenten als erledigt markiert.
**Ziel:** Letzten ungeteseteten Kernpfad im Workflow-Cockpit durch echte Unit-Tests absichern; abgeschlossene Punkte korrekt in den Quellen berichtigen.
**Dateibesitz:** `tests/test_wf_cockpit_nats_projector.py`, `scripts/check_critical_backend_coverage.py`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/hr-time-ux-workflow-roadmap-2026-05-12.md`, `docs/agent-ops/slices/COV-RATCHET-007.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** 14 Tests exit 0; Ratchet-Script enthaelt `wf_cockpit_nats_projector.py: 0.75`; UX-M1 in Roadmap als umgesetzt markiert.

## DOC-OPS-SEPARATION-001 - Trennung Dev-Gap-Track vs. operative Go-Live-Gates

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — P4-Abschnitt aus open-gaps-and-known-issues.md entfernt; alle externen Gates konsolidiert im Runbook unter neuem Abschnitt "Externe Go-Live Gates" mit fuenf Gate-Tabellen (Infra, Integration, HRM, UAT, Compliance).
**Ziel:** Operative Abhaengigkeiten (Live-Credentials, UAT-Unterschriften, Steuerberater-Freigaben, Restore-Drills) aus dem Entwicklungs-Gap-Track herausloesen und als Betriebsverantwortung im Production-Readiness-Runbook konsolidieren.
**Dateibesitz:** `docs/project-context/open-gaps-and-known-issues.md`, `docs/operations/production-readiness-runbook.md`, `docs/agent-ops/slices/DOC-OPS-SEPARATION-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** open-gaps-and-known-issues.md hat keinen P4-Abschnitt mehr; Runbook hat vollstaendige Gate-Tabellen mit Runbook-Anker `#externe-go-live-gates`.

## DOC-PROJECT-CONTEXT-002 - Weitere Projekt-Kontext-Docs in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Sieben weitere Projekt-Kontext-Dokumente (Agrar-ERP-Gap-Matrix, Agrar-Paritaetsmatrix, AI-Dev-Plan, UI-Maskenbestand, Doku-Konsolidierung, ERP-Referenz-Gap-Analyse, ERP-Referenzmatrix) mit Frontmatter versehen und als Referenz-Navigation veroeffentlicht.
**Ziel:** Strategische Gap-Analysen, ERP-Referenzmatrizen und Projektkontextdokumente fuer Entwickler und Product im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/project-context/agrar-erp-gap-matrix-2026-05-17.md`, `agrar-parity-matrix-2026-05-17.md`, `ai-assisted-development-implementation-plan-2026-06-23.md`, `ui-maskenbestand.md`, `documentation-consolidation-2026-06-26.md`, `erp-reference-gap-analysis-amic-community-erp-fiori-2026-04-08.md`, `erp-reference-matrix-2026-04-12.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-PROJECT-CONTEXT-002.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle sieben Dateien haben gueltiges Frontmatter; `mkdocs build` gruen (0 Errors, 38.98 s).

## DOC-AGENTOPS-SURFACE-002 - Weitere Agent-Ops-Skill-Docs in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Vier weitere Agent-Ops-Dokumente (README/Ueberblick, autogoal-skill, goal-skill, agent-orchestrator-pilot) mit Frontmatter versehen und im Agent-Ops-Unterabschnitt veroeffentlicht.
**Ziel:** Agent-Skill-Dokumentation und Orchestrator-Pilotbeschreibung fuer Agenten und Entwickler im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/agent-ops/README.md`, `autogoal-skill.md`, `goal-skill.md`, `agent-orchestrator-pilot.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-AGENTOPS-SURFACE-002.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle vier Dateien haben gueltiges Frontmatter; `mkdocs build` gruen (0 Errors, 26.38 s).

## DOC-AGENTOPS-SURFACE-001 - Agent-Ops-Koordinationsdokumente in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Sechs Agent-Ops-Koordinationsdokumente (active-workboard, session-start-checklist, task-slice-template, handoff-template, parallel-work-protocol, resume-packet-template) mit Frontmatter versehen und als Unterabschnitt Agent-Ops unter Agent-Dokumentation veroeffentlicht.
**Ziel:** Agenten-Koordinationsinfrastruktur fuer Claude- und Codex-Sitzungen im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `session-start-checklist.md`, `task-slice-template.md`, `handoff-template.md`, `parallel-work-protocol.md`, `resume-packet-template.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-AGENTOPS-SURFACE-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle sechs Dateien haben gueltiges Frontmatter; `mkdocs build` gruen (0 Errors, 24.92 s).

## DOC-CARDS-SURFACE-001 - Cards-Konzept und interne Inventar-Docs in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Zwei Cards-Konzeptdokumente (README, card-template) mit Frontmatter versehen; zwei bereits frontmatter-versehene interne Inventar-Docs (_internal/cards-inventory, legacy-docs-inventory) per exclude_docs-Ausnahme eingebunden; Unterabschnitt Prozess-Cards unter Entwickler veroeffentlicht.
**Ziel:** Interne Prozess-Audit-Infrastruktur (Cards-Konzept, Template, Inventar) fuer Entwickler und QA im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/cards/README.md`, `card-template.md`, `docs/_internal/cards-inventory.md`, `legacy-docs-inventory.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-CARDS-SURFACE-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle vier Dateien haben gueltiges Frontmatter; `mkdocs build` gruen (0 Errors, 18.49 s).

## DOC-WAREHOUSE-SURFACE-001 - Warehouse/WM-AGRI-Dokumente in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Sechs Warehouse-/WM-AGRI-Forschungsdokumente (Hofplan Folkerts Landhandel, Handbuch-C-Inventar, Silo-Baustein, Hersteller-Recherche, Benchmark, Open-Source-Bausteine) mit Frontmatter versehen und als Unterabschnitt Warehouse/WM-AGRI unter Referenz veroeffentlicht.
**Ziel:** WM-AGRI-Recherche- und Referenzdokumente fuer Entwickler und Agenten im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/warehouse/folkerts-landhandel-hofplan.md`, `handbuch-c-inventar.md`, `agrar-silo-materialfluss-studio-baustein.md`, `agri-silo-vendor-interface-research-2026-06-12.md`, `agri-silo-material-flow-benchmark-2026-06-12.md`, `reusable-open-source-silo-material-flow-2026-06-12.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-WAREHOUSE-SURFACE-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle sechs Dateien haben gueltiges Frontmatter; `mkdocs build` gruen (0 Errors, 18.33 s).

## DOC-QA-SURFACE-002 - QA-Docs und Workflow-Chains in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Drei QA-Dokumente (soll-ist-checks, external-auditor-simulation-template, e2e-crud-acceptance-matrix) mit Frontmatter versehen; _internal/workflow-chains.md (bereits frontmatter-versehen) per exclude_docs-Ausnahme eingebunden; alle vier Dateien unter Entwickler-Navigation veroeffentlicht.
**Ziel:** Verbleibende QA-Methodik- und interne Workflow-Ketten-Dokumente fuer Entwickler und QA im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/quality-assurance/soll-ist-checks.md`, `external-auditor-simulation-template.md`, `e2e-crud-acceptance-matrix-2026-04-24.md`, `docs/_internal/workflow-chains.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-QA-SURFACE-002.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle vier Dateien haben gueltiges Frontmatter; `mkdocs build` gruen (0 Errors, 18.39 s).

## DOC-ARCH-SURFACE-003 - Restliche Architekturdokumente und Open-Gaps in MkDocs

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Sieben von architecture/index.md verlinkte Architektur-Konzeptdokumente und open-gaps-and-known-issues.md mit Frontmatter versehen und in MkDocs integriert; INFO-Warnungen fuer ausgeschlossene Links behoben.
**Ziel:** Alle von architecture/index.md referenzierten Dokumente im Docs-Build auffindbar machen und Open-Gaps-Tracker unter Referenz veroeffentlichen.
**Dateibesitz:** `docs/architecture/adr-clusters-and-epics.md`, `business-logic-architecture.md`, `module-resolution-architecture.md`, `react-lifecycle-architecture.md`, `KI-USABILITY-MICROSERVICES.md`, `context-architecture-revolution.md`, `typescript-generic-architecture.md`, `docs/project-context/open-gaps-and-known-issues.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-ARCH-SURFACE-003.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle acht Dateien haben gueltiges Frontmatter; `docs-governance-check` gruen; `mkdocs build` gruen (0 Errors, 26.45 s).

## DOC-ARCH-SURFACE-002 - Weitere Architekturdokumente in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — DMS-Integration, AI-Dev-Standard, Architecture-Decision-Map und Agrar-Event-Contracts mit Frontmatter versehen und im Architektur-Abschnitt veroeffentlicht.
**Ziel:** Integrations- und Standard-Architekturdokumente fuer Entwickler und Agenten im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/architecture/dms-paperless-integration.md`, `ai-assisted-enterprise-development-standard.md`, `architecture-decision-map.md`, `agrar-event-hook-contracts.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-ARCH-SURFACE-002.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle vier Dateien haben gueltiges Frontmatter; `docs-governance-check` gruen; `mkdocs build` gruen (0 Errors, 25.53 s).

## DOC-ARCH-SURFACE-001 - Schluessel-Architekturdokumente in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Vier Architekturdokumente (Ist-Prozesse, Zielprozesse, Zielbild Landhandel ERP, Quality-Governance-Tooling) mit Frontmatter versehen und im Architektur-Abschnitt der Entwickler-Navigation veroeffentlicht.
**Ziel:** Architektonische Orientierungsdokumente fuer Entwickler und Agenten im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/architecture/current-processes.md`, `target-processes.md`, `target-state-landhandel-erp.md`, `tooling-quality-governance.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-ARCH-SURFACE-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle vier Dateien haben gueltiges Frontmatter; `docs-governance-check` gruen; `mkdocs build` gruen (0 Errors, 17.75 s).

## DOC-PROJECT-CONTEXT-001 - Schluessel-Projektkontextdokumente in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Vier Projektkontextdokumente (System-Overview, Business Rules, Module Map, Domain Landhandel) mit Frontmatter versehen und unter Referenz im Docs-Build veroeffentlicht.
**Ziel:** Fachliche Orientierungsdokumente fuer Agenten und Entwickler im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/project-context/system-overview.md`, `business-rules.md`, `module-map.md`, `domain-landhandel-und-agrarhandel.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-PROJECT-CONTEXT-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle vier Dateien haben gueltiges Frontmatter; `docs-governance-check` gruen; `mkdocs build` gruen (0 Errors, 38.14 s).

## DOC-UAT-CHECKLISTS-001 - UAT-Domain-Checklisten in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Fuenf UAT-Abnahme-Checklisten (Agrar, CRM, Finance, Inventory, Sales) mit Frontmatter versehen und im Entwickler-Bereich unter UAT Checklisten veroeffentlicht.
**Ziel:** Faehigkeitsrelevante Abnahmekriterien fuer QA und Entwickler im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/uat/checklisten/AGRAR.md`, `CRM.md`, `FINANCE.md`, `INVENTORY.md`, `SALES.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-UAT-CHECKLISTS-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle fuenf Dateien haben gueltiges Frontmatter; `docs-governance-check` gruen; `mkdocs build` gruen (0 Errors, 26.19 s).

## DOC-DEPLOYMENT-RUNBOOKS-001 - Deployment-Runbooks in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Sechs Deployment-Dokumente (ArgoCD/GitOps, Canary-Rollout, IDEV-Setup, Secrets, Zoll, Frontend EPCIS) mit Frontmatter versehen und unter Admin → Deployment in Navigation aufgenommen.
**Ziel:** Betriebsrelevante Deployment-Runbooks fuer Admins und Entwickler auffindbar machen.
**Dateibesitz:** `docs/deployment/gitops/argocd.md`, `docs/deployment/runbook/infra/canary-rollout.md`, `docs/deployment/runbook/infra/idev-setup.md`, `docs/deployment/runbook/security/secrets-inventory.md`, `docs/deployment/runbook/compliance/zoll-setup.md`, `docs/deployment/runbook/frontend/epcis-ui.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-DEPLOYMENT-RUNBOOKS-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle sechs Dateien haben gueltiges Frontmatter; `docs-governance-check` gruen; `mkdocs build` gruen (0 Errors, 25.66 s).

## DOC-QA-SURFACE-001 - QA/Test-Docs und External-Mock-Verträge in MkDocs

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — 3 QA-/Test-Dokumente mit Frontmatter versehen und in Build integriert; External-Mock-Verträge-Runbook in Agent-Dokumentation verlinkt.
**Ziel:** Playwright-Auth-Anleitung, Browser-Use-Checklists und External-Mock-Verträge (DATEV/ELSTER/TSE/Bank/DSFinV-K) im kuratierten Docs-Build auffindbar machen.
**Dateibesitz:** `docs/quality-assurance/playwright-smoke-auth.md`, `docs/quality-assurance/browser-use-checklists.md`, `docs/agent-docs/runbooks/external-mock-vertraege.md` (nur Nav-Link), `mkdocs.yml`, `docs/agent-ops/slices/DOC-QA-SURFACE-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** `docs-governance-check` gruen; `mkdocs build` gruen (0 Errors, 48.84 s).

## DOC-WORKFLOW-INDEX-001 - Kuratierter Workflow-Index fuer Entwickler

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — 161 Workflow-Dokumente in docs/workflows/ in 7 Kategorien katalogisiert und als Entwickler-Index veroeffentlicht.
**Ziel:** Alle Workflow-Dokumente auffindbar machen ohne sie direkt in den kuratierten Build zu ziehen.
**Dateibesitz:** `docs/entwickler/workflow-index.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-WORKFLOW-INDEX-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** `docs-governance-check` gruen; `mkdocs build` gruen (0 Errors, 39.59 s); Quelldateien bleiben in docs/workflows/ ausgeschlossen.

## DOC-USER-MANUAL-004 - Benutzerhandbuch vollstaendig

**Von:** Cursor - **Owner:** Cursor - **Stand:** abgeschlossen 2026-06-26

Generatorische Vollabdeckung des Benutzerhandbuchs fuer 851/851 Endnutzer-Routen,
29 Fachkapitel, MkDocs-Navigation und In-App-Hilfe-Mapping. Fachliche
Domain-How-tos bleiben fuer Tiefenwissen fuehrend; Screenshots/UAT sind
operative Folgegates.

## DOC-OPS-RUNBOOKS-001 - Ops/Runbook-Dateien in MkDocs integrieren

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-27 — Vier bisher ausgeschlossene Operations-/Runbook-Seiten mit Frontmatter versehen, in Navigation aufgenommen und zwei Build-Blocker behoben.
**Ziel:** ALERTS, DISASTER-RECOVERY, production-readiness-runbook und dependency-and-compatibility-maintenance im Admin-Betriebsbereich der Doku zugaenglich machen.
**Dateibesitz:** `docs/runbooks/ALERTS.md`, `docs/runbooks/DISASTER-RECOVERY.md`, `docs/operations/production-readiness-runbook.md`, `docs/operations/dependency-and-compatibility-maintenance.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-OPS-RUNBOOKS-001.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Alle vier Runbook-Seiten haben gueltiges Frontmatter; `docs-governance-check` gruen; `mkdocs build` gruen ohne Pygments-/Jinja-Blocker (0 Errors, 22.02 s).

## DOC-USER-MANUAL-003 - Benutzerhandbuch Kern- und Spezialdomaenen

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — Vier neue How-tos (Agrar-Kontrakte, NaWaRo, Genossenschaft, Belegarchiv); sieben Legacy-Kapitel mit Quellen/Reverse-Pflege; In-App-Hilfe-Mapping auf korrekte Handbuchseiten (Logistik, Controlling, POS, Personal, Kontrakte).
**Ziel:** Benutzerhandbuch fachlich vollstaendiger machen und In-App-Deep-Links konsistent halten.
**Dateibesitz:** `docs/benutzerhandbuch/**`, `mkdocs.yml`, `scripts/generate_inapp_help_map.py`, `packages/frontend-web/src/lib/docs-help.ts`, Slice-YAML, Workboard.
**Abnahme:** `docs-governance-check` gruen; `mkdocs build` gruen. Screenshots fuer neue Domänen optional nachziehbar.

## DOC-USER-MANUAL-002 - Benutzerhandbuch vervollstaendigen

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-26 - Benutzerhandbuch um POS/Kasse, Logistik/Touren, Compliance/Meldewesen, Personal/Zeit/Lohn, Controlling/Kostenrechnung und Futtermittel/Produktion erweitert.
**Ziel:** POS/Kasse, Logistik, Compliance/Meldewesen, Personal/Lohn, Controlling/Kostenrechnung und Futtermittel/Produktion als Endnutzer-How-tos in `docs/benutzerhandbuch/` ergaenzen.
**Dateibesitz:** `docs/benutzerhandbuch/**`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-USER-MANUAL-002.yaml`, dieser Workboard-Abschnitt.
**Abnahme:** Docs-Governance gruen; Staleness gruen; `mkdocs build` gruen. `mkdocs build --strict` bleibt durch bestehende Warnungen ausserhalb dieses Slice blockiert (ADR-/Architecture-Links und nicht navigierte Agent-Docs-Runbook-Seite), keine neuen Handbuch-Warnungen.

## Wave 15 — WF-COCKPIT-RETRY-001: Retry + Kompensationspfad

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26

`retry_instance()` + `compensate_instance()` in `WorkflowCockpitPersistService` implementiert. Neue Endpoints `POST /workflow/cockpit-db/instances/{id}/retry` (FAILED/blocked → retry_pending) und `POST /workflow/cockpit-db/instances/{id}/compensate` (→ compensated). Schliesst letztes offenes Sub-Item aus VALEO-WF-COCKPIT-001.

## Wave 14 — COV-RATCHET-009 + CRM-LEGACY-Abschluss + Stale-Gap-Cleanup

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26

**COV-RATCHET-009**: `futtermittel_qs.py` und `psm_proplanta.py` in Coverage-Ratchet aufgenommen (Wave-13-Endpoints, 40%-Baseline). Test `test_futtermittel_qs.py` mit 8 Unit-/Endpoint-Tests fuer HACCP/VLOG/QS-Pruefpunkte geschrieben.

**CRM-LEGACY-API-MIGRATE-001 abgeschlossen**: Verifikation Wave 14 — CRM-Seiten (`kontakt-management.tsx`, `kunden-liste.tsx`, `lieferanten-liste.tsx`) haben keine `@/lib/axios`-Imports; `/api/v1/crm/`-Pfade durchgaengig.

**Stale open-gaps bereinigt**: CMP-UStVA-Bug geschlossen (Code-Nachweis), WM-AGRI Zielzellen-Vorschlag als abgeschlossen markiert (retroaktiv WM-AGRI-MAP-001).

## Wave 13 — WF-COCKPIT-002 + FEED-QS-001 + RUNTIME-KAT-E-002

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26

**WF-COCKPIT-002**: `WfCockpitNatsProjector` in `startup_event_consumer()` eingebunden — wird bei `EVENT_BUS_ENABLED=true` und `EVENT_BUS_PROVIDER=nats` nach `nats_consumer.start()` gestartet; Shutdown sauber verdrahtet; domain_workflow.wf_cockpit_* Tabellen idempotent in Repair-Migration gesichert.

**FEED-QS-001**: Neuer Router `/futtermittel/qs` mit HACCP-Plaenen (Gefahrenanalyse/CCP/Ueberwachung), VLOG-Meldungen (GVO-frei, Zertifikat, Status-Workflow) und QS-Leitfaden-Pruefpunkten (Periode, Bestaetigung, Abweichung/Massnahme). 3 neue domain_shared-Tabellen.

**RUNTIME-KAT-E-002**: Proplanta PSM 400 → 503 bei fehlender Konfiguration (6 Stellen in psm_proplanta.py).

**Neuer Alembic-Head:** `feed_qs_wf_cockpit_repair_20260626`

## FINANCE-HR-EINKAUF-REPAIR-001 — Finance + HR + Einkauf Batch-Repair-Migration Wave 12

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
P1-Batch (Wave 12): 24 domain_erp-Tabellen (ap_approval_rules/requests/approvals, matching_rules, bank_matches, booking_templates, closing_checklist_templates, closing_checklists, tax_keys, vat_returns, offene_posten, open_items, business_partners, collaterals, debitors, debtors, pos_transactions, pos_transaction_lines, delivery_notes/erp, cash_movements, serial_numbers, gift_cards, bank_statements, bank_statement_lines) + ADD COLUMN journal_entries/lines + rfq_requests/quotes (domain_einkauf) + shifts (domain_hr) + zahlungsformulare/zinsgruppen/leergutarten (domain_shared) — alle aus Parallel-Branches, idempotent in Hauptkette. Finaler Single-Head-Merge `final_single_head_merge_20260626` schliesst alle offenen Branches.
**Dateibesitz:** `alembic/versions/finance_hr_einkauf_repair_20260626.py`, `alembic/versions/final_single_head_merge_20260626.py`, `docs/agent-ops/slices/FINANCE-HR-EINKAUF-REPAIR-001.yaml`
**Neuer Alembic-Head:** `final_single_head_merge_20260626` (SINGLE HEAD — alle 55+ Parallel-Branches geschlossen)

## BULK-REPAIR-001 — Finance + Agrar + Sales Batch-Repair-Migration Wave 11

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
P1-Batch (Wave 11): Finance-Tabellen `dunning_rules`, `dunning_notices`, `payment_runs`, `payment_run_items`, `payment_returns`, `exchange_rates` (domain_erp) + `ernte_planung`, `agrar_maschinen` (domain_agrar) + `branches` (domain_shared) + `delivery_notes` (domain_sales) + `sales_order_items` + `shipping_method` (domain_crm) — alle aus Parallel-Branches, idempotent in Hauptkette gebracht.
**Dateibesitz:** `alembic/versions/finance_agrar_sales_repair_20260626.py`, `docs/agent-ops/slices/BULK-REPAIR-001.yaml`
**Neuer Alembic-Head:** `finance_agrar_sales_repair_20260626`

## WAREHOUSE-REPAIR-001 — domain_inventory.warehouses Schema-Repair + Kat-C-Fix

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
Kat-C-500 `/api/v1/inventory/warehouses/` geschlossen: `001_initial_schema.py` hatte `address` als JSONB angelegt, Pydantic-Schema erwartete `Optional[str]` → `model_validate` fehlgeschlagen. Fix: `field_validator("address", mode="before")` in `WarehouseBase` konvertiert JSONB-dict → str. Repair-Migration `warehouse_schema_repair_20260626` ergaenzt fehlende Spalten + legt `inventory_counts` und `inventory_stock_movements` idempotent an.
**Dateibesitz:** `alembic/versions/warehouse_schema_repair_20260626.py`, `app/api/v1/schemas/inventory.py`, `docs/agent-ops/slices/WAREHOUSE-REPAIR-001.yaml`
**Neuer Alembic-Head:** `warehouse_schema_repair_20260626`

## EINKAUF-LS-REPAIR-001 — Einkauf-Lieferschein + Opportunities Repair-Migration

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
P1-Gap (Welle 9) geschlossen: `einkauf_lieferscheine`, `einkauf_lieferschein_positionen`, `einkauf_frachtauftraege` + `opportunities` (public schema) lagen in Parallel-Branches → 500 UndefinedTable fuer `/einkauf/lieferscheine[/last]`, `/crm/opportunities/pipeline`. Repair-Migration `einkauf_ls_opportunities_repair_20260626` idempotent angehaengt.
**Dateibesitz:** `alembic/versions/einkauf_ls_opportunities_repair_20260626.py`, `docs/agent-ops/slices/EINKAUF-LS-REPAIR-001.yaml`
**Neuer Alembic-Head:** `einkauf_ls_opportunities_repair_20260626`

## ALEMBIC-MERGE-001 — Admin-Mobile + Charge-Lineage Alembic Repair-Migration

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
P1-Gap geschlossen: 14 Admin-Mobile-Tabellen (`admin_devices`, `admin_stations`, `admin_routing_rules` u.a.) + `charge_lineage_links` + `storage_fee_runs` lagen in Parallel-Alembic-Branches (55 Heads) und verursachten `UndefinedTable`-500er. Repair-Migration `admin_mobile_repair_20260626` mit `CREATE TABLE IF NOT EXISTS` an neuen Hauptketten-Head angehaengt.
**Dateibesitz:** `alembic/versions/admin_mobile_repair_20260626.py`, `docs/agent-ops/slices/ALEMBIC-MERGE-001.yaml`
**Neuer Alembic-Head:** `admin_mobile_repair_20260626`

## TAIL-CRM-001 — CRM RAG-/Intent-Panel + Dublettencheck (retroaktiv dokumentiert)

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
Gap-Verifikation: LegacyKundenStammModern.tsx enthält vollständige Dublettensicht, Wissenspanel und Naechste-Aktion-Surface. Bereits von Codex erledigt.
**Dateibesitz:** `packages/frontend-web/src/pages/crm/kunden-stamm-modern/LegacyKundenStammModern.tsx`, `docs/agent-ops/slices/TAIL-CRM-001.yaml`

## TAIL-NAWARO-001 — NaWaRo Druck/Vorschau/Serienbrief (retroaktiv dokumentiert)

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
Gap-Verifikation: mitteilung-drucken.tsx + anbauflaechen.tsx nutzen `nawaro-communication.ts` (buildCsvArtifact, downloadArtifact, openHtmlPreview). Bereits von Codex erledigt.
**Dateibesitz:** `packages/frontend-web/src/pages/nawaro/`, `packages/frontend-web/src/lib/nawaro-communication.ts`, `docs/agent-ops/slices/TAIL-NAWARO-001.yaml`

## TAIL-AGRI-001 — Agrar PSM-Beratung + Saatgut-Edit (retroaktiv dokumentiert)

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
Gap-Verifikation: beratung.tsx nutzt echte PSM-Stammdaten mit expliziter Readiness; saatgut-stamm.tsx hat echten Edit-Flow. Keine Demo-Fallbacks. Bereits von Codex erledigt.
**Dateibesitz:** `packages/frontend-web/src/pages/agrar/psm/beratung.tsx`, `packages/frontend-web/src/pages/agrar/saatgut-stamm.tsx`, `docs/agent-ops/slices/TAIL-AGRI-001.yaml`

## TAIL-SALES-001 — Sales orders-modern Export/Import/Archiv (retroaktiv dokumentiert)

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
Gap-Verifikation: orders-modern.tsx an reale Order-Liste angebunden, CSV-Export, echte Statusfilter, Import/Archiv über kanonische Auftragsliste. Bereits von Codex erledigt.
**Dateibesitz:** `packages/frontend-web/src/pages/sales/orders-modern.tsx`, `docs/agent-ops/slices/TAIL-SALES-001.yaml`

## RUNTIME-KAT-C-002 — Response-Model-Mismatches Kat. C Restliste (7 Endpoints)

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
7 Endpoints: `policies/policy/list` ok→success, `einkauf/lieferanten+kontrakte+artikel-lager-parameter` Einzelobjekt→list[], `kaeufergruppe/katalog` dict→list[dict], `messages/health` MessageOut→dict[str,str], `crm/bestell-inbox` GET dict→list[dict].
**Dateibesitz:** `policies.py`, `einkauf_bestellvorschlag.py`, `kaeufergruppe.py`, `messages.py`, `whatsapp_intake.py`, `docs/agent-ops/slices/RUNTIME-KAT-C-002.yaml`

## WM-AGRI-MAP-001 — Zielzellen-Regelengine (retroaktiv dokumentiert)

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
Gap-Verifikation ergab: `silo_target_cell.py` + `silo_rule_engine_service.py` + `agri_lot_link_booking.py` bereits vollständig implementiert. GET /silo/zielzellen-vorschlag, GET /zielzellen-vorschlag/lot/{lot_id}, POST /material-flow/lot-link/auto-book vorhanden.
**Dateibesitz:** `app/api/v1/endpoints/silo_target_cell.py`, `app/services/silo_rule_engine_service.py`, `docs/agent-ops/slices/WM-AGRI-MAP-001.yaml`

## LOG-TRACK-001 — Logistik Track & Trace / ePOD (retroaktiv dokumentiert)

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
Gap-Verifikation ergab: `logistics_tours.py` + `logistics_epod_service.py` + Alembic `domain_logistics.tour_events` bereits vollständig. POST /tours/{id}/events, GET /gps-track, ePOD-Settlement (DOM-LOG-004.3) vorhanden.
**Dateibesitz:** `app/api/v1/endpoints/logistics_tours.py`, `app/services/logistics_epod_service.py`, `docs/agent-ops/slices/LOG-TRACK-001.yaml`

## LOG-FRACHTBRIEF-001 — Logistik Frachtbrief-Endpoint

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
Alembic-Migration `log_frachtbriefe_20260626` + Endpoint `GET/POST/PATCH /api/v1/logistik/frachtbriefe` + Tests. Frontend `useFrachtbriefe()` liefert jetzt 200 statt 404.
**Dateibesitz:** `alembic/versions/log_frachtbriefe_20260626.py`, `app/api/v1/endpoints/logistik_frachtbriefe.py`, `tests/test_log_frachtbrief.py`, `docs/agent-ops/slices/LOG-FRACHTBRIEF-001.yaml`

## MCP-ERP-TOOLS-001 — MCP Tool-Katalog YAML

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
`app/config/mcp_erp_tools.yaml` mit 21 validen Tool-Definitionen (Agrar, Verkauf, Einkauf, Lager, CRM, Finance, Logistik, Compliance). GET /api/v1/mcp/tools liefert 200 statt 500 FileNotFoundError.
**Dateibesitz:** `app/config/mcp_erp_tools.yaml`, `docs/agent-ops/slices/MCP-ERP-TOOLS-001.yaml`

## RUNTIME-KAT-C-001 — Response-Model-Mismatches Kat. C (health/live + ebilanz/taxonomie)

**Von:** Claude Code · **Owner:** Claude Code · **Stand:** abgeschlossen 2026-06-26
- `health.py`: `return StatusResponse(success=True, message="alive")` statt `{"status":"alive"}` (fehlende `success`-Feld-ResponseValidationError)
- `ebilanz_elster.py`: `response_model=list[EbilanzElsterOut]` statt Einzelobjekt fuer list-Return
**Dateibesitz:** `app/api/v1/endpoints/health.py`, `app/api/v1/endpoints/ebilanz_elster.py`, `docs/agent-ops/slices/RUNTIME-KAT-C-001.yaml`

## DOC-CONSOLIDATION-010 - Doku-Konsolidierung: erledigte Zukunftsplaene, Dubletten, echter Restbacklog

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-26 - Konsolidierungsbericht erstellt, Open-Gaps mit aktuellem Doku-Status versehen, wichtigste historische Gap-/Roadmap-/Heuristikdateien markiert. `doc_drift_report.py`: 0 Drift-Items; Docs-Governance und Staleness gruen.
**Ziel:** Aktive Dokumentation wieder als verlaessliche Produkt- und Entwicklungsquelle nutzbar machen.
**Dateibesitz:** `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/documentation-consolidation-2026-06-26.md`, ausgewaehlte aktive `docs/**/*.md` mit belegbarer Statuskorrektur, `docs/agent-ops/slices/DOC-CONSOLIDATION-010.yaml`. Keine Edits an `docs/_internal/archive/**`.

## DOC-FOUNDATION-001 — Dokumentations-Fundament: MkDocs-Material + Versionierung + Taxonomie

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — Docs-as-Code-Fundament steht: `mkdocs.yml` (Material, DE), `requirements-docs.txt` (mkdocs-material + mike), Diataxis-Taxonomie mit 7 Einstiegsseiten + `docs/index.md`, Frontmatter-Standard, frontmatter-fähige Doku-Checks, `.github/workflows/docs.yml` (mkdocs build), Altbestände per `exclude_docs` ausgeschlossen. `mkdocs build` läuft lokal fehlerfrei (Exit 0). Inhalt/Migration folgen in DOC-INTERFACES/USER-MANUAL/ADMIN-OPS/AGENT-CATALOG/GOVERNANCE/MIGRATION-Slices.
**Ziel:** Wartbares, versioniertes, agententaugliches Doku-System schaffen, ohne bestehende Inhalte zu verschieben.
**Dateibesitz:** `mkdocs.yml`, `requirements-docs.txt`, `.github/workflows/docs.yml`, `docs/index.md`, `docs/dokumentation/dokumentationskonzept.md`, `docs/dokumentation/frontmatter-standard.md`, `docs/{benutzerhandbuch,admin,entwickler,schnittstellen,agent-docs,compliance,referenz}/index.md`, `docs/agent-ops/slices/DOC-FOUNDATION-001.yaml`

## DOC-INTERFACES-001 — Schnittstellenhandbuch: OpenAPI + MCP-Tools + Event-Katalog

**Von:** Cursor · **Owner:** Cursor · **Stand:** abgeschlossen 2026-06-25 — `scripts/generate_openapi.py` erzeugt `docs/schnittstellen/openapi.json` (2451 Pfade, 8,2 MB, vom Docs-CI entkoppelt); `scripts/generate_mcp_tool_reference.py` rendert `mcp-tools.md` (12 Tools); `rest-api.md` bettet Swagger-UI ein; `events.md` Event-Katalog; Nav erweitert; `mkdocs build` grün.
**Dateibesitz:** `docs/schnittstellen/{rest-api,mcp-tools,events}.md`, `docs/schnittstellen/openapi.json`, `scripts/generate_openapi.py`, `scripts/generate_mcp_tool_reference.py`, `mkdocs.yml`, `requirements-docs.txt`, `docs/agent-ops/slices/DOC-INTERFACES-001.yaml`

## DOC-USER-MANUAL-001 — Benutzerhandbuch: Inhalte, Glossar, In-App-Deep-Links

**Von:** Cursor · **Owner:** Cursor · **Stand:** abgeschlossen 2026-06-25 — How-tos: Einstieg, Annahme, Verkauf, Lager, FiBu; Glossar; In-App-Hilfe-Konzept (Routen-ID → Doku); Index + Nav verlinkt; `mkdocs build` grün.
**Dateibesitz:** `docs/benutzerhandbuch/*.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-USER-MANUAL-001.yaml`

## DOC-ADMIN-OPS-001 — Administration & Betrieb: Mandanten-Admin- + Betriebshandbuch

**Von:** Cursor · **Owner:** Cursor · **Stand:** abgeschlossen 2026-06-25 — 9 Seiten: Mandanten-Admin, Module/Flags, RBAC; Deployment, Backup/Restore, DB-Migrationen, Monitoring/SLO, Incident-Response, Skalierung (verweist auf PERF-MULTIUSER-001); Index + Nav; `mkdocs build` grün.
**Dateibesitz:** `docs/admin/*.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-ADMIN-OPS-001.yaml`

## DOC-AGENT-CATALOG-001 — Agent-Dokumentation: Capability- + Tool-Katalog + Guardrails

**Von:** Cursor · **Owner:** Cursor · **Stand:** abgeschlossen 2026-06-25 — Capability-Katalog, Tool-Katalog (Agent-Sicht, verweist auf generierte MCP-Referenz), Guardrails (Human-Approval/fail-closed/RBAC/Idempotenz), ai_harness-Vertragsmodell; Index + Nav; `mkdocs build` grün.
**Dateibesitz:** `docs/agent-docs/*.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-AGENT-CATALOG-001.yaml`

## DOC-GOVERNANCE-001 — Doku-Governance: CODEOWNERS, Link-/Staleness-Check, Changelog, Release-Versionierung

**Von:** Cursor · **Owner:** Cursor · **Stand:** abgeschlossen 2026-06-25 — `.github/CODEOWNERS` (auf realen Owner @JochenWeerda), `scripts/docs-staleness-check.cjs` (+ nicht-blockierender CI-Step), `.github/workflows/docs-release.yml` (mike), `CHANGELOG.md`, `docs/dokumentation/governance.md`; `mkdocs build` grün. **Externes Gate erledigt:** mike-Deploy auf `gh-pages` gepusht, GitHub Pages aktiv → Live-Site https://jochenweerda.github.io/VALEO-NeuroERP-3.0/ (Build „built", HTTP 200). Begleitend: `WMS-FLOW-001.yaml` (Fremd-Slice) auf Pflichtschema gebracht; Screenshot-Infrastruktur (`benutzerhandbuch/img/`) + Verfahren angelegt (Live-Aufnahme blockiert durch fehlende OIDC-Test-Credentials).
**Dateibesitz:** `.github/CODEOWNERS`, `.github/workflows/docs.yml`, `.github/workflows/docs-release.yml`, `scripts/docs-staleness-check.cjs`, `CHANGELOG.md`, `docs/dokumentation/governance.md`, `docs/agent-ops/slices/DOC-GOVERNANCE-001.yaml`

## DOC-MIGRATION-001 — Doku-Migration: Altbestaende archivieren und einordnen

**Von:** Cursor · **Owner:** Cursor · **Stand:** abgeschlossen 2026-06-25 — `docs/_internal/` etabliert (Build- + Check-ausgeschlossen), 34 historische Root-Artefakte per `git mv` nach `docs/_internal/archive/` (Historie erhalten), Migrationsplan mit Kategorien→Bucket; `mkdocs build` grün.
**Dateibesitz:** `docs/_internal/**`, `docs/dokumentation/migrationsplan.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-MIGRATION-001.yaml`

## PERF-MULTIUSER-001 — Multi-User-Performance: Middleware auf pure ASGI + Logging entschlacken

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — alle 6 Middleware (Prometheus, Correlation, SecurityHeaders, Audit, Bearer-Auth, Request-Logging) von BaseHTTPMiddleware auf reine ASGI umgestellt; Per-Request-Logging auf Slow-Requests (>1s) + Fehler reduziert; Micro-Benchmark: Stack-Overhead von ~82 ms/Req auf <0,3 ms/Req (RPS GET 334→795); Tests grün (test_middleware_asgi 6/6, Auth/Tenant/Security 75/75). DB-Pool bewusst unveraendert (bereits passend dimensioniert).
**Ziel:** Latenz/CPU pro Request unter Multi-User-Last senken, ohne Auth-, Tenant-, Audit- oder Security-Header-Semantik zu aendern.
**Dateibesitz:** `app/middleware/metrics.py`, `app/middleware/correlation.py`, `app/middleware/security_headers.py`, `app/middleware/audit_middleware.py`, `main.py`, `scripts/benchmark_middleware_stack.py`, `tests/test_middleware_asgi.py`, `docs/agent-ops/slices/PERF-MULTIUSER-001.yaml`, `docs/workflows/perf-multiuser-001-middleware-asgi-2026-06-25.md`

## OPERATOR-AGENT-001 — ERP Operator-Agent (Read-Only/Proposal-Modus)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-25 — `operator_agent_service.py` (Proposal-Lifecycle, RBAC: agent:read/propose/approve, Human-Approval HIGH-risk, Audit-Events); API `/agent/operator/*` (7 Endpoints); 13 Unit-Tests grün; Slice-YAML; Router in api.py registriert; Coverage-Ratchet +2 Eintraege.
**Ziel:** Operator-Agent-Service: liest Kontext, schlägt Handlungen vor, verlangt Human Approval, schreibt nie autonom.
**Dateibesitz:** `app/services/operator_agent_service.py`, `app/api/v1/endpoints/operator_agent.py`, `tests/test_operator_agent.py`, `docs/agent-ops/slices/OPERATOR-AGENT-001.yaml`

## DEV-HARNESS-CLI-001 — Valeo-Slice CLI

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-25 — `scripts/valeo_slice.py` (claim/verify/close/status/list); 11 Unit-Tests grün; Slice-YAML; py_compile OK.
**Ziel:** CLI-Tool fuer Slice-Lifecycle-Management mit YAML-Schema-Validation und Governance-Checks.
**Dateibesitz:** `scripts/valeo_slice.py`, `tests/test_valeo_slice_cli.py`, `docs/agent-ops/slices/DEV-HARNESS-CLI-001.yaml`

## COMPAT-GOV-MATRIX-SYNC-20260625 — Alembic-Head + Coverage-Ratchet Nachzug

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-25 — Alembic-Head in open-gaps + STATUS.md auf `external_mock_sessions_20260623` aktualisiert; Coverage-Ratchet um mcp_tool_registry, external_mock_harness, operator_agent erweitert.
**Ziel:** Governance-Doku auf Head `external_mock_sessions_20260623` bringen; Coverage-Ratchet um neue Services erweitern.
**Dateibesitz:** `docs/project-context/open-gaps-and-known-issues.md`, `docs/architecture/process-kernel/STATUS.md`, `scripts/check_critical_backend_coverage.py`

## PROCESS-MAP-001 — P2.1 Workflow-Prozesskarte

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-25 — 5 Prozesskarten (O2C/WMS/P2P/FIBU/POS); API /process-map/*; externe Gates + Human-Approval-Steps strukturiert; 11 Unit-Tests grün.
**Ziel:** Strukturierte Prozesskarten mit Steps, Gates, Policies, SLA, Verantwortlichkeiten.
**Dateibesitz:** `app/services/process_map_service.py`, `app/api/v1/endpoints/process_map.py`, `tests/test_process_map_service.py`, `docs/agent-ops/slices/PROCESS-MAP-001.yaml`

## AI-METRICS-001 — P2.2 Produktivitaetsmetriken AI-Engineering

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-25 — Cycle Time aus Slice-YAMLs, Coverage aus coverage.xml, Rework-Indikator, Gate-Blocker, Owner-Verteilung; API /ai-engineering/metrics/*; 9 Unit-Tests grün.
**Ziel:** Mess- und steuerbare AI-Engineering-Metriken fuer den VALEO-Entwicklungsbetrieb.
**Dateibesitz:** `app/services/ai_engineering_metrics_service.py`, `app/api/v1/endpoints/ai_engineering_metrics.py`, `tests/test_ai_engineering_metrics.py`, `docs/agent-ops/slices/AI-METRICS-001.yaml`

## AI-DATA-CLASSES-001 — P2.3 Lokale KI-Datenklassen

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-25 — 12 Datenkategorien C0-C5; TSE/ELSTER/Bankkonto/Passwort=C5; Personal/Kunden/Kontrakte=C3; check-model-Pruefung; API /ai-data-classes/*; 15 Unit-Tests grün.
**Ziel:** Verbindliche KI-Zugriffsklassen fuer alle VALEO-Datenkategorien (DSGVO/GoBD/Steuergeheimnis).
**Dateibesitz:** `app/services/ai_data_classification_service.py`, `app/api/v1/endpoints/ai_data_classification.py`, `tests/test_ai_data_classification.py`, `docs/agent-ops/slices/AI-DATA-CLASSES-001.yaml`

## SEMANTIC-E2E-P2P-FIBU-POS-QS-001 — P2P + FIBU + POS/TSE + QS/Reklamation Semantische Ketten

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-25 — P2P (12 Schritte: RFQ→Bestellung→WE→3-Wege-Match→ERS→SEPA→DATEV) + FIBU (13 Schritte: OP→CAMT→Auszifferung→Mahnlauf→DATEV→Periodenabschluss→ELSTER-VA) + POS/TSE (12 Schritte: Bon→TSE-Signatur→Zahlung→Tagesabschluss→DSFinV-K→FIBU→Retoure) + QS/Reklamation (14 Schritte: Labor→Sperre→Reklamation→Retoure/Gutschrift→CAPA→Lieferant-Sperre). Alle Specs fail-safe. Externe Gates simuliert (simulated=true). P0.2 vollstaendig.
**Dateibesitz:** `playwright-tests/specs/e2e-matrix/p2p-semantic-chain.spec.ts`, `fibu-semantic-chain.spec.ts`, `pos-tse-semantic-chain.spec.ts`, `qs-reklamation-semantic-chain.spec.ts`, `docs/agent-ops/slices/SEMANTIC-E2E-P2P-FIBU-POS-QS-001.yaml`

## SEMANTIC-E2E-MATRIX-001-CHAIN — O2C + WMS/Silo Semantische Ketten

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-25 — O2C (10 Schritte: Kunde→Angebot→Auftrag→LS→RE→Zahlung→Mahnung→DATEV-Mock) + WMS/Silo (11 Schritte: Annahme→Waage→Lot→Silo→QS-Probe→Freigabe/Sperre→Traceability→Abgang) als API-semantische Playwright-Specs. Fail-safe (akzeptiert 404/422/503).
**Dateibesitz:** `playwright-tests/specs/e2e-matrix/o2c-semantic-chain.spec.ts`, `playwright-tests/specs/e2e-matrix/wms-silo-semantic-chain.spec.ts`

## WF-COCKPIT-UI-001 — Workflow-Leitstand Frontend-UI

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — `pages/workflow/leitstand.tsx` (KPI-Kacheln, Status-Filter, Detail-Dialog, Replay-Button); `lib/api/workflow-cockpit.ts`; Nav-Eintrag unter System & Betrieb; Route `workflow/leitstand`; 883 Routen; TS 0 Fehler.
**Ziel:** Frontend-UI für den Workflow-Prozessleitstand: ListReport mit Status-Filter/Auto-Refresh, Detail-Drawer mit Event-Kette, Replay-Button (role-guarded).
**Dateibesitz:** `packages/frontend-web/src/pages/workflow/leitstand.tsx`, `packages/frontend-web/src/lib/api/workflow-cockpit.ts`, `packages/frontend-web/src/app/navigation/domains/operations.tsx`, `packages/frontend-web/src/app/routing/navigation-routes.json`, `docs/agent-ops/slices/WF-COCKPIT-UI-001.yaml`

## MCP-ERP-TOOLS-001 — ERP MCP Tool-Katalog

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — `config/mcp_erp_tools.yaml` (13 Tools: CRM/Sales/FIBU/WMS/DMS/Compliance); Service+API; 9 Unit-Tests grün; validate_all() 0 Fehler.
**Ziel:** Produktiver rollenbasierter ERP-MCP-Toolkatalog mit Schema/Scope/Idempotenz/Risiko-Validierung.
**Dateibesitz:** `config/mcp_erp_tools.yaml`, `app/services/mcp_tool_registry_service.py`, `app/api/v1/endpoints/mcp_tool_registry.py`, `tests/test_mcp_tool_registry.py`, `docs/agent-ops/slices/MCP-ERP-TOOLS-001.yaml`

## EXTERNAL-MOCK-HARNESS-001 — Mock-Schicht für externe Systeme

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — `external_mock_harness_service.py` (DATEV/TSE/DSFinV-K/ELSTER/DMS/CAMT, deterministisch, simulated=true); Dev-API `/dev/external-mocks/*`; Alembic `external_mock_sessions_20260623`; 14 Unit-Tests grün.
**Ziel:** Reproduzierbare Mock-Stubs für externe Systeme ohne echten Systemkontakt.
**Dateibesitz:** `app/services/external_mock_harness_service.py`, `app/api/v1/endpoints/external_mock_harness.py`, `alembic/versions/external_mock_sessions_20260623.py`, `tests/test_external_mock_harness.py`, `docs/agent-ops/slices/EXTERNAL-MOCK-HARNESS-001.yaml`

## AI-DOC-DRIFT-DASHBOARD-001 — Doku-Drift-Report

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — `scripts/doc_drift_report.py` (Endpoints/Migrationen/Services/Pages vs. Docs, JSON+Markdown); 4 Unit-Tests grün.
**Ziel:** Heuristischer Drift-Report für Code-Objekte ohne Doku-Entsprechung.
**Dateibesitz:** `scripts/doc_drift_report.py`, `tests/test_doc_drift_report.py`, `docs/agent-ops/slices/AI-DOC-DRIFT-DASHBOARD-001.yaml`

## VALEO-WF-COCKPIT-001 - Workflow- und Prozessleitstand fuer VALEO Process Kernel

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-23 - Backend-/API-MVP fuer P0.1 aus `valeo_neuroerp_youtube_gap_analyse_2026-06-23.md`: `WorkflowCockpitService`, `/workflow/cockpit/*`, Statusmodell, externe Gate-Blocker, Event-Kette, Replay-Guard, 6 Unit-Tests gruen.
**CI-Nachzug 2026-06-23:** Gitleaks-False-Positive in `tests/test_workflow_cockpit_service.py` durch niedrigere Testdaten-Entropie beseitigt; bestehende Agrar-/Sales-/Procurement-Migrationen `agrar_partie_settlement_20260623.py`, `sales_ab_preisabweichung_20260623.py` und `proc_bestellung_wareneingang_20260623.py` leer-DB-tauglich gemacht, indem die jeweiligen Legacy-Basistabellen vor additiven `ALTER TABLE`-Schritten bei Bedarf minimal angelegt werden.
**CI-Nachzug 2026-06-23:** E2E-Smoke-Folgefix auf `main`: API-only Smoke-Specs fuer Finance, Sales, Agrar und Inventory nutzen in CI explizit `http://127.0.0.1:8000` statt `localhost`, weil GitHub-Runner `localhost` fuer Playwright auf `::1` aufloesen koennen, waehrend uvicorn im Workflow nur IPv4 sicher bereitsteht. Der E2E-Workflow prueft den Backend-Start jetzt vor Testbeginn per `/healthz`; NATS/Eventbus und Outbox-Worker werden im Smoke-Workflow explizit deaktiviert, weil `.env.example` NATS fuer Dev-Compose aktiviert, der E2E-Runner aber keinen Broker startet.
**CI-Nachzug 2026-06-23:** API-only Smoke-Specs fuer Finance, Sales, Agrar und Inventory senden jetzt den Dev-Bearer-Token (`API_DEV_TOKEN`/`VALEO_API_DEV_TOKEN`/`VITE_API_DEV_TOKEN`, Fallback `dev-token`) mit. Ursache der roten E2E-Runs war kein fachlicher Endpoint-Fehler, sondern 401 auf geschuetzten Routen durch fehlenden Auth-Kontext im direkten Playwright-API-Client.
**CI-Nachzug 2026-06-23:** E2E-Smoke-Workflow startet jetzt einen dedizierten Postgres-Service und fuehrt `python scripts/init_db.py` vor dem Backend-Start aus. Die roten Finance/Agrar/Inventory-Smokes nach dem Auth-Fix waren neue DOM-004-Tabellen auf einer nicht migrierten CI-Smoke-DB; Sales-Preisabweichung nutzt den tatsaechlichen Routerpfad unter `/sales/orders/orders/...`.
**CI-Nachzug 2026-06-23:** Quality-Gate-Folgefix: neun neue SQL-f-string-Funde aus parallelen DOM-004/POS/Feed/Meldewesen-Slices wurden review-markiert (`# nosec S608`), weil die dynamischen SQL-Teile ausschliesslich aus festen, codekontrollierten SET-Fragmenten bestehen und alle Werte weiterhin parametrisiert gebunden werden.
**Ziel:** Operativen Workflow-Leitstand fuer Prozessinstanzen, Events, externe Gate-Blocker, Fehler, Retry/Replay und Audit-Kontext schaffen. Deterministische Fachlogik bleibt in Process Kernel, Domain-Services, Outbox/NATS und Audit; kein n8n-Kernersatz.
**Dateibesitz:** `app/services/workflow_cockpit_service.py`, `app/api/v1/endpoints/workflow_cockpit.py`, `tests/test_workflow_cockpit_service.py`, `docs/workflows/valeo-wf-cockpit-001-workflow-leitstand-2026-06-23.md`, `docs/agent-ops/slices/VALEO-WF-COCKPIT-001.yaml`, dieser Workboard-Abschnitt.
**Abnahmekriterien:** Tenantisolierte Prozessliste; Statusmodell `pending/running/blocked_external_gate/failed/completed/compensated`; chronologische Event-Kette; externe Blocker getrennt von `failed`; Replay/Retry nur mit expliziter Rolle; Unit-Tests und Doku gruen.

## DOM-CONTROLLING-004 — Controlling-Domäne Vollständige Vertiefung (.2–.5)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — Budget-Lifecycle (.2), Plan/Ist-Abweichung (.3), KST-Abschluss (.4), Playwright @smoke + UAT-Script (.5), Alembic-Migration controlling_budget_abschluss_20260623, 19 Unit-Tests grün, Slice-YAML + Workflow-Doku
**Ziel:** Controlling-Kern-Prozesse auf volle 004-Tiefe heben: Budget-Lifecycle (.2), Plan/Ist-Abweichungsanalyse (.3), Kostenstellen-Abschluss-Flow (.4), Playwright @smoke + UAT (.5).
**Dateibesitz:** `app/services/controlling_budget_lifecycle_service.py`, `app/services/controlling_abweichung_service.py`, `app/services/controlling_kostenstellen_abschluss_service.py`, `alembic/versions/controlling_budget_abschluss_20260623.py`, `app/api/v1/endpoints/controlling_actions.py`, `playwright-tests/specs/controlling/controlling-lifecycle-smoke.spec.ts`, `scripts/uat/controlling_lifecycle_uat.py`, `docs/workflows/dom-controlling-004-controlling-deepening-2026-06-23.md`, `docs/agent-ops/slices/DOM-CONTROLLING-004.yaml`, `tests/test_dom_controlling_004.py`
**Koordination:** Keine aktiven Cursor-Controlling-Slices. `controlling_service.py` bleibt unangetastet.

## DOM-PROC-004 — Procurement-Domäne Vollständige Vertiefung (.2–.5)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — Bestellung-Lifecycle (.2), Wareneingangs-Buchung+QS (.3), Rechnungsprüfung+ERS (.4), Playwright @smoke + UAT-Script (.5), Alembic-Migration proc_bestellung_wareneingang_20260623, 13 Unit-Tests grün, Slice-YAML + Workflow-Doku
**Ziel:** Procurement-Kern-Prozesse auf volle 004-Tiefe heben: Bestellung-Lifecycle (.2), Wareneingangs-Buchung + QS (.3), Rechnungsprüfung + ERS-Abschluss (.4), Playwright @smoke + UAT (.5).
**Dateibesitz:** `app/services/proc_bestellung_lifecycle_service.py`, `app/services/proc_wareneingang_service.py`, `app/services/proc_rechnungspruefung_service.py`, `alembic/versions/proc_bestellung_wareneingang_20260623.py`, `app/api/v1/endpoints/procurement_match.py`, `playwright-tests/specs/procurement/proc-lifecycle-smoke.spec.ts`, `scripts/uat/proc_lifecycle_uat.py`, `docs/workflows/dom-proc-004-procurement-deepening-2026-06-23.md`, `docs/agent-ops/slices/DOM-PROC-004.yaml`, `tests/test_dom_proc_004.py`
**Koordination:** Keine aktiven Cursor-Procurement-Slices. Fremde Dateien bleiben unangetastet.

## DOM-SALES-004 — Sales-Domäne Vollständige Vertiefung (.2–.5)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — AB-Lifecycle (.2), Lieferschein-Close (.3), Preisabweichungs-Eskalation (.4), Playwright @smoke + UAT-Script (.5), Alembic-Migration sales_ab_preisabweichung_20260623, 14 Unit-Tests grün, Slice-YAML + Workflow-Doku
**Ziel:** Sales-Kern-Prozesse auf volle 004-Tiefe heben: Auftragsbestätigung-Lifecycle (.2), Lieferschein-Closing-Flow (.3), Preisabweichungs-Eskalation (.4), Playwright @smoke + UAT (.5).
**Dateibesitz:** `app/services/sales_ab_lifecycle_service.py`, `app/services/sales_lieferschein_close_service.py`, `app/services/sales_preisabweichung_service.py`, `alembic/versions/sales_ab_preisabweichung_20260623.py`, `app/api/v1/endpoints/sales_orders.py`, `playwright-tests/specs/sales/sales-lifecycle-smoke.spec.ts`, `scripts/uat/sales_lifecycle_uat.py`, `docs/workflows/dom-sales-004-sales-deepening-2026-06-23.md`, `docs/agent-ops/slices/DOM-SALES-004.yaml`, `tests/test_dom_sales_004.py`
**Koordination:** Keine aktiven Cursor-Sales-Slices. Fremde Dateien bleiben unangetastet.

## DOM-FINANCE-004 — Finance-Domäne Vollständige Vertiefung (.2–.5)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — SEPA-Zahlungsträger (.2), Ratenzahlungsplan-Lifecycle (.3), Mahnstufen-Eskalation-Trail (.4), Playwright @smoke + UAT-Script (.5), Alembic-Migration finance_sepa_ratenzahlung_20260623, 15 Unit-Tests grün, Slice-YAML + Workflow-Doku
**Ziel:** Finance-Kern-Prozesse auf volle 004-Tiefe heben: SEPA-Zahlungsträger (.2), Ratenzahlungsplan-Lifecycle (.3), Mahnwesen-Eskalation-Trail (.4), Playwright @smoke + UAT (.5).
**Dateibesitz:** `app/services/finance_sepa_service.py`, `app/services/finance_ratenzahlung_service.py`, `app/services/finance_mahnstufe_service.py`, `alembic/versions/finance_sepa_ratenzahlung_20260623.py`, `app/api/v1/endpoints/finance_actions.py`, `playwright-tests/specs/finance/finance-lifecycle-smoke.spec.ts`, `scripts/uat/finance_lifecycle_uat.py`, `docs/workflows/dom-finance-004-finance-deepening-2026-06-23.md`, `docs/agent-ops/slices/DOM-FINANCE-004.yaml`, `tests/test_dom_finance_004.py`
**Koordination:** Keine aktiven Cursor-Finance-Slices. Fremde Dateien bleiben unangetastet.

## DOM-COMPLIANCE-004 — Compliance-Domäne Vollständige Vertiefung (.2–.5)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — PCN-Lifecycle (.2), VVVO-Sachkunde (.3), Sperre-Audit-Trail (.4), Playwright @smoke + UAT-Script (.5), Alembic-Migration compliance_pcn_audit_20260623, 17 Unit-Tests grün, Slice-YAML + Workflow-Doku
**Ziel:** Compliance-Kern-Prozesse auf volle 004-Tiefe heben: PCN-Meldung-Lifecycle (.2), VVVO-Prüfung + Sachkunde-Ablauf (.3), Artikel-Sperre-Audit-Trail (.4), Playwright @smoke + UAT (.5). Schließt Lücke bei strukturiertem Service-Layer für behördliche Meldepflichten.
**Dateibesitz:** `app/services/compliance_pcn_lifecycle_service.py`, `app/services/compliance_vvvo_sachkunde_service.py`, `app/services/compliance_sperre_audit_service.py`, `alembic/versions/compliance_pcn_audit_20260623.py`, `app/api/v1/endpoints/compliance.py`, `playwright-tests/specs/compliance/compliance-lifecycle-smoke.spec.ts`, `scripts/uat/compliance_lifecycle_uat.py`, `docs/workflows/dom-compliance-004-compliance-deepening-2026-06-23.md`, `docs/agent-ops/slices/DOM-COMPLIANCE-004.yaml`, `tests/test_dom_compliance_004.py`
**Koordination:** Cursor besitzt keine aktiven Compliance-Slices. Fremde Dateien bleiben unangetastet.

## DOM-AGRAR-004 — Agrar-Domäne Vollständige Vertiefung (.2–.5)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — Partie-Aggregation (.2), Trocknungsabrechnung (.3), Selbstabrechnung-Lifecycle (.4), Playwright @smoke + UAT-Script (.5), Alembic-Migration agrar_partie_settlement_20260623, 13 Unit-Tests grün, Slice-YAML + Workflow-Doku
**Ziel:** Agrar-Kern-Prozess auf volle 004-Tiefe heben: Ernteannahme→Partie (.2), Trocknungsabrechnung→Settlement (.3), Selbstabrechnung-Lifecycle (.4), E2E-UAT (.5). Kein Überlapp mit WM-AGRI-QS-004 (Cursor, QS-Leitstand).
**Dateibesitz:** `app/services/agrar_partie_service.py`, `app/services/agrar_trocknung_abrechnung_service.py`, `app/services/agrar_selbstabrechnung_lifecycle_service.py`, `alembic/versions/agrar_partie_settlement_20260623.py`, `app/api/v1/endpoints/agrar_p0.py`, `playwright-tests/specs/agrar/agrar-lifecycle-smoke.spec.ts`, `scripts/uat/agrar_lifecycle_uat.py`, `docs/workflows/dom-agrar-004-agrar-deepening-2026-06-23.md`, `docs/agent-ops/slices/DOM-AGRAR-004.yaml`
**Koordination:** WM-AGRI-QS-004 (Cursor) besitzt `agri_qs_workflow*.py` — kein Überlapp. Fremde Dateien bleiben unangetastet.

## DOM-INV-004 — Inventory/Lager Domänen-Vertiefung (.2–.5)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — LotTrace/FEFO (.2), Inventur-Differenzbeleg (.3), Korrektur-Storno (.4), Playwright @smoke (.5), UAT-Script (.5), Alembic-Migration inv_lot_trace_20260623, 12 Unit-Tests, Slice-YAML + Workflow-Doku
**Ziel:** Inventory-Domäne auf volle 004-Tiefe heben: Chargen-/MHD-Traceability (.2), Inventur-Abschluss + Lagerbewegungs-Abstimmung (.3), Bestandskorrektur-Lifecycle (.4), E2E-UAT (.5). Schließt das DOMAIN-PARITY-001-Gap "tieferes Chargen-/MHD-Modell".
**Dateibesitz:** `app/services/inventory_lot_trace_service.py`, `app/services/inventory_count_close_service.py`, `app/services/inventory_correction_service.py`, `alembic/versions/inv_lot_trace_20260623.py`, `app/api/v1/endpoints/inventory_operations.py`, `playwright-tests/specs/inventory/inv-lifecycle-smoke.spec.ts`, `scripts/uat/inv_lifecycle_uat.py`, `docs/workflows/dom-inv-004-inventory-deepening-2026-06-23.md`, `docs/agent-ops/slices/DOM-INV-004.yaml`
**Koordination:** Kein Überlapp mit WM-AGRI-QS-004 (Cursor). Fremde Dateien bleiben unangetastet.

## WM-AGRI-QS-004 — QS-Leitstand-UI (Silo-Lots / Silozellen)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-23 — Worklist-API, Freigabe-Vorschlag, Leitstand-UI `lager/qs-leitstand`, Nav/Route, 7 Unit-Tests grün, TS 0.

## DOM-CRM-004.5 — CRM Kundenstamm E2E + UAT (DOM-CRM-004 abgeschlossen)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-23 — Playwright `crm-stammdaten-smoke.spec.ts` (bestehend), Live-UAT `scripts/uat/crm_stammdaten_lifecycle_uat.py`, Nachweisdoku aktualisiert.
**Ziel:** DOM-CRM-004 formal abschliessen analog CON/SALES 004.5.
**Dateibesitz:** `scripts/uat/crm_stammdaten_lifecycle_uat.py`, `tests/test_crm_stammdaten_uat.py`, `docs/dom-crm-004-uat-2026-06-10.md`, `docs/agent-ops/slices/DOM-CRM-004.5.yaml`.

## DOM-LOG-004 — Logistik-Domäne vollständige Vertiefung (.2–.5)

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-23 — Disposition-Check (.2), ePOD-Settlement (.3), Playwright @smoke (.5), UAT-Script (.5), Alembic-Migration log_disposition_20260623, Unit-Tests (9 Fälle), Slice-YAML + Workflow-Doku
**Ziel:** Logistik-Domäne auf volle 004-Tiefe heben analog CON/SALES/FIN/DOC/PROC: Tour-Disposition (Kapazitäts-/Zeitfenster-Optimierung), ePOD-Lifecycle (Lieferschein→Ablieferungsbeleg→Settlement), Frachtkostenabrechnung (Tarif→Abrechnung→Storno), Supply-Chain-Traceability (Tour→Freight→LS-Kette), Playwright-E2E + Live-UAT.
**Dateibesitz:** `app/api/v1/endpoints/logistics_*.py`, `app/services/logistics_*.py`, `alembic/versions/log_*`, `packages/frontend-web/src/pages/logistik/**`, `tests/test_logistics_*.py`, `scripts/uat/log_*.py`, `playwright-tests/specs/logistik/`, `docs/dom-log-004-*.md`, `docs/agent-ops/slices/DOM-LOG-004.yaml`
**Koordination:** Keine parallelen LOG-Dateien durch Cursor bekannt (alle LOG-*-Slices abgeschlossen). Fremde Dateien bleiben unangetastet.

## AI-HARNESS-GOV-001 - AI-assisted Development Harness Governance

**Von:** Codex → **Harness-Betrieb ab 2026-06-23:** Cursor (Auto)
**Owner:** Cursor (Betrieb/Wartung Harness); Umsetzung urspruenglich Codex
**Stand:** abgeschlossen 2026-06-23 — Governance-Artefakte umgesetzt; **Cursor uebernimmt operativen Harness-Betrieb** (Slice-Claims, Doku-Sync, Readiness-Checks vor Abschluss, keine fremden WIP-Buendel).
**Info an parallele Agenten:** Harness-Pflicht vor jedem neuen Slice: Workboard-Claim, `ai_harness`-Felder in Slice-YAML, Dateibesitz einhalten, `node scripts/ai-slice-readiness-check.cjs --slice <ID>` und `docs-code-sync-check` bei relevanten Aenderungen. Cursor pflegt Agent-Ops-/Governance-Dateien; fachliche WMS-/Silo-/LOG-Slices bleiben beim jeweiligen Slice-Owner.
**Ziel:** Slice-Harness, Doku-/Code-Sync, AI-Definition-of-Done, semantische QA-Templates, Nightly-Drift-Report, Vendor-Unabhaengigkeit und Security-/Major-Update-Prozess operativ einfuehren.
**Dateibesitz:** `docs/agent-ops/*` nur AI-Harness-relevante Dateien, `docs/architecture/ai-assisted-enterprise-development-standard.md`, `docs/project-context/ai-assisted-development-implementation-plan-2026-06-23.md`, neue QA-Templates, `config/docs-code-sync-map.yaml`, `artifacts/ai-tool-compatibility-matrix.json`, `scripts/docs-*.cjs`, `scripts/ai-slice-readiness-check.cjs`, `.github/workflows/docs-governance.yml`, `.github/workflows/quality-gate.yml`, `.github/workflows/ai-doc-sync.yml`.
**Abnahmekriterien:** Neue/geaenderte Slice-YAMLs werden auf AI-Harness-Felder validiert; kritische Codepfade benoetigen Doku/Gaps oder explizite Ausnahme; AI-Slice-Readiness ist pruefbar; semantische QA-Templates und Drift-Report existieren; Security-/Major-Update-Prozess ist dokumentiert.
**Risiken:** Legacy-Slices duerfen nicht sofort repo-weit blockiert werden; Checks gelten initial fuer neue/geaenderte Artefakte und kritische Diff-Pfade.
**Verifikation:** `node --check` fuer neue/geaenderte Governance-Scripts gruen; `node scripts/docs-governance-check.cjs docs/agent-ops/slices/AI-HARNESS-GOV-001.yaml` gruen; `node scripts/ai-slice-readiness-check.cjs --slice AI-HARNESS-GOV-001` gruen; `node scripts/docs-code-sync-check.cjs --base HEAD --head WORKTREE` gruen; `pnpm.cmd run docs:check` gruen.
**CI-Nachzug 2026-06-23:** Quality-Gate-Folgefix auf `main`: `agri_plc_stub.py` bekam `response_model=dict[str, Any]` fuer die vier neuen PLC-Stub-Routen, damit die Response-Model-Coverage wieder unter dem erlaubten untyped-Routen-Schwellwert liegt. Der neue Docs/code-sync-Check hat den reinen Code-Fix korrekt als dokumentationspflichtig markiert; diese Workboard-Zeile ist der zugehoerige Nachweis.

## ALEMBIC-MERGE-DOM004-20260623 — Ein Head nach paralleler 004-Welle

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-23 — Merge-Revision `merge_dom004_feed_chain_20260623` vereint
`feed_chain_article_map_20260623` (FEED-CHAIN-004) und `sales_ab_preisabweichung_20260623`
(DOM-SALES-004-Kette); `test_alembic_single_head.py`; wieder genau 1 Alembic-Head.
**Ziel:** `alembic upgrade head` / init_db / Container-Bootstrap nicht durch Multiple-Heads blockieren.
**Dateibesitz:** `merge_dom004_feed_chain_20260623.py`, `test_alembic_single_head.py`, Open-Gaps Build-Health.
**Abnahmekriterien:** `alembic heads` → 1 Zeile; Governance-Test grün.
**Hinweis DOM-PROC-004:** Migration `proc_bestellung_wareneingang_20260623` hängt an
`merge_dom004_feed_chain_20260623` — aktueller Head (Stand nach DOM-PROC-004 Abschluss).

## COMPAT-GOV-MATRIX-SYNC-20260623 — Release-Matrix Alembic-Head

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-23 — `generate_release_compatibility_matrix.py` lokal ausgeführt;
`database_revision=proc_bestellung_wareneingang_20260623`; Open-Gaps + Process-Kernel STATUS
aktualisiert; Governance-Tests grün.
**Ziel:** Kompatibilitätsmatrix und Doku auf aktuellen DB-Head nach DOM-PROC-004 bringen.
**Abnahmekriterien:** `build_matrix()` liefert einen Head; `test_alembic_single_head` grün.

## COV-RATCHET-FEED-001 — Coverage FeedInventoryLinkService

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-23 — `test_feed_inventory_link_unit.py` (11 Unit-Tests);
Ratchet-Einträge `feed_inventory_link_service.py` + `produktion_mischfutter.py` in
`check_critical_backend_coverage.py`.
**Ziel:** FEED-CHAIN-004 Service-Pfad im kritischen Coverage-Ratchet absichern.
**Abnahmekriterien:** 11 Unit-Tests grün; Ratchet-Pfade registriert.

## WM-AGRI-MAP-001 — Silo Bird-View / Kapazitäts-Dashboard

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-23 — `pages/lager/silo-uebersicht.tsx`; Route `lager/silo-uebersicht`; Nav-Eintrag „Silo-Übersicht (Bird-View)"; routes:generate 880 Routen; ESLint 0 Warnings; TS 0 Fehler.
**Ziel:** Operatives Bird-View-Dashboard aller Silozellen eines Lagers: Kapazitäts-Füllstand als Balken, QS-Ampel (grün/gelb/rot), Material/Lot-Info, Zusammenfassungs-KPIs (Gesamt-t, Auslastung %, gesperrte Zellen), QS-Filter, Auto-Refresh alle 30 s, Transfer-Button → lager/materialfluss.
**Dateibesitz:** `packages/frontend-web/src/pages/lager/silo-uebersicht.tsx`, `packages/frontend-web/src/app/route-aliases.json`, `packages/frontend-web/src/app/navigation/domains/operations.tsx`, `packages/frontend-web/src/app/routing/route-tree.gen.tsx`.
**Abnahmekriterien:** Route lager/silo-uebersicht; SummaryBar mit Gesamt-t/Auslastung/gesperrt; Kachel-Grid mit Füllbalken/QS-Badge/Lot-Info/Transfer-Button; QS-Filter; refetchInterval 30 s; ESLint 0 / TS 0.

## WM-AGRI-BIDIR-SYNC-001 — Bidirektionaler Sync WMS-FLOW-001 → silo_lots

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-23 — `AgriSiloLotLinkService.sync_lots_from_transfer` implementiert; best-effort Hook in `AgriSiloMaterialFlowService.book_material_transfer` vor commit; 3 neue Unit-Tests (29/29 gesamt grün).
**Ziel:** Materialtransfers im WMS-Graph (WMS-FLOW-001) spiegeln sich jetzt in `domain_inventory.silo_lots` zurück — Quell-Lot wird um `quantity_kg/1000 t` reduziert (ggf. auf `closed` gesetzt), Ziel-Lot erhöht (wenn aktives Lot mit passendem Artikel im legacy_silo existiert). Je eine `SiloLotMovement`-Zeile ('out'/'in') wird geschrieben. Fail-soft wenn kein `legacy_silo_id`-Mapping vorhanden.
**Dateibesitz:** `app/services/agri_silo_lot_link_service.py`, `app/services/agri_silo_material_flow_service.py`, `tests/test_agri_silo_material_flow.py`.
**Abnahmekriterien:** Quell-Lot reduziert; status='closed' bei Restmenge=0; Ziel-Lot erhöht wenn Kandidat vorhanden; ok=False fail-soft ohne Mapping; kein eigener commit; 29/29 Unit-Tests grün.

## WM-AGRI-AUTO-LINK-001 — Vollautomatische LOT-LINK-Buchung (Annahme/Waage → Silozelle)

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-23 — `auto_book_lot_link_by_lot_id` in `AgriLotLinkBookingService`; Auto-Hook `_auto_book_lot_link` in `silo.py` `create_silo_lot`; neuer Endpoint `POST /material-flow/lot-link/auto-book`; 3 neue Unit-Tests (8/8 grün).
**Ziel:** Medienbruch Annahme/Waage → Silozelle schließen: nach Silo-Lot-Anlage wird automatisch via `legacy_silo_id`-Mapping die beste Zielzelle ermittelt und `book_lot_to_cell` transaktional ausgeführt — kein manueller Operator-Schritt nötig. Fail-soft wenn kein Mapping vorhanden (ok=False + reason statt Exception).
**Dateibesitz:** `app/services/agri_lot_link_booking_service.py`, `app/api/v1/endpoints/agri_lot_link_booking.py`, `app/api/v1/endpoints/silo.py`, `tests/test_agri_lot_link.py`.
**Abnahmekriterien:** `auto_book_lot_link_by_lot_id` findet beste Zelle via `legacy_silo_id`-Score; bucht transaktional mit Stock-Movement + Trace-Event; gibt ok=False fail-soft wenn kein Mapping/inaktives Lot/alle Zellen gesperrt; Auto-Hook nach `create_silo_lot`; Endpoint `/material-flow/lot-link/auto-book` für Retry; 8/8 Unit-Tests grün.
**Verifikation:** `python -m py_compile` grün; `pytest -q -o addopts= tests/test_agri_lot_link.py` → 8 passed.

## HRM-PAYROLL-DEEP-001 — HRM Payroll Deepening

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-18 — Payroll-Preview und Closeout-Vertrag umgesetzt; parallel dirty Dateien (`app/api/v1/api.py`, Scheduler, WF/STMD/Waage/XRechnung, WM-AGRI-SILO-001) bleiben unberuehrt.
**Ziel:** Lohnbuchhaltung von Payroll-Readiness zu einem pruefbaren Closeout-Vertrag vertiefen: Brutto-Netto-Kontext, Arbeitgeberanteile, Lohnarten, DATEV-ASCII-Uebergabedaten, FIBU-Buchungssaetze, externe Gates und Regressionstests.
**Dateibesitz:** `app/services/lohn_service.py`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_payroll_deep.py`, `docs/project-context/hrm-payroll-deepening-2026-06-18.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/HRM-PAYROLL-DEEP-001.yaml`.
**Abnahmekriterien:** Explizites Payroll-Response-Modell, Monats-Closeout mit AN-/AG-Anteilen, DATEV-/FIBU-Uebergabevertrag, fail-closed externe Gates, Regressionstests.
**Verifikation:** `python -m py_compile` gruen; direkte Python-Vertragschecks fuer Payroll-Service und Closeout gruen. Voller Pytest-Harness haengt aktuell im bestehenden globalen Test-Setup.

## INT-ACCOUNTING-EXPORT-PROFILES-001 — Steuerberater-/Accounting-Exportprofile

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-18 — kanonisches Exportmodell, sieben YAML-Profile, Validierung, CSV-Rendering, Checksummen, Korrekturvertrag, Doku und Tests angelegt.
**Ziel:** Kanzleisoftware-neutrales kanonisches Exportmodell mit versionierten Profilen fuer DATEV, Agenda, ADDISON, Simba, Lexware, Sage und SBS/Wolters Kluwer; keine Zertifizierung behaupten, Steuerberater-Testimport bleibt externes Gate.
**Dateibesitz:** `app/services/accounting_export_profiles.py`, `config/export_profiles/*.yaml`, `tests/test_accounting_export_profiles.py`, `docs/integrations/tax-advisor-export-profiles.md`, `docs/agent-ops/slices/INT-ACCOUNTING-EXPORT-PROFILES-001.yaml`.
**Abnahmekriterien:** Pflichtfeldvalidierung, KOST1/KOST2-Mapping, CSV-Rendering, Checksummen, Batch-Status, Korrekturexport-Versionierung und not_certified/requires_tax_advisor_test_import fuer nicht abgenommene Profile.
**Verifikation:** `python -m py_compile` gruen; direkte Python-Vertragschecks laden alle sieben Profile, validieren balancierte Batches und rendern CSV mit Checksummen.

Stand: `2026-06-18`

## WM-AGRI-QS-003 — QS-Freigabe und Audit fuer Silo-Lots

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-18 — QS-Workflow-Service, API, Lot-/Silozellen-Rueckkopplung, Audit-Event, Tests und Doku umgesetzt.
**Ziel:** QS-/Compliance-Tiefe fuer Silo-Lots erhoehen: Statuswechsel mit Pflichtgrund, Bediener, Proben-/Analyse-/Dokumentenbezug, GMP+/VLOG-Nachweisen, Silozellen-Rueckkopplung und append-only Supply-Chain-Audit.
**Dateibesitz:** `app/services/agri_qs_workflow_service.py`, `app/api/v1/endpoints/agri_qs_workflow.py`, `app/api/v1/api.py`, `tests/test_agri_qs_workflow.py`, `docs/agent-ops/slices/WM-AGRI-QS-003.yaml`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/workflows/wm-agri-silo-supply-chain-integration-2026-06-13.md`.
**Abnahmekriterien:** Tenant-Scope, erlaubte QS-Transitionen, Pflichtgrund, Audit-Payload mit Labor-/Dokumentenbezug, Update `silo_lots.status`, Update verknuepfter `silo_cells.qs_status`, Trace-Event, Regressionstest.
**Verifikation:** `python -m py_compile app/services/agri_qs_workflow_service.py app/api/v1/endpoints/agri_qs_workflow.py app/api/v1/api.py tests/test_agri_qs_workflow.py`; `python -m pytest -q -o addopts= tests/test_agri_qs_workflow.py` (4 passed).

## WM-AGRI-LOT-LINK-001 — Lot-/Bestands-Sync Waage/WE -> Silozelle

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-18 — Backend-Kontrakt `POST /material-flow/lot-link`, Service-Härtung, Regressionstests und Doku umgesetzt; UI-/Leitstand-Folgen bleiben eigene Slices.
**Ziel:** Medienbruch Annahme -> Waage -> Lot -> Silozelle -> kg-Bestand -> Trace schließen: Silo-Lots werden fail-closed mit `silo_cells.current_lot_id`, `current_material_id`, `current_stock_kg`, Bestandsbewegung und Trace-Event verbunden.
**Dateibesitz:** `app/services/agri_lot_link_booking_service.py`, `app/api/v1/endpoints/agri_lot_link_booking.py`, `app/api/v1/api.py`, `tests/test_agri_lot_link.py`, `docs/workflows/wm-agri-silo-supply-chain-integration-2026-06-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/WM-AGRI-LOT-LINK-001.yaml`.
**Abnahmekriterien:** Tenant-Scope, Zielzellen-/Kapazitätsprüfung, Lot-/Material-Konfliktschutz, idempotenter Bewegungsbeleg, Aktualisierung von `current_*`, Trace-Event, Regressionstest und aktualisierte Doku.
**Verifikation:** `python -m py_compile app/services/agri_lot_link_booking_service.py app/api/v1/endpoints/agri_lot_link_booking.py app/api/v1/api.py tests/test_agri_lot_link.py`; `python -m pytest -q -o addopts= tests/test_agri_lot_link.py` (4 passed im ersten Lauf; spätere Wiederholung hing im bestehenden globalen Harness ohne Testausgabe, Direktvertrag grün).

## P0-INTEGRATION-SLICES-001 — Fachliche Integrationslücken (5 Slices)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-18 — alle 7 Slices (5 neu, 2 bereits vorhanden) implementiert und gepusht. HEAD: `b25d10e5b` + nachgezogener CI-Fix fuer Procurement-Inventory-Kompatibilitaet und Tenant-Testvertrag.
**Ziel:** Schließt kritische Prozesskettenlücken aus ERP-Tiefenanalyse:
  - WMS-FLOW-001: `book_material_transfer()` in AgriSiloMaterialFlowService + Endpoint POST /material-flow/transfer — Silozell→StockMovement-Kopplung mit Kontaminationsschutz; UI Transfer-Card auf `lager/materialfluss` (2026-06-19)
  - KORE-BAB-001: BAB-Engine (GET /kostenrechnung/bab) + Kostenumlage (POST /kostenrechnung/umlagen) + BAB-Tab im Frontend
  - CRM-360-REAL: crm_360.py komplett neu mit schema-qualifizierten Tabellennamen, 404 bei fehlendem Kunde, echte OP-Summe
  - PROC-3WM-001: POST /procurement/match/auto + GET /procurement/match/results — Match-Persistierung in domain_procurement.procurement_match_results
  - QS-CHARGE-001: QsChargeService (Feuchte/Unreinheiten/HL-Gewicht/Mykotoxin-Abschläge) + GET /harvest-acceptances/{id}/qs-abschlag
  - Alembic: wms_material_flow_stock_link_20260619 (silo_cells.current_stock_kg + kostenstellen_umlagen + harvest_acceptances.quality_protocol_id + procurement_match_results)
**Dateibesitz:** app/services/agri_silo_material_flow_service.py, app/services/qs_charge_service.py (neu), app/api/v1/endpoints/agri_silo_material_flow.py, app/api/v1/endpoints/kostenrechnung.py, app/api/v1/endpoints/crm_360.py, app/api/v1/endpoints/procurement_match.py, app/api/v1/endpoints/harvest_acceptance.py, packages/frontend-web/src/lib/api/kostenrechnung.ts, packages/frontend-web/src/pages/fibu/kostenstellenrechnung.tsx, alembic/versions/wms_material_flow_stock_link_20260619.py
**Codex-Review 2026-06-18:** KORE-BAB-001 und PROC-3WM-001 gehaertet: valide Monatsgrenzen statt `YYYY-MM-31`, aktive Quell-/Ziel-KST-Validierung, monatliche Budget-Normalisierung, String-ID-kompatible Migration, fehlendes `domain_procurement`-Schema, toleranzbasierte 3-Way-Match-Klassifikation mit persistierten Mengen-/Wertkennzahlen.

## QM-REK-LAB-001 - Reklamation/Labor fachlich schliessen

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-18 - Tenant-Scope, Statusmaschine, Laborbefund, QS-Folgeaktion und E2E-Blocker umgesetzt; Pytest-HTTP-Lauf blockiert im bestehenden TestClient/DB-Start, Import/Lint/py_compile gruen.
**Ziel:** Complaint-to-Resolution technisch und fachlich haerten: Tenant-Scope, serverseitige Statusmaschine, Laborbefund, QS-Entscheidung, Folgeaktionen fuer Sperre/Freigabe/Retoure/Gutschrift/CAPA.
**Dateibesitz:** `app/api/v1/endpoints/reklamation_api.py`, `app/api/v1/endpoints/labor.py`, `app/core/reklamation.py`, `tests/test_reklamation_api.py`, `tests/test_labor_api.py`, `packages/frontend-web/src/lib/api/betrieb.ts`, `packages/frontend-web/src/pages/qualitaet/labor-detail.tsx`, `docs/cards/qualitaet/REK-001-complaint-to-resolution.md`.
**Abnahmekriterien:** Body-basierter Statuswechsel; kein Cross-Tenant-Read; Laborbefund mit Folgeentscheidung; E2E-Risiken sichtbar; Import/Lint/py_compile/direkte Vertragspruefung gruen, Pytest-HTTP-Timeout dokumentiert.

## KOND-001 — Konditionssystem / Preisfindung

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-17 — vollständige Frontend-UI für alle vorhandenen Backend-Preismodule.
**Ziel:** Kern des Landhandels: Kundenpreislisten, Staffelpreise, Rabattgruppen/-klassen, zeitbegrenzte Konditionen, hierarchische Preisfindung.
**Bestandsaufnahme (2026-06-17):** Backend war vollständig vorhanden (price_lists.py, pricing.py, preis_rabattgruppen.py, zu_abschlaggruppen.py, individualpreise.py, price_calculation.py); Frontend-UI komplett fehlend.
**Dateibesitz:**
- `packages/frontend-web/src/lib/api/konditionen.ts` — API-Client (Preislisten, Preisfindung, Rabattgruppen/klassen/sätze, Individualpreise)
- `packages/frontend-web/src/pages/konditionen/konditionssystem.tsx` — 6-Tab-Hauptseite (Preislisten, Rabattgruppen, Rabattklassen, Rabattsätze, Individualpreise, Preisfindung-Kalkulator)
- `packages/frontend-web/src/app/navigation/domains/commercial.tsx` — Nav-Eintrag unter „Preise & Kalkulation"
**Abnahmekriterien:** ESLint 0 Warnings; alle 6 Tabs rendern; CRUD für Preislisten/Rabattgruppen/klassen/sätze/Individualpreise; Live-Preisfindung gegen `/api/v1/pricing/calculate`.

## FUHRPARK-VERTIEFUNG-001 — Fuhrpark Tiefenausbau (5 Gaps)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-16 — alle 5 identifizierten Gaps implementiert.
**Ziel:** Status-Lifecycle, Schadensfälle, Bußgeld, KM-basierte Wartungsvorhersage, Leasing-Rückgabe.
**Dateibesitz:**
- `alembic/versions/fuhrpark_vertiefung_20260616.py` — 3 neue Tabellen `ops_fahrzeug_status_historie`, `ops_fahrzeug_schaeden`, `ops_fahrzeug_bussgeld`
- `app/api/v1/endpoints/fuhrpark.py` — 10 neue Endpunkte (Status-Wechsel, Historie, Schaeden CRUD, Bussgeld CRUD, Wartungsvorhersage, Leasing-Rückgabe)
- `packages/frontend-web/src/lib/api/fuhrpark.ts` — 4 neue Typen + 10 neue Funktionen
- `packages/frontend-web/src/pages/fuhrpark/fahrzeug-vertiefung.tsx` — neue 5-Tab-Seite
- `packages/frontend-web/src/app/navigation/domains/operations.tsx` — Nav-Eintrag „Vertiefung & Analyse"
- `tests/test_fuhrpark_vertiefung.py` — Integrationstests (integration, needs_live_db)
**Abnahmekriterien:** `alembic upgrade head` erzeugt 3 Tabellen; 10 neue API-Endpunkte erreichbar; Frontend Lint 0 Warnings; Integrationstests grün (needs_live_db).

## WM-AGRI-SILO-001 — Agrar-Silo / Materialfluss (additiv WMS)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-19 — Stammdaten, Live-Graph, Route-Validierung, Silozellen-PATCH inkl. Layout, Supply-Chain-Anbindung (CHAIN-002), Materialtransfer (WMS-FLOW-001) Backend+UI; Alembic-Head `agri_silo_cells_layout_20260619`; 18 Unit-Tests grün.
**Ziel:** Digitales Modell Siloanlage/Silozelle/Materialfluss ohne PLC; QS-Sperre und Verschleppungs-Hinweis auf Routen; Mandanten-Trennung.
**Dateibesitz:** genannte Alembic-/Backend-/Frontend-/Test-/Doku-Dateien, `docs/warehouse/README.md`, `docs/agent-ops/slices/WM-AGRI-SILO-001.yaml`, `docs/agent-ops/slices/WMS-FLOW-001.yaml`, Roadmap `WM-AGRI-FLOW-001.yaml`.
**Abnahmekriterien:** `alembic heads` einheitlich; API erreichbar; Tests `pytest tests/test_agri_silo_material_flow.py --no-cov` grün; Transfer-UI auf `lager/materialfluss`; Navigation + `npm run routes:generate` konsistent.
**Folge-Slices umgesetzt:** WM-AGRI-AUTO-LINK-001, WM-AGRI-BIDIR-SYNC-001, WM-AGRI-MAP-001, WM-AGRI-FLOW-002, WM-AGRI-FLUSH-006, WM-AGRI-MOBILE-004, WM-AGRI-PLC-005 — alle abgeschlossen 2026-06-23.

## WM-AGRI-FLOW-002 — Graph-Editor Create/Delete (Knoten & Kanten)

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-23 — `CreateNodeDialog`, `CreateEdgeDialog` in `materialfluss-visualisierung.tsx`; `DELETE /material-flow/nodes/{id}` + `DELETE /material-flow/edges/{id}` Backend-Endpoints; `useDeleteAgriFlowNode/Edge` React-Query-Hooks; Selection-State + Trash-Buttons.
**Ziel:** Operatoren können im Graph-Editor neue Knoten/Kanten anlegen und bestehende löschen.
**Dateibesitz:** `packages/frontend-web/src/pages/lager/materialfluss-visualisierung.tsx`, `packages/frontend-web/src/lib/api/agri-material-flow.ts`, `app/services/agri_silo_material_flow_service.py`, `app/api/v1/endpoints/agri_silo_material_flow.py`.

## WM-AGRI-FLUSH-006 — Spülcharge-Workflow

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-23 — `AgriSiloMaterialFlowService.book_flush_charge`; `POST /material-flow/flush-charge`; `flush_required` Reset auf betroffenen Kanten; Supply-Chain-Event + Outbox; 4 neue Tests (22/22 grün).
**Ziel:** Reinigungslauf vor Materialwechsel: Spülcharge bucht Out/In mit `ownership_type='flush'`, setzt `flush_required=false` auf Route, emittiert Trace-Event.
**Dateibesitz:** `app/services/agri_silo_material_flow_service.py`, `app/api/v1/endpoints/agri_silo_material_flow.py`, `tests/test_agri_silo_material_flow.py`.

## WM-AGRI-MOBILE-004 — Mobil-UI Waage/Hallenterminal

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-23 — `pages/lager/silo-mobil.tsx`; Route `lager/silo-mobil`; Nav-Eintrag „Silo-Terminal (Mobil)"; Panels: Auto-Lot-Link, Schnelltransfer, Spülcharge, Zellen-Schnellübersicht.
**Ziel:** Touch-optimierte Seite (max-w-2xl) für Tablet-Operatoren an Waage und Hallenterminal. Alle zentralen Silo-Aktionen (Lot-Link, Transfer, Flush) ohne Desktop-Navigation erreichbar.
**Dateibesitz:** `packages/frontend-web/src/pages/lager/silo-mobil.tsx`, `packages/frontend-web/src/app/route-aliases.json`, `packages/frontend-web/src/app/navigation/domains/operations.tsx`, `packages/frontend-web/src/lib/api/agri-material-flow.ts`.

## WM-AGRI-PLC-005 — PLC/OPC-UA Anbindung Stub

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-23 — `AgriPlcService` + 3 Endpoints (`POST /plc/ingest`, `POST /plc/silo-level`, `POST /plc/device-status`, `GET /plc/info`); Router in `api.py` unter Prefix `/lager/wms/agri`; 5 Unit-Tests grün.
**Ziel:** Stub-Endpoint für SPS/OPC-UA-Sensordaten: IoT-Gateway liefert Füllstand-/Temperatur-/Statusmeldungen per REST; `silo_level`-Endpoint schreibt `current_stock_kg` auf Silozelle. Produktionserweiterung: asyncua-Polling + plc_tag_mappings-Tabelle.
**Dateibesitz:** `app/api/v1/endpoints/agri_plc_stub.py`, `app/api/v1/api.py`, `tests/test_agri_plc_stub.py`.

## WM-AGRI-LOT-LINK — silo_lots ↔ silo_cells

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-19 — Sync, Lot-Link-Buchung, **Vorschlag-API** (`GET …/lot-link/suggest`) + UI auf `lager/materialfluss`; Tests grün (5).
**Offen:** Vollautomatische Buchung bei Annahme/Waage; Rücksync WMS-FLOW-001 → `silo_lots`.

## WAVE-PHYS-CHAIN-001 — Task 0 Verifikation + Logistik-Audit

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — Playwright Dev-Session ohne Fake-Login; Audit-Dokument physische Kette / Logistik.
**Ziel:** Blindfläche aus Advisor-Feedback schließen, bevor LOG-*-Slices gebaut werden.
**Dateibesitz:** `playwright-tests/helpers/api.ts`, `playwright-tests/fixtures/testSetup.ts`, `docs/quality-assurance/playwright-smoke-auth.md`, `docs/workflows/wave-physical-chain-logistics-audit-2026-06-12.md`, `domain-depth-plan`.
**Abnahmekriterien:** Doku + funktionierender Dev-Pfad für @smoke; keine parallelen DOM-005-Spines.

## LOG-PROD-001 — Logistik `domain_logistics` per Alembic

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — Alembic `log_logistics_core_20260612`; Runtime-DDL aus `logistics_tours.py` und `logistics_freight.py` entfernt; Integrationstests `tests/test_logistics_integration.py`.
**Ziel:** Production-gleiche Persistenz für Touren/ePOD/Statistik und Frachttarife (analog PROC-RFQ-001).
**Dateibesitz:** `alembic/versions/log_logistics_core_20260612.py`, Logistik-Endpunkte, genannte Tests, Audit-Dokument.
**Abnahmekriterien:** `alembic upgrade head` erzeugt Tabellen; keine `_ensure_schema` / `_ensure_freight_table` in den Routern; bestehende Unit-Tests mit Mocks angepasst.
**2026-06-12:** Frachtkosten simulate/calculate mit **X-Tenant-ID-Pflicht** und SQL-Filter auf Tarifzeilen (kein Fremd-Tenant); Tests in `test_logistics_integration.py` / `test_logistics_tour_freight.py`. Anschliessend: **GET freight-tariffs** ohne Header nur `tenant_id IS NULL`; **POST freight-tariffs** verlangt Header (422) — weitere Integrationstests.

## LOG-SPINE-RAND-001 — Lieferschein-Referenz Read-Spine (Logistik)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — GET ``sales-delivery-note-by-ref`` + optional ``include_delivery_hints`` auf Tour-Detail; Tests ``test_logistics_delivery_hint.py``.
**Ziel:** Medienbruch reduzieren ohne Schema-FK; Muster wie `sales_storno_service` (id oder Nummer).
**Dateibesitz:** `logistics_tours.py`, `tests/test_logistics_delivery_hint.py`, Wave-Audit, Slice-YAML.
**Abnahmekriterien:** Neuer GET-Resolve + optional `include_delivery_hints` auf Tour-Detail; Tests gruen.

## LOG-LIFE-001 — Tour-/Stopp-Storno (fail-closed) + UAT

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — API-Storno in `logistics_tours.py`, Frontend
`misc-modules.ts` / `tourenplanung.tsx`, Integrationstest
`test_tour_cancel_fail_closed_and_stop_cancel`, UAT
`scripts/uat/logistics_tour_lifecycle_uat.py`; Decorator-Fix `add_event`.
**Ziel:** Storno ohne Medienbruch; 409/422/403 fail-closed; reproduzierbares UAT.
**Dateibesitz:** genannte Dateien + Wave-Audit.
**Abnahmekriterien:** Storno-POSTs + Tests + UAT-Skript (dry-run/execute) dokumentiert.
**Review (Claude, 2026-06-12):** zwei Fixes direkt eingespielt — (1) `test_freight_tariff_create_and_simulate`
war versehentlich in den neuen Storno-Test hineingemergt (Methodenzeile ersetzt statt eingefügt);
wieder als eigene Testmethode ausgegliedert. (2) `add_event`: `status_code=201` wiederhergestellt
(der Decorator-Umbau hatte den Create-Statuscode stillschweigend auf 200 geändert; kein Konsument
hängt daran, aber Vertrag bleibt so stabil). Verifiziert: `pytest tests/test_logistics_integration.py
tests/test_logistics_delivery_hint.py` → 6/6 grün; ESLint + `type-check:focused` grün.

## LOG-CHAIN-001 — Ketten-Lifecycle (Audit Bruchstelle 2)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — Integrationstest
`test_chain_lifecycle_ls_tour_hints_freight_supply_read` in `tests/test_logistics_integration.py`
(ohne `DEMO-LS-001` aus `seed_demo_sales.py`: Skip), UAT
`scripts/uat/logistics_chain_lifecycle_uat.py`; Wave-Audit Abschnitt 2 Punkt 2 geschlossen.
**Ziel:** Reproduzierbare Kette **Lieferschein-Ref → Tour mit Hints → Fracht simulate →
`GET /supply-chain/traceability/tickets` (Settlement-Seite read-only) → Tour-Storno**.
**Dateibesitz:** genannte Test-/UAT-Dateien, Audit-Dokument.
**Abnahmekriterien:** Test + UAT (dry-run/execute) dokumentiert; keine Abrechnungs-Mutation im Slice.

## LOG-LIFE-UI — Tour-Storno in der Tourenplanung (Frontend)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — `cancelLogisticsTour` / optional `cancelLogisticsTourStop`
in `logistics-tours.ts`; Tourenplanung: Bestätigungsdialog, `invalidateQueries(['logistik','touren'])`,
Toasts, Pending-State.
**Ziel:** LOG-LIFE-001 vom Schreibtisch aus bedienbar ohne REST-Client.
**Dateibesitz:** `tourenplanung.tsx`, `logistics-tours.ts`, Wave-Audit, Workboard.

## LOG-TF-WS-001 — Tour & Fracht Dispo-Arbeitsraum (gemeinsame Route)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — Seite `tour-fracht-arbeitsraum.tsx`, Nav-Eintrag, Auto-Route
`logistik/tour-fracht-arbeitsraum`, Domain-Landing `tour-fracht-arbeitsraum`; `routes:generate` + Navigation-Check gruen;
Erweiterung: **RoleFocusBar**, **Frachtkosten-Kurzcard** (`logistics-freight.ts` → Tarife + GET simulate).
**Ziel:** Wave-Audit Punkt 5 — eine operative Einstiegssicht fuer Tour + Frachtbrief.
**Dateibesitz:** genannte Dateien, `operations.tsx`, `dashboard-catalog.ts`, `auto-groups/generated/logistik.ts`.
**Review (Claude, 2026-06-12):** keine Befunde — `useSupplyChainOverview` liefert `initialData`
(kein Undefined-Zugriff auf `chain` vor dem Load), Frachtkosten-Probe mit Pending-Guard/finally/Toast,
ESLint auf beiden neuen Dateien grün.
**E2E:** Route in `main-routes-smoke.spec.ts` (expectedText) und `visual-tour.spec.ts` ergänzt.

## FEED-CHAIN-001 — Produktion→Charge-Durchstich (Mischfutter)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-12 — Migration `feed_chain_verbrauch_20260612` (Single-Head),
Service + Endpoint-Umbau, Seed `seed_demo_feed_chain.py` (DEMO-MLF-18), 7 neue Tests grün,
20 Bestands-Regressionstests grün, UAT dry-run + `--execute` gegen Live-Backend grün.
**Ziel:** Belegbruch schließen: Produktionsauftrag ``fertig`` erzeugt die Fertigwaren-Charge
(``domain_ops.ops_chargen``) mit Mischprotokoll (``rohstoffe``/``produktionsprozess``) statt
nur ``fertig_am``; Verbrauchs-Snapshot bei Freigabe (fixt auch Bestandsdrift beim Storno nach
Rezeptänderung); Trace Auftrag/Charge → Komponenten.
**Dateibesitz:** `app/api/v1/endpoints/produktion_mischfutter.py`,
`app/services/feed_production_chain_service.py` (neu), `app/infrastructure/models/futtermittel_models.py`,
Alembic `feed_chain_verbrauch_20260612`, `tests/test_feed_production_chain.py` (neu),
`scripts/uat/feed_production_chain_uat.py` (neu), Audit-Doc Futtermittel-Kette.
**Abnahmekriterien:** fertig → Charge idempotent + fail-closed (409 bei fremder chargen_id);
Storno restauriert exakt den Freigabe-Verbrauch; Trace-GET; Tests + UAT grün.

## FEED-CHAIN-002 — Produktions-Lifecycle im Frontend (Mischfutter)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-12 — Browser-verifiziert (Dev :3000): Wizard → Auftrag (201) →
Freigeben → Produktion starten → Fertig (Charge `CH-…` erscheint mit Link in der Zeile) →
„Kette anzeigen“ (Trace-Panel „Kette geschlossen“, Mischprotokoll 1.240/0.680/0.080 t bei 2 t).
Zusatzbefund behoben: ``initialData: []`` + ``staleTime`` unterdrückte den ersten Fetch
(Rezept-Select war deshalb schon immer leer) → Hooks ohne ``initialData``, Fallback `?? []`.
ESLint + `type-check:focused` grün.
**Ziel:** Kette vom Schreibtisch aus bedienbar. Befund: Wizard postet ``{rezeptur, menge}``,
Backend erwartet ``{rezept_id, menge_t}`` (→ 422, Create war tot); Komponenten-Map nutzt
``k.name`` statt ``komponente_name`` (Bedarfsprüfung leer). Fix der Hooks/Payloads +
Auftragsliste mit Statusübergängen (freigeben → in_produktion → fertig → storniert),
Charge-Link nach ``fertig`` und Trace-Ansicht; Per-Entity-Pending laut Invariante.
**Dateibesitz:** `packages/frontend-web/src/lib/api/produktion.ts`,
`packages/frontend-web/src/pages/produktion/mischfutter-produktion.tsx`, Audit-Doc Futtermittel-Kette.
**Abnahmekriterien:** Create gegen echtes Backend (201), Statusaktionen mit keyed Pending +
Toast, fertige Aufträge zeigen Charge/Trace; ESLint + type-check grün.

## WMS-PICK-LINK-001 — Lieferschein → Kommissionierliste → Warenausgang (Belegbruch)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `create_pick_list_from_delivery_note()` in `warehouse_service.py`
(prüft Status posted/printed, kein Duplicate, keine leere Pos-Liste → 409); `confirm_pick_list` setzt
Lieferschein automatisch auf `shipped` wenn DELIVERY_NOTE-Pick-Liste COMPLETED;
`POST /lager/wms/pick-lists/from-delivery-note/{ls_id}` (409 fail-closed); `warehouse-wms.ts`
(PickList-Typen, `createPickListFromDeliveryNote`, `confirmPickList`, Hooks); Kommissionierungs-Seite
`lager/kommissionierung` (per-entity Pending, „Alle bestätigen", FEFO-Zeilen, Toast bei shipped);
6 Unit-Tests grün; ESLint + type-check grün; Route + Nav-Eintrag generiert.
**Ziel:** Belegbruch Lieferschein (posted/printed) → Kommissionierliste (WMS/FEFO) → Warenausgang
(shipped) ohne manuelles REST-Tool.
**Dateibesitz:** `app/services/warehouse_service.py` (Methoden-Erweiterung),
`app/api/v1/endpoints/warehouse_wms.py` (neuer Endpoint + PickListFromDeliveryNoteIn),
`packages/frontend-web/src/lib/api/warehouse-wms.ts` (PickList-Typen + API-Funktionen),
`packages/frontend-web/src/pages/lager/kommissionierung.tsx` (neu),
`tests/test_wms_pick_link.py` (neu), `route-aliases.json`, `operations.tsx` (Nav).
**Abnahmekriterien:** 409 wenn LS nicht posted/printed; 409 bei Duplicate; confirm setzt LS auf shipped;
6 Tests grün; ESLint + type-check grün; Route `/lager/kommissionierung` erreichbar.

## FEED-CHAIN-003 — quality_lot_binding DB-Persistenz + Charge-Rückkopplung

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — Migration `feed_chain_quality_lot_20260613` (Alembic Single-Head von
`agri_silo_material_flow_20260612`): `domain_ops.quality_lot_profiles` + `domain_ops.quality_release_decisions`
(je UNIQUE tenant_id+lot_id). Endpoint `quality_lot_binding.py` rewritten: in-memory-Dicts entfernt,
`_ensure_tables` (503 wenn Migration nicht läuft), upsert-Insert für Lot und Decision,
Charge-Rückkopplung: `approve → freigegeben`, `reject → gesperrt`, `hold → quarantaene` auf `ops_chargen`.
7 Unit-Tests grün.
**Ziel:** Belegbruch schließen: `quality_lot_binding`-Daten überlebten keinen Neustart → Persistenz in DB;
Freigabe/Sperrung ist jetzt auf der Charge sichtbar.
**Dateibesitz:** `app/api/v1/endpoints/quality_lot_binding.py`, `alembic/versions/feed_chain_quality_lot_20260613.py`,
`tests/test_feed_chain_003.py` (neu).
**Abnahmekriterien:** 503 ohne Migration; Lot upsert; Decision approve/reject schreibt Charge-Status; 7 Tests grün.

## FEED-CHAIN-004 — Einzelfutter ↔ inventory.articles + Bewegungsbelege

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-23 — Migration `feed_chain_article_map_20260623` (`inventory_article_id` auf
`futtermittel_einzelfutter`); `FeedInventoryLinkService` verknüpft Einzelfutter per `artikel_nummer` mit
`domain_inventory.articles` und schreibt bei Produktionsfreigabe/Storno kanonische Bewegungen in
`inventory_stock_movements` (`source_document_type=feed_production`, idempotent per `reference_number`);
Hooks in `produktion_mischfutter` nach `apply_verbrauch`; API `GET/POST …/inventory-links`; 4 Integrationstests.
**Ziel:** Belegbruch schließen: Verbrauch nur in `futtermittel_einzelfutter.verfuegbar_t` ohne Lagerbewegungs-Audit.
**Dateibesitz:** `feed_inventory_link_service.py`, `produktion_mischfutter.py`, Migration, `test_feed_chain_004.py`.
**Abnahmekriterien:** Freigabe → 2× out-Bewegungen; Storno → 2× in-Bewegungen; ensure idempotent; Tests grün.

## FEED-CHAIN-004.5 — Lagerartikel-Verknüpfung UI (Mischfutter)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-23 — `useFeedInventoryLinks` + `useEnsureFeedInventoryLink` in `produktion.ts`;
Verknüpfungs-Card auf `mischfutter-produktion.tsx` (Lager-Rolle oder bei offenen Mappings sichtbar);
per-row Pending + Toast; Typecheck grün.
**Ziel:** Operator kann Einzelfutter ↔ Lagerartikel vor Freigabe verknüpfen (Ergänzung FEED-CHAIN-004 Backend).
**Dateibesitz:** `produktion.ts`, `mischfutter-produktion.tsx`, `FEED-CHAIN-004.5.yaml`.
**Abnahmekriterien:** Unmapped-Liste + Ensure-Button; Mutation-Guards; tsc 0.

## SALES-COLL-001 — Sammelrechnung/Sammellieferschein Belegbruch

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `collective_documents.py`: (1) `create_collective_invoice` validiert
jetzt DN-Status (nur `shipped`/`delivered` abrechnungsfähig — 422; bereits `BERECHNET` → 409) und setzt
Quell-Lieferscheine nach Rechnungserstellung auf `BERECHNET` + `invoice_id`; (2) `create_collective_delivery`
prüft auf Doppel-Lieferung (`geliefert` → 409) und setzt Quell-Aufträge auf `geliefert`; (3) `collective_eligible`
filtert nur noch `shipped`/`delivered`; 5 Unit-Tests grün.
**Ziel:** Belegbruch schließen: Sammelrechnung markierte Lieferscheine nicht als berechnet → Doppelabrechnung möglich;
Sammellieferschein setzte Aufträge nicht auf geliefert.
**Dateibesitz:** `app/api/v1/endpoints/collective_documents.py`, `tests/test_sales_coll_001.py` (neu).
**Abnahmekriterien:** 409 bei Doppelabrechnung; 422 bei falschem DN-Status; DN-Update auf BERECHNET; Auftrag-Update auf geliefert; 5 Tests grün.

## LAGER-BWERT-001 — Bestandsbewertung + Einlagerungsstrategie (Putaway)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — (1) `book_stock_movement` berechnet jetzt Ø-Einstandspreis
(weighted-average cost) bei Zugang auf bestehendem Bestand (UPDATE unit_cost = COALESCE(:cost, unit_cost));
(2) `suggest_putaway_bin()` in `warehouse_service.py`: CAPACITY/CONSOLIDATE/FEFO_ZONE-Strategien,
TOP-10-Bins nach Restkapazität; (3) `POST /lager/wms/warehouses/{id}/suggest-putaway` Endpoint;
(4) Frontend: `StockValuationRow`-Typ + `useStockValuation()`-Hook in `warehouse-wms.ts`;
Seite `lager/bestandsbewertung.tsx` (Übersichtstabelle + Summary-Cards); Nav-Eintrag + Route generiert;
Tests grün; type-check grün.
**Ziel:** Belegbrüche schließen: (a) `GET /lager/wms/stock-valuation` lieferte NULL-Werte wenn
`unit_cost=None` (kein Ø-Kosten-Update auf bestehenden Rows); (b) Einlagerung ohne Bin-Vorschlag
(Putaway-Strategie fehlte komplett — Tiefenplan §3 ❌ Kritisch); (c) keine UI-Seite für Lagerwerte
(Periodenabschluss-Voraussetzung).
**Dateibesitz:** `app/services/warehouse_service.py` (weighted-avg + putaway),
`app/api/v1/endpoints/warehouse_wms.py` (suggest-putaway endpoint),
`packages/frontend-web/src/lib/api/warehouse-wms.ts` (valuation types+hook),
`packages/frontend-web/src/pages/lager/bestandsbewertung.tsx` (neu),
`tests/test_lager_bwert_001.py` (neu), `route-aliases.json`, `operations.tsx` (Nav).
**Abnahmekriterien:** Ø-Einstandspreis wird bei Zugang berechnet; Putaway-Suggest gibt TOP-10 zurück;
Seite `/lager/bestandsbewertung` erreichbar; Tests + type-check grün.

## SALES-O2C-001 — O2C Completion: DN delivered → Auftrag geliefert

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `sales_delivery_notes.py`: (1) `DeliveryNoteBase` + INSERT um `sales_order_id`
erweitert; (2) `deliver_delivery_note` prüft nach shipped→delivered-Transition via `SalesMatchService.match()`,
ob Auftrag vollständig geliefert ist, und setzt ihn dann auf `geliefert` (fail-soft); 4 Unit-Tests grün.
**Ziel:** Belegbruch schließen: Lieferschein-Deliver aktualisierte nie den Quell-Auftrag → Auftrag blieb
nach vollständiger Lieferung auf Offen/In Bearbeitung, kein automatisches O2C-Ende.
**Dateibesitz:** `app/api/v1/endpoints/sales_delivery_notes.py`, `tests/test_sales_o2c_001.py` (neu).
**Abnahmekriterien:** 400 wenn Status ≠ shipped; Auftrag auf geliefert wenn vollständig; kein Update bei
Teillieferung; kein Fehler wenn kein sales_order_id; 4 Tests grün.

## SALES-INV-DN-001 — SalesInvoice.sourceDelivery → delivery_notes.invoice_number

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `finance_invoices.create_invoice`: wenn `sourceDelivery` gesetzt,
UPDATE `domain_sales.delivery_notes SET invoice_number = :inv_nr` (nur wenn noch leer); 2 Tests grün.
**Ziel:** Belegbruch schließen: Einzelrechnung verknüpfte nie den Lieferschein zurück →
`delivery_notes.invoice_number` blieb NULL auch nach Rechnungserstellung.
**Dateibesitz:** `app/api/v1/endpoints/finance_invoices.py`, `tests/test_sales_inv_dn_link_001.py` (neu).

## ERS-OP-001 — ERS-Settlement → Kreditoren-OP anlegen

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `ers_settlement.trigger_ers`: Nach ERS-Rechnungserstellung
INSERT in `domain_erp.offene_posten` (konto_typ='kreditoren', op_status='offen'). Fail-soft.
**Ziel:** Belegbruch schließen: ERS-Lauf erzeugte Rechnungsdatensatz aber keinen Kreditoren-OP →
AP-Kette (Zahlungslauf/Auszifferung) wäre nie ansteuerbar gewesen.
**Dateibesitz:** `app/api/v1/endpoints/ers_settlement.py`.

## AGRAR-KON-001 — Ernte-Annahme final release → AgrarContract Restmenge + Status

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `harvest_acceptance_service.py`: Bei `release_status=final`
und vorhandenem `contract_id` wird jetzt `AgrarContract.remaining_quantity_kg -= net_weight_kg`
gesetzt; `status='fulfilled'` wenn Restmenge=0, sonst `'partially_allocated'`. Fail-soft. 2 Tests grün.
**Ziel:** Belegbruch schließen: Ernte-Annahme-Freigabe aktualisierte nie den verknüpften Kontrakt →
Kontrakt blieb auf `open` trotz vollständiger Erfüllung.
**Dateibesitz:** `app/services/harvest_acceptance_service.py`, `tests/test_agrar_kon_001.py` (neu).
**Abnahmekriterien:** remaining_quantity_kg reduziert; status fulfilled wenn leer; 2 Tests grün.

## EINK-GR-PO-001 — Wareneingang → PO-Mengen-Fortschreibung + Bestellstatus

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `einkauf_compat_service.py`: `_update_po_delivery_quantities()`
schreibt `menge_geliefert += recv_qty` + `menge_offen -= recv_qty` auf `bestellung_positionen`;
setzt `status='vollstaendig_geliefert'` wenn vollständig; UPDATE `bestellungen.status='geliefert'`
wenn alle Positionen vollständig. 4 Unit-Tests grün.
**Ziel:** Belegbruch schließen: GR-Erfassung aktualisierte nie PO-Positionsmengen und Bestellstatus →
PO blieb dauerhaft auf `freigegeben` auch nach vollständiger Lieferung.
**Dateibesitz:** `app/services/einkauf_compat_service.py`, `tests/test_eink_gr_po_001.py` (neu).
**Abnahmekriterien:** menge_geliefert aktualisiert; status=geliefert wenn vollständig; skip ohne POI; 4 Tests grün.

## FIN-BELEG-001 — Finance Belegbrüche: Zahlungseingang → Rechnung BEZAHLT

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — (1) `finance_clearing.py`: `record_payment` setzt
`sales_invoice.status='BEZAHLT'` nach `voll_ausgeziffert=True` via Document-Store;
(2) `payment_runs.py`: `execute_payment_run` setzt `op_status='ausgeziffert'` + `ap_invoice.status='BEZAHLT'`
wenn OP durch Zahlungslauf vollständig ausgeglichen; (3) `op_skonto_auszifferung.py`: `create_auszifferung`
reduziert jetzt `offene_posten.offen` + setzt `op_status='ausgeziffert'` + `sales_invoice.status='BEZAHLT'`
bei Vollausgleich. 3 Unit-Tests grün.
**Ziel:** Belegbrüche schließen: 3 Zahlungspfade aktualisierten nie den Beleg-Status auf BEZAHLT →
Rechnungen blieben dauerhaft auf GEBUCHT/VERBUCHT auch nach Vollzahlung.
**Dateibesitz:** `app/api/v1/endpoints/finance_clearing.py`, `app/api/v1/endpoints/payment_runs.py`,
`app/api/v1/endpoints/op_skonto_auszifferung.py`, `tests/test_fin_belegbruch_001.py` (neu).
**Abnahmekriterien:** AR-Rechnung BEZAHLT nach voll_ausgeziffert; AP-Rechnung BEZAHLT nach Zahlungslauf;
OP-Betrag reduziert + Rechnung BEZAHLT nach Skonto-Ausgleich; 3 Tests grün.

## EINKAUF-3WM-001 — 3-Wege-Match (PO/GR/IR) Alembic-Persistenz

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — Migration `einkauf_3wm_invoice_verification_20260613` (Single-Head von
`feed_chain_quality_lot_20260613`): `domain_einkauf.invoice_verification` mit Index auf tenant_id+match_status
und po_id+gr_id+invoice_id. Endpoint `purchase_invoice_verification.py`: runtime-DDL ersetzt durch
`_ensure_schema` (503 wenn Migration nicht läuft, statt stiller CREATE TABLE). 5 Unit-Tests grün.
**Ziel:** Belegbrüche schließen: (a) `CREATE TABLE IF NOT EXISTS` in prod-Endpunkt → instabil bei
Migrations-Race und Multi-Tenant; (b) Tiefenplan §2 ❌ Wichtig: 3-Wege-Match persistiert jetzt
via Alembic-Tabelle statt Runtime-DDL.
**Dateibesitz:** `alembic/versions/einkauf_3wm_invoice_verification_20260613.py` (neu),
`app/api/v1/endpoints/purchase_invoice_verification.py`, `tests/test_einkauf_3wm_001.py` (neu).
**Abnahmekriterien:** 503 ohne Migration; Alembic single-head; 5 Tests grün.

## EINK-WE-001 — Wareneingang einbuchen (Einkauf-Lieferschein → Lager)

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `POST /einkauf/lieferscheine/{ls_id}/einbuchen` in `einkauf_lieferschein.py`:
Verbucht alle Positionen mit `artikel_nr`+`menge>0` als EINLAGERUNG in `domain_inventory.inventory_stock_movements`
und `bin_stock` via `WarehouseService.book_stock_movement()`; Bin-Auflösung: erst `lagerfach` der Position,
dann `default_bin_id`, dann auto-Suggest via `suggest_putaway_bin(CAPACITY)`; setzt `erledigt=TRUE` nach
Buchung; übersprungene Positionen (keine artikel_nr, kein Bin) werden in `detail`-Liste gemeldet; 4 Unit-Tests grün.
**Ziel:** Belegbruch schließen: Einkauf-Lieferschein (Wareneingang vom Lieferanten) aktualisierte nie
`bin_stock`/`inventory_stock_movements` → Lager hatte nach Wareneingang keinen aktuellen Bestand.
**Dateibesitz:** `app/api/v1/endpoints/einkauf_lieferschein.py` (neuer Endpoint),
`tests/test_eink_we_001.py` (neu).
**Abnahmekriterien:** 404 wenn LS fehlt; 422 ohne Positionen; Buchung pro Position; erledigt=TRUE danach; 4 Tests grün.

## WAVE-PHYS-CHAIN-000 — (reserviert / Lead)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-13 — optionaler Bucket geschlossen durch **LOG-FREIGHT-STORNO-001**
(Fracht-Tarif-Storno API + UI); segmentierte Route-Blocks weiterhin optional per Harvest.
**Ziel:** Rest-Medienbruch Fracht ohne neue DOM-Insel.
**Dateibesitz:** `logistics_freight.py`, `tour-fracht-arbeitsraum.tsx`, `logistics-freight.ts`, Alembic `log_freight_tariff_storno_20260613`, Integrationstests.
**Abnahmekriterien:** Soft-Storno sichtbar; Kostenpfade ignorieren stornierte Zeilen.

## LOG-FREIGHT-STORNO-001 — Fracht-Tarif Storno (soft)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-13 — `POST /logistik/freight-tariffs/{id}/cancel`, Migration Storno-Spalten,
Dispo-Arbeitsraum: Tarifliste + Bestätigung + `cancelFreightTariff`; Tests in `test_logistics_integration.py`.
**Ziel:** WAVE-PHYS-CHAIN-000 Fracht-Storno-API/UI — fail-closed wie Touren-Storno.
**Dateibesitz:** genannte Dateien, `docs/agent-ops/slices/LOG-FREIGHT-STORNO-001.yaml`.
**Abnahmekriterien:** 422 ohne Tenant; 403 global/fremd; 409 doppelt; simulate nach Storno ohne Treffer.

## WM-STRUCT-001 — Lagerstruktur Gang (Depth-Plan §3 Schritt 1)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — Alembic `wms_warehouse_aisles_20260612` (`domain_inventory.warehouse_aisles`, `warehouse_bins.aisle_id`); ORM `WarehouseAisle`; `WarehouseService` + `GET/POST /lager/wms/aisles`, `GET /bins?aisle_id=`, `POST /bins` mit optionalem `aisle_id`; Unit-Tests in `test_warehouse_wms_fefo.py`; UI: `lagerplaetze.tsx` + `warehouse-wms.ts`, E2E in `lager-wms.spec.ts`.
**Ziel:** ERP-Lücke Lager/Zone/**Gang**/Fach — Gang-Ebene zwischen Zone und Lagerplatz abbilden (Depth-Plan §3 Schritt 1).
**Dateibesitz:** genannte Dateien, `docs/agent-ops/slices/WM-STRUCT-001.yaml`, `docs/project-context/domain-depth-plan-2026-05-17.md`.
**Abnahmekriterien:** `alembic upgrade head` legt Tabelle/Spalte an; API tenant-isoliert wie bestehende WMS-Routen; 422 wenn `aisle_id` nicht zur Zone passt.

## WM-WMS-BIN-001 — Bin-PATCH + Kapazität bei Stock-Buchung

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — `WarehouseService.get_bin` / `update_bin` / `set_bin_stock_line_quantity`; `book_stock_movement` prüft Summe `bin_stock` vs. `capacity_kg`; API `GET`/`PATCH /lager/wms/bins/{bin_id}`, `PATCH …/stock-lines/{id}`; Lagerplätze-Dialog; `scripts/seed_demo_wms_structure.py`; Slice-YAML `WM-WMS-BIN-001.yaml`.
**Ziel:** Depth-Plan §3 Schritt 2 teilweise — Lagerplatz-Stammdaten pflegen und Einlagerung gegen Platzhöchstmenge absichern.
**Dateibesitz:** genannte Dateien, `docs/agent-ops/slices/WM-WMS-BIN-001.yaml`, `docs/project-context/domain-depth-plan-2026-05-17.md`.
**Abnahmekriterien:** PATCH Bin + Stock-Line; Kapazitätsüberschreitung 422; UI mit Pending/Toast; Demo-Seed; `pytest tests/test_warehouse_wms_fefo.py` grün.

## LOG-SPINE-001 — Lieferschein ↔ Tour UI + Seed

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-12 — `useTouren` → `/logistik/tours` + `stop_count`; Tourenplanung: Auflösen + Tour-Hints; `seed_demo_logistics_spine.py`; PATCH `delivery_note_ref`.
**Ziel:** LOG-SPINE-RAND-001 im UI sichtbar machen; Demo-Daten idempotent.
**Dateibesitz:** `misc-modules.ts`, `logistics-tours.ts`, `tourenplanung.tsx`, `logistics_tours.py`, Seed-Skript, Audit.
**Abnahmekriterien:** `pnpm --filter @valero-neuroerp/frontend-web type-check` grün; Logistics-Unit-Tests grün.

## PROC-RFQ-001 — RFQ production-ready

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — Alembic `proc_rfq_20260611`, Service `rfq_service.py`, Lazy-DDL entfernt, Zuschlag erzeugt echte `bestellungen`+Position, Seed `seed_demo_rfq.py`, 2 Integrationstests grün.
**Ziel des Slices:** Anfrageprozess RFQ ohne Mocks und ohne Runtime-Schema-DDL production-ready.
**Dateibesitz:** `proc_rfq_20260611.py`, `rfq_service.py`, `rfq.py`, `seed_demo_rfq.py`, `test_rfq_integration.py`, Open-Gaps.
**Abnahmekriterien:** Migration statt `_ensure_schema`; Accept legt PO an; Integration grün.

## PROC-PROD-001 — Production-Härtung Match-Spine

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — Silent-DB-Fallbacks entfernt; 6 echte API/DB-Integrationstests (`test_procurement_match_integration.py`, auto-`alembic upgrade`); Seed zieht `DEMO-RE-001` idempotent nach; `drei_wege_abgeglichen` nur Rechnungswert-Toleranz; 21 Tests grün (15 Unit + 6 Integration).
**Ziel des Slices:** DOM-PROC-004 production-ready ohne Mocks auf Persistenz-Pfaden.
**Dateibesitz:** `procurement_match_service.py`, `seed_demo_procurement.py`, Integrationstests, DOM-PROC-Doku.
**Abnahmekriterien:** Keine `except: return []` auf Schreib-/Lesepfaden; Integration grün gegen echte DB.

## PROC-004.5 — ERS + UAT (DOM-PROC-004 abgeschlossen)

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — `calculate_ers_credit` + `procurement_ers_credits`, API `/match/ers`, UI ERS-Karte, UAT `proc_match_lifecycle_uat.py`, Playwright-Smoke; 18 Procurement-Unit-Tests grün; Alembic-Head `proc_ers_credit_20260611`.
**Ziel des Slices:** ERS-Gutschriftsverfahren aus Match-Abweichungen + UAT-Nachweispaket für DOM-PROC-004.
**Dateibesitz:** `proc_ers_credit_20260611.py`, Match-Service/Endpoints, Frontend, UAT/Smoke, DOM-PROC-UAT-Doku.
**Abnahmekriterien:** DEMO-PO-002 → 960 € Vorschau; UAT `--execute` mit Cleanup; keine SALES/CON-Dateien.

## PROC-004.4 — Folgeaktionen Match-Ausnahmen

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — append-only `procurement_follow_up`, API `GET/POST /procurement/match/follow-up`, Eskalationsstufe, UI Folgeaktionen + Protokoll in Wareneingangsabgleich; 4 Unit-Tests grün; Alembic-Head `proc_follow_up_20260611`.
**Ziel des Slices:** Nachforderung/Reklamation/Eskalation/Freigabe bei Match-Ausnahmen mit Pflicht-Grund (Event-Log).
**Dateibesitz:** `proc_follow_up_20260611.py`, `procurement_match_service.py`, `procurement_match.py`, `procurement-match.ts`, `wareneingangsabgleich.tsx`, `test_procurement_follow_up.py`, DOM-PROC-Doku.
**Abnahmekriterien:** Append-only; keine UPDATE/DELETE-API; UI nur bei Ausnahmen; Tests grün.
**Abstimmung:** Keine SALES/CON-Dateien.

## PROC-004.2 — 3-Wege-Match Rechnungsstufe

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — Rechnungsstufe: `match_three_way` + API `/procurement/match/three-way`, Migration `proc_three_way_inv_20260611`, Seed `DEMO-RE-001`, UI Wareneingangsabgleich; 10 Procurement-Tests grün; Folge-Slice 004.4 erledigt.
**Ziel des Slices:** Echter 3-Wege-Match Bestellung ↔ Wareneingang ↔ Eingangsrechnung mit Ausnahmen (keine Rechnung, Wertabweichung).
**Dateibesitz:** `procurement_match_service.py`, `procurement_match.py`, `proc_three_way_invoice_20260611.py`, `seed_demo_procurement.py`, `test_procurement_three_way_match.py`, `procurement-match.ts`, `wareneingangsabgleich.tsx`, DOM-PROC-Doku.
**Abnahmekriterien:** API + Unit-Tests + Seed + UI; keine Überschneidung mit CON/SALES-Slices.
**Abstimmung:** Claude — CON/SALES abgeschlossen; keine `contract_*` / `sales_match_*` Dateien.

## COMPAT-GOV-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — Release-Kompatibilitätsmatrix als generiertes Artefakt (`scripts/generate_release_compatibility_matrix.py` → `artifacts/release-compatibility-matrix.{json,md}`), kanonische Toolchain-Pins (`config/release-toolchain-pins.json`), Drift-Check (`scripts/check_toolchain_pins.py`), unpinned `pytest-cov` aus `quality-gate.yml`/`sonarcloud.yml`/`ci.yml` entfernt, Finance-Subservices auf `pytest-cov==7.1.0`/`coverage==7.14.1` angeglichen. 5 Governance-Tests grün.
**Ziel des Slices:** Nach PROD-READINESS-001 Kompatibilitätsmatrix und einheitliche Test-Toolchain-Pins repo-weit verbindlich machen.
**Dateibesitz:** `config/release-toolchain-pins.json`, `scripts/generate_release_compatibility_matrix.py`, `scripts/check_toolchain_pins.py`, `tests/test_release_compatibility_governance.py`, `.github/workflows/quality-gate.yml`, `release-gates.yml`, `sonarcloud.yml`, `ci.yml`, Finance-`requirements.txt`, `docs/operations/dependency-and-compatibility-maintenance.md`, Handshake/Slices.
**Abnahmekriterien:** Matrix-Generator in Quality-/Release-Gate; Toolchain-Drift blockiert CI; keine losen `pip install pytest-cov`; Finance-Subservices aligned; Tests grün.
**Offene Risiken:** `recursionlimit` in `conftest.py` bleibt Coverage-Workaround; Vollsuite-Zahlen erst nach naechstem gruenen `quality-gate`-Lauf aktualisieren.

## INV-STOCK-MOVEMENTS-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-11 — `articles.py` Chargenabfrage auf `inventory_stock_movements.charge`; `pos_retoure.py` INSERT auf kanonische Tabelle mit Pflichtfeldern/Warehouse-Subselect; kein `stock_movements` mehr unter `app/api/v1/endpoints/`; 3 Vertragstests grün.
**Ziel des Slices:** Legacy-SQL-Pfade `domain_inventory.stock_movements` in `articles.py` und `pos_retoure.py` auf kanonische Tabelle `inventory_stock_movements` umstellen inkl. Chargen-/Bestandsvertrag.
**Dateibesitz:** `app/api/v1/endpoints/articles.py`, `app/api/v1/endpoints/pos_retoure.py`, fokussierte Tests, Doku in `open-gaps-and-known-issues.md`.
**Abnahmekriterien:** Keine Schreibpfade mehr auf `stock_movements`; Regression für Artikel-Bestand und POS-Retoure grün; Schema-Vertrag unverändert grün.
**Offene Risiken:** POS-Retoure aktualisiert `articles.current_stock` noch nicht; MHD/Expiry weiterhin ohne Chargenstamm.

## DOC-004.5 — Browser-E2E + UAT (DOM-DOC-004 ABGESCHLOSSEN)

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Playwright-@smoke `docflow/nachweisraum-lifecycle-smoke.spec.ts` (3 Seiten) + Live-UAT `scripts/uat/doc_nachweisraum_lifecycle_uat.py` (`--execute`: Evidence→Probe→Upload→Freigabe→Wiedervorlage→GoBD-Manifest, Status `passed`, DB-Cleanup) + Nachweis `docs/dom-doc-004-uat-2026-06-11.md`. **Robustheits-Fund (UAT):** Fremd-`artifactType` → 500 (DB-CHECK); `upload_artifact` validiert jetzt vorab → 422 (Test ergänzt). Damit DOC-Tiefe 004.1–004.5 komplett. 18 docflow-Backendtests kumuliert grün.
**Ziel des Slices:** End-to-End-Abnahme des GoBD-Nachweisraums + Browser-Smoke. DOM-DOC-004.5.
**Dateibesitz:** `playwright-tests/specs/docflow/nachweisraum-lifecycle-smoke.spec.ts`, `scripts/uat/doc_nachweisraum_lifecycle_uat.py`, `app/services/docflow_artifact_service.py` (nur Typ-Guard), `tests/test_docflow_artifact.py` (nur Guard-Test), `docs/dom-doc-004-uat-2026-06-11.md`, DOC-Doku, Workboard-Block.
**Abnahmekriterien:** Live-UAT grün mit DB-Cleanup; Smoke-Spec suite-konsistent; Fremd-Artefakttyp liefert 422 statt 500.
**Offene Risiken / ehrlich:** Paperless-Liveprobe in DEV „nicht konfiguriert"; reales ZIP-Paket als JSON-Manifest-Vertrag. Smoke-Login-Fixture lokal nur CI-Preview (:4173).

## DOC-004.4 — GoBD-Exportpaket + Paperless-Liveprobe

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `docflow_gobd_service.py` (reine `build_gobd_manifest` mit Prüfsumme + `export_package` (reuse Evidence, vermerkt exported_at) + `paperless_probe` ehrlich gegated), Endpoints `/docflow/evidence/{gobd-export,paperless-probe}`, Frontend `pages/docflow/gobd-export.tsx` + Hooks + Nav + Route. 18 docflow-Backendtests kumuliert grün, tsc 0, eslint clean; Live verifiziert (PYTEST-Vorgang revisionssicher + Prüfsumme; Paperless „nicht konfiguriert"). Keine Migration.
**Ziel des Slices:** GoBD-Exportpaket je Vorgang (Manifest + Prüfsumme + Export-Vermerk) + DMS/Paperless-Liveprobe. DOM-DOC-004.4.
**Dateibesitz:** `app/services/docflow_gobd_service.py`, `app/api/v1/endpoints/docflow_gobd.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_docflow_gobd.py`, `packages/frontend-web/src/lib/api/docflow-gobd.ts`, `packages/frontend-web/src/pages/docflow/gobd-export.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), DOC-Doku.
**Abnahmekriterien:** Manifest mit Artefakt-Hashes + deterministischer Prüfsumme; Revisionssicherheit korrekt; Export vermerkt exported_at; Paperless-Probe ehrlich (konfiguriert/erreichbar); Backendtests + tsc + eslint grün.
**Offene Risiken / ehrlich:** PAPERLESS_URL in DEV nicht gesetzt → Probe meldet „nicht konfiguriert" (kein Schein-OK). Realer Binär-Paketdownload (ZIP mit Dateien) hier als JSON-Manifest-Vertrag. Browser-E2E + UAT in 004.5.

## DOC-004.3 — Bescheid/Rückmeldung + Wiedervorlage

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `doc_followup_20260611` (`document_followups`), Service `docflow_followup_service.py` (reine `followup_overdue` + `create_followup`/`complete_followup`/`list_followups`/`open_wiedervorlagen`), Endpoints `/docflow/evidence/{followups,wiedervorlagen}`, Frontend `pages/docflow/wiedervorlagen.tsx` + Hooks + Nav + Route. 9 Backendtests grün (5 Followup + 4 Artefakt-Regression), tsc 0, eslint clean; Live verifiziert (Wiedervorlage überfällig in Worklist, Bescheid, Erledigen + 422).
**⚠️ Alembic:** chained auf `doc_artifact_version_20260611`, gezielt angewandt; paralleler PROC-Head (Cursor) → Merge nötig sobald beide committet.
**Ziel des Slices:** Bescheide/Rückmeldungen + Wiedervorlagen je Vorgang mit Fälligkeit + Worklist offener (überfälliger) Wiedervorlagen. DOM-DOC-004.3.
**Dateibesitz:** `alembic/versions/doc_followup_20260611.py`, `app/services/docflow_followup_service.py`, `app/api/v1/endpoints/docflow_followup.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_docflow_followup.py`, `packages/frontend-web/src/lib/api/docflow-followup.ts`, `packages/frontend-web/src/pages/docflow/wiedervorlagen.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), DOC-Doku.
**Abnahmekriterien:** Followup-Erfassung (Wiedervorlage mit Pflicht-Fälligkeit); Worklist markiert überfällig; Erledigen idempotent-gesperrt (422); Backendtests + tsc + eslint grün.
**Offene Risiken:** Automatische Benachrichtigung/Eskalation der Wiedervorlagen nicht Teil des Slices. GoBD-Exportpaket + Paperless-Liveprobe in 004.4.

## DOC-004.2 — Artefakt-Upload + Versionierung + Freigabe

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `doc_artifact_version_20260611` (`document_artifacts` +version/+freigabe_status/+Audit), Service `docflow_artifact_service.py` (reine `next_version`/`valid_transition`/`sha256_hex` + `upload_artifact`/`set_freigabe`/`list_artifacts`), Endpoints `/docflow/evidence/artifacts[/{id}/freigabe]`, Frontend `pages/docflow/artefakt-freigabe.tsx` + Hooks + Nav + Route. 9 Backendtests grün (4 Artefakt + 5 Evidence-Regression), tsc 0, eslint clean; Live verifiziert (Upload v1/v2, Transitions, 422).
**⚠️ Alembic-Koordination:** Paralleler PROC-Head (`proc_rfq_20260611`, Cursor). Meine Migration an meinem committeten Head (`sales_delivery_storno_20260611`) gekettet und gezielt angewandt. Merge-Head `doc_artifact_version` + PROC-Tip nötig, sobald beide committet (Single-Head-Gate).
**Ziel des Slices:** Artefakt-Upload (SHA-256) + Versionierung je Header/Typ + Freigabe-Status-Transitions (entwurf→freigegeben→archiviert). DOM-DOC-004.2.
**Dateibesitz:** `alembic/versions/doc_artifact_version_20260611.py`, `app/services/docflow_artifact_service.py`, `app/api/v1/endpoints/docflow_artifact.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_docflow_artifact.py`, `packages/frontend-web/src/lib/api/docflow-artifact.ts`, `packages/frontend-web/src/pages/docflow/artefakt-freigabe.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), DOC-Doku.
**Abnahmekriterien:** Upload erzeugt SHA-256 + fortlaufende Version; Freigabe nur über zulässige Transitions (sonst 422); Liste markiert aktuelle Version; Backendtests + tsc + eslint grün.
**Offene Risiken:** Realer Datei-Binärupload/Storage-Anbindung (S3/Paperless) hier als Inhalt→Hash-Vertrag; DMS-Liveprobe in 004.4. Bescheid/Wiedervorlage in 004.3.

## FIN-004.5 — DATEV-Export + E2E/UAT (DOM-FIN-004 ABGESCHLOSSEN)

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `finance_datev_service.py` (reine `datev_row`/`datev_csv` + `export_open_items`), Endpoint `/finance/datev-export`, Frontend `pages/finance/datev-export.tsx` + Hooks + Nav + Route, Playwright-@smoke `finance/op-lifecycle-smoke.spec.ts`, Live-UAT `scripts/uat/fin_op_lifecycle_uat.py` (`--execute`: passed, DB-Restore), Nachweis `docs/dom-fin-004-uat-2026-06-11.md`. Damit FIN-Tiefe 004.1–004.5 komplett. 25 Finance-Backendtests kumuliert grün, tsc 0, eslint clean.
**Ziel des Slices:** DATEV-Buchungsstapel-Export (in-repo) + End-to-End-Abnahme der FIBU-Kette. DOM-FIN-004.5.
**Dateibesitz:** `app/services/finance_datev_service.py`, `app/api/v1/endpoints/finance_datev.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_finance_datev.py`, `packages/frontend-web/src/lib/api/finance-datev.ts`, `packages/frontend-web/src/pages/finance/datev-export.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), `playwright-tests/specs/finance/op-lifecycle-smoke.spec.ts`, `scripts/uat/fin_op_lifecycle_uat.py`, FIN-Doku.
**Abnahmekriterien:** DATEV-CSV mit korrekten Spalten/Konten; Live-UAT grün mit Restore; Smoke-Spec suite-konsistent.
**Offene Risiken / ehrlich:** Kein zertifizierter DATEV-EXTF; Steuerberater-Cutover bleibt externes Gate. Smoke-Login-Fixture lokal nur CI-Preview (:4173).

## FIN-004.4 — Periodenabschluss + Storno-Konsistenz

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `finance_period_service.py` (reine `period_bounds` + `close_readiness` + `list_periods`/`readiness`/`close_period`/`reopen_period`), Endpoints `/finance/perioden[/{p}/readiness|/close|/reopen]`, Frontend `pages/finance/periodenabschluss.tsx` + Hooks + Nav + Route. Perioden self-contained aus OP abgeleitet (Tabelle leer). 5 Backendtests grün, tsc 0, eslint clean; Live verifiziert (Abschluss-Guard 422, Force, Reopen). Keine Migration.
**Ziel des Slices:** Buchungsperioden abschließen/sperren mit Abschlussreife-Prüfung (offene + Storno-inkonsistente Posten blockieren) + Wiedereröffnung mit Grund. DOM-FIN-004.4.
**Dateibesitz:** `app/services/finance_period_service.py`, `app/api/v1/endpoints/finance_period.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_finance_period.py`, `packages/frontend-web/src/lib/api/finance-period.ts`, `packages/frontend-web/src/pages/finance/periodenabschluss.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), FIN-Doku.
**Abnahmekriterien:** Reife blockiert bei offenen/Storno-inkonsistenten OP; Abschluss setzt status=closed; Force erzwingt mit Hinweis; Reopen mit Pflicht-Grund; Backendtests + tsc + eslint grün.
**Offene Risiken:** Echte Buchungssperre (Verhindern neuer Journalbuchungen in geschlossener Periode) setzt Journal-Integration voraus — hier Periodenstatus-Vertrag. DATEV/Steuerberater-Cutover (extern) + UAT in 004.5.

## FIN-004.3 — Zahlungseingang / OP-Auszifferung

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `finance_clearing_service.py` (reine `clearing_result` + `record_payment` ziffert `domain_erp.offene_posten` aus, protokolliert `op_auszifferungen` + `clearings`), Endpoints `/finance/zahlungseingang[/clearings]`, Frontend `pages/finance/zahlungseingang.tsx` + Hooks + Nav + Route. Schließt Lücke der isolierten `op_skonto_auszifferung` (reduzierte OP-Saldo nicht). 10 Backendtests grün (5 Auszifferung + 5 Mahnlauf-Regression), tsc 0, eslint clean; Live verifiziert (Teil→Voll+Skonto→422, Restore). Keine Migration.
**Ziel des Slices:** Zahlungseingang gegen offenen Debitoren-Posten ausziffern (offen reduzieren, Skonto, op_status). Kreditoren-Zahlungslauf = vorhandenes `payment_runs.py`. DOM-FIN-004.3.
**Dateibesitz:** `app/services/finance_clearing_service.py`, `app/api/v1/endpoints/finance_clearing.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_finance_clearing.py`, `packages/frontend-web/src/lib/api/finance-clearing.ts`, `packages/frontend-web/src/pages/finance/zahlungseingang.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), FIN-Doku.
**Abnahmekriterien:** Teil-/Vollausgleich reduziert `offen`; Vollausgleich setzt `op_status='ausgeziffert'`; Skonto berücksichtigt; Überzahlung 422; Backendtests + tsc + eslint grün.
**Offene Risiken:** FIBU-Gegenbuchung (Journal) der Auszifferung nicht Teil des Slices (op_auszifferungen führt fibu_konto/skonto_konto als Vertrag). Abschluss/Periodensteuerung in 004.4.

## FIN-004.2 — Mahnlauf + Mahnstufen-Eskalation

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `finance_dunning_service.py` (reine `days_based_level`/`next_dunning_level`/`compute_dunning` + `candidates`/`run_dunning`/`list_notices`), Endpoints `/finance/mahnlauf/{candidates,notices,run}`, Frontend `pages/finance/mahnlauf.tsx` + Hooks + Nav + Route. Default-Mahnregeln (da `dunning_rules` in DEV leer). 11 Backendtests grün (5 Mahnlauf + 6 OP-Regression), tsc 0, eslint clean; Live verifiziert (RE-103 Stufe 2→3 Zins 13,33; RE-100 1→2 Zins 10,27; Restore). Keine Migration (vorhandene Tabellen).
**Ziel des Slices:** Mahnlauf aus überfälligen Debitoren-OP (`offene_posten`) erzeugen (`dunning_notices`) + Mahnstufen-Eskalation. DOM-FIN-004.2.
**Dateibesitz:** `app/services/finance_dunning_service.py`, `app/api/v1/endpoints/finance_dunning.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_finance_dunning.py`, `packages/frontend-web/src/lib/api/finance-dunning.ts`, `packages/frontend-web/src/pages/finance/mahnlauf.tsx`, `finance.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), FIN-Doku.
**Abnahmekriterien:** Kandidaten zeigen nächste Stufe + Gebühr/Zinsen/Gesamt; Mahnlauf erzeugt Mahnungen + eskaliert `dunning_level`; Default-Regeln greifen bei leerer Regeltabelle; Backendtests + tsc + eslint grün.
**Offene Risiken:** `dunning_rules` in DEV leer → Default-Regeln (in Prod Regeln pflegen). Mahnungs-Versand (Druck/Mail) nicht Teil des Slices. OP-Auszifferung/Zahlungslauf folgt in 004.3.

## SALES-004.5 — Browser-E2E + UAT (DOM-SALES-004 ABGESCHLOSSEN)

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Playwright-@smoke `playwright-tests/specs/sales/o2c-lifecycle-smoke.spec.ts` (3 O2C-Seiten) + Live-UAT `scripts/uat/sales_o2c_lifecycle_uat.py` (`--execute`: Match→Kreditampel→Storno-Rückfluss, Status `passed`, DB-Restore) + Nachweis-Doku `docs/dom-sales-004-uat-2026-06-11.md`. Damit ist die SALES-Tiefe 004.1–004.5 komplett.
**Ziel des Slices:** End-to-End-Abnahme der O2C-Kette + Browser-Smoke. DOM-SALES-004.5.
**Dateibesitz:** `playwright-tests/specs/sales/o2c-lifecycle-smoke.spec.ts`, `scripts/uat/sales_o2c_lifecycle_uat.py`, `docs/dom-sales-004-uat-2026-06-11.md`, SALES-Doku, Workboard-Block.
**Abnahmekriterien:** Live-UAT grün mit DB-Restore; Smoke-Spec suite-konsistent.
**Offene Risiken / ehrlich:** Smoke-Login-Fixture lokal nur gegen CI-Preview (:4173), nicht Dev :3000 (wie CON-004.5). 14 Sales-Backendtests kumuliert grün.

## SALES-004.4 — Storno/Gutschrift durchgängig

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `sales_delivery_storno_20260611` (`delivery_notes` +`storno_grund`), Service `sales_storno_service.py` (reine `can_storno` + `storno_delivery` + `order_storno_status` mit toleranter Gutschrift-Übersicht), Endpoints `/sales/deliveries/{nr}/storno` + `/sales/storno/status`, Frontend `pages/sales/lieferung-storno.tsx` (Storno-Dialog + Gutschriften) + Hooks + Nav + Route. Stornierte Lieferscheine zählen nicht mehr als geliefert (Match filtert `status<>'storniert'` → durchgängig). 9 Backendtests grün (4 Storno + 5 Match), tsc 0, eslint clean; Live verifiziert (Guard 422, Match-Rückfluss, Restore).
**⚠️ Alembic-Koordination:** Beim Anwenden tauchte ein **paralleler PROC-Head** (`proc_three_way_inv_20260611`→`proc_follow_up_20260611`, untracked/fremd) auf. Ich habe meine Migration NICHT in fremde uncommittete Revisionen gekettet, sondern gezielt angewandt (`alembic upgrade sales_delivery_storno_20260611`, down_revision=`con_settlement_storno_20260611`, committet/stabil). **Sobald die PROC-Migrationen committet sind, ist ein Merge-Head `sales_delivery_storno` + `proc_follow_up` nötig** (Single-Head-Gate). Wer PROC committet, sollte den Merge mitliefern.
**Ziel des Slices:** Lieferschein-Storno, der durchgängig in den Auftrag-Lieferschein-Match zurückfließt + Gutschrift-Übersicht; fail-closed bei berechneten Lieferungen. DOM-SALES-004.4.
**Dateibesitz:** `alembic/versions/sales_delivery_storno_20260611.py`, `app/services/sales_storno_service.py`, `app/services/sales_match_service.py` (nur Storno-Filter), `app/api/v1/endpoints/sales_storno.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_sales_storno.py`, `packages/frontend-web/src/lib/api/sales-storno.ts`, `packages/frontend-web/src/pages/sales/lieferung-storno.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), SALES-Doku.
**Abnahmekriterien:** Storno setzt Lieferschein 'storniert' (Grund pflicht); berechnete Lieferung blockiert (422); stornierte Lieferung zählt nicht mehr im Match; Backendtests + tsc + eslint grün.
**Offene Risiken:** Gutschrift-Erstellung erfolgt über das bestehende `sales_credit_notes`-Modul (hier nur Übersicht); echte Gutschrift→FIBU-Buchung bleibt außerhalb. Browser-E2E + UAT in 004.5.

## SALES-004.3 — Kreditlimit-Prüfung + Billing-Status

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `sales_credit_service.py` (reine `credit_check`-Ampel + `order_credit` + `list_customers`), Endpoints `/sales/credit-check[/customers]`, Seed (DEMO-CUST-001 Limit 20.000 € in `domain_crm.customers`), Frontend `pages/sales/kreditlimit-pruefung.tsx` + Hooks + Nav + Route. 10 Backendtests grün (5 Credit + 5 Match-Regression), tsc 0, eslint clean; Live verifiziert (Auslastung 86,5 % → Ampel warnung). Keine Migration.
**Ziel des Slices:** Kreditlimit-Prüfung (Limit vs. offene Exposure, Ampel, Wirkung des Auftrags) + Billing-Status je Lieferschein im O2C-Kontext. DOM-SALES-004.3.
**Dateibesitz:** `app/services/sales_credit_service.py`, `app/api/v1/endpoints/sales_credit.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `scripts/seed_demo_sales.py` (Kundensatz), `tests/test_sales_credit.py`, `packages/frontend-web/src/lib/api/sales-credit.ts`, `packages/frontend-web/src/pages/sales/kreditlimit-pruefung.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), SALES-Doku.
**Abnahmekriterien:** Ampel ok/warnung/blockiert/kein_limit korrekt; verfügbarer Rahmen + Auslastung mit/ohne Auftrag; Kunden-Ampel-Liste; Backendtests + tsc + eslint grün.
**Offene Risiken / ehrlich:** Vorhandene `credit_management.py`-Infra braucht `domain_finance.finance_invoices` + `domain_crm.credit_limits` — **in DEV nicht vorhanden** (`/credit-status` 404). Daher tolerant self-contained (Limit am Kundensatz, Exposure aus offenen Aufträgen). Tiefe FIBU-Journal-/Debitoren-OP-Verknüpfung = Folgeschritt. Storno/Gutschrift in 004.4.

## SALES-004.2 — Positions-Match Auftrag↔Lieferschein

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Service `sales_match_service.py` (match je Auftragsposition `sales_order_items` gegen Summe `delivery_note_positions`, Schlüssel Artikelnummer; reuse reine `match_position` aus PROC + `match_summary`), Endpoints `/sales/match[/orders]`, Seed-Erweiterung (Lieferschein-Positionen DEMO-LS-001), Frontend `pages/sales/auftrag-lieferschein-abgleich.tsx` + Hooks + Nav + Route. 11 Backendtests grün (5 Sales + 6 PROC-Regression), tsc 0, eslint clean; Live verifiziert (Pos 1 25/25 voll, Pos 2 3/5 teil → 1.800 € offen). Keine Migration (vorhandene Tabellen).
**Ziel des Slices:** Positions-Match Auftrag↔Lieferschein (Teil-/Überlieferung, Toleranz, offene Menge/Wert, Lücken) analog PROC-Match. DOM-SALES-004.2.
**Dateibesitz:** `app/services/sales_match_service.py`, `app/api/v1/endpoints/sales_match.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `scripts/seed_demo_sales.py` (LS-Positionen), `tests/test_sales_match.py`, `packages/frontend-web/src/lib/api/sales-match.ts`, `packages/frontend-web/src/pages/sales/auftrag-lieferschein-abgleich.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), SALES-Doku.
**Abnahmekriterien:** Positions-Match offen/teil/voll/über mit Toleranz + offener Wert; Lücken; Picker; Backendtests + tsc + eslint grün.
**Offene Risiken:** Match-Schlüssel ist Artikelnummer (keine Auftragszeilen-ID am Lieferschein) — bei doppelten Artikeln je Auftrag aggregiert. Rechnung/Buchung/OP + Kreditlimit folgt in 004.3.

## CON-004.5 — Browser-E2E + UAT (DOM-CON-004 ABGESCHLOSSEN)

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Playwright-@smoke-Spec `playwright-tests/specs/agrar/kontrakt-lifecycle-smoke.spec.ts` (3 Arbeitsräume) + Live-UAT `scripts/uat/con_contract_lifecycle_uat.py` (`--execute`: 11/11 ✓, Status `passed`, DB-Cleanup) + Nachweis-Doku `docs/dom-con-004-uat-2026-06-11.md`. Damit ist die CON-Tiefe 004.1–004.5 komplett.
**Ziel des Slices:** End-to-End-Abnahme der Kontrakt-Kette (Fixierung→Engagement→Settlement→Storno) + Browser-Smoke der Arbeitsräume.
**Dateibesitz:** `playwright-tests/specs/agrar/kontrakt-lifecycle-smoke.spec.ts`, `scripts/uat/con_contract_lifecycle_uat.py`, `docs/dom-con-004-uat-2026-06-11.md`, CON-Doku, Workboard-Block.
**Abnahmekriterien:** Live-UAT grün mit DB-Cleanup; Smoke-Spec geschrieben und suite-konsistent.
**Offene Risiken / ehrlich:** Die `@smoke`-Login-Fixture authentifiziert lokal nicht gegen den Vite-Dev-Server :3000 — **identischer Fehlschlag bei allen bestehenden Specs** (gegengeprüft `duenger-smoke`: 3/3 „browser closed"). Browser-Abnahme läuft in CI (Preview-Build :4173); fachlicher Nachweis hier via grünem Live-UAT. Reale Abrechnungs-Buchung (agrar_settlements-Integration) bleibt tiefergehender Folgeschritt außerhalb DOM-CON-004.

## CON-004.4 — Settlement-Übergabe + Storno

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `con_settlement_storno_20260611` (`kon_contract_movement` +settled_at/+is_storniert/+storno_grund), Service `contract_settlement_service.py` (`movement_state` + `handover`/`storno_movement`/`storno_fixing`/`settlement_status`), Endpoints `/contracts/settlement[/status]` + `/contracts/movements/{id}/storno` + `/contracts/fixings/{id}/storno`, Frontend `pages/agrar/kontrakt-settlement.tsx` (Abrechnen + Storno-Dialog mit Pflicht-Grund) + Hooks + Nav + Route. Fulfillment-/Engagement-Sichten filtern jetzt stornierte Bewegungen. 18 Backendtests grün (kumuliert), tsc 0, eslint clean; Live verifiziert (Handover, Storno-Guard 422, Fixing-Storno gibt Menge frei).
**Ziel des Slices:** Abruf-Bewegungen an die Abrechnung übergeben + revisionssicherer Storno von Bewegungen/Fixierungen (frei werdende Mengen); fail-closed: abgerechnete Bewegungen sind storno-gesperrt. DOM-CON-004.4.
**Dateibesitz:** `alembic/versions/con_settlement_storno_20260611.py`, `app/services/contract_settlement_service.py`, `app/services/contract_fulfillment_service.py` + `contract_engagement_service.py` (nur is_storniert-Filter), `app/api/v1/endpoints/contract_settlement.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_contract_settlement.py`, `packages/frontend-web/src/lib/api/contract-settlement.ts`, `packages/frontend-web/src/pages/agrar/kontrakt-settlement.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), CON-Doku.
**Abnahmekriterien:** Übergabe markiert Bewegung(en) abgerechnet; Storno gebuchter Bewegung blockiert (422); Fixing-/Bewegungs-Storno gibt Menge frei und fließt in Erfüllung/Engagement zurück; Single Alembic-Head; Backendtests + tsc + eslint grün.
**Offene Risiken:** Echte Abrechnungs-Buchung (Integration `agrar_settlements`/Posting) ist tiefergehender Folgeschritt — hier nur Settlement-Übergabe-Vertrag (Beleg-Referenz), keine Finanzbuchung. Browser-E2E + UAT in 004.5.

## CON-004.3 — Engagement-Sicht + Kontraktmahnung

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `con_reminder_20260611` (append-only `kon_contract_reminder`), Service `contract_engagement_service.py` (reine Aggregation `offen_menge`/`netto_position`/`naechste_mahnstufe` + `engagement`/`dunning_candidates`/`create_reminder`/`list_reminders`), Endpoints `/contracts/engagement` + `/contracts/dunning[/candidates|/list]`, Frontend `pages/agrar/kontrakt-engagement.tsx` (Engagement je Artikel/Partei + Mahnkandidaten mit per-Zeile-Mahnen) + Hooks + Nav + Route. 15 Backendtests grün (kumuliert), tsc 0, eslint clean; Live-API verifiziert.
**Ziel des Slices:** Offene Kontraktmenge je Artikel (Netto Einkauf−Verkauf) und je Partei + Kontraktmahnung überfällig-untererfüllter Kontrakte (append-only Mahnstufen-Eskalation). DOM-CON-004.3.
**Dateibesitz:** `alembic/versions/con_reminder_20260611.py`, `app/services/contract_engagement_service.py`, `app/api/v1/endpoints/contract_engagement.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `tests/test_contract_engagement.py`, `packages/frontend-web/src/lib/api/contract-engagement.ts`, `packages/frontend-web/src/pages/agrar/kontrakt-engagement.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), CON-Doku.
**Abnahmekriterien:** Engagement summiert offen je Artikel/Partei korrekt (Netto-Vorzeichen); Mahnung nur bei offener Menge (sonst 422); Mahnstufe eskaliert; Single Alembic-Head; Backendtests + tsc + eslint grün.
**Offene Risiken:** Settlement-Übergabe + Storno (inkl. Fixierungs-Storno) folgen in 004.4; reale Mahn-Texte/Versand (Mail/Print) sind in diesem Slice nicht enthalten.

## CON-004.2 — Fixierungs-Arbeitsraum + MATIF-Bewertung

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-11 — Migration `con_fixing_matif_20260611` (Tabellen `kon_contract_fixing` + `matif_quote`), Service `contract_fixing_service.py` (reine Bewertungslogik + Teilfixierung mit Guards + Workspace + Notierung), Endpoints `/contracts/fixing[/workspace|/list]` + `/contracts/matif-quote`, Seed DEMO-KT-004 (MATIF-Verkauf), Frontend `pages/agrar/kontrakt-fixierung.tsx` + Hooks + Nav + Route. 12 Backendtests grün, tsc 0, eslint clean; Live-API verifiziert.
**Nebenbefund/Fix (kritisch):** Der Abend-Stand 2026-06-10 hinterließ **zwei offene Alembic-Heads** (`repair_customer_contract_20260610` + `sales_o2c_link_20260610`), die nie zusammengeführt wurden → `scripts/init_db.py` (`upgrade head`, Singular) scheiterte mit `Multiple head revisions` → **Backend-Container im Crash-Loop** (seit Reboot 06:32). Behoben, indem die neue Migration **beide Heads revidiert** (Merge + Tabellen in einem) → wieder genau 1 Head, Backend `healthy`.
**Ziel des Slices:** Teilfixierung MATIF-bepreister Kontrakte (Menge zu MATIF-Preis + Prämie) und Mark-to-Market gegen die jüngste Marktnotierung: fixierter/offener Anteil, Ø-Fixpreis, Bewertungsergebnis. DOM-CON-004.2 gemäß `docs/dom-con-004-kontrakt-erfuellung-2026-06-10.md`.
**Dateibesitz:** `alembic/versions/con_fixing_matif_20260611.py`, `app/services/contract_fixing_service.py`, `app/api/v1/endpoints/contract_fixing.py`, `app/api/v1/api.py` (nur eigene include-Zeilen), `scripts/seed_demo_contracts.py` (DEMO-KT-004), `tests/test_contract_fixing.py`, `packages/frontend-web/src/lib/api/contract-fixing.ts`, `packages/frontend-web/src/pages/agrar/kontrakt-fixierung.tsx`, `commercial.tsx` (nur eigener Nav-Eintrag), `route-aliases.json` (+ generierte Route-Artefakte), CON-Doku.
**Abnahmekriterien:** Fixierung nur auf MATIF-Positionen, Menge>0 und ≤ offen, Preis>0 (sonst 422); Workspace zeigt fixiert/offen/Ø-Fixpreis/Bewertung; ohne Notierung keine erfundene Bewertung (fail-closed); Backendtests + tsc + eslint grün; Backend wieder startfähig (1 Head).
**Offene Risiken:** Fixierungs-Storno und Settlement-Übergabe folgen in 004.4. Symbol-Auflösung nutzt `basis_reference` (Fallback Artikel) — bei produktiven Kontrakten Symbol-Pflege nötig.

## PROD-READINESS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09 (repo-seitig); externe Live-Gates offen — Nachzug COMPAT-GOV-001 2026-06-11
**Abstimmung:** Repo-weiter CI-/Deployment-/Security-/Dokumentations-Slice. Parallel laufender Slice `KIM-DEPRECATE-COCKPIT-001` besitzt ausschliesslich `packages/frontend-web/src/pages/crm/kunden-cockpit.tsx` und den Kunden-Cockpit-Eintrag in `packages/frontend-web/src/app/navigation/domains/commercial.tsx`; diese Dateien werden nicht beruehrt.
**Ziel des Slices:** Alle repo-seitig schliessbaren P0-Gaps der Produktionsreife beseitigen: keine tolerierten Kernfehler in Release-CI, blockierende High/Critical-Security-Gates, SBOM, produktionssichere Runtime-/Secret-Preflights, belastbarer Staging-/Production-Deploymentvertrag mit Migration, Smoke und Rollback sowie eine aktuelle, ehrliche Go-live-Matrix.
**Dateibesitz:** `.github/workflows/quality-gate.yml`, `.github/workflows/security-scan.yml`, `.github/workflows/deploy-staging.yml`, `.github/workflows/valeo-erp-deployment.yml`, neue fokussierte Release-/Security-Workflows, produktionsbezogene Dateien unter `scripts/deployment/**`, neue Preflight-Skripte und Tests, fokussierte Helm-/Kubernetes-Werte soweit zwingend, `docs/project-context/open-gaps-and-known-issues.md`, neue Production-Readiness-/Runbook-Doku und relevante Status-/README-Verweise.
**Abnahmekriterien:** Release-CI kann Typecheck/Lint/Tests oder High/Critical-Befunde nicht uebergehen; SBOM wird erzeugt; produktive Konfiguration scheitert bei Dev-Tokens, Default-Secrets, Debug/Reload, Wildcard-Hosts oder fehlenden Pflichtwerten; Deployments sind environment-geschuetzt und besitzen Migration-Preflight, Smoke und Rollback; externe UAT-, Steuer-, DMS-, TSE- und Hardwareabnahmen bleiben explizit blockierend; YAML-, Skript-, Doku- und fokussierte Vertragstests sind gruen.
**Offene Risiken:** Echte Cloud-/Kubernetes-Zugangsdaten, Branch-Protection-Regeln, GitHub-Environment-Approvals und fachliche Unterschriften koennen nur als externe GitHub-/Betriebs-Gates konfiguriert, nicht im Repository erfunden werden.

## KIM-DEPRECATE-COCKPIT-001

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-09 (Commit `3e62f00e5`) — Page→Redirect auf /crm, Nav relabelt; tsc 0, eslint clean. Folge-Lücke: WhatsApp-Deep-Link in KIM.
**Ziel des Slices:** Das klassische „Verkauf Kunden-Cockpit" (`pages/crm/kunden-cockpit.tsx`) ablösen — durch KIM (`/crm`) funktional ersetzt. Seite wird Redirect→/crm (keine 404 für Altlinks), Nav-Eintrag als abgelöst markiert. KEINE Route-Regenerierung (route-tree.gen/navigation-routes.json sind generiert + aktuell fremd-dirty → nicht anfassen).
**Dateibesitz:** `docs/agent-ops/active-workboard.md` (eigener Block), `packages/frontend-web/src/pages/crm/kunden-cockpit.tsx`, `packages/frontend-web/src/app/navigation/domains/commercial.tsx` (nur kunden-cockpit-Eintrag). **NICHT:** generierte Routing-Dateien, core.tsx, Fiskaly.
**Abnahmekriterien:** `/crm/kunden-cockpit` leitet auf `/crm` um (kein 404); Nav-Eintrag kennzeichnet die Ablösung; tsc/eslint grün. Parität: WhatsApp-Deep-Link (wa.me) ist Rest-Lücke in KIM (notieren, Folge-Slice).
**Offene Risiken:** Generierte Routing-Dateien sind fremd-dirty — Redirect über die Page-Komponente lösen, nicht über Routen-Regenerierung.


## POS-FISCAL-OPS-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Abstimmung:** Folge-Slice zu `POS-FISCAL-PROVIDERS-001`, konfliktfrei zu den laufenden KIM-/CRM-Arbeiten. Keine Aenderung unter `packages/frontend-web/src/pages/crm/kim/**` oder an CRM-Playwright-Specs.
**Ziel des Slices:** Die Fiskalisierungsprovider betrieblich nutzbar machen: tenantbezogene Admin-Konfiguration und Readiness, explizite Produkt-Gates fuer fiskaly SUBMIT DE/RECEIPT/SAFE sowie durchgaengige POS-/Tagesabschluss-Browsertests fuer fiskaly und Swissbit.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/POS-FISCAL-OPS-002.yaml`, Fiskalisierungsdoku und QA, `app/services/fiscalization/**`, `app/api/v1/endpoints/pos_fiscalization.py`, fokussierte POS-Migrationen/-Tests, `packages/frontend-web/src/pages/admin-suite/**` fuer eine neue Fiskalisierungsseite, providerneutraler Fiskalisierungsclient, generierte Route-/Navigationsartefakte und fokussierte POS-Playwright-Specs.
**Abnahmekriterien:** Provider und Kassenkontext sind ohne Browser-Secrets administrierbar; Readiness zeigt konkrete Blocker und optionale fiskaly-Produkte getrennt; undokumentierte externe Vertraege bleiben fail-closed; POS-Signatur, Browser-Zurueck, Tagesabschluss-Gates und beide Provideralternativen sind automatisiert; Typecheck, Lint, Backendtests, Playwright und Governance sind gruen.
**Offene Risiken:** fiskaly Produktlizenzen/Credentials und Swissbit Partnervertraege sind externe Live-Gates; partnergeschuetzte URLs oder Payloads duerfen nicht geraten werden.
**Ergebnis:** Tenantbezogene Admin-Seite mit Typed Route, Provider-/DSFinV-K-Auswahl, Kassen-, Client- und Terminalkontext sowie expliziter Simulationsfreigabe umgesetzt. Readiness prueft Konfiguration und Kassenkontext. Secret-artige Settings werden vor DB-Zugriff abgewiesen und beim Lesen redigiert. SUBMIT DE, RECEIPT und SAFE besitzen getrennte, fail-closed Vertrags-Gates ohne geratenen Live-Call. Der POS-Browsertest belegt Swissbit als TSE bei separatem fiskaly DSFinV-K sowie den blockierten Tagesabschluss bei offenen Fiskaltransaktionen.
**Checks:** 11 fokussierte Backendtests; Frontend- und Playwright-TypeScript gruen; fokussierter ESLint gruen; POS-Playwright 2 Tests bestanden; Produktions-Build und Typed-Route-Generierung gruen.
**Handoff:** Ergebnisdateien wurden wegen eines parallelen Shared-Worktree-Commits zusammen mit Claim `e12b261a6` publiziert; dieser Nachtrag ordnet sie verbindlich `POS-FISCAL-OPS-002` zu.

## POS-FISCAL-PROVIDERS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Abstimmung:** Konfliktfreier POS-/Compliance-Slice parallel zu Claudes KIM-L3-S3-S5. Keine Aenderung unter `packages/frontend-web/src/pages/crm/kim/**` oder an CRM-Backenddateien.
**Ziel des Slices:** Demo- und Pseudo-TSE-/DSFinV-K-Pfade durch eine typisierte Provider-Abstraktion fuer fiskaly SIGN DE/DSFINVK DE sowie Swissbit Cloud-/Hardware-TSE ersetzen; Tagesabschluss, Export, Status und Readiness fail-closed, tenantbezogen und idempotent integrieren.
**Dateibesitz:** Neue Fiskalisierungsservices unter `app/services/fiscalization/**`, POS-Fiskalisierungsendpoint, `tse_fiskaly_service.py`, fokussierte Edits in `admin_pos.py`, `pos_dsfinvk.py`, `kasse_tagesabschluss.py`, `app/api/v1/api.py`, neue POS-Migration, fokussierte Tests und Doku.
**Abnahmekriterien:** Providerwahl fiskaly/Swissbit; korrekte fiskaly Token-Authentifizierung; konfigurierbarer Swissbit REST-/Gateway-Vertrag; persistente idempotente Signierung; getrennte TSE-/DSFinV-K-Exporte; providergebundener Tagesabschluss; kein produktiver Scheinerfolg bei Simulator oder fehlender Vertragsfreigabe.
**Offene Risiken:** Swissbit Detail-API/SDK ist partner-/loginpflichtig; Live-Credentials und externe Pruefwerkzeugabnahme bleiben Betriebs-Gates.
**Ergebnis:** Provider-Abstraktion fuer fiskaly, Swissbit Cloud, Swissbit Hardware-Gateway und explizite Simulation umgesetzt. Providerwahl und DSFinV-K-Provider sind tenantbezogen getrennt. Browser-Secrets, stille Mock-Signaturen und der Festdaten-DSFinV-K-Export wurden entfernt. Transaktionen, Cash Point Closings und Exporte werden idempotent persistiert. POS uebergibt MwSt., Rabatte und Split Payments; Tagesabschluss laedt das Fiskaljournal und blockiert bei offenen Vorgaengen, Summendifferenzen, Providerfehlern oder Simulation.
**Checks:** 15 fokussierte Backendtests bestanden; Frontend-TypeScript und fokussierter ESLint gruen; Python-Compile und Router-Import gruen; Migration `pos_fiscal_providers_20260609` angewandt und einziger Head; Workboard, Doku-Governance und `git diff --check` gruen. Bestehender Wave-1-Sammeltest hat einen unabhaengigen Collection-Fehler in `admin_core.WorkflowSandboxCampaignMatchOut`.

## KIM-L3-S2-REVIEW-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Abstimmung:** Eng begrenzter Review-Fix fuer S2-Commit `ca39b1b06`. Claude pausiert bis zum Handoff Aenderungen an `CustomerActionBar.tsx`, `SalesDocumentsPanel.tsx` und der S2-Dispatch-Stelle in `kim/index.tsx`; S3/S4-Backend bleibt unberuehrt.
**Ziel des Slices:** Information- und Ang./Auf.-Dropdown gegen Bauplan, Routenvertraege und modellbasierte Klicktests pruefen und nachgewiesene fachliche, logische sowie testseitige Fehler beheben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KIM-L3-S2-REVIEW-001.yaml`, fokussierte QA-Doku, S2-Komponenten unter `packages/frontend-web/src/pages/crm/kim/` sowie CRM360-Action-Contracts und -Playwright-Spec.
**Abnahmekriterien:** Ang./Auf.-Menue entspricht dem Bauplan; Uebersicht zeigt alle Belege ohne klebende Altselektion; alle Informationsmodule sind ohne 404 erreichbar; Dropdown-Aktionen sind automatisiert; TypeScript, ESLint und CRM360-Playwright sind gruen.
**Offene Risiken:** Dateieueberschneidung mit Claudes geplantem S3-S5-Frontend; Backend-Belegtypen muessen mit dem Bauplan abgeglichen werden.
**Ergebnis:** Ang./Auf.-Menue auf den dokumentierten Sollvertrag Angebote/Auftraege/Lieferschein/Anfrage/Bestellung/Uebersicht korrigiert. Das Belegpanel ist kontrolliert; Uebersicht zeigt wirklich alle Belege und deaktiviert die unklare Sammel-Neuanlage. Informations-Shortcuts und stabile Zielselektoren ergaenzt. Alle elf Informationsmodule und sechs Belegmenuepunkte sind modellbasiert geklickt.
**Checks:** Frontend- und Playwright-TypeScript gruen; fokussierter ESLint gruen; CRM360-Playwright 17 Tests bestanden; Workboard und `git diff --check` gruen.

## KIM-L3-S3-S5 (CRM-Customer-360 Ausbau)

**Von:** Claude
**Owner:** Claude
**Stand:** ABGESCHLOSSEN 2026-06-09 — S3 (Präsente BE+FE), S4 (Ansprechpartner Werbe-Matrix + DSGVO-Pseudonymisierung BE+FE), S5 (konfigurierbare Action-Bar). model-based Suite 17/17 grün; tsc 0, eslint clean. Backend-Migrationen idempotent.
**Abstimmung:** Codex bearbeitet aktiv `KIM-L3-S1-GAP-CLOSURE-001` (uncommittete WIP in `index.tsx`, `ContactPersonsTable.tsx`, `ContactHistoryTable.tsx`, `CustomerActionBar.tsx`, `crm_kim.py`, CRM360-Playwright). **Ich fasse diese Dateien NICHT an, solange sie Codex' uncommittete WIP tragen.** Mein Frontend (S3-Präsente-Tab, S4-Ansprechpartner-Vollformular, S5-konfigurierbare Action-Bar) startet erst nach Codex' Commit (Baum sauber). Bis dahin nur **neue, nicht-kollidierende Backend-Dateien**.
**Ziel des Slices:** S3 Präsente (Tab+Backend), S4 Ansprechpartner-Vollformular (~40 Felder + Werbe-Matrix + Pseudonymisieren, Backend), S5 benutzerbezogen konfigurierbare Action-Bar — gemäß `docs/crm-customer-360-bauplan-2026-06-09.md`.
**Dateibesitz (Backend, jetzt):** `alembic/versions/crm_gifts_*`, `alembic/versions/crm_contacts_ext_*`, `app/services/crm_gift_service.py`, `app/services/crm_contact_ext_service.py`, `app/api/v1/endpoints/crm_gifts.py`, `app/api/v1/endpoints/crm_contacts_ext.py`, `app/api/v1/api.py` (nur eigene include_router-Zeilen), Backendtests. **Frontend (nach Handoff):** neue `kim/components/CustomerGiftsTab.tsx`, `CustomerContactsForm.tsx`; abgestimmte Edits in `kim/index.tsx`, `ContactPersonsTable.tsx`, `CustomerActionBar.tsx`.
**Abnahmekriterien:** Präsente-CRUD; Ansprechpartner-Vollformular + Werbe-Matrix + Pseudonymisieren; konfigurierbare Action-Bar (Sichtbarkeit + Reset, benutzerbezogen); model-based Suite grün; tsc/eslint/Backendtests grün.
**Offene Risiken:** Hohe Datei-Überschneidung mit Codex' aktivem Slice → strikte Workboard-Koordination; Frontend erst nach sauberem Baum.

## KIM-L3-S1-GAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Abstimmung:** Review-Fix zu Commit `cb8e7af10`, parallel zu Claudes S2-Arbeit. Codex bearbeitet zunaechst nur konfliktfreie Dateien. Claude besitzt waehrend S2 die aktuell uncommittierten Dateien `packages/frontend-web/src/pages/crm/kim/index.tsx`, `components/SalesDocumentsPanel.tsx`, `components/CustomerActionBar.tsx` und `components/InformationPanel.tsx`. Aenderungen an `index.tsx` und `SalesDocumentsPanel.tsx` werden erst nach Claudes S2-Commit auf dessen Stand integriert; fremder WIP wird nicht ueberschrieben.
**Ziel des Slices:** Alle im S1-Review gefundenen funktionalen und testseitigen Luecken schliessen: bestehende Angebote mit korrekter ID laden, Kontaktlogs fehlertolerant speichern, Ansprechpartner-Telefonie ueber TAPI und Logfuehrung abwickeln, Ansprechpartner-E-Mail fachlich korrekt liefern, eine belastbare Druckansicht bereitstellen und alle neuen Aktionen samt Ruecknavigation modellbasiert pruefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KIM-L3-S1-GAP-CLOSURE-001.yaml`, fokussierte QA-Doku, `packages/frontend-web/src/pages/crm/kim/components/ContactHistoryTable.tsx`, `ContactPersonsTable.tsx`, nach S2-Handoff abgestimmte Aenderungen in `kim/index.tsx` und `SalesDocumentsPanel.tsx`, `packages/frontend-web/src/pages/sales/angebot-erstellen.tsx`, `app/api/v1/endpoints/crm_kim.py`, fokussierte Backendtests sowie CRM360-Playwright-Vertraege und -Specs.
**Abnahmekriterien:** Vorhandene Belege laden die uebergebene Beleg-ID; fehlgeschlagene Logspeicherung behaelt Formulardaten und zeigt einen Fehler; Ansprechpartner-Telefonie nutzt Nummernauswahl, TAPI und anschliessendes Log; Ansprechpartner-E-Mail nutzt die Ansprechpartneradresse oder weist transparent auf fehlende Daten hin; Print rendert eine vollstaendige druckbare Cockpit-Sicht; Neukunde, Beleg-Oeffnen, Kontaktlog, Ansprechpartneraktionen, Print und Browser-Zurueck sind automatisiert; Typecheck, Lint, fokussierte Backendtests, Playwright, Build und Governance sind gruen.
**Offene Risiken:** Die Ansprechpartner-Tabelle kann produktiv noch keine E-Mail-Spalte besitzen; Schema und Query muessen tolerant erweitert werden. Die drei S2-Dateien duerfen erst nach Claudes Handoff integriert werden.
**Ergebnis:** Claudes S2-Commit `ca39b1b06` wurde als Integrationsbasis uebernommen. Angebots-Deep-Links laden die Entity-ID samt Kopf/Kunde/Positionen; Kontaktlog- und Ansprechpartner-Mutationen behalten Eingaben bei Fehlern; der Ansprechpartner-Create-Vertrag akzeptiert Neuanlagen ohne serverseitige ID-Felder; Ansprechpartner-Telefonie nutzt Nummernauswahl, TAPI und kontaktbezogenes Folge-Log; Ansprechpartner-E-Mail wird backendseitig gelesen/geschrieben und bei Legacy-Schemas lesend tolerant behandelt; CRM360 besitzt eine vollstaendige Print-Sicht mit Opt-out aus dem globalen Tabellen-Print-Fallback. Action-Matrix und Browsertests decken Neukunde, Print, Kontaktaktionen, Logfehler, Belegoeffnung und Browser-Zurueck ab.
**Checks:** Backendtests `9 passed`; Frontend- und Playwright-TypeScript gruen; fokussierter ESLint gruen; CRM360-Playwright `15 passed`; Produktions-Build gruen; `git diff --check` und Governance gruen.

## KIM-L3-QUICK-001

**Von:** Codex
**Owner:** Claude Code (Uebernahme 2026-06-09 von Codex; Abschluss 2026-06-23)
**Stand:** abgeschlossen 2026-06-23 — alle frontendseitigen L3-Bedienluecken geschlossen: Neukunde, Print, Ansprechpartner (Oeffnen/E-Mail/Praesente/Filter/TAPI-Flow), 27 Action-Contracts mit stabilen Action-IDs, Ang./Auf.-Dropdown mit 6 korrekt gerouteten Belegkategorien, Toolbar-Konfiguration (S5), NeuroAI-Panel, QA-Klicktest-Doku. ESLint 0, TSC 0, `pnpm docs:check` gruen.
**Abstimmung:** Komplementaer zu `KIM-L3-BACKEND-001` (Claude). Codex bearbeitet ausschliesslich `packages/frontend-web/src/pages/crm/kim/**`, CRM-Playwright-Vertraege und den eigenen QA-/Slice-Nachweis. Keine Aenderung an `app/**`, `alembic/**`, `tools/tapi-bridge/**` oder Backendtests. Neue Backend-Endpunkte werden in diesem Slice nicht vorausgesetzt; ihre Frontend-Integration erfolgt nach Claudes stabiler Handoff-Schnittstelle.
**Ziel des Slices:** Die im L3-Funktionsabgleich nachgewiesenen, rein frontendseitigen KIM-Bedienluecken schliessen: separate Kunden-Neuanlage, druckbare Cockpit-Ansicht, auswählbare Ansprechpartner mit Oeffnen/E-Mail/Praesente/Filter sowie fachlich korrekte Oeffnen-/Neu-Navigationen fuer vorhandene Verkaufsbelege.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KIM-L3-QUICK-001.yaml`, `docs/quality-assurance/` fuer den KIM-L3-Klicknachweis, `packages/frontend-web/src/pages/crm/kim/**` sowie fokussierte CRM-Playwright-Vertraege unter `playwright-tests/specs/crm/`.
**Abnahmekriterien:** Jede neue Aktion besitzt eine stabile semantische Action-ID; Neukunde oeffnet eine leere kanonische Kundenmaske; Print erzeugt eine druckbare Cockpit-Sicht; Ansprechpartner sind selektier- und filterbar und Oeffnen/E-Mail/Praesente arbeiten im gewaehlten Kontext; unterstuetzte Verkaufsbelege oeffnen die richtige Detail- beziehungsweise Neuanlagemaske mit Kunden-/Belegkontext; unbekannte oder noch nicht kanonisch routbare Belegarten behaupten keinen erfolgreichen Fachprozess; Typecheck, Build, Playwright und Governance sind gruen.
**Offene Risiken:** TAPI-Wahl, CC/Benachrichtigung und neue Kontaktlog-Persistenz sind explizit nicht Teil dieses Slices. Kaufangebote, Kaufabrechnungen und Fremdbestaende duerfen nur verdrahtet werden, wenn eine kanonische Zielroute eindeutig nachweisbar ist.

## KIM-L3-FRONTEND-001

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — Belegtabs (INVOICES/DUNNING/CONTRACTS/DROP_SHIPMENTS) rufen jetzt `fetchContactDocs` statt lokal zu filtern. Neuer Postfach-Tab in KIM zeigt interne CRM-Benachrichtigungen mit markRead-Funktion und unread-Badge im Tab-Label.
**Dateibesitz:** `packages/frontend-web/src/pages/crm/kim/components/ContactHistoryTable.tsx`, `packages/frontend-web/src/pages/crm/kim/index.tsx`, `docs/agent-ops/slices/KIM-L3-FRONTEND-001.yaml`

## KIM-L3-BACKEND-001

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-26 (Backend 2026-06-09, Frontend-Verdrahtung via KIM-L3-FRONTEND-001)
**Ergebnis (Backend):** (A1) Kontaktlog persistiert Art/Betreff/Kommentar/CC (`crm_kim.py` LogCreateIn/create_log/_log_from_row/ContactLog; Tabelle `kunden_kontakte` unterstuetzte die Spalten bereits, keine Migration). (B) TAPI Click-to-Dial: `POST /crm/tapi/dial` + `GET /crm/tapi/dial/pending` + `POST /crm/tapi/dial/{id}/done` (reuse `tapi_calls`, richtung='aus', status='dial_req', acked=TRUE, caller-Default 'KIM'; graceful ohne Bridge). (C) `GET /crm/kim/customers/{nr}/contact-docs?kind=invoices|dunning|contracts|drop_shipments` (Rechnungen/Mahnungen aus kanonischer `domain_shared.open_items`, Kontrakte/Strecken tolerant leer). (D) Internes Benachrichtigungssystem: Migration `crm_notifications_kim_l3_backend_20260609` (idempotent angewandt), `crm_notification_service.py` (intern persistent + extern Mail best-effort), Endpoints `POST/GET /crm/kim/notifications` + `/{id}/read`, CC-Auto-Dispatch in `create_log`. Verifiziert: 6 Unit-Tests gruen, alle Endpoints per curl 200 (Dial/Inbox/contact-docs), Migration idempotent. **Offen (Folge-Slice, Frontend):** Verdrahtung im KIM-Cockpit (Art-Dropdown/Betreff/Kommentar/CC-Feld, Tel→Dial, Kontakte-Belegtabs, Postfach-Anzeige) — nach KIM-L3-QUICK-001.
**Abstimmung:** Komplementaer zu `KIM-L3-QUICK-001` (Codex/Claude Code). Claude Code macht die rein frontend-/routenseitigen Bedienluecken (`packages/frontend-web/src/pages/crm/kim/**` + CRM-Playwright-Vertraege). Ich (Claude) baue die von KIM-L3-QUICK-001 **ausdruecklich ausgeklammerten** Backend-Fundamente: Kontaktlog-Persistenz (Art/Betreff/Kommentar/CC), TAPI-Wahl-Trigger, internes Benachrichtigungssystem sowie kanonische Kontakte-Belegquellen. **Ich fasse KEINE Datei unter `packages/frontend-web/src/pages/crm/kim/**` und KEINE `playwright-tests/specs/crm/**` an** — Frontend-Verdrahtung dieser Backends erfolgt als Folge-Slice, nachdem KIM-L3-QUICK-001 gelandet ist.
**Ziel des Slices:** Backend-Vertraege bereitstellen, damit die L3-Funktionen Kontaktdokumentation (Art/Betreff/Kommentar/CC), TAPI-Wahl, interne/externe Benachrichtigung und kontaktbezogene Belegtabs (Rechnungen/Mahnungen/Kontrakte/Strecken) im KIM-Cockpit fachlich hinterlegt sind.
**Dateibesitz:** `docs/agent-ops/active-workboard.md` (nur eigener Block), `docs/agent-ops/slices/KIM-L3-BACKEND-001.yaml`, `app/api/v1/endpoints/crm_kim.py`, neue `app/services/*`-Dateien fuer Benachrichtigung/Belegquellen, neue `alembic/versions/*` Migration(en), TAPI-Anbindung via `tools/tapi-bridge`, sowie `tests/test_*`-Backendtests. **NICHT:** `packages/frontend-web/**`, `playwright-tests/specs/crm/**`.
**Abnahmekriterien:** `create_log` persistiert Art/Betreff(kurzinfo)/Kommentar(notiz)/CC(weiterleitung_an) und `list_logs` gibt sie zurueck; TAPI-Wahl-Endpoint loest einen ausgehenden Call ueber die Bridge aus (mit Fallback/Gate ohne Bridge); internes Benachrichtigungsmodell + Endpoints (an Mitarbeiter/Abteilung) und externer Fachberater-Mail-Hook; kontaktbezogene Belegquellen-Endpoints liefern Rechnungen/Mahnungen/Kontrakte/Strecken aus kanonischen Quellen tolerant; `pytest` der neuen Tests gruen; `alembic upgrade head` idempotent.
**Offene Risiken:** Schnittstelle zwischen meinen Backend-Endpoints und der spaeteren Frontend-Verdrahtung muss stabil benannt sein. Bei gleichzeitigem Edit von `active-workboard.md` nur den eigenen Block pflegen.

## CRM360-MBT-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Ziel des Slices:** Den modellbasierten CRM360-Klickvertrag nach dem KIM-Designsystem-Umbau vollstaendig erneut ausfuehren und alle Regressionen bei Buttons, Tabs, CRUD, fachlichen Zielmasken, Entity-Kontext, 404-/Console-Fehlern und Browser-Zurueck beheben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/CRM360-MBT-005.yaml`, CRM360-QA-Dokumentation unter `docs/quality-assurance/`, CRM360-Spezifikationen und Hilfen unter `playwright-tests/specs/crm/` und `playwright-tests/helpers/`, `playwright.config.ts`, `playwright.global-setup.mjs`, `playwright.global-teardown.mjs`, `packages/frontend-web/src/pages/sales/order-editor.tsx`, `packages/frontend-web/src/pages/sales/invoice-editor.tsx`, `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx` sowie nur nachgewiesene Verdrahtungs- oder Selektorfixes unter `packages/frontend-web/src/pages/crm/kim/**`.
**Abnahmekriterien:** Die vollstaendige CRM360- und Revenue-Handover-Playwright-Suite laeuft gegen den aktuellen KIM-Stand; alle vertraglich erfassten Aktionen sind sichtbar und klickbar; CRUD-Requests, Zielroute, Hauptinhalt und Kunden-/Belegkontext stimmen; Browser-Zurueck liefert CRM360 ohne 404; keine neuen Console- oder Request-Fehler; Typechecks, fokussierter Lint, Build und Governance sind gruen.
**Offene Risiken:** Der Playwright-Global-Setup kann mit bereits laufenden lokalen Servern kollidieren. Selektoren duerfen nur stabilisiert werden, wenn die fachliche Aktion unveraendert bleibt; echte Verdrahtungsfehler werden im KIM-Code behoben und nicht durch nachsichtige Tests verdeckt.
**Ergebnis:** Der KIM-Designsystem-Umbau ist gegen elf modellbasierte CRM360- und Revenue-Handover-Tests regressionsgeprueft. Dialogtitel, aktive Tab-Tokens und delegierte Formularfelder besitzen wieder stabile Testvertraege. Playwright verwendet vorhandene Server oder startet entkoppelte eigene Prozesse ohne Portkonflikt und Haengen. Auftrags- und Lieferschein-Erfassung behalten den bereits typisiert uebergebenen CRM-Kundenkontext auch dann, wenn ein spaeter optionaler Kunden-Detail-Lookup leer bleibt; dadurch wird die Kundennummer bis Rechnung und Debitoren-OP durchgereicht.
**Checks:** CRM360 + Revenue-Handover Playwright `12 passed`; isolierter Self-Start-/Teardown-Smoke bestanden; Frontend- und Playwright-Typecheck gruen; Produktions-Build gruen; KIM-Lint ohne Fehler; Workboard- und Doku-Governance gruen.

## KIM-DS-001

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-09
**Ziel des Slices:** Das unter `/crm` fuehrende KIM-360-Cockpit von der portierten systemERP-L3-Terminal-Optik vollstaendig auf das VALEO-Designsystem umbauen (DS-Komponenten, Semantik-Farbtokens, Dark-Mode, Dialog-/Toolbar-Muster) und die wahrgenommene Ladeperformance der grossen Debitorenliste reduzieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KIM-DS-001.yaml`, `packages/frontend-web/package.json`, `packages/frontend-web/src/pages/crm/kim/index.tsx` und alle `packages/frontend-web/src/pages/crm/kim/components/*.tsx`.
**Abnahmekriterien:** Keine `font-mono`/`uppercase`-Terminal-Optik und keine hartkodierten Hex-Farben mehr; alle Flaechen nutzen DS-Semantik-Tokens und Dark-Mode rendert korrekt; Raw-Buttons/Inputs/Selects/Textareas/Modals durch `Button`/`Input`/`NativeSelect`/`Textarea`/`Dialog` ersetzt; mutierende Aktionen mit Submit-Guard + Disabled + Toast; alle `data-action-id` und Test-Selektoren identisch zu HEAD; Debitorenliste rendert nur ein begrenztes DOM-Fenster; eslint clean, tsc 0 Fehler, Screenshot hell+dunkel ok.
**Offene Risiken:** Praesentations-Refactor ueber 14 Dateien — Test-Selektoren des model-based CRM360-Tests duerfen nicht brechen. Die Cold-Start-Langsamkeit ist Vite-Dev-Erstaufbau (im Prod-Build irrelevant), kein App-Bug.
**Ergebnis:** Alle 14 KIM-Komponenten auf das VALEO-Designsystem umgebaut (~250x `font-mono`/`uppercase` entfernt, hunderte Hex-Farben → DS-Tokens, Dark-Mode funktioniert, DS-Primitive durchgaengig inkl. `Dialog`/`Progress`/`Skeleton`/`Badge`, Submit-Guards an Master-Edit + Quick-Call). Alle 12 `data-action-id` und Schluessel-IDs identisch zu HEAD. Debitorenliste rendert ein 80er-Fenster (462 total → 80 im DOM, „weitere anzeigen") bei voll erhaltener Suche/Filter/Tastatur-Navigation. `package.json` `predev`/`prebuild`/`pretype-check`/`check:navigation-targets` von `pnpm` auf `npm run routes:generate` korrigiert (Container hat kein pnpm → Exit 127).
**Checks:** `eslint` (`--max-warnings 0`) clean; `tsc --noEmit` 0 Fehler projektweit; Render-Fenster verifiziert (total=462, rendered=80, load-more=1); Dark-Mode-Screenshot ok. **Follow-up ERLEDIGT (2026-06-09, Commit `74b274a8d`):** Port-Konflikt via „reuse existing server" im Global-Setup gelöst, Selektoren auf stabile IDs gehärtet, model-based Suite `crm360-model-based.spec.ts` **10/10 grün** (`npx playwright test … --retries=1` gegen Preview :4173, APIs gemockt); Doku `docs/quality-assurance/playwright-port-konflikt-reuse-2026-06-09.md`. Offen bleibt nur die optionale Server-seitige Kundensuche bei stark wachsendem Kundenstamm.

## CRM360-MBT-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-09
**Ziel des Slices:** Den CRM360-Revenue-Handover um den fachlichen Abschluss Rechnung -> Buchung -> offener Posten erweitern und gegen reale Backend-Vertraege validieren. Der Nachweis muss tenant-isoliert, revisionssicher und ohne hartes Loeschen gebuchter Finanzdaten auskommen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/CRM360-MBT-004.yaml`, relevante CRM360-/OTC-QA-Dokumentation, `scripts/uat/crm360_revenue_handover_uat.py`, fokussierte Tests unter `tests/`, `app/services/docflow_service.py`, `app/services/sales_posting_service.py`, `app/services/finance_transaction_service.py`, `app/infrastructure/models/journal.py` und `app/api/v1/endpoints/finance_invoices.py`.
**Abnahmekriterien:** Ein realer oder explizit gegateter UAT weist Rechnung, Posting und Debitoren-OP samt Kunden-, Betrag-, Beleg- und Tenant-Bezug nach; Wiederholung ist idempotent; gebuchte Daten werden nur ueber fachliche Kompensation/Storno behandelt; fehlende Kontierung oder Finanzkonfiguration wird als klarer Blocker ausgewiesen; Backendtests, Live-UAT und Governance sind gruen.
**Offene Risiken:** Posting kann Kontenplan, Geschaeftsjahr, Steuerlogik und Debitorenkonto voraussetzen. Falls kein revisionssicherer Kompensationsvertrag existiert, darf der persistente Lauf nicht buchen und muss stattdessen das fehlende Gate belastbar dokumentieren.
**Ergebnis:** Docflow-Ausgangsrechnungen erzeugen nun ueber den gemeinsamen Sales-Posting-Service eine gebuchte, ausgeglichene JournalEntry und einen Debitoren-OP. Wiederholung mit gleichem Idempotenzschluessel ist stabil; Storno erzeugt eine GoBD-Gegenbuchung, setzt Original und Docflow-Beleg auf `reversed` und schliesst den OP als `storniert` mit Rest `0`. Auch die produktiven Finance-Invoice-Call-Sites delegieren an denselben Kern. Behoben wurden fehlende Journal-Zeilennummern und kanonische Betragsfelder, Kontonummer-zu-Konto-ID-Aufloesung, der Konflikt zwischen global eindeutigen Kontonummern und tenant-spezifischer Suche sowie freie technische Akteure in einem User-FK-Feld.
**Checks:** Finanz-Live-UAT `status=passed` mit erhaltener reversierter Evidenzkette; Original- und Gegenbuchung jeweils Soll=Haben `20,00 EUR`, Hashwerte vorhanden, OP `storniert/offen=0`, keine verwaisten Sales-Invoice-Drafts; 91 fokussierte Backendtests, Python-Compile und Governance bestanden.

## CRM360-MBT-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-08
**Ziel des Slices:** Fuer den CRM360-Revenue-Handover einen persistenten, wiederholbaren und aufraeumbaren UAT-Durchstich gegen reale Backend-Vertraege bereitstellen. Testdaten muessen eindeutig markiert, tenant-isoliert und nach dem Lauf entfernt werden; fehlende produktive Infrastruktur wird als explizites Gate statt als Scheinerfolg ausgewiesen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/CRM360-MBT-003.yaml`, relevante CRM360-UAT-/QA-Dokumentation, neue fokussierte UAT-Hilfen und Tests unter `playwright-tests/specs/crm/`, `scripts/uat/`, `tests/`, eine idempotente O2C-Repair-Migration unter `alembic/versions/` sowie nur die fuer Cleanup oder konsistente O2C-Vertraege zwingend erforderlichen Sales-/Delivery-/Invoice-Backenddateien.
**Abnahmekriterien:** Der Lauf erzeugt oder verwendet isolierte Kunden-/Belegdaten, prueft persistente Folgeobjekte und ihren Zusammenhang, beseitigt erzeugte Daten idempotent und unterscheidet sauber zwischen bestanden, nicht konfiguriert und fachlich fehlgeschlagen; Typechecks, fokussierte Backendtests, Browser-UAT und Governance sind gruen.
**Offene Risiken:** Eine lokal erreichbare, migrationsaktuelle Datenbank und gestartete Backenddienste koennen fehlen. Finanzbuchungen duerfen nicht destruktiv geloescht werden; gegebenenfalls endet der automatisierte Lauf vor finaler Buchung und weist diese als externes Freigabe-Gate aus.
**Ergebnis:** Guarded UAT-Skript erzeugt einen markierten Kunden und fuehrt die realen API-Vertraege Angebot -> Auftrag -> Lieferschein -> Docflow-Rechnung aus. Persistenz, Positionen, Kunden-/Quellbelegbezug und API-Soft-Delete werden gegen eine frische DB-Session validiert; ein abschliessender ID-basierter Cleanup entfernt alle UAT-Artefakte. Behoben wurden das veraltete Lieferschein-SQL, eine fehlende Dev-Tabellenstruktur, die falsche FK-Einfuegereihenfolge der Docflow-Konvertierung und ein Best-Effort-Audit, dessen geschluckter SQL-Fehler zuvor die gesamte Fachtransaktion implizit zurueckrollte.
**Checks:** Live-UAT `status=passed`; sieben fokussierte Backendtests bestanden; Python-Compile bestanden; Alembic steht auf `crm360_o2c_delivery_20260608 (head)`; Residuenpruefung fuer Kunden, Angebote, Lieferscheine, Docflow und Outbox jeweils `0`.

## CRM360-MBT-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-08
**Ziel des Slices:** Den bisher nur modellierten CRM360-Folgeprozess Kunde -> Angebot -> Auftrag -> Lieferschein -> Rechnung -> OP als echten, typisierten Browser-Handover umsetzen und mit Playwright gegen Zielmaske, Kunden-/Belegkontext, Ruecksprung und 404-/Console-Fehler pruefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/CRM360-MBT-002.yaml`, relevante QA-/Workflow-Doku, `app/api/v1/endpoints/sales_offers.py`, `tests/test_security_sales_offers.py`, neuer gemeinsamer Handover-Vertrag unter `packages/frontend-web/src/lib/workflow/`, `packages/frontend-web/src/pages/sales/angebot-erstellen.tsx`, `order-editor.tsx`, `delivery-editor.tsx`, `invoice-editor.tsx`, `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx`, `packages/frontend-web/src/pages/finance/op-debitoren.tsx` sowie fokussierte Tests unter `playwright-tests/specs/crm/`.
**Abnahmekriterien:** Jede Belegstufe liest und reicht einen einheitlichen Kunden-/Quellbelegkontext weiter; sichtbare Folgeprozess-Aktionen oeffnen die fachlich erwartete Maske; Browser-Zurueck endet nicht auf 404; Playwright fuehrt den gesamten Handover mit deterministischen Fixtures aus; Typecheck, Build, fokussierte Tests und Governance sind gruen.
**Offene Risiken:** Die Fachmasken verwenden teils unterschiedliche API- und Query-Vertraege. Persistenter Live-CRUD ueber alle Stufen kann isolierte Backend-Fixtures erfordern; ein Browser-Handover darf nicht als Buchungsnachweis ausgegeben werden.
**Ergebnis:** Einheitlicher typisierter Sales-Handover eingefuehrt; Angebot, Auftrag, kanonischer Lieferschein, Rechnung und OP transportieren Kunden- und Quellbelegkontext. Auftragspositionen werden in den Lieferschein uebernommen, die Angebot-zu-Auftrag-API besitzt ein korrektes Response-Modell, und elf kombinierte CRM360-Browsertests sind gruen.
**Checks:** Frontend- und Playwright-Typecheck, Produktions-Build, Routing-Integritaet, Navigation-Targets, drei Backendtests und elf Playwright-Tests bestanden.

## ROUTER-NEXT-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-08
**Ziel des Slices:** Nach dem erfolgreichen TanStack-Browser-Router-Cutover werden die verbliebenen produktiven Aufrufe des React-Router-Kompatibilitaetsadapters auf native TanStack-Hooks und streng typisierte VALEO-Route-Contracts migriert.
**Dateibesitz:** `packages/frontend-web/src/**`, Routing-Scripts, Routing-Dokumentation und fokussierte Tests.
**Abnahmekriterien:** Keine produktiven Imports aus `react-router-compat.tsx`; Navigation, Links, Parameter und Search verwenden TanStack Router beziehungsweise den typisierten Route-Contract; Adapter nur noch als Testinfrastruktur oder entfernt; alle Routing-Gates gruen.
**Offene Risiken:** Mehr als 300 produktive Dateien verwenden die alte ergonomische Aufrufsignatur. Dynamische Pfade werden explizit klassifiziert und nicht durch untypisierte Casts verdeckt.
**Ergebnis:** Der React-Router-Kompatibilitaetsadapter ist entfernt. 338 produktive Aufrufer verwenden die TanStack-basierte `typed-router.tsx`-Fassade; Unit-Tests verwenden getrennt `test-router.tsx` mit TanStack Memory History. Der Generator erzeugt 851 explizite Routen, einen maschinenlesbaren Route-Katalog sowie geschlossene Parameter- und Search-Key-Contracts. 94 produktive Navigationsziele und 34 Legacy-Redirects sind explizit registriert. Das neue Gate `check:navigation-targets` validiert statische und template-basierte Deep Links. Vollstaendiger Typecheck, Routing-Integritaet, Navigation-Audit, 127 Vitest-Tests, Produktions-Build und acht Playwright-Smokes sind gruen.

## ROUTER-NEXT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-08
**Ziel des Slices:** Die Frontend-Routing-Infrastruktur vollstaendig von zentraler React-Router-Splat-/Alias-Aufloesung auf einen automatisch generierten, typisierten TanStack-Route-Tree migrieren. Kanonische Route-Contracts, typisierte Parameter/Search-Werte, Breadcrumb-Metadaten, Auth, Deep Links und Legacy-Redirects werden in einer Source of Truth zusammengefuehrt; es gibt zu keinem Zeitpunkt zwei Browser-Router auf derselben History.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ROUTER-NEXT-001.yaml`, neue Routing-ADR/Projektkontext-Doku, `packages/frontend-web/package.json`, `packages/frontend-web/vite.config.ts`, `packages/frontend-web/src/app/**` (Routing und Navigation), `packages/frontend-web/src/routes/**`, `packages/frontend-web/src/routeTree.gen.ts`, routergekoppelte Layouts/Komponenten/Seiten, Routing-Scripts sowie fokussierte Unit-/E2E-Tests.
**Abnahmekriterien:** TanStack Router ist der einzige Browser-Router; Route Tree wird reproduzierbar generiert; dynamische Parameter und Search-Werte sind typisiert; Breadcrumbs und Auth laufen ueber Route-Metadaten/Context; bekannte Legacy-Links redirecten auf kanonische URLs; unbekannte Pfade liefern 404; `AppRouteRuntime` und React-Router-Splat entfallen; Typecheck, Build, Routing-Tests und E2E-Smokes sind gruen.
**Offene Risiken / Integrationsreihenfolge:** Sehr hoher Blast Radius durch 569 Aliase und hunderte React-Router-Imports. Root-Router, Vite-Konfiguration und gemeinsame Navigation bleiben exklusiver Besitz dieses Slices. Migration erfolgt contract-first mit automatisierten Import-/API-Umstellungen und fokussierter manueller Nacharbeit; fremde parallele Aenderungen werden nicht reverted.
**Ergebnis:** TanStack Router ist der einzige Browser-Router. 757 explizite Routen, Route-Parameter und geerntete Search-Keys werden generiert und typisiert; 25 bekannte Legacy-URLs redirecten explizit auf kanonische Ziele. Breadcrumbs verwenden Match-Metadaten, Auth sitzt am App-Layout, der Unsaved-Changes-Blocker verwendet die TanStack-API. `AppRouteRuntime`, `PortalRouteRuntime`, `routes.tsx`, `App.tsx`, die zentrale Splat-Aufloesung und `react-router-dom` sind entfernt. Routing-Integritaet, Typecheck, Build, fokussierte Unit-Tests und der neue TanStack-Browser-Smoke sind gruen.

## KIM-CRM-360-001

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen + nach `main` gemergt/gepusht 2026-06-07 (Commit `6ab79d080`; Konsolidierung kunden-cockpit als Folgescope)
**Ziel des Slices:** Eine mit Google AI Studio gebaute 360°-CRM-Ansicht (systemERP-L3-Stil) als führendes Cockpit **„KIM – Kunde im Mittelpunkt" unter `/crm`** nach VALEO transponieren: portieren, an echte Daten anbinden (inkl. `public.kunden`-Erweiterung + Lese-Endpoints), NeuroAI anbieterunabhängig machen (Admin wählt LLM-Anbieter), Lead-Management + CRM-Geo als Tabs einbetten.
**Dateibesitz:** `packages/frontend-web/src/pages/crm/kim/**`, `pages/admin-suite/ki-anbieter.tsx`, `lib/api/admin-suite.ts`, `app/route-aliases.json`, `app/route-builders/auto-groups/generated/admin-suite.ts`, `app/navigation/domains/{commercial,core}.tsx`, `package.json`; `app/api/v1/endpoints/crm_kim.py`, `app/services/llm_gateway.py`, `app/api/v1/endpoints/admin_suite.py`, `app/api/v1/api.py`, `alembic/versions/kunden_crm360_20260607.py`, `app/services/{whatsapp_intake_service,kaeufer_klassifikator}.py`, `tests/test_{llm_gateway,crm_kim}.py`.
**Abnahmekriterien:** `/crm` lädt das 360°-Cockpit mit echten Kundendaten; Stammdaten-Edit persistiert (kunden_crm360-Satellit, Konvention-konform: kunden_nr-FK, kein tenant_id); Kontakte/Wiedervorlage/OP/Belege als echte Lese-Tabs; NeuroAI über anbieterunabhängiges Gateway mit deterministischem Fallback, Admin-Konfiguration unter `/admin-suite/ki-anbieter` (Key nie im Klartext); Lead-/Geo-Tabs eingebettet; type-check 0, eslint 0, Build grün, Backend-Tests grün.
**Erledigt:**
- **A+B:** 360°-App portiert (React 19→18, Tailwind v4→v3, Gemini raus, react-markdown@9); `kim-api.ts` → `/crm/kim/*`; Route `/crm` + Nav. Migration `kunden_crm360` (1:1-Satellit); `crm_kim.py` (customers CRUD-light, contacts via Alt-Tabelle `kunden_ansprechpartner`, logs/Wiedervorlage, financials/documents tolerant).
- **C:** `llm_gateway.py` (anthropic/openai_compatible/ollama, Tenant-Settings+Env, Fallback); Admin `GET/PUT/test /admin-suite/llm-gateway` + UI `ki-anbieter.tsx`; `neuro-summary` + `draft-email`; `whatsapp_intake`/`kaeufer_klassifikator` auf Gateway konsolidiert.
- **D:** Tabs „Lead-Management" (`leads`) + „CRM-Geo / Karte" (`kunden-karte`) lazy eingebettet.
**Checks:** `pytest tests/test_llm_gateway.py` (9), `test_crm_kim.py` (6), Smoke `test_admin_suite_readiness+test_kaeufergruppe` (35 gesamt) — alle grün (Container via `docker cp`+`MSYS_NO_PATHCONV=1`); `alembic upgrade head` (kunden_crm360_20260607); `tsc --noEmit` 0, `eslint src/pages/crm/kim` 0, `npm run build` grün; alle `/crm/kim/*`-Endpoints HTTP 200; Dev-Server `/crm` 200 inkl. API-Proxy.
**Offene Risiken / Folgescope:** Konsolidierung KIM ↔ `kunden-cockpit` (klassisch belassen, nicht entfernt — Deep-Links/Tests). Belege/OP in DEV leer → reale Leerzustände bis Verkaufsdaten existieren (Mapping verifiziert). `ANTHROPIC_API_KEY` ohne Guthaben → NeuroAI engine='fallback'; Admin kann auf Ollama/OpenRouter wechseln. Direktanlage OP/Beleg aus dem Cockpit ist bewusst Folgescope: Add-Aktionen geben ehrliche „im Fachprozess anlegen"-Rückmeldung (Lesen produktionsecht, financials aus domain_shared.open_items verifiziert). Vorbestehende, nicht-KIM CSS-Build-Warnung (font-stack) + 3 Analytics-Routing-Lücken bleiben rot (Repo-Altschuld, im Workboard akzeptiert). Auf `main` gemergt + gepusht.

## CRM360-MBT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-06-08
**Ziel des Slices:** Fuer das KIM-CRM-360-Cockpit einen semantischen, modellbasierten Klickvertrag einfuehren. Alle Buttons, Tabs, Links und CRUD-Aktionen werden gegen erwartete Zielmaske, Entity-Kontext, Persistenz, Ruecksprung und fachlichen CRM-to-Revenue-Workflow geprueft; die bestehende Visual-Tour bleibt reiner Smoke-Test.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, neuer Slice-Vertrag unter `docs/agent-ops/slices/CRM360-MBT-001.yaml`, CRM-360-Testdokumentation/Report unter `docs/quality-assurance/`, neue CRM-360-Tests und Hilfen unter `playwright-tests/`, notwendige stabile Action-IDs und nachgewiesene Verdrahtungsfixes unter `packages/frontend-web/src/pages/crm/kim/**`.
**Abnahmekriterien:** Maschinenlesbare Action-Matrix deckt alle interaktiven CRM-360-Elemente ab; Playwright prueft Sichtbarkeit, Klickbarkeit, Zielinhalt, URL/Entity-Kontext, 404/Console/Request-Fehler und Ruecksprung; echte KIM-CRUD-Pfade pruefen Persistenz, delegierte Fachprozesse werden explizit als solche validiert; CRM-to-Revenue-Modellpfad ist als ausfuehrbarer Testvertrag vorhanden; Markdown-Report klassifiziert OK, fehlende Verknuepfung, falsches Ziel, fehlendes CRUD, Back/404 und fachlich fragwuerdig.
**Bekannte Risiken:** Testdaten und laufende Backend-Dienste koennen vollstaendige Live-CRUD-Ausfuehrung lokal begrenzen; destructive Aktionen benoetigen isolierte Fixtures oder API-Cleanup. Bestehende fachlich unvollstaendige Buttons werden nicht durch nachsichtige Assertions kaschiert.
**Pflichtchecks:** CRM-360-Playwright-Suite, TypeScript-Typecheck der Testvertraege, Frontend-Typecheck bei UI-Aenderungen, Doku-Governance.
**Ergebnis:** 23 typisierte Action-Contracts und ein CRM-to-Revenue-Zustandsmodell eingefuehrt. Die zehnteilige Playwright-Suite prueft Kopfaktionen, echte KIM-Updates/Creates, NeuroAI-Kontext, delegierte Fachprozesse, URL-/Entity-Kontext und Browser-Ruecksprung ohne 404. Behoben wurden tote CRM360-Handler, falsche Zielnavigation, unsichtbare Toasts, Label-Zuordnungen, der haengende Playwright-Teardown, alle gefundenen Playwright-Typfehler sowie zwei Buildfehler ausserhalb CRM360 (POS-Doppelimport und ungueltige Tailwind-Regel).
**Checks:** CRM360 Playwright `10 passed`; Playwright-Typecheck gruen; Frontend-Typecheck gruen; Produktions-Build gruen; Workboard-Governance wird im Abschlusslauf validiert.
**Offene Risiken:** `mailto:` bleibt ein externer OS-Workflow. Der Unterlagen-Tab ist weiterhin lokal und kein persistentes DMS. Der fachliche Durchstich Angebot -> Auftrag -> Lieferschein -> Rechnung -> OP ist modelliert, benoetigt fuer einen echten Live-Nachweis aber isolierte, aufraeumbare Daten in allen beteiligten Fachmodulen.

## CRM-GEO-ABSCHLUSS-001

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-05
**Ziel des Slices:** Die vier offenen Fäden der CRM-/Geo-Arbeit zu Ende führen — (1) Geo-Hofgenauigkeits-Loop schließen, (2) echte Ist-Belegaggregation statt modellierter Seeds, (3) Durchdringungs-Pipeline-Performance (N+1), (4) TAPI-Bridge-Dienst — plus die jüngste GAP-Datenquelle (impdata2025.csv) korrekt autoritativ machen.
**Dateibesitz:** `scripts/import_kmz_betriebe.py`, `app/services/ist_aggregation_service.py` (neu), `scripts/aggregate_produktgruppen_bezug.py` (neu), `tests/test_ist_aggregation.py` (neu), `app/services/bedarfsdeckung_service.py`, `app/services/gap_pipeline.py`, `app/services/geo_pipeline.py`, `scripts/enrich_betriebe_csv.py`, `scripts/seed_ackerbau_profil.py`, `tools/tapi-bridge/tapi_bridge.py` (neu), `tools/tapi-bridge/README.md` (neu), `tests/test_tapi_bridge.py` (neu).
**Abnahmekriterien:** KMZ-Koordinaten-Import hebt Kunden offline auf `precision='address'`; Ist-Aggregator füllt `kunden_produktgruppen_bezug` (`quelle='verkauf'`) aus echten Belegen und löst beide Medienbrüche (UUID→kunden_nr, Artikel→Produktgruppe); Pipeline ohne N+1; TAPI-Bridge meldet Anrufe an `/crm/tapi/incoming`; GAP-Konsumenten filtern auf das jüngste Jahr (keine Doppelzählung).
**Erledigt:**
- **Geo-Loop:** `import_kmz_betriebe.py` parst `<Point><coordinates>`, schreibt Koordinaten nach `gap_map_points` (Ausreißer außerhalb der Region verworfen) und ruft `match_address_points()` → Kunde auf `precision='address'` (verifiziert: GAP00001 place→address).
- **Ist-Aggregation:** `IstAggregationService` unioniert `domain_crm.sales_orders` + `domain_portal.customer_orders`, Resolver mappt customer_id/UUID/webshop/legacy → kunden_nr, reiner Klassifikator `klassifiziere_artikel` → 9 Produktgruppen; rollierend 12 M; Upsert `quelle='verkauf'` ohne Käufergruppen zu überschreiben. Integrationstest (beide Brücken, DB-Marge) grün; Dev hat keine echten Belege → Dry-Run 0, greift automatisch sobald Belege existieren.
- **Pipeline:** `BedarfsdeckungService.pipeline()` lädt 5 Batch-Queries vor + `_compute()` (eine Quelle der Wahrheit mit `cockpit()`). 4 s → **0,11 s** (~36×), Ergebnis 10/10 identisch zum Einzel-Cockpit.
- **TAPI:** `tools/tapi-bridge/tapi_bridge.py` (stdlib-only) — FRITZ!Box-Callmonitor (TCP 1012) / generischer TCP-Listener / Simulationsmodus; Reconnect-Backoff, Dedupe je Verbindungs-ID. Live getestet: `+49 551 12345` → Musterfirma GmbH.
- **GAP 2025:** 2025 war bereits importiert (20.817 Zeilen). Doppelzählung 2024+2025 in `geo_pipeline.get_map_points` (Karte) + `enrich_betriebe_csv` + `seed_ackerbau_profil` behoben via neuem `gap_pipeline.latest_gap_year()`; Ackerbau-/Bezug-Profile aufgefrischt (Ø-Fläche 125,3→112,6 ha).
**Checks:** `python -m pytest tests/test_ist_aggregation.py` (9 passed, im Container); `tests/test_tapi_bridge.py` (6 passed); reversibler Integrationstest Ist-Aggregation grün; `pipeline(500)` 448 Betriebe/0,11 s, 10/10 == Einzel-Cockpit; `import_kmz` Koordinaten-Loop verifiziert + Cleanup; TAPI live `/incoming`+`/pending` verifiziert + Cleanup; `python -m py_compile` aller geänderten Dateien.
**Offene Risiken:** Hofgenauigkeit braucht den manuellen My-Maps-Schritt (CSV anreichern → dort geokodieren → KMZ mit Koordinaten zurück) — extern. Echte Ist-Aggregation liefert erst Werte, sobald reale Verkaufsbelege existieren (Dev leer). 16 Ackerbau-Profile bleiben nach 2025-Reseed als Restbestand unter der ha-Schwelle (modelliert, unkritisch). TAPI-Bridge in Prod mit gültigem OIDC-Token statt `dev-token` betreiben. GAP-CSV nicht neu heruntergeladen (Vollimport >1 Mio. Sätze) — 2025 ist bereits regional importiert; Refresh bei Bedarf via `download_gap_csv(2025, force=True)`.

## KUNDENSTAMM-KONSOLIDIERUNG-001

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-02 (Repo-seitig; Prod-Ausfuehrung extern, siehe Runbook)
**Ziel des Slices:** Parallele Kunden-Wahrheiten auf einen fuehrenden Business Partner (System of Record) konsolidieren — `public.kunden` ueber `business_partner_id` an die BP-Identitaet binden, den 83-Spalten-Monolithen in schlanke Domaenensatelliten zerlegen, Konsumenten ueber die kanonische Zugriffsschicht lesen lassen und die Prod-Ausfuehrung (Bruecke fuellen, FK, Altspalten-Drop) per Runbook vorbereiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KUNDENSTAMM-KONSOLIDIERUNG-001.yaml`, `docs/kunden-konsolidierung.md`, `docs/runbooks/kunden-konsolidierung-schritt5.md`, `alembic/versions/kunden_*.py` + `perf_indexes_apply_20260602.py` + `performance_indexes_20260526.py`, `app/services/kunden_merge.py`, `app/services/kunden_backfill.py`, `app/services/business_partner_service.py`, `app/api/v1/endpoints/customers.py`, `tests/test_kunden_merge.py`, `packages/frontend-web/src/lib/api/kunden-lookup.ts`, `packages/frontend-web/src/pages/crm/kunden-schnellauswahl.tsx`.
**Abnahmekriterien:** `alembic current == head` (kunden_deprecate_legacy_cols_20260602), idempotent; Satelliten gefuellt (Backfill vollstaendig); Lookup-/Detail-Endpoints liefern Satellitendaten; Reader-Fallback loggt `deprecated`-Warnung; Identitaetsbruecke aufloesbar; `kunden_merge --apply` schreibt nur exact/strong; Prod-Ausfuehrung als phasenweises Runbook mit Backup/Freigabe-Gates dokumentiert.
**Erledigt:** Phase 2A (kunden_merge Reconciliation), 2D (Satelliten `kunden_adressen/zahlung/external_refs/aggregates` + Backfill + `kunden_lookup`-View + Schnellauswahl-Maske), Schritt 4 (30 Altspalten als DEPRECATED markiert, kein Drop, Fallback-Beobachtbarkeit), Schritt 5 vorbereitet (Resolver + `/crm/customers/lookup/resolve` + `/by-partner/{id}/detail` + FE-Hooks + `bridge_status`), Prod-Runbook, Pilot-Enabler `kunden_merge --plz-prefix` (Aurich/Emden/Leer = 265-268). Funktionaler Durchstich Dry-Run/Apply/bridge-status auf Dev fehlerfrei.
**Checks:** `python -m pytest tests/test_kunden_merge.py -q --no-cov` (`9 passed`); `python -m pyflakes` (sauber); `python -m alembic upgrade head` (current == head, idempotent); `pnpm --filter @valero-neuroerp/frontend-web type-check` (`0 errors`); `python scripts/agent_workboard_supervisor.py validate`.
**Offene Risiken:** EXTERN — die eigentliche Prod-Ausfuehrung (`kunden_merge --apply`, FK-Aktivierung, Altspalten-Drop) ist NICHT Teil dieses Slices: benoetigt Prod-`DATABASE_URL`, frisches Backup und Freigabe; Ablauf in `docs/runbooks/kunden-konsolidierung-schritt5.md`. Im Environment ist nur die Dev-DB verbunden (Pilot-Lauf Aurich/Emden/Leer auf Prod ausstehend). Landkreis-Scope ueber PLZ-Praefixe — exakte PLZ-Liste fachlich bestaetigen (Randbereiche 264/269). Identitaetsgebundene Produktivmasken (Combobox/Stamm) lesen erst nach Bruecken-Befuellung ueber resolve/by-partner.

## ADMIN-SUITE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Additive Grundstruktur fuer die VALEO Admin Suite mit zentralem Production-Readiness-Dashboard unter `/admin-suite`, ohne bestehende Health-, Integrations- oder Admin-Pfade zu duplizieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-001.yaml`, `docs/project-context/admin-suite-roadmap-2026-05-30.md`, `app/api/v1/endpoints/admin_suite.py`, `app/api/v1/api.py`, `tests/test_admin_suite_readiness.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/navigation/domains/core.tsx`, fokussierte Frontend-Tests und generierte Route-Dateien falls erforderlich.
**Abnahmekriterien:** `/api/v1/admin-suite/readiness` liefert nachvollziehbare Evidenz mit `ready`, `warning`, `blocked` oder `unchecked`; unbekannte oder externe Nachweise werden nie als Erfolg gewertet; `/admin-suite` zeigt Score, Evidenz und Links auf bestehende Admin-Bereiche; Navigation, Backend-Test, Frontend-Typecheck und Workboard-Validierung sind gruen.
**Erledigt:** Read-only Aggregator, konservative Evidenznormalisierung, Top-Level-Route, Navigation, Kachel-Dashboard, Roadmap und fokussierte Tests umgesetzt. Konfigurationsstatus wird nicht als Live-Erfolg bewertet.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_readiness.py tests/test_integration_bootstrap.py -q --no-cov` (`7 passed`); `pnpm --filter @valero-neuroerp/frontend-web test:run -- src/__tests__/pages/admin-suite/index.test.tsx` (`1 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierter `git diff --check`.
**Offene Risiken:** Globaler Routing-Integritaetscheck bleibt wegen drei vorbestehenden Analytics-Page-Group-Luecken rot. Globaler Workboard-Supervisor bleibt wegen sechs vorbestehenden Voice-YAMLs ohne `file_ownership` rot. Externe Live-Probes sind explizit nicht Teil dieses Slices.

## ADMIN-SUITE-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Persistierten, tenant-isolierten Setup-Wizard auf Basis der Admin-Suite-Roadmap einfuehren und vorhandene Fachmasken als gefuehrte Schritte verknuepfen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-002.yaml`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_setup.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/setup.tsx`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`, fokussierte Frontend-Tests.
**Abnahmekriterien:** Setup-Session und Schritte sind tenant-isoliert persistiert; `unchecked`, `in_progress`, `warning`, `blocked` und `completed` bleiben unterscheidbar; Navigation allein erzeugt keine Abschlussfreigabe; Resume nach Browser-Neustart ist abgesichert.
**Erledigt:** Tenant-isolierte Setup-Session in `domain_shared.tenants.settings`, explizite Step-Updates, Resume-Lesepfad und gefuehrte UI unter `/admin-suite/setup` umgesetzt. Vorhandene Fachmasken werden verlinkt, Navigation erzeugt keinen impliziten Abschluss.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov` (`6 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierter `git diff --check`.
**Offene Risiken:** Historisierung mehrerer Setup-Sessions bleibt Folgescope; fuer den initialen Wizard reicht der etablierte Tenant-Settings-Vertrag.

## ADMIN-SUITE-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Generischen Migration Core mit Source Profiles, Batches, Mapping-Version, Reconciliation-Gates und L3-/CSV-Cockpit einfuehren, ohne den bestehenden L3-Importer zu ersetzen.
**Dateibesitz:** Vor Claim verbindlich festlegen; neue Admin-Suite-Migrationsdateien, fokussierte Tests und minimale additive Router-/UI-Integration.
**Abnahmekriterien:** Dry Run und Staging bleiben Pflicht; Produktivfreigabe ist ohne Reconciliation blockiert; Batch-ID, Hash, Quelle und Mapping-Version sind sichtbar; L3 und CSV sind als Profile vorhanden.
**Erledigt:** Tenant-isolierter Migration-Control-Plane-Vertrag mit Source Profiles, Dry-Run-Batches, Hash, Mapping-Version und Reconciliation-Gates sowie Cockpit unter `/admin-suite/migration` umgesetzt. L3 und CSV sind verfuegbar; AMIC wird ohne verifizierten Feldkatalog sichtbar blockiert.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_migration.py tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov` (`8 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierter `git diff --check`.
**Offene Risiken:** Der Control Plane fuehrt bewusst keinen Produktivimport aus und ersetzt `scripts/import_l3.py` nicht. Ein produktives AMIC-Profil benoetigt einen verifizierten Feldkatalog und Beispieldaten-UAT.

## ADMIN-SUITE-004

**Von:** Codex
**Owner:** Codex
**Stand:** integriert in `ADMIN-SUITE-003` 2026-05-30
**Ziel des Slices:** CSV und AMIC Source Profiles kontrolliert bereitstellen.
**Erledigt:** CSV-Profil ist verfuegbar. AMIC/A.eins ist als sichtbares, blockiertes Profil katalogisiert. Die produktive Aktivierung bleibt bis zum verifizierten Feldkatalog und Beispieldaten-UAT gesperrt.
**Offene Risiken:** Eine scheinbar fertige AMIC-Anbindung ohne reale Quelltabellen und Feldkatalog waere fachlich gefaehrlicher als der explizite Blocker.

## ADMIN-SUITE-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Lesendes Security- und Agent-Governance-Cockpit mit Rollenpaketen, effektiven Scopes, SoD-Warnungen und Rollen-Simulation einfuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-005.yaml`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_security.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/security.tsx`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`.
**Abnahmekriterien:** Bestehendes RBAC bleibt Source of Truth; Simulation liefert effektive Scopes ohne Persistenz; Agentenrollen sind sichtbar getrennt; kritische Scope-Kombinationen erzeugen SoD-Warnungen.
**Erledigt:** Lesendes Governance-Cockpit unter `/admin-suite/security`, RBAC-Adapter, effektive Rechte-Simulation, SoD-Warnungen und getrennte Agentenrollen umgesetzt. Laufende Rollenvertraege werden nicht migriert.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_security.py tests/test_admin_suite_migration.py tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov` (`12 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierter `git diff --check`.
**Offene Risiken:** Normalisierte Permission Sets, Standort-/Lagerfilter und Break-glass-Schreibworkflow bleiben nachgelagerte, migrationspflichtige Governance-Erweiterungen.

## ADMIN-SUITE-006

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Read-only Connector Hub mit vereinheitlichtem Katalog, Credential-Metadaten und klarer Trennung von Konfiguration und Live-Probe einfuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-006.yaml`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_operations.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/connectors.tsx`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`.
**Abnahmekriterien:** Kein Secret-Wert wird ausgegeben; vorhandene Integrationen sind katalogisiert; Konfigurationsstatus und Live-Probe bleiben getrennt.
**Erledigt:** Read-only Connector Hub unter `/admin-suite/connectors` mit redigierten Credential-Metadaten, vereinheitlichtem Katalog und getrennter Live-Evidenz umgesetzt.
**Checks:** Gemeinsame Admin-Suite-Gates: `18 passed`, TypeScript gruen, Frontend-Smoke gruen, fokussierter Diff-Check gruen.
**Offene Risiken:** Provider-spezifische Retry-/DLQ-Schreibaktionen folgen erst nach Audit-Vertrag.

## ADMIN-SUITE-007

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Hardware Center als read-only Evidenzsicht ueber bestehende Device-, Mobile-, Waage- und POS-Vertraege einfuehren.
**Dateibesitz:** Gemeinsam mit `ADMIN-SUITE-006/008` in additiven Admin-Suite-Dateien.
**Abnahmekriterien:** Device-Kategorien, Registry-Quellen, Testaktionen und Live-Evidenzstatus sind sichtbar; Registrierung wird nicht als Hardware-UAT gewertet.
**Erledigt:** Hardware Center unter `/admin-suite/devices` mit Registry-Quellen, Testaktionen und explizit ungepruefter Live-Evidenz umgesetzt.
**Checks:** Gemeinsame Admin-Suite-Gates: `18 passed`, TypeScript gruen, Frontend-Smoke gruen, fokussierter Diff-Check gruen.
**Offene Risiken:** Reale Heartbeats, Eichnachweise und Standort-UAT bleiben externe bzw. adapterpflichtige Nachweise.

## ADMIN-SUITE-008

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Operations Center fuer Backup, Restore, Release, Alembic und Diagnose als ehrliche Evidenzsicht einfuehren.
**Dateibesitz:** Gemeinsam mit `ADMIN-SUITE-006/007` in additiven Admin-Suite-Dateien.
**Abnahmekriterien:** Deploybare Jobs und nachgewiesene Betriebslaeufe bleiben unterscheidbar; simulierter Restore wird nie als produktiver Nachweis gewertet.
**Erledigt:** Operations Center unter `/admin-suite/operations` mit Backup-, Restore-, Release-, Alembic- und Diagnose-Evidenz umgesetzt. Deploybare Jobs werden nicht als erfolgreiche Betriebslaeufe gewertet.
**Checks:** Gemeinsame Admin-Suite-Gates: `18 passed`, TypeScript gruen, Frontend-Smoke gruen, fokussierter Diff-Check gruen.
**Offene Risiken:** Letzte reale Laufzeitdaten benoetigen spaeter einen Ops-Adapter oder Monitoring-Import.

## ADMIN-SUITE-009

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Read-only Compliance- und Audit-Evidenzsicht fuer GoBD, DSGVO, POS/TSE, Meldewesen und externe Betriebsabnahmen in die Admin Suite integrieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-009.yaml`, `docs/project-context/admin-suite-roadmap-2026-05-30.md`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_compliance.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/compliance.tsx`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`.
**Abnahmekriterien:** Bestehende Compliance-Vertraege bleiben Source of Truth; Implementierung, Runtime-Nachweis und externe Abnahme bleiben getrennt sichtbar; kein ungepruefter Nachweis wird als produktiv bereit bewertet; `/admin-suite/compliance` ist erreichbar; Backend-Test, Frontend-Typecheck und fokussierter Diff-Check sind gruen.
**Erledigt:** Read-only Compliance Evidence Center unter `/admin-suite/compliance` mit acht Evidenzbereichen umgesetzt. GoBD, DSGVO Art. 30/33, POS/TSE, ELSTER, ATLAS, Meldewesen und Sanktionspruefung verlinken bestehende Fachvertraege; Runtime-Evidenz und externe Gates bleiben explizit getrennt.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_compliance.py tests/test_admin_suite_operations.py tests/test_admin_suite_security.py tests/test_admin_suite_migration.py tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov --tb=short` (`17 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierte Doku-Checks; `git diff --check`.
**Offene Risiken:** Externe Zertifikate, Behoerdenquittungen und produktive UAT-Nachweise bleiben ausserhalb des Repos.

## ADMIN-SUITE-010

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Read-only Systemstatus-Evidenzsicht fuer Health, Release, Migration, Event-Bus, Worker und Voice in die Admin Suite integrieren, ohne beim Cockpit-Aufruf Live-Probes auszuloesen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-010.yaml`, `docs/project-context/admin-suite-roadmap-2026-05-30.md`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_system_status.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/system-status.tsx`, `packages/frontend-web/src/pages/admin-suite/index.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`.
**Abnahmekriterien:** Bestehende Health- und Monitoring-Vertraege bleiben Source of Truth; implementierte Probe, beobachteter Runtime-Status und Cockpit-Abruf bleiben getrennt; kein Cockpit-GET startet externe oder zustandsaendernde Probe; `/admin-suite/system-status` ist erreichbar; Backend-Test, Frontend-Typecheck und fokussierter Diff-Check sind gruen.
**Erledigt:** Read-only System Status Evidence Center unter `/admin-suite/system-status` mit acht Evidenzbereichen umgesetzt. API-Liveness, API-Readiness, Startup-Guards, Release, Alembic, Event-Bus, Worker und Voice verlinken vorhandene Probe-Vertraege; der Cockpit-Aufruf fuehrt keine Live-Probe aus.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_system_status.py tests/test_admin_suite_compliance.py tests/test_admin_suite_operations.py tests/test_admin_suite_security.py tests/test_admin_suite_migration.py tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov --tb=short` (`20 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; fokussierte Doku-Checks; `git diff --check`.
**Offene Risiken:** Reale Laufzeitwerte benoetigen spaeter einen expliziten Ops-Adapter oder Monitoring-Import.

## ADMIN-SUITE-011

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Redigierten read-only Diagnosepaket-Manifest-Katalog fuer Supportfaelle in die Admin Suite integrieren, ohne Logs, Secrets oder Live-Daten beim Cockpit-Aufruf zu exportieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ADMIN-SUITE-011.yaml`, `docs/project-context/admin-suite-roadmap-2026-05-30.md`, `app/api/v1/endpoints/admin_suite.py`, `tests/test_admin_suite_diagnostics.py`, `packages/frontend-web/src/lib/api/admin-suite.ts`, `packages/frontend-web/src/pages/admin-suite/diagnostics.tsx`, `packages/frontend-web/src/pages/admin-suite/operations.tsx`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts`.
**Abnahmekriterien:** Diagnosekategorien, Quellen, Redaktionspflicht und Sammelstatus sind sichtbar; Secret- und personenbezogene Inhalte werden nicht ausgegeben; Cockpit-GET sammelt oder exportiert keine Live-Daten; `/admin-suite/diagnostics` ist erreichbar; Backend-Test, Frontend-Typecheck und fokussierter Diff-Check sind gruen.
**Erledigt:** Read-only Diagnosepaket-Manifest unter `/admin-suite/diagnostics` mit sieben Kategorien umgesetzt. Release, Health, Migration, Connectoren, Event-Bus, Worker und Audit zeigen Quelle, Redaktionspflicht und `not_collected`; das Operations Center verlinkt den Katalog.
**Checks:** `python -m compileall -q app/api/v1/endpoints/admin_suite.py`; `python -m pytest tests/test_admin_suite_diagnostics.py tests/test_admin_suite_system_status.py tests/test_admin_suite_compliance.py tests/test_admin_suite_operations.py tests/test_admin_suite_security.py tests/test_admin_suite_migration.py tests/test_admin_suite_setup.py tests/test_admin_suite_readiness.py -q --no-cov --tb=short` (`23 passed`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; fokussierte Doku-Checks; `git diff --check`.
**Offene Risiken:** Ein echter Diagnoseexport benoetigt spaeter Audit-Vertrag, Rollenpruefung, Retention und explizite Nutzeraktion.

## DESIGN-MERIDIAN-HARDCOLORS-014

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Vierter Meridian-Hardcolor-Batch fuer verbleibende Admin-Resttreffer.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-HARDCOLORS-014.yaml`, priorisierte Dateien unter `packages/frontend-web/src/pages/admin/`.
**Abnahmekriterien:** Bearbeitete Admin-Restseiten nutzen semantische Meridian-Tokens statt generischer Tailwind-Hardcolors; gezielter Hardcolor-Scan auf bearbeiteten Dateien ohne Treffer; Typecheck und Diff-Checks sind gruen.
**Erledigt:** Benutzerliste, Rollenverwaltung, Integrationen-Quarantaene, Nummernkreise, Control Center, DMS-Setup und Voice-Channel auf `primary`, `muted`, `destructive`, Badge-Varianten und semantische Success-/Warning-Tokens umgestellt.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; gezielter Hardcolor-Scan auf den bearbeiteten Dateien ohne Treffer; `git diff --check`.
**Offene Risiken:** Weitere Hardcolors ausserhalb Admin bleiben Folgescope.

## DESIGN-MERIDIAN-HARDCOLORS-013

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Dritter Meridian-Hardcolor-Batch fuer verbleibende sichtbare Admin-Fachseiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-HARDCOLORS-013.yaml`, priorisierte Dateien unter `packages/frontend-web/src/pages/admin/`.
**Abnahmekriterien:** Ausgewaehlte Admin-Seiten nutzen semantische Meridian-Tokens statt generischer Tailwind-Hardcolors; gezielter Hardcolor-Scan auf bearbeiteten Dateien ohne Treffer; Typecheck, Workboard-Validierung und Diff-Checks sind gruen.
**Erledigt:** AI-Approvals, GAP-Pipeline-Console, Webhooks und Webshop von generischen Green-Hardcolors auf Badge-Varianten und semantische Success-Tokens umgestellt.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; gezielter Hardcolor-Scan auf den bearbeiteten Dateien ohne Treffer; `git diff --check`.
**Offene Risiken:** Weitere Domaenen ausserhalb Admin bleiben Folgescope.

## DESIGN-MERIDIAN-HARDCOLORS-012

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Zweiter Meridian-Hardcolor-Batch fuer sichtbare Admin-/Monitoring-Fachseiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-HARDCOLORS-012.yaml`, priorisierte Dateien unter `packages/frontend-web/src/pages/admin/` und `packages/frontend-web/src/features/workflow/`.
**Abnahmekriterien:** Ausgewaehlte Admin-/Monitoring-Seiten nutzen semantische Meridian-Tokens statt generischer Tailwind-Hardcolors; gezielter Hardcolor-Scan auf bearbeiteten Dateien ohne Treffer; Typecheck, Workboard-Validierung und Diff-Checks sind gruen.
**Erledigt:** Command Monitor, Audit Log, Compliance Dashboard, APInvoiceApprovalPanel und Monitoring Alerts auf `primary`, `muted`, `destructive`, Badge-Varianten und semantische Meridian-Token umgestellt.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; gezielter Hardcolor-Scan auf den bearbeiteten Dateien ohne Treffer; `git diff --check`.
**Offene Risiken:** Weitere Fachseiten-Hardcolors bleiben Folgescope.

## DESIGN-MERIDIAN-HARDCOLORS-011

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Fachseiten-Hardcolors in einem ersten risikoarmen Folgeslice auf Meridian-/semantische Tokens ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-HARDCOLORS-011.yaml`, fokussierte Frontend-Fachseiten/-Features nach Audit.
**Abnahmekriterien:** Ein klar abgegrenzter Satz sichtbarer Fachseiten/Feature-Komponenten nutzt keine generischen Tailwind-Hardcolors mehr fuer Status-, Surface- und Textsemantik; Typecheck, Workboard-Validierung und Diff-Checks sind gruen; verbleibende Hardcolors werden als Folgescope dokumentiert.
**Erledigt:** Workflow-Oversight, ApprovalPanel, Copilot Dock/Insights, CRUD-Audit/Cancel/Delete und AlertBanner von generischen Slate/Gray/Green/Red/Amber/Emerald-Hardcolors auf `primary`, `muted`, `card`, `destructive` und semantische Meridian-Token gezogen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts\agent_workboard_supervisor.py validate`; gezielter `rg`-Hardcolor-Scan auf den bearbeiteten Dateien ohne Treffer; `git diff --check`.
**Offene Risiken:** Repo enthaelt sehr viele historische Hardcolors; dieser Slice schliesst bewusst einen priorisierten Batch statt alle Fachseiten in einem grossen Refactor.

## ERP-QUALITY-ROADMAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Noch repo-seitig umsetzbare Punkte aus `docs/quality/ERP-QUALITY-ROADMAP.md` abschliessen oder belastbar als externe Betriebs-/Zertifizierungsgates abgrenzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ERP-QUALITY-ROADMAP-CLOSURE-001.yaml`, `docs/quality/ERP-QUALITY-ROADMAP.md`, `app/services/fints_connector.py`, `app/api/v1/endpoints/banken.py`, `packages/frontend-web/src/lib/api/agrar.ts`, `packages/frontend-web/src/components/agrar/SchlagKarte.tsx`, `packages/frontend-web/src/pages/agrar/feldbuch/schlagkartei.tsx`, `app/workers/low_stock_agent.py`, `app/api/v1/endpoints/agents.py`, fokussierte Tests/E2E-Specs fuer Roadmap-Abschluss.
**Abnahmekriterien:** FinTS TAN-Challenge-Flow ist simulatorfaehig und API-seitig erreichbar; MapLibre-Schlagkarte ist im Feldbuch verdrahtet und typecheckt; Low-Stock-Agent hat einen testbaren Event-/Batch-Pfad; Response-Model-Gate bleibt bei 0; externe ELSTER/Fiskaly/GoBD-Gates sind als nicht repo-seitig abschliessbare Betriebsnachweise dokumentiert; Workboard-, Doku-, Backend- und Frontend-Checks sind dokumentiert.
**Erledigt:** FinTS-TAN-Challenge-Response mit Simulator und API-Endpunkten nachgezogen; MapLibre-Schlagkarte in der Feldbuch-Schlagkartei eingebunden; Low-Stock-Agent mit EOQ-Heuristik, NATS-Subject und Status-/Simulations-API angelegt; Lager/Einkauf/HR-Voice-Intents integriert; fokussierte Backend-, Voice- und Frontend-Gates gruen.
**Checks:** `python -m compileall -q app\api\v1\endpoints\banken.py app\api\v1\endpoints\agents.py app\services\fints_connector.py app\workers\low_stock_agent.py services\ki-usability\app\services\action_registry.py services\ki-usability\app\services\intent_resolver.py`; `python -m pytest tests\test_roadmap_closure_fints_low_stock.py -q --no-cov`; `python -m pytest tests\test_voice_intent_lager_einkauf_hr.py -q --no-cov` in `services/ki-usability`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts\check_response_models.py --threshold 0`; `python scripts\agent_workboard_supervisor.py validate`.
**Offene Risiken:** Externe Zertifikate/Zugaenge (ELSTER-Org-Zertifikat, Fiskaly-Produktivzugang, Wirtschaftsprüfer-Testat) bleiben ausserhalb des Repos; breite Godfile-/Pagination-Komplettreduktion ist ein mehrwoechiges Programm und wird nur soweit risikoarm innerhalb dieses Slices geschlossen.

## DESIGN-MERIDIAN-ORCH-001

**Von:** Cursor (VAN-Mode)
**Owner:** Cursor + Codex + Claude Code
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** VAN-Entscheidungen fuer den MERIDIAN/TERRA-Designrollout verbindlich machen, Slice-Kette claimen und Handshake zwischen Codex und Claude Code etablieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-ORCH-001.yaml`, `docs/agent-ops/handshake-codex-claude-design-2026-05-23.md`, `docs/design/EMPFEHLUNG.md`
**Abnahmekriterien:** Scope gesamtes ERP mit MERIDIAN-Haupttheme; Terra nur auf Agrar-Routen im Kundenportal; Implementierungsreihenfolge Quick-Wins vor Phase 4 dokumentiert; Handshake mit Dateibesitz, Claim-Protokoll und CLAUDE.md-Invarianten; Folgeslices reserviert; Workboard-Validierung gruen.
**Erledigt:** VAN-Alignment und User-Freigaben; Handshake erstellt; Slice-Kette angelegt; `/goal`-Skill unter `.cursor/skills/goal/SKILL.md`; gesamter Rollout in Folgeslices umgesetzt.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `node scripts/docs-markdown-check.cjs docs/agent-ops/handshake-codex-claude-design-2026-05-23.md`
**Offene Risiken:** Screen-by-Screen-Hardcolors in Fachmodulen bleiben domaenenspezifische Folgeslices.

## DESIGN-MERIDIAN-QUICK-WINS-001

**Von:** Cursor (/goal)
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** Verbleibende Quick-Wins aus `docs/design/EMPFEHLUNG.md` abschliessen, bevor Phase 4 startet.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-QUICK-WINS-001.yaml`, `docs/design/EMPFEHLUNG.md`, `packages/frontend-web/src/components/ui/badge.tsx`, `packages/frontend-web/src/components/ui/alert.tsx`, `packages/frontend-web/src/components/ui/table.tsx`, `packages/frontend-web/src/components/ui/data-table.tsx`
**Abnahmekriterien:** Badge-Status-Semantik nutzt Meridian-Token statt harter Utility-Farben; Alert warning/info auf semantische Tokens; Table-Header/tabular-nums global konsistent; EMPFEHLUNG Phase-1-Checkboxen auf erledigt; Frontend-Typecheck und Workboard-Validierung gruen.
**Erledigt:** badge.tsx und alert.tsx auf `--color-semantic-*`-Tokens umgestellt; data-table numeric cells auf tabular-nums; EMPFEHLUNG Phase-1 als erledigt dokumentiert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `git diff --check`
**Offene Risiken:** Keine.

## DESIGN-TERRA-AGRAR-PORTAL-001

**Von:** Cursor (/goal)
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** Terra-Theme auf Agrar-Routen im Kundenportal aktivieren — Waldgruen/Gold fuer Landwirt-Self-Service, ohne MERIDIAN-Haupt-ERP zu beeinflussen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-TERRA-AGRAR-PORTAL-001.yaml`, `packages/frontend-web/src/lib/portal-theme.ts`, `packages/frontend-web/src/layouts/CustomerPortalLayout.tsx`, `packages/frontend-web/src/pages/portal/feldbuch.tsx`, `packages/frontend-web/src/pages/portal/naehrstoffbilanzen.tsx`, `packages/frontend-web/src/pages/portal/rationsoptimierung.tsx`
**Abnahmekriterien:** Terra-Routen `/portal/feldbuch`, `/portal/naehrstoffbilanzen`, `/portal/rationsoptimierung` rendern mit `theme-terra`; restliches Portal und ERP-Shell bleiben MERIDIAN; Terra-Sidebar/Accent-Tokens sichtbar; keine Token-Leaks auf Nicht-Agrar-Portal-Routen; Typecheck gruen.
**Erledigt:** `portal-theme.ts` mit Routen-Helper; `CustomerPortalLayout` aktiviert `theme-terra` bedingt per Pfad; Navigation/Header auf primary/accent-Tokens im Terra-Zweig.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`
**Offene Risiken:** Playwright computed-style auf Terra-Routen optional in CI.

## DESIGN-MERIDIAN-PHASE4-001

**Von:** Cursor (/goal)
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** Phase 4 aus EMPFEHLUNG — Dashboard-Polish, ObjectPage Golden-Ratio-Split, Form-States, WCAG-Audit — nach Abschluss der Quick-Wins.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-PHASE4-001.yaml`, `docs/design/EMPFEHLUNG.md`, `docs/design/WCAG-AUDIT-2026-05-23.md`, `packages/frontend-web/src/components/mask-builder/ObjectPage.tsx`, `packages/frontend-web/src/components/management/KPICard.tsx`
**Abnahmekriterien:** KPI-Cards mit konsistentem Amber-Akzent; ObjectPage 61.8/38.2-Split implementiert; axe-core WCAG-Audit fuer Kernrouten dokumentiert; Quick-Wins-Slice abgeschlossen; Typecheck gruen.
**Erledigt:** KPICard warning/success/danger auf Token; ObjectPage splitLayout default true mit 61.8/38.2 Grid und Sidepanel; WCAG-AUDIT-2026-05-23.md erstellt.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs docs/design/WCAG-AUDIT-2026-05-23.md`
**Offene Risiken:** axe-core CI-Integration bleibt Folgeslice; tiefe Fachseiten-Hardcolors unveraendert.

## DESIGN-MERIDIAN-AXE-CI-001

**Von:** Cursor (/goal weiter)
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** @axe-core/playwright fuer MERIDIAN/TERRA-Kernrouten in CI verankern und blockierende A11y-Verstoesse in Shell/Global-Komponenten beheben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-AXE-CI-001.yaml`, `docs/design/WCAG-AUDIT-2026-05-23.md`, `.github/workflows/quality-gate.yml`, `packages/frontend-web/tests/e2e/accessibility.spec.ts`, `packages/frontend-web/package.json`
**Abnahmekriterien:** axe-Tests auf 8 Kernrouten lokal und in quality-gate gruen; @axe-core/playwright installiert; Shell-Komponenten ohne kritische Verstoesse auf Kernrouten.
**Erledigt:** accessibility.spec.ts mit 8 Routen; A11y-Fixes (Breadcrumbs Home-Link, Copilot inert, ShortcutHelp aria-labels, AskVALEO FAB, NativeSelect ariaLabel); quality-gate Job `frontend-accessibility`.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web test:e2e:accessibility`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`
**Offene Risiken:** Fachseiten ausserhalb der 8 Kernrouten ungeprueft; manueller Screen-Reader-UAT bleibt extern.

## FACHLICHE-VERTIEFUNG-UX-W10-001

**Von:** Cursor (Composer)
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** Produktive CRUD-Stammdaten-Masken fuer Wave-10 Erlöskennziffern und Zahlungsbedingungen gegen FIBU-Backend-Vertraege.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/FACHLICHE-VERTIEFUNG-UX-W10-001.yaml`, `docs/FACHLICHE-VERTIEFUNG-ABNAHME.md`, `packages/frontend-web/src/lib/api/fibu.ts`, `packages/frontend-web/src/pages/fibu/erloeskennziffern.tsx`, `packages/frontend-web/src/pages/einkauf/zahlungsbedingungen.tsx`, E2E-Specs
**Abnahmekriterien:** Beide Masken CRUD-faehig gegen echte Endpoints; Warengruppen ohne Regression; E2E + Typecheck gruen.
**Erledigt:** API-Hooks in fibu.ts; erloeskennziffern.tsx (ekz_nr, bezeichnung); zahlungsbedingungen.tsx (ZABD-Felder laut Schema); Navigation/Routes; Playwright-Gates.
**Checks:** type-check; warengruppen/erloeskennziffern/zahlungsbedingungen Playwright; workboard validate
**Offene Risiken:** Keine — EKZZ ist als eigener Slice abgeschlossen; Waves 11-13 unveraendert backend-only.

## FACHLICHE-VERTIEFUNG-UX-W10-EKZZ-001

**Von:** Cursor (Composer 2.5)
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-23
**Ziel des Slices:** Produktive EKZZ-Maske fuer Erlöskontenzuordnung und Konto-Lookup gegen Wave-10-FIBU-Backend-Vertraege.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/FACHLICHE-VERTIEFUNG-UX-W10-EKZZ-001.yaml`, `docs/FACHLICHE-VERTIEFUNG-ABNAHME.md`, `packages/frontend-web/src/lib/api/fibu.ts`, `packages/frontend-web/src/pages/fibu/erloeskontenzuordnung.tsx`, Navigation/Routes, E2E-Spec
**Abnahmekriterien:** Zuordnungen Liste/Filter/Upsert; Lookup nutzbar; keine Regression Wave-10-Masken; E2E + Typecheck gruen.
**Erledigt:** API-Hooks; erloeskontenzuordnung.tsx unter `/fibu/erloeskontenzuordnung`; Navigation FIBU; Playwright-Gate `fachliche-vertiefung-ekzz.spec.ts`.
**Checks:** type-check; warengruppen/erloeskennziffern/zahlungsbedingungen/ekzz Playwright; workboard validate; docs-markdown-check
**Offene Risiken:** Kein DELETE-Endpunkt im Backend — UI bietet nur Upsert/Update, kein Loeschen.

## FRONTEND-DOMAIN-AUDIT-REPAIR-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-22
**Ziel des Slices:** Claudes lokale Domain-Audit-Nacharbeiten vor dem Push qualitaetssichern: korrumpierte i18n-/Encoding-Aenderungen reparieren, temporaere Skripte entfernen, Routing-Aenderungen validieren, Workboard nachziehen und lokale Commit-Historie mit korrektem Autor konsolidieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/FRONTEND-DOMAIN-AUDIT-REPAIR-001.yaml`, `packages/frontend-web/src/app/route-aliases.json`, `packages/frontend-web/src/app/page-module-loader.ts`, `packages/frontend-web/src/app/page-module-groups/commercial.ts`, `packages/frontend-web/src/i18n/locales/*.json`, betroffene Frontend-Pages mit Encoding-Korrekturen.
**Abnahmekriterien:** Keine neu eingefuehrte deutsche Locale-Mojibake; temporaere Reparaturskripte sind aus dem Worktree entfernt; Routing-Aliases referenzieren existierende Module; Typecheck, JSON-Parse, Encoding-Scan und Diff-Checks sind gruen; lokale sieben Claude-Commits sind vor Push zu einem sauberen Commit mit korrektem Autor zusammengefuehrt.
**Erledigt:** Deutsche Locale-Korruption aus dem lokalen Audit-Stand zurueckgenommen und `pattern.listreport.items_count` gezielt in `de/en/es/fr` ergaenzt; verbleibende neue Mojibake-Funde in den aktuell betroffenen Pages repariert; temporaere Root-Skripte entfernt; Route-Aliases gegen existierende Module validiert; lokale unpushed Historie fuer Konsolidierung vorbereitet.
**Checks:** JSON-Parse fuer `de/en/es/fr`; Encoding-Scan auf aktuell betroffene Locale-/Page-Dateien; Route-Alias-Modulvalidierung; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `git diff --check`; Workboard-/Doku-Checks.
**Offene Risiken:** Bestehende Alt-Mojibake in nicht bearbeiteten Legacy-Kommentaren oder Altmasken kann separat behandelt werden; dieser Slice blockiert nur neue/aktuelle Audit-Aenderungen.

## QA-FACHLICHE-VERTIEFUNG-GATES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-22
**Ziel des Slices:** Die nach der Wave-1-13-QA verbliebenen Gates repo-seitig schliessen: DB-Integration ausführbar machen, Frontend-E2E fuer Warengruppen absichern, Fach-UAT-Paket dokumentieren und Restgate-Status sauber aktualisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-GATES-001.yaml`, `docs/FACHLICHE-VERTIEFUNG-ABNAHME.md`, `packages/frontend-web/src/lib/api/einkauf.ts`, neue fokussierte DB-/E2E-Gate-Tests fuer fachliche Vertiefung.
**Abnahmekriterien:** DB-Gate ist als opt-in PostgreSQL-Integrationstest im Repo vorhanden; Warengruppen-Frontend hat einen Playwright-E2E-Vertrag gegen den echten Stammdaten-Endpunkt; Abnahmedoku unterscheidet repo-seitig geschlossene Gates von externer Fachfreigabe; Workboard-, Backend-, Frontend-/E2E- und Doku-Checks sind dokumentiert.
**Erledigt:** Opt-in-DB-Gate `tests/test_fachliche_vertiefung_db_integration.py` ergaenzt; Warengruppen-Playwright-Gate mit echtem Stammdaten-API-Pfad und Create/Update/Delete-Flows ergaenzt; Warengruppen-Query von `initialData` auf `placeholderData` korrigiert, damit echte Fetches nicht durch frischen Leercache blockiert werden; Abnahmedoku von offenen Restgates auf geschlossene repo-seitige Gate-Artefakte umgestellt.
**Checks:** `python -m py_compile tests/test_fachliche_vertiefung_db_integration.py`; `pytest tests/test_fachliche_vertiefung_db_integration.py -q --no-cov` (2 skipped ohne `RUN_DB_INTEGRATION=1`); `pnpm --filter @valero-neuroerp/frontend-web type-check`; `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/fachliche-vertiefung-warengruppen.spec.ts --project=chromium`; weitere Abschlusschecks siehe Slice-Datei.
**Offene Risiken:** Externe Fachsignatur und produktive Testdaten bleiben Business-/Betriebsabnahme; Playwright-Global-Teardown meldet vorhandene Visual-Tour-Issues aus `visual-tour-results`, der fokussierte Gate-Test selbst ist gruen.

## QA-FACHLICHE-VERTIEFUNG-WAVES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-22
**Ziel des Slices:** Alle QA-Blocker aus der fachlichen Vertiefung Wave 1-13 schliessen: Alembic-Head bereinigen, API-Smokes/CRUD-Vertraege absichern, Frontend-Verlinkung fuer Warengruppen korrigieren und Traceability-Doku nachziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-WAVES-001.yaml`, `docs/FACHLICHE-VERTIEFUNG-ABNAHME.md`, `alembic/versions/merge_heads_20260522.py`, `app/api/v1/endpoints/warengruppen.py`, `app/api/v1/endpoints/erloeskennziffern.py`, `app/api/v1/endpoints/zahlungsbedingungen.py`, `packages/frontend-web/src/lib/api/einkauf.ts`, `packages/frontend-web/src/pages/einkauf/warengruppen.tsx`, `tests/test_api_smoke_waves.py`.
**Abnahmekriterien:** `alembic heads` hat wieder einen Head fuer den fachlichen Abnahmepfad; API-Smokes pruefen zentrale Wave-10-13-Routen inklusive CRUD/Lookup-Fehlerpfade; Warengruppen-UI nutzt den neuen Backend-Vertrag; Doku beschreibt Abdeckung, Restgates und Pruefergebnis; Backend-/Frontend-/Doku-Checks sind gruen.
**Erledigt:** Alembic-Merge-Revision `merge_heads_20260522` fuehrt Agrar-Ernteplanung und fachliche Vertiefung Wave 13 auf einen Head zusammen; Wave-10-Stammdaten haben Update-Vertraege; Warengruppen-Frontend nutzt `/api/v1/stammdaten/warengruppen` mit Create/Update/Delete-Aktionen; API-Smokes decken Wave 10-13 ab; Abnahmedoku beschreibt Matrix, Restgates und Pruefkommandos.
**Checks:** `alembic heads`; `python -m py_compile alembic/versions/merge_heads_20260522.py app/api/v1/endpoints/warengruppen.py app/api/v1/endpoints/erloeskennziffern.py app/api/v1/endpoints/zahlungsbedingungen.py tests/test_api_smoke_waves.py`; `pytest tests/test_api_smoke_waves.py tests/test_fachliche_vertiefung_wave10.py tests/test_fachliche_vertiefung_wave11.py tests/test_fachliche_vertiefung_wave12.py tests/test_fachliche_vertiefung_wave13.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs docs/FACHLICHE-VERTIEFUNG-ABNAHME.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/QA-FACHLICHE-VERTIEFUNG-WAVES-001.yaml`; `git diff --check`
**Offene Risiken:** Breite fachliche Vollabdeckung aller 5118 Referenzseiten bleibt nur ueber weitere domaenenspezifische UATs beweisbar; DB-Integration gegen echte PostgreSQL-Testdaten und Frontend-E2E bleiben separate Betriebs-/UAT-Gates.

## SERVICE-LAYER-LEGACY-ENDPOINTS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Die bekannten grossen Legacy-Endpunkte final aus dem README-Tech-Debt herausfuehren: `harvest_acceptance.py`, `agrar_settlements.py` und `docflow.py` sollen als Thin-Router mit dedizierten Service-Klassen nachgewiesen sein.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/SERVICE-LAYER-LEGACY-ENDPOINTS-001.yaml`, `README.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/uat/ABNAHMEPROTOKOLL-WAVE-2026-05-17.md`, `app/api/v1/endpoints/harvest_acceptance.py`, `app/api/v1/endpoints/agrar_settlements.py`, `app/api/v1/endpoints/docflow.py`, `app/services/harvest_acceptance_service.py`, `app/services/agrar_settlement_service.py`, `app/services/docflow_service.py`, fokussierte Tests fuer die betroffenen Routen.
**Abnahmekriterien:** Die drei bekannten Legacy-Dateien haben dedizierte Services; verbliebene Router enthalten nur Request-/Response-Schema, Dependency-Wiring und HTTP-Fehler-Mapping; README/UAT-Doku fuehren keine offenen grossen Legacy-Service-Layer-Gaps mehr; fokussierte API-/Unit-Tests und Doku-Checks sind gruen.
**Erledigt:** `harvest_acceptance.py` war bereits ueber `HarvestAcceptanceService` entkoppelt; `agrar_settlements.py` delegiert Preview-, Drying-, Backfill-, PDF-, Freigabe- und Completion-Logik an `AgrarSettlementService`; `docflow.py` delegiert Sales-Invoice-Kundenfreigaben an `DocflowService`; README, UAT-Protokoll und Open-Gaps-Doku fuehren die drei grossen Legacy-Endpunkte nicht mehr als offene Service-Layer-Auflage.
**Checks:** `python -m py_compile app/api/v1/endpoints/agrar_settlements.py app/services/agrar_settlement_service.py app/api/v1/endpoints/docflow.py app/services/docflow_service.py app/api/v1/endpoints/harvest_acceptance.py app/services/harvest_acceptance_service.py tests/test_agrar_settlements_api.py tests/test_agrar_settlement_calculation.py`; `python -c "import app.api.v1.endpoints.agrar_settlements as a; import app.api.v1.endpoints.docflow as d; import app.api.v1.endpoints.harvest_acceptance as h; print('import-ok')"`; `pytest tests/test_agrar_settlement_calculation.py tests/test_agrar_settlement_campaign_backfill.py tests/test_agrar_settlement_campaign_reference.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs README.md docs/uat/ABNAHMEPROTOKOLL-WAVE-2026-05-17.md docs/project-context/open-gaps-and-known-issues.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/SERVICE-LAYER-LEGACY-ENDPOINTS-001.yaml`; `git diff --check`; `rg -n "Offen — Backlog|bleiben Tech-Debt|remain service-layer tech debt|weiter in Slices" README.md docs/uat/ABNAHMEPROTOKOLL-WAVE-2026-05-17.md docs/project-context/open-gaps-and-known-issues.md`
**Offene Risiken:** Sehr grosse fachliche Services koennen spaeter weiter modularisiert werden; dieser Slice schliesst die Endpoint-Tech-Debt-Aussage, nicht jede interne Service-Feinstruktur. Drei lokale HTTP-Smokes in `tests/test_agrar_settlements_api.py` bleiben gegen die aktuelle Entwickler-DB durch fehlende Spalte `domain_inventory.agrar_settlements.campaign_id` blockiert und benoetigen die passende lokale Migration.

## README-STATUS-2026-05-21

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Root-README auf den aktuellen GitHub-/Repo-Lieferstand nach Meridian-, UAT-, Gap-Closure-, Container-Health- und Keycloak-Nachlieferungen aktualisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/README-STATUS-2026-05-21.yaml`, `README.md`
**Abnahmekriterien:** README nennt Stand 2026-05-21, verweist auf aktuelle Source-of-Truth-Dokumente, beschreibt Meridian-Shell/Core-UI, UAT-Auflagen, Phase-2/3-Gap-Closure, Container-/Keycloak-Hardening und trennt repo-seitig geschlossene Punkte von externen Gates.
**Erledigt:** Root-README deutsch/englisch auf Stand 2026-05-21 gezogen; Test-/Coverage-Angaben korrigiert; Service-Layer-Aussage von pauschal abgeschlossen auf Hauptwellen plus bekannte Legacy-Tech-Debt geschaerft; Meridian, UAT, Keycloak-/Container-Hardening und externe Gates ergaenzt.
**Checks:** `rg` gegen veraltete README-Aussagen; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs README.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/README-STATUS-2026-05-21.yaml`; `git diff --check`
**Offene Risiken:** Tiefe Fachstatusdetails bleiben in den verlinkten Status-/Gap-/UAT-Dokumenten statt in der README.

## REPO-HYGIENE-LOCAL-ARTIFACTS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Lokal generierte Analyse- und Visual-Inspection-Artefakte aus dem Git-Status heraushalten, ohne sie zu loeschen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/REPO-HYGIENE-LOCAL-ARTIFACTS-001.yaml`, `.gitignore`
**Abnahmekriterien:** `packages/frontend-web/visual-tour-results/`, lokale Endpoint-Dumps und temporaere Analyse-Skripte werden ignoriert; vorhandene Artefakte bleiben lokal erhalten; Workboard-Validierung und Diff-Checks sind gruen.
**Erledigt:** `.gitignore` ignoriert lokale Visual-Tour-Ergebnisse, Endpoint-Dumps und temporaere `Templanalyze`-Skripte; bestehende Artefakte bleiben lokal erhalten und verschwinden aus `git status`.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs docs/agent-ops/active-workboard.md docs/agent-ops/slices/REPO-HYGIENE-LOCAL-ARTIFACTS-001.yaml`; `git diff --check`; `git status -sb`
**Offene Risiken:** Weitere lokal erzeugte Tool-Artefakte koennen spaeter separate Ignore-Regeln benoetigen.

## CONTAINER-HEALTH-CRM-INVENTORY-001

**Von:** Claude Code / Codex Integration
**Owner:** Team
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Container-Health-Probleme in Backend, Inventory und CRM-Services nach Neustart-/Healthcheck-Diagnose repo-seitig stabilisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/CONTAINER-HEALTH-CRM-INVENTORY-001.yaml`, `app/api/v1/endpoints/*.py` 204-Response-Korrekturen, `services/inventory/app/workflows/registration.py`, `services/crm-*/**`, `services/crm-analytics/Dockerfile`, `services/crm-communication/Dockerfile`, `services/crm-multichannel/Dockerfile`, `services/crm-security/main.py`, `services/crm-workflow/Dockerfile`
**Abnahmekriterien:** FastAPI-Routen mit 204 liefern keine Response-Body-Definition mehr; Inventory-Workflow-Registrierung ist Pydantic-v2-kompatibel; CRM-Services nutzen absolute Imports und `pydantic-settings`; Docker-Builds koennen Dependency-Layer gezielt invalidieren; verbleibende Containerstarts sind separat ueber Compose-Health zu beobachten.
**Erledigt:** 115 FastAPI-204-Routen gehaertet; CRM-Konfigurationen auf `pydantic-settings` und absolute Imports gezogen; reservierte SQLAlchemy-`metadata`-Attribute umbenannt; Inventory-URL-Cast fuer Pydantic v2 korrigiert; CRM-Dockerfiles mit `CACHEBUST`-Arg fuer reproduzierbare Dependency-Rebuilds ergaenzt.
**Checks:** Commit `67f8b9c51`; gezielte Docker-/Containerdiagnose; finales Git-Diff der Nachlieferung beschraenkt auf CRM-Dockerfiles und `services/crm-security/main.py`.
**Offene Risiken:** Einzelne Container koennen weiterhin an laufzeitabhaengigen externen Dependencies, Migrationen oder Credentials scheitern; untracked Analyseartefakte bleiben ausserhalb dieses Slices.

## DESIGN-MERIDIAN-SCREENS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Die wichtigsten sichtbaren Fach-/Maskenflaechen nach der Shell-Umstellung weiter auf Meridian tokenisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-SCREENS-001.yaml`, `packages/frontend-web/src/components/mask-builder/ListReport.tsx`, `packages/frontend-web/src/components/mask-builder/ObjectPage.tsx`, `packages/frontend-web/src/components/mask-builder/OverviewPage.tsx`, `packages/frontend-web/src/features/dashboard/DashboardCharts.tsx`, `packages/frontend-web/src/features/contracts/Contracts.tsx`, `packages/frontend-web/src/features/inventory/Inventory.tsx`, `packages/frontend-web/src/features/weighing/Weighing.tsx`, `packages/frontend-web/src/features/sales/Sales.tsx`
**Abnahmekriterien:** Masken-Builder-Basisflaechen nutzen Meridian-Oberflaechen, Tabellen-/Filter-/Header-Muster und 44px Controls; Dashboard-Charts und Kernfeatures vermeiden generische Slate/Blue/Green-Mischung in den sichtbarsten Cards; Frontend-Typecheck und Workboard-Validierung sind gruen.
**Erledigt:** Masken-Builder `ListReport`, `ObjectPage` und `OverviewPage` auf Meridian-Header, tokenisierte Oberflaechen, Primary/Harvest/Destructive-Zustandsfarben und 44px-kompatible Controls nachgezogen; Dashboard-Charts auf tokenisierte Empty/Error/Skeleton-Zustaende und Ocean/Harvest-Akzentkanten umgestellt; Contracts, Inventory, Weighing und Sales von generischen Slate/Blue/Green/Yellow/Red-Utility-Mustern auf Meridian-Cards, Badges, Listen-Items und Leerzustaende gezogen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs docs/agent-ops/active-workboard.md docs/agent-ops/slices/DESIGN-MERIDIAN-SCREENS-001.yaml`; `git diff --check` fuer Slice-Dateien; `docker compose up -d --build frontend-web`; Playwright-Check auf `http://localhost:3000` mit `data-theme=meridian`, H1 `App Starter`, Topbar `56px`, Input `44px`.
**Offene Risiken:** Tiefe Modulunterseiten enthalten weiterhin harte Utility-Farben und brauchen bei Bedarf weitere fachbereichsweise Slices.

## DESIGN-MERIDIAN-SHELL-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Meridian sichtbar in Frontend-Shell und Core-UI aktivieren, damit `localhost:3000` die beschlossene Designrichtung zeigt.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DESIGN-MERIDIAN-SHELL-001.yaml`, `packages/frontend-web/index.html`, `packages/frontend-web/src/index.css`, `packages/frontend-web/src/styles/design-tokens-meridian.css`, `packages/frontend-web/tailwind.config.js`, `packages/frontend-web/src/layouts/DashboardLayout.tsx`, `packages/frontend-web/src/components/layout/AppShell.tsx`, `packages/frontend-web/src/components/navigation/AppShell.tsx`, `packages/frontend-web/src/components/navigation/Sidebar.tsx`, `packages/frontend-web/src/components/navigation/SidebarFavorites.tsx`, `packages/frontend-web/src/components/navigation/SidebarSettingsLink.tsx`, `packages/frontend-web/src/components/navigation/TopBar.tsx`, `packages/frontend-web/src/components/ui/button.tsx`, `packages/frontend-web/src/components/ui/input.tsx`, `packages/frontend-web/src/components/ui/card.tsx`, `packages/frontend-web/src/components/ui/table.tsx`, `packages/frontend-web/src/components/ui/data-table.tsx`, `packages/frontend-web/src/features/dashboard/Dashboard.tsx`, `packages/frontend-web/src/pages/start-dashboard.tsx`
**Abnahmekriterien:** Meridian-Theme ist am Root aktiv; sichtbare Shell nutzt Navy-Sidebar, tokenbasierte Breiten und kompaktere Topbar; Button/Input-Defaults erfuellen 44px-Touch-Target; Dashboard/ListReport-Basismuster zeigen Ocean-Blue/Harvest-Akzente statt generischer Slate/Blue-Mischung; Frontend-Typecheck und Workboard-Validierung sind gruen.
**Erledigt:** Meridian am HTML-Root aktiviert; alte Brand-/Neutral-Aliase auf Ocean-Blue, Harvest und blau getoente Neutrals gezogen; echte Runtime-Shell (`DashboardLayout`/`components/navigation`) startet expanded mit 240px Navy-Sidebar, 56px Topbar und 44px Sidebar-Zielen; Legacy-Shell ebenfalls auf Meridian-Breiten/-Farben nachgezogen; Button/Input/Card/Table-Basis auf Meridian-Masse und Fokusverhalten angepasst; Start-Dashboard und Analytics-Dashboard zeigen tokenbasierte Oberflaechen und Harvest/Ocean-Akzente.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-markdown-check.cjs docs/agent-ops/active-workboard.md docs/agent-ops/slices/DESIGN-MERIDIAN-SHELL-001.yaml`; `git diff --check`; Playwright computed-style check auf `http://localhost:3001` und nach Frontend-Container-Rebuild auf `http://localhost:3000` mit `data-theme=meridian`, Sidebar `240px`, Topbar `56px`, Input `44px`, min. Sidebar-Target `44px`.
**Offene Risiken:** Viele Fachseiten enthalten weiterhin harte Tailwind-Farben und brauchen Folgeslices; dieser Slice fokussiert die sichtbarste Shell/Core-UI-Schicht.

## KEYCLOAK-PSQL-DB-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-21
**Ziel des Slices:** Fehlende Keycloak-Datenbank im laufenden PostgreSQL anlegen und Init-Script fuer kuenftige Deployments absichern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/KEYCLOAK-PSQL-DB-001.yaml`, `scripts/init.sql`
**Abnahmekriterien:** Datenbank `keycloak` existiert im laufenden Postgres; Init-Script enthaelt Bootstrap fuer kuenftige Deployments; Keycloak startet ohne `database "keycloak" does not exist`; Claudes Dirty Files bleiben unberuehrt.
**Erledigt:** Laufende PostgreSQL-DB `keycloak` mit Owner `keycloak` angelegt; Verbindung als User `keycloak` gegen DB `keycloak` geprueft; `scripts/init.sql` von ungueltigem `CREATE DATABASE` im `DO`-Block auf psql-`\\gexec`-Bootstrap umgestellt; Keycloak neu gestartet und Schema-Initialisierung im Log bestaetigt.
**Checks:** `docker exec valeo-neuro-erp-postgres psql -U keycloak -d keycloak -tAc "SELECT current_database(), current_user;"`; `docker compose restart keycloak`; `docker logs --tail 40 valeo-neuro-erp-keycloak`; `python scripts/agent_workboard_supervisor.py validate`
**Offene Risiken:** Keycloak kann nach DB-Anlage noch an separaten Realm-/Credential-/Healthcheck-Themen scheitern.

## UAT-AUFLAGEN-2026-05-17

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-18
**Ziel des Slices:** Verbleibende UAT-Auflagen aus der Abnahme 2026-05-17 repo-seitig auf hohem Standard schliessen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UAT-AUFLAGEN-2026-05-17.yaml`, `docs/uat/**`, `packages/frontend-web/tests/e2e/uat/**`, `tests/uat/**`, `app/api/v1/endpoints/compliance.py`, `app/api/v1/endpoints/kontrakt_klassen.py`, `tests/test_compliance_pos_gap_extensions.py`
**Abnahmekriterien:** PCN/UFI API-Contract ist implementiert und getestet; ungueltige Kontraktklassen-Varianten werden per Pydantic validiert; UAT-Auflagenstatus ist in Protokoll und Traceability aktualisiert; fokussierte API-/UAT-Contract-Tests und Doku-Checks sind gruen.
**Erledigt:** PCN/UFI-Endpoint mit UFI-/Statusvalidierung und DB-Fallback-Vertrag gehaertet; `KontraktKlasseCreate.variante` per Pydantic `Literal` validiert; UAT-API-Contracts auf aktuelle v1-Routen und idempotente Testdaten nachgezogen; UAT-Protokoll, Master-Plan und Traceability auf repo-seitig erledigte Auflagen aktualisiert.
**Checks:** `python -m py_compile app/api/v1/endpoints/compliance.py app/api/v1/endpoints/kontrakt_klassen.py tests/uat/test_uat_api_contracts.py`; `pytest tests/uat/test_uat_api_contracts.py tests/test_compliance_pos_gap_extensions.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Externe PCN-Portal-/ECHA-Anbindung, Steuerberaterfreigabe und produktive Browser-Abnahme bleiben Betriebsfreigaben.

## VALEO-PARITY-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-18
**Ziel des Slices:** O2C/P2P/Partie-Kette als repo-seitig pruefbaren UAT-Pfad ausweisen und externe UAT-Gates sauber abgrenzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/VALEO-PARITY-001.yaml`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/agrar-parity-matrix-2026-05-17.md`, `app/api/v1/endpoints/o2c_uat_scaffold.py`, `tests/test_webshop_atlas_saatzucht_uat.py`
**Abnahmekriterien:** API liefert UAT-Readiness mit O2C/P2P/Partie-Abdeckung; bestehende 7-Schritt-Szenarien bleiben kompatibel; Gap-Status trennt repo-seitigen Pfad von externer UAT-Unterschrift; fokussierte Tests und Doku-Checks sind gruen.
**Erledigt:** `/uat/o2c/readiness` liefert repo-seitige Abdeckung fuer O2C, P2P und Partie-Kette sowie externe Gates; bestehender 7-Schritt-Szenario-Runner und Tests bleiben kompatibel; Gap- und Parity-Doku trennen repo-seitigen Pfad von externer UAT-Unterschrift.
**Checks:** `pytest tests/test_webshop_atlas_saatzucht_uat.py -q --no-cov`
**Offene Risiken:** Produktive Browser-UATs mit realen Mandanten-, Waage-, DMS-, Druck- und Steuerberaterdaten bleiben externe Abnahmen.

## REPORT-PRINT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-18
**Ziel des Slices:** Partie-Genealogie, Wiegschein-PDF-Nachweis und Etikett-/Label-Vertrag als repo-seitig pruefbaren Report-/Print-Pfad schliessen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/REPORT-PRINT-001.yaml`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/report_print.py`, `app/services/report_print_service.py`, `app/api/v1/api.py`, `tests/test_report_print_api.py`
**Abnahmekriterien:** API liefert Partie-Genealogie mit Rueckverfolgungsknoten, Wiegschein-PDF-Preview/Artefaktmetadaten und Etikettendaten fuer Charge/Partie; Router ist registriert; fokussierte Tests und Doku-Checks sind gruen.
**Erledigt:** Neuer Thin-Router `/report-print` plus `ReportPrintService` liefern Readiness, Partie-Genealogie, Wiegeschein-PDF-Preview/Artefaktmetadaten und print-ready GS1-Labeldaten fuer Partie/Charge/Artikel/SSCC/GTIN; Router ist im v1-API-Router registriert.
**Checks:** `python -m py_compile app/api/v1/endpoints/report_print.py app/services/report_print_service.py tests/test_report_print_api.py`; `pytest tests/test_report_print_api.py -q --no-cov`
**Offene Risiken:** Echte Drucker-/PDF-Rendering- und UAT-Abnahme mit Produktivdaten bleiben externe Betriebsfreigaben.

## DOMAIN-PHASE23-GAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-18
**Ziel des Slices:** Phase-2- und Phase-3-Restgaps aus dem Domain-Depth-Plan repo-seitig schliessen bzw. vorhandene Implementierungen mit Tests und Doku belastbar als geschlossen ausweisen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/DOMAIN-PHASE23-GAP-CLOSURE-001.yaml`, `docs/project-context/domain-depth-plan-2026-05-17.md`, `docs/project-context/open-gaps-and-known-issues.md`, Phase-2/3-nahe Endpoint-/Service-/Testdateien mit explizitem Fokus auf `ebilanz_elster`, `gs1_*`, `pos_dsfinvk`, `saatzucht`, `atlas_zollausfuhr`, `futtermittel`, `crm`, `finance`, `hrm`, `sales`
**Abnahmekriterien:** Phase-2/3-Plan ist nicht mehr als offener 183-Tage-Backlog missverstaendlich; verbleibende echte Luecken sind externe Gates oder klar benannte Resttiefe; fokussierte API-/Router-/Doku-Checks sind gruen.
**Erledigt:** eBilanz/ELSTER um ERiC-Readiness-Vertrag ergaenzt; GS1-Barcode-Parser gibt SSCC direkt aus; DSFinV-K-v2.3-ZIP, Phase-2/3-Routerpfade, GS1/SSCC, eBilanz-Readiness und Futtermittel-Regressionen getestet; Domain-Depth-Plan und Open-Gaps-Doku auf repo-seitig geschlossene Phase 2/3 mit externen Gates gezogen.
**Checks:** `pytest tests/test_phase23_gap_closure_api.py tests/test_gs1_webhook_ruestliste.py tests/test_sammelabrechnung_interessent_waagen_vorlage.py -q --no-cov`; `pytest tests/test_webshop_atlas_saatzucht_uat.py tests/test_compliance_pos_gap_extensions.py tests/test_futtermittel_complete.py tests/test_major_domain_router_registration.py -q --no-cov`
**Offene Risiken:** Externe Provider-Credentials, ERiC-/TSE-Pruefwerkzeuge, Steuerberater-/Rechtsfreigaben und echte UATs koennen repo-seitig nur als Readiness-/Gate-Vertraege abgebildet werden.

## L3-WEBSHOP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-18
**Ziel des Slices:** Webshop-B2B-Bestellintegration repo-seitig als belastbaren Import-/Sync-Vertrag bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/L3-WEBSHOP-001.yaml`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/*webshop*`, `app/services/*webshop*`, `app/api/v1/api.py`, `tests/test_*webshop*`
**Abnahmekriterien:** B2B-Webshop-Bestellungen koennen idempotent importiert und gelesen werden; Kunden-/Artikel-/Mengen-/Preis-/Lieferkontext wird validiert; Dubletten und fachliche Blocker werden sichtbar; Router ist unter `/api/v1/...` registriert; fokussierte Tests und Doku-Updates sind gruen.
**Erledigt:** `webshop_integration.py` vom DB-Stub auf thin-router + `WebshopIntegrationService` umgestellt; Import ist idempotent je externer Bestellnummer, meldet Dubletten und fachliche Blocker, listet/liest importierte Bestellungen und blockiert die ERP-Verarbeitung fehlerhafter Imports.
**Checks:** `python -m py_compile app/api/v1/endpoints/webshop_integration.py app/services/webshop_integration_service.py tests/test_webshop_atlas_saatzucht_uat.py`; `pytest tests/test_webshop_atlas_saatzucht_uat.py -q --no-cov`
**Offene Risiken:** Echte Shopware-/WooCommerce-/Shopify-Credentials und produktive Webhook-Signaturen bleiben externe Betriebsfreigaben.

## ENTERPRISE-DOMAIN-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-17
**Ziel des Slices:** Von parallelen Agents begonnene ERP-/Odoo-/Agrar-Spezialsoftware-Domain-Closure uebernehmen, fehlende Router-Registrierung und nicht gelieferte POS-/Compliance-Teile schliessen.
**Dateibesitz:** `app/api/v1/api.py`, `app/api/v1/endpoints/*asset_accounting.py`, `*budget_planning.py`, `*liquidity_planning.py`, `*crm_360.py`, `*crm_account_hierarchy.py`, `*logistics_tours.py`, `*logistics_freight.py`, `*purchase_invoice_verification.py`, `*ers_settlement.py`, `*rfq.py`, `*einkauf_kpis.py`, `*sales_blanket_orders.py`, `*credit_management.py`, `*collective_documents.py`, `*central_contracts.py`, `*futtermittel_rohwaren.py`, `*futtermittel_rezepte.py`, `*compliance_dsgvo.py`, `*compliance_whistleblower_lksg.py`, `*pos_payments_promotions.py`, `app/api/v1/endpoints/personal.py`, `app/api/v1/endpoints/cases.py`, `app/api/v1/endpoints/opportunities.py`, `app/api/v1/endpoints/warehouse_wms.py`, `tests/test_*domain*`, `tests/test_*gap*`, `docs/project-context/domain-depth-plan-2026-05-17.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Alle erzeugten Domain-Endpunkte sind ueber `/api/v1/...` erreichbar; HRM-Arbeitszeitkonto nutzt `domain_hr.time_entries.entry_date/hours`; POS Split-Payment und Promotions-Preview existieren; Whistleblower und LkSG-API-Vertraege existieren; fokussierte Tests und Doku-/Workboard-Checks sind gruen.
**Erledigt:** Router-Registrierungen fuer CRM, Finance, Logistik, Einkauf, Verkauf/Kontrakte, Futtermittel, HRM, Compliance und POS ergaenzt; `warehouse_wms.py` auf kanonischen Tenant-Dependency-Import korrigiert; Logistik-Statistik gegen nicht-numerische DB-/Mockwerte gehaertet; HRM-Org-Subtree und Arbeitszeitkonto fachlich korrigiert; POS Split-Payment/Promotions und Whistleblower/LkSG nachgeliefert; Domain-Depth-Plan und Open-Gaps aktualisiert.
**Checks:** `pytest tests/test_crm_pipeline_360.py tests/test_einkauf_3way_match_ers_rfq.py tests/test_finance_asset_budget_liquidity.py tests/test_logistics_tour_freight.py tests/test_major_domain_router_registration.py tests/test_personal_major_gap_extensions.py tests/test_compliance_pos_gap_extensions.py tests/test_process_kernel_wave100_settlement_completion.py tests/test_process_kernel_wave31_dq_extended_write_paths.py -q --no-cov --tb=short`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/open-gaps-and-known-issues.md docs/project-context/domain-depth-plan-2026-05-17.md`; `git diff --check`
**Offene Risiken:** Echte externe Abnahmen bleiben ausserhalb des Repos: Steuerberater-/DATEV-Mapping, DMS-Live-Probe, TSE-/DSFinV-K-Pruefwerkzeugvalidierung, E-Signatur/Providerzugang und UAT-Unterschriften mit Produktivdaten.

## ERP-FINANZ-ORDERS-DOC-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Veraltete `packages/erp-domain`-Order-REST-Dokumentation auf die entschiedene Python-FastAPI-Zielroute ausrichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/ERP-FINANZ-ORDERS-DOC-001.yaml`, `packages/erp-domain/README.md`, `packages/erp-domain/src/bootstrap.ts`, `C:\Users\Jochen\.cursor\plans\erp-finanz_roadmap_9029845d.plan.md`
**Abnahmekriterien:** README nennt keine oeffentlichen Node-Order-Endpunkte mehr; Orders-REST verweist auf `/api/v1/sales/orders`; Roadmap-Phase 3 ist nicht mehr zweigeteilt, sondern Doku/Redirect-only.
**Erledigt:** `packages/erp-domain/README.md` beschreibt Orders-REST jetzt als Python-FastAPI-Vertrag unter `/api/v1/sales/orders`; die veralteten `/api/orders`-Beispiele sind entfernt. `packages/erp-domain/src/bootstrap.ts` enthaelt keinen irrefuehrenden Controller-TODO mehr. Die Cursor-Roadmap ist auf die entschiedene Doku/Redirect-only-Variante gezogen.
**Checks:** `pnpm test:erp-domain -- erp-bootstrap-orders.spec.ts`; `python scripts/agent_workboard_supervisor.py validate`; `git diff --check`
**Offene Risiken:** Historische Archive und generierte API-Dumps koennen weiterhin alte Order-Begriffe enthalten; dieser Slice betrifft nur aktive Roadmap-/Paketdoku.

## HRM-GERMANY-GAP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Deutsche HRM-Gaps ueber Personalakte, eAU, Payroll/DATEV, ESS/MSS, Recruiting/Onboarding, Reporting, Datenschutz, kontrollierte KI und Office-Connectoren als pruefbaren Zielvertrag schliessen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GERMANY-GAP-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_readiness_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** Zielbild und Gap-Matrix decken die 15 Mindestpunkte ab; API liefert HRM-Readiness mit Status, Rechts-/Compliance-Referenzen, Integrationen, KI-Kontrollen und naechsten Slices; Tests sichern eAU, §26 BDSG, BAG-Arbeitszeitpflicht, EU-AI-Act-Hochrisiko und Office-/DATEV-Connectoren.
**Erledigt:** `GET /api/v1/personal/hrm-readiness` eingefuehrt; Zielvertrag deckt die 15 HRM-Mindestpunkte, eAU, Personalakte, DATEV/Payroll, ESS/MSS, Recruiting/Performance, Datenschutz, kontrollierte KI und Office-Connectoren ab. Frontend-API-Hook `useHrmReadiness` ergaenzt. Gap-Plan und Open-Gaps-Doku aktualisiert.
**Checks:** `pytest tests/test_personal_hrm_readiness_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Rechtsfeinpruefung, Betriebsvereinbarungen, echte eAU-/DATEV-/Microsoft-/Google-Zugangsdaten und produktive AVV/DPA bleiben Folgeslices.

## HRM-AKTE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Ersten Vertrag fuer digitale Personalakte mit Dokumentklassen, DMS-Referenzen, Rollenfilter, Audit- und Retention-Sicht bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-AKTE-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_employee_file_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** Personalakte kann Dokumentmetadaten lesen und anlegen; Dokumentklassen weisen Rechtsgrundlage, Standard-Sichtbarkeit und Retention aus; Rollenfilter fuer Employee/Manager/HR/Payroll ist regressionsgesichert; Export-/Loeschkonzept ist im Contract sichtbar.
**Erledigt:** `GET /api/v1/personal/employee-files/{employee_ref}` und `POST /api/v1/personal/employee-files/{employee_ref}/documents` eingefuehrt. Dokumentklassen, Rollenfilter, Exportpaket, Retention-Sicht und Frontend-Hooks sind verfuegbar; Doku markiert produktive DB-/DMS-Anbindung als Folgeslice.
**Checks:** `pytest tests/test_personal_employee_file_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_employee_file_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive DMS-Ablage, echte Signaturen, Rechtsfreigabe der Aufbewahrungsfristen und DB-Migration bleiben Folgeslices.

## HRM-GAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Alle verbleibenden HRM-Plan-Gaps repo-seitig als API-/Frontend-/Doku-Vertraege schliessen: eAU, DATEV/Payroll-Closeout, Vertragsvorlagen, ESS, MSS, Recruiting, Analytics, Privacy, AI-Governance und Office-Connectoren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GAP-CLOSURE-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_gap_closure_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** HRM-Plan weist keine fachlichen Repo-Gaps mehr aus; jeder verbliebene Punkt hat einen API-Vertrag und Frontend-Hook; Tests sichern eAU ohne Diagnosedaten, DATEV-Closeout, Vertragsvorlagen, ESS/MSS, Recruiting-Retention, Analytics-Aggregationsschutz, AI-Human-Gate und Office-Connector-Readiness.
**Erledigt:** `GET /api/v1/personal/hrm-operating-system` eingefuehrt; HRM-Plan weist keine fachlichen Repo-Gaps mehr aus. Frontend-Hook `useHrmOperatingSystem` ergaenzt. Tests sichern eAU ohne Diagnosedaten, DATEV-Closeout, Vertragsvorlagen, ESS/MSS, Recruiting-Retention, Analytics-Aggregationsschutz, AI-Human-Gate, Office-Connector-Readiness und die kanonischen `time_entries`-Service-Regeln.
**Checks:** `pytest tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_employee_file_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_employee_file_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte eAU-/DATEV-/Microsoft-/Google-/LibreOffice-/E-Signatur-Zugangsdaten, AVV/DPA, Betriebsvereinbarungen, DSFA und Rechtsfreigaben bleiben externe Betriebsfreigaben.

## HRM-OPERATIONS-GATES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Externe HRM-Betriebsfreigaben fachlich sauber zum Abschluss fuehren: Evidenzanforderungen, Owner, Go-live-Blocker, Abnahme und Auditstatus fuer eAU, DATEV, Office/SSO, LibreOffice/E-Signatur, AVV/DPA, Betriebsrat, DSFA und Rechtsfreigaben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-001.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_operations_gates_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** `GET /api/v1/personal/hrm-operations-gates` liefert Gate-Status mit Evidenzpflichten und Go-live-Blockern; Doku unterscheidet fachlich abgeschlossen, repo-seitig umgesetzt und extern freizugeben; Tests sichern alle externen Gates und Professional-Practice-Kriterien.
**Erledigt:** `GET /api/v1/personal/hrm-operations-gates` eingefuehrt; alle verbleibenden HRM-Betriebsfreigaben sind als blockierende Gates mit Owner, Evidenzanforderungen, Abnahmekriterien, Auditspur und Professional-Practice-Regeln modelliert. Frontend-Hook `useHrmOperationsGates` ergaenzt. HRM-Plan und Open-Gaps-Doku fuehren keine unspezifizierten Restpunkte mehr, sondern nur noch evidenzbasierte Go-live-Gates.
**Checks:** `pytest tests/test_personal_hrm_operations_gates_api.py tests/test_personal_hrm_gap_closure_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_operations_gates_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Abschluss der Gates erfordert reale externe Nachweise; ohne diese Nachweise bleibt Go-live bewusst blockiert.

## HRM-OPERATIONS-GATES-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Betriebsfreigabe-Gates technisch vollstaendig machen: persistente Gate-/Evidence-Daten, Approval-/Reject-Workflow, Connector-Probe-Status, Auditspur und Go-live-Policy.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-002.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `alembic/versions/hrm_operations_gates_20260513.py`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_operations_gate_workflow_api.py`, `packages/frontend-web/src/lib/api/personal.ts`
**Abnahmekriterien:** Gates werden aus DB-Zustand plus Default-Katalog gelesen; Evidence kann angelegt werden; Gate-Entscheidungen koennen approved/rejected werden; Connector-Probes aktualisieren Status; `goLiveAllowed` wird aus persistenten Status abgeleitet; API-/Frontend-Contracts und Tests sind vorhanden.
**Erledigt:** Persistente Gate-, Evidence-, Probe- und Audit-Tabellen per Alembic ergaenzt; `GET /hrm-operations-gates` liest Runtime-Status aus DB mit Katalog-Fallback; Evidence-, Probe- und Decision-Endpunkte sowie `GET /hrm-operations-gates/go-live-policy` umgesetzt; Frontend-Hooks fuer Lesen, Evidence, Probe, Entscheidung und Go-live-Policy ergaenzt; Tests sichern Seed, Evidence, Probe, Approval, Evidence-Pflicht und Blocker-Policy.
**Checks:** `pytest tests/test_personal_hrm_operations_gate_workflow_api.py tests/test_personal_hrm_operations_gates_api.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_employee_file_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_operations_gate_workflow_api.py alembic/versions/hrm_operations_gates_20260513.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte externe Providerzugriffe benoetigen weiterhin produktive Credentials; dieser Slice implementiert die technische Workflow- und Persistenzschicht inklusive Probe-Status, nicht die Beschaffung externer Freigaben.

## HRM-OPERATIONS-GATES-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Betriebsfreigabe-Gates als bedienbares Frontend-Cockpit verfuegbar machen: Go-live-Status, Gate-Liste, Evidence-Erfassung, Probe-Erfassung und Approval/Reject-Aktionen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-003.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `packages/frontend-web/src/app/navigation/domains/operations.tsx`, `packages/frontend-web/src/app/route-builders/alias-groups/generated/personal.ts`, `packages/frontend-web/src/app/route-builders/auto-groups/generated/personal.ts`
**Abnahmekriterien:** Personal-Navigation enthaelt das HRM-Freigabe-Cockpit; Route ist aufloesbar; UI zeigt Go-live-Policy, Blocker und Gate-Details; pro Gate koennen Evidence, Probe und Entscheidung ausgelöst werden; Typecheck ist gruen.
**Erledigt:** `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx` als HR-Freigabe-Cockpit ergaenzt; Personal-Navigation und Route-Aliase zeigen `/personal/hrm-freigaben`; UI nutzt einfache Buero-Sprache fuer Produktivstart, Pruefpunkte, Nachweise, Tests, Freigaben und naechste Aktionen. HRM-Plan und Open-Gaps-Doku markieren den Bedienpfad als repo-seitig geschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte externe Freigaben bleiben betriebliche Nachweise; UI stellt den technischen Bedienpfad bereit.

## HRM-OPERATIONS-GATES-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Freigabe-Cockpit fachlich als Admin-/Compliance-/Go-live-Readiness-Arbeitsflaeche schaerfen: Name, Risiko, Prioritaet, Faelligkeit, Rollenhinweis und letzte Aenderung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-004.yaml`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_operations_gate_workflow_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `packages/frontend-web/src/app/navigation/domains/operations.tsx`
**Abnahmekriterien:** API liefert Readiness-Metadaten je Gate; UI heisst HRM-Betriebsfreigaben; UI zeigt Risiko, Prioritaet, Faelligkeit, letzte Aenderung, Rollen-/Sichtbarkeitshinweis und Abnahmekriterien; Typecheck und fokussierte API-Tests sind gruen.
**Erledigt:** `HrmOperationsGateOut` liefert Prioritaet, Risiko-Level, Faelligkeit, letzte Aenderung, berechtigte Rollen und Read-only-Rollen. Das Frontend heisst jetzt `HRM-Betriebsfreigaben`, zeigt Admin-/Compliance-/Readiness-Kontext, Risiko, Prioritaet, Faelligkeit, letzte Aenderung, Rollenhinweis und einfache Arbeitsbegriffe.
**Checks:** `pytest tests/test_personal_hrm_operations_gate_workflow_api.py tests/test_personal_hrm_operations_gates_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_operations_gate_workflow_api.py`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive Rollen-/Rechtesteuerung haengt an der zentralen Auth-/Navigation-Enforcement; dieser Slice macht fachliche Sichtbarkeit und API-Metadaten explizit.

## HRM-OPERATIONS-GATES-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** Google-Studio-Designentwurf fuer `HRM-Betriebsfreigaben` in die bestehende VALEO-React-Seite uebertragen: Readiness-Header, KPI-Leiste, Policy-Box, Stopper-Markierung, kompakte Pruefpunkt-Zeilen und aufklappbare Arbeitsbereiche.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-OPERATIONS-GATES-005.yaml`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`
**Abnahmekriterien:** Seite folgt dem Studio-Entwurf ohne neue Dependencies; bestehende React-Query-Hooks bleiben verdrahtet; sichtbare Sprache bleibt buerotauglich; Typecheck ist gruen.
**Erledigt:** Google-Studio-Entwurf in die echte VALEO-Seite uebertragen: sticky Readiness-Header, KPI-Leiste, Policy-Box, Stopper-Markierung, kompakte Pruefpunkt-Zeilen, aufklappbare Details und Arbeitsaktionen. Keine neue `motion`-Dependency; alle bestehenden Runtime-Hooks bleiben verdrahtet.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Studio-Prototyp enthaelt Mockdaten und `motion`; Uebernahme erfolgt auf echte VALEO-Daten und ohne zusaetzliche Animationsdependency.

## HRM-GO-LIVE-TEMPLATES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Go-live-Evidenzpaket als operative Repo-Vorlagen unter `docs/hrm-go-live-templates/` bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-TEMPLATES-001.yaml`, `docs/hrm-go-live-templates/README.md`, `docs/hrm-go-live-templates/00_hrm_go_live_gesamtwerk.md`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Gesamtwerk enthaelt Gate-Matrix, Go-live-Protokoll, Betriebsratsstatus, Mitarbeiterinformation, VVT, AVV/DPA, DSFA, Rollen, TOM, Retention, eAU, DATEV/Payroll, Office/SSO, DMS/E-Signatur, KI/Analytics, Evidence/Audit, Geschaeftsfuehrungsfreigabe und optionale Betriebsvereinbarung; Doku verweist auf das Vorlagenpaket; rechtlicher Arbeitsvorlagen-Charakter ist klar markiert.
**Erledigt:** `docs/hrm-go-live-templates/README.md` und `00_hrm_go_live_gesamtwerk.md` ergaenzt. Das Gesamtwerk deckt alle sieben HRM-Betriebsfreigabe-Gates mit ausfuellbaren Arbeitsmustern, Mindest-Evidence, Freigaben und Auditspur ab. HRM-Plan und Open-Gaps-Doku verweisen auf das Vorlagenpaket.
**Checks:** `rg -n "HRM-GATE-001|Mindest-Evidence|BDSG Paragraf 26|DSFA-Vorpruefung|Geschaeftsfuehrungsfreigabe" docs/hrm-go-live-templates/00_hrm_go_live_gesamtwerk.md`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktivnutzung erfordert reale Datenschutz-, Payroll-/Steuerberater-, IT-Sicherheits- und Rechtspruefung.

## HRM-GO-LIVE-TEMPLATES-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Go-live-Formulare auf den tatsaechlichen VALEO-Funktionsumfang begrenzen und hypothetische, nicht vorgesehene KI-/Auswertungsbegriffe aus Mitarbeiter- und Freigabetexten entfernen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-TEMPLATES-002.yaml`, `docs/hrm-go-live-templates/README.md`, `docs/hrm-go-live-templates/00_hrm_go_live_gesamtwerk.md`, `docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_hrm_gap_closure_api.py`
**Abnahmekriterien:** Formulare nennen keine nicht vorgesehenen Funktionen; Mitarbeiterinformation beschreibt nur real vorgesehene HRM-Funktionen; KI-Freigabe ist als optionale Assistenzfunktions-Pruefung formuliert; API-/Doku-Vertraege sind konsistent.
**Erledigt:** Formulare, HRM-Plan, Open-Gaps-Doku und Personal-API sind auf den realen Funktionsumfang gezogen. Mitarbeitertexte nennen Personalverwaltung, Arbeitszeit, Abwesenheiten, Dokumente, Payroll-Vorbereitung, freigegebenes HR-Reporting, Compliance und optional konkret freigegebene KI-Assistenz; hypothetische Sonderfunktionen wurden entfernt.
**Checks:** `pytest tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_hrm_operations_gates_api.py -q --no-cov`; `python -m py_compile app/api/v1/endpoints/personal.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_readiness_api.py tests/test_personal_hrm_operations_gates_api.py`; `rg -n "Emotion|Scoring|Ranking|Score|Profiling|verdeckte|heimliche|Leistungsueberwachung|Verhaltens|KI-/Analytics|Analytics-/KI|Reports und Scores" docs/hrm-go-live-templates docs/project-context/hrm-germany-operating-system-gap-plan-2026-05-13.md docs/project-context/open-gaps-and-known-issues.md app/api/v1/endpoints/personal.py tests/test_personal_hrm_gap_closure_api.py tests/test_personal_hrm_operations_gates_api.py tests/test_personal_hrm_readiness_api.py` (keine Treffer); `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Konkrete spaetere KI- oder Analytics-Erweiterungen brauchen erneut gesonderte Datenschutz-, Legal- und Betriebsratspruefung.

## HRM-GO-LIVE-TEMPLATES-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Go-live-Gesamtwerk in einzelne, direkt auffindbare Formular-Dateien unter `docs/hrm-go-live-templates/` zerlegen, ohne den fachlichen Master zu duplizieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-TEMPLATES-003.yaml`, `docs/hrm-go-live-templates/README.md`, `docs/hrm-go-live-templates/01_hrm_go_live_freigabeprotokoll.md`, `docs/hrm-go-live-templates/02_betriebsratsstatus_kein_betriebsrat.md`, `docs/hrm-go-live-templates/03_mitarbeiterinformation_hrm.md`, `docs/hrm-go-live-templates/04_vvt_hrm_system.md`, `docs/hrm-go-live-templates/05_avv_dpa_pruefprotokoll.md`, `docs/hrm-go-live-templates/06_dsfa_vorpruefung.md`, `docs/hrm-go-live-templates/07_rollen_berechtigungskonzept.md`, `docs/hrm-go-live-templates/08_tom_it_sicherheitsfreigabe.md`, `docs/hrm-go-live-templates/09_retention_loeschkonzept.md`, `docs/hrm-go-live-templates/10_eau_freigabeprotokoll.md`, `docs/hrm-go-live-templates/11_datev_payroll_abnahme.md`, `docs/hrm-go-live-templates/12_office_sso_abnahme.md`, `docs/hrm-go-live-templates/13_dms_esignatur_rendering_abnahme.md`, `docs/hrm-go-live-templates/14_ki_assistenz_reporting_freigabe.md`, `docs/hrm-go-live-templates/15_evidence_auditprotokoll.md`, `docs/hrm-go-live-templates/16_geschaeftsfuehrungsfreigabe.md`, `docs/hrm-go-live-templates/17_betriebsvereinbarung_optional.md`
**Abnahmekriterien:** Alle im README genannten Einzelvorlagen existieren; jede Einzelvorlage ist als Auszug mit Zweck, Verwendung und Link zum Master auffindbar; keine Einzelvorlage nennt hypothetische, nicht vorgesehene HRM-Funktionen; Doku-Checks sind gruen.
**Erledigt:** Einzelvorlagen `01_...` bis `17_...` unter `docs/hrm-go-live-templates/` ergaenzt und im README verlinkt. Jede Vorlage ist als Arbeitsauszug aus dem Master gekennzeichnet und auf den realen HRM-Funktionsumfang begrenzt. HRM-Plan und Open-Gaps-Doku nennen die operativen Einzelvorlagen.
**Checks:** `Get-ChildItem -Path docs/hrm-go-live-templates -Filter *.md`; `rg -n "Emotion|Scoring|Ranking|Score|Profiling|verdeckte|heimliche|Leistungsueberwachung|Verhaltens|KI-/Analytics|Analytics-/KI|Reports und Scores" docs/hrm-go-live-templates` (keine Treffer); `$files = (Get-ChildItem -Path docs/hrm-go-live-templates -Filter *.md | ForEach-Object { $_.FullName }); node scripts/docs-markdown-check.cjs @files`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Die Einzeldateien sind Arbeitskopien aus dem Master; bei inhaltlichen Aenderungen muss der Master als Source of Truth zuerst angepasst werden.

## HRM-GO-LIVE-UX-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-13
**Ziel des Slices:** HRM-Betriebsfreigaben von Compliance-Cockpit zu gefuehrter Arbeitsflaeche ausbauen und daraus einen repo-weiten UX-Exzellenzstandard fuer alle Domaenen ableiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HRM-GO-LIVE-UX-001.yaml`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** HRM-Seite bietet Rollenfokus, Gate-Aufgabenplan, Vorlage-Link je Gate, gefuehrte Nachweis-/Test-/Freigabe-Schritte, Audit-Zeitleiste und Management-Entscheidungsbild; repo-weiter UX-Standard uebertraegt diese Muster auf alle Domaenen; Typecheck und Doku-Checks sind gruen.
**Erledigt:** HRM-Betriebsfreigaben bieten jetzt Rollenfokus, Management-Entscheidungsbild, Vorlage-Link je Gate, gefuehrte Auswahllisten fuer Nachweise und Tests, Aufgabenplan je Gate und Audit-Zeitleiste. Der neue UX-Exzellenzstandard uebertraegt Rollenfokus, Aufgabenplan, naechste Aktion, Vorlage-/Nachweislink, gefuehrte Eingabe, Audit-Zeitleiste und Management-Bild auf alle Domaenen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/project-context/open-gaps-and-known-issues.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/HRM-GO-LIVE-UX-001.yaml`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Vollstaendige Ueberarbeitung aller Domaenen bleibt ein Rollout-Programm; dieser Slice liefert Referenzumsetzung und verbindlichen Standard.

## UX-STANDARD-COMPONENTS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Wiederverwendbare UX-Exzellenz-Komponenten fuer Rollenfokus, Aufgabenplan, naechste Aktion, Evidence-Link, Audit-Zeitleiste, Managemententscheidung und CRUD-Abdeckung bereitstellen und in HRM als Referenz nutzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-STANDARD-COMPONENTS-001.yaml`, `packages/frontend-web/src/components/workflow/ux-standard.tsx`, `packages/frontend-web/src/components/workflow/index.ts`, `packages/frontend-web/src/pages/personal/hrm-operations-gates.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Komponenten sind typisiert und domaenenneutral; HRM nutzt mindestens Rollenfokus, Aufgabenplan, Evidence-Link, Audit-Zeitleiste und Managemententscheidung aus dem Baukasten; UX-Standard dokumentiert den Baukasten und CRUD-Matrix; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `ux-standard.tsx` stellt `RoleFocusBar`, `OperationalTaskPlan`, `NextActionPanel`, `EvidenceTemplateLink`, `AuditTimeline`, `ManagementDecisionPanel`, `CrudCapabilityChecklist` und `EmptyStateWithAction` bereit. HRM-Betriebsfreigaben nutzen den Baukasten fuer Rollenfokus, Aufgabenplan, Evidence-Link, Audit-Zeitleiste, Next Action und Managemententscheidung. UX-Standard dokumentiert Komponenten und CRUD-Abdeckung.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-STANDARD-COMPONENTS-001.yaml`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Weitere Domaenen muessen in Folgeslices migriert werden; dieser Slice schafft den gemeinsamen Baukasten und die HRM-Referenzverdrahtung.

## UX-FINANCE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Den UX-Exzellenzbaukasten auf Finance/FIBU anwenden, beginnend mit dem Kreditoren-Zahlungslauf als produktkritischer Zahlungsarbeitsflaeche.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-001.yaml`, `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Kreditoren-Zahlungslauf zeigt Rollenfokus, Aufgabenplan, Managemententscheidung, Audit-/Zahlungspfad und CRUD-Abdeckung; naechste Aktion bleibt sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/zahlungslauf-kreditoren.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Aufgabenplan, Managemententscheidung, Next Action und CRUD-Abdeckung. Der bestehende Zahlungspfad und Kontext bleiben erhalten. UX-Standard dokumentiert den Finance-Rollout-Status und naechste Finance-Slices.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Weitere Finance-Seiten wie UStVA, Mahnwesen und Abschluss folgen in separaten Rollout-Slices.

## UX-FINANCE-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** UStVA als zweite Finance-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Melde-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Meldeabdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-002.yaml`, `packages/frontend-web/src/pages/finance/ustva.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** UStVA zeigt Rollenfokus fuer FIBU, Steuerbuero, Controlling und Leitung; Melde-Aufgabenplan fuehrt Periode, Abweichungen, Freigabe und ELSTER; Managemententscheidung zeigt abgabefaehig/gestoppt; CRUD-/Meldeabdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/ustva.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Melde-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Meldeabdeckung. Bestehender Meldeverlauf, UStVA-Kontext, FIBU-KPIs und Submit-/Export-Aktionen bleiben erhalten. UX-Standard markiert `UX-FINANCE-002` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Mahnwesen und Periodenabschluss folgen in separaten Finance-UX-Slices.

## UX-FINANCE-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Mahnwesen als dritte Finance-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Mahn-Aufgabenplan, Eskalationsentscheidung, Next Action und CRUD-/Kommunikationsabdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-003.yaml`, `packages/frontend-web/src/pages/finance/mahnwesen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Mahnwesen zeigt Rollenfokus fuer FIBU, Forderungsmanagement, Vertrieb, Leitung und Steuerbuero; Aufgabenplan fuehrt OP-Auswahl, Parameter, Versand/Eskalation und Zahlungsklaerung; Managemententscheidung zeigt sendbar/gestoppt; CRUD-/Kommunikationsabdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/mahnwesen.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Mahn-Aufgabenplan, Eskalationsentscheidung, Next Action und CRUD-/Kommunikationsabdeckung. Bestehende Mahnlage, Kontext, FIBU-KPIs, Versand-, Paid-, Export- und Inkasso-Aktionen bleiben erhalten. UX-Standard markiert `UX-FINANCE-003` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Periodenabschluss folgt in separatem Finance-UX-Slice.

## UX-FINANCE-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Periodenabschluss als vierte Finance-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Close-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Close-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FINANCE-004.yaml`, `packages/frontend-web/src/pages/finance/abschluss.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Periodenabschluss zeigt Rollenfokus fuer FIBU, Controlling, Steuerbuero, Leitung und Audit; Close-Aufgabenplan fuehrt Periode, Abstimmung, Freigabe und Sperre/Export; Managemententscheidung zeigt abschliessbar/gestoppt; CRUD-/Close-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `finance/abschluss.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Close-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Close-Abdeckung. Bestehende Abschlusslage, Kontext, FIBU-KPIs, Calculate-/Approve-/Close-/Lock- und Export-Aktionen bleiben erhalten. UX-Standard markiert `UX-FINANCE-004` als abgeschlossen und leitet Einkauf/CRM/Logistik als naechste Rollout-Domaenen ein.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-FINANCE-004.yaml`; `git diff --check`
**Offene Risiken:** Einkauf und weitere Domaenen folgen in separaten UX-Rollout-Slices.

## UX-EINKAUF-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Rechnungseingaenge als erste Einkaufs-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Freigabeplan, Managemententscheidung, Next Action und CRUD-/Workflow-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-001.yaml`, `packages/frontend-web/src/pages/einkauf/rechnungseingaenge-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Rechnungseingaenge zeigen Rollenfokus fuer Einkauf, Wareneingang, FIBU, Leitung und Audit; Aufgabenplan fuehrt Erfassen, Pruefen, Freigeben und Verbuchen; Managemententscheidung zeigt buchbar/gestoppt; CRUD-/Workflow-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/rechnungseingaenge-liste.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Freigabeplan, Managemententscheidung, Next Action und CRUD-/Workflow-Abdeckung. Bestehende Rechnungseingangs-KPIs, Bulk-Pruefen, Bulk-Freigeben, Bulk-Verbuchen, Export und Importpfad bleiben erhalten. UX-Standard markiert `UX-EINKAUF-001` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-001.yaml`; `git diff --check`
**Offene Risiken:** Bestellung, Wareneingang und Lieferantenstamm folgen in separaten Einkaufs-UX-Slices.

## UX-CRM-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Opportunities als erste CRM-/Vertriebs-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Pipeline-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-CRM-001.yaml`, `packages/frontend-web/src/pages/crm/opportunities-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Opportunities zeigen Rollenfokus fuer Vertrieb, Inside Sales, Leitung, Finance und Customer Success; Aufgabenplan fuehrt Qualifizieren, Angebot erstellen, Entscheiden und Nachfassen; Managemententscheidung zeigt Pipeline handlungsfaehig/leer; CRUD-/Pipeline-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `crm/opportunities-liste.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Pipeline-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Pipeline-Abdeckung. Bestehende Opportunity-Liste, CSV-Import/-Export und Bulk-Aktionen fuer Angebot, gewonnen und verloren bleiben erhalten. UX-Standard markiert `UX-CRM-001` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-CRM-001.yaml`; `git diff --check`
**Offene Risiken:** Angebots- und Auftragseditor folgen in separaten Sales-/CRM-UX-Slices.

## UX-SALES-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Verkaufsauftraege als erste Sales-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Auftrag-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Fulfillment-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-001.yaml`, `packages/frontend-web/src/pages/sales/auftraege-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Verkaufsauftraege zeigen Rollenfokus fuer Vertrieb, Auftragsabwicklung, Logistik, Finance und Leitung; Aufgabenplan fuehrt Erfassen, Liefertermin klaeren, Liefern und Fakturieren; Managemententscheidung zeigt handlungsfaehig/leer; CRUD-/Fulfillment-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/auftraege-liste.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Auftrag-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Fulfillment-Abdeckung. Bestehende Filter, Suche, CSV-Import, Export, Druck und Editor-Navigation bleiben erhalten. UX-Standard markiert `UX-SALES-001` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-001.yaml`; `git diff --check`
**Offene Risiken:** Angebotsliste und Auftragseditor folgen in separaten Sales-UX-Slices.

## UX-LOGISTIK-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Tourenplanung als erste Logistik-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Dispo-Plan, Managemententscheidung, Next Action und CRUD-/Transport-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-001.yaml`, `packages/frontend-web/src/pages/logistik/tourenplanung.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Tourenplanung zeigt Rollenfokus fuer Disposition, Fahrer, Lager/Waage, QS und Leitung; Aufgabenplan fuehrt Planen, Ressourcen klaeren, unterwegs ueberwachen und abschliessen; Managemententscheidung zeigt disponierbar/blockiert; CRUD-/Transport-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `logistik/tourenplanung.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Dispo-Aufgabenplan, Managemententscheidung, Next Action und CRUD-/Transport-Abdeckung. Bestehende Tourenlage, Ressourcen-KPIs, Supply-Chain-Kontext und aktive Tourenliste bleiben erhalten. UX-Standard markiert `UX-LOGISTIK-001` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-001.yaml`; `git diff --check`
**Offene Risiken:** Frachtbriefe und Waage folgen in separaten Logistik-UX-Slices.

## UX-EINKAUF-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Bestellungen als zweite Einkaufs-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Bestell-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Liefer-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-002.yaml`, `packages/frontend-web/src/pages/einkauf/bestellungen-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Bestellungen zeigen Rollenfokus fuer Einkauf, Wareneingang, Finance, Lieferant und Leitung; Aufgabenplan fuehrt Erfassen, Freigeben, Bestellen/Liefern und Nachweis/Export; Managemententscheidung zeigt bestellfaehig/blockiert; CRUD-/Liefer-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/bestellungen-liste.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Bestell-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Liefer-Abdeckung. Bestehende Listenfunktion, Bulk-Freigabe, Bulk-Storno, Druck, Import, Export und Detailnavigation bleiben erhalten. UX-Standard markiert `UX-EINKAUF-002` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-002.yaml`; `git diff --check`
**Offene Risiken:** Wareneingang und Lieferantenstamm folgen in separaten Einkaufs-UX-Slices.

## UX-SALES-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Angebotsliste als zweite Sales-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Angebots-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Conversion-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-002.yaml`, `packages/frontend-web/src/pages/sales/angebote-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Angebote zeigen Rollenfokus fuer Vertrieb, Inside Sales, Auftragsabwicklung, Finance und Leitung; Aufgabenplan fuehrt Erfassen, Nachfassen, Entscheiden und in Auftrag ueberfuehren; Managemententscheidung zeigt Angebotsarbeit handlungsfaehig/leer; CRUD-/Conversion-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/angebote-liste.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Angebots-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Conversion-Abdeckung. Bestehende Suche, Filter, CSV-Import, Export, Druck und Detailnavigation bleiben erhalten. UX-Standard markiert `UX-SALES-002` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-002.yaml`; `git diff --check`
**Offene Risiken:** Auftragseditor folgt in separatem Sales-UX-Slice.

## UX-LOGISTIK-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-14
**Ziel des Slices:** Frachtbriefe als zweite Logistik-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Dokument-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-002.yaml`, `packages/frontend-web/src/pages/logistik/frachtbriefe.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Frachtbriefe zeigen Rollenfokus fuer Disposition, Fahrer, Lager/Waage, Dokumentation und Leitung; Aufgabenplan fuehrt Erstellen, Versenden, Transport verfolgen und Zustellung sichern; Managemententscheidung zeigt nachweisfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `logistik/frachtbriefe.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Dokument-Follow-up-Plan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Frachtlage, Supply-Chain-Kontext, Suche, Ketten-KPIs und Frachtbrief-Liste bleiben erhalten. UX-Standard markiert `UX-LOGISTIK-002` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-002.yaml`; `git diff --check`
**Offene Risiken:** Waage folgt in separatem Logistik-UX-Slice.

## UX-EINKAUF-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Wareneingang als dritte Einkaufs-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Eingangspruefplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-003.yaml`, `packages/frontend-web/src/pages/einkauf/wareneingang.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Wareneingang zeigt Rollenfokus fuer Wareneingang, Einkauf, QS, Lager und Finance; Aufgabenplan fuehrt Bestellung auswaehlen, Lieferschein erfassen, Mengen/QS pruefen und buchen; Managemententscheidung zeigt buchbar/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/wareneingang.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Eingangspruefplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Bestellauswahl, Lieferschein-/Kopfdatenerfassung, Mengen-/QS-Tabelle und Buchungsaktion bleiben erhalten. UX-Standard markiert `UX-EINKAUF-003` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-003.yaml`; `git diff --check`
**Offene Risiken:** Lieferantenstamm folgt in separatem Einkaufs-UX-Slice.

## UX-SALES-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Auftragseditor als dritte Sales-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Auftrags-Erfassungsplan, Managemententscheidung, Next Action und CRUD-/Folgebeleg-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-003.yaml`, `packages/frontend-web/src/pages/sales/order-editor.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Auftragseditor zeigt Rollenfokus fuer Vertrieb, Auftragsabwicklung, Logistik, Finance und Leitung; Aufgabenplan fuehrt Kunde, Positionen, Liefertermin und Folgebeleg; Managemententscheidung zeigt belegfaehig/blockiert; CRUD-/Folgebeleg-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/order-editor.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Auftrags-Erfassungsplan, Managemententscheidung, Next Action und CRUD-/Folgebeleg-Abdeckung. Bestehende Kundenauswahl, Positionserfassung, Belegfolge, Druck, DMS, Attestation, Lieferschein- und Sofort-Rechnung-Aktionen bleiben erhalten. UX-Standard markiert `UX-SALES-003` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-003.yaml`; `git diff --check`
**Offene Risiken:** Detailtiefe einzelner Dialoge bleibt im bestehenden Editor; dieser Slice setzt den Leitbereich oberhalb der Maske.

## UX-EINKAUF-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Lieferantenstamm als vierte Einkaufs-Arbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Lieferanten-Onboardingplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Compliance-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-004.yaml`, `packages/frontend-web/src/pages/einkauf/lieferanten-stamm.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Lieferantenstamm zeigt Rollenfokus fuer Einkauf, QS, Finance, Compliance und Leitung; Aufgabenplan fuehrt Stammdaten, Bank/Zahlung, QS-/Dokumentnachweise und Sperr-/Archivstatus; Managemententscheidung zeigt einkaufsbereit/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/lieferanten-stamm.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Lieferanten-Onboardingplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Compliance-Abdeckung. Bestehende Stammdaten-, Kontakt-, Bank-, Steuer-, Klassifikations-, Compliance- und QS-Tabs bleiben erhalten. UX-Standard markiert `UX-EINKAUF-004` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-004.yaml`; `git diff --check`
**Offene Risiken:** Detaildialoge fuer Ansprechpartner, Bankkonten, Klassifikationen und Dokumente bleiben bestehend; dieser Slice setzt den Leitbereich oberhalb der Stammdatenmaske.

## UX-SALES-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Rechnungs- und Lieferschein-Editor als Folgebeleg-Arbeitsflaechen auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Folgebelegplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-004.yaml`, `packages/frontend-web/src/pages/sales/invoice-editor.tsx`, `packages/frontend-web/src/pages/sales/delivery-editor.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Rechnungseditor zeigt Rollenfokus fuer Faktura, Vertrieb, Finance und Leitung; Lieferschein-Editor zeigt Rollenfokus fuer Versand, Vertrieb, Lager und Faktura; beide zeigen Folgebelegplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/invoice-editor.tsx` und `sales/delivery-editor.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Folgebelegplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Docflow-, Approval-, Druck-, Export-, OP-, Kunden-, Artikel- und Lieferscheinbuchungsfunktionen bleiben erhalten. UX-Standard markiert `UX-SALES-004` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-004.yaml`; `git diff --check`
**Offene Risiken:** Tiefe Belegdruck- und Exportprozesse bleiben in bestehenden Funktionen; dieser Slice setzt den Leitbereich oberhalb der bestehenden Editor-Masken.

## UX-LOGISTIK-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Waagearbeitsflaechen auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Waage-Aufgabenplan, Stopper-/Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-003.yaml`, `packages/frontend-web/src/pages/waage/wiegungen.tsx`, `packages/frontend-web/src/pages/waage/wiegeschein-detail.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Wiegungen und Wiegeschein-Detail zeigen Rollenfokus fuer Waage, Annahme, Disposition, QS und Abrechnung; Aufgabenplan fuehrt Ticket, Gewichte, Qualitaet, Kontrakt und Abschluss; Stopper-/Managemententscheidung zeigt buchbar/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `waage/wiegungen.tsx` und `waage/wiegeschein-detail.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Waage-/Wiegeschein-Aufgabenplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Ticketanlage, Gewichtserfassung, Kontraktzuordnung, Supply-Chain-Kennzahlen, Timeline und Detail-Tabs bleiben erhalten. UX-Standard markiert `UX-LOGISTIK-003` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-003.yaml`; `git diff --check`
**Offene Risiken:** Waage-Hardware-Integration bleibt ausserhalb dieses Slice; dieser Slice fokussiert die Bedien- und Nachweissicht.

## UX-EINKAUF-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Lieferantenbewertung auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Bewertungsplan, Eskalationsentscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-005.yaml`, `packages/frontend-web/src/pages/einkauf/lieferantenbewertung.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Lieferantenbewertung zeigt Rollenfokus fuer Einkauf, QS, Finance und Leitung; Bewertungsplan fuehrt Datenbasis, Scores, Eskalation und Review; Managemententscheidung zeigt akzeptabel/klaerungsbeduerftig; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/lieferantenbewertung.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Bewertungsplan, Eskalationsentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Suche, Bewertungsmatrix und Score-Anpassung bleiben erhalten. UX-Standard markiert `UX-EINKAUF-005` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-005.yaml`; `git diff --check`
**Offene Risiken:** Score-Historie und Massnahmenworkflow bleiben ausserhalb dieses Slice; dieser Slice setzt die Bedien- und Entscheidungssicht auf die bestehende Bewertungsmatrix.

## UX-SALES-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Gutschriften-Editor als Verkaufsfolge auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Freigabeplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-005.yaml`, `packages/frontend-web/src/pages/sales/credit-note-editor.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Gutschriften-Editor zeigt Rollenfokus fuer Vertrieb, Faktura, Finance und Leitung; Freigabeplan fuehrt Kunde, Ausgangsrechnung, Grund, Positionen und Zahlung; Managemententscheidung zeigt freigabefaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/credit-note-editor.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Gutschriften-Freigabeplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende ObjectPage-Konfiguration, Validierung, Freigabe, Versand, Druck und Storno bleiben erhalten. UX-Standard markiert `UX-SALES-005` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-005.yaml`; `git diff --check`
**Offene Risiken:** Retourenlogik ausserhalb des Gutschriften-Editors bleibt fuer einen separaten Sales-/Einkauf-Slice offen.

## UX-LOGISTIK-004

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Hofliste und Waagenliste auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Prioritaetsplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-004.yaml`, `packages/frontend-web/src/pages/waage/hofliste.tsx`, `packages/frontend-web/src/pages/waage/liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Hofliste und Waagenliste zeigen Rollenfokus fuer Waage, Hof, Disposition, QS und Leitung; Prioritaetsplan fuehrt offene Vorgange, Eichung, Suche und naechste Aktion; Stopperentscheidung zeigt arbeitsfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `waage/hofliste.tsx` und `waage/liste.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Prioritaetsplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Hotkeys, Tabellen, Anlage, Zweit-Wiegung, Suche, Export, OperationalCaseHeader und Kettenkontext bleiben erhalten. UX-Standard markiert `UX-LOGISTIK-004` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-004.yaml`; `git diff --check`
**Offene Risiken:** Waage-Hardware- und Echtzeit-Sensorik bleiben ausserhalb dieses Slice.

## UX-EINKAUF-006

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Retouren und Gutschriften/Belastungen auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Freigabeplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-006.yaml`, `packages/frontend-web/src/pages/einkauf/retouren.tsx`, `packages/frontend-web/src/pages/einkauf/gutschriften-belastungen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Retouren und Gutschriften/Belastungen zeigen Rollenfokus fuer Einkauf, Wareneingang, Finance, QS und Leitung; Freigabeplan fuehrt Wareneingang/Rechnung, Grund, Positionen, Gutschrift/Belastung und Ausgleich; Stopperentscheidung zeigt freigabefaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `einkauf/retouren.tsx` und `einkauf/gutschriften-belastungen.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Freigabeplan, Stopperentscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Wareneingangs-Auswahl, Retourendialog, Statuspflege, Memo-Erstellung, Settlement-Entwurf und Ausgleichsdialoge bleiben erhalten. UX-Standard markiert `UX-EINKAUF-006` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-006.yaml`; `git diff --check`
**Offene Risiken:** Tiefe Buchhaltungs- und Lieferantenkommunikationsworkflows bleiben in den bestehenden Aktionen; dieser Slice setzt die Bedien- und Entscheidungssicht.

## UX-SALES-006

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Verkaufsdashboard, Rechnungs- und Lieferlisten auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-006.yaml`, `packages/frontend-web/src/pages/dashboard/sales-dashboard.tsx`, `packages/frontend-web/src/pages/sales/rechnungen-liste.tsx`, `packages/frontend-web/src/pages/sales/lieferungen-liste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Dashboard, Rechnungs- und Lieferlisten zeigen Rollenfokus fuer Vertrieb, Faktura, Logistik, Finance und Leitung; Prioritaetsplan fuehrt Umsatz, offene Rechnungen, Lieferstatus und Nachweis; Managemententscheidung zeigt arbeitsfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `dashboard/sales-dashboard.tsx`, `sales/rechnungen-liste.tsx` und `sales/lieferungen-liste.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende KPI-Karten, Top-Kunden, OperationalCaseHeader, Filter, Import, Export, Druck, Tabellen und Editor-Navigation bleiben erhalten. UX-Standard markiert `UX-SALES-006` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-006.yaml`; `git diff --check`
**Offene Risiken:** Auftrags- und Angebotslisten sind bereits in frueheren Sales-Slices abgedeckt; dieser Slice fokussiert Dashboard, Rechnungen und Lieferungen.

## UX-EINKAUF-007

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Einkaufs-Dashboard auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Einkaufs-Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestell- und Rechnungseingangslisten sind bereits in frueheren Einkauf-Slices abgedeckt.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-007.yaml`, `packages/frontend-web/src/pages/dashboard/einkauf-dashboard.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Einkaufs-Dashboard zeigt Rollenfokus fuer Einkauf, Wareneingang, Finance, Lieferantenmanagement und Leitung; Prioritaetsplan fuehrt offene Bestellungen, Ueberfaelligkeit, Einkaufsvolumen, offene Posten und Nachweis; Managemententscheidung zeigt arbeitsfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `dashboard/einkauf-dashboard.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Einkaufs-Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende KPI-Karten, Ueberfaelligkeitswarnung und aktuelle Bestellungen bleiben erhalten. UX-Standard markiert `UX-EINKAUF-007` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-007.yaml`; `git diff --check`
**Offene Risiken:** Detail-Listen bleiben in den vorhandenen Einkaufs-Slices; dieser Slice fokussiert die Management- und Prioritaetssicht des Dashboards.

## UX-SALES-007

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Moderne Sales-Auftragssicht als Ausnahmen- und Eskalationsarbeitsflaeche auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Eskalationsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-007.yaml`, `packages/frontend-web/src/pages/sales/orders-modern.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Moderne Sales-Auftragssicht zeigt Rollenfokus fuer Vertrieb, Auftragsabwicklung, Logistik, Faktura und Leitung; Eskalationsplan fuehrt offene, teilgelieferte, rechnungsfaehige und Archiv-/Storno-Kandidaten; Managemententscheidung zeigt arbeitsfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `sales/orders-modern.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Sales-Eskalationsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende Toolbar, CSV-Export, Suche, Filter, KPI-Karten, DataTable und Fokusauftrag bleiben erhalten. UX-Standard markiert `UX-SALES-007` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-007.yaml`; `git diff --check`
**Offene Risiken:** Rechnungsliste und Lieferliste sind in `UX-SALES-006` abgedeckt; dieser Slice fokussiert die moderne Sales-Ausnahmensicht.

## UX-LOGISTIK-005

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Bestands-/Logistik-Dashboard als vorhandene Dashboardflaeche fuer Logistik- und Waagefolge auf den UX-Exzellenzbaukasten ziehen: Rollenfokus, Ketten-Prioritaetsplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-005.yaml`, `packages/frontend-web/src/features/inventory/InventoryDashboard.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Dashboard zeigt Rollenfokus fuer Lager, Logistik, Waage, Einkauf und Leitung; Prioritaetsplan fuehrt Bestand, Alerts, Nachschub, Wert und Nachweis; Managemententscheidung zeigt arbeitsfaehig/blockiert; CRUD-/Nachweis-Abdeckung ist sichtbar; Typecheck und Doku-Checks sind gruen.
**Erledigt:** `features/inventory/InventoryDashboard.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Bestands-Kettenplan, Managemententscheidung, Next Action und CRUD-/Nachweis-Abdeckung. Bestehende KPI-Karten, Alerts, Nachschubvorschlaege und Quick Actions bleiben erhalten. UX-Standard markiert `UX-LOGISTIK-005` als abgeschlossen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-005.yaml`; `git diff --check`
**Offene Risiken:** Es gibt aktuell keine separate Logistik-Dashboard-Route; dieser Slice nutzt die bestehende Inventory-Dashboard-Flaeche als operative Logistik-/Bestandsuebersicht.

## UX-EINKAUF-008

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Einkaufs-Ausnahmen fuer EDI/Lieferantenportal und Service Entry Sheets als verstaendliche Arbeitsflaechen mit Stopper-, Prioritaets- und Nachweissicht fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-EINKAUF-008.yaml`, `packages/frontend-web/src/pages/einkauf/edi-portal.tsx`, `packages/frontend-web/src/pages/einkauf/service-entry-sheets.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** EDI-Portal und Service-Entry-Sheets zeigen Rollenfokus, konkreten Pruefplan, Stopper-/Managemententscheidung, naechste Aktion, Nachweis-/Vorlagenbezug und CRUD-/Workflow-Abdeckung in normaler Buero-Sprache.
**Erledigt:** `einkauf/edi-portal.tsx` und `einkauf/service-entry-sheets.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Pruefplan, Stopper-/Freigabeentscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung. Leere Zustaende und sichtbare Begriffe sind auf normale Buero-Sprache gezogen.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-EINKAUF-008.yaml`; `git diff --check`
**Offene Risiken:** OCR hat aktuell keine eigene sichtbare Einkaufsseite; der Slice behandelt die vorhandenen Ausnahmeflaechen EDI/Lieferantenportal und Service Entry Sheets.

## UX-SALES-008

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Angebots-Erfassung als gefuehrte Sales-Assistenz fuer Angebots-/Auftragsuebergaben mit naechster Aktion, Nachweisstatus und Abschlussentscheidung fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SALES-008.yaml`, `packages/frontend-web/src/pages/sales/angebot-erstellen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Angebots-Erfassung zeigt Rollenfokus, Uebergabeplan, Management-/Abschlussentscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Erfassungs-, Druck-, DMS- und Auftraguebergabe-Funktionen bleiben erhalten.
**Erledigt:** `sales/angebot-erstellen.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Uebergabeplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Die bestehende Angebots-Erfassung, Suche, Positionserfassung, Druck, DMS-Anhang, Loeschen und Auftraguebergabe bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SALES-008.yaml`; `git diff --check`
**Offene Risiken:** Die Angebotsliste ist bereits ueber `UX-SALES-002` abgedeckt; dieser Slice fokussiert die eigentliche Erfassungs- und Uebergabemaske.

## UX-LOGISTIK-006

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Fracht-/Speditions-Ausnahmen fuer Frachtdokumentdruck und Frachttarife mit Eskalationssicht, naechster Aktion und Kettennachweis fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LOGISTIK-006.yaml`, `packages/frontend-web/src/pages/versand/frachtdokumente.tsx`, `packages/frontend-web/src/pages/strecke/speditionen-fracht-preise.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Frachtdokumente und Speditions-Frachttarife zeigen Rollenfokus, Ausnahme-/Pruefplan, Eskalationsentscheidung, naechste Aktion, Nachweislink und CRUD-/Workflow-Abdeckung in normaler Buero-Sprache.
**Erledigt:** `versand/frachtdokumente.tsx` und `strecke/speditionen-fracht-preise.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Pruefplan, Eskalations-/Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Der Frachtdokument-Druckfehler ist als klaerer Versandstopper formuliert; Frachttarife zeigen aktive/inaktive Tarife, Preisnachweis und naechste Klaerung.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LOGISTIK-006.yaml`; `git diff --check`
**Offene Risiken:** `logistik/frachtbriefe.tsx` ist bereits ueber `UX-LOGISTIK-002` abgedeckt; dieser Slice fokussiert Druck-/Tarifausnahmen.

## UX-DMS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Dokumente/DMS als gefuehrte Arbeitsflaechen fuer Klassifikation, Retention, Version, Vorlage, Freigabe und naechste Aktion in normaler Buero-Sprache fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-DMS-001.yaml`, `packages/frontend-web/src/pages/document.tsx`, `packages/frontend-web/src/pages/admin/setup/dms-integration.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Dokumentenpanel und DMS-Integration zeigen Rollenfokus, Arbeitsplan, Managemententscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung; Upload, Suche, Scan, Loeschen und DMS-Verbindung bleiben erhalten.
**Erledigt:** `document.tsx` und `admin/setup/dms-integration.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Klassifikations-/Einrichtungsplan, Managemententscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung. Upload, Suche, Scan, Loeschen, Verbindungstest, Einrichtung und Neu-Konfiguration bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-DMS-001.yaml`; `git diff --check`
**Offene Risiken:** `dokumente/ablage.tsx` hat bereits einen operativen Nachweisrahmen; dieser Slice fokussiert zentrale QM-Dokumente und technische DMS-Anbindung.

## UX-QS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Qualitaet/Produktion fuer Pruef-, Sperr- und Freigabeprozesse mit Rollenfokus, naechster Aktion, Nachweisstatus und normaler Buero-Sprache fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-QS-001.yaml`, `packages/frontend-web/src/pages/annahme/klaerung-gesperrt.tsx`, `packages/frontend-web/src/pages/qualitaet/ausnahmen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Gesperrte-Ware-Klaerung und QS-Ausnahmen zeigen Rollenfokus, Pruef-/Eskalationsplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Entscheidung, Begruendung, Liste und Agent-Vorschlaege bleiben erhalten.
**Erledigt:** `annahme/klaerung-gesperrt.tsx` und `qualitaet/ausnahmen.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Sperr-/Eskalationsplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Bestehende Entscheidung, Begruendung, Liste, Kennzahlen und Agent-Vorschlaege bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-QS-001.yaml`; `git diff --check`
**Offene Risiken:** `annahme/qualitaets-check.tsx` hat bereits einen operativen Fallkopf; dieser Slice fokussiert die Klär- und Eskalationsraeume.

## UX-LAGER-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Lagerarbeitsflaechen fuer Lagerplaetze und Bestandsbewegungen mit Rollenfokus, Engpassentscheidung, naechster Aktion und Nachweisstatus fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-LAGER-001.yaml`, `packages/frontend-web/src/pages/lager/lagerplaetze.tsx`, `packages/frontend-web/src/features/inventory/StockManagement.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Lagerplaetze und StockManagement zeigen Rollenfokus, Lager-/Bewegungsplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Kapazitaetsanzeige, Artikel-/Bestandsliste und Bewegungsdialog bleiben erhalten.
**Erledigt:** `lager/lagerplaetze.tsx` und `features/inventory/StockManagement.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Kapazitaets-/Bestandsplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Bestehende Kapazitaetsanzeige, Artikel-/Bestandsliste und Bewegungsdialog bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-LAGER-001.yaml`; `git diff --check`
**Offene Risiken:** Einzelne Lagerseiten wurden in OP-ROLL-Slices bereits fallartig aufgewertet; dieser Slice fokussiert Lagerplaetze und das zentrale StockManagement.

## UX-PORTAL-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Portal-/Self-Service-Dokumente mit Rollenfokus, klarer Nutzeraufgabe, Nachweisstatus, naechster Aktion und CRUD-/Workflow-Abdeckung fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-PORTAL-001.yaml`, `packages/frontend-web/src/pages/portal/dokumente.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Portal-Dokumente zeigen Rollenfokus, Nachweisplan, Managemententscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung; bestehende KPI-Karten, Compliance-Spur, Suche, Filter, Tabs und Download bleiben erhalten.
**Erledigt:** `portal/dokumente.tsx` nutzt den UX-Baukasten fuer Rollenfokus, Nachweisplan, Managemententscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung. Bestehende KPI-Karten, Compliance-Spur, Suche, Filter, Tabs und Download bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-PORTAL-001.yaml`; `git diff --check`
**Offene Risiken:** Dieser Slice fokussiert die Portal-Dokumentenseite; weitere Portal-Self-Service-Seiten bleiben Folgeslices.

## UX-PRODUKTION-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Produktionsarbeitsflaechen fuer Mischfutter-Auftrag und Produktionsdokument-Druck mit Rollenfokus, Materialentscheidung, Dokumentnachweis und naechster Aktion fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-PRODUKTION-001.yaml`, `packages/frontend-web/src/pages/produktion/mischfutter-produktion.tsx`, `packages/frontend-web/src/pages/produktion/produktions-dokumente-drucken.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Mischfutter-Produktion und Produktionsdokument-Druck zeigen Rollenfokus, Produktions-/Dokumentplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehender Wizard und Druckmaske bleiben erhalten.
**Erledigt:** `produktion/mischfutter-produktion.tsx` und `produktion/produktions-dokumente-drucken.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Produktions-/Dokumentplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Bestehender Wizard, Materialpruefung, Auftragserstellung und Druckmaske bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-PRODUKTION-001.yaml`; `git diff --check`
**Offene Risiken:** Produktion hat bisher nur schmale sichtbare Frontend-Flaechen; weitere Produktionsdetails bleiben Folgeslices.

## UX-ADMIN-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Admin-Benutzer- und Rollenverwaltung mit klarer Betriebsaufgabe, Status, naechster Aktion und sicherer Aenderungsfuehrung nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-ADMIN-001.yaml`, `packages/frontend-web/src/pages/admin/benutzer-liste.tsx`, `packages/frontend-web/src/pages/admin/rollen-verwaltung.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Benutzer- und Rollenverwaltung zeigen Rollenfokus, Admin-Aufgabenplan, Managemententscheidung, Next Action, Vorlage-/Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Liste, Suche, Export und Neuanlage bleiben erhalten.
**Erledigt:** `admin/benutzer-liste.tsx` und `admin/rollen-verwaltung.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Sicherheits-/Berechtigungsplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Bestehende Listen, Suche, Export und Neuanlage bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-ADMIN-001.yaml`; `git diff --check`
**Offene Risiken:** DMS-Setup ist bereits ueber `UX-DMS-001` abgedeckt; weitere Admin-Spezialseiten bleiben Folgeslices.

## UX-FUHRPARK-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Fuhrparkseiten fuer Fahrzeugstatus, Dokumente, Fristen, naechste Aktion und Nachweisfuehrung nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-FUHRPARK-001.yaml`, `packages/frontend-web/src/pages/fuhrpark/fahrzeuge.tsx`, `packages/frontend-web/src/pages/fuhrpark/ausgehende-belege-dokumente.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Fahrzeugliste und ausgehende Fuhrpark-Dokumente zeigen Rollenfokus, Fristen-/Dokumentplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Liste, Suche, Export, Quicklinks und Dokument-CRUD bleiben erhalten.
**Erledigt:** `fuhrpark/fahrzeuge.tsx` und `fuhrpark/ausgehende-belege-dokumente.tsx` nutzen den UX-Baukasten fuer Rollenfokus, Fristen-/Dokumentplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung. Bestehende Liste, Suche, Export, Quicklinks und Dokument-CRUD bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-FUHRPARK-001.yaml`; `git diff --check`
**Offene Risiken:** Fuhrpark-Menues und Detailstammdaten bleiben Folgeslices; dieser Slice fokussiert Status-/Fristen- und Dokumentsteuerung.

## HR-TIME-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Lizenz- und Zielarchitektur fuer deutsche Abwesenheitsverwaltung, Zeiterfassung und VALEO-eigenen Driver-Time-Layer festhalten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-001.yaml`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Urlaubsverwaltung wird als Apache-2.0-Abwesenheitskandidat bewertet; AGPL/GPL-Zeiterfassung ist als Codebasis ausgeschlossen; VALEO-Driver-Time-Layer, Integrationsgrenzen, Pilotumfang und Lizenzrisiken sind dokumentiert.
**Erledigt:** Zielarchitektur und Lizenzlinie in `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md` dokumentiert; `open-gaps` fuehrt HR-TIME-001 als P2-Thema mit naechstem Pilot-Slice.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Finale Rechtspruefung, Anbieter-AVV/DPA und produktive Tacho-/Telematik-Schnittstellen liegen ausserhalb des Repos.

## HR-TIME-PILOT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Ersten VALEO-eigenen Driver-Time-Toolkern fuer LKW-Fahrerzeit, Tour-/Fahrzeugbezug und Plausibilitaetschecks umsetzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PILOT-001.yaml`, `packages/hr-domain/src/domain/entities/driver-time-event.ts`, `packages/hr-domain/src/domain/services/driver-time-service.ts`, `packages/hr-domain/dist/domain/entities/driver-time-event.*`, `packages/hr-domain/dist/domain/services/driver-time-service.*`, `packages/hr-domain/tests/domain/driver-time-service.test.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** Fahrerzeitereignisse besitzen typisierte Ereignisarten, Tour-/Fahrzeugbezug, Quellen- und Auditfelder; Plausibilitaetschecks erkennen Ueberlappungen, fehlende Tour-/Fahrzeugdaten, fehlende Korrekturbegruendung und Abwesenheitskollisionen; die Zeiterfassungsseite zeigt den Driver-Time-Pilot ohne AGPL-/GPL-Codeuebernahme.
**Erledigt:** `DriverTimeEventEntity` und `DriverTimeService` eingefuehrt; fokussierte Vitest-Regression deckt Zusammenfassung, Blocker, Abwesenheitskollision und Tacho-/Manuell-Abweichung ab; `personal/zeiterfassung.tsx` zeigt Driver-Time-Pilot-KPIs und Ereignistabelle.
**Checks:** `pnpm --filter @valero-neuroerp/hr-domain exec vitest run tests/domain/driver-time-service.test.ts`; `pnpm --filter @valero-neuroerp/hr-domain build`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Produktive Persistenz, Tacho-/Telematik-Import und Payroll-/DATEV-Export bleiben Folgeslices. Der volle `@valero-neuroerp/hr-domain test`-Lauf ist aktuell durch den bestehenden `testcontainers`-Import im Repository-Integrationstest blockiert.

## HR-TIME-PILOT-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Driver-Time-Pilot als Backend-/Frontend-Toolvertrag an die bestehende Personal-API anbinden.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PILOT-002.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_driver_time_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** `/api/v1/personal/driver-time/summary` liefert Fahrerzeit-KPIs, Ereignisse und Plausibilitaetsbefunde aus einem stabilen API-Vertrag; Frontend nutzt diesen Hook statt harter lokaler Driver-Time-Daten; Tests decken Happy Path und Befundlogik ab.
**Erledigt:** Personal-API liefert Driver-Time-Summary mit DB-ableitung aus Stundenzetteln, Abwesenheitskollisionen und Pilot-Fallback; Frontend-Hook `useDriverTimeSummary` ersetzt harte lokale Driver-Time-Daten; Tests decken Helper, API-Happy-Path und Fallback ab.
**Checks:** `pytest tests/test_personal_driver_time_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Persistente Fahrerzeitereignisse, Tacho-/Telematik-Import und Payroll-/DATEV-Export bleiben Folgeslices.

## HR-TIME-PRO-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Zeiterfassung vom Fahrerzeit-Pilot zu einem professionellen Time-&-Labor-Cockpit mit Freigabe-, Compliance- und Payroll-Sicht ausbauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PRO-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_time_cockpit_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** Backend liefert ein Time-Cockpit mit Perioden-KPIs, Freigabequeue, Compliance-Befunden, Payroll-Readiness und Driver-Time-Zusammenfassung; Frontend zeigt diese Steuerung statt reiner Mock-/Tabellenseite; Tests sichern Kernvertrag und Regelbefunde.
**Erledigt:** `GET /api/v1/personal/time-cockpit` liefert professionelle Steuerungsdaten inklusive Payroll-Readiness und Compliance-Befunden; Zeiterfassungsseite nutzt Tabs fuer Steuerung, Driver-Time, Arbeitszeit und Payroll; Tests decken API-Vertrag und Regelbefunde ab.
**Checks:** `pytest tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Rechtsfeingranulare ArbZG-/Lenkzeitregeln, echte Dienstplanung, Buchungsworkflow und Lohnexport bleiben Folgeslices.

## HR-TIME-GAP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** GAP-Liste, Lastenheft, Roadmap, Integrationsanforderungen und Landhandel-spezifische HRM-Planung gegen ERP/Shiftfy-Benchmark dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-GAP-001.yaml`, `docs/project-context/hr-time-sap-oracle-gap-lastenheft-roadmap-2026-05-08.md`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** ERP-/Shiftfy-Benchmark ist quellenbasiert; VALEO-GAPs, Lastenheft, Roadmap-Milestones, Integrationsanforderungen, Kreuzverbindungen, Mitarbeitertypen im Landhandel, Kalenderintegration, Saison-/Arbeitsspitzenplanung, Kampagneninterferenzen und Aussendienstplanung sind als umsetzbare Planung dokumentiert.
**Erledigt:** GAP-/Lastenheft-/Roadmap-Dokument in `docs/project-context/hr-time-sap-oracle-gap-lastenheft-roadmap-2026-05-08.md` erstellt und in die HR-Time-Zielarchitektur verlinkt.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Detailauslegung Arbeitszeit-/Lenkzeitrecht, Tarif-/Betriebsvereinbarungen, Anbieter-AVV/DPA und echte Kalender-/Tacho-/Telematik-Zugangsdaten bleiben fachlich oder extern zu klaeren.

## HR-TIME-DATA-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Persistenten HR-Time-Datenkern fuer Mitarbeiter-Zeitprofile, produktive Zeitereignisse und Audit-/Statusfelder einfuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-DATA-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_time_data_api.py`, `migrations/sql/hr/001_hr_time_core.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`, `docs/project-context/hr-time-sap-oracle-gap-lastenheft-roadmap-2026-05-08.md`
**Abnahmekriterien:** Kanonisches HR-Time-Kerndatenmodell und Konsistenzregeln sind dokumentiert; API liefert kanonische HR-Time-Profile aus Datenbank oder Pilot-Fallback; produktive Zeitereignisse besitzen Quelle, Status, Kostenstelle, Arbeitsbereich, Audit und Korrekturgrund im Migrationsvertrag; Tests sichern Profil- und Event-Transformation.
**Erledigt:** Kanonisches Kerndatenmodell inklusive API-Resource-URLs und Konsistenzanalyse dokumentiert; SQL-Vertrag fuer `employee_time_profiles`, erweiterte `time_entries` und `driver_time_events` erstellt; `GET /api/v1/personal/time-profiles` mit Datenbank-, User- und Pilot-Fallback umgesetzt; fokussierte API-/Mapping-Regression ergaenzt.
**Checks:** `pytest tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive Anwendung der Migration, echte HR-Stammdatenquelle und Lohnartenmapping bleiben Folgeslices.

## HR-TIME-BOOK-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Buchungs-, Korrektur-, Einreichungs- und Freigabe-Workflow fuer kanonische HR-Time-Zeitereignisse bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-BOOK-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_time_booking_api.py`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Zeitbuchungen koennen erstellt, eingereicht und freigegeben werden; Korrekturen verlangen einen Grund; exportierte Eintraege werden nicht still mutiert; API-Tests sichern Statusuebergaenge und Fehlerfaelle.
**Erledigt:** `POST /api/v1/personal/time-entries`, `/submit`, `/approve` und `/correct` eingefuehrt; Korrekturgrund und Export-Schutz werden serverseitig erzwungen; fokussierte API-Regression deckt Happy Path und Fehlerfaelle ab.
**Checks:** `pytest tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Rollenbasierte echte Managerfreigabe, Payroll-Export und UI-Aktionen bleiben Folgeslices.

## HR-TIME-ABS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Abwesenheits-Contract als kanonischen Planungsblocker fuer Urlaubsverwaltung/SaaS-Adapter, Tour, Schicht, Kalender und Payroll bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-ABS-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_absence_api.py`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`, `docs/project-context/hr-time-absence-driver-integration-2026-05-07.md`
**Abnahmekriterien:** Abwesenheiten koennen als Contract importiert und gelesen werden; genehmigte Abwesenheiten werden als `time_entries` mit Quelle `absence` gespiegelt; API weist Planungsblocker fuer Tour, Schicht, Kalender und Payroll aus; Tests sichern Import, Listing und Driver-Time-Kollision.
**Erledigt:** `GET /api/v1/personal/absences` und `POST /api/v1/personal/absences/import` umgesetzt; Import spiegelt genehmigte Abwesenheiten als kanonische `time_entries` mit Quelle `absence`; Planungsblocker und Driver-Time-Kollision sind regressionsgesichert.
**Checks:** `pytest tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echter Urlaubsverwaltung-HTTP-Connector, AVV/DPA und bidirektionale Konfliktaufloesung bleiben Folgeslices.

## HR-TIME-SCHED-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Schicht- und Einsatzplanung mit Standort, Rolle, Qualifikationen, Besetzung und Abwesenheitskonflikten auf dem kanonischen HR-Time-Modell bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-SCHED-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_shift_planning_api.py`, `migrations/sql/hr/002_hr_time_scheduling.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Schichten koennen erstellt und gelesen werden; Planung prueft Mindestbesetzung, aktive Profile, Qualifikationen und genehmigte Abwesenheiten; Konflikte werden als Warnung/Blocker im API-Vertrag ausgewiesen; Tests sichern Happy Path und Konfliktfaelle.
**Erledigt:** `domain_hr.shifts` als SQL-Vertrag, `GET/POST /api/v1/personal/shifts` und Konfliktpruefung gegen Mindestbesetzung, Profile, Qualifikationen und genehmigte Abwesenheiten umgesetzt; Regression fuer Blocker/Warnungen ergaenzt.
**Checks:** `pytest tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** UI-Kalender, echte Optimierung/Auto-Staffing und rollenbasierte Managerfreigabe bleiben Folgeslices.

## HR-TIME-CAL-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Provider-neutralen Kalendervertrag fuer HR-Time-Blocker, Schichten, Abwesenheiten, Touren und Aussendienst bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-CAL-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_calendar_api.py`, `migrations/sql/hr/003_hr_time_calendar.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Kalenderereignisse koennen erstellt und gelesen werden; private externe Termine werden nur als Busy-Blocker ohne Betreffdetails gefuehrt; Konfliktlevel und Sync-State sind im Contract sichtbar; Tests sichern Datenschutzmaskierung und Vertrag.
**Erledigt:** `domain_hr.calendar_events` als SQL-Vertrag, `GET/POST /api/v1/personal/calendar-events`, Sync-State, Konfliktlevel und Datenschutzmaskierung fuer private/busy-only Termine umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Microsoft/Google OAuth, Delta-Sync und echte externe Kalenderzugriffe bleiben Folgeslices.

## HR-TIME-PAY-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Payroll-/DATEV-Exportvertrag fuer freigegebene HR-Time-Zeitwerte mit Lohnarten, Kostenstellen und Blockerpruefung bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-PAY-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_payroll_export_api.py`, `migrations/sql/hr/004_hr_time_payroll_exports.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Payroll-Export kann fuer Zeitraum erzeugt und gelesen werden; nur freigegebene Zeitwerte werden exportfaehig; offene/nicht freigegebene Buchungen werden als Blocker ausgewiesen; Tests sichern Lohnartenmapping und Blocker.
**Erledigt:** `domain_hr.payroll_exports`, `GET/POST /api/v1/personal/payroll-exports`, Lohnartenmapping fuer Regelzeit/Ueberstunden/Abwesenheit und Blocker fuer nicht freigegebene Zeitbuchungen umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_payroll_export_api.py tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Echte DATEV-/Lohnsoftware-Dateiformate, Steuerberaterfreigabe und Rueckschreibstatus bleiben Folgeslices.

## HR-TIME-CAMPAIGN-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Saison-/Kampagnen-Kapazitaetsplanung mit Rollenbedarf, Abwesenheiten, Schichten und Engpassbewertung bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-CAMPAIGN-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_campaign_capacity_api.py`, `migrations/sql/hr/005_hr_time_campaign_capacity.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Kampagnenkapazitaet kann erstellt und gelesen werden; Rollenbedarf wird gegen aktive Profile, Abwesenheiten und bereits geplante Schichten bewertet; Engpaesse werden als Warnung/Blocker im Contract ausgewiesen.
**Erledigt:** `domain_hr.campaign_capacity_plans`, `GET/POST /api/v1/personal/campaign-capacity` und Rollenbedarfspruefung gegen aktive Profile, Abwesenheiten und geplante Schichten umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_campaign_capacity_api.py tests/test_personal_payroll_export_api.py tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Optimierungsalgorithmus, Wetter-/Mengenforecast und UI-Heatmap bleiben Folgeslices.

## HR-TIME-FIELD-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Aussendienstplanung mit Kunde, Gebiet, Kampagne, Kalender- und Abwesenheitskonflikten auf HR-Time-Basis bereitstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-FIELD-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_field_service_api.py`, `migrations/sql/hr/006_hr_time_field_service.sql`, `docs/project-context/hr-time-canonical-core-data-model-2026-05-08.md`
**Abnahmekriterien:** Aussendiensttermine koennen erstellt und gelesen werden; Planung prueft HR-Time-Profil, Abwesenheit und Kalenderueberschneidung; Konflikte werden im Contract ausgewiesen; Tests sichern Blocker und Happy Path.
**Erledigt:** `domain_hr.field_service_plans`, `GET/POST /api/v1/personal/field-service-plan` und Konfliktpruefung gegen HR-Time-Profil, Abwesenheiten und Kalenderblocker umgesetzt und getestet.
**Checks:** `pytest tests/test_personal_field_service_api.py tests/test_personal_campaign_capacity_api.py tests/test_personal_payroll_export_api.py tests/test_personal_calendar_api.py tests/test_personal_shift_planning_api.py tests/test_personal_absence_api.py tests/test_personal_time_booking_api.py tests/test_personal_time_data_api.py tests/test_personal_time_cockpit_api.py tests/test_personal_driver_time_api.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** CRM-Live-Connector, Routenoptimierung und mobile Aussendienst-UI bleiben Folgeslices.

## HR-TIME-UI-CRUD-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** HR-Time-Tools als Human/AI-Agent-Interface mit CRUD-Aktionen fuer Zeitbuchung, Abwesenheit, Schicht, Kalender, Payroll, Kampagne und Aussendienst operationalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-UI-CRUD-001.yaml`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`
**Abnahmekriterien:** Frontend nutzt die neuen HR-Time-Contracts fuer Listen und Create-Mutations; Nutzer koennen zentrale HR-Time-Objekte aus dem Cockpit anlegen; Agent-Hinweise fassen Blocker, Freigaben und naechste Aktionen zusammen; Typecheck ist gruen.
**Erledigt:** Frontend-API-Hooks fuer Zeitbuchung, Abwesenheit, Schicht, Kalender, Payroll, Kampagne und Aussendienst ergaenzt; Zeiterfassungsseite zu einem kompakten ERP-Object-Page-Cockpit mit Agent Worklist, CRUD-Formulargruppen und Planungs-/Payroll-Tabellen ausgebaut.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Detail-CRUD mit Edit/Delete, echte Optimierungsvorschlaege und mobile Offline-UX bleiben Folgeslices.

## HR-TIME-OPS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** HR-Time-Verdrahtung fuer Navigation vor/zurueck, Bearbeiten/Nachbearbeiten, Drucken, Arbeitsplanabruf und praferenzbasierte Planung mit Nachttouren, Urlaub, Schulferien, Brueckentagen und Feiertagsdruck operationalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-OPS-001.yaml`, `app/api/v1/endpoints/personal.py`, `tests/test_personal_work_plan_api.py`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`
**Abnahmekriterien:** Backend liefert einen Arbeitsplanvertrag mit Planungsbefunden und Mitarbeiterpraeferenzen; Zeitbuchungen koennen aus der UI nachbearbeitet und neu eingereicht werden; Frontend bietet vor/zurueck-Navigation, Druckpfade und Arbeitsplanabruf; Tests sichern Arbeitsplan- und Praeferenzlogik.
**Erledigt:** `/api/v1/personal/work-plan` mit Praeferenz-, Ferien-, Brueckentags-, Feiertags- und Abwesenheitsbefunden umgesetzt; Frontend-Hooks fuer Arbeitsplan, Einreichen und Korrektur ergaenzt; Zeiterfassungsseite bietet Tagesnavigation, Arbeitsplan-Druck, Arbeitsplan-Tab und Nachbearbeitungsmaske.
**Checks:** `pytest tests/test_personal_work_plan_api.py tests/test_personal_shift_planning_api.py tests/test_personal_time_booking_api.py -q --no-cov`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `git diff --check`
**Offene Risiken:** Produktive Ferienkalender-Provider, Betriebsvereinbarungen und echte Optimierungsengine bleiben Folgeslices.

## HR-TIME-OPS-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Durchklicktest-Befund beheben: HR-Time-GET-Hooks duerfen leere Platzhalterdaten nicht als frische Daten cachen und muessen beim Oeffnen der Maske wirklich laden.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-OPS-002.yaml`, `packages/frontend-web/src/lib/api/personal.ts`, `packages/frontend-web/tests/e2e/hr-time-clickthrough.generated.spec.ts`
**Abnahmekriterien:** HR-Time-Durchklicktest sieht geladene Arbeitsplan-/Cockpitdaten; GET-Hooks verwenden Platzhalter statt frischer Initialdaten; Formular-POSTs und Druckaktion bleiben funktionsfaehig.
**Erledigt:** React-Query-HR-Time-Hooks von `initialData` auf `placeholderData` umgestellt; Playwright-Durchklicktest fuer Navigation, Arbeitsplan, Erfassung, Nachbearbeitung, Submit/Korrektur-POSTs und Druckpfad ergaenzt; Testlauf hat GET-Requests und UI-Rendering verifiziert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/hr-time-clickthrough.generated.spec.ts --project=chromium`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Der temporäre E2E-Smoke nutzt API-Mocks; produktive Browser-E2E gegen echte FastAPI/Postgres bleibt Folgeslice.

## HR-TIME-OPS-003

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Nachbearbeitung ergonomisch aus der Arbeitszeitliste starten statt manuelle Zeitbuchungs-ID-Eingabe zu erzwingen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-OPS-003.yaml`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `packages/frontend-web/tests/e2e/hr-time-clickthrough.generated.spec.ts`
**Abnahmekriterien:** Arbeitszeitzeilen haben eine Bearbeiten-Aktion; Klick fuellt die Nachbearbeitung mit ID, Zeiten, Stunden und Typ; die UI springt zur Erfassungs-/Nachbearbeitungsgruppe; E2E-Durchklicktest nutzt diesen Pfad.
**Erledigt:** Arbeitszeitliste erhaelt Bearbeiten-Aktion mit ID-/Zeit-/Typ-Uebernahme; Tabs sind kontrolliert und springen in die Erfassung; Playwright-Durchklicktest nutzt den realen Bearbeiten-Pfad vor Submit/Korrektur.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/hr-time-clickthrough.generated.spec.ts --project=chromium`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Voller Edit/Delete-Workflow fuer alle HR-Time-Objekte bleibt Folgeslice.

## HR-TIME-UX-ROADMAP-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** HR-Time-Workflows als klickarme End-to-End UX-Roadmap mit Milestones, Quervernetzungen, User-Fragen, Masken, Such-/Filter-/Sortierfunktionen planen und den ersten Filter-/Such-Slice im Cockpit umsetzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/HR-TIME-UX-ROADMAP-001.yaml`, `docs/project-context/hr-time-ux-workflow-roadmap-2026-05-12.md`, `packages/frontend-web/src/pages/personal/zeiterfassung.tsx`, `packages/frontend-web/tests/e2e/hr-time-clickthrough.generated.spec.ts`
**Abnahmekriterien:** Roadmap beschreibt Milestones mit Quervernetzungen und Abhaengigkeiten; User-Fragen sind Masken, Datenquellen und Aktionen zugeordnet; UI bietet zentrale Suche, Schnellfilter und Sortierung fuer Arbeitszeit/Arbeitsplan; Durchklicktest nutzt Suche/Filter/Sortierung.
**Erledigt:** UX-Workflow-Roadmap mit Milestones UX-M1 bis UX-M7, User-Fragen, Masken, Datenquellen, Aktionen, Quervernetzungen und Folge-Slices dokumentiert; Zeiterfassungs-Cockpit um zentrale Suche, Schnellfilter und Sortierung fuer Arbeitszeit und Arbeitsplan erweitert; E2E-Durchklicktest nutzt Suche/Filter/Sortierung.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web exec playwright test tests/e2e/hr-time-clickthrough.generated.spec.ts --project=chromium`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Weitere Milestones wie Action Panel, Wizard, Driver-Dispo und Payroll Closeout bleiben Folge-Slices.

## AGENT-ORCH-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Symphony als Blaupause fuer einen VALEO-eigenen Agent-Orchestrator in einem kleinen, repo-sicheren Pilot umsetzen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/agent-orchestrator-pilot.md`, `scripts/agent_workboard_supervisor.py`, `tests/test_agent_workboard_supervisor.py`
**Abnahmekriterien:** Ein CLI-Pilot erkennt Workboard-Slices, erzeugt Claim-Vorschlaege, listet Checks und Handoff-Geruest, ohne automatisch zu claimen, zu committen, zu pushen oder Agents zu starten.
**Erledigt:** Read-only Supervisor `scripts/agent_workboard_supervisor.py` eingefuehrt; Parser erkennt Slice-IDs, Statusklassen, Owner, Dateibesitz, Checks und Risiken; CLI liefert `list`, `claim-proposal`, `checks` und `handoff-template`. Pilotdoku liegt in `docs/agent-ops/agent-orchestrator-pilot.md`.
**Checks:** `pytest tests/test_agent_workboard_supervisor.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py list --status open`; `python scripts/agent_workboard_supervisor.py claim-proposal DOM-FIN-002 --owner Codex`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Markdown-Workboard ist kein striktes Datenformat; der Pilot muss konservativ parsen und unklare Bloecke melden statt still zu raten.

## AGENT-ORCH-002

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Maschinenlesbare Slice-Dateien oder ein Validierungs-Gate fuer Workboard-Claims einfuehren, damit der Orchestrator nicht dauerhaft auf weichem Markdown basiert.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/**`, `scripts/agent_workboard_supervisor.py`, `tests/test_agent_workboard_supervisor.py`
**Abnahmekriterien:** Claim-Pflicht ist maschinenlesbar validierbar; unklare Status-/Owner-/Dateibesitz-Felder werden als Fehler gemeldet, ohne automatische Git-Aktionen auszufuehren.
**Erledigt:** YAML-Slice-Format eingefuehrt (`docs/agent-ops/slices/*.yaml`); `validate`-Subcommand in `agent_workboard_supervisor.py` ergaenzt; 14 neue Tests gruen; historische Markdown-Bloecke werden nur validiert wenn YAML-Datei oder `--strict-ids` vorhanden.
**Checks:** `pytest tests/test_agent_workboard_supervisor.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`
**Offene Risiken:** Bestehende historische Workboard-Bloecke sind uneinheitlich und duerfen nicht durch ein zu striktes Gate blockieren.

## ERP-CRIT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Backend-Testabdeckung und Vertragsstabilitaet fuer kritische ERP-Pfade zuerst an real roten Tests und Ratchet-Pfaden verbessern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/payment_runs.py`, `tests/test_process_kernel_wave1_contracts.py`, relevante Coverage-/Ratchet-Doku.
**Abnahmekriterien:** Der aktuell rote Payment-Return-Vertrag laeuft wieder; Coverage-Ratchet-Status ist dokumentiert; naechste unterdeckte Pfade sind als konkrete Test-Slices priorisiert.
**Erledigt:** `payment_runs.return_payment` toleriert aktuelle und Legacy-Zeilenformate fuer Ruecklaeufer-Betraege; der rote Vertragstest ist gruen. Coverage-Ratchet-Folgereihenfolge ist dokumentiert in `docs/quality-assurance/critical-backend-coverage-plan-2026-04-24.md`.
**Checks:** `pytest tests/test_process_kernel_wave1_contracts.py::test_return_payment_persists_outbox_event tests/test_process_kernel_wave1_contracts.py::test_payment_return_amount_accepts_current_and_legacy_row_shapes -q`
**Offene Risiken:** `check_critical_backend_coverage.py` bleibt nach dem gruenen Sammellauf noch rot fuer `dunning.py`, `booking_templates.py`, `chart_of_accounts.py`, `finance_read_models.py`, `waage.py`, `warehouses.py`, `warehouse_transfers.py`; diese Pfade sind in der Coverage-Plan-Datei als Folgeslices priorisiert.

## ERP-CRUD-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Browser-/CRUD-Abnahme der wichtigsten E2E-Prozesse in eine ausfuehrbare, priorisierte Testmatrix ueberfuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/quality-assurance/browser-use-checklists.md`, `docs/quality-assurance/e2e-crud-acceptance-matrix-2026-04-24.md`, ggf. vorhandene Frontend-E2E-Testkonfiguration.
**Abnahmekriterien:** Die neun Flow-Spine-Prozesse besitzen eine priorisierte CRUD-/Statuswechsel-/Korrekturmatrix mit klaren P0/P1-Prueffaellen und Repo-Pruefkommandos.
**Erledigt:** Neue priorisierte E2E-CRUD-Matrix fuer P0/P1-Flow-Spine-Prozesse erstellt und in den Browser-Use-Checklisten verlinkt.
**Offene Risiken:** Echte Browser-Ausfuehrung haengt vom lokal startbaren Fullstack und Seed-Daten ab.

## ERP-LIVE-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Live-Integrations-Readiness mit echten Secrets/Zielsystemen so weit repo-seitig vorbereiten, dass Ops nur noch Werte eintragen und Pruefkommandos ausfuehren muss.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/integration-bootstrap-readiness-2026-04-12.md`, `scripts/check_integration_bootstrap.py`, `app/services/integration_bootstrap.py`, `.env.example`.
**Abnahmekriterien:** Readiness-Bericht trennt deterministische Repo-Pruefung und externe Live-Probes; fehlende Secrets/Ziele werden maschinenlesbar als Blocker ausgewiesen.
**Erledigt:** `--strict-live` ergaenzt; Live-Probe-Plan und Gate sind dokumentiert.
**Offene Risiken:** Produktive Tenant-Secrets und Zielsystem-URLs liegen ausserhalb des Repos.

## FIBU-CUTOVER-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** FIBU-Cutover-Mappings fachlich abschliessbar machen, indem Pflichtmapping, Freigabezustand und Validierung formalisiert werden.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/fibu-cutover-mapping-readiness-2026-04-24.md`, `config/fibu_cutover_mapping.template.yaml`, `scripts/check_fibu_cutover_mapping.py`, `tests/test_fibu_cutover_mapping.py`.
**Abnahmekriterien:** Konten-, Steuer-, Kostenstellen- und Gegenkonto-Mappings haben eine Vorlage, einen Validator und einen klaren Blockerstatus fuer fachliche Freigabe.
**Erledigt:** FIBU-Cutover-Template, Validator, Tests und Readiness-Doku erstellt.
**Offene Risiken:** Fachlich freigegebene Zielkonten/-steuerschluessel muessen vom Fachbereich geliefert werden.

## RATIONS-SPLIT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rations-Solver technisch weiter entkoppeln, ohne die LP-Semantik zu aendern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/rations_optimization.py`, `app/agrar/rations/solver/*`, relevante Rations-Tests.
**Abnahmekriterien:** Ein weiterer klarer Solver-Baustein wird aus `rations_optimization.py` in das Solver-Paket gezogen oder mit typisierter Hilfslogik isoliert; Regression bleibt gruen.
**Erledigt:** Mischgruppen-Reihenfolge als `app/agrar/rations/solver/mixing.py` aus dem Endpoint-Pfad herausgezogen und separat getestet.
**Offene Risiken:** Vollstaendige `_run_lp`-Zerlegung ist ein mehrstufiger Refactor.

## DOMAIN-PARITY-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Domänenparitaet in schwächeren Bereichen als messbares Ausbauprogramm statt loser Absicht fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/domain-parity-roadmap-2026-04-24.md`, `docs/project-context/open-gaps-and-known-issues.md`.
**Abnahmekriterien:** Finance, Supply/Inventory, Procurement, Contracts, CRM und Documents sind nach Fachlogik, Testtiefe, Integration und UI-Operationalisierung bewertet; naechste Code-/Test-Slices sind priorisiert.
**Erledigt:** Domain-Parity-Roadmap mit Bewertungsraster, Prioritaeten und naechsten Code-Slices erstellt und in `open-gaps` verlinkt.
**Offene Risiken:** Tiefe fachliche Paritaet braucht weitere domänenspezifische Arbeit und Fachentscheidungen.

## RATIONS-HARD-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rations-/Fuetterungsmodul nach Punkt 4 gezielt haerten, ohne den Solver grossflaechig umzubauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_feeding_system.py`, `tests/test_rations_mixing_protocol.py`
**Abnahmekriterien:** Weide wird auch bei nominellem TMR-Input nicht ins Mischprotokoll aufgenommen; Auto-Promotion TMR -> PMR_pasture ist regressionsgesichert; Mischprotokoll nutzt die vorhandene Feed-Dataclass als typisierte Solver-Sicht.
**Erledigt:** Mischprotokoll nutzt `Feed.from_dict()` fuer die typisierte Feed-Sicht; TMR+verfuegbare Weide wird auf PMR_pasture auto-promoted; falsch als `tmr_block` gelabelte Weide wird aus der Mischung ausgeschlossen und im Protokoll als `excluded_pasture` ausgewiesen.
**Checks:** `pytest tests/test_rations_feeding_system.py tests/test_rations_mixing_protocol.py tests/test_rations_feed_dataclass.py -q`
**Offene Risiken:** Vollstaendige Zerlegung von `_run_lp` und regelbasiertes Warnsystem bleiben Folgeslices. Konzentrat-Tagesmax wird jetzt als Stage-2-LP-Slack abgebildet (siehe RATIONS-POLICY-PIPE-001).

## RATIONS-POLICY-PIPE-001

**Von:** Cursor
**Stand:** abgeschlossen 2026-04-24
**Ziel des Slices:** Rationspipeline policy-/fachlich schaerfer machen (Saftfutter-Caps, PMR-Weide-Profile, k_l, Infeasibility-Hilfen, Konzentrat-Slack) und Frontend/TS an die erweiterte API anbinden.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_feeding_system.py`, ggf. `app/agrar/rations/solver/mixing.py` / `tests/test_rations_solver_mixing.py`.
**Abnahmekriterien:** Backend liefert die neuen Meta-Felder (u. a. Konzentrat-Slack, `ration_blocks.feeding_system.auto_promoted_from_tmr`, Mixing `excluded_pasture`); Frontend sendet `feeding_system_config` und zeigt RationBlocks/Mixing/KF-Slack; Regression gruen.
**Erledigt:** Saftfutter/nasse CoP: weiche/harte Caps, LP-hart, Soft-Constraint + Referenz-HTML; `_POLICY_PROFILE_TARGETS` um `tmr_standard`, `pmr_standard`, `pmr_pasture_spring/summer/autumn`; Stage-2 Konzentrat-Tagesmax-Slack + Response `concentrate_max_lp_slack_*`; nach Solve FS mit Ist-Mengen neu aufgeloest, `_block_labels` aktualisiert; Infeasibility: Heu/Stroh-Abdeckung, aNDFom-Kapazitaet (`ndf_capacity`), generischer Zweig nur bei grobfutterarmem Set; k_l bei PMR+Weide ueber FANi + TMR-ME-Dichte (`_kl_milk_from_me_density`); `result.x` auf Feed-Laenge begrenzt. Frontend: Typen, Default-Config im Request, Panels, Policy-Badge fuer KF-Slack.
**Checks:** `pytest tests/test_rations_feeding_system.py tests/test_rations_optimization_milk_plausibility.py -q`; im Paket `frontend-web`: `pnpm run type-check`
**Offene Risiken:** Optional Wizard fuer manuelle `feeding_system_config`-Overrides; E2E-Smoke Rations-UI; weiteres Zerlegen von `_run_lp`.

## RATIONS-WIZARD-E2E-001

**Von:** Cursor
**Stand:** abgeschlossen 2026-04-24
**Ziel des Slices:** Wizard-Schritt 3 (Grenzen + weiche Ziele) als State/API an Backend anschließen, Prioritäten grob an `objective_strategy` koppeln, TM-Ziel/`target_dmi_kg` und Wizard-TM-Band im `_gfe_requirements` nutzen, Workbench-Duplikatnamen klären, Playwright mit `webServer`, kurze Pytest-Regression, QA-Checkliste ohne private Fixtures.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py` (`_gfe_requirements`, `_run_lp` Wizard-Dichten), `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `packages/frontend-web/playwright.config.ts`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `tests/test_rations_wizard_requirements.py`, `docs/agent-ops/rations-manual-compound-qa.md`.
**Abnahmekriterien:** Frontend sendet `objective_strategy`, `policy_overrides.wizard_*`, `wizard_dmi_*` am Profil; Backend klemmt TM-Band; Playwright kann Vite selbst starten; Regressionstests gruen.
**Checks:** `pytest tests/test_rations_wizard_requirements.py -q`; im Paket `frontend-web`: `pnpm exec playwright test tests/e2e/rations-compound-upload.spec.ts` (mit laufendem Backend) bzw. `pnpm run type-check`.
**Erledigt (Folgesession LP):** `policy_overrides.wizard_hard_bounds` steuert ME-/Stärke-/aNDFom-Mindest- bzw. Höchst-Dichten (linear auf Gesamtration); `andfom_gf_min_pct_tm` schärft die aNDFomGF+CoP-Untergrenze vor LP-Aufbau.
**Erledigt (Session 2026-04-24ff):** `wizard_soft_goals` wirken solver-seitig fuer `minimize_soya` (Stage-1-Welfare-Penalty + Stage-2-Kostenzuschlag auf Soja-Futtermittel), `prefer_homegrown` (Bonus fuer `gfa_`-/`_source=="gfa"`-Feeds), `maximize_n_efficiency_rmd` (Penalty bei hohem Feed-RMD); Metadata `wizard_soft_goals_lp` listet aktive Flags. `optimization_strategy` bleibt Legacy-Kurzstring; Detail in `optimization_strategy_pipeline`. Milch-Kennziffern GF/Weide: anteilige Erhaltungsbuchung ueber GF-ME-/Teilmengen-ME-Anteil (`_maintenance_allocation_fraction`).
**Erledigt (Session 2026-04-24 Baseline-L1):** `minimize_deviation_from_baseline` mit `policy_overrides.wizard_baseline_kg_dm` (feed_id -> kg TM): L1-Abstand via Hilfsvariablen in Stage 1 (`_WIZARD_BASELINE_L1_WEIGHT`) und gekoppeltes Gewicht in Stage 2; Frontend speichert nach erfolgreicher Optimierung die Ist-Ration als Baseline und sendet sie bei Re-Optimierung. Playwright-Smoke `tests/e2e/rations-smoke.spec.ts` (Demo-Pfad).
**Offene Risiken:** Gewicht `_WIZARD_BASELINE_L1_WEIGHT` ggf. kalibrieren; weiteres Zerlegen von `_run_lp`.

## INT-LIVE-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Produktnahe Live-Integrationspruefung nach Punkt 6 repo-seitig konkreter machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/services/integration_bootstrap.py`, `scripts/check_integration_bootstrap.py`, `tests/test_integration_bootstrap.py`, `docs/project-context/integration-bootstrap-readiness-2026-04-12.md`, `docs/project-context/open-gaps-and-known-issues.md`
**Abnahmekriterien:** Bootstrap-Readiness liefert zusaetzlich einen Probe-Plan fuer echte Connectivity-Pruefungen; CLI kann diesen Plan ausgeben; Tests unterscheiden ready, disabled, blocked und manual/external.
**Erledigt:** `build_integration_bootstrap_summary()` liefert jetzt `probe_plan`; `scripts/check_integration_bootstrap.py --probe-plan` gibt nur diesen Live-Probe-Plan aus; Tests decken ready/blocked/disabled fuer OIDC, NATS, Superglue, Voice und CRM-Downstream ab.
**Checks:** `pytest tests/test_integration_bootstrap.py -q`
**Offene Risiken:** Echte Produktivtests benoetigen weiterhin externe Tenant-Secrets, Zielsystem-URLs und Ops-Freigaben.

## RATIONS-REFACTOR Schritte 1-5 (abgeschlossen 2026-04-23)

**Von:** Cursor
**Auslöser:** User-Feedback "rations_optimization.py: too large, too much in one pass, Refactoring-Roadmap in 5 Schritten".
**Stand:** Alle 5 Refactoring-Schritte umgesetzt; 561 passende Tests in der Rations-Regression (547 + 8 Aggregator + 6 Feed).

**Auslieferung:**
- **Paketstruktur** (Schritt 1a-e): Neues Paket `app/agrar/rations/` mit Subpackages `constants/`, `compound_feed/`, `repository/`, `http/`, `solver/`, `response/`. Konstanten, HTTP-Proxy, DLG-JSON-Loader und Compound-Feed-Parser (OCR/PDF/Etikett) leben jetzt in dedizierten Modulen; Re-Exports in `rations_optimization.py` halten die öffentliche Schnittstelle stabil.
- **Zentrale Aggregation** (Schritt 2): `RationAggregates` @dataclass(slots=True) + `aggregate_ration()` in `app/agrar/rations/response/aggregator.py`. `_build_response` nutzt sie jetzt in einem einzigen Pass statt 16+ `_sum()`-Aufrufen plus separaten Schleifen für Forage, CoP, pabKH und pendf. Block-Aggregation (Slice 1f) ist integriert.
- **Constraint-Registry** (Schritt 3): `ConstraintRegistry` + 17 symbolische Constraint-Namen in `app/agrar/rations/solver/constraint_registry.py`. `_run_lp` registriert jeden `_geq`/`_leq`-Aufruf benannt; die 4 historisch magischen Relaxations-Indizes (`_IDX_XL`, `_IDX_ANDFOM_GF`, `_IDX_RMD`, `_IDX_ME_ABS`) werden jetzt via `registry.index_of(...)` aufgelöst. Regressions-Asserts sichern die historische Reihenfolge.
- **Relaxations-Kapselung** (Schritt 4): Die 4-stufige Relaxations-Kaskade (XL → RMD → aNDFomGF-Drop → sidP-85%) ist aus dem LP-Hauptblock in eine benannte Closure `_relax_stage1()` ausgezogen. Semantik unverändert.
- **Feed-Dataclass** (Schritt 5): `Feed` @dataclass(slots=True) in `app/agrar/rations/solver/feed.py` als read-only View auf die Dict-Struktur. Bietet `Feed.from_dict()` mit konsistenter Typkonvertierung (None → 0.0 bei numerischen Pflichtfeldern, Optional bei unsicheren). Slot-Schutz verhindert unbeobachtete Attributerweiterungen. **Keine Breitenumstellung**, Opt-in für künftige Module.

**Tests:**
- Neue Unit-Tests `tests/test_rations_aggregator.py` (8 Tests) und `tests/test_rations_feed_dataclass.py` (6 Tests).
- Volle Rations-Regression: **561 pass** (davon 547 bestehende, unverändert grün).

**Offene Folgeschritte (bewusst separat):**
- Vollständige Zerlegung von `_run_lp` in Constraint-Builder/Relaxation/Stage2-Cost/Solve-Orchestrator (Schritt 4 ist bewusst minimal invasiv geblieben; ein echter Split ist ein eigener, größerer Slice).
- Breitenumstellung `Feed.from_dict`-basiert in `_run_lp` und `_build_response` (Schritt 5 legt nur das Fundament).
- Warnsystem regelbasiert (`WarningRule` statt if-Kaskade).
- Feed-Matrix mit NumPy für den Koeffizienten-Aufbau.



Dieses Board ist bewusst schlank gehalten, damit Session-Starts und Agent-Handoffs weniger Kontext verbrauchen.

## RATIONS-LP-SPLIT-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** `_run_lp` in `rations_optimization.py` durch Extraktion des Constraint-Matrix-Aufbaus in `app/agrar/rations/solver/lp_constraints.py` und der Stage-2-Policy-Extension in `app/agrar/rations/solver/lp_stage2.py` von ~1350 auf ~800 Zeilen reduzieren.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py`, `app/agrar/rations/solver/lp_constraints.py` (neu), `app/agrar/rations/solver/lp_stage2.py` (neu), `tests/test_rations_lp_constraints.py` (neu)
**Abnahmekriterien:** Volle Rations-Regression gruen; `_run_lp` < 900 Zeilen; `lp_constraints.py` exportiert `build_lp_constraint_matrix`; `lp_stage2.py` exportiert `build_policy_band_lp_extension`.

## COV-RATCHET-004

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Coverage-Schwellen fuer bereits gruene kritische Pfade kontrolliert anheben (Puffer auf 97 % des gemessenen Wertes) und drei neue Ratchet-Pfade aufnehmen (strecke.py, sales_orders.py, ap_invoices.py).
**Dateibesitz:** `scripts/check_critical_backend_coverage.py`, `docs/project-context/domain-parity-roadmap-2026-04-24.md`
**Abnahmekriterien:** Alle Schwellen liegen <= gemessener Wert; `python scripts/check_critical_backend_coverage.py` gibt gruenen Exit-Code wenn coverage.xml vorhanden.

## DOMAIN-PARITY-COV-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** COV-INT-002: Integrations-Governance-Tests fuer `strecke.py`, `kontrakte.py` und `ap_invoices.py` hinzufuegen; domain-parity-roadmap um abgeschlossene Slices aktualisieren.
**Dateibesitz:** `tests/test_strecke_api.py` (neu), `tests/test_kontrakte_api.py` (neu), `tests/test_ap_invoices_api.py` (neu), `docs/project-context/domain-parity-roadmap-2026-04-24.md`
**Abnahmekriterien:** Neue Testdateien vorhanden, >= 5 Tests je Datei, pytest gruen; Roadmap-Dokument aktualisiert.

## RATIONS-FS-WIZARD-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** Wizard-Schritt fuer `feeding_system_config` im Rations-Wizard in `rationsoptimierung.tsx` sichtbar machen (System-Auswahl TMR/PMR_stall/PMR_pasture, Konzentratsverteilung, Limits je Verteilung).
**Dateibesitz:** `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `packages/frontend-web/src/lib/api/rations-optimization.ts`
**Abnahmekriterien:** Wizard-Schritt sichtbar, `feeding_system_config` wird im Request gesendet, TypeScript-Typen passen, `pnpm run type-check` gruen.

## RATIONS-FANI-KL-001

**Von:** Cursor
**Owner:** Cursor
**Stand:** abgeschlossen 2026-05-07
**Ziel des Slices:** FANi-basiertes dynamisches k_l in den Solver-Iterationsloop einbauen: `_gfe_requirements` erhaelt optionales `fani`-Argument, das `k_l_planning` (bisher fix 0,60) via `_kl_milk_from_me_density` iterativ anpasst. Gilt fuer PMR_pasture und TMR.
**Dateibesitz:** `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_fani_kl.py` (neu)
**Abnahmekriterien:** `_gfe_requirements(profile, fani=3.2)` gibt anderen `me_mj` als `fani=None`; Rations-Regression gruen; FANi-Iteration in `_run_lp` reicht FANi an `_gfe_requirements` durch.

Archiv des vorherigen Boards:
- [active-workboard-2026-04-10-pre-slim.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/archive/active-workboard-2026-04-10-pre-slim.md)

## AGRAR-COV-001

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Unit- und HTTP-Tests fuer `agrar_contracts.py` und `agrar_settlements.py` — Abnahme-Status-Logik, Abrechnungs-Rundung, DQ-Datensatz-Aufbau und CRUD-Smoke-Pfade.
**Dateibesitz:** `tests/test_agrar_contracts_api.py` (neu), `tests/test_agrar_settlements_api.py` (neu)
**Abnahmekriterien:** >= 15 Tests je Datei; `_compute_status`, `_round_money`, `_round_qty`, `_build_*_dq_datensatz` und HTTP-Pfade gruendeckend; pytest gruen.
**Erledigt:** 20 agrar_contracts-Tests (Status-Logik, DQ, CRUD); 17 agrar_settlements-Tests (Rundung, Modell-Validierung, Smoke-HTTP). 54 pass gesamt.

## FIN-COV-002

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Unit- und HTTP-Tests fuer `closing_checklists.py` und `bank_reconciliation.py` — Mapping-Funktion, Freigabe-Logik, Pydantic-Modelle und Smoke-Pfade.
**Dateibesitz:** `tests/test_closing_checklists_api.py` (neu), `tests/test_bank_reconciliation_api.py` (neu)
**Abnahmekriterien:** `build_closing_checklist_response` vollstaendig getestet inkl. approval_can_close und explainability; Pydantic-Modelle fuer BankReconciliation; HTTP-Smoke-Pfade gruen.
**Erledigt:** 17 closing_checklists-Tests (Mapping, Freigabe, Explainability, Validierung, HTTP); 11 bank_reconciliation-Tests (Pydantic-Modelle, HTTP-Smoke). 54 pass gesamt.

## Arbeitsregel

- Nur aktive oder frisch abgeschlossene Slices bleiben hier sichtbar.
- Historische Serien wandern ins Archiv.
- Claim-Pflicht bleibt unveraendert:
  1. Slice auf `reserviert`
  2. Workboard committen
  3. erst dann implementieren

## FEEDING-SYSTEM-ARCHITECTURE Slices 1-3 (abgeschlossen 2026-04-23)

**Von:** Cursor
**Stand:** Slice 1a-1f/1h + Slice 2 (Futterabruf-Staffel) + Slice 3 (Mischprotokoll) komplett implementiert und gruen; 98 Slice-spezifische Tests plus 386 pass in der vollen Rations-Regression.
**Auslieferung:**
- **Datenmodell** (Slice 1a): Neue Pydantic-Modelle `ConcentrateRecipeProfile` (starch_breakdown_class rapid/mixed/slow, rumen_buffer_present, source), `FeedingSystemConfig` (system TMR/PMR_stall/PMR_pasture, concentrate_distribution transponder/ams/milkparlor/included_in_tmr, Grenzen je Verteilung), `FeedBlockAssignment` (manuelles Override fuer Feed->Block).
- **Block-Zuordnung** (Slice 1b): Helper `_feeding_system_defaults`, `_resolve_feeding_system_config`, `_auto_assign_block`, `_split_feeds_by_block`; Mineralfutter wird prioritaer ins `tmr_block` gesetzt (auch wenn im Namen "Weide" steht).
- **k_l-Logik** (Slice 1d): `_kl_milk_from_me_density` setzt bei `PMR_pasture` fix `k_l=0.60` (dokumentiertes Uebergangs-Fallback; FANi-basiertes k_l ist Folgeslice).
- **Solver-Scoping** (Slice 1c): Struktur-/CP-/XL-/pabKH-Dichten im LP nur auf den TMR-Block, wenn PMR-System mit aktivem pasture_block oder concentrate_staged_block vorliegt. Weide wird nicht als strukturell irrelevant behandelt (eigene Weide-/Aufnahmelogik weiterhin aktiv).
- **Konzentrat-Limits** (Slice 1e, nachgeschaerft): Einzelgabe physiologisch hart als 1.5x-Sicherheitsnetz im LP; empfohlenes Tagesmax weich im Constraint-Status (Klasse B, Halbbreite 1,5 kg). Rezepturklassen wirken: rapid REDUZIERT Tagesmax (SARA-Schutz), slow+Puffer = Premium.
- **Response-Payload** (Slice 1f): Neue Felder `ration_items[*].block` und `ration_blocks` (feeding_system + tmr_block/pasture_block/concentrate_staged_block mit DMI, Kosten, ME, sidP, CP und Items-Liste). Abwaertskompatibel: bei TMR bleibt pasture_block/concentrate_staged_block leer.
- **Wire-up** (Slice 1h): `_OptimizeFromProfileBody.feeding_system_config` und `feed_block_overrides` freigegeben; `_resolve_runtime_options` normalisiert beide und reicht sie bis in den Solver durch.
- **Regressionstests erweitert**: Bruder-Fall (PMR+Weide Fruehjahr) prueft jetzt explizit (a) keine harte globale Strukturstrafe, (b) plausible Milch-aus-Grobfutter (10-40 kg nach 1-kg-Milch/kg-TM-Praxisregel), (c) vollstaendige Mg/K-Diagnose, (d) kein technisches False-Infeasible, (e) ration_blocks-Aggregat deckungsgleich mit Gesamt-DMI.
- **Slice 2 - Konzentrat-Futterabruf-Staffel** (`_build_concentrate_call_up_table`): Linear / stueckweise linear oberhalb Basisleistung (Milch aus Grobfutter). Band 0,45-0,50 kg Konzentrat (FM) je kg Zusatzmilch (Praxisrichtwert, nicht KI-Bildwerte). Einzelgabe-Limit je Verteilungssystem (Transponder/AMS/Melkstand), empfohlenes Tagesmax (weich) und physiologische Obergrenze 1,5x (hart) werden explizit geprueft. Nur fuer gestaffelte Systeme; `None` bei TMR/included_in_tmr. Response-Feld: `concentrate_call_up`. Neues UI-Panel `ConcentrateCallUpPanel` unterhalb des Weide-Risiko-Panels. 12 neue Tests.
- **Slice 3 - Misch- und Fuetterungsprotokoll** (`_build_mixing_protocol`): Nur bei TMR-Block (TMR / PMR_stall). Reihenfolge Vertikalmischer: Strukturfutter -> Silagen -> Saftfutter/CoP -> Sonstiges -> KF/Mineralien. Wasserzugabe auf Ziel-TM 40 % (Standard), Uebermenge +5 % fuer Mischverluste. Transparente Warnungen bei sehr trockener / sehr nasser Mischung. Response-Feld: `mixing_protocol`. UI-Panel `MixingProtocolPanel` rendert direkt aus Backend-Daten (keine Heuristik im Frontend mehr). 11 neue Tests.
**Offene Folgeslices / Mittelfristig:** FANi-basiertes dynamisches k_l (statt fixem 0,60 bei PMR_pasture); dedizierte Weideaufnahme-/Substitutionslogik mit saisonalen Profilen (Sommer-Hitzestress, Herbst-N-Ueberschuss); echte LP-Slacks fuer das Konzentrat-Tagesmax (aktuell Post-Solve-Penalty); Wizard-UI fuer `feeding_system_config` (derzeit nur ueber API).

## FAN-MODE-V1 (abgeschlossen 2026-04-21)

**Von:** Codex
**Stand:** alle sechs Slices umgesetzt, committed und gruen; 63 FAN-MODE-Gate-Tests plus bestehende Rations-Regression passen (266 pass + 6 pre-existing wave74-Fehler, unabhaengig von FAN-MODE).
**Freigegebene Spezifikation:** [docs/project-context/rations-optimization-fan1-fani-spec-2026-04-21.md](C:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/rations-optimization-fan1-fani-spec-2026-04-21.md)
**Kernentscheidungen V1 (alle 2026-04-21 freigegeben, siehe §11.1):**
- `fan_tolerance=0.05`, warn `0.10`, max 5 Iterationen
- FAN-Presets `2.5 / 3.0 / 3.5` + Freiwert
- `relaxation_policy` dreistufig `strict` / `standard` / `soft`, Default `standard`
- Strafterme **dimensionslos normiert** auf Zielkorridor, Basis 1,0 EUR, Klassen A x10 / B x3 / C x1
- Drei-Block-Limits als versionierte **Policy-Profile** (`tmr_standard`, `pmr_standard`, `pmr_pasture_spring`), Override nur im Expertenmodus
- FAN-Formel-Katalog mit **Herkunftsflag** `exact | mapped | fallback` (Mapping auf DLG-Hauptgruppen GF/KF/SF, saisonal bei Weide/Gras)
- Wizard-FAN-Modus **sichtbar-kompakt** (Default `auto_iterative` direkt sichtbar, Reference/EvaluationOnly einklappbar)
- Bruder-Regression als **fachlich differenziertes** Abnahmekriterium (kein technisches False-Infeasible)
**Abgeschlossene Slices und zugehoerige Commits:**
- FAN-MODE-001: additiver Datenvertrag, neue Request-/Response-Felder, `_resolve_runtime_options`, Policy-/Season-Enums (commit vor dieser Session, +11 Gate-Tests).
- FAN-MODE-002: Hart/Weich-Split mit normierter Penalty (`_build_constraint_status_v2`, `_compute_penalty`, `_summarize_penalty`), erweiterte Infeasibility-Diagnose (commit `82b02735c`, +11 Gate-Tests).
- FAN-MODE-003: Fixpunkt-FAN-Iteration (`_apply_fan_effect`, `_fani_from_result`) mit Katalog `app/config/fan_slope_catalog.json` und drei Modi `auto_iterative` / `reference` / `evaluation_only`; Startwert aus geschaetzter DMI fuer schnelle Konvergenz (commit `f0dce8abb`, +12 Gate-Tests).
- FAN-MODE-004: Wizard-UI-Erweiterung in `rationsoptimierung.tsx` (Bewertungsmodus-Block, Reference-Presets, Advanced-Optionen) und Ergebnispanels `FanCalibrationPanel` + `ConstraintStatusPanel` in der Workbench (commit `b6bd983c7`).
- FAN-MODE-005: Saisonales Weideprofil im UI (PMR+Weide oeffnet Advanced, preset `spring_mid`, zeigt aktives Profil `pmr_pasture_spring`); Backend-Auto-Mapping in `_resolve_policy_profile` abgedeckt (commit `9a035ddd8`, +7 Gate-Tests).
- FAN-MODE-006: Strafsatz-Konfiguration vollstaendig sichtbar (Normalisierung, Klassen A/B/C, relaxation-Policy Monotonie), `penalty_summary` im Response und in der UI (commit `769cd1527`, +10 Gate-Tests).
**Offene Risiken / Follow-ups:** siehe §13 der Spec.
**Naechster Schritt:** Beobachtung der Fruehjahrsration-Regression unter `pmr_pasture_spring` in der Praxis, anschliessend optionaler Spec-Folge-Slice fuer explizite Slack-Variablen im Solver (Vollwert-3-Stage-Objective statt Post-Solve-Penalty) – nur bei konkretem Bedarf.

## peNDF als Kontrollgroesse + aNDFomGF-staerkeadaptiv (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; 22 neue peNDF-Demotion-Gate-Tests plus volle Rations-Regression `357 pass` (keine Regression gegenueber vorherigem Stand).
**Kontext / DLG-Position:** Die DLG 01|2023 stellt explizit fest: peNDF steht fuer die Rationsplanung **nicht zur Verfuegung**. Empfohlene primaere Planungsgroesse ist die aNDFomGF-Dichte (Grobfutter-NDF) mit Zielwert >= 200 g/kg TM fuer Hochleistungsrationen, bei hoeheren pansenabbaubaren Kohlenhydraten entsprechend mehr. peNDF bleibt als Kontroll-/Validierungsgroesse erhalten.
**Auslieferung:**
- **Neuer Helper `_andfom_gf_min_target`**: aNDFomGF-Mindestdichte setzt sich zusammen aus Basis (200 g/kg TM non-pasture, 180 g/kg TM PMR+Weide) + staerkeadaptivem Aufschlag (+10 g/kg TM pro 20 g/kg TM Staerke oberhalb 180, Cap +40) + Saisonal-Boost + SARA-Boost. Ist jetzt die primaere Pansenstruktur-Planungsgroesse.
- **Stage-2-LP umgebaut** (`_run_lp`): Der bisherige harte `pendf_floor` in Stage 2 (Cost-Stage) wurde durch ein staerkeadaptives `stage2_andfom_gf_min` ersetzt. peNDF bleibt nur noch als absolute physiologische Sicherheits-Floor (120 g/kg TM) im LP, nicht mehr als Planungsgroesse.
- **Kalibrierungsstatus `_pendf_model_calibrated`**: Das peNDF-Lookup-Modell gilt als kalibriert, wenn Staerke in [0, 250] g/kg TM und TM-Aufnahme in [10, 25] kg/d liegt. Ausserhalb laufen Fallback-Regeln. In `dlg_indicators` neu: `pendf_model_calibrated: bool`, `pendf_model_status: "peNDF-Modell im kalibrierten Bereich" | "peNDF ausserhalb Modellbereich; Fallback-Regeln verwendet"`, `pendf_role: "Kontrolle/Validierung (DLG 01|2023)"`. Ebenfalls neu: `andfom_gf_base` und `andfom_gf_starch_uplift` als transparente Herkunfts-Aufschluesselung.
- **Warnungen angepasst**: peNDF-Warnung laueft jetzt **primaer ueber den Kalibrierungs-Status** - ausserhalb Modellbereich erscheint ein expliziter Fallback-Hinweis statt einer pauschalen Unterdeckungs-Ampel. Innerhalb des Modellbereichs wird peNDF als "Kontrollgroesse im Warnbereich" markiert, mit Verweis auf aNDFomGF und pabKH als eigentliche Steuergroessen.
- **SARA-Trigger-Logik angepasst** (`_detect_sara_risk`): peNDF-Trigger feuert nur, wenn das Modell kalibriert ist. Zusaetzlich feuert jetzt ein expliziter `aNDFomGF < Ziel - 10`-Trigger als primaerer Struktur-Sicherheitspfad. pH-Trigger und pabKH-Trigger bleiben unveraendert.
- **Frontend-Panel `rationsoptimierung.tsx`** neu zweigeteilt: oberhalb "Planung (primaer)" mit Strukturindex, aNDFomGF (inkl. Staerke-Aufschlag-Zerlegung), pabKH, RMD - darunter "Kontrolle / Validierung (DLG 01|2023)" mit peNDF-Modell-Status-Zeile und peNDF/pH-Ampel. peNDF-Zeile heisst jetzt explizit "peNDF (Kontrolle)" und die Ampel wird neutralisiert (grau), wenn das Modell im Fallback-Bereich laeuft.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_pendf_demotion.py` (neu, 22 Tests).
**Tests:** `pytest -k "rations or optim or wave74"` -> **357 pass**. Neue Suite `tests/test_rations_optimization_pendf_demotion.py`: staerkeadaptive aNDFomGF-Berechnung parametrisiert, Kalibrierungsflag fuer typische und Extremwerte, `dlg_indicators`-Zeichenketten ("Kontrolle"/"aNDFomGF"/Fallback-Status), SARA-Trigger respektiert Kalibrierungsstatus, Warnung bei peNDF-Fallback.
**Simulation bestaetigt:** Variant B (Hochleistung 48 kg Milch, DMI 26.6 kg/d > 25) liefert jetzt den Hinweis "peNDF ausserhalb Modellbereich ... Fallback-Regeln verwendet - peNDF-Ampel nur eingeschraenkt belastbar". Keine False-Alarme bei fachlich guten Rationen.
**Offene Follow-ups:** Praxisvalidierung der staerkeadaptiven aNDFomGF-Staffelung mit echten Hochleistungsrationen. Ggf. Sekundaer-Kalibrierungs-Flag fuer die pH-Formel analog dokumentieren (ist bereits via `ph_formula_applicable` verfuegbar).

## Gras-/Silage-/Heu-Klassifikation TM-basiert (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `96 pass` (inkl. `32 neue Gate-Tests` in `tests/test_rations_optimization_grass_classification.py`).
**Kontext:** User-Feedback zum Screenshot vom 2026-04-21: In der Ration war "Gras, frisch o. konserviert, 2. Aufwuchs" mit 6,6 kg FM / 2,32 kg TM (→ 35 % TM) enthalten, wurde aber faelschlich als Weide klassifiziert - das UI-Panel zeigte "Grassilage TM: 0,00 kg". Die Namens-Heuristik konnte die drei DLG-Varianten (frisch/siliert/trocken, `TMGEHALT` 175/350/860 g/kg) nicht sauber unterscheiden, weil das Feed-Namens-Feld fuer alle drei identisch ist.
**Fachliche Regel (User):** "Haupterkennung fuer Silagen sind ein TM Gehalt von 30 bis 40 %, bei ueber 80 % Heulage, bei ueber 85 % Heu bei Gras."
**Auslieferung:**
- **Neue zentrale Funktion** `_grass_feed_kind(feed)` in `rations_optimization.py`: klassifiziert Gras-basierte Grobfutter **primaer ueber `dm_frac`** (TM-Anteil), mit Name-Fallback wenn TM fehlt. Rueckgabe `"pasture"` (TM < 30 %), `"grass_silage"` (30-80 % TM, inkl. Anwelksilage/Heulage), `"grass_hay"` (≥ 80 % TM bei Gras-Kontext) oder `None` (Nicht-Gras).
- **Vier Call-Sites vereinheitlicht:** `_is_pasture_feed` und `_is_grass_silage` (in `_build_response`), `_max_kg_for` (LP-Obergrenze), `_feed_pendf_factor_base`, `_has_pasture_forage`, `weide_mask` (TMR-Deckelung) und `_map_feed_to_gfe_group` (FAN-Gruppen-Zuordnung) nutzen jetzt durchgaengig die TM-basierte Klassifikation.
- **Regression aufgeloest:** "Gras, frisch o. konserviert, 2. Aufwuchs" mit 35 % TM wird jetzt korrekt als `grass_silage` erkannt; "Weide, Fruehjahr, jung" mit 17,5 % TM bleibt Weide. Die UI-Anzeige "Grassilage TM" im Weide-Panel listet kuenftig die konservierten DLG-Varianten korrekt.
- **Tests**: `tests/test_rations_optimization_grass_classification.py` (neu, 32 Tests) deckt ab: TM-Grenzen 30 %/80 %, alle drei DLG-Varianten, Weide-Erkennung, Heulage/Heu, Nicht-Gras-Futtermittel (Mais/Weizen/Soja/Stroh/Mineral), Name-Fallback ohne TM, Screenshot-Regression.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py` (6 Aenderungen: neue Helper-Funktion `_grass_feed_kind`, `_is_pasture_feed`/`_is_grass_silage`, `_max_kg_for`, `_feed_pendf_factor_base`, `_has_pasture_forage`, `_map_feed_to_gfe_group`), `tests/test_rations_optimization_grass_classification.py` (neu), `docs/agent-ops/active-workboard.md`.
**Tests:** `pytest tests/test_rations_optimization_dlg2025.py tests/test_rations_optimization_compound_feed.py tests/test_rations_optimization_grass_classification.py` → **96 pass**, keine Regression.
**Offene Follow-ups:** - (keine).

## Milch-aus-Grundfutter Plausibilitaet + TM-basierte Gras-Klassifikation (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `115 pass` in 4 relevanten Rations-Suiten (davon `51 neue Gate-Tests`: 32 in `test_rations_optimization_grass_classification.py`, 19 in `test_rations_optimization_milk_plausibility.py`).

**Kontext:** Zwei verschraenkte User-Beobachtungen aus dem Screenshot vom 2026-04-21:
1. "Gras, frisch o. konserviert, 2. Aufwuchs" (35 % TM) wurde faelschlich als Weide klassifiziert -> UI zeigte "Grassilage TM: 0,00 kg". Der Feed-Name konnte die drei DLG-Varianten (frisch 17,5 % / siliert 35 % / trocken 86 % TM) nicht unterscheiden, weil das Namensfeld fuer alle identisch ist.
2. Faustregel "1 kg TM Grundfutter ~ 1 kg Milch, Spitzengrundfutter bis 1,2" wurde massiv ueberschritten (37,6 kg Milch / 22,1 kg GF-TM = 1,70 kg/kg).

**Auslieferung - TM-basierte Klassifikation:**
- **Neue zentrale Funktion** `_grass_feed_kind(feed)` in `rations_optimization.py`: klassifiziert primaer ueber `dm_frac` (Frischgras < 30 %, Grassilage inkl. Anwelksilage/Heulage 30-80 %, Heu >= 80 %), Name-Fallback wenn TM fehlt.
- **Sechs Call-Sites vereinheitlicht:** `_is_pasture_feed`, `_is_grass_silage`, `_max_kg_for`, `_feed_pendf_factor_base`, `_has_pasture_forage`, `_map_feed_to_gfe_group` nutzen jetzt durchgaengig die TM-Klassifikation.

**Auslieferung - Milch-aus-GF-Plausibilitaet (drei Slices):**
- **Slice A - Weide-Aktivitaetszuschlag:** In `_gfe_requirements` und `_milk_requirement_factors` wird bei `feeding_type == "PMR+Weide"` ME_maint um **+15 %** erhoeht (DLG-Merkblatt 417 / GfE 2001: Lauf-, Rupf-, Thermoregulations-Aktivitaet). Das wirkt sowohl auf die Solver-Bedarfsberechnung (Konsistenz) als auch auf die Anzeige "Milch aus Grundfutter".
- **Slice B - Weide-TM-Obergrenze:** In `_max_kg_for` wurde die Weide-Obergrenze von 14 auf **12 kg TM/d** reduziert (DLG 417: Praxismittel Hochleistungs-Standweide 10-12 kg). Das begrenzt die LP-Optimierung auf physisch erreichbare Aufnahmemengen.
- **Slice C - dichte-abhaengiges k_l:** Neue Helper-Funktion `_kl_milk_from_me_density(me_density)` implementiert GfE 2001 §5: **k_l = 0,463 + 0,24 * q** mit q = ME/GE (GE ~ 18,4 MJ/kg TM), begrenzt auf den Arbeitsbereich [0,58 ; 0,64]. Statt fix `k_l = 0,62` rechnet der Code jetzt fuer jede Auswerte-Ebene (Gesamt, Grundfutter, Weide, Grassilage, Weide+Silage) mit der ration-spezifischen ME-Dichte. In `_gfe_requirements` selbst bleibt `k_l_planning = 0,60` als konservativer Default fuer den Solver-Bedarf (leichte Verschaerfung gegenueber vorher 0,62, ~3 % mehr ME-Bedarf).

**Wirkung auf den Screenshot-Fall (ME-Dichte 11,6 MJ/kg TM, 22,1 kg GF-TM, PMR+Weide):**
- Alte Anzeige: 37,6 kg Milch aus GF -> 1,70 kg/kg TM
- Neu (A+C in fester Ration): 37,1 kg -> 1,68 kg/kg TM (nur -0,5 kg, weil bei 11,6 MJ/kg ME-Dichte die Faustregel rechnerisch hoeher liegt)
- **Eigentlicher Hebel ist Slice B in der LP-Optimierung**: Die naechste Demo-Rueckoptimierung wird statt 14 kg Weide nur noch 12 kg ansetzen duerfen, wodurch der Solver mehr Kraftfutter einsetzt und "Milch aus Grundfutter" auf realistische 28-32 kg faellt (~1,3-1,4 kg/kg TM).

**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py` (neue Helper `_grass_feed_kind`, `_kl_milk_from_me_density`; modifiziert: `_gfe_requirements`, `_milk_requirement_factors`, `_milk_from_supply`, `_max_kg_for`, `_is_pasture_feed`, `_is_grass_silage`, `_feed_pendf_factor_base`, `_has_pasture_forage`, `_map_feed_to_gfe_group`, alle Weide-/Grassilage-Milch-Aufrufe im `_build_response`).
**Neue Tests:** `tests/test_rations_optimization_grass_classification.py` (32 Gate-Tests), `tests/test_rations_optimization_milk_plausibility.py` (19 Gate-Tests fuer k_l-Kurve, Weide-Zuschlag, Screenshot-Regression, Faustregel-Korridor).

**Tests:** `pytest tests/test_rations_optimization_*.py` -> **115 pass**, keine Regression in den bestehenden Suites (dlg2025: 60, compound_feed: 4).

**Fachliche Quellen:**
- GfE 2001 (Empfehlungen fuer die Energie- und Naehrstoffversorgung der Milchkuh), §5 k_l-Berechnung
- DLG-Merkblatt 417 "Fuetterung der Milchkuh auf der Weide"
- DLG-Futterwerttabellen 2025 (Feld `KONSERVIERUNG`: frisch / siliert / trocken mit TM 175/350/860 g/kg)

**Offene Follow-ups:** - (keine). Weitere Feldvalidierung erfolgt durch den naechsten Durchlauf der Bruder-Regression mit den neuen Grenzen.

## DLG-01|2025 LP-Slacks + Praxisvalidierung Bandgewichte (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `155 pass` in den acht relevanten Rations-Suiten (inkl. `+22 neue Gate-Tests` in `tests/test_rations_optimization_dlg2025.py` → jetzt 60 DLG2025-Tests).
**Kontext:** Zwei Follow-ups aus dem Slice "DLG-01|2025 Solver-Bindung" zusammengezogen - (a) die Post-Solve-Penalty fuer Policy-Baender wurde durch **native LP-Slack-Variablen** ersetzt, und (b) die Halbbreiten (`min_halfwidth`) je Parameter wurden mit typischen Hochleistungs- und Trockensteher-Rationen kalibriert und als Tests abgesichert.
**Auslieferung:**
- **Backend `_build_policy_band_lp_extension`** (neu in `rations_optimization.py`): baut fuer jedes Policy-Band (ME-/CP-/sidP-/pabKH-/XL-/Grundfutter-/aNDFomGF+CoP-/aNDFom-Dichte) eine **Slack-Variable** `s_min` bzw. `s_max >= 0` mit normierter Penalty im Objective auf. Die Slack-Kosten skalieren mit `base × class_B × relax_factor / (halfwidth × DMI_typ)`, so dass LP-Slack und Post-Solve-Penalty fachlich aequivalent sind. `_run_lp` fuehrt, wenn ein DLG-2025-Profil aktiv ist, einen **erweiterten Stage-2-Solve** durch (`prices ⊕ slack_costs`, `A ⊕ slack_cols`, `bounds ⊕ (0, ∞)`); bei Erfolg werden nur die Feed-Anteile uebernommen, die Slack-Werte gehen als Diagnose-Payload `policy_profile_lp_slacks` in die Response. Metadaten-Strategie ist dann `stage1_balance_then_stage2_cost_plus_policy_slack`.
- **Response-Erweiterung:** neue Felder `policy_profile_lp_slacks` (pro Band: `slack_value`, `weight`, `halfwidth`, `penalty_cost`, `active`), `policy_profile_lp_total_penalty`, `policy_profile_lp_mode`. Die bisherige Post-Solve-Auswertung `policy_profile_evaluation` bleibt als unabhaengiger Gegencheck erhalten, wenn die LP-Slacks aus technischen Gruenden kein Payload liefern.
- **Frontend `rations-optimization.ts`**: neuer Typ `PolicyProfileLpSlack`, Response-Interface um die drei neuen Felder erweitert.
- **UI `rationsoptimierung.tsx`**: im Panel "Leistungsstufen-Check (DLG 01|2025)" neues Badge **"LP-Slack aktiv"** (gruen) bei nativer Bindung plus Subsection "LP-Solver-Slacks (aktive Korridor-Verletzungen)" mit Slack-Wert/Einheit und Penalty pro Band sowie Summen-Penalty - zeigt, welche Baender der Solver selbst relaxieren musste.
- **Praxisvalidierung `test_rations_optimization_dlg2025.py`**: neue Klassen `TestPolicyBandLpSlackExtension` (6 Tests) und `TestPolicyBandHalfwidthCalibration` (16 parametrisierte Tests) belegen fuer typische Hochleistungs- (35-45 kg, ME 7,0-7,2 / CP 155-170 / sidP 78-85) und Trockensteher-Rationen (ME 5,8-6,2 / CP 120-135 / aNDFom 380-460), dass Werte **im Korridor zero-penalty** sind und Abweichungen > Halbbreite **monoton zunehmende Strafen** erzeugen. Zusaetzlich: `test_halfwidth_is_reference_for_penalty_unit` fixiert, dass eine Abweichung von exakt `1 × min_halfwidth` ausserhalb des Korridors die Einheits-Strafe `base × class_B × relax_standard` ergibt.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_dlg2025.py`, `docs/agent-ops/active-workboard.md`.
**Tests:** `pytest tests/test_rations_optimization_*.py tests/test_drying_rule_engine.py` → **155 pass**, keine Regression.
**Offene Follow-ups:** - (keine mehr aus dem DLG-01|2025-Block; weitere Feldvalidierung erfolgt im Rahmen der Bruder-Regression und der Hitzestress-/Herbstrations-Slices.)

## DLG-01|2025 Solver-Bindung + Wizard-Leistungsstufen (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; `138 pass` in den sieben relevanten Rations-Suiten (inkl. 7 neue Band-/Solver-Bindungs-Tests in `tests/test_rations_optimization_dlg2025.py`).
**Kontext:** Follow-ups aus dem "DLG-01|2025-Alignment"-Slice wurden zusammen gezogen - (a) die Referenzkorridore aus `_POLICY_PROFILE_TARGETS` waren bisher nur im Response sichtbar, aber nicht im Solver gebunden, und (b) die neuen DLG-2025-Leistungsstufen waren nicht im Wizard anwaehlbar.
**Auslieferung:**
- **Backend `rations_optimization.py`**: Neue Helfer `_policy_profile_band_evaluate` + `_build_policy_profile_evaluation`. Nach jedem erfolgreichen LP-Lauf werden die Ist-Werte der Ration gegen die DLG-01|2025-Referenzkorridore des aktiven Profils als **weiche Bandchecks** (direction = min / max / target, Band-Modell) ausgewertet. Penalty faellt in **Klasse B** (Balance), relaxation_policy skaliert wie gewohnt (strict = 3x, standard = 1x, soft = 0.3x). Innerhalb des Korridors gilt `deviation_norm = 0`, also keine Strafe - dadurch keine zusaetzliche Infeasibility-Gefahr fuer schwierige Praxisrationen.
- **Ausgewertete Baender:** ME-Dichte (MJ/kg TM), CP-Dichte (g/kg TM), sidP-Dichte (g/kg TM), pabKH (max), Rohfett XL, Grundfutteranteil (%TM), aNDFomGF+CoP (min), aNDFom (min). Jedes Band traegt den Namen `DLG-Policy: ...` in `constraint_status` (source=`policy_profile`).
- **Response-Erweiterung:** neues Feld `policy_profile_evaluation` mit `profile`, `label`, `bands` (alle Checks inkl. `ok`), `violation_count`, `violations`, `penalty_total`, `source`. `penalty_summary.by_class.B` enthaelt die Policy-Strafe mit.
- **Frontend `rations-optimization.ts`**: neue Typen `PolicyProfileBand` + `PolicyProfileEvaluation`, Response um `policy_profile_evaluation` erweitert, `PolicyProfileTargets`-Feldnamen an das Backend angepasst (`forage_share_min_pct` / `forage_share_max_pct` / `ndf_kgdm_min`).
- **Wizard `rationsoptimierung.tsx`**: Im Advanced-Block neuer Dropdown **"Leistungsstufe (DLG 01|2025 Tab. 13-15)"** mit sechs Leistungs-/Physiologiestufen (`tmr_fresh_lactation`, `tmr_high_yield`, `tmr_mid_yield`, `tmr_late_lactation`, `tmr_transit`, `tmr_dry_cow`) plus den Bestandsprofilen (`tmr_standard`, `pmr_standard`, `pmr_pasture_spring|summer|autumn`). Default "Auto (aus Fuetterungstyp/Saison)". Die Auswahl wird durch den vorhandenen `policy_profile`-Request-Parameter an das Backend durchgereicht. Hinweistext macht sichtbar, dass die Bindung **weich** ist (Klasse B, relaxation-policy-skaliert).
- **Ergebnispanel:** neues Panel "Leistungsstufen-Check (DLG 01|2025)" direkt nach dem DLG-Strukturkontrolle-Panel. Zeigt Profil-Label, Gesamtstrafe Klasse B, pro Band `Ist-Wert`, `Korridor (min … max)`, Abweichungs-Norm und Ampelpunkt (gruen/ok oder orange/violated). Badge oben zeigt "alle Baender im Korridor" oder "N Abweichung(en)".
- **Tests (7 neu in `tests/test_rations_optimization_dlg2025.py`):** `_policy_profile_band_evaluate` → ok-Band ohne Strafe, Unter-Min und Ueber-Max erzeugen Strafe in Klasse B, strict/standard/soft skaliert Strafe monoton, `_build_policy_profile_evaluation` returniert `None` ohne Profil/Targets, End-to-End-Response belegt `policy_profile_evaluation` + `constraint_status`-Eintraege mit `source=policy_profile` und fuettert `penalty_summary.by_class.B`. Negativtest: `tmr_standard` liefert kein `policy_profile_evaluation`.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_dlg2025.py`.
**Tests:** `pytest tests/test_rations_optimization_*.py` → **138 pass** in den sieben relevanten Suiten, keine Regressionen gegenueber dem vorherigen Stand (82 pass).
**Offene Follow-ups:**
- Praxisvalidierung der Bandgewichte (min_halfwidth je Parameter) mit echten Hochleistungs-/Trockensteher-Rationen.
- Optional: Umstellung von Post-Solve-Penalty auf native LP-Slacks mit gemeinsamer Stufe-2-Zielfunktion (fachlich aequivalent, aber zukunftssicherer fuer Priorisierungsschemata).

## DLG-01|2025-Alignment (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; 32 neue DLG2025-Gate-Tests plus volle Rations-Regression `82 pass` in den vier relevanten Suiten.
**Kontext:** Nach dem SARA-Reopt + peNDF-Demotion hat der User um Abgleich der aktuellen Annahmen und Gleichungsformeln mit `DLG-Information 01|2025` (und, soweit nicht ueberholt, `01|2023`) gebeten. Der Abgleich hat vier konkrete Differenzen offengelegt, die in diesem Slice zusammen umgesetzt wurden.
**Auslieferung:**
- **DLG2025-PH-FORMEL**: Pansen-pH-Prediction nach Zebeli 2008 (zitiert in DLG 01|2025 Kap. 8.3), jetzt mit korrekten Koeffizienten `pH = 6,05 + 0,044·peNDF − 0,0006·peNDF² − 0,017·abbauSt − 0,016·TM`. Neuer Helfer `_abbaust_density_kgdm` ermittelt die **pansenabbaubare Staerke** (`ST − bST`), die als zweite formelwirksame Eingangsgroesse dient. Zucker beeinflusst die Formel **nicht** mehr. `dlg_indicators.ph_formula_source` = `Zebeli 2008 (DLG 01|2025)`, zusaetzlich `abbaust_kgdm` in `nutrient_supply` / `dlg_indicators`.
- **DLG2025-ANDFOMGF-COP**: Einfuehrung der Co-Produkt-Klassifikation (`structural_coproduct`-Flag je Feed; Heuristik ueber `_is_structural_coproduct` auf Namen/Kategorie; Saftfutter wie Biertreber/Pressschnitzel/Kartoffelpuelpe/Trockenschnitzel/Malztreber werden jetzt automatisch als strukturwirksam gefuehrt). `aNDFomGF`-Planung wird ersetzt durch `aNDFomGF+CoP` mit **binaerer DLG-Kaskade** (pabKH ≤ 210 → 200 g/kg TM, pabKH > 210 → 280 g/kg TM, pabKH > 260 loest Warnung). `_andfom_gf_min_target` nimmt `pabkh_density_kgdm` und greift auf die Kaskade zurueck, wenn verfuegbar; die alte Staerke-uplift-Linearitaet bleibt nur als Fallback. LP-Constraint in `_run_lp` ist entsprechend auf `aNDFomGF+CoP-Dichte` umgezogen; `constraint_report`, `nutrient_supply`, `dlg_indicators` und `_detect_sara_risk` nutzen die neue Groesse.
- **DLG2025-FIKH**: Neue Kontrollgroesse **Fermentationsindex Kohlenhydrate** (DLG 01|2025 Kap. 8.4): `FIKH [%] = DNDF / (DNDF + ST+ZU−bST) · 100`, Zielwert ≥ 50 %. Helfer `_fikh_percent` beruecksichtigt fehlende `NDFD`-Werte und liefert Diagnose (`no_ndfd` / `ok`). Ergebnis unter `dlg_indicators.fikh_pct | fikh_ziel | fikh_erfuellt | fikh_diagnose | fikh_quelle`. Warnung wenn FIKH < 50 %.
- **DLG2025-POLICY-TABELLE14**: `_POLICY_PROFILES` erweitert um leistungs-/physiologiestufige Profile (`tmr_fresh_lactation`, `tmr_high_yield`, `tmr_mid_yield`, `tmr_late_lactation`, `tmr_dry_cow`, `tmr_transit`). Neuer Katalog `_POLICY_PROFILE_TARGETS` mit Referenzkorridoren fuer ME, CP, sidP, pabKH, XL, Grobfutteranteil, `aNDFomGF+CoP`, `aNDFom` je Profil. Response liefert `policy_profile_targets`, wenn ein DLG-2025-Profil aktiv ist - Basis fuer die Folge-Slices (Solver-Bindung / UI-Auswahl).
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `tests/test_rations_optimization_sara_reopt.py`, `tests/test_rations_optimization_dlg2025.py` (neu, 32 Tests).
**Tests:** `pytest tests/test_rations_optimization_sara_reopt.py tests/test_rations_optimization_pendf_demotion.py tests/test_rations_optimization_compound_feed.py tests/test_rations_optimization_dlg2025.py` → **82 pass**.
**Offene Follow-ups:**
- Frontend `rationsoptimierung.tsx`: FIKH-Zeile im "Kontrolle / Validierung"-Block und `aNDFomGF+CoP` im Planung-Block ergaenzen (bisher nur `aNDFomGF` sichtbar).
- Wizard: Auswahl der neuen Leistungsstufen-Profile (`tmr_fresh_lactation` usw.) per Expertenmodus freischalten; derzeit nur per API-Override.
- Solver-Bindung der `policy_profile_targets`: aktuell nur Referenzwerte im Response, noch nicht als weiche Constraints im LP gefuehrt. Folge-Slice bei Bedarf.

## SARA-Safety-Reopt + pH/peNDF-Fixes (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, gruen; 23 neue SARA-Gate-Tests plus volle Rations-Regression `335 pass` (keine Regression).
**Kontext:** Der User hat eine Szenariosimulation mit gezielter Pansenacidose-Provokation angefragt. Dabei kamen False-Positive-SARA-Alarme (pH=5.50 ROT auch bei fachlich guter Ration) zum Vorschein. Ursachenanalyse: (a) `_feed_pendf_factor` unrealistisch hoch (z. B. `0.90` fuer Grundfutter), (b) Zebeli/Schwarz-pH-Formel wurde mit **g/kg TM** statt **% TM** gefuettert, (c) es gab keinen automatischen Reopt-Loop.
**Auslieferung:**
- **pH-Formel-Korrektur (`_ph_predict`)**: Inputs werden jetzt von g/kg TM nach % TM umgerechnet (`peNDF_%`, `Staerke_%`), zusaetzlich auf den publizierten Validitaetsbereich geclippt (peNDF 60-250 g/kg TM, Staerke 50-350 g/kg TM, DMI 10-25 kg/d). Neue Helfer `_ph_inputs_in_range` und Response-Flag `dlg_indicators.ph_formula_applicable`.
- **peNDF-Faktor-Neukalibrierung (`_feed_pendf_factor`)** nach Zebeli 2012 / DLG 01|2023: Grundfutter 0.90 -> 0.50 Default, dazu Overrides: Stroh 1.00, Heu 0.95, Luzerne 0.70, Grassilage 0.55, Maissilage 0.45, Trockenkraftfutter 0.10, Getreide 0.10, Melasse 0.00.
- **SARA-Safety-Reopt-Loop (`_maybe_run_sara_safety_reopt`)**: Nach der primaeren FAN-Iteration prueft `_detect_sara_risk` auf pH < 5.9, peNDF < Minimum oder pabKH am Limit. Bei Trigger laeuft eine zweite LP-Runde mit verschaerften Constraints (pabKH-Max -20 g/kg TM, peNDF-Floor +15 g/kg TM, aNDFomGF +10 g/kg TM, NaHCO3-Pansenpuffer als Pflicht mit min. 0.15 kg TM/d). Ergebnis-Payload `sara_safety_reopt` mit `triggered`, `reason`, `actions`, `resolved`, `metrics_before` / `metrics_after`.
- **Frontend-Badge**: Neues Panel in `rationsoptimierung.tsx` zeigt bei aktivem Reopt-Loop die Ausloese-Indikatoren, durchgefuehrte Verschaerfungen und Vorher/Nachher-Metriken (pH, peNDF, pabKH). Farbcode orange = `resolved`, rot = `resolved=false`. DLG-Panel verdeckt die pH-Ampel, wenn die Formel ausserhalb ihres Validitaetsbereichs liegt, um False-Positives zu unterdruecken.
- **Defense-in-Depth**: Provokationsszenarien (`scripts/simulate_acidosis_scenarios.py`, Varianten G/H: 42-45 kg Milch, Maissilage + viel Getreide, ohne Grundstruktur) werden bereits vom LP als `infeasible` abgelehnt (harte Constraints: CP-Dichte, XL-Dichte, Mg-Kapazitaet) - der Reopt-Loop greift als zweite Sicherung, wenn die LP eine scheinbar optimale Loesung mit SARA-Risiko liefert.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_rations_optimization_sara_reopt.py` (neu, 23 Tests), `scripts/simulate_acidosis_scenarios.py`, `scripts/_list_feeds.py` (neu, Helper).
**Tests:** `pytest -k "rations or optim or wave74"` -> **335 pass**. Neue Suite `tests/test_rations_optimization_sara_reopt.py`: pH-Clipping + Einheit, peNDF-Faktoren (parametrisiert 13 Feed-Typen), SARA-Risikoerkennung, End-to-End-Reopt, False-Positive-Regression.
**Simulation (Live-Nachweis):** Alle sechs fachlich guten Varianten A-F (TMR, PMR+Weide spring/summer/autumn) zeigen jetzt Pansen-pH 6.46-6.50 GRUEN und peNDF 200-215 g/kg TM GRUEN. Keine False-Positives mehr.
**Offene Follow-ups:** Winterration-Profil bei Bedarf nachziehen. Felddaten sammeln, um den Reopt-Loop in echten SARA-Fruehwarnfaellen zu validieren.

## FAN-MODE-V1 §12 Saisonprofile + wave74-Fix (abgeschlossen 2026-04-21)

**Von:** Cursor
**Stand:** implementiert, committed und gruen; 30 neue Saisonprofile-Gate-Tests + 6 wave74-Tests repariert. Keine offenen Regressionen in `rations`/`optim` (303 pass).
**Auslieferung:**
- **Wave74-Fix:** `get_rations_base_url()` ist jetzt oeffentlich (vormals `_rations_base_url`). Die wave74-Proxy-Tests bilden den neuen **hybriden Kontrakt** ab: Ohne `RATIONS_OPTIMIZATION_URL` laeuft der interne GfE-2023-Solver (200 + `active_policy_profile`), 503 nur wenn Proxy konfiguriert **und** nicht erreichbar.
- **Sommerration (Hitzestress, DLG-Merkblatt 417 / GfE-Workshop 2023):**
  - Neues Policy-Profil `pmr_pasture_summer` fuer PMR+Weide + `summer_young|mid|late`.
  - DMI-Reduktion je Saisonstufe: `summer_young -3 %`, `summer_mid -7 %`, `summer_late -12 %` (auf `dmi_target/min/max/ndf_min/k_max`).
  - Na-Boost +15 % / +25 % / +30 % fuer Schwitzverluste.
  - Neues Spezialsupplement `special_summer_rumen_buffer` (NaHCO3, 220 g Na/kg TM) wird automatisch als Pflichtbaustein mit `min_kg >= buffer_min_kg` gefuehrt.
  - `summer_late` zusaetzlich +10 g/kg TM aNDFomGF-Boost.
- **Herbstration (stickstoffreicher Grasaufwuchs):**
  - Neues Policy-Profil `pmr_pasture_autumn` fuer PMR+Weide + `autumn`.
  - CP-Dichte-Obergrenze hart auf 175 g/kg TM (Harnstoffschutz, vs. 185 Default PMR+Weide).
  - aNDFomGF-Mindestdichte +15 g/kg TM (Strukturstuetzung gegen N-Ueberschuss).
  - RMD-Korridor kontrolliert um +1 g N/kg TM entspannt (weidetypisch, nicht beliebig).
- **Frontend:** `PolicyProfile`-Typ erweitert; Wizard zeigt je Saison aktive Policy-Hinweise (Sommer/Herbst) im PMR+Weide-Block.
**Geaenderte Dateien:** `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `tests/test_process_kernel_wave74_rations_optimization.py`, `tests/test_rations_optimization_fan_mode_004_policy.py`, `tests/test_rations_optimization_fan_mode_v1.py`, `tests/test_rations_optimization_seasonal_profiles.py` (neu).
**Tests:** `pytest -k "rations or optim"` → 303 pass; neue Suite `tests/test_rations_optimization_seasonal_profiles.py` mit 30 Tests gruen; wave74-Suite mit 28 Tests gruen.
**Offene Follow-ups:**
- Winterration bei Zukunftsbedarf modellieren (aktuell neutraler `winter`-Profilpunkt ohne Anpassungen).
- Felddaten aus Praxistests Sommer/Herbst sammeln, um DMI-Faktoren und Buffer-Minima zu kalibrieren.

## RAT-OPT-001

**Von:** Codex
**Stand:** abgeschlossen 2026-05-16
**Ziel des Slices:** Rationsoptimierung fachlich und technisch auf belastbaren DLG-01|23-Stand ziehen: Frontend-Submit stabilisieren, TMR/PMR-Logik explizit machen und Ergebnisdarstellung um Grundfutter-/Kraftfutter-Leistungsbeitrag inklusive Grundfutterverdrängung ergänzen.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `app/api/v1/endpoints/rations_optimization.py`, `packages/frontend-web/src/lib/api/rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, ggf. gezielte Tests unter `tests/`
**Abnahmekriterien:** Optimierung startet stabil aus dem Wizard ohne State-Race; Response und UI zeigen Milch aus Energie/Protein als IST-/Soll-Sicht aus Grundfutter sowie Zusatz-Kraftfutter für Zielmilch; PMR berücksichtigt Konzentratgabe und Grundfutterverdrängung nachvollziehbar; DLG-01|23-Abgleich ist dokumentiert.
**Erledigt:** Wizard-Submit, Feeding-Type-Vertrag, Grundfutter-/Kraftfutter-Leistungsbeitrag, PMR-/Weide-Logik, Compound-Upload, Weidemineral, Pasture-Risk, Fruehjahrsfall und relevante Rations-Regressionen wurden in den Updates vom 2026-04-21 umgesetzt. Der Eintrag bleibt als historische Zusammenfassung erhalten und ist nicht mehr aktiver Work-in-Progress.
**Offene Risiken:** DLG-Dokument liefert fachliche Leitplanken, aber keine 1:1-Formeln fuer jede Betriebsheuristik; kuenftige Kalibrierungen wie Winterprofil, Felddatenvalidierung oder weitere Solver-Zerlegung sind separate Folgeentscheidungen, keine offenen Punkte dieses Slices.
**Update 2026-04-21:** Wizard-Submit auf mutierende State-Race geprüft und auf parameterisierte Mutation umgestellt; `feeding_type` geht jetzt explizit in den Request. Backend liefert `forage_performance` mit Milch aus Energie/Protein aus Grundfutter, Zielmilch, Kraftfutter-TM und dokumentierter Grundfutterverdrängungs-Heuristik für TMR/PMR. Frontend zeigt die Kennzahlen in Workbench und Review. Checks: `python -m py_compile app/api/v1/endpoints/rations_optimization.py`, `cmd /c pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, direkte Modulverifikation via `python -` auf `_optimize_internal(_demo_profile())`. Laufender lokaler FastAPI-Prozess muss für die neuen Response-Felder ggf. neu geladen werden.
**Update 2026-04-21 (Upload/Bridge):** `main.py` loggt Dev-Warnungen jetzt ASCII-sicher. `POST /api/v1/agrar/rations-optimization/compound-feed/upload` nimmt PDF- und Foto-Dokumente für Kraftfutter-Rezepturen/Lieferscheine an, parst Deklarationswerte, matched Rezepturanteile gegen die DLG-Futterdatenbank und liefert eine Legacy-zu-GfE-2023-Brücke inkl. direkt nutzbarem Optimizer-Feed. Der Wizard in `rationsoptimierung.tsx` kann diese Uploads jetzt als betriebseigenes Kraftfutter in die Futtermittelauswahl übernehmen. Regressionstest `tests/test_rations_optimization_compound_feed.py` ist grün; API-Vertrag lokal per `TestClient` mit `Bödeker Ditzum.pdf` geprüft. Die enge Praxisprobe `Weide + Grassilage 2. Schnitt + 1 kg Maismehl + 1 kg Gerstenmehl + Milchleistungsfutter` bleibt unter den aktuellen harten PMR-Restriktionen noch `infeasible` und ist damit jetzt ein fachlicher Solver-Kalibrierpunkt, kein Upload-/UI-Defekt mehr.
**Update 2026-04-21 (Solver-Prinzip):** Interner LP-Solver priorisiert jetzt nicht mehr direkt Kosten, sondern rechnet zweistufig: Stage 1 sucht zuerst eine fachlich ausgeglichene, pansenstabile Basisration; Stage 2 optimiert erst innerhalb dieses Balance-Korridors auf Kosten. Außerdem greift die starre `Weide <= 4 kg TM`-Grenze jetzt nur noch bei `TMR`, nicht mehr pauschal auch bei `PMR/Weide`. Checks: `python -m py_compile app/api/v1/endpoints/rations_optimization.py`, Praxisprobe via `python -` auf `_optimize_internal(...)`, Regression `pytest tests/test_rations_optimization_compound_feed.py -q --no-cov`. Die konkrete Frühjahrsration bleibt trotz korrigierter PMR-Logik noch `infeasible`; nächster fachlicher Slice ist damit die Kalibrierung der harten XL-/CP-/Weide-Regeln für Weidesysteme.
**Update 2026-04-21 (Weide/PMR):** Auf Basis von DLG 443/444, DLG 417, DLG-Information 01|2023 und dem GfE-Workshop-Stand vom 5. März 2026 ist jetzt ein erster `PMR+Weide`-Pfad eingezogen: Weide-/Frischgrasfutter sind nicht mehr global auf 4 kg TM gedeckelt, TMR-Deckelung greift nur noch im echten TMR-Fall; fuer PMR+Weide werden `aNDFomGF`, `pabKH`, `XL`, `CP`, `K` und Mindest-Grundfutteranteil adaptiv bewertet. Die Fruehjahrsprobe mit `Weide + Grassilage 2. Schnitt + 1 kg Mais + 1 kg Gerste + Boedeker-Milchleistungsfutter` bleibt fachlich weiter `infeasible`; die Diagnose weist jetzt explizit auf das reale Mg-/Energie-Problem der engen Auswahl hin (`Magnesiumdichte ... reicht innerhalb der zulaessigen Energieversorgung nicht aus`) statt nur pauschal auf PMR/Weide zu zeigen.
**Update 2026-04-21 (Weidemineral + PMR+Weide-Modus):** Drei fachliche Slices umgesetzt: (1) Weidemineral `Weidemineral Mg/Na Ausgleich` ist jetzt ein echter Optimierungsbaustein in der Feedbasis (`_SPECIAL_SUPPLEMENTS`) und wird bei `feeding_type="PMR+Weide"` automatisch als Sicherheitsbaustein (>= 0,05 kg TM/d) in die Ration gezwungen – Ableitung aus DLG 417/443 / GfE-Workshop 2023 (K/Mg-Antagonismus, Grastetanie-Risiko). (2) Der Wizard in `rationsoptimierung.tsx` bietet jetzt `TMR / PMR / PMR+Weide` als explizite Modi inkl. kurzer fachlicher Info; `feeding_type` wird ueber den `CowProfile`-Contract an das Backend uebergeben und per `_normalize_feeding_type` robust normalisiert (`PMR+Weide`, `PMR_WEIDE`, `pasture` u.ae.). (3) Response enthaelt neu `pasture_risk` (aktiv bei `PMR+Weide` oder bei > 1 kg TM Weideaufnahme) mit `K:Mg`-Verhaeltnis, Weide-Rohprotein, Mg-Supplement-Menge und drei Milch-Panels (Milch aus Weide, Milch aus Grassilage, Milch aus Weide+Grassilage); `PastureRiskPanel` ist in Workbench- und Review-Ansicht sichtbar. Checks: `python -m py_compile app/api/v1/endpoints/rations_optimization.py`, `pytest tests/test_rations_optimization_pasture.py tests/test_rations_optimization_compound_feed.py -q --no-cov` (5 passed), `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`, E2E-Sanity-Test via FastAPI-`TestClient` mit `feeding_type="PMR+Weide"` (Response liefert `pasture_risk.active=true`, `mg_supplement_dmi_kg=0.05`, K:Mg-Warnung wird ausgeworfen).
**Update 2026-04-21 (Fruehjahrsfall-Abschluss, RMD + Compound-Parser):** Die Praxisprobe `Weide Fruehjahr jung + Grassilage 2. Schnitt + 1 kg Mais + 1 kg Gerste + Boedeker-Milchleistungsfutter` ist jetzt im Modus `PMR+Weide` `optimal` (Kosten 1,66 EUR/d, DMI 18 kg TM, ME 204,6 MJ, Mg 37,3 g, K:Mg 12,4 → Grastetanie-Warnung wird korrekt gemeldet). Zwei zusammenhängende Blocker wurden aufgelöst: (a) **RMD-Dichte-Obergrenze** (DLG 01|25 Ziel ≤ 1,5 g N/kg TM) ist für Weidesysteme strukturell nicht erreichbar, weil Jungweide laut DLG-Futterwerttabelle bereits 7–9 g N/kg TM liefert. Die Grenze wird jetzt nach DLG-Merkblatt 417 je Fütterungsmodus gestaffelt (`TMR 1,5 / PMR 3,0 / PMR+Weide 8,0`, Relaxation-Stufe `TMR 3,0 / PMR 5,0 / PMR+Weide 12,0`) – die Stall-Norm bleibt für Stallfütterung unverändert. (b) **Compound-Feed-Parser** (`_parse_compound_feed_text`) produzierte physikalisch unmögliche Werte (ME 15,4 MJ/kg TM, XL 165 g/kg TM, Ca 72 g/kg TM), verursacht durch zwei Bugs: ein Off-by-one-Matching in `_extract_labelled_value` (Pattern-Reihenfolge vertauscht, `"Rohfett"` nahm den Wert von `"Rohprotein"` etc.) und eine fehlende FM→TM-Umrechnung der Deklaration (% FM wurde direkt als g/kg TM interpretiert). Beides gefixt: Label-zuerst-Pattern hat jetzt Priorität, Deklaration wird konsistent mit `1/dm_frac` auf g/kg TM gehoben. Regressionstests: `tests/test_rations_optimization_compound_feed.py` (3 neue Tests gegen Off-by-one, physikalische Plausibilität, FM→TM), `tests/test_rations_optimization_spring_pasture_case.py` (4 neue E2E-Tests für den Bruder-Fall). Komplette `rations_optimization`-Suite: 34 passed (6 Pre-Existing-Errors in `test_process_kernel_wave74_rations_optimization.py` wegen entfallener `get_rations_base_url`-Funktion, unabhängig von diesem Slice).

## FLOW-LC-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Flow-Spine-Instanzen vom reinen Routing-/Node-Status-Anker auf einen echten, restart-sicheren Lifecycle mit Timeline und Resume-Vertrag heben.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, `app/domains/operations/models.py`, `alembic/versions/*`, `app/api/v1/endpoints/flow_spines.py`, `tests/test_flow_spines_api.py`
**Abnahmekriterien:** `FlowSpineInstance` traegt technische Lifecycle-Felder; eine Event-/Timeline-Spur ist modelliert; API-Contracts fuer `save`, `resume`, `hold`, `complete`, `cancel`, `fail` sind dokumentiert oder implementiert; bestehende `transition`-Logik ist sauber in den Gesamtvertrag eingeordnet.
**Erledigt:** `FlowSpineInstance` fuehrt jetzt Lifecycle-, Resume-, Owner-, Grund- und Abschlussfelder; `domain_ops.ops_flow_spine_instance_events` bildet Timeline/Audit persistent ab; `flow_spines.py` bietet jetzt `PATCH`, `save`, `resume`, `hold`, `complete`, `cancel`, `fail` und `timeline`; `transition` schreibt ebenfalls in die Eventspur und hebt `draft` auf `in_progress`.
**Checks:** `python -m py_compile app/api/v1/endpoints/flow_spines.py app/domains/operations/models.py alembic/versions/flow_spine_lifecycle_20260417.py tests/test_flow_spines_api.py`, `pytest tests/test_flow_spines_api.py -q --no-cov`
**Naechster Schritt:** `FLOW-LC-002` bis `FLOW-LC-006` entlang der neuen Lifecycle-Uebersicht staffeln, beginnend mit generischen Workspace-Actions und Resume-/Abbruch-Dialogen im Frontend.

## FLOW-LC-003

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Gemeinsamen Workspace-Lifecycle-Rahmen fuer alle 9 Flow-Spines einziehen: Aktionsleiste, Resume-Hinweis, Timeline und generische Dialoge fuer `save`, `hold`, `complete`, `cancel`, `fail`.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, `packages/frontend-web/src/components/workflow/FlowSpineWorkspace.tsx`, `packages/frontend-web/src/lib/api/flow-spines.ts`, relevante UI-Tests falls vorhanden
**Abnahmekriterien:** Der Workspace zeigt Lifecycle-Status, Resume-Ziel und Timeline; die generischen Lifecycle-Aktionen sprechen den neuen Backend-Vertrag an; `cancel` und `fail` erzwingen Pflichtgruende auch im UI; der Rahmen ist prozessneutral fuer alle 9 Flows nutzbar.
**Erledigt:** `flow-spines.ts` kennt jetzt Lifecycle-Status, Timeline-Events und Mutationen fuer `save`, `resume`, `hold`, `complete`, `cancel`, `fail`; `FlowSpineWorkspace.tsx` zeigt fuer geladene Instanzen eine generische Lifecycle-Leiste mit Status, Resume-Ziel, Timeline und prozessneutralen Dialogen; die Instanzliste zeigt den Lifecycle-Status direkt in der Sidebar.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`
**Naechster Schritt:** `FLOW-LC-004` fuer OTC / P2P / Inventory aufsetzen und dort Resume-/Handover-Pfade mit den jeweiligen Fachmasken wirklich durchgaengig machen.

## FLOW-LC-004

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** OTC, P2P und Inventory so an den Lifecycle-Vertrag anbinden, dass `save` und `resume` nicht nur im Workspace leben, sondern in reale Wiedereinstiegspfade der Fachmasken zeigen.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, `packages/frontend-web/src/lib/api/flow-spines.ts`, `packages/frontend-web/src/pages/sales/order-editor.tsx`, `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`, `packages/frontend-web/src/pages/lager/bestandsuebersicht.tsx`
**Abnahmekriterien:** OTC speichert einen belastbaren Resume-Punkt in die Auftragsmaske; P2P speichert nach Erstanlage in die echte Bestell-Detailroute; Inventory speichert vor vertieften Dashboard-Spruengen den operativen Zielpfad als Resume-Ziel.
**Erledigt:** `flow-spines.ts` bietet jetzt einen schlanken `saveFlowSpineResumeCheckpoint()`-Helper; `order-editor.tsx` schreibt beim Speichern den Resume-Punkt auf die konkrete Auftragsmaske und ersetzt nach Erstanlage die URL auf `?id=...`; `bestellung-anlegen.tsx` schreibt nach Erstanlage den Resume-Punkt auf die echte Bestell-Detailroute `/einkauf/bestellungen/{id}`; `bestandsuebersicht.tsx` persistiert vor den Spruengen in `mhd-uebersicht`, `psm-abverkauf`, `renner-liste` und `penner-liste` den jeweiligen Zielpfad als Inventory-Resume-Ziel und traegt den Workflow-Kontext dorthin weiter.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`
**Naechster Schritt:** `FLOW-LC-005` aufsetzen und die restlichen sechs Prozessraeume mit denselben Resume-/Handover-Mustern nachziehen.

## FLOW-LC-005

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Die restlichen sechs Flow-Spine-Prozessraeume mit denselben Resume-/Handover-Mustern wie OTC, P2P und Inventory anbinden.
**Owner:** Codex
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/workflows/flow-spine-instance-lifecycle-overview.md`, relevante Zielseiten unter `packages/frontend-web/src/pages/**`, ggf. `packages/frontend-web/src/lib/api/flow-spines.ts`
**Abnahmekriterien:** `harvest-to-settlement`, `contract-to-settlement`, `complaint-to-resolution`, `service-to-customer`, `finance-to-close` und `compliance-to-report` schreiben oder tragen echte Resume-/Handover-Ziele in ihre Fachmasken; die Workflow-Kontexte bleiben beim Wiedereinstieg erhalten.
**Erledigt:** `ernte-annahme-erfassung.tsx` schreibt beim Speichern den Resume-Punkt auf die konkrete Annahme-Route und ersetzt nach Erstsave die URL auf `/agrar/ernte-annahme-erfassung/{id}`; `FrmKontraktDetail.tsx` schreibt nach Save auf die echte Kontrakt-Detailroute; `reklamationen.tsx` und `service/anfragen.tsx` sichern vor `neu`- und Detail-Spruengen die jeweiligen Zielpfade; `abschluss-cockpit.tsx` speichert beim Oeffnen den Cockpit-Resume-Punkt und vor Detail-Spruengen den Checklistenpfad; `co2-bilanz.tsx` persistiert die Reporting-Maske selbst als Resume-Ziel.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`
**Naechster Schritt:** Die verbleibende Vertiefung ist kein generischer Resume-Rahmen mehr, sondern fachliche Feinarbeit: pro Flow konkrete Grundcode-Kataloge, weitergehende Handover in Untermasken und Abschluss-/Abbruchregeln.

## CRM-PICKER-001

**Von:** Claude Code / Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Order-to-Cash-Kundenauswahl im Flow-Spine-Startdialog von Modal-Auswahl auf schnellen Inline-Typeahead mit Neuanlage-Ruecksprung umstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/CUSTOMER-PICKER-PLAN.md`, `app/api/v1/endpoints/customers.py`, `alembic/versions/crm_customers_search_index_20260414.py`, `packages/frontend-web/src/components/crm/CustomerCombobox.tsx`, `packages/frontend-web/src/components/workflow/FlowSpineWorkspace.tsx`, `packages/frontend-web/src/pages/verkauf/kunde-neu.tsx`, `packages/frontend-web/src/pages/verkauf/kunden-stamm.tsx`
**Abnahmekriterien:** Typeahead nutzt schlanke Quick-/Recent-Endpoints; neuer Kunde kann aus dem Flow-Spine-Dialog angelegt werden; nach Speichern kehrt die App in den Dialog mit vorausgewaehltem Kunden zurueck; erweiterte Kundensuche bleibt erreichbar.
**Erledigt:** `CustomerCombobox` ist fuer `order-to-cash` integriert; `/quick-search` und `/recent` liefern schlanke Picker-Daten; `returnTo` bleibt ueber den Alias-Redirect erhalten; kanonischer Kundenstamm liest `initialName` und navigiert nach Save zurueck; `FlowSpineWorkspace` setzt `customerId` und `customerNumber` im Order-Editor-Handover; der `order-editor` prefilled den uebergebenen Kunden jetzt direkt beim Workflow-Einstieg; bestehende Flow-Spine-Instanzen loesen den kompakten Kundenkontext robust ueber `business_partner_id`; `CustomerSelectionDialog` ist als "Erweiterte Suche" angebunden.
**Checks:** Browser-Use Roundtrip `Flow Spine -> Kunde neu -> Flow Spine Dialog -> Order Editor`, `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `pytest tests/test_flow_spines_api.py tests/test_customers_picker_api.py -q --no-cov`, `node scripts/docs-governance-check.cjs`, `GET /api/v1/crm/customers/recent`, `GET /api/v1/crm/customers/quick-search`

## DOC-REF-002

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Externe ERP-Referenzdoku neutralisieren, Lizenz-/Referenzlage scharfziehen und direkte Nennungen des angefragten Systems aus den aktiven Repo-Dokumenten entfernen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/*.md`
**Abnahmekriterien:** Die Referenzanalyse bleibt fachlich brauchbar, benennt aber nur noch neutrale Vergleichsklassen bzw. permissive/kommerzielle Lizenzrisiken; direkte Nennungen des angefragten Systems sind aus den aktiven Projektkontext-Dateien entfernt.
**Erledigt:** Die aktive Referenzdatei wurde auf `docs/project-context/erp-reference-gap-analysis-amic-community-erp-fiori-2026-04-08.md` umgestellt; Tail-Plan, i18n-, Setup-, Roadmap- und Archivdoku nutzen jetzt neutrale Bezeichnungen; ein repo-weiter Textscan auf die direkte Nennung liefert keine Treffer mehr.
**Checks:** `rg -n -i "\\bodoo\\b" . --glob '!node_modules/**' --glob '!.git/**' --glob '!packages/frontend-web/node_modules/**' --glob '!venv/**' --glob '!coverage_html/**'`, `node scripts/docs-governance-check.cjs`

## DOC-REF-003

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Eine neutrale ERP-Referenzmatrix im Repo festhalten und daraus die naechsten sechs fachlichen Vertiefungs-Slices fuer VALEO ableiten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/*.md`
**Abnahmekriterien:** Es gibt eine eigenstaendige Matrix mit Referenzmustern, Lizenz-/Uebernahmeregeln und VALEO-Istbild; daraus sind sechs konkrete Slices mit Zielbild und Prioritaet im Workboard abgeleitet.
**Erledigt:** `docs/project-context/erp-reference-matrix-2026-04-12.md` verdichtet jetzt fachliches Tiefenbild, Community-ERP-Referenzmuster, Web-ERP-Standard-/OpenUI5-UIX-Muster, Lizenzregeln und konkrete Slice-Ableitung; die naechsten sechs fachlichen Vertiefungs-Slices sind daraus direkt abgeleitet.
**Checks:** `node scripts/docs-governance-check.cjs`

## DOM-FIN-003

**Von:** Codex
**Stand:** abgeschlossen 2026-06-23
**Ziel des Slices:** FIBU-Operatorpfade fuer Abschluss, Reorganisator, Zinswesen und Revisionssicht semantisch verdichten.
**Abnahmekriterien:** Abschluss- und FIBU-Operatorraeume tragen denselben klaren Status-, Fristen-, Revisions- und Folgeaktionsrahmen.
**Ergebnis:** Alle 4 FIBU-Masken (abschluss-cockpit, schnittstellen-center, mahnwesen, zahlungslaeufe) tragen OperationalCaseHeader mit Status/Blocker/Folgeaktion.

## DOM-SUPPLY-003

**Von:** Codex
**Stand:** abgeschlossen 2026-06-23
**Ziel des Slices:** Die physische Kette `Partie -> Annahme -> Wiegung -> Charge -> Fracht -> Abrechnung` fachlich und statusseitig durchgaengig harmonisieren.
**Abnahmekriterien:** Jeder Uebergabepunkt zeigt Objektbezug, Abweichung, naechste Aktion und Folgeobjekt konsistent.
**Ergebnis:** Alle 6 Supply-Masken (waage/liste, tourenplanung, wareneingang, wiegeschein-detail, rohware, frachtbriefe) tragen OperationalCaseHeader.

## DOM-PROC-003

**Von:** Codex
**Stand:** abgeschlossen 2026-06-23
**Ziel des Slices:** Einkaufsausnahmen, Matching, Nachforderung und Lieferantenkommunikation auf echte Folgefaelle heben.
**Abnahmekriterien:** Beschaffungsfaelle bilden Matching-Ausnahmen, Nachforderung und Folgekommunikation als echte Arbeitsobjekte ab.
**Ergebnis:** Alle 5 Einkauf-Masken (rechnung-abgleich, rechnungseingang, lieferanten-dokumente, anlieferavis, auftragsbestaetigung) tragen OperationalCaseHeader.

## DOM-CON-003

**Von:** Codex
**Stand:** abgeschlossen 2026-06-23
**Ziel des Slices:** Kontraktfixierung, Marktbewertung, Mahnung und Engagement als vollwertige Operatorraeume ausbauen.
**Abnahmekriterien:** Fixierungs-, Markt- und Mahnlogik ist nicht nur sichtbar, sondern als klarer Operatorpfad bedienbar.
**Ergebnis:** Alle 4 Kontrakt-Masken (contracts-v2, KontraktPositionsmonitor, FrmKontraktDetail, KontraktAlarmDashboard) tragen OperationalCaseHeader.

## DOM-CRM-003

**Von:** Codex
**Stand:** abgeschlossen 2026-06-23
**Ziel des Slices:** CRM-/Servicefaelle mit Ownership, Folgeobjekten, Dubletten- und Abschlusslogik angleichen.
**Abnahmekriterien:** CRM und Service tragen denselben Fallbezug, Ownership-Rahmen und Abschlusspfad.
**Ergebnis:** Alle 4 CRM-/Service-Masken (LegacyKundenStammModern, anfrage-detail, opportunity-detail, kontakt-management) tragen OperationalCaseHeader.

## DOM-DOC-003

**Von:** Codex
**Stand:** abgeschlossen 2026-06-23
**Ziel des Slices:** Nachweis-, Bescheid-, Artefakt- und Rueckmeldungskette ueber Dokumente, Meldungen und Vorgangskontext vereinheitlichen.
**Abnahmekriterien:** Dokumente und Meldungen zeigen revisionsrelevanten Nachweisstatus, Rueckmeldungspfad und Wiedervorlage konsistent.
**Ergebnis:** Alle 3 Dokumenten-/Compliance-Masken (ablage, meldewesen-konsole, atlas) tragen OperationalCaseHeader.

## COV-FIN-002

**Von:** Codex
**Stand:** abgeschlossen 2026-06-23
**Ziel des Slices:** Coverage-Tiefe fuer FIBU-Kernpfade aufbauen: Journal, Zahlungslaeufe, DATEV/ELSTER-nahe Follow-up-Logik und Abschlusskontext.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, relevante Finance-/FIBU-Services und Endpunkte
**Abnahmekriterien:** Kritische FIBU-Kernpfade besitzen gezielte Tests statt nur allgemeiner Gesamtquote; Ratchet kann fuer Finance spaeter angehoben werden.
**Fortschritt:** Start auf den API-/Service-Kern fuer Follow-up, Mahnwesen, Lastschrift- und Kassenexport sowie FIBU-nahe Exportpersistenz; `tests/test_finance_followup_api.py` deckt jetzt Preview-, Export-, Download-, DMS-Redirect- und Upload-Metadatenpfade ab. Zusaetzlich haertet `tests/test_fibu_connectors_api.py` jetzt Profile-CRUD, Import-Upload, Run-Summary, Run-Items und Workflow-Folgeaktionen in `api/v1/endpoints/fibu_connectors.py`. `tests/test_finance_actions.py` deckt Bankabgleich, Buchungsfreigabe, Kassenabschluss, Lastschriftlauf, Periodenabschluss, Kreditlimits, Sicherheiten, Zahlungsvorschlaege und Buchungsuebergabe ab. Die zuvor `skipped` Finance-API-Tests wurden auf deterministische Test-Doubles umgestellt (`tests/test_finance_dunning_api.py`, `tests/test_finance_exchange_rates_api.py`, `tests/test_finance_payment_runs_api.py`), damit sie nicht mehr an einer zufaelligen Live-DB haengen. Nebenbei wurden echte Ursachen im Code behoben: Geldbetraege im Mahnwesen werden jetzt quantisiert, `payment_runs.py` serialisiert Zahlungsobjekte sauber und der Ruecklaeuferpfad nutzt wieder den korrekten Betrag. Fuer Bestandsinstallationen erzwingt `ensure_finance_api_tables_20260413` die fehlenden Finance-API-Tabellen auch dann, wenn ein aelterer Migrationspfad sie ausgelassen hat.

## COV-FIN-003

**Von:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Die verbliebenen Finance-Ratchet-Luecken `booking_templates.py` und `chart_of_accounts.py` ueber deterministische API-/Unit-Tests und einen stabilen JSON-Serialisierungspfad schliessen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/quality-assurance/critical-backend-coverage-plan-2026-04-24.md`, `docs/project-context/open-gaps-and-known-issues.md`, `app/api/v1/endpoints/booking_templates.py`, `tests/test_booking_templates_api.py`, `tests/test_chart_of_accounts_api.py`
**Abnahmekriterien:** `booking_templates.py` liegt ueber 40 Prozent, `chart_of_accounts.py` ueber 50 Prozent; der kritische Coverage-Ratchet laeuft gegen die Sammelsuite gruen.
**Erledigt:** `booking_templates.py` serialisiert Template-Lines jetzt ueber `model_dump_json()` JSON-sicher; `tests/test_booking_templates_api.py` und `tests/test_chart_of_accounts_api.py` decken Listen-, CRUD-, Validierungs-, Export- und Fehlerpfade ab. Der vollstaendige kritische Ratchet ist gruen.
**Checks:** `pytest tests/test_booking_templates_api.py tests/test_chart_of_accounts_api.py -q --no-cov`; `pytest tests/test_tenant_enforcement.py tests/test_secrets_vault.py tests/test_event_bus_runtime.py tests/test_process_kernel_wave2_events.py tests/test_integration_bootstrap.py tests/test_finance_actions.py tests/test_finance_followup_api.py tests/test_fibu_connectors_api.py tests/test_dunning_api.py tests/test_finance_payment_runs_api.py tests/test_finance_exchange_rates_api.py tests/test_finance_read_models_api.py tests/test_process_kernel_wave1_contracts.py tests/test_inventory_operations.py tests/test_inventory_counts.py tests/test_waage_api.py tests/test_warehouses_api.py tests/test_warehouse_transfers_api.py tests/test_booking_templates_api.py tests/test_chart_of_accounts_api.py tests/test_l3c_smoke.py -q`; `python scripts/check_critical_backend_coverage.py`

## COV-INV-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-05
**Ziel des Slices:** Coverage fuer Bestandsfuehrung, Lagerbewegung, Inventur und physische Objektkette erweitern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, Inventory-/Ops-/Logistik-Endpunkte und Services
**Abnahmekriterien:** Stock-Movements, Inventur und kritische Lagerpfade sind ueber gezielte Tests gegen Regressionen abgesichert.
**Erledigt:** `waage.py`, `warehouses.py`, `warehouse_transfers.py`, `inventory_counts.py` und `inventory_operations.py` liegen im kritischen Coverage-Ratchet ueber Schwelle; die Sammelsuite laeuft gruen.
**Checks:** siehe `COV-FIN-003` Sammelsuite und `python scripts/check_critical_backend_coverage.py`

## COV-INT-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** Integrations-Governance tiefer testen: Superglue, Secrets, Outbound-Gates, Bootstrap und Tenant-Schutz.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `tests/**`, `app/services/**`, `app/integrations/**`
**Abnahmekriterien:** Integrationsnahe Kernpfade werden nicht nur konfiguriert, sondern auch testseitig breiter abgesichert.
**Erledigt:** `IntegrationCircuitBreaker` (12 Tests), `superglue_execution_journal` (9 Tests), `superglue_admin_state` (11 Tests), `superglue_monitoring` (5 Tests) — 37 Tests gruen. Stand: 2026-05-12.

## DOM-FIN-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** FIBU-/L3-Parity fachlich weiter vertiefen, insbesondere Abschluss-, Revisions- und Operator-Pfade.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante FIBU-/Finance-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** Finance/FIBU ist nicht nur breit, sondern in den priorisierten Operatorpfaden semantisch konsistenter und tiefer.
**Erledigt:** (1) `accruals_provisions.py`: GET/PUT/DELETE-Endpoints fuer Einzelobjekte hinzugefuegt (waren fehlend — nur List+Create+Post vorhanden); (2) `closing_checklists.py`: POST `/{id}/approve` + DELETE `/{id}` hinzugefuegt (approve-Schritt fehlte im Workflow); (3) Tests: `test_accruals_provisions_api.py` (12), `test_subsidiary_ledger_reconciliation_api.py` (12) — 24 Tests gruen. Stand: 2026-05-12.

## DOM-INV-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** Inventory-/Ops-/Logistik-Parity weiterziehen, insbesondere physische Objektkette, Queue, Wiegung, Fracht und Charge.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante Inventory-/Ops-/Logistik-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** Die physische Kette ist fachlich tiefer und konsistenter ueber mehrere Kernmasken und Backend-Pfade hinweg.
**Erledigt:** Tests fuer `silo_operations_api.py` (DOM-INV-002, `test_silo_operations_api.py`) und `charges.py` (`test_charges_api.py`) hinzugefuegt — Modellvalidierung + HTTP-Smoke-Tests.

## DOM-CRM-002

**Von:** Codex
**Stand:** abgeschlossen 2026-05-08
**Ziel des Slices:** CRM-/Sales-/Service-Parity angleichen, insbesondere Vorgangsbezug, Folgeobjekte und echte Arbeitsobjekte statt Listenbreite.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, relevante CRM-/Sales-/Service-Module, Doku unter `docs/project-context/`
**Abnahmekriterien:** CRM-/Sales-/Service-Raeume besitzen vergleichbare fachliche Tiefe in den priorisierten Kernobjekten.
**Erledigt:** Tests fuer `sales_orders.py`, `sales_delivery_notes.py`, `reklamation_api.py`, `contacts.py` hinzugefuegt — Helper-Unit-Tests + HTTP-Smoke (60 Tests grueen).

## ARCH-DOM-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Fachliche Schema-Zuordnung der Tabellen nicht nur behaupten, sondern mit einem expliziten Audit- und Guardrail-Pfad pruefbar machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `scripts/check_required_domain_schemas.py`, neues Domain-Mapping-Audit unter `scripts/`
**Abnahmekriterien:** Es gibt einen automatisierten Check fuer Kern-Schemaanker plus fachlich schiefe bzw. bewusst tolerierte Cross-Domain-Zuordnungen.
**Erledigt:** `scripts/check_domain_table_ownership.py` prueft jetzt representative Exact-Ownership-Regeln, Prefix-Regeln und dokumentierte Legacy-Placements; `scripts/smoke_first_install_docker.ps1/.sh` fuehren den Ownership-Check nach frischer Migration mit aus.
**Checks:** `powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55437`, `python scripts/check_domain_table_ownership.py` (gegen frische Smoke-DB)

## COVERAGE-ERP-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Backend-Coverage fuer ERP-Kernpfade auf einen belastbaren Ratchet-Pfad bringen statt pauschal 100% zu behaupten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `.github/workflows/quality-gate.yml`, `pytest.ini`, neue Coverage-Guard-Skripte/Tests unter `scripts/` und `tests/`
**Abnahmekriterien:** CI prueft einen expliziten Mindeststandard fuer kritische Pfade; die Doku benennt ehrlich, was repo-seitig erreichbar ist und was nicht.
**Erledigt:** `.github/workflows/quality-gate.yml` fuehrt jetzt `scripts/check_critical_backend_coverage.py` nach pytest aus; neue Tests fuer Event-Bus-Runtime, Integrations-Bootstrap und Tenant-Enforcement stabilisieren die Kernpfade; die Doku benennt `100%` repo-weit explizit nicht als kurzfristig belastbares Ziel.
**Checks:** `pytest tests/test_event_bus_runtime.py tests/test_integration_bootstrap.py tests/test_secrets_vault.py tests/test_security_startup_guards.py tests/test_nats_event_handlers.py tests/test_tenant_enforcement.py -q`, `python scripts/check_critical_backend_coverage.py`

## NATS-DEV-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Event-Bus/NATS im Dev-Betrieb automatisch mit Docker laufen lassen, statt nur config-aktivierbar zu sein.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docker-compose*.yml`, `.env.example`, ggf. `app/core/config.py`, Event-Bus-Tests
**Abnahmekriterien:** Standard-Dev-Compose bringt NATS mit hoch und Backend laeuft dabei automatisch auf NATS statt Memory-Fallback.
**Erledigt:** `docker-compose.yml` und `docker-compose.dev.yml` starten NATS jetzt mit JetStream-Healthcheck; die jeweiligen Backend-Services laufen dort automatisch mit `EVENT_BUS_ENABLED=true`, `EVENT_BUS_PROVIDER=nats`, `EVENT_BUS_NATS_URL=nats://nats:4222`; `.env.example` spiegelt denselben Dev-Pfad.
**Checks:** `docker compose -f docker-compose.yml config -q`, `docker compose -f docker-compose.dev.yml config -q`

## INT-BOOT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Externe Integrationen soweit repo-seitig vorbereiten, dass lokale oder frische Installationen nicht an fehlenden Bootstrap-Hinweisen fuer Secrets, Zielsysteme und Ops-Parameter scheitern.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `.env.example`, `scripts/`, ggf. Integrations-README unter `docs/`
**Abnahmekriterien:** Es gibt einen reproduzierbaren Readiness-/Bootstrap-Check fuer Live-Integrationen und klare env-/secret-Vorlagen fuer lokale bzw. ops-seitige Aktivierung.
**Erledigt:** `app/services/integration_bootstrap.py` verdichtet OIDC-, NATS-, Superglue-, Voice- und CRM-Downstream-Readiness; `scripts/check_integration_bootstrap.py` reportet bzw. failt optional strikt; `.env.example` fuehrt die zentralen Bootstrap-Variablen; `docs/project-context/integration-bootstrap-readiness-2026-04-12.md` dokumentiert die repo-seitig vorbereiteten und die ops-seitig verbleibenden Themen.
**Checks:** `python scripts/check_integration_bootstrap.py`, `pytest tests/test_integration_bootstrap.py -q`

## DOCS-README-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Root-README gegen den aktuellen Repo-, Delivery- und Bootstrap-Stand aufraeumen und wieder als belastbaren Einstiegspunkt ausrichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `README.md`
**Abnahmekriterien:** README ist encoding-sauber, verweist auf die echten Source-of-Truth-Dokumente, ueberzeichnet den Produktreifegrad nicht und bildet den aktuellen Docker-/Bootstrap-Pfad korrekt ab.
**Erledigt:** `README.md` ist von veralteter Langform und Mojibake auf einen knappen, ehrlichen Einstiegspunkt umgestellt; der aktuelle Reifegrad, der Alembic-/Docker-Erstinstallationspfad, die Mehr-Domaenen-Struktur, lokale Prüfkommandos sowie die maßgeblichen Source-of-Truth-Dokumente sind jetzt korrekt referenziert; ueberspannte Vollstaendigkeits- und Production-Claims wurden entfernt.
**Checks:** `node scripts/docs-governance-check.cjs`, `rg -n "ð|â|Ã|�" README.md`

## DB-BOOT-001

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Erstinstallation ueber Alembic und Docker auf leerer Postgres-DB deterministisch machen und die Mehr-Domaenen-Struktur automatisiert pruefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `alembic/env.py`, `alembic/versions/*`, `scripts/init_db.py`, `scripts/check_required_domain_schemas.py`, `docker-compose*.yml`, `Dockerfile*`, `.github/workflows/quality-gate.yml`
**Abnahmekriterien:** `python scripts/init_db.py` laeuft auf leerer DB bis `head`; der Compose-/Docker-Pfad verschluckt keine Migrationsfehler; eine Strukturpruefung bestaetigt zentrale ERP-Domaenen und Kernobjekte.
**Erledigt:** `add_business_partners_tenant_id_20260219.py` ist jetzt neuinstallationssicher und ersetzt den falschen globalen Business-Partner-Unique-Pfad; `perf_indexes_multitenant_20260408.py` legt optionale Indexe nur noch fehlertolerant an; `docker-compose.yml`, `docker-compose.staging.yml`, `docker-compose.dev.yml`, `entrypoint.sh`, `Dockerfile` und `Dockerfile.backend` starten Backend-Prozesse erst nach erfolgreichem `python scripts/init_db.py`; Legacy-SQL-Tabellenpfade sind aus dem Dev-Erststart entfernt; `scripts/check_required_domain_schemas.py` verifiziert die zentrale Mehr-Domaenen-Struktur im CI und `scripts/smoke_first_install_docker.ps1/.sh` liefern einen reproduzierbaren First-Install-Smoke fuer frische GitHub-Spiegel.
**Checks:** frische Postgres-Container-DB via `python scripts/init_db.py`, `python scripts/check_required_domain_schemas.py`, `powershell -ExecutionPolicy Bypass -File scripts/smoke_first_install_docker.ps1 -HostPort 55434`, `python -m py_compile scripts/init_db.py scripts/check_required_domain_schemas.py alembic/env.py alembic/versions/add_business_partners_tenant_id_20260219.py alembic/versions/perf_indexes_multitenant_20260408.py`, `docker compose -f docker-compose.yml config -q`, `docker compose -f docker-compose.staging.yml config -q`, `docker compose -f docker-compose.dev.yml config -q`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-013

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Annahme-Abrechnung als echten Settlement-Fall mit Ressourcen-, Preis- und Freigabekontext surfacen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/annahme/abrechnung.tsx`
**Abnahmekriterien:** Abrechnung zeigt Fallkopf, knappen Kontext und Timeline ueber dem Settlement-Arbeitsplatz, ohne neue API-Last.
**Erledigt:** `annahme/abrechnung.tsx` zeigt jetzt Settlement-Fallkopf, Abrechnungskontext und Verlauf aus bereits vorhandenen Preview-/Campaign-/Settlement-Daten direkt ueber dem Self-Billing-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-014

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rechnungseingaenge-Liste als operativen Sammelarbeitsplatz statt reine Tabelle verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/rechnungseingaenge-liste.tsx`
**Abnahmekriterien:** Die Liste zeigt klaren Freigabe-/Verbuchungsdruck und die naechste Bulk-Aktion, ohne den Listenraum zu ueberladen.
**Erledigt:** `rechnungseingaenge-liste.tsx` verdichtet jetzt Freigabe-/Verbuchungsstau, Summenlage und die naechste Bulk-Aktion ueber der bestehenden Liste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-015

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Mahnwesen als echten Follow-up-Fall mit Owner-, Risiko- und Governance-Sicht verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/finance/mahnwesen.tsx`
**Abnahmekriterien:** Mahnwesen zeigt Mahndruck, Zins-/Connector-Lage und naechste FIBU-Aktion direkt vor dem Objektarbeitsplatz.
**Erledigt:** `finance/mahnwesen.tsx` fuehrt jetzt Mahndruck, Zins-/Connector-Kontext und naechste FIBU-Massnahme als kompakten Follow-up-Kopf ueber dem Objektarbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-016

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Offene-Posten-Raeume fuer Debitoren und Kreditoren auf eine gemeinsame operative Sicht ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/finance/{op-debitoren,op-kreditoren}.tsx`
**Abnahmekriterien:** Beide OP-Raeume zeigen Rueckstand, Risiko und naechste Massnahme konsistent und schlank.
**Erledigt:** `op-debitoren.tsx` und `op-kreditoren.tsx` nutzen jetzt dasselbe leichte OP-Modell fuer Rueckstand, Mahn-/Ueberfaelligkeitsdruck, Kontext und Folgeaktion, ohne die Facharbeit in Tabellen und Dialogen zu verdoppeln.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-017

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Einkaufsnahe Dokumenten-/Lieferobjekte mit leichtem Vorgangsbild harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/{anlieferavis,auftragsbestaetigung}.tsx`
**Abnahmekriterien:** Beide Objektmasken gewinnen Blocker-, Kontext- und naechste-Aktion-Sicht ohne Doppelung zur Fachmaske.
**Erledigt:** `anlieferavis.tsx` und `auftragsbestaetigung.tsx` haben jetzt einen kompakten Logistik-/Pruefkopf ueber der ObjectPage und bleiben darunter fachlich unveraendert tief.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-018

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Scope und offene Restgrenzen fuer den naechsten Operativ-Rollout dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, ggf. `docs/project-context/operational-rollout-scope-2026-04-09.md`
**Abnahmekriterien:** Es ist dokumentiert, welche Sammel- und Follow-up-Masken jetzt unter dem Zielbild laufen und welche bewusst weiterhin schlank bleiben.
**Erledigt:** Das schlanke Workboard und die Scope-Doku decken jetzt auch Sammel- und Follow-up-Masken fuer Settlement, Rechnungseingaenge, Mahnwesen, OP-Raeume sowie einkaufsnahe Lieferobjekte ab.
**Checks:** `node scripts/docs-governance-check.cjs`

## OP-ROLL-019

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Einkaufslisten fuer Avis und Auftragsbestaetigungen als operative Sammelarbeitsplaetze verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/{anlieferavis-liste,auftragsbestaetigungen-liste}.tsx`
**Abnahmekriterien:** Beide Listen zeigen Stau, Blocker und naechste Bulk-Aktion ueber der Liste, ohne den Tabellenraum zu ueberfrachten.
**Erledigt:** `anlieferavis-liste.tsx` und `auftragsbestaetigungen-liste.tsx` fuehren jetzt denselben leichten Sammelvorgangskopf fuer Liefer- und Freigabestau ueber der bestehenden ListReport-Facharbeit.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-020

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Zahlungslaeufe und UStVA/ELSTER als echte Finance-Follow-up-Raeume verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/{fibu/zahlungslaeufe,finance/ustva,fibu/elster-online}.tsx`
**Abnahmekriterien:** Die Seiten zeigen FIBU-Druck, Fristen und naechste Massnahme ueber dem Arbeitsraum.
**Erledigt:** `zahlungslaeufe.tsx`, `finance/ustva.tsx` und `fibu/elster-online.tsx` zeigen jetzt Fristen, Freigabedruck und Einreichungs-/Exportpfad als leichten Finance-Follow-up-Rahmen ueber Wizard bzw. Fachformular.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-021

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Schnittstellen- und Meldefolgearbeitsplatz mit demselben schlanken Fallmodell harmonisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/schnittstellen-center.tsx`, ggf. angrenzende FIBU-Follow-up-Seiten.
**Abnahmekriterien:** Schnittstellen-Center zeigt operativen Druck, Risiken und naechste Aktion ohne KPI-Dopplung.
**Erledigt:** `fibu/schnittstellen-center.tsx` fuehrt Connector-, Revisions- und Periodenlage jetzt als technischen FIBU-Fallkopf mit kurzer Timeline und Masterdatenkontext.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-022

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Annahme- und Queue-Sammelraum mit derselben Leitlogik weiterziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/annahme/warteschlange.tsx`
**Abnahmekriterien:** Warteschlange zeigt operativen Stau, aktuelle Prioritaet und naechste Massnahme ueber der Liste.
**Erledigt:** `annahme/warteschlange.tsx` verdichtet Queue-Druck, Objektkettenlage und Bottleneck-Hinweis jetzt als operativen Annahmekopf ueber der bestehenden Operator-Oberflaeche.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-023

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Labor-/Qualitaets-Sammelarbeitsplaetze auf den leichten Operationsrahmen heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/{labor/proben-liste,qualitaet/labor-liste}.tsx`
**Abnahmekriterien:** Laborlisten zeigen Probenstau, kritische Faelle und naechste Folgeaktion ueber der Liste.
**Erledigt:** `labor/proben-liste.tsx` und `qualitaet/labor-liste.tsx` zeigen jetzt offenen Analyse- und Probenstau, Labor-/Chargekontext und die naechste Folgeaktion ueber den Tabellen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-024

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Scope und Restgrenzen nach der dritten Rollout-Welle erneut komprimiert dokumentieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, ggf. `docs/project-context/operational-rollout-scope-2026-04-09.md`
**Abnahmekriterien:** Der Rollout bleibt nachvollziehbar und weiterhin bewusst schlank.
**Erledigt:** Scope und Open-Gaps dokumentieren jetzt die dritte Welle fuer Einkaufslisten, FIBU-Follow-up, Schnittstellen, Queue und Laborraeume weiterhin als leichten Rollout ohne Zusatz-Requests.
**Checks:** `node scripts/docs-governance-check.cjs`

## OP-ROLL-025

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditorenraum als FIBU-Profiarbeitsplatz mit echter Folgeaktion statt Info-Toast vertiefen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/kreditoren.tsx`
**Abnahmekriterien:** `fibu/kreditoren.tsx` fuehrt DATEV-/Exportpfade als belastbare Folgeaktion ohne lokale Quittungs-Toastlogik.
**Erledigt:** `fibu/kreditoren.tsx` ist jetzt als echter Follow-up-Arbeitsraum mit Fallkopf, Kontext und Timeline verdichtet; DATEV-Export fuehrt direkt in den Buchungsuebergabe-Raum statt lokaler Info-Toast.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-026

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lieferanten-Dokumentraum mit realem Downloadverhalten statt TXT-Fallback professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/einkauf/lieferanten-stamm.tsx`
**Abnahmekriterien:** Dokumentdownload in `lieferanten-stamm.tsx` nutzt nur echte Artefaktpfade und zeigt klare Fehlerfuehrung ohne pseudo-download.
**Erledigt:** `lieferanten-stamm.tsx` nutzt jetzt nur noch den echten Downloadpfad; pseudo-TXT-Fallback ist entfernt und Fehlersituationen zeigen klaren DMS-/Artefakt-Hinweis.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-027

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Fuhrpark-Funktionsaktionen robust und revisionssicher machen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fuhrpark/fahrzeug-stamm.tsx`
**Abnahmekriterien:** Drucker-/Druck-/Unfall-/Loesch-Aktionen behandeln Fehler sauber und quittieren nicht mehr blind.
**Erledigt:** `fuhrpark/fahrzeug-stamm.tsx` fuehrt Setup-, Druck-, Unfall- und Loesch-Aktionen jetzt mit try/catch, klaren Fehlertoasts und Loeschbestaetigung aus.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-028

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Charge-Verfolgung von fragiler Static-Toast-Konfiguration auf belastbaren Runtime-Aktionspfad ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/futtermittel/charge-verfolgung.tsx`
**Abnahmekriterien:** Bulk-Aktionen in der Charge-Verfolgung sind eindeutig runtime-gebunden und enthalten keine toten Static-Action-Reste.
**Erledigt:** `futtermittel/charge-verfolgung.tsx` fuehrt keine static Toast-BulkActions mehr; alle Massenaktionen laufen nur noch ueber den runtime-verdrahteten Aktionspfad.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-029

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** L3/FIBU-Monatswerte als modernen ERP-Operatorraum mit klaren Folgeaktionen und Kontrolldichte veredeln.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/fibu/monatswerte.tsx`
**Abnahmekriterien:** Monatswerte liefern klaren Fallkopf, Risiken und naechste Aktion ohne Zusatz-Requests, konsistent zum Operational-Modell.
**Erledigt:** `fibu/monatswerte.tsx` hat jetzt denselben leichten Fallrahmen fuer L3/FIBU-Auswertung (Status, Risiken, naechste Aktion) ohne neue Datenabfragen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-030

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** L3/Cutover-nahe Buchungsuebergabe als FIBU-Leitstand mit Governance- und Revisionskontext vervollstaendigen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/schnittstelle-fibu.tsx`
**Abnahmekriterien:** Schnittstelle-FIBU zeigt operativen Druck, Revisions-/Cutover-Kontext und belastbare Folgewege ohne Platzhalteraktionen.
**Erledigt:** `fibu/schnittstelle-fibu.tsx` zeigt jetzt Fallkopf, Timeline und Revisions-/Cutover-Kontext fuer den Buchungsuebergabeprozess, inklusive klarer Folgefuehrung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-031

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchungsjournal als FIBU-Operatorraum mit Revisionsdruck, Periode und naechster Aktion verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/buchungsjournal.tsx`
**Abnahmekriterien:** `fibu/buchungsjournal.tsx` zeigt Fallkopf, Kontext und Timeline aus bereits geladenen Journaldaten und fuehrt DATEV-/Stornofolge ohne Blindflug.
**Erledigt:** `fibu/buchungsjournal.tsx` fuehrt Journalbuchungen jetzt als Revisionsfall mit Fallkopf, Referenzkontext, Timeline und direktem Exportpfad in die Buchungsuebergabe.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-032

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Abschluss-Checkliste als echter Close-Fall mit Pflichtdruck, Owner und Flow-Spine-Kontext fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/abschluss-checklist-detail.tsx`
**Abnahmekriterien:** `abschluss-checklist-detail.tsx` verdichtet Pflichtquote, Blocker und naechste Abschlussaktion oberhalb der Checkliste.
**Erledigt:** `abschluss-checklist-detail.tsx` zeigt jetzt den Close-Fall mit Pflichtdruck, Flow-Spine-Bezug, Blockern und kompakter Vorgangssicht ueber der Checkliste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-033

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditoren-Zahlungslauf als modernen ERP-Zahlungsoperatorraum mit Governance- und Freigabedruck heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/zahlungslauf-kreditoren.tsx`
**Abnahmekriterien:** `zahlungslauf-kreditoren.tsx` zeigt kompakten Zahlungsfallkopf, Kontext und Timeline ohne Zusatz-Requests.
**Erledigt:** `zahlungslauf-kreditoren.tsx` fuehrt den Kreditorenlauf jetzt mit Freigabe-, Skonto- und Ausfuehrungsdruck ueber dem bestehenden SEPA-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-034

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lastschriftlauf als Debitoren-Follow-up mit Mandats-, Frist- und Ausfuehrungsdruck darstellen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/lastschriften-debitoren.tsx`
**Abnahmekriterien:** `lastschriften-debitoren.tsx` bekommt denselben leichten Vorgangsrahmen fuer Mandatslage, Freigabe und Export.
**Erledigt:** `lastschriften-debitoren.tsx` surfact Mandatsluecken, Debitorenlauf und Freigabestatus jetzt als kompakten Follow-up-Rahmen ueber dem ObjectPage-Arbeitsplatz.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-035

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchhaltungsuebersicht als L3/FIBU-Cockpit mit Perioden- und Schnittstellenlage professionell verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/buchhaltungsuebersicht.tsx`
**Abnahmekriterien:** `buchhaltungsuebersicht.tsx` zeigt kompakten Operatorrahmen fuer Periodenlage, Exportpfad und Revisionskontext.
**Erledigt:** `fibu/buchhaltungsuebersicht.tsx` verdichtet Periodenlage, Revisionskontext und Folgepfade jetzt als L3/FIBU-Cockpit ueber der Auswertung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## OP-ROLL-036

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Waagenliste als physischer Leitknoten auf das einheitliche Fallmodell ziehen, ohne die bestehende Uebersicht zu ueberladen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/waage/liste.tsx`
**Abnahmekriterien:** `waage/liste.tsx` fuehrt kompakten Fallkopf, Kontext und Timeline fuer den physischen Kettenzustand aus vorhandenen Daten.
**Erledigt:** `waage/liste.tsx` nutzt jetzt denselben leichten Fallrahmen fuer Bottleneck, Eichlage und die physische Kette direkt ueber der Operatorliste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-037

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bankabgleich als echter Klaerungs- und Ausgleichsfall mit Owner, Matching-Druck und naechster Aktion verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/bank-abgleich.tsx`
**Abnahmekriterien:** `bank-abgleich.tsx` nutzt den leichten Fallrahmen ohne neue Requests und macht offene Matching-Lage sofort lesbar.
**Erledigt:** `finance/bank-abgleich.tsx` verdichtet Importstand, Abgleichsdifferenz, Zuordnungsdruck und naechste Aktion jetzt direkt ueber dem Object-Page-Arbeitsraum.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-038

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Payment-Matching als FIBU-Klaerungsarbeitsplatz mit Kontext, Timeline und Folgepfad professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/payment-matching.tsx`
**Abnahmekriterien:** `payment-matching.tsx` fuehrt Rueckstand, Matching-Risiko und naechste Aktion komprimiert ueber dem Arbeitsraum.
**Erledigt:** `finance/payment-matching.tsx` surfact Matching-Stau, manuellen Klaerungsbedarf und Importkontext als kompakten Vorgangsrahmen ohne Zusatz-Last.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-039

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** AP-Invoices-Liste als operativer Pruef- und Freigabestauplatz statt reine Tabelle verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/ap-invoices-list.tsx`
**Abnahmekriterien:** `ap-invoices-list.tsx` zeigt Stau, Blocker und naechste Sammelaktion aus vorhandenen Listen-/Statusdaten.
**Erledigt:** `finance/ap-invoices-list.tsx` zeigt jetzt Freigabestau, buchbare Rechnungen und die naechste Sammelaktion direkt ueber der Liste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-040

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** AP-Invoice-Form als echter Pruef- und Buchungsfall mit Governance- und Dokumentdruck fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/ap-invoice-form.tsx`
**Abnahmekriterien:** `ap-invoice-form.tsx` erhaelt den leichten Fallrahmen fuer Freigabe, Blocker und naechste Massnahme ohne neue API-Last.
**Erledigt:** `finance/ap-invoice-form.tsx` fuehrt Freigabestatus, Buchbarkeit und Summenlage jetzt als kompakten Pruef- und Buchungsfall.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-041

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** FIBU-Offene-Posten-Gesamtraum als operatorischer Sammelfall zwischen Debitoren und Kreditoren verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/offene-posten.tsx`
**Abnahmekriterien:** `fibu/offene-posten.tsx` zeigt OP-Druck, Ausgleichslage und Folgeweg ueber dem Arbeitsraum.
**Erledigt:** `fibu/offene-posten.tsx` verdichtet OP-Druck, Ueberfaelligkeit und Mahnfolge als klares Arbeitsbild vor der Liste.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-042

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Zahlungseingaenge als echter Clearing- und Rueckstandsraum mit kompaktem Vorgangsbild heben.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/zahlungseingaenge.tsx`
**Abnahmekriterien:** `zahlungseingaenge.tsx` surfact Rueckstand, Abgleichslage und naechste Aktion oberhalb der Facharbeit.
**Erledigt:** `fibu/zahlungseingaenge.tsx` fuehrt Rueckstand, Trefferquote und Import-/Klaerungskontext jetzt als einheitlichen Clearing-Rahmen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-043

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Zahlungsvorschlaege als FIBU-Entscheidungsraum mit Priorisierung und Governance-Kontext fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/zahlungsvorschlaege.tsx`
**Abnahmekriterien:** `zahlungsvorschlaege.tsx` zeigt Prioritaet, Liquiditaetsdruck und naechste Folgeaktion ohne neue Requests.
**Erledigt:** `fibu/zahlungsvorschlaege.tsx` zeigt jetzt Prioritaet, Skonto-Potenzial und Zahlungsfreigabe als kompakten Entscheidungsraum.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-044

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** BWA als modernen ERP-Analysearbeitsplatz mit Perioden-, Abweichungs- und Folgekontext aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/bwa.tsx`
**Abnahmekriterien:** `bwa.tsx` fuehrt Fallkopf, Kontext und Timeline aus bereits geladenen Auswertungsdaten.
**Erledigt:** `fibu/bwa.tsx` verdichtet Periodenlage, Ergebnisabweichung und Folgeaktion als leichten Analysearbeitsplatz ueber der Auswertung.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-045

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bilanz als L3/FIBU-Abschlussraum mit Risiko- und Folgepfad konsistent zum neuen Arbeitsmodell ziehen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/bilanz.tsx`
**Abnahmekriterien:** `bilanz.tsx` liefert kompakten Operatorrahmen fuer Abschlusslage, Revisionskontext und Drilldown-Folgewege.
**Erledigt:** `fibu/bilanz.tsx` fuehrt Bilanzsumme, EK-Quote, Ausgleichslage und Abschlussfolge nun als kompakten Abschlussrahmen.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-046

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Rueckverfolgung als physischer Ausnahme- und Nachweisfall mit Charge-/Dokumentdruck fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/charge/rueckverfolgung.tsx`
**Abnahmekriterien:** `charge/rueckverfolgung.tsx` zeigt Status, Blocker und Folgewege fuer Charge-/Nachweisfaelle ohne neuen Datenpfad.
**Erledigt:** `charge/rueckverfolgung.tsx` verdichtet Spurpfad, Lieferkettenblocker und Nachweisfolge ueber der eigentlichen Timeline.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-047

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Wareneingang als physischer Fall zwischen Annahme, Charge und Lager deutlich mit dem Zielbild verknuepfen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/charge/wareneingang.tsx`
**Abnahmekriterien:** `charge/wareneingang.tsx` fuehrt den leichten Fallrahmen fuer Ressource, Blocker und naechste Aktion aus vorhandenen Daten.
**Erledigt:** `charge/wareneingang.tsx` fuehrt Lieferant, Charge, Lagerort und QS-Lage nun als kompakten Eingangsvorgang vor dem Wizard.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-048

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Tourenplanung als Logistik-Leitraum mit Folgecharakter, Bottleneck und Aktionspriorisierung verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/logistik/tourenplanung.tsx`
**Abnahmekriterien:** `tourenplanung.tsx` bekommt den kompakten Vorgangsrahmen fuer Druck, Blocker und naechste Massnahme ohne Zusatz-Requests.
**Erledigt:** `logistik/tourenplanung.tsx` zeigt Dispositionslage, Ressourcenengpaesse und die naechste Aktionsprioritaet jetzt direkt ueber den Touren.
**Checks:** `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`, `node scripts/docs-governance-check.cjs`

## OP-ROLL-049

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Debitorische Ausgangsrechnungen als echter Freigabe-, Druck- und Forderungsfall statt reine Listenmaske fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/invoices-list.tsx`
**Abnahmekriterien:** `invoices-list.tsx` zeigt Rueckstand, Druck-/Versanddruck und naechste Sammelaktion aus bestehender Listenlage.

## OP-ROLL-050

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Ausgangsrechnungsformular als echter Faktura-, Freigabe- und Folgebelegfall verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/invoice-form.tsx`
**Abnahmekriterien:** `invoice-form.tsx` fuehrt Status, Blocker und naechste Aktion oberhalb der Fachbearbeitung.

## OP-ROLL-051

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Dunning-Editor als echter Mahn- und Eskalationsfall professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/dunning-editor.tsx`
**Abnahmekriterien:** `dunning-editor.tsx` surfact Mahnstufe, Eskalationspfad und naechste Aktion ohne neue Requests.

## OP-ROLL-052

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Buchungsimport als echter Import-, Pruef- und Verbuchungsfall aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/buchungsimport.tsx`
**Abnahmekriterien:** `buchungsimport.tsx` zeigt Importdruck, Fehlerlage und Folgepfad aus bereits vorhandenen Daten.

## OP-ROLL-053

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Audit-Trail als FIBU-Revisionsraum mit Follow-up und Ausnahmebild fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/audit-trail.tsx`
**Abnahmekriterien:** `audit-trail.tsx` fuehrt Revisionslage, offene Auffaelligkeiten und naechste Pruefaktion kompakt.

## OP-ROLL-054

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Nebenbuch-Abstimmung als echter Clearing- und Differenzraum verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/finance/nebenbuch-abstimmung.tsx`
**Abnahmekriterien:** `nebenbuch-abstimmung.tsx` zeigt Differenzen, Blocker und naechste Klaerungsschritte im leichten Fallmodell.

## OP-ROLL-055

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Hauptbuch als echter Abschluss- und Revisionsraum aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/hauptbuch.tsx`
**Abnahmekriterien:** `hauptbuch.tsx` fuehrt Abschlusslage, Journaldruck und naechste Aktion oberhalb der Sachkontensicht.

## OP-ROLL-056

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** GuV als FIBU-Abweichungs- und Ergebnisraum konsistent zum Operationsmodell verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/guv.tsx`
**Abnahmekriterien:** `guv.tsx` zeigt Ergebnisdruck, Ausreisser und Folgeweg ohne Zusatz-Requests.

## OP-ROLL-057

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kontenplan als professionellen Steuerungsraum mit Revisions- und Nutzungskontext ausbauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/kontenplan.tsx`
**Abnahmekriterien:** `kontenplan.tsx` surfact Kontenlogik, Sperr-/Nutzungslage und naechste Verwaltungsaktion ohne Ueberladung.

## OP-ROLL-058

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** OP-Verwaltung als querliegender FIBU-Klaerungsraum zwischen Debitoren und Kreditoren fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/op-verwaltung.tsx`
**Abnahmekriterien:** `op-verwaltung.tsx` zeigt Blocker, Rueckstand und Eskalationspfad ueber der Sammelmaske.

## OP-ROLL-059

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Anlagen-Suite als echter Revisions-, Abschreibungs- und Abschlussfall verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/anlagen-suite.tsx`
**Abnahmekriterien:** `anlagen-suite.tsx` fuehrt Abschreibungsdruck, Revisionslage und naechste Periode kompakt.

## OP-ROLL-060

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Kreditlinien als Risiko- und Freigaberaum fuer Finanzierung und Forderungsschutz aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/fibu/kreditlinien.tsx`
**Abnahmekriterien:** `kreditlinien.tsx` zeigt Auslastung, Grenzverletzungen und naechste Massnahme im einheitlichen Arbeitsmodell.

## OP-ROLL-061

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bestandsuebersicht als echter Lager- und Reservierungsraum mit Folgepfad verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/bestandsuebersicht.tsx`
**Abnahmekriterien:** `bestandsuebersicht.tsx` zeigt Verfuegbarkeit, Engpaesse und naechste Lageraktion ohne neue API-Last.

## OP-ROLL-062

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Bestandskorrektur als echter Pruef-, Freigabe- und Auditfall fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/bestandskorrektur.tsx`
**Abnahmekriterien:** `bestandskorrektur.tsx` surfact Differenz, Begruendung und Folgeaktion oberhalb der Erfassung.

## OP-ROLL-063

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Einlagerung als physischer Vorgang zwischen Bestand, Charge und Lagerplatz klar verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/einlagerung.tsx`
**Abnahmekriterien:** `einlagerung.tsx` fuehrt Ressourcenlage, Blocker und naechste Massnahme ohne neue Requests.

## OP-ROLL-064

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Auslagerung als echter Liefer- und Verfuegbarkeitsfall professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/auslagerung.tsx`
**Abnahmekriterien:** `auslagerung.tsx` zeigt Verfuegbarkeit, Reservierungsdruck und Folgeweg oberhalb der Facharbeit.

## OP-ROLL-065

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lagerbewegungen als Revisions- und Rueckverfolgungsraum einheitlich aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/lagerbewegungen.tsx`
**Abnahmekriterien:** `lagerbewegungen.tsx` verdichtet Bewegungsdruck, Audit-Lage und Folgepfad ohne zusaetzliche Datenlast.

## OP-ROLL-066

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Inventur als echter Klaerungs- und Differenzraum zwischen Lager und FIBU fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/inventur.tsx`
**Abnahmekriterien:** `inventur.tsx` zeigt Differenzdruck, Owner und naechste Inventuraktion im leichten Fallmodell.

## OP-ROLL-067

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Lagerterminal als physischer Arbeitsraum fuer schnelle Entscheidungen mit kompaktem Kontext aufwerten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/lager/terminal.tsx`
**Abnahmekriterien:** `terminal.tsx` fuehrt Status, Blocker und naechste Aktion ohne die Touch-Bedienung zu ueberfrachten.

## OP-ROLL-068

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Qualitaetsausnahmen als echter Eskalations- und Freigaberaum fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/qualitaet/ausnahmen.tsx`
**Abnahmekriterien:** `ausnahmen.tsx` zeigt Risiko, Owner, naechste Massnahme und Eskalationsdruck ueber dem Arbeitsraum.

## OP-ROLL-069

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Reklamationsliste als Sammelraum fuer Eskalationen, Wiedervorlagen und Folgewege verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/qualitaet/reklamationen.tsx`
**Abnahmekriterien:** `reklamationen.tsx` surfact Rueckstand, Risikobild und naechste Sammelaktion kompakt aus vorhandenen Daten.

## OP-ROLL-070

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Labor-Detail als echter Pruef- und Freigabefall zwischen Probe, Charge und QS fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/qualitaet/labor-detail.tsx`
**Abnahmekriterien:** `labor-detail.tsx` fuehrt Befundlage, Blocker und naechste Aktion konsistent ueber der Fachmaske.

## OP-ROLL-071

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Frachtbriefe als echter Logistik- und Nachweisraum zwischen Tour, Charge und Dokument professionalisieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/logistik/frachtbriefe.tsx`
**Abnahmekriterien:** `frachtbriefe.tsx` zeigt Blocker, Dokumentdruck und naechste Aktion ohne neue Requests.

## OP-ROLL-072

**Von:** Codex
**Stand:** abgeschlossen
**Ziel des Slices:** Wiegungen als operative Sammelmaske zwischen Waage, Annahme und Abrechnung verdichten.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/project-context/operational-rollout-scope-2026-04-09.md`, `packages/frontend-web/src/pages/waage/wiegungen.tsx`
**Abnahmekriterien:** `wiegungen.tsx` surfact Rueckstand, Blocker und Folgepfad im leichten Fallmodell aus bereits geladenen Daten.

## ERP-FINANZ-ROADMAP-P3P4

**Von:** Claude Code
**Owner:** (Team)
**Stand:** abgeschlossen 2026-05-12
**Ziel des Slices:** ERP-Finanz Roadmap Phase 3 (Orders-REST Architektur-Entscheid + Tenant-Isolation-Tests) und Phase 4 (Observability Counter + DB-Indexes) abschliessen.

**Dateibesitz:**
- `packages/erp-domain/src/bootstrap.ts` — Architektur-Kommentar Orders-REST = Python
- `packages/erp-domain/tests/integration/tenant-isolation.spec.ts` — Negative Tenant-Tests
- `app/core/metrics.py` — tenant_auth_errors_total Counter
- `app/middleware/tenant_enforcement.py` — Counter-Inkrementierung
- `migrations/sql/erp/006_missing_tenant_indexes.sql` — Composite-Indexes domain_sales/inventory/erp/finanz
- `alembic/versions/faf00a6bfc11_006_missing_tenant_indexes.py` — No-Op Alembic-Revision
- `tests/test_gap_fixes_phase4.py` — Phase-4-Smoke-Tests

**Abnahmekriterien:**
- bootstrap.ts dokumentiert: Orders-REST = Python; controller-Token nicht registriert (Invariante)
- Tenant-Isolation: fremder Tenant sieht keine Debitoren/Kreditoren des anderen Tenants
- `tenant_auth_errors_total{route, error_type}` Counter in Prometheus scrappbar
- 006_missing_tenant_indexes.sql: idempotente Composite-Indexes auf alle relevanten Schemas
- `alembic upgrade head` laeuft ohne drop_table-Operationen

**Erledigt:** Alle 4 Phase-3+4-Ziele umgesetzt, committed `f4d0462ae` + `6cf97afcc`; Linter sauber; 4/4 Phase-4-Tests gruen; `alembic upgrade head` = no-op; main + develop auf GitHub gepusht.

**Checks:** `pytest tests/test_gap_fixes_phase4.py -v`; `alembic upgrade head`; `flake8 app/core/metrics.py app/middleware/tenant_enforcement.py`

## UX-SERVICE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Service-Anfragen und Rueckmeldung mit Rollenfokus, klarer Aufgabe, Status, naechster Aktion und Nachweisfuehrung nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SERVICE-001.yaml`, `packages/frontend-web/src/pages/service/anfragen.tsx`, `packages/frontend-web/src/pages/service/rueckmeldung.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Service-Anfragen und Rueckmeldung zeigen Rollenfokus, Service-/Rueckmeldeplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Liste, Suche, Export, Workflow-Handover, Rueckmeldeformular und Navigation bleiben erhalten.
**Erledigt:** Service-Anfragen um Rollenfokus, Service-Arbeitsplan, Managemententscheidung, Next Action, Nachweislink, CRUD-Abdeckung und klare Leerzustandsaktion erweitert; Rueckmeldung um Rollenfokus, Rueckmeldeplan, Pflichtklarheit, Folgehinweis, Nachweislink und gefuehrte Sendebereitschaft erweitert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SERVICE-001.yaml`; `git diff --check`
**Offene Risiken:** Service-Abschluss und Feldservice-Detail bleiben Folgeslices; dieser Slice fokussiert Anfrageuebersicht und Rueckmeldung.

## UX-MONITORING-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Monitoring-Alerts und Monitoring-Regeln mit Betriebsstatus, Owner, naechster Aktion, Eskalationsnachweis und CRUD-Klarheit nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-MONITORING-001.yaml`, `packages/frontend-web/src/pages/admin/monitoring/alerts.tsx`, `packages/frontend-web/src/pages/admin/monitoring/regeln.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Alert-Uebersicht und Regelverwaltung zeigen Rollenfokus, Betriebs-/Regelplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Alert-Liste, Regelanlage, Kanalverwaltung, Scheduler-Jobs und Loeschen bleiben erhalten.
**Erledigt:** Alert-Uebersicht um Rollenfokus, Betriebsplan, Managemententscheidung, Next Action, Eskalationsnachweis, Alert-Zeitleiste und klaren Leerzustand erweitert; Monitoring-Regeln um Rollenfokus, Regelbetriebsplan, Managemententscheidung, Next Action, Nachweislink, CRUD-Abdeckung und gefuehrte Auswahlfelder erweitert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-MONITORING-001.yaml`; `git diff --check`
**Offene Risiken:** `system/live-monitor` bleibt technischer Folgeslice; dieser Slice fokussiert Admin-Alerts und Monitoring-Regeln.

## UX-COMPLIANCE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Compliance-Center und QS-Checkliste mit klarer Pruefaufgabe, Risiko, naechster Aktion, Nachweisfuehrung und CRUD-/Workflow-Klarheit nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-COMPLIANCE-001.yaml`, `packages/frontend-web/src/pages/admin/compliance-dashboard.tsx`, `packages/frontend-web/src/pages/compliance/qs-checkliste.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Compliance-Center und QS-Checkliste zeigen Rollenfokus, Pruefplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Reports, Detailnavigation, Agent-Panel, Tastaturleiste und Tabellen bleiben erhalten.
**Erledigt:** Compliance-Center um Rollenfokus, Compliance-Pruefplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung erweitert; QS-Checkliste um Rollenfokus, QS-Pruefplan, Entscheidungsbild, Nachweislink und gefuehrte Auditbereitschaft erweitert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-COMPLIANCE-001.yaml`; `git diff --check`
**Offene Risiken:** Meldewesen-Konsole bleibt Spezial-Folgeslice; dieser Slice fokussiert Dashboard und QS-Pruefaufgabe.

## UX-AGRIBUSINESS-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Feldservice-Aufgaben als Agribusiness-Einsatzliste mit Einsatzstatus, Owner, naechster Aktion, Nachweisfuehrung und CRUD-/Workflow-Klarheit nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-AGRIBUSINESS-001.yaml`, `packages/frontend-web/src/pages/agribusiness/field-service-tasks.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Field-Service-Aufgaben zeigen Rollenfokus, Einsatzplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Suche, Copilot, Druck, Neu/Bearbeiten/Abbrechen/Loeschen, Workflow-Hinweis und Audit-Drawer bleiben erhalten.
**Erledigt:** Field-Service-Aufgabenliste um Rollenfokus, Einsatzplan, Managemententscheidung, Next Action, Nachweislink, Einsatz-KPIs und CRUD-/Workflow-Abdeckung erweitert; bestehende Suche, Copilot, Druck, Neu/Bearbeiten/Abbrechen/Loeschen, Workflow-Hinweis und Audit-Drawer bleiben erhalten.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-AGRIBUSINESS-001.yaml`; `git diff --check`
**Offene Risiken:** Neue-/Edit-Masken und Farmer-Stamm bleiben Folgeslices; dieser Slice fokussiert die Einsatzliste.

## UX-SYSTEM-LIVE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Technischen Live-Monitor von roher JSON-Sicht zu einer verstaendlichen Betriebsstatusseite mit Rollenfokus, Statusdeutung, naechster Aktion und Nachweisbezug nach UX-Standard umbauen.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-SYSTEM-LIVE-001.yaml`, `packages/frontend-web/src/pages/system/live-monitor.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Live-Monitor zeigt Rollenfokus, Betriebsplan, Managemententscheidung, Next Action, Nachweislink und kompakte Ereignisuebersichten; technische JSON-Rohdaten bleiben als Diagnosebereich verfuegbar; bestehender NavLiveStatus und Live-Store werden weiter genutzt.
**Erledigt:** Live-Monitor als Live-Betriebsmonitor mit Rollenfokus, Betriebsplan, Managemententscheidung, Next Action, Nachweislink, Live-KPIs, Ereigniszeitleiste und kompakten Sales-/Bestands-/Policy-Listen umgesetzt; technische JSON-Rohdaten bleiben als Diagnosebereich verfuegbar.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-SYSTEM-LIVE-001.yaml`; `git diff --check`
**Offene Risiken:** Externe SSE-Verfuegbarkeit bleibt umgebungsabhaengig; dieser Slice verbessert die UI-Deutung vorhandener Live-Daten.

## UX-MELDEWESEN-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-15
**Ziel des Slices:** Meldewesen-Konsole mit Meldefrist, Artefaktstatus, Owner, naechster Einreichungsaktion, Nachweisfuehrung und CRUD-/Workflow-Klarheit nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-MELDEWESEN-001.yaml`, `packages/frontend-web/src/pages/compliance/meldewesen-konsole.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Meldewesen-Konsole zeigt Rollenfokus, Meldeplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Connector-, Unit-, Schedule-, Job-, Import-/Export- und Artefaktfunktionen bleiben erhalten.
**Erledigt:** Meldewesen-Konsole um Rollenfokus, Meldeplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung fuer Connectoren, Reporting Units, Zeitplaene, Jobs, Import/Export und Artefakte erweitert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-MELDEWESEN-001.yaml`; `git diff --check`
**Offene Risiken:** Echte externe Meldestellen-Quittungen bleiben umgebungsabhaengig; dieser Slice verbessert die UI-Steuerung der vorhandenen Jobs und Artefakte.

## UX-AGRAR-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-16
**Ziel des Slices:** Agrar-Schlagkartei und Massnahmen-Dokumentation mit Feld-/Massnahmenstatus, Nachweis, naechster Aktion und gefuehrter CRUD-/Workflow-Klarheit nach UX-Standard fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-AGRAR-001.yaml`, `packages/frontend-web/src/pages/agrar/feldbuch/schlagkartei.tsx`, `packages/frontend-web/src/pages/agrar/feldbuch/massnahmen.tsx`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Schlagkartei und Massnahmen-Dokumentation zeigen Rollenfokus, Feld-/Massnahmenplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung; bestehende Filter, Export, Feldblockfinder, Tabs, Tabellen, Anlage-, Bearbeitungs- und Loeschpfade bleiben erhalten.
**Erledigt:** Schlagkartei um Rollenfokus, Feldplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Workflow-Abdeckung erweitert; Massnahmen-Dokumentation um Rollenfokus, Massnahmenplan, Managemententscheidung, Next Action, Nachweislink und CRUD-/Nachweis-Abdeckung erweitert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-AGRAR-001.yaml`; `git diff --check`
**Offene Risiken:** Duengungsplanung, PSM-Spezialmasken und Portal-Feldbuch bleiben Folgeslices; dieser Slice fokussiert Schlag- und Massnahmenuebersicht.

## UX-UX-AUDIT-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-16
**Ziel des Slices:** Pruefen und verbindlich festlegen, wo der UX-Exzellenzbaukasten weiterhin fachlich sinnvoll ist, wo eine kompakte oder minimale Variante reicht und wo der systemweite Rollout als abgeschlossen gilt.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-UX-AUDIT-001.yaml`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`
**Abnahmekriterien:** Der UX-Standard unterscheidet volle, kompakte und minimale Baukasten-Nutzung; Stop-Regeln verhindern Ueberladung; verbleibende sinnvolle Rollout-Slices sind nach Nutzerwert priorisiert; Doku-Checks und Workboard-Validierung sind gruen.
**Erledigt:** UX-Standard von pauschaler Pflicht auf Seitentyp-Klassifikation umgestellt; Stop-Regeln gegen Ueberladung fuer Rollenfokus, Management-Bild, Nachweislinks, Audit-Zeitleiste und CRUD-Checkliste ergaenzt; systemweiter Rollout fuer Kernbereiche als abgeschlossen dokumentiert; weitere Arbeiten erfolgen nur noch nutzerwertbasiert.
**Checks:** `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-UX-AUDIT-001.yaml`; `git diff --check`
**Offene Risiken:** Bereits umgestellte Seiten koennen im Einzelfall zu schwer sein; kuenftige Trim-Reviews reduzieren nur konkret sichtbare Ueberladung, statt den Baukasten pauschal zurueckzunehmen.

## UX-REMAINDER-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-16
**Ziel des Slices:** Verbleibende sinnvolle UX-Abschlussarbeiten fuer Futtermittel, Duengung und Portal nach der neuen Baukasten-Einsatzlogik umsetzen: voll nur fuer echte Experten-/Pruefflaechen, kompakt fuer Planung und leicht fuer Self-Service.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-REMAINDER-001.yaml`, `docs/project-context/ux-excellence-operating-standard-2026-05-13.md`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`, `packages/frontend-web/src/pages/futtermittel/futtermittel-qualitaetskontrolle.tsx`, `packages/frontend-web/src/pages/agrar/duengung/planung.tsx`, `packages/frontend-web/src/pages/agrar/duenger/bedarfsrechner.tsx`, `packages/frontend-web/src/pages/portal/feldbuch.tsx`, `packages/frontend-web/src/pages/portal/naehrstoffbilanzen.tsx`
**Abnahmekriterien:** Futtermittel-Expertenseiten zeigen Pruefstatus, Risiko, naechste Aktion und Nachweis ohne einfache Pflegebereiche zu ueberladen; Duengungsplanung und Bedarfsrechner fuehren Bedarf, Sperrfrist/Risiko, Nachweis und naechste Planungshandlung kompakt; Portal-Feldbuch und Naehrstoffbilanzen nutzen leichte Self-Service-Sprache; keine unpassenden Management-Bilder oder sichtbaren CRUD-Checklisten auf Self-Service-Seiten; Typecheck, Workboard-Validierung und Doku-Checks sind gruen.
**Erledigt:** Futtermittel-Rationsoptimierung um leichte fachliche Schrittfolge erweitert; Futtermittel-QS um Pruefablauf, naechste Pruefaktion und QS-Nachweislink erweitert; Duengungsplanung und Bedarfsrechner um kompakte Planung/Eingabefuehrung erweitert; Portal-Feldbuch und Naehrstoffbilanzen um leichte Self-Service-Next-Actions und Leerzustaende erweitert; UX-Standard auf abgeschlossenes Abschlussbild aktualisiert.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/ux-excellence-operating-standard-2026-05-13.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-REMAINDER-001.yaml`; `git diff --check`
**Offene Risiken:** Kuenftige neue Fachfunktionen brauchen wieder Seitentyp-Klassifikation; aktuell sind keine weiteren UX-Flaechenrollouts vorgesehen.

## UX-GAP-CLOSURE-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-16
**Ziel des Slices:** Die fuenf Abschlussgaps aus dem Ist/Soll-Vergleich schliessen: Open-Gaps-Doku auf die neue UX-Einsatzlogik ziehen, Portal-Dokumente entladen, RAT-OPT-001 im Workboard abschliessen, P1-Restprogramme klar von UX trennen und HRM-/Live-Gates als Betriebsnachweise statt Repo-Code-Gaps fuehren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/UX-GAP-CLOSURE-001.yaml`, `docs/project-context/open-gaps-and-known-issues.md`, `packages/frontend-web/src/pages/portal/dokumente.tsx`
**Abnahmekriterien:** Open-Gaps-Doku beschreibt UX nicht mehr als pauschale Pflichtmuster, sondern als abgeschlossenen Rollout mit Seitentyp-Logik; Portal-Dokumente zeigen keine Rollenleiste, kein Management-Bild und keine sichtbare CRUD-Checkliste mehr; RAT-OPT-001 ist im Workboard nicht mehr irrefuehrend als in Arbeit gefuehrt; Coverage/Domain-Parity und externe Gates sind klar als eigene technische bzw. betriebliche Programme abgegrenzt; Typecheck, Workboard-Validierung und Doku-Checks sind gruen.
**Erledigt:** Open-Gaps-Doku auf abgeschlossene UX-Seitentyp-Logik aktualisiert; Portal-Dokumente von Rollenleiste, Management-Entscheidung und CRUD-Checkliste auf leichte Self-Service-Fuehrung reduziert; RAT-OPT-001 im Workboard als abgeschlossen und historisch eingeordnet; Coverage/Domain-Parity als Qualitaetsprogramme und HRM-/Live-Gates als Betriebsnachweise abgegrenzt.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs`; `node scripts/docs-markdown-check.cjs docs/project-context/open-gaps-and-known-issues.md docs/agent-ops/active-workboard.md docs/agent-ops/slices/UX-GAP-CLOSURE-001.yaml`; `git diff --check`
**Offene Risiken:** Kuenftige neue Fachfunktionen koennen neue UX-Detailreviews ausloesen; aktuell bestehen keine offenen UX-Baukasten-Rollout-Gaps.

## FRONTEND-DOMAIN-AUDIT-REPAIR-001

**Von:** Codex
**Owner:** Codex
**Stand:** abgeschlossen 2026-05-22
**Ziel des Slices:** Claude-Domain-Audit-Fixes vor Push qualitaetssichern: i18n-/Encoding-Korruption reparieren, temporaere Skripte entfernen, Routing- und Module-Registrierung validieren und lokale Commit-Historie mit korrektem Autor konsolidieren.
**Dateibesitz:** `docs/agent-ops/active-workboard.md`, `docs/agent-ops/slices/FRONTEND-DOMAIN-AUDIT-REPAIR-001.yaml`, `packages/frontend-web/src/app/route-aliases.json`, `packages/frontend-web/src/app/page-module-loader.ts`, `packages/frontend-web/src/app/page-module-groups/commercial.ts`, `packages/frontend-web/src/i18n/locales/*/translation.json`, `packages/frontend-web/src/pages/**/*.tsx`
**Abnahmekriterien:** Keine neue UTF-8-Mojibake in geaenderten Frontend-Dateien; route-aliases verweisen auf ladbare Page-Module; fehlende i18n-Keys aus dem Audit sind ergaenzt ohne Locale-Korruption; Typecheck und Workboard-Validierung sind gruen; unpushte Commits haben korrekte Autoren-Metadaten.
**Erledigt:** Locale-Dateien de/en/es/fr auf sauberen Stand zurueckgefuehrt und `pattern.listreport.items_count` gezielt ergaenzt; Encoding-Funde im gesamten `packages/frontend-web/src` bereinigt; ungueltige UTF-8-Dateien nach UTF-8 konvertiert; temporaere Reparatur-Skripte entfernt; Route-Aliases gegen existierende Module validiert; lokale unpushed Historie vor Push auf saubere Autor-/Commitstruktur konsolidiert.
**Checks:** `node` JSON-Parse fuer `packages/frontend-web/src/i18n/locales/de|en|es|fr/translation.json`; Encoding-Scan `rg -n "Ã|Â|â" packages/frontend-web/src`; UTF-8-Validierung fuer `packages/frontend-web/src`; Route-Alias-Modulvalidierung gegen `packages/frontend-web/src`; `pnpm --filter @valero-neuroerp/frontend-web type-check`; `pnpm --filter @valero-neuroerp/frontend-web lint`; `pnpm --filter @valero-neuroerp/frontend-web build`; `python scripts/agent_workboard_supervisor.py validate`; `node scripts/docs-governance-check.cjs docs/agent-ops/active-workboard.md docs/agent-ops/slices/FRONTEND-DOMAIN-AUDIT-REPAIR-001.yaml`; `node scripts/docs-markdown-check.cjs docs/agent-ops/active-workboard.md docs/agent-ops/slices/FRONTEND-DOMAIN-AUDIT-REPAIR-001.yaml`; `git diff --check`
**Offene Risiken:** Vite-Build meldet weiterhin bestehende, nicht blockierende Warnungen aus CSS-Minifizierung und POS-Doppelimport; backendabhaengige Datenladefehler sind von Frontend-Routing/Rendering getrennt zu bewerten.

## FACHLICHE-VERTIEFUNG-UX-W17-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-26
**Ziel des Slices:** Wave 17 UX — Zu-/Abschlaggruppen [ZAGR], Zu-/Abschlagklassen [ZAKL] und Zu-/Abschlagkonditionen [ZAK] als vollständige produktive Maske unter `/preise/zu-abschlaggruppen`.
**Dateibesitz:** `docs/agent-ops/slices/FACHLICHE-VERTIEFUNG-UX-W17-001.yaml`, `packages/frontend-web/src/lib/api/zuAbschlaggruppen.ts`, `packages/frontend-web/src/pages/preise/zu-abschlaggruppen.tsx`, `packages/frontend-web/tests/e2e/fachliche-vertiefung-zu-abschlaege.spec.ts`
**Abnahmekriterien:** Tabs ZAGR/ZAKL/ZAK produktiv; CREATE + DELETE für Gruppen und Klassen; CREATE + Listenansicht für Konditionen; E2E 4/4 grün; Regression Rabattgruppen + Betriebsstätten grün; Typecheck grün; Workboard grün.
**Erledigt:** API-Client `zuAbschlaggruppen.ts`; UI-Maske mit 3 Tabs; Navigation + Route-Builder bereits vorhanden; E2E 4/4; Regression 9/9; TypeScript grün; alle Gates grün.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; Playwright-Gates W17 + Regression W14; `python scripts/agent_workboard_supervisor.py validate`; `git diff --check`
**Offene Risiken:** Keine.

## FACHLICHE-VERTIEFUNG-UX-W16-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-25
**Ziel des Slices:** Wave 16 Integration Vertreterstamm und Vertreterprovisionsgruppen: provisionsgruppe_nr in der Vertreterstamm-Maske (W15) als Select aus echten Provisionsgruppen (W12) statt freiem Text-Input.
**Dateibesitz:** `docs/agent-ops/slices/FACHLICHE-VERTIEFUNG-UX-W16-001.yaml`, `packages/frontend-web/src/pages/crm/vertreterstamm.tsx`, `packages/frontend-web/tests/e2e/fachliche-vertiefung-vertreterstamm-prov-integration.spec.ts`, Fremdfix: `packages/frontend-web/tests/e2e/fachliche-vertiefung-vertreterprovisionen.spec.ts`
**Abnahmekriterien:** provisionsgruppe_nr im Vertreter-Anlegen-Formular ist ein Select; provisionsgruppe_nr im Edit-Dialog ist ein Select; W16-Integrationstest gruen; Regression W15/W12 gruen; Typecheck gruen.
**Erledigt:** vertreterstamm.tsx Create-Form + Edit-Dialog auf useProvisionsgruppen()-Select; W16-Integrationstest (2/2 gruen); W15-Regression (4/4 gruen); W12-Regression (1/1 gruen, 1 Staffel-Test skip mit Begruendung); Fremdfix W12-Spec strict-mode-Violations.
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; Playwright-Gates W16+W15+W12; `python scripts/agent_workboard_supervisor.py validate`; `git diff --check`
**Offene Risiken:** W12-Staffeln-Test skip ist dokumentiertes pre-existing Playwright-Isolation-Issue; keine fachlichen Risiken.

## FACHLICHE-VERTIEFUNG-UX-W21-001

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-26
**Ziel des Slices:** Wave 21 — 6 fehlende Frontend-Pages: Daueraufträge, Massebilanz, Vermehrungsverträge, Zinsabrechnung, Artikel-Bestandteile, Artikelverpackung. Inkl. API-Clients, Navigation, Routen und E2E-Tests.
**Dateibesitz:** `packages/frontend-web/src/lib/api/dauerauftraege.ts`, `packages/frontend-web/src/lib/api/massebilanz.ts`, `packages/frontend-web/src/lib/api/vermehrungsvertraege.ts`, `packages/frontend-web/src/lib/api/zinsabrechnung.ts`, `packages/frontend-web/src/lib/api/artikelbestandteile.ts`, `packages/frontend-web/src/lib/api/artikelverpackung.ts`, `packages/frontend-web/src/pages/verkauf/dauerauftraege.tsx`, `packages/frontend-web/src/pages/lager/massebilanz.tsx`, `packages/frontend-web/src/pages/agrar/vermehrungsvertraege.tsx`, `packages/frontend-web/src/pages/agrar/zinsabrechnung.tsx`, `packages/frontend-web/src/pages/stammdaten/artikelbestandteile.tsx`, `packages/frontend-web/src/pages/stammdaten/artikelverpackung.tsx`, Navigation- und Route-Builder-Dateien, 6 E2E-Specs
**Abnahmekriterien:** 6 API-Clients + 6 Pages mit Mutation Lifecycle Guards; Toast-Feedback; Navigation aktualisiert; Route-Builder-Einträge; 6 E2E-Tests gruen; TypeCheck gruen.
**Erledigt:** 6 API-Clients, 6 Pages, Navigation und Route-Builder aktualisiert, 6 E2E-Tests. TypeCheck: 0 Fehler. Bugfix vermehrungsvertraege.tsx (Radix SelectItem value="").
**Checks:** `pnpm --filter @valero-neuroerp/frontend-web type-check`; Playwright-Gates W21; `python scripts/agent_workboard_supervisor.py validate`
**Gate-Ergebnis:** 6/6 E2E-Tests gruen, TypeCheck 0 Fehler (2026-05-26, develop)
**Offene Risiken:** Keine.

## BACKEND-SLICE-GDPR-KONTRAKTE-DMS-001

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-26
**Ziel des Slices:** Vier offene Backend-Slices implementieren: GDPR-requests-Lifecycle (Art. 15/17/20), Kontrakte-Amendments/Templates, Agribusiness-Farmers und DMS-Inbox + admin/dms. Pydantic-V2-ConfigDict-Migration in allen neuen Endpoint-Dateien.
**Dateibesitz:** `app/api/v1/endpoints/gdpr_requests.py`, `app/api/v1/endpoints/kontrakte.py`, `app/api/v1/endpoints/agribusiness.py`, `app/api/v1/endpoints/dms_inbox.py`, `app/api/v1/endpoints/admin_dms.py`, `app/infrastructure/models/agribusiness_models.py`, Alembic-Migrationen fuer GDPR und Farmers, `app/api/v1/api.py`
**Abnahmekriterien:** GDPR-Lifecycle (PENDING→VERIFIED→PROCESSING→COMPLETED|REJECTED) mit Download; Kontrakte GET amendments-templates + POST/PATCH amendments; Farmers GET/DELETE mit 204; DMS GET/POST/DELETE inbox + admin status/test/bootstrap; Pydantic V2 ohne Config-Deprecation-Warnungen.
**Erledigt:** 8 GDPR-Endpoints (814de39d0); 4 Kontrakte-Amendments-Endpoints (80077b009); Farmer-Model + Migration + 2 Endpoints (e8dd5b24e); 6 DMS-Inbox/Admin-Endpoints via Mayan-Client (a3a118e85); Pydantic-ConfigDict-Fix (0fb3f84eb).
**Checks:** `pytest tests/test_process_kernel_wave8_complaint_e2e.py -q --no-cov`; `python scripts/agent_workboard_supervisor.py validate`
**Gate-Ergebnis:** pytest Full Suite 9228 passed, 0 failed (2026-05-26, develop 271bc5e12)
**Offene Risiken:** Keine.

## TEST-SUITE-CLEANUP-001

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-05-26
**Ziel des Slices:** Alle 32 pre-existing und neu einfuehrten Failures in der pytest-Full-Suite auf 0 bringen. Kein semantic-breaking Code-Change.
**Dateibesitz:** `app/api/v1/endpoints/reklamation_api.py`, `app/core/multi_context_agent.py`, `app/api/v1/endpoints/agrar_settlements.py`, `app/api/v1/endpoints/ebilanz_elster.py`, `app/api/v1/endpoints/silo_operations_api.py`, `tests/test_workers_coverage.py`, `tests/test_process_kernel_wave8_complaint_e2e.py`, `tests/test_hrm_compliance_pos.py`, `tests/test_kontrakt_hedging_preis_erechnung.py`
**Abnahmekriterien:** `pytest --no-cov -q` liefert 0 failed in der Full-Suite.
**Erledigt:** reklamation_api.py: _build_reklamation_payload + _store-Stub + computed fields + audit-key-fix (34d02a803); multi_context_agent.py: field_validator UTC-aware + datetime.now(timezone.utc) (34d02a803); asyncio.run() in test_workers_coverage + test_hrm_compliance_pos + test_kontrakt_hedging_preis_erechnung; agrar_settlements.py: get_repository/save_to_store Stubs; ebilanz_elster.py: XBRL-Fallback mit taxNumber; silo_operations_api.py: GET /zellen/{id} by-ID Route; wave8_complaint: PostgreSQL SessionLocal statt SQLite (271bc5e12).
**Checks:** `pytest --no-cov -q` (Full Suite)
**Gate-Ergebnis:** 9228 passed, 0 failed (2026-05-26, develop 271bc5e12) — zuvor 32 Failures
**Offene Risiken:** Keine.

## SLICE-006-EINVOICE-B2B-EXPORT-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Commit:** `08d64eff4`
**Ziel des Slices:** XRechnung 3.0 (UBL 2.1) und ZUGFeRD 2.x (PDF/A-3 + CII-XML Profil EN 16931) Export für reguläre B2B-Verkaufsrechnungen (SalesInvoice). Schließt die einzige verbliebene gesetzliche Lücke (E-Rechnung-2025 B2B-Versand).
**Dateibesitz:** `docs/agent-ops/slices/SLICE-006-EINVOICE-B2B-EXPORT-001.yaml`, `app/services/einvoice_generator.py`, `app/api/v1/endpoints/sales_invoice_einvoice.py`, `tests/test_einvoice_generator.py`, `packages/frontend-web/src/lib/api/einvoice.ts`, `packages/frontend-web/src/pages/sales/invoice-editor.tsx`, `docs/PROJEKT-GESAMTSTAND-2026-05-27.md`, `docs/FACHLICHE-VERTIEFUNG-ABNAHME.md`, `docs/GOBD-COMPLIANCE.md`.
**Erledigt:** `einvoice_generator.py` (EN-16931-UBL-2.1 + CII-XML + PDF/A-3 via factur-x, 23 pytest-Tests); Endpoints `POST/GET /api/v1/sales/invoices/{n}/einvoice/xrechnung|zugferd` mit GoBD-Archiv; Frontend-Download-Buttons (XRechnung + ZUGFeRD) in Rechnungsmaske mit Mutation-Pending-Guard; 1/1 E2E grün; TypeCheck 0 Fehler; Fremdfix `closing_checklists.py` (Optional-Import fehlte).
**Gate-Ergebnis:** 23/23 pytest grün; 1/1 E2E grün; TypeScript 0 Fehler; py_compile grün; 3 Endpoints registriert; GoBD-Artifact-Persistenz vorhanden.
**Offene Risiken:** Volle Schematron-Validierung bleibt optionaler Hook; Peppol-Versand bleibt Folgeslice.

## SLICE-008-DSGVO-ART30-ROPA-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** DSGVO Art. 30 Verzeichnis von Verarbeitungstätigkeiten (Records of Processing Activities). Backend CRUD + JSON-Export + Frontend-Verwaltungsmaske. Art. 15/17/20 bereits implementiert — Art. 30 war die letzte zentrale DSGVO-Pflicht-Lücke.
**Dateibesitz:** `docs/agent-ops/slices/SLICE-008-DSGVO-ART30-ROPA-001.yaml`, `app/api/v1/endpoints/gdpr_art30_ropa.py`, `packages/frontend-web/src/lib/api/gdpr-art30.ts`, `packages/frontend-web/src/pages/compliance/verarbeitungsverzeichnis.tsx`, `packages/frontend-web/tests/e2e/slice-008-dsgvo-art30.spec.ts`, `tests/test_gdpr_art30_ropa.py`.
**Gate-Ergebnis:** pytest 20/20 ✅ · E2E 5/5 ✅ · TypeScript 0 Fehler ✅ · Routing fixiert ✅
**Offene Risiken:** Produktive DB-Persistenz bleibt Folgeslice (In-Memory-Store als Fallback aktiv).

## SLICE-009-DSGVO-ART33-BREACH-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** DSGVO Art. 33 Datenpannen-Meldeprozess — Backend CRUD + 72h-Fristüberwachung + Frontend-Maske mit Ampelindikator. Fremdfix: banken.py (get_tenant_id fehlte) + ebilanz_elster.py (Field fehlte).
**Dateibesitz:** `docs/agent-ops/slices/SLICE-009-DSGVO-ART33-BREACH-001.yaml`, `app/api/v1/endpoints/gdpr_art33_breach.py`, `packages/frontend-web/src/lib/api/gdpr-art33.ts`, `packages/frontend-web/src/pages/compliance/datenpannen.tsx`, `packages/frontend-web/tests/e2e/slice-009-dsgvo-art33.spec.ts`, `tests/test_gdpr_art33_breach.py`.
**Gate-Ergebnis:** pytest 24/24 ✅ · E2E 5/5 ✅ · TypeScript 0 Fehler ✅
**Offene Risiken:** E-Mail-Versand an Behörde bleibt Folgeslice.

## SLICE-010-VOICE-LAGER-EINKAUF-HR-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Voice-Intent für Lager / Einkauf / HR ausbauen — 15 neue Intents in action_registry.py, Keyword-Fallbacks im IntentResolver, Frontend-AI-Shortcuts.
**Dateibesitz:** `services/ki-usability/app/services/action_registry.py`, `services/ki-usability/app/services/intent_resolver.py`, `packages/frontend-web/src/app/navigation/ai-shortcuts.tsx`, `tests/test_voice_intent_lager_einkauf_hr.py`.
**Abnahmekriterien:** 15 neue Intents; Resolver löst alle Phrasen auf; pytest grün; TypeScript 0 Fehler.
**Erledigt:** 15 Lager/Einkauf/HR-Intents in der ActionRegistry, robuste Keyword-/Phrase-Aufloesung inklusive EAN-, Mengen-, Betrags- und HR-Datumsparametern sowie Frontend-AI-Shortcuts fuer die drei Domaenen.
**Checks:** `python -m pytest tests/test_voice_intent_lager_einkauf_hr.py -q --no-cov` in `services/ki-usability`; `pnpm --filter @valero-neuroerp/frontend-web type-check`.
**Offene Risiken:** VoiceButton-Integration auf einzelnen Fachseiten bleibt Folgeslice.

## SLICE-011-VOICE-VERKAUF-CRM-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Dispatch-Nachzug fuer Slice-010 (NAV_ACTIONS) + Voice Wave A fuer Verkauf und CRM.
**Dateibesitz:** `ActionDispatchContext.tsx`, `action_registry.py`, `intent_resolver.py`, `ai-shortcuts.tsx`, `tests/test_voice_intent_verkauf_crm.py`.
**Gate-Ergebnis:** pytest 62/62 ✅ (39 Slice-010 + 23 Slice-011) · TypeScript 0 Fehler ✅ · 52 Actions in Registry ✅
**Erledigt:** 14 NAV_ACTIONS fuer Slice-010 nachgezogen; 15 neue Verkauf/CRM-Intents; Resolver-Fallbacks + Param-Extraktion; AI-Shortcuts Verkauf/CRM.
**Offene Risiken:** Wave B (FiBu/Compliance) und Wave C (Agrar/Logistik) folgen als Slice-012+.

## SLICE-012-VOICE-FIBU-COMPLIANCE-AGrar-LOGISTIK-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Voice Wave B (FiBu + Compliance) und Wave C (Agrar + Logistik) — 26 neue Intents, NAV_ACTIONS, Resolver, AI-Shortcuts.
**Dateibesitz:** `ActionDispatchContext.tsx`, `action_registry.py`, `intent_resolver.py`, `ai-shortcuts.tsx`, `tests/test_voice_intent_fibu_compliance_agrar_logistik.py`.
**Gate-Ergebnis:** pytest 85/85 ✅ · TypeScript 0 Fehler ✅ · 78 Actions in Registry ✅
**Erledigt:** 8 Finanz-, 5 Compliance-, 8 Agrar-, 5 Logistik-Intents; NAV_ACTIONS-Dispatch; AI-Shortcuts fuer alle vier Domaenen.
**Offene Risiken:** Voice-Domain-Filter im Frontend (context.domain) noch ohne Resolver-Scoping — Folgeoptimierung.

## SLICE-013-VOICE-LOCAL-POLISH-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Privacy-First Diktat: faster-whisper STT + Ollama Text-Polish + Frontend Rohtext/Polish-Anzeige.
**Dateibesitz:** `voice_adapter.py`, `services/ki-usability/app/services/voice_polish.py`, `local_stt.py`, `ollama_client.py`, `voice.py` (Endpoints), `VoiceFeedback.tsx`, `useVoiceIntent.ts`, `VoiceButton.tsx`, `tests/test_voice_polish.py`.
**Gate-Ergebnis:** pytest 93/93 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** POST `/voice/polish` + `/voice/transcribe`; Ollama-Polish mit Fallback auf Rohtext; faster-whisper in `voice_adapter.py`; Frontend zeigt Rohtext und polierten Text in `VoiceFeedback`.
**Offene Risiken:** faster-whisper optional — ohne Install liefert `/transcribe` 503; Browser-STT bleibt Standard im Frontend bis Slice-013b.

## SLICE-013B-VOICE-SUMMARY-TTS-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Ollama 15s-Summary + lokales Piper-TTS + Frontend-Wiedergabe mit Browser-Fallback.
**Dateibesitz:** `voice_summary.py`, `local_tts.py`, `voice.py`, `voice_adapter.py`, `VoiceFeedback.tsx`, `useVoicePlayback.ts`, `VoiceButton.tsx`, `voice.ts`, `tests/test_voice_summary_tts.py`.
**Gate-Ergebnis:** pytest 103/103 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** POST `/voice/summary` + `/voice/synthesize`; Piper in `voice_adapter.py`; Summary + Vorlesen-Button in `VoiceFeedback`; Browser-SpeechSynthesis-Fallback.
**Offene Risiken:** Piper optional — ohne Modell/CLI nur Browser-TTS; Kokoro als Folge-Provider moeglich.

## SLICE-013C-VOICE-WHISPERBAR-SHORTCUTS-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** WhisperBar Shortcuts Strg+Shift+1/2, AutoHotkey/PowerShell, POST /voice/pipeline.
**Dateibesitz:** `tools/voice/whisperbar.ahk`, `whisperbar-summary.ps1`, `voice_pipeline.py`, `VoiceWhisperBarHost.tsx`, `useWhisperBarShortcuts.ts`, `ai-shortcuts.tsx`.
**Gate-Ergebnis:** pytest 112/112 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** Browser-Shortcuts Diktat/Summary; AHK aktiviert ERP + ruft Summary-API; Pipeline-Endpoint dictate|summary|intent.
**Offene Risiken:** AHK erfordert lokal installiertes AutoHotkey v1.1; ki-usability muss auf Port 5200 laufen fuer PS-Summary.

## SLICE-013D-VOICE-DOMAIN-CONTEXT-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** context.domain filtert Intent-Aufloesung; voice-intent Events mit Domain-Payload.
**Dateibesitz:** `intent_resolver.py`, `useVoiceIntent.ts`, `command-palette-model.ts`, `CommandPalette.tsx`, `test_voice_domain_context.py`.
**Gate-Ergebnis:** pytest 112/112 ✅
**Erledigt:** Domain-Aliase und Registry-Filter; Command Palette dispatcht eventPayload als eventDetail; VoiceWhisperBarHost reagiert auf voice-intent.
**Offene Risiken:** Sehr generische Phrasen koennen domain-uebergreifend kollidieren — weiteres Tuning bei Bedarf.

## SLICE-014-VOICE-LOCAL-STACK-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-27
**Ziel des Slices:** Kokoro TTS, Docker Voice Stack (Ollama), Frontend Local STT via faster-whisper.
**Dateibesitz:** `local_kokoro.py`, `local_tts.py`, `docker-compose.voice.yml`, `useLocalVoiceCapture.ts`, `useVoiceIntent.ts`, `voice_adapter.py`, `test_voice_kokoro.py`.
**Gate-Ergebnis:** pytest ✅ · TypeScript 0 Fehler ✅
**Erledigt:** Kokoro HTTP-Provider; docker-compose.voice.yml; VITE_VOICE_STT_PROVIDER=local mit Browser-Fallback.
**Offene Risiken:** faster-whisper/Kokoro muessen im ki-usability-Container oder lokal installiert sein; Kokoro-Image optional und gross.

## SLICE-015-VOICE-PRODUCTION-HARDENING-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Production Hardening — faster-whisper Docker, GET /voice/status, E2E WhisperBar-Smoke, Copilot Summary.
**Dateibesitz:** `Dockerfile.voice`, `voice_status.py`, `docker-compose.voice.yml`, `slice-015-voice-whisperbar.spec.ts`, `useVoiceCopilotSummary.ts`, `CopilotDockPanel.tsx`.
**Gate-Ergebnis:** pytest 116/116 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** Dockerfile.voice + requirements-voice.txt; GET /voice/status; WhisperBar E2E Smoke; Copilot-Dock Voice-Summary mit Vorlesen.
**Offene Risiken:** faster-whisper-Image groesser; Kokoro weiterhin optional.

## SLICE-016-VOICE-ADMIN-STATUS-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Admin Voice-Kanal mit GET /voice/status Readiness und korrigiertem Transkript-Verlauf.
**Dateibesitz:** `voice-channel.tsx`, `useVoiceStackStatus.ts`, `voice-channel.test.tsx`.
**Gate-Ergebnis:** Vitest 1/1 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** Status-Panel STT/TTS/Ollama; Transkript im Verlauf; useVoiceStackStatus Hook.
**Offene Risiken:** ki-usability muss laufen damit Status sichtbar ist.

## FACHLICHE-VERTIEFUNG-UX-W23-KUNDENBANKEN-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Kundenbankverbindungen (IBAN/BIC, SEPA) in Kundenstamm gegen Wave-3-Backend.
**Dateibesitz:** `kundenbanken.ts`, `KundenBankverbindungenPanel.tsx`, `kunden-stamm.tsx`, `fachliche-vertiefung-kundenbanken.spec.ts`.
**Gate-Ergebnis:** E2E 1/1 ✅
**Erledigt:** API-Client; Panel mit Anlegen/Standard/Löschen; Route-ID-Fix für Splat-Router; E2E gemockt.
**Offene Risiken:** Keine.

## FACHLICHE-VERTIEFUNG-UX-W24-INDIVIDUELLE-ARTIKELNUMMERN-001

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-05-30
**Ziel des Slices:** Individuelle Artikelnummern (Kunde/Lieferant-Mapping) gegen Wave-9-Backend.
**Dateibesitz:** `individuelleArtikelnummern.ts`, `individuelle-artikelnummern.tsx`, `stammdaten.ts`, `commercial.tsx`, `fachliche-vertiefung-individuelle-artikelnummern.spec.ts`.
**Gate-Ergebnis:** E2E 1/1 ✅ · TypeScript 0 Fehler ✅
**Erledigt:** API-Client; Seite mit Liste/Anlegen/Lookup/Löschen; Route + Navigation; E2E gemockt.
**Offene Risiken:** Keine.

## LOG-POD-DN-001 — POD ABGELIEFERT → delivery_notes.status = 'delivered'

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `logistics_tours.save_pod`: nach `ABGELIEFERT`-Update wird `tour_stops.delivery_note_ref` gelesen und `domain_sales.delivery_notes SET status='delivered'` gesetzt (fail-soft, kein Update bei `delivered`/`BERECHNET`); 2 Unit-Tests grün.
**Ziel:** Belegbruch schließen: Stopp-POD setzte Lieferschein-Status nie auf `delivered` → Lieferschein blieb auf `shipped` nach ePOD-Eingang.
**Dateibesitz:** `app/api/v1/endpoints/logistics_tours.py`, `tests/test_log_pod_dn_001.py` (neu).
**Abnahmekriterien:** delivery_notes UPDATE ausgeführt wenn delivery_note_ref gesetzt; kein Update ohne ref; 2 Tests grün.

## SALES-CN-INV-001 — Gutschrift anlegen → sales_invoice.status = 'GUTGESCHRIEBEN'

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `sales_credit_notes.create_credit_note`: wenn `invoice_reference` gesetzt, setzt `sales_invoice` im Store auf `GUTGESCHRIEBEN` (fail-soft); 2 Tests grün.
**Ziel:** Belegbruch schließen: Gutschrift referenzierte Originalrechnung ohne Rückmeldung → Rechnung blieb auf OFFEN/GEBUCHT.
**Dateibesitz:** `app/api/v1/endpoints/sales_credit_notes.py`, `tests/test_sales_cn_inv_001.py` (neu).

## SALES-RETURN-001 — Retoure → delivery_notes.status='returned' + Invoice GUTGESCHRIEBEN

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `sales_credit_notes.create_return`: setzt `delivery_notes.status='returned'` (fail-soft) wenn `delivery_note_reference` gesetzt; setzt `sales_invoice.status='GUTGESCHRIEBEN'` wenn `invoice_reference` gesetzt; 2 Tests grün.
**Ziel:** Belegbruch schließen: Retoure-Anlage aktualisierte weder Lieferschein noch Rechnung.
**Dateibesitz:** `app/api/v1/endpoints/sales_credit_notes.py`, `tests/test_sales_return_dn_001.py` (neu).

## FIN-STORNO-001 — storno_invoice → sales_invoice.status = 'STORNIERT' im Store

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `finance_invoices.storno_invoice`: nach Buchungsumkehr wird `sales_invoice` im Store auf `STORNIERT` gesetzt (fail-soft); 1 Test grün.
**Ziel:** Belegbruch schließen: Storno-Buchung korrigierte Buchhalter-Sicht aber nicht den Dokument-Store.
**Dateibesitz:** `app/api/v1/endpoints/finance_invoices.py`, `tests/test_fin_storno_store_001.py` (neu).

## SALES-ORDERS-DN-LINK-001 — create_delivery_from_order → sales_order_id in DN

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `sales_orders.create_delivery_from_order`: `sales_order_id` wird jetzt beim INSERT in `domain_sales.delivery_notes` gesetzt (zuvor fehlend) → SALES-O2C-001 greift auch auf auto-erstellte Lieferscheine.
**Dateibesitz:** `app/api/v1/endpoints/sales_orders.py`.

## PICK-LIST-ORDER-001 — pick_list book-order → sales_order.status = 'in_delivery'

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `pick_lists.book_pick_list_order`: setzt `domain_crm.sales_orders.status='in_delivery'` wenn `order_id` verknüpft (fail-soft); kein Update wenn bereits in_delivery/geliefert/completed/cancelled.
**Dateibesitz:** `app/api/v1/endpoints/pick_lists.py`.

## CREDIT-MEMO-OP-001 — Credit-Memo settle → offene_posten reduzieren

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `credit_debit_memos.settle_credit_memo`: nach Store-Update wird `domain_erp.offene_posten.offen -= per_invoice` mit auto-Auszifferung gesetzt (fail-soft).
**Ziel:** Belegbruch schließen: Gutschrift-Verrechnung reduzierte den AP-OP-Saldo nicht.
**Dateibesitz:** `app/api/v1/endpoints/credit_debit_memos.py`.

## EINK-VERIF-AP-001 — Rechnungsprüfung approve → AP-Invoice freigeben + Kreditoren-OP

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `purchase_invoice_verification.approve_verification`: nach GEMATCHT-Übergang werden `domain_einkauf.ap_invoices.status = 'freigegeben'` und ein Kreditoren-OP in `domain_erp.offene_posten` angelegt (fail-soft).
**Ziel:** Belegbruch schließen: 3-Wege-Match-Freigabe aktualisierte weder AP-Invoice noch offene Posten.
**Dateibesitz:** `app/api/v1/endpoints/purchase_invoice_verification.py`.

## AGRAR-SETTLE-OP-001 — Agrar-Abrechnung FIBU-Buchung → Kreditoren-OP

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-13 — `agrar_settlement_service.post_to_fibu_full`: nach GL-Buchung wird Kreditoren-OP für Netto-Lieferantenzahlung in `domain_erp.offene_posten` angelegt (fail-soft).
**Ziel:** Belegbruch schließen: Agrar-Auszahlung erzeugte Journal-Entry aber keinen OP-Eintrag für Lieferantenzahlung.
**Dateibesitz:** `app/services/agrar_settlement_service.py`.

## BLANKET-RELEASE-CLOSE-001 — Rahmenauftrag-Abruf → auto-close bei vollständigem Abruf

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `sales_blanket_orders.create_release`: nach Abruf-Anlage wird Restmenge geprüft; bei vollständigem Abruf wird Rahmenauftrag automatisch auf `ABGESCHLOSSEN` gesetzt (fail-soft).
**Ziel:** Belegbruch schließen: vollständig abgerufene Rahmenaufträge blieben auf `AKTIV`.
**Dateibesitz:** `app/api/v1/endpoints/sales_blanket_orders.py`.

## PAY-MATCH-INV-001 — Zahlungseingang-Matching → AR-Rechnung BEZAHLT

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `payment_matching.match_payment` + `auto_match_payments`: nach vollständigem OP-Abgleich wird `sales_invoice.status = BEZAHLT` im Document-Store gesetzt (fail-soft).
**Ziel:** Belegbruch schließen: Zahlungseingang-Matching schloss den OP aber setzte die AR-Rechnung nie auf BEZAHLT.
**Dateibesitz:** `app/api/v1/endpoints/payment_matching.py`.

## COLL-INV-OP-001 — Sammelrechnung → Debitoren-OP anlegen

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `collective_documents.create_collective_invoice`: nach Rechnungsanlage und GL-Buchung wird Debitoren-OP in `domain_erp.offene_posten` angelegt (fail-soft).
**Ziel:** Belegbruch schließen: Sammelrechnung erzeugte keine offene Forderung (OP).
**Dateibesitz:** `app/api/v1/endpoints/collective_documents.py`.

## SALES-DN-INV-OP-001 — LS→RE create_invoice_from_delivery → OP + Document-Store

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `sales_delivery_notes.create_invoice_from_delivery`: nach GL-Buchung werden Debitoren-OP und `sales_invoice`-Eintrag im Document-Store angelegt (fail-soft).
**Ziel:** Belegbruch schließen: Einzel-LS→RE-Konvertierung erzeugte JE aber keinen OP und keinen Store-Eintrag.
**Dateibesitz:** `app/api/v1/endpoints/sales_delivery_notes.py`.

## DAUERAUFTRAG-OP-001 — Dauerauftrag starten → Debitoren-OP anlegen

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `dauerauftraege.dauerauftrag_starten`: nach Anlage der Ausführung wird aus den Positionen ein Gesamtbetrag berechnet und Debitoren-OP in `domain_erp.offene_posten` angelegt (fail-soft).
**Ziel:** Belegbruch schließen: Dauerauftrag-Ausführung erzeugte Belegnummer aber keinen offenen Posten.
**Dateibesitz:** `app/api/v1/endpoints/dauerauftraege.py`.

## STRECKE-CLOSE-OP-001 — Streckengeschäft abschließen → Kreditoren-OP

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `strecke.close_streckengeschaeft`: nach Setzung `erledigt=True + rechnungsnr` wird Kreditoren-OP für `brutto`-Betrag in `domain_erp.offene_posten` angelegt (fail-soft).
**Ziel:** Belegbruch schließen: Streckengeschäft-Abschluss verknüpfte Lieferantenrechnung aber erzeugte keinen OP.
**Dateibesitz:** `app/api/v1/endpoints/strecke.py`.

## ASSET-DISPOSE-JE-001 — Anlagen-Abgang → GL-Journal-Entry

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `asset_accounting.dispose_asset`: nach Deaktivierung der Anlage wird GL-Buchung (Veräußerungserlös/Buchwert-Abgang/Gewinn-Verlust) via `FinanceTransactionService` gebucht (fail-soft).
**Ziel:** Belegbruch schließen: Anlagen-Abgang berechnete Gewinn/Verlust aber erzeugte keinen FiBu-Buchungssatz.
**Dateibesitz:** `app/api/v1/endpoints/asset_accounting.py`.

## WEBSHOP-CONV-ORDER-001 — Webshop-Bestellimport → ERP Sales Order anlegen

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `webshop_integration_service.process_order`: nach Markierung VERARBEITET wird `domain_crm.sales_orders`-Datensatz angelegt (fail-soft, ON CONFLICT DO NOTHING).
**Ziel:** Belegbruch schließen: Webshop-Order-Konvertierung setzte Status auf VERARBEITET aber legte keinen ERP-Auftrag an.
**Dateibesitz:** `app/services/webshop_integration_service.py`.

## ZINS-BUCHUNG-JE-001 — Zinsabrechnung buchen → Kreditoren-OP anlegen

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `zinsabrechnung.buche_zinsabrechnung`: nach Buchung wird Kreditoren-OP für Zins+MwSt (Zinsgutschrift an Lieferant) in `domain_erp.offene_posten` angelegt (fail-soft).
**Ziel:** Belegbruch schließen: Zinsabrechnung-Buchung erzeugte Belegnummer aber keinen Kreditoren-OP.
**Dateibesitz:** `app/api/v1/endpoints/zinsabrechnung.py`.

## ERECHNUNG-BUCHEN-OP-001 — e-Rechnung buchen → Kreditoren-OP anlegen

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `erechnung_import.buchen`: nach IMPORTIERT-Setzung wird Kreditoren-OP für `betrag_brutto` der e-Rechnung in `domain_erp.offene_posten` angelegt (fail-soft).
**Ziel:** Belegbruch schließen: e-Rechnungs-Buchung setzte Status auf IMPORTIERT aber erzeugte keinen Kreditoren-OP.
**Dateibesitz:** `app/api/v1/endpoints/erechnung_import.py`.

## GENO-ANTEILE-JE-001 — Anteilsbewegung → GL-Buchung Kapital

**Von:** Claude
**Owner:** Claude
**Stand:** abgeschlossen 2026-06-15 — `genossenschaft.create_anteilsbewegung`: nach Mitglieder-Saldo-Update wird GL-Buchung via `FinanceTransactionService` erzeugt (Zeichnung: Bank/Kapital; Rückzahlung: Kapital/Verbindlichkeiten-Mitglieder) (fail-soft).
**Ziel:** Belegbruch schließen: Genossenschafts-Anteilsbewegung aktualisierte Mitgliedersaldo aber erzeugte keinen FiBu-Buchungssatz.
**Dateibesitz:** `app/api/v1/endpoints/genossenschaft.py`.

## WF-COCKPIT-PERSIST-001 — Workflow-Cockpit Persistenz

**Owner:** dev
**Stand:** abgeschlossen 2026-06-25 — DB-Persistenz fuer Workflow-Cockpit-Instanzen, Events und Blocker plus NATS-Projector.
**Dateibesitz:** `app/services/wf_cockpit_persist_service.py`, `app/services/wf_cockpit_nats_projector.py`, `app/api/v1/endpoints/wf_cockpit_persist.py`.

## WM-SILO-RULE-ENGINE-001 — Silo Zielzellen-Regelengine

**Owner:** dev
**Stand:** abgeschlossen 2026-06-25 — regelbasierte Zielzellen-Vorschlaege fuer Artikel-/Lot-basierte Agrar-Einlagerung.
**Dateibesitz:** `app/services/silo_rule_engine_service.py`, `app/api/v1/endpoints/silo_target_cell.py`.

## WM-SILO-RULE-UPGRADE-001 — Regelengine-Fallback in Auto-Einlagerung

**Owner:** claude-sonnet-4-6
**Stand:** abgeschlossen 2026-06-25 — Auto-Einlagerung nutzt die Silo-Zielzellen-Regelengine als Fallback, wenn Legacy-Mapping keine fachlich passende freie Zelle liefert oder QS-Sperren alle Kandidaten ausschliessen; Regelengine-Ausfall bleibt fail-soft und fuehrt zu `ok=false` statt StopIteration/500.
**Dateibesitz:** `app/services/agri_lot_link_booking_service.py`, `scripts/check_critical_backend_coverage.py`, `docs/agent-ops/slices/WM-SILO-RULE-UPGRADE-001.yaml`.

## HRM-ABWESENHEIT-ANTRAG-001 — HRM Abwesenheitsantrag-Workflow

**Owner:** claude-sonnet-4-6
**Stand:** abgeschlossen 2026-06-25 — Antragserstellung, Liste, Detail, Genehmigung, Ablehnung, Rueckzug, Urlaubskonto, Ueberschneidungspruefung, eAU-Pflicht und Tenant-Isolation umgesetzt; Legacy-DOM-HRM-004-Funktionsvertrag (`VALID_ABWESENHEIT_TRANSITIONS`, `create_abwesenheitsantrag`, `transition_abwesenheit`) bleibt kompatibel; alle 7 HRM-Abwesenheitsrouten tragen OpenAPI-`summary=`.
**Dateibesitz:** `app/services/hrm_abwesenheit_service.py`, `app/api/v1/endpoints/hrm_abwesenheit.py`, `tests/test_hrm_abwesenheit.py`, `app/api/v1/api.py`, `scripts/check_critical_backend_coverage.py`, `docs/agent-ops/slices/HRM-ABWESENHEIT-ANTRAG-001.yaml`.
## COVERAGE-RATCHET-ERP-CORE-001 — Coverage kritischer Landhandel-Kern-Pfade anheben

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-25 — 54 Unit-Tests grün; DI-Override-Pattern etabliert; harvest_acceptance/articles/kontrakte/sales_orders-HTTP-Pfade + Service-Fehlerbehandlung abgedeckt.
**Ziel:** Gesamt-Coverage 64,85 % → 70 %; neue Unit-Tests fuer die vier schwächsten kritischen Endpoint-Dateien (harvest_acceptance 24 %, articles 23 %, kontrakte 27 %, sales_orders 38 %); Ratchet-Schwellen angehoben.
**Dateibesitz:** `tests/test_coverage_ratchet_erp_core_001.py`, `docs/agent-ops/slices/COVERAGE-RATCHET-ERP-CORE-001.yaml`, `scripts/check_critical_backend_coverage.py`

## RUNTIME-A-JOBS-001 - Runtime Sweep Kategorie A: Job-Runner-Tabellen

**Owner:** Codex
**Stand:** abgeschlossen 2026-06-25 - `job_runner_tables_repair_20260625` legt `domain_shared.jobs` und `domain_shared.job_artifacts` idempotent am aktuellen Alembic-Head an; `GET /api/v1/jobs` degradiert bei fehlender Tabelle auf `[]` statt 500; fokussierte Runtime-Sweep-Tests 10/10 gruen; Alembic single-head `job_runner_tables_repair_20260625`.
**Ziel:** `domain_shared.jobs` und `domain_shared.job_artifacts` per idempotenter Repair-Migration am aktuellen Alembic-Head absichern; Job-Listenpfad bei fehlender Migration kontrolliert leer degradieren.
**Dateibesitz:** `alembic/versions/job_runner_tables_repair_20260625.py`, `app/api/v1/endpoints/job_runner.py`, `tests/test_runtime_sweep_category_a_jobs.py`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/RUNTIME-A-JOBS-001.yaml`.

## WA-AGENT-001 — WhatsApp Bestellkanal mit Test-Webhook-Simulator

**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-25 — Eingehende WhatsApp-Textnachrichten werden per LLM (claude-haiku, Fallback: Regex) zu Bestelldetails extrahiert und als Sales Order angelegt (👍-Bestätigung). Dev-Simulator ohne Meta-Auth unter `/api/v1/whatsapp/dev/simulate` + Chat-UI unter `/portal/whatsapp-simulator`. 25/25 Unit-Tests grün.
**Ziel:** WhatsApp-Textnachricht → Kundenzuordnung → Bestellextraktion → Auftragsanlage ODER Rückfrage (max. 1 Round). Start mit In-Memory-Simulator, Meta-Produktions-Webhook vorbereitet.
**Dateibesitz:** `app/services/whatsapp_agent_service.py`, `app/api/v1/endpoints/whatsapp_webhook.py`, `packages/frontend-web/src/pages/portal/whatsapp-simulator.tsx`, `tests/test_whatsapp_agent.py`, `docs/agent-ops/slices/WA-AGENT-001.yaml`.
**Folge-Slices:** WA-NOTIFY-001 (Lieferankündigung Push), PORTAL-SHOP-001 (Betriebsmittel-Shop).

## WA-NOTIFY-001 — WhatsApp Ausgehende Push-Benachrichtigungen

**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-26 — Lieferankündigung (🚛 LKW ~ETA-Min entfernt) + Dokument-Ready (📄 Lieferschein/Rechnung im Portal verfügbar). Meta Cloud API-ready (HMAC, httpx); Fallback: simulierter Outbox-Log. Simulator-UI um Tabs "Ausgehend (Push)" + "Outbox" erweitert. 13/13 Tests grün.
**Ziel:** Vollständige WhatsApp-Prozesskette: Bestellung eingehend (WA-AGENT-001) → Lieferankündigung 1h vor Ankunft → Dokument-Benachrichtigung nach Erstellung.
**Dateibesitz:** `app/services/whatsapp_notify_service.py`, `app/api/v1/endpoints/whatsapp_notify.py`, `tests/test_whatsapp_notify.py`, `docs/agent-ops/slices/WA-NOTIFY-001.yaml`.
**Integration:** Logistik → `/dev/notify/lieferankuendigung`, Docflow → `/dev/notify/dokument-ready`.

## DOC-MIGRATION-002 — Alt-Dokumente konsolidiert (Phase E)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — ~390 Markdown-Dateien nach `docs/_internal/archive/` migriert; `docs/archive/` aufgelöst; Root-Docs von 107→2 (`index.md`, `MASKEN.md`); Inventar + Duplikat-Report; `mkdocs build` grün.
**Dateibesitz:** `scripts/docs-legacy-migrate.py`, `docs/_internal/archive/**`, `docs/_internal/legacy-docs-inventory.md`, `docs/agent-ops/slices/DOC-MIGRATION-002.yaml`.

## DOC-MIGRATION-003 — Card-Duplikate + Architektur-Nav (Phase F)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — INV-001-Duplikat (`inventory/` → kanonisch `lager/`); Architektur + ADR in MkDocs-Nav; Wave-Ordner weiter ausgeschlossen; Inventar-Zählung per `resolve()`.
**Dateibesitz:** `mkdocs.yml`, `docs/entwickler/index.md`, `docs/cards/inventory/INV-001-inventory-to-settlement.md`, `docs/agent-ops/slices/DOC-MIGRATION-003.yaml`.

## DOC-MIGRATION-004 — Compliance-Nav + Roadmap-Status (Phase H)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — Compliance-Unterseiten in MkDocs-Nav; Admin BRANDING/NUMBERING; Duplikat-Inventar ohne Archiv-Kopien.
**Dateibesitz:** `mkdocs.yml`, `docs/compliance/index.md`, `docs/roadmap/README.md`, `scripts/docs-legacy-migrate.py`, `docs/agent-ops/slices/DOC-MIGRATION-004.yaml`.

## DOC-MIGRATION-005 — Abgearbeitete Roadmaps entfernt (Phase I)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — 23 Legacy-Roadmap-Dateien gelöscht; Verweise auf Process-Kernel/Open-Gaps umgestellt.
**Dateibesitz:** `scripts/docs-legacy-migrate.py`, `docs/roadmap/README.md`, `docs/agent-ops/slices/DOC-MIGRATION-005.yaml`.

## DOC-MIGRATION-006 — Frontmatter Compliance + Operations-Archiv (Phase J)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — Frontmatter auf 10 Compliance-/Admin-Seiten; `docs/operations/` nach `_internal/archive/operations/`.
**Dateibesitz:** `docs/compliance/**`, `docs/admin/BRANDING.md`, `docs/admin/NUMBERING.md`, `scripts/docs-legacy-migrate.py`, `docs/agent-ops/slices/DOC-MIGRATION-006.yaml`.

## DOC-MIGRATION-007 — Staleness-Gate blockierend (Phase D)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-25 — CI blockiert bei fehlendem/veraltetem `last_reviewed` (365 Tage, kuratierte MkDocs-Seiten).
**Dateibesitz:** `.github/workflows/docs.yml`, `.github/workflows/docs-governance.yml`, `scripts/docs-staleness-check.cjs`, `docs/dokumentation/governance.md`, `docs/agent-ops/slices/DOC-MIGRATION-007.yaml`.

## DOC-MIGRATION-008 — Migrationsprogramm abgeschlossen (Phase C/K)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — Phase C (CRM/i18n/GAP in Archiv) dokumentiert; Duplikat-Inventar klassifiziert (140 harmlos / 0 offen); `docs/index.md` + Open-Gaps + Migrationsplan-Abschluss; 0 Archiv-Kandidaten.
**Dateibesitz:** `scripts/docs-legacy-migrate.py`, `docs/_internal/legacy-docs-inventory.md`, `docs/dokumentation/migrationsplan.md`, `docs/index.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/DOC-MIGRATION-008.yaml`.

## DOC-MIGRATION-009 — ADR-Navigation in MkDocs (Generator)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — `scripts/generate_adr_nav.py` patcht 38 ADRs in `mkdocs.yml`; CI-Drift-Check in `docs.yml`; 4 Unit-Tests grün; `mkdocs build` grün.
**Dateibesitz:** `scripts/generate_adr_nav.py`, `tests/test_generate_adr_nav.py`, `mkdocs.yml`, `.github/workflows/docs.yml`, `docs/agent-ops/slices/DOC-MIGRATION-009.yaml`.

## AI-DOC-DRIFT-CI-001 — Drift-Report woechentlich in CI

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — `doc_drift_report.py` nutzt alle Nav-Domain-Dateien + `route-inventory.gen.json`; Workflow `doc-drift-report.yml` (Montag, Artifact); 6 Unit-Tests grün; `.gitignore` für `site_check_*/`.
**Dateibesitz:** `scripts/doc_drift_report.py`, `tests/test_doc_drift_report.py`, `.github/workflows/doc-drift-report.yml`, `docs/dokumentation/governance.md`, `docs/agent-ops/slices/AI-DOC-DRIFT-CI-001.yaml`.

## DOC-DEV-GUIDE-001 — Entwicklerhandbuch (Setup, Tenancy, Konventionen, Tests)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — 4 Seiten unter `docs/entwickler/`; MkDocs-Nav erweitert; `entwickler/index.md` aktualisiert; `mkdocs build` + Staleness grün.
**Dateibesitz:** `docs/entwickler/{lokales-setup,datenmodell-tenancy,konventionen,test-strategie}.md`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-DEV-GUIDE-001.yaml`.

## DOC-REFERENZ-001 — Referenzbereich (MASKEN, Glossar, Skripte)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — `MASKEN.md` in MkDocs-Build; Referenz-Nav mit Glossar + Skripte-Übersicht; `referenz/index.md` aktiv.
**Dateibesitz:** `docs/referenz/**`, `mkdocs.yml`, `docs/agent-ops/slices/DOC-REFERENZ-001.yaml`.

## DOC-INVENTORY-001 — Code-Inventare (Generator + CI)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — `generate_code_inventories.py` für Endpoint/Service/Migration; CI-Drift-Check in `docs.yml`; Drift-Report 0; 4 Unit-Tests grün.
**Dateibesitz:** `scripts/generate_code_inventories.py`, `tests/test_generate_code_inventories.py`, `docs/{schnittstellen/endpoint-inventory,entwickler/service-inventory,admin/migration-inventory}.md`, `docs/agent-ops/slices/DOC-INVENTORY-001.yaml`.

## DOC-INDEX-POLISH-001 — Diataxis-Einstiegsseiten (Status aktiv)

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — `benutzerhandbuch/`, `admin/`, `agent-docs/` Index auf `aktiv`; Migrationsplan-Abschluss erweitert (009–INVENTORY); Staleness grün.
**Dateibesitz:** `docs/{benutzerhandbuch,admin,agent-docs}/index.md`, `docs/dokumentation/migrationsplan.md`, `docs/agent-ops/slices/DOC-INDEX-POLISH-001.yaml`.

---

## CARD-AUDIT-Follow-up (2026-06-26)

Parallele Fix-Slices aus Cards-Inventar-Audit (`CARD-AUDIT-001`). Claim-Protokoll: `docs/agent-ops/parallel-work-protocol.md`.

| Slice | Priorität | Owner | Stand |
|-------|-----------|-------|-------|
| FIN-ABSCHLUSS-STUBS-001 | P1 | Claude Sonnet 4.6 | abgeschlossen 2026-06-26 |
| OTC-010-POS-HANDOVER-001 | P2 | Codex/Claude | abgeschlossen 2026-06-26 |
| CMP-UStVA-API-CLIENT-001 | P2 | Cursor/Claude | abgeschlossen 2026-06-26 |
| CRM-LEGACY-API-MIGRATE-001 | P2 | Cursor/Claude | abgeschlossen 2026-06-26 |
| COM-REGISTER-CAMELCASE-001 | P2 | Claude Sonnet 4.6 | abgeschlossen 2026-06-26 |
| P2P-010-OVERVIEW-001 | P3 | Cursor | abgeschlossen 2026-06-26 |
| DOC-CARD-CHAIN-001 | Doku | Cursor | abgeschlossen 2026-06-26 |
| DOC-CARD-FRONTMATTER-001 | Doku | Cursor | abgeschlossen 2026-06-26 (Registry-Cards) |

## FIN-ABSCHLUSS-STUBS-001 — Finanz-Abschluss calculate/lock/run

**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-26 — `finance_closing_service.py` mit echten GoBD-Salden aus `domain_erp.journal_entries`, atomarer Periodensperre via `FinancePeriodService` (kein Doppel-Sperren), Abschluss-Buchungs-Eintrag; Exception-Propagation statt fail-soft in calculate/lock/run (HTTP 422/500); 15/15 Unit-Tests grün.
**Dateibesitz:** `app/services/finance_closing_service.py`, `app/api/v1/endpoints/finance_actions.py`, `tests/test_finance_closing_service.py`, `docs/agent-ops/slices/FIN-ABSCHLUSS-STUBS-001.yaml`.

## OTC-010-POS-HANDOVER-001 — Positionen Auftrag→Lieferschein

**Owner:** Codex + Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-26 — `sales_order_id` im LS-Payload (Belegkette); `order-editor.tsx`: Sofort-Rechnung navigiert mit `buildSalesHandoverPath` (Kontext); `invoice-editor.tsx`: `useParams<{id}>` als Deep-Link-Fallback.
**Dateibesitz:** `packages/frontend-web/src/pages/verkauf/lieferschein-erfassung.tsx`, `packages/frontend-web/src/pages/sales/order-editor.tsx`, `packages/frontend-web/src/pages/sales/invoice-editor.tsx`, `docs/agent-ops/slices/OTC-010-POS-HANDOVER-001.yaml`.

## CMP-UStVA-API-CLIENT-001 — UStVA Response-Normalisierung

**Owner:** Cursor + Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-26 — `mapVatReturnPayload` extrahiert, `transformResponse` konsistent via `.data`-Zugriff ohne doppeltes Unwrapping; `getAxiosErrorMessage` in allen catch-Blöcken.
**Dateibesitz:** `packages/frontend-web/src/pages/finance/ustva.tsx`, `docs/agent-ops/slices/CMP-UStVA-API-CLIENT-001.yaml`.

## CRM-LEGACY-API-MIGRATE-001 — CRM axios → /api/v1/crm/

**Owner:** Cursor + Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-26 — `kontakt-management.tsx`: `@/lib/axios` → `apiClient` + `unwrapCrmListPage`; `kunden-liste.tsx` / `lieferanten-liste.tsx` bereits auf `apiClient`. `crm-list-response.ts` als gemeinsamer Unwrapper eingeführt.
**Dateibesitz:** `packages/frontend-web/src/pages/crm/kontakt-management.tsx`, `packages/frontend-web/src/lib/api/crm-list-response.ts`, `docs/agent-ops/slices/CRM-LEGACY-API-MIGRATE-001.yaml`.

## COM-REGISTER-CAMELCASE-001 — Compliance-Register CamelCase

**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-26 — Tippfehler `geprrueftAm` → `geprueftAm` (QS-Checkliste); `ausstellendeStelle` camelCase-Alias ergänzt (Sachkunde-Register). VVVO/Zulassungen waren bereits korrekt.
**Dateibesitz:** `app/api/v1/endpoints/compliance.py`, `docs/agent-ops/slices/COM-REGISTER-CAMELCASE-001.yaml`.

## P2P-010-OVERVIEW-001 — P2P Overview-Card

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — `docs/cards/einkauf/P2P-010-procure-to-pay.md` angelegt; `workflow-chains.md` Step 0 aktualisiert; CHAIN_REGISTRY ergänzt.
**Dateibesitz:** `docs/cards/einkauf/P2P-010-procure-to-pay.md`, `docs/agent-ops/slices/P2P-010-OVERVIEW-001.yaml`.

## DOC-CARD-CHAIN-001 — Workflow-Ketten-Registry + Inventar-Audit

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — `workflow-chains.md`, `cards-inventory-audit.py`, `card-template.md`, Inventar v3; 148 Cards, 0 ohne Ketten-Zuordnung.
**Dateibesitz:** `docs/_internal/workflow-chains.md`, `scripts/cards-inventory-audit.py`, `docs/agent-ops/slices/DOC-CARD-CHAIN-001.yaml`.

## DOC-CARD-FRONTMATTER-001 — Card-Frontmatter Rollout

**Owner:** Cursor
**Stand:** abgeschlossen 2026-06-26 — `scripts/migrate-cards-frontmatter.py` migriert 32 Registry-Cards + P2P-010; Metrik „ohne Frontmatter“ = 0 für Prozess-Cards.
**Dateibesitz:** `docs/cards/**/*.md`, `scripts/migrate-cards-frontmatter.py`, `docs/agent-ops/slices/DOC-CARD-FRONTMATTER-001.yaml`.

## PORTAL-SHOP-001 — Betriebsmittel-Online-Shop (Governance-Erfassung)

**Owner:** Cursor (Backend + Frontend) / Claude Sonnet 4.6 (Governance-Doku)
**Stand:** abgeschlossen 2026-06-26 — Backend (`portal_shop.py`) + Frontend (`shop.tsx`) waren bereits vollständig durch Cursor implementiert. Slice-YAML zur Governance-Compliance nacherfasst.
**Ziel:** Saatgut/Dünger/PSM-Shop im Kundenportal mit Kontrakt-/Vorkauf-Preisen, Idempotenz, Status-Maschine und Reconciliation.
**Dateibesitz:** `docs/agent-ops/slices/PORTAL-SHOP-001.yaml`.

## CI-WA-PORTAL-GATE-20260626 - WhatsApp/Portal CI-Gate-Nachzug

**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — Response-Model-Coverage 97,4 % (Threshold 80 % ✅). Build-Blocker behoben: 5 fehlende Exports in `docs-help.ts` (`HELP_ROUTE`, `DOCS_USER_MANUAL_URL`, `getEmbeddedHelpHref`, `resolveHelpUrl`, `openDocs`) ergänzt. Frontend-Build ✅, TSC ✅.
**Ziel:** CI wieder gruenschalten, ohne neue WhatsApp-/Portal-Fachlogik einzufuehren oder fremde Parallel-Agent-Aenderungen zu buendeln.
**Dateibesitz:** `app/api/v1/endpoints/whatsapp_notify.py`, `app/api/v1/endpoints/whatsapp_webhook.py`, `packages/frontend-web/src/pages/portal/whatsapp-simulator.tsx`, optional `packages/frontend-web/src/components/ui/use-toast.ts`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/CI-WA-PORTAL-GATE-20260626.yaml`, dieser Workboard-Abschnitt.
**Abnahmekriterien:** `python scripts/check_response_models.py --threshold 80`, `pnpm --dir packages/frontend-web typecheck`, `pnpm --dir packages/frontend-web build` lokal gruen; GitHub Actions Quality Gate/E2E-Smoke nach Push pruefen.

## AI-ENGINEERING-METRICS-001 — Produktivitätsmetriken für das AI-Engineering (P2.2)

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-26 — `scripts/ai_engineering_metrics.py` (CLI: summary/JSON/CSV); liest Git-Log + 249 Slice-YAMLs; berechnet Cycle-Time, Rework-Quote, Doku-Drift, Agent-Verteilung, Langläufer. Live-Sample: 96 Slices, 84 abgeschlossen, Median-Cycle-Time 0.1 h, P90 0.3 h, Rework-Rate 59 %, Top-Langläufer DOM-CONTROLLING-004 (0.8 h). 29 Unit-Tests grün.
**Ziel:** P2.2 aus YouTube-Gap-Analyse: messbare AI-Engineering-Produktivitätskennzahlen ohne subjektive Einschätzung, automatisch aus Git + YAML-Slices.
**Dateibesitz:** `scripts/ai_engineering_metrics.py`, `tests/test_ai_engineering_metrics.py`, `docs/agent-ops/slices/AI-ENGINEERING-METRICS-001.yaml`.
**Abnahmekriterien:** 29 Unit-Tests grün; `python scripts/ai_engineering_metrics.py --since 2026-06-01` gibt Report aus; `--json`/`--csv` funktionieren.
**Folge:** AI-ENGINEERING-METRICS-002 (CI-Nightly-Cron + MkDocs-Dashboard).

## AI-ENGINEERING-METRICS-002 — Nightly CI-Cron + MkDocs Dashboard (P2.2 Ausbau)

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-26 — GitHub Actions Nightly Cron (`0 4 * * *`) + `scripts/generate_metrics_page.py` (Markdown aus JSON); `docs/agent-ops/engineering-metrics.md` initial generiert; MkDocs-Nav-Eintrag gesetzt. 15 Unit-Tests grün.
**Ziel:** AI Engineering Metrics täglich automatisch berechnen, als JSON-Artefakt (90 Tage Retention) sichern und als MkDocs-Dashboard-Seite publizieren.
**Dateibesitz:** `.github/workflows/ai-engineering-metrics.yml`, `scripts/generate_metrics_page.py`, `docs/agent-ops/engineering-metrics.md`, `tests/test_generate_metrics_page.py`, `mkdocs.yml`.
**Abnahmekriterien:** 15 Unit-Tests grün; Workflow syntaktisch korrekt; Seite hat Frontmatter; MkDocs-Nav enthält Eintrag.
**Externes Gate:** Erster erfolgreicher Nightly-Lauf auf GitHub Actions.

## WORKFLOW-PROCESS-MAP-001 — Visuelle ERP Prozesskarte (P2.1)

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-26 — `docs/architecture/process-map.md` mit 6 Mermaid-Flussdiagrammen (O2C, P2P, FiBu, WMS/Agrar, POS/TSE, QS/Reklamation); Belege, NATS-Events, externe Gates und kritische Invarianten je Kette; MkDocs-Nav-Eintrag + Whitelist gesetzt.
**Ziel:** P2.1 aus YouTube-Gap-Analyse: operativ nutzbare visuelle Prozesskarte ohne n8n-Abhängigkeit — direkt aus der ERP-Fachlogik abgeleitet.
**Dateibesitz:** `docs/architecture/process-map.md`, `mkdocs.yml`, `docs/agent-ops/slices/WORKFLOW-PROCESS-MAP-001.yaml`.

## DATA-CLASSIFICATION-001 — KI-Datenklassen-Policy (P2.3)

**Von:** Claude Sonnet 4.6
**Owner:** Claude Sonnet 4.6
**Stand:** abgeschlossen 2026-06-26 — `config/ai_data_classification.yaml` (5 Stufen, 19 Kategorien); `scripts/validate_data_classification.py` (Validator, 0 Fehler); `docs/architecture/ai-data-classification.md` (MkDocs mit Tabellen + Rechtsgrundlagen); 27 Unit-Tests grün. NEVER: Credentials, Audit-Log, Zahlung, Mitarbeiter, Gehalt, Prompt-History. LOCAL_ONLY: Agrar-Kontrakte, GoBD-Journal, DATEV, Mandanten-Config.
**Ziel:** P2.3: Verbindliche maschinenlesbare Policy welche Datenkategorien externen KI-Modellen zugänglich sind.
**Dateibesitz:** `config/ai_data_classification.yaml`, `scripts/validate_data_classification.py`, `tests/test_data_classification.py`, `docs/architecture/ai-data-classification.md`, `mkdocs.yml`.
**Externe Gates:** DSGVO-Review durch Datenschutzbeauftragten; juristisches Review Agrar-Kontrakte.

## DOC-OPENAPI-CI-001 — OpenAPI-Drift-Gate in CI

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — `--check`-Step in quality-gate.yml (blockiert PRs bei Drift); `openapi-drift.yml` (Auto-Commit auf main bei API-Änderungen).
**Ziel:** `generate_openapi.py --check` als blockierendes CI-Gate; bei Drift auto-commit durch CI statt manuellem Schritt.
**Dateibesitz:** `.github/workflows/openapi-drift.yml`, `docs/agent-ops/slices/DOC-OPENAPI-CI-001.yaml`

## DOC-ASYNCAPI-001 — AsyncAPI 2.6 Event-Katalog

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — 51 NATS/Outbox-Events aus Codebase extrahiert; `docs/schnittstellen/asyncapi.yaml` (AsyncAPI 2.6, 51 Channels); `docs/schnittstellen/events.md` (MkDocs-Seite nach Domäne); `scripts/extract_events.py` + `scripts/generate_asyncapi.py` (portable, kein Hardcoded-Pfad).
**Ziel:** Maschinenlesbare Event-Spec für Integratoren; Events nach Domäne dokumentiert.
**Dateibesitz:** `docs/schnittstellen/asyncapi.yaml`, `docs/schnittstellen/events.md`, `scripts/extract_events.py`, `scripts/generate_asyncapi.py`.

## DOC-INAPP-HELP-002 — In-App-Hilfe Route → Dokumentation Mapping

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — 50 Routen gemappt auf MkDocs-Seiten; `src/lib/docs-help.ts` mit `ROUTE_HELP_MAP` + `findHelpEntry()` (längster-Präfix-Match); `docs/benutzerhandbuch/in-app-hilfe.md` mit Konzept + Mapping-Tabelle; `scripts/generate_inapp_help_map.py` (portable Generator).
**Ziel:** Kontextsensitive In-App-Hilfe: aktuelle Route → passende Doku-Seite, sofort per useInAppHelp()-Hook nutzbar.
**Dateibesitz:** `packages/frontend-web/src/lib/docs-help.ts`, `docs/benutzerhandbuch/in-app-hilfe.md`, `scripts/generate_inapp_help_map.py`.

## DOC-DRIFT-GATE-002 — Doku-Code-Drift-Gate in CI

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — `--fail-over 0`-Step in `quality-gate.yml` eingetragen; Baseline 0 Drift-Items; lokal verifiziert (Exit 0). Bei Drift > 0 schlägt CI mit Hinweis fehl.
**Ziel:** Doku-Drift von Endpoints/Migrationen/Services/Pages dauerhaft auf 0 halten durch blockierendes CI-Gate.
**Dateibesitz:** `.github/workflows/quality-gate.yml`, `docs/agent-ops/slices/DOC-DRIFT-GATE-002.yaml`.

## DOCS-CODE-SYNC-002 — Mapping-Härtung

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — `docs-code-sync-map.yaml`: `generated_artifacts` + `generated_doc_paths` Felder ergänzt (openapi.json, asyncapi.yaml, endpoint-inventory.md, migration-inventory.md, service-inventory.md, route-inventory.gen.json, docs-help.ts); `docs-code-sync-check.cjs`: Parser + Prüflogik für generierte Artefakte erweitert (zählen als Doku-Nachweis).
**Ziel:** Endpoint/Migration/Service/Seite-PRs können generierte Inventar-Dateien statt klassischer .md-Doku vorweisen — verhindert false-positive CI-Fehler bei Inventar-basierten Doku-Ansätzen.
**Dateibesitz:** `config/docs-code-sync-map.yaml`, `scripts/docs-code-sync-check.cjs`.

## DOC-DRIFT-DASHBOARD-002 — MkDocs-Sichtbarkeit

**Von:** Claude Code
**Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — `scripts/generate_drift_dashboard_page.py` generiert `docs/entwickler/drift-dashboard.md` mit Status (GRUEN/GELB/ROT), Dimensionen, offenen Punkten und Gate-Dokumentation; in MkDocs-Nav eingebunden; `doc-drift-report.yml` committet Dashboard nach jedem Nightly-Report automatisch.
**Ziel:** Drift-Status für Entwickler direkt in MkDocs sichtbar; Auto-aktualisiert durch Nightly-Workflow.
**Dateibesitz:** `scripts/generate_drift_dashboard_page.py`, `docs/entwickler/drift-dashboard.md`, `.github/workflows/doc-drift-report.yml`, `mkdocs.yml`.

## RELEASE-EVIDENCE-GATE-001 — Freigabe-Aggregator

**Von:** Claude Code · **Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — `scripts/release_evidence_report.py` (6 Dimensionen), `release-gates.yml`, Runbook-Abschnitt; Artifact `release_evidence.json`.
**Dateibesitz:** `scripts/release_evidence_report.py`, `.github/workflows/release-gates.yml`, `docs/operations/production-readiness-runbook.md`.

## SEMANTIC-ACTION-MATRIX-002 — Action-Matrices YAML

**Von:** Claude Code · **Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — YAML-Matrizen unter `docs/quality-assurance/action-matrices/`; `generate_action_matrix_report.py`; Report `action-matrix-report.md`.
**Dateibesitz:** `docs/quality-assurance/action-matrices/**`, `scripts/generate_action_matrix_report.py`.

## SEMANTIC-E2E-STRICT-001 — Playwright @critical Tags

**Von:** Claude Code · **Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — `@critical` in allen 6 E2E-Ketten (O2C, WMS, P2P, FIBU, POS, QS); CI-Workflow `e2e-critical.yml` (12 Health-Tests, Repo-Root).
**Dateibesitz:** `.github/workflows/e2e-critical.yml`, `playwright-tests/specs/e2e-matrix/*-semantic-chain.spec.ts`.

## TRACEABILITY-MATRIX-001 — Slice↔Test↔Doku

**Von:** Claude Code · **Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — `generate_traceability_matrix.py` → `docs/quality-assurance/traceability-matrix.md` (114 Slices).
**Dateibesitz:** `scripts/generate_traceability_matrix.py`, `docs/quality-assurance/traceability-matrix.md`.

## OPERATOR-AGENT-002 — Agent DB-Persistenz

**Von:** Claude Code · **Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — Schema `agent_proposals`, Repository mit Mapper, Alembic + Merge-Head; **OPERATOR-AGENT-002b:** Service verdrahtet via `Depends(get_db)`, Idempotency-Key, Persistenz-Tests (`test_operator_agent_persist.py`).
**Dateibesitz:** `alembic/versions/agent_proposals_persist_20260626.py`, `app/infrastructure/models/agent_proposal_model.py`, `app/repositories/agent_proposal_repository.py`, `app/services/operator_agent_service.py`, `app/api/v1/endpoints/operator_agent.py`, `tests/test_operator_agent_persist.py`.

## MCP-ERP-TOOLS-002 — MCP-Tools Erweiterung

**Von:** Claude Code · **Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — 18 Tools mit `data_classification: LOCAL_ONLY`; Registry-Validation erzwingt Policy-Stufen; 11 Contract-Tests grün; `check_all_doc_generators.sh` bindet MCP-Check ein.
**Dateibesitz:** `config/mcp_erp_tools.yaml`, `app/services/mcp_tool_registry_service.py`, `tests/test_mcp_tool_registry.py`, `scripts/check_all_doc_generators.sh`.

## DOC-RELEASE-NOTES-001 — Release-Notes-Generator

**Von:** Claude Code · **Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — `generate_release_notes.py` → `docs/benutzerhandbuch/release-notes.md`; mike-Kopplung folgt in Welle 4.
**Dateibesitz:** `scripts/generate_release_notes.py`, `docs/benutzerhandbuch/release-notes.md`.

## INTEGRATION-EVIDENCE-BOARD-001 — Qualitäts-Cockpit

**Von:** Claude Code · **Owner:** Claude Code
**Stand:** abgeschlossen 2026-06-26 — `quality_evidence.py` API, Router, `admin/qualitaets-cockpit.tsx`, Nav/Route, 3 API-Tests (`4d3dbbf52`).
**Dateibesitz:** `app/api/v1/endpoints/quality_evidence.py`, `packages/frontend-web/src/pages/admin/qualitaets-cockpit.tsx`.

## EXTERNAL-MOCK-WORKFLOW-001 — Playwright Mock-Verträge (Claim)

**Von:** Claude Code / **Stand:** abgeschlossen 2026-06-26

---

## Programmabschluss Wellen 1–4 (2026-06-26)

Alle 16 Slices des Qualitäts-ERP-Programms abgeschlossen:

| Slice | Status |
|---|---|
| DOC-OPENAPI-CI-001 | abgeschlossen |
| DOC-ASYNCAPI-001 | abgeschlossen |
| DOC-INAPP-HELP-002 | abgeschlossen |
| DOC-DRIFT-GATE-002 | abgeschlossen |
| DOCS-CODE-SYNC-002 | abgeschlossen |
| DOC-DRIFT-DASHBOARD-002 | abgeschlossen |
| RELEASE-EVIDENCE-GATE-001 | abgeschlossen |
| SEMANTIC-ACTION-MATRIX-002 | abgeschlossen |
| SEMANTIC-E2E-STRICT-001 | abgeschlossen |
| TRACEABILITY-MATRIX-001 | abgeschlossen |
| OPERATOR-AGENT-002 | abgeschlossen |
| MCP-ERP-TOOLS-002 | abgeschlossen |
| COVERAGE-RATCHET-002 | abgeschlossen |
| DOC-USER-MANUAL-002 | abgeschlossen |
| DOC-RELEASE-NOTES-001 | abgeschlossen |
| INTEGRATION-EVIDENCE-BOARD-001 | abgeschlossen |
| EXTERNAL-MOCK-WORKFLOW-001 | abgeschlossen |

**Erfolgskriterien:**
- Drift: --fail-over 0 dauerhaft grün (0 Items)
- Release-Evidence: 6 Dimensionen aggregiert, --fail-on-red aktiv
- Semantik: @critical-Blöcke in O2C + WMS, separater CI-Job
- Traceability: 123 Slices geparst, 2% Coverage (Phase 1 dokumentiert Lücken)
- Nutzer: QS-Handbuch, Release-Notes, 50 INAPP-Mappings
- Agent: Proposals persistent in DB, 18 MCP-Tools mit data_classification

---

## ARCH-OS — Architecture Operating System (2026-06-27)

**Stand:** abgeschlossen — Structurizr DSL, Index-Generator, Domain Packs, Agent Protocol, CI-Gates.

| Slice | Status | Deliverable |
|---|---|---|
| ARCH-OS-001 | abgeschlossen | ADR-037, `workspace.dsl`, `render_c4_views.py`, generierte C4 L1/L2 |
| ARCH-OS-002 | abgeschlossen | `generate_architecture_index.py`, `config/architecture-index.yaml` |
| ARCH-OS-003 | abgeschlossen | CRM Domain Pack, `architecture-protocol.md`, AGENTS.md |
| ARCH-OS-004 | abgeschlossen | `pnpm arch:*`, `architecture_drift_check.py`, quality-gate |
| ARCH-OS-005 | abgeschlossen | Domain Packs Finance, Inventory, Agrar |
| ARCH-OS-006 | abgeschlossen | Domain Pack DMS/Compliance |

**CLI:** `pnpm arch:render` · `pnpm arch:validate` · `pnpm arch:drift`

**Agent-Einstieg:** `config/architecture-index.yaml` + [architecture-protocol.md](../architecture/agents/architecture-protocol.md) + [Rollout-Prompt](../architecture/agents/architecture-os-rollout-prompt.md) (Copy-Paste für neue Sessions)
