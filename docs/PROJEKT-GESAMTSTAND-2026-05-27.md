# VALEO NeuroERP 3.0 — Projekt-Gesamtstand 2026-05-27

> Aggregierte Lieferstands-Sicht über alle Slices, Waves und Compliance-Bereiche.
> Source of Truth bleiben die referenzierten Detaildokumente.

**Branch:** `perf/crm-kim-dashboard` | **HEAD:** `eb8e62237` | **Stand:** 2026-06-18

---

## 1. Executive Summary

VALEO NeuroERP 3.0 ist ein mandantenfähiges, agrarhandels-spezifisches ERP mit KI-First-Architektur. Der Liefer- und Reifegrad ist Mitte 2026:

- **Process Kernel** Waves 1–104 abgeschlossen (Service-Layer, Gap-Closure, Test-Fixes).
- **Fachliche Vertiefung** Waves 1–22 mit Frontend-Masken für 17+ Stammdatenbereiche.
- **Backend-Security** Wave 22 (globale Auth, RFC-7807, nosec SQL) und Wave-A3 (Tenant-Isolation-CI-Gate).
- **OpenAPI-Coverage** 100% (2663 Routen mit `summary=`, Wave-D2).
- **Compliance** GoBD, DSGVO Art. 15/17/20/30/33, E-Rechnung Import **und Export** vollständig implementiert.
- **DOM-*-004-Tiefenwelle** abgeschlossen (2026-06-12): CON/SALES/FIN/DOC/PROC/SUPPLY auf voller operativer Tiefe.
- **Logistik-Kette** (2026-06-12/13): Tourenplanung, Fracht/Tarif/Storno, Read-Spine LS↔Tour, Ketten-Lifecycle-Test.
- **Wave-3 Produktions-Readiness** (2026-06-18): WF-Trigger-Log, Stammdaten-Duplikat-Erkennung, XRechnung-Export/Batch, Bank-Import MT940/CAMT053, Waage Mobile Sync, Mahnwesen-Scheduler.
- **HRM-PAYROLL-DEEP-001** (2026-06-18): Payroll-Closeout-Preview, AN-/AG-Anteile, DATEV-/kanzleisoftware-neutrale Exportprofile.

---

## 2. Quantitative Übersicht

| Kennzahl | Wert | Quelle |
|---|---|---|
| Backend-API-Endpoints | 316+ Endpoint-Module | `app/api/v1/endpoints/*.py` (+5 Wave-3) |
| OpenAPI-Routen mit `summary=` | 2663 (100%) | Commit `554625ae7` |
| Backend-Tests (pytest) | 9527+ gesammelt (2026-06-11); letzter Voll-Lauf 9228 passed | Commit `271bc5e12` (2026-05-26) |
| Backend-Testabdeckung | 64,85%+ | Ratchet ≥60% grün, 33 kritische Pfade (COV-RATCHET-005) |
| Frontend-TypeCheck | 0 Fehler | Wave-22-Gate (2026-05-27) |
| Frontend-Pages (Fachliche Vertiefung) | 17+ neue Masken | Waves 10–22 |
| E2E-Tests (Playwright Wave 11/20–22) | 23/23 grün | Integrations-Gate `97c41d479` |
| Alembic-Heads | 1 | `wave3_wf_trigger_log_20260618` (aktueller Head) |

---

## 3. Wave-Lieferstand

### 3.1 Process-Kernel (1–104) — abgeschlossen
Siehe [docs/architecture/process-kernel/STATUS.md](architecture/process-kernel/STATUS.md).

### 3.2 Fachliche Vertiefung — Backend (Wave 1–13) — abgeschlossen
Migrations `fachliche_vertiefung_wave1..13_20260521`. Siehe [FACHLICHE-VERTIEFUNG-ABNAHME.md](FACHLICHE-VERTIEFUNG-ABNAHME.md).

### 3.3 Fachliche Vertiefung — UX (Wave 10–22) — abgeschlossen

| Wave | UX-Lieferung | Slice | Status |
|---|---|---|---|
| W10 | Warengruppen, Erlöskennziffern, Zahlungsbedingungen, EKZZ | FACHLICHE-VERTIEFUNG-UX-W10-001/EKZZ | ✅ |
| W11 | Partiestamm, Forderungsgruppen, Periodische Buchungen | FACHLICHE-VERTIEFUNG-UX-W11-001 | ✅ |
| W14 | Rabattgruppen, Betriebsstätten | FACHLICHE-VERTIEFUNG-UX-W14-001 | ✅ |
| W15 | Vertreterstamm, Hausbankenstamm | FACHLICHE-VERTIEFUNG-UX-W15-001 | ✅ |
| W16 | Vertreterstamm × Vertreterprovisionsgruppen | FACHLICHE-VERTIEFUNG-UX-W16-001 | ✅ |
| W17 | Zu-/Abschlaggruppen (ZAGR/ZAKL/ZAK) | FACHLICHE-VERTIEFUNG-UX-W17-001 | ✅ |
| W20 | Rohwarengruppen | FACHLICHE-VERTIEFUNG-UX-W20-001 | ✅ |
| W21 | Daueraufträge, Massebilanz, Vermehrungsverträge, Zinsabrechnung, Artikel-Bestandteile, Artikelverpackung | FACHLICHE-VERTIEFUNG-UX-W21-001 | ✅ |
| W22 | Frachttabellen, Versandprofile, Rezepturgruppen, Geschäftsjahre, Zahlungsmeldungen, Individualpreise, Mengeneinheiten | (Wave 22 Frontend-Block) | ✅ |

Waves 18/19 waren bereits vorbefüllt und wurden im Sweep gestoppt.

### 3.4 DOM-*-004 Tiefenwelle — abgeschlossen (2026-06-12)

| Domain | Lieferung | Services |
|---|---|---|
| CON-004 | Fixierung/MATIF-Marktwert, Engagement-Sicht, Kontraktmahnung, Settlement-Übergabe/Storno | `contract_{fixing,engagement,settlement}_service.py` |
| SALES-004 | Positions-Match O2C, Kreditlimit-Prüfung, Storno/Gutschrift | `sales_{match,credit,storno}_service.py` |
| FIN-004 | Mahnlauf/Eskalation, OP-Auszifferung, Periodenabschluss/Storno, DATEV-Export | `finance_{dunning,clearing,period,datev}_service.py` |
| DOC-004 | Artefakt-Upload/Versionierung/Freigabe, Bescheid/Wiedervorlage, GoBD-Exportpaket | `docflow_{artifact,followup,gobd}_service.py` |
| PROC-004 | 3-Wege-Match, Folgeaktionen/Reklamation, ERS, RFQ→PO | `procurement_match_service.py`, `rfq_service.py` |
| SUPPLY-004 | Rückverfolgbarkeit, Ketten-Event-Log, Lot-Folgeaktionen, Ketten-Storno | `supply_chain_traceability_service.py` |

### 3.5 Logistik-Kette — abgeschlossen (2026-06-12/13)

| Slice | Lieferung |
|---|---|
| LOG-PROD-001 | Alembic `log_logistics_core_20260612`, Lazy-DDL entfernt |
| LOG-SPINE-RAND-001 | Read-API `GET /logistik/sales-delivery-note-by-ref`, `delivery_note_ref`-Auflösung |
| LOG-SPINE-001 | Frontend Tourenplanung + Tour-Hints + PATCH `delivery_note_ref`, Seed |
| LOG-CHAIN-001 | Ketten-Lifecycle-Test LS→Tour→Fracht→Traceability |
| LOG-LIFE-001 | Storno-Endpunkte fail-closed + Frontend Status STORNIERT |
| LOG-FREIGHT-STORNO-001 | Fracht-Tarif Soft-Storno + Alembic `log_freight_tariff_storno_20260613` |

### 3.6 Wave-3 Produktions-Readiness — abgeschlossen (2026-06-18)

| Slice | Lieferung | Endpoint / Modul |
|---|---|---|
| WF-TRIGGER-001 | WF-Trigger-Map + Log | `wf_trigger.py`, `wf_trigger_service.py`, `domain_ops.wf_trigger_log` |
| STMD-DUP-001 | Stammdaten Duplikat-Erkennung (UST-ID, IBAN, PLZ+Name, EAN) | `stmd_duplikat.py` |
| INT-XRECHNUNG-001 | XRechnung 3.0 UBL-Export + Batch-ZIP | `xrechnung.py` |
| INT-BANK-001 | Bank-Import MT940 + CAMT.053 + OP-Matching | `bank_import.py` |
| WGE-MOB-001 | Waage Mobile Sync (Idempotenz-Key, Batch-Sync, Offline-Queue) | `waage_mobile.py` |
| MAHNWESEN-AUTO | Scheduler: Dunning-Auto tägl. 07:00, WF-Trigger-Pending 15min | `scheduler_service.py` |

### 3.7 Wave-2 Integration Slices — abgeschlossen (2026-06-18)

| Slice | Lieferung |
|---|---|
| PROD-FIBU-001 | Produktions-FIBU-Journal-Referenz |
| LOG-FRACHT-001 | Frachtbriefe/Carrier Invoices |
| BI-DRILL-001 | BI-Drill-Down Reporting |
| COMP-SPERR-001 | Artikel-Sperren Cross-Domain |

### 3.8 Backend-Hardening — abgeschlossen

| Wave | Lieferung | Commit |
|---|---|---|
| Wave-A3 | Tenant-Isolation-Audit + CI-Gate | `c106f74e8` |
| Wave-D2 | OpenAPI `summary=` für alle 2663 Routen | `554625ae7` |
| Wave-D3 | RFC-7807 Error-Format + Cache | `389a411a1` |
| Wave 22 Backend-Security | Global Auth, nosec SQL, WhatsApp-Config | `4ab228f92` + `732d84376` |
| CI-Gate SQL-f-String-Check | `scripts/check_sql_fstrings.py` | `b613366a1` |

---

## 4. Compliance — Norm-Mapping

### 4.1 GoBD (BMF 28.11.2019)

| Anforderung | Status | Implementiert in |
|---|---|---|
| Unveränderbarkeit (§146 AO) | ✅ vollständig | `gobd_archiv.py`, `audit_hardening.py`, Hash-Chain via DB-Trigger |
| Nachvollziehbarkeit (§146 AO) | ✅ vollständig | `audit.py`, `audit_evidence.py`, `neuro_audit.py` |
| Vollständigkeit (§146 AO) | ✅ vollständig | Belegnummern-Lücken-Check `/gobd/belegnummern` |
| Aufbewahrung (§147 AO) | ✅ vollständig | `gobd_archiv.py` Artifact-Registry, WORM-fähig |
| Storno-Zwang | ✅ vollständig | Journal-Endpoints; kein DELETE für verbuchte Belege |
| Audit-Pfad zentral | ✅ vollständig | siehe [compliance/BUCHUNGEN-AUDIT-PFAD.md](compliance/BUCHUNGEN-AUDIT-PFAD.md) |

### 4.2 DSGVO

| Artikel | Anforderung | Status | Endpoint/Modul |
|---|---|---|---|
| Art. 15 | Auskunftsrecht | ✅ | `/api/v1/gdpr/data-export` |
| Art. 17 | Löschung | ✅ | `/api/v1/gdpr/requests` Lifecycle PENDING→VERIFIED→COMPLETED |
| Art. 20 | Datenportabilität | ✅ | `/api/v1/gdpr/data-export` |
| Art. 30 | Verarbeitungsverzeichnis | ✅ | `gdpr_art30_ropa.py` (83% Coverage, Slice-008) |
| Art. 32 | Sicherheit der Verarbeitung | ✅ | OIDC, Tenant-Isolation, RFC-7807-Fehlermaskierung |
| Art. 33 | Meldepflicht bei Datenpanne | ✅ | `gdpr_art33_breach.py` (97% Coverage, Slice-009) |

### 4.3 E-Rechnung (Wachstumschancengesetz, B2B-Pflicht ab 2025/2027/2028)

| Funktion | Status | Modul |
|---|---|---|
| Import XRechnung 3.0 / ZUGFeRD 2.1 | ✅ | `erechnung_import.py` |
| Format-Erkennung | ✅ | `_detect_format()` |
| Felder-Extraktion (Betrag, Lieferant, Rechnungsnr.) | ✅ | `_parse_xrechnung()` / `_parse_zugferd()` |
| Persistente Import-Records | ✅ | `domain_finance.erechnung_imports` |
| Buchen aus Import | ✅ | `POST /erechnung/imports/{id}/buchen` |
| **Export Self-Billing-Gutschriften** | ✅ | `modules/agrar/services/self_billing_service.py` (XRechnung UBL 2.1, ZUGFeRD PDF/A-3 via `factur-x`) |
| **Export B2B-Verkaufsrechnungen XRechnung** | ✅ **Implementiert** | `app/services/einvoice_generator.py` + `sales_invoice_einvoice.py` (Slice-006, Commit `08d64eff4`) |
| **Export B2B-Verkaufsrechnungen ZUGFeRD** | ✅ **Implementiert** | `app/services/einvoice_generator.py::build_zugferd_pdf` via `factur-x` |
| EN-16931-Schematron-Validierung | ⚠️ optionaler Hook via `set_xrechnung_generator()` | — |

### 4.4 Weitere Normen

| Norm | Anforderung | Status |
|---|---|---|
| DIN EN ISO 9241 | 44px Touch-Targets | ✅ Meridian-System |
| DIN EN ISO 9241 | Ctrl+K Command Palette | ⚠️ Slice-007 (geplant) |
| WCAG 2.1 AA | Audit dokumentiert | ✅ [docs/design/WCAG-AUDIT-2026-05-23.md](design/WCAG-AUDIT-2026-05-23.md) |
| TSE / DSFinV-K | POS-Konformität | ✅ repo-seitig (Prüfwerkzeug-Abnahme extern) |
| § 17a UStDV | Gelangensbestätigung | ✅ implementiert (VALEO-FIBU-001) |
| Intrastat | EU-Handelsstatistik | ✅ implementiert (VALEO-FIBU-002) |
| ATLAS | Zollausfuhr | ✅ implementiert (extern Zertifikat) |
| eBilanz / ELSTER | XBRL-Übermittlung | ✅ repo-seitig (ERiC/Steuerberater extern) |

---

## 5. KI-First / Agent-Orchestration

| Capability | Modul |
|---|---|
| MCP Tool Contracts | `copilot_ws.py`, NeuroCore-Pipeline |
| Agent Pipeline + State Graph | `neuro_pipeline.py`, `neuro_state_graph_api.py` |
| Voice-to-Intent | `ki_usability.py` (`voice_router`) |
| Voice REST Adapter | `neuro_voice.py` (Session/Transcribe/Synthesize) |
| Approval Decision Support | `neuro_fast_track.py` |
| Guardrails / Compliance | `neuro_guardrails.py`, `neuro_consent.py` |
| Knowledge / RAG | `neuro_knowledge.py` (Chroma + Obsidian-Sync) |
| Compensation / Rollback | `neuro_compensation.py` |
| Audit für Agent-Actions | `neuro_audit.py` |
| Prompt Packs | `neuro_prompt_packs.py` |
| Event Monitoring | `neuro_event_monitoring.py` + Grafana Dashboards |

Voice-Provider: Whisper / Azure / OpenAI TTS konfigurierbar, Browser-Fallback.

---

## 6. Infrastruktur-Stand (Kurzreferenz)

| Komponente | Status | Bemerkung |
|---|---|---|
| PostgreSQL 15 | produktiv | Multi-Schema, 1 Alembic-Head |
| Redis 7 | produktiv | Session/Cache |
| NATS JetStream | dev-auto + ops-konfigurierbar | Event-Bus, Monitoring komplett |
| Keycloak/OIDC | produktiv | RS256/JWKS, Dev-Bypass via `API_DEV_TOKEN` |
| Paperless-ngx DMS | produktiv | HTTP-Client mit Retry |
| ChromaDB (RAG) | produktiv | Artikel + Kunden + Kontrakte + Futtermittel + Knowledge |
| Superglue Self-Host | verdrahtet | Upstream-Contract aktuell, 3 Pilot-Tools |
| Voice-Provider | provider-ready | Whisper / Azure / OpenAI / Browser-Fallback |
| Tenant-Enforcement | Middleware | `TenantEnforcementMiddleware` validiert `X-Tenant-ID` zentral |
| Event-Bus-Monitoring | komplett | Grafana-Dashboards + Prometheus-Alerts in `monitoring/` |

---

## 7. Offene Punkte (Stand 2026-06-18)

| Slice | Beschreibung | Priorität | Status |
|---|---|---|---|
| **Slice-006** | XRechnung/ZUGFeRD-Generierung für B2B-Verkaufsrechnungen (E-Rechnung 2025 B2B-Pflicht) | **P1** | ✅ abgeschlossen (Commit `08d64eff4`, 2026-05-27) |
| Slice-007 | Ctrl+K Universal Command Palette | P2 | ✅ abgeschlossen — `components/navigation/CommandPalette.tsx` + AppShell, Ctrl+K via `useFeature('commandPalette')` |
| Slice-008 | DSGVO Art. 30 Verarbeitungsverzeichnis automatisiert | P2 | ✅ abgeschlossen — `gdpr_art30_ropa.py` + `test_gdpr_art30_ropa.py` (83% Coverage) |
| Slice-009 | DSGVO Art. 33 Datenpannen-Meldeprozess (workflow) | P2 | ✅ abgeschlossen — `gdpr_art33_breach.py` + `test_gdpr_art33_breach.py` (97% Coverage) |
| Slice-010 | Voice-Intent für Lager/Einkauf/HR ausbauen | P3 | ✅ abgeschlossen — `ActionDispatchContext.tsx` Lager/Einkauf/HR-Intents, `test_voice_intent_lager_einkauf_hr.py` |
| Slice-011 | Meridian-Fachseiten-Hardcolors (Folgeslices) | P3 | ✅ abgeschlossen — DESIGN-MERIDIAN-HARDCOLORS-011 bis 014 (alle 2026-05-27) |

### Externe / nicht repo-seitig lösbar

| Gate | Owner |
|---|---|
| UAT-Unterschrift (VALEO-PARITY-001, CTS-H2S-UAT-001) | Business |
| ATLAS-Zertifikat | Zollbehörde |
| ERiC/Steuerberater-Freigabe (eBilanz) | Steuerberater |
| DMS-Live-Probe Mandant | Ops |
| Live-Credentials (Superglue, L3, Finance-Export) | Ops |
| FIBU-Cutover-Mapping SKR03/SKR04 | Steuerberater |

---

## 8. Quellen für tiefergehende Detailnachweise

- **Operative Liefer- und Workboard-Sicht:** [docs/agent-ops/active-workboard.md](agent-ops/active-workboard.md)
- **Fachliche Abnahme:** [docs/FACHLICHE-VERTIEFUNG-ABNAHME.md](FACHLICHE-VERTIEFUNG-ABNAHME.md)
- **Process Kernel Detail-Waves:** [docs/architecture/process-kernel/STATUS.md](architecture/process-kernel/STATUS.md)
- **Bekannte Lücken & Risiken:** [docs/project-context/open-gaps-and-known-issues.md](project-context/open-gaps-and-known-issues.md)
- **GAP-Index:** [docs/GAP-UND-TODO-INDEX.md](GAP-UND-TODO-INDEX.md)
- **GoBD-Mapping:** [docs/GOBD-COMPLIANCE.md](GOBD-COMPLIANCE.md)
- **Design-System:** [docs/DESIGNSYSTEM.md](DESIGNSYSTEM.md), [docs/design/EMPFEHLUNG.md](design/EMPFEHLUNG.md)
- **Agrar-ERP-Parität:** [docs/project-context/agrar-erp-gap-matrix-2026-05-17.md](project-context/agrar-erp-gap-matrix-2026-05-17.md)
- **AI-First Roadmap (Cursor-intern, nicht versioniert):** `.cursor/plans/ai_first_transformation.md`

---

## 9. Sicherheitszertifikate dieses Status-Stands

- ✅ Letzte 5 Commits auf `develop` enthalten keine ungestagten Backend-Endpoint-Modifikationen.
- ✅ Working Tree sauber zum Stichtag.
- ✅ Integrations-Gate Wave 18–22: 23/23 E2E grün, TypeCheck 0 Fehler, Workboard-Validierung grün (Commit `97c41d479`).
- ✅ Kein Force-Push in der Wave-22-Lieferung.
- ✅ Backend `py_compile` + Import-Test grün für alle Wave-22-Module.
