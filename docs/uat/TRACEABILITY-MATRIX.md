# Traceability-Matrix — VALEO NeuroERP 3.0
**Version:** 1.0  
**Stand:** 2026-05-18  
**Standard:** IEEE 829-2008 (Requirements Traceability)  
**Klassifizierung:** Intern — Qualitätssicherung  

---

## Leseanleitung

Die Matrix verknüpft:
- **Business Requirements** (fachliche Anforderungen aus Epic/User Story)
- **Test Case IDs** (UAT-Testfall-Referenz)
- **Gherkin-Szenarien** (Szenario-Name in `.feature`-Datei)
- **Playwright-Test** (E2E-Testdatei und describe-Block)
- **pytest-Test** (Python-Testdatei und Testfunktion)
- **Automationsstatus**: ✅ Automatisiert | 🔄 In Entwicklung | ✏️ Manuell | ⏳ Geplant
- **Risk Level**: P0 Kritisch | P1 Hoch | P2 Mittel

---

## F01 — Ernte-Annahme (Harvest Acceptance)

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| Ernte-Annahme | BR-AGRAR-001: Lieferung anlegen | TC-F01-001 | Neue Ernteanlieferung anlegen | `agrar/ernte-annahme.spec.ts` → "Neue Anlieferung anlegen" | `tests/uat/step_defs/agrar_steps.py::test_create_harvest` | 🔄 | P0 |
| Ernte-Annahme | BR-AGRAR-002: Bruttogewicht erfassen | TC-F01-002 | Bruttogewicht von Wiegebrücke übernehmen | `agrar/ernte-annahme.spec.ts` → "Bruttogewicht" | `tests/test_harvest_acceptance.py::test_gross_weight` | ✅ | P0 |
| Ernte-Annahme | BR-AGRAR-003: Qualitätsprüfung | TC-F01-003 | Qualitätsparameter für Weizen erfassen | `agrar/ernte-annahme.spec.ts` → "Qualitätsprüfung" | `tests/test_harvest_acceptance.py::test_quality_check` | ✅ | P0 |
| Ernte-Annahme | BR-AGRAR-003: Qualitätsablehnung | TC-F01-004 | Qualitätsparameter außerhalb Toleranz — Ablehnung | `agrar/ernte-annahme.spec.ts` → "Ablehnung" | `tests/test_harvest_acceptance.py::test_quality_rejection` | ✅ | P0 |
| Ernte-Annahme | BR-AGRAR-004: Trocknungsregel | TC-F01-005 | Automatische Trocknungsregel bei erhöhter Feuchte | — | `tests/test_drying_rule_engine.py::test_drying_calc_standard` | ✅ | P0 |
| Ernte-Annahme | BR-AGRAR-004: Keine Trocknung | TC-F01-006 | Keine Trocknungsregel notwendig bei Normalfeuchte | — | `tests/test_drying_rule_engine.py::test_no_drying_required` | ✅ | P0 |
| Ernte-Annahme | BR-AGRAR-005: Tarierung | TC-F01-007 | Nettogewicht durch Tarierung ermitteln | `agrar/ernte-annahme.spec.ts` → "Tarierung" | `tests/test_harvest_acceptance.py::test_tara_calculation` | ✅ | P0 |
| Ernte-Annahme | BR-AGRAR-006: Lagerplatzzuweisung | TC-F01-008 | Automatische Lagerplatzzuweisung nach Qualität | — | `tests/test_harvest_acceptance.py::test_storage_assignment` | ✅ | P0 |
| Ernte-Annahme | BR-AGRAR-006: Kapazitätswarnung | TC-F01-009 | Kapazitätswarnung bei vollem Silo | — | `tests/test_harvest_acceptance.py::test_capacity_warning` | ✅ | P0 |
| Ernte-Annahme | BR-AGRAR-007: Abrechnung | TC-F01-010 | Abrechnungsauslösung nach vollständiger Einlagerung | `agrar/ernte-annahme.spec.ts` → "Abrechnung" | `tests/test_harvest_acceptance.py::test_settlement_trigger` | 🔄 | P0 |

**F01 Coverage:** 10/10 Test Cases definiert | Automation: 8 automatisiert, 2 in Entwicklung

---

## F02 — Agrar-Kontrakte

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| Kontrakte | BR-KONTR-001: Fixpreis anlegen | TC-F02-001 | Fixpreis-Kontrakt anlegen | `agrar/kontrakte.spec.ts` → "Fixpreis anlegen" | `tests/test_agrar_contracts.py::test_create_fixed_price` | ✅ | P0 |
| Kontrakte | BR-KONTR-001: Mengenlimit | TC-F02-002 | Fixpreis-Kontrakt — Mengenlimit überschreiten | — | `tests/test_agrar_contracts.py::test_quantity_exceeded` | ✅ | P0 |
| Kontrakte | BR-KONTR-002: Basis-Kontrakt | TC-F02-003 | Basis-Kontrakt anlegen (Preisfixierung offen) | `agrar/kontrakte.spec.ts` → "Basis-Kontrakt" | `tests/test_agrar_contracts.py::test_create_basis_contract` | ✅ | P0 |
| Kontrakte | BR-KONTR-002: Preisfixierung | TC-F02-004 | Preisfixierung für Basis-Kontrakt durchführen | `agrar/kontrakte.spec.ts` → "Preisfixierung" | `tests/test_agrar_contracts.py::test_price_fixation` | ✅ | P0 |
| Kontrakte | BR-KONTR-002: Fristüberschreitung | TC-F02-005 | Basis-Kontrakt — Fixierungsfrist überschritten | — | `tests/test_agrar_contracts.py::test_fixation_deadline_exceeded` | ✅ | P0 |
| Kontrakte | BR-KONTR-003: Prämien anlegen | TC-F02-006 | Prämien-Kontrakt anlegen mit Qualitätsprämien | `agrar/kontrakte.spec.ts` → "Prämien-Kontrakt" | `tests/test_agrar_contracts.py::test_create_premium_contract` | ✅ | P0 |
| Kontrakte | BR-KONTR-003: Prämienberechnung | TC-F02-007 | Prämienberechnung bei Anlieferung auslösen | — | `tests/test_agrar_contracts.py::test_premium_calculation` | ✅ | P0 |
| Kontrakte | BR-KONTR-004: Kontraktklasse | TC-F02-008 | Kontraktklasse für Pool-Abrechnung zuweisen | — | `tests/test_agrar_contracts.py::test_contract_class` | 🔄 | P1 |
| Kontrakte | BR-KONTR-005: Änderungshistorie | TC-F02-009 | Kontrakt-Änderungshistorie nachvollziehen | `agrar/kontrakte.spec.ts` → "Historie" | `tests/test_agrar_contracts.py::test_change_history` | 🔄 | P1 |

**F02 Coverage:** 9/9 Test Cases definiert | Automation: 7 automatisiert, 2 in Entwicklung

---

## F03 — Agrar-Abrechnung (Settlement)

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| Settlement | BR-SETTL-001: Sammelabrechnung | TC-F03-001 | Sammelabrechnung für einen Lieferanten erstellen | `agrar/abrechnung.spec.ts` → "Sammelabrechnung" | `tests/test_agrar_settlements.py::test_create_settlement` | 🔄 | P1 |
| Settlement | BR-SETTL-001: Positionsdetails | TC-F03-002 | Sammelabrechnung — Positionsdetails prüfen | — | `tests/test_agrar_settlements.py::test_settlement_positions` | 🔄 | P1 |
| Settlement | BR-SETTL-002: Trocknung | TC-F03-003 | Trocknungskosten korrekt ausweisen | — | `tests/test_agrar_settlements.py::test_drying_costs_display` | ✅ | P1 |
| Settlement | BR-SETTL-003: PDF | TC-F03-004 | Abrechnungs-PDF generieren | `agrar/abrechnung.spec.ts` → "PDF-Export" | `tests/test_agrar_settlements.py::test_pdf_generation` | ✏️ | P1 |
| Settlement | BR-SETTL-003: PDF-Fehler | TC-F03-005 | PDF-Generation bei fehlendem Bankdaten | — | `tests/test_agrar_settlements.py::test_pdf_missing_bank` | ✅ | P1 |
| Settlement | BR-SETTL-004: Genehmigung einreichen | TC-F03-006 | Sammelabrechnung zur Genehmigung einreichen | `agrar/abrechnung.spec.ts` → "Genehmigung" | `tests/test_agrar_settlements.py::test_submit_approval` | 🔄 | P1 |
| Settlement | BR-SETTL-004: Genehmigen | TC-F03-007 | Sammelabrechnung genehmigen | — | `tests/test_agrar_settlements.py::test_approve_settlement` | 🔄 | P1 |
| Settlement | BR-SETTL-004: Ablehnen | TC-F03-008 | Sammelabrechnung ablehnen mit Begründung | — | `tests/test_agrar_settlements.py::test_reject_settlement` | 🔄 | P1 |
| Settlement | BR-SETTL-005: Zahlungsanweisung | TC-F03-009 | Zahlungsanweisung aus freigegebener Abrechnung | — | `tests/test_agrar_settlements.py::test_payment_instruction` | ⏳ | P1 |

**F03 Coverage:** 9/9 Test Cases definiert | Automation: 2 automatisiert, 5 in Entwicklung, 1 manuell, 1 geplant

---

## F04 — POS Tagesabschluss / DSFinV-K

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| POS DSFinV-K | BR-POS-001: Z-Abschluss | TC-F04-001 | Z-Abschluss für Tages-Kassenbericht | `pos/tagesabschluss.spec.ts` → "Z-Abschluss" | `tests/test_pos_tagesabschluss.py::test_z_closing` | 🔄 | P0 |
| POS DSFinV-K | BR-POS-001: Z-Nummer lückenlos | TC-F04-002 | Z-Nummer lückenlose Fortschreibung | — | `tests/test_pos_tagesabschluss.py::test_z_number_sequential` | ✅ | P0 |
| POS DSFinV-K | BR-POS-002: DSFinV-K-Export | TC-F04-003 | DSFinV-K-Export für Betriebsprüfung | `pos/tagesabschluss.spec.ts` → "DSFinV-K" | `tests/test_pos_dsfinvk.py::test_dsfinvk_export` | ✅ | P0 |
| POS DSFinV-K | BR-POS-002: TSE-Validierung | TC-F04-004 | DSFinV-K-Export — TSE-Signatur-Validierung | — | `tests/test_pos_dsfinvk.py::test_tse_signature_validation` | ✅ | P0 |
| POS DSFinV-K | BR-POS-003: Kassensturz | TC-F04-005 | Kassensturz vor Z-Abschluss | `pos/tagesabschluss.spec.ts` → "Kassensturz" | `tests/test_pos_tagesabschluss.py::test_cash_count` | 🔄 | P0 |
| POS DSFinV-K | BR-POS-003: Differenz-Sperre | TC-F04-006 | Kassendifferenz über Toleranzgrenze — Sperre | — | `tests/test_pos_tagesabschluss.py::test_cash_diff_block` | ✅ | P0 |
| POS DSFinV-K | BR-POS-004: USt-Berechnung | TC-F04-007 | USt-Berechnung im Z-Bon korrekt | — | `tests/test_pos_tagesabschluss.py::test_vat_calculation` | ✅ | P0 |

**F04 Coverage:** 7/7 Test Cases definiert | Automation: 5 automatisiert, 2 in Entwicklung

---

## F05 — POS Retoure

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| POS Retoure | BR-RET-001: Retoure mit Bon | TC-F05-001 | Warenrückgabe mit Originalbon buchen | `pos/retoure.spec.ts` → "Retoure mit Bon" | `tests/test_pos_retoure.py::test_return_with_receipt` | 🔄 | P1 |
| POS Retoure | BR-RET-002: Retoure ohne Bon | TC-F05-002 | Warenrückgabe ohne Originalbon (mit Genehmigung) | `pos/retoure.spec.ts` → "Retoure ohne Bon" | `tests/test_pos_retoure.py::test_return_without_receipt` | 🔄 | P1 |
| POS Retoure | BR-RET-002: Ablehnung | TC-F05-003 | Retoure ohne Bon — Ablehnung durch Filialleiter | — | `tests/test_pos_retoure.py::test_return_rejected` | 🔄 | P1 |
| POS Retoure | BR-RET-003: Teilretoure | TC-F05-004 | Teilweise Warenrückgabe aus Originalbon | `pos/retoure.spec.ts` → "Teilretoure" | `tests/test_pos_retoure.py::test_partial_return` | 🔄 | P1 |
| POS Retoure | BR-RET-004: Retouren-Limit | TC-F05-005 | Retoure über Retourengrenze — Sicherheitsprüfung | — | `tests/test_pos_retoure.py::test_return_limit` | ✅ | P1 |
| POS Retoure | BR-RET-005: Erstattungsweg EC | TC-F05-006 | Erstattung per ursprünglichem Zahlungsweg (EC) | `pos/retoure.spec.ts` → "EC-Erstattung" | `tests/test_pos_retoure.py::test_refund_ec_card` | ✏️ | P1 |
| POS Retoure | BR-RET-005: Erstattungsweg Bar | TC-F05-007 | Erstattung als Barauszahlung | — | `tests/test_pos_retoure.py::test_refund_cash` | ✏️ | P1 |

**F05 Coverage:** 7/7 Test Cases definiert | Automation: 1 automatisiert, 4 in Entwicklung, 2 manuell

---

## F06 — POS Offline-Queue

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| POS Offline | BR-OFF-001: Offline-Verkauf | TC-F06-001 | Verkauf im Offline-Modus buchen | `pos/offline-queue.spec.ts` → "Offline-Verkauf" | — | 🔄 | P1 |
| POS Offline | BR-OFF-001: Queue akkumulieren | TC-F06-002 | Mehrere Offline-Transaktionen in der Queue | `pos/offline-queue.spec.ts` → "Queue" | — | ✏️ | P1 |
| POS Offline | BR-OFF-002: Cache-Lookup | TC-F06-003 | Offline — Artikel-Stammdaten aus Cache | `pos/offline-queue.spec.ts` → "Cache-Lookup" | — | 🔄 | P1 |
| POS Offline | BR-OFF-002: Unbekannter Artikel | TC-F06-004 | Offline — unbekannter Artikel ohne Cache | `pos/offline-queue.spec.ts` → "Unbekannter Artikel" | — | 🔄 | P1 |
| POS Offline | BR-OFF-003: Synchronisation | TC-F06-005 | Automatische Synchronisation bei Reconnect | `pos/offline-queue.spec.ts` → "Sync" | `tests/test_pos_offline.py::test_sync_on_reconnect` | 🔄 | P1 |
| POS Offline | BR-OFF-003: Sync-Erfolg | TC-F06-006 | Synchronisation — alle Transaktionen erfolgreich | — | `tests/test_pos_offline.py::test_sync_all_success` | 🔄 | P1 |
| POS Offline | BR-OFF-004: Konflikt | TC-F06-007 | Konflikt — Artikel deaktiviert | `pos/offline-queue.spec.ts` → "Konflikt" | `tests/test_pos_offline.py::test_sync_conflict` | 🔄 | P1 |
| POS Offline | BR-OFF-004: Konfliktauflösung | TC-F06-008 | Manuelle Entscheidung durch Supervisor | `pos/offline-queue.spec.ts` → "Konfliktauflösung" | — | ✏️ | P1 |
| POS Offline | BR-OFF-005: Sync-Protokoll | TC-F06-009 | Synchronisations-Protokoll abrufen | — | `tests/test_pos_offline.py::test_sync_protocol` | ⏳ | P1 |
| POS Offline | BR-OFF-006: Verschlüsselung | TC-F06-010 | Offline-Queue verschlüsselt gespeichert | `pos/offline-queue.spec.ts` → "Verschlüsselung" | — | ⏳ | P1 |
| POS Offline | BR-OFF-007: Max-Offline-Dauer | TC-F06-011 | Maximale Offline-Dauer — Warnung | `pos/offline-queue.spec.ts` → "Offline-Dauer" | — | ⏳ | P1 |

**F06 Coverage:** 11/11 Test Cases definiert | Automation: 4 in Entwicklung, 3 manuell, 4 geplant

---

## F07 — Gelangensbetätigung (§17a UStDV)

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| Gelangensb. | BR-GB-001: Erstellen | TC-F07-001 | Gelangensbetätigung erstellen | `compliance/gelangensbetaetigung.spec.ts` → "Erstellen" | `tests/test_compliance.py::test_create_gelangensbestaetigung` | ✅ | P0 |
| Gelangensb. | BR-GB-002: Bestätigung | TC-F07-002 | Bestätigung vom Empfänger hinterlegen | `compliance/gelangensbetaetigung.spec.ts` → "Bestätigung" | `tests/test_compliance.py::test_confirm_gelangensbestaetigung` | ✅ | P0 |
| Gelangensb. | BR-GB-003: Frist läuft | TC-F07-003 | 90-Tage-Frist noch nicht überschritten | — | `tests/test_compliance.py::test_deadline_not_exceeded` | ✅ | P0 |
| Gelangensb. | BR-GB-003: Erinnerung | TC-F07-004 | 30-Tage-Vorab-Erinnerung | — | `tests/test_compliance.py::test_30day_reminder` | ✅ | P0 |
| Gelangensb. | BR-GB-003: Frist überschritten | TC-F07-005 | 90-Tage-Frist überschritten — Eskalation | — | `tests/test_compliance.py::test_deadline_exceeded_escalation` | ✅ | P0 |
| Gelangensb. | BR-GB-004: Massenliste | TC-F07-006 | Massenabruf aller ausstehenden Betätigungen | `compliance/gelangensbetaetigung.spec.ts` → "Liste" | `tests/test_compliance.py::test_list_pending_gb` | ✅ | P0 |

**F07 Coverage:** 6/6 Test Cases definiert | Automation: 6 automatisiert (100 %)

---

## F08 — Sanktionsprüfung

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| Sanktion | BR-SAN-001: Positiver Treffer | TC-F08-001 | Sanktionsprüfung ergibt positiven Treffer | — | `tests/test_compliance.py::test_sanctions_positive_hit` | ✅ | P0 |
| Sanktion | BR-SAN-002: Kein Treffer | TC-F08-002 | Sanktionsprüfung — kein Treffer | — | `tests/test_compliance.py::test_sanctions_no_hit` | ✅ | P0 |
| Sanktion | BR-SAN-003: Verdächtiger Treffer | TC-F08-003 | Sanktionsprüfung — verdächtiger Treffer | — | `tests/test_compliance.py::test_sanctions_suspicious_hit` | ✅ | P0 |
| Sanktion | BR-SAN-004: Falsch-positiv | TC-F08-004 | Manuelle Prüfung — falsch-positiv | — | `tests/test_compliance.py::test_sanctions_false_positive` | ✅ | P0 |
| Sanktion | BR-SAN-005: Listen-Update | TC-F08-005 | Sanktionslisten-Update auslösen | — | `tests/test_compliance.py::test_sanctions_list_update` | ✅ | P0 |

**F08 Coverage:** 5/5 Test Cases definiert | Automation: 5 automatisiert (100 %)

**PCN/UFI Nachtrag 2026-05-18:** `POST /api/v1/compliance/pcn-meldungen`
ist als UAT-API-Contract `tests/uat/test_uat_api_contracts.py::TestComplianceEndpoints::test_pcn_meldung_create_validates_ufi_and_returns_contract`
abgesichert. Ungueltige UFI werden mit HTTP 422 abgelehnt.

---

## F09 — LKSG Lieferanten-Risikobewertung

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| LKSG | BR-LKSG-001: Score berechnen | TC-F09-001 | LKSG-Risikoscore berechnen | — | `tests/test_compliance.py::test_lksg_score_calculation` | ✅ | P1 |
| LKSG | BR-LKSG-002: Kritisch-Sperre | TC-F09-002 | Kritische Risikoschwelle — Sperrung | — | `tests/test_compliance.py::test_lksg_critical_block` | ✅ | P1 |
| LKSG | BR-LKSG-002: Hoch-Maßnahmen | TC-F09-003 | LKSG-Score grenzwertig — Maßnahmenplan | — | `tests/test_compliance.py::test_lksg_high_action_plan` | 🔄 | P1 |
| LKSG | BR-LKSG-003: Maßnahmenplan | TC-F09-004 | Maßnahmenplan für kritischen Lieferanten | — | `tests/test_compliance.py::test_lksg_action_plan_create` | 🔄 | P1 |
| LKSG | BR-LKSG-004: Sperraufhebung | TC-F09-005 | Maßnahmenplan abgeschlossen — Sperrung aufheben | — | `tests/test_compliance.py::test_lksg_unblock` | 🔄 | P1 |
| LKSG | BR-LKSG-005: Jahresbericht | TC-F09-006 | Jährlicher LKSG-Bericht | — | `tests/test_compliance.py::test_lksg_annual_report` | ⏳ | P1 |

**F09 Coverage:** 6/6 Test Cases definiert | Automation: 2 automatisiert, 3 in Entwicklung, 1 geplant

---

## F10 — Intrastat-Meldung

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| Intrastat | BR-INTRA-001: Meldung erstellen | TC-F10-001 | Monatliche Intrastat-Meldung erstellen | — | `tests/test_compliance.py::test_intrastat_create` | ✅ | P1 |
| Intrastat | BR-INTRA-001: Fehlende CN8 | TC-F10-002 | Intrastat — fehlende CN8-Codes erkennen | — | `tests/test_compliance.py::test_intrastat_missing_cn8` | ✅ | P1 |
| Intrastat | BR-INTRA-002: XML-Export | TC-F10-003 | INSTAT/XML-Datei exportieren | — | `tests/test_compliance.py::test_intrastat_xml_export` | ✅ | P1 |
| Intrastat | BR-INTRA-003: CSV-Export | TC-F10-004 | Intrastat-CSV exportieren | — | `tests/test_compliance.py::test_intrastat_csv_export` | ✅ | P1 |
| Intrastat | BR-INTRA-004: Validierung | TC-F10-005 | Intrastat-Meldung validieren | — | `tests/test_compliance.py::test_intrastat_validation` | ✅ | P1 |
| Intrastat | BR-INTRA-005: Duplikatsschutz | TC-F10-006 | Doppelte Meldung verhindern | — | `tests/test_compliance.py::test_intrastat_duplicate_prevention` | ✅ | P1 |
| Intrastat | BR-INTRA-006: Korrekturmeldung | TC-F10-007 | Korrekturmeldung erstellen | — | `tests/test_compliance.py::test_intrastat_correction` | 🔄 | P1 |

**F10 Coverage:** 7/7 Test Cases definiert | Automation: 6 automatisiert, 1 in Entwicklung

---

## F11 — GS1/SSCC Barcode-System

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| GS1/SSCC | BR-GS1-001: SSCC generieren | TC-F11-001 | SSCC-Nummer GS1-konform generieren | — | `tests/test_gs1_sscc.py::test_sscc_generation` | ✅ | P1 |
| GS1/SSCC | BR-GS1-002: SSCC zuordnen | TC-F11-002 | SSCC einer Lagereinheit zuordnen | — | `tests/test_gs1_sscc.py::test_sscc_assignment` | ✅ | P1 |
| GS1/SSCC | BR-GS1-003: Label-Druck | TC-F11-003 | GS1-128 Barcode-Label als PDF | — | `tests/test_gs1_sscc.py::test_label_pdf_generation` | 🔄 | P1 |
| GS1/SSCC | BR-GS1-004: Scan-Einlagerung | TC-F11-004 | SSCC-Scan in Einlagerung | — | `tests/test_gs1_sscc.py::test_sscc_scan_inbound` | ✅ | P1 |
| GS1/SSCC | BR-GS1-005: Rückverfolgung | TC-F11-005 | Rückverfolgung über SSCC | — | `tests/test_gs1_sscc.py::test_sscc_traceability` | ⏳ | P1 |

**F11 Coverage:** 5/5 Test Cases definiert | Automation: 3 automatisiert, 1 in Entwicklung, 1 geplant

---

## F12 — eBilanz / XBRL-Export

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| eBilanz | BR-EBIL-001: XBRL-Mapping | TC-F12-001 | eBilanz-Daten in XBRL-Taxonomie mappen | — | `tests/test_ebilanz.py::test_xbrl_mapping` | 🔄 | P0 |
| eBilanz | BR-EBIL-002: XBRL valide | TC-F12-002 | XBRL-Datei gegen HGB-Taxonomie validieren | — | `tests/test_ebilanz.py::test_xbrl_validation` | 🔄 | P0 |
| eBilanz | BR-EBIL-003: Plausibilität | TC-F12-003 | Plausibilitätsprüfung vor Export (Aktiva = Passiva) | — | `tests/test_ebilanz.py::test_balance_check` | ✅ | P0 |
| eBilanz | BR-EBIL-004: ELSTER-Format | TC-F12-004 | Export für ELSTER-Upload geeignet | — | `tests/test_ebilanz.py::test_elster_format` | 🔄 | P0 |
| eBilanz | BR-EBIL-005: Archivierung | TC-F12-005 | Jahresabschluss-Versionsverwaltung | — | `tests/test_ebilanz.py::test_version_archive` | ⏳ | P0 |

**F12 Coverage:** 5/5 Test Cases definiert | Automation: 1 automatisiert, 3 in Entwicklung, 1 geplant

---

## F13 — Genossenschaft (Mitgliederverwaltung)

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| Geno | BR-GENO-001: Mitglied anlegen | TC-F13-001 | Mitglied mit Pflichtfeldern anlegen | `admin/genossenschaft.spec.ts` → "Mitglied anlegen" | `tests/test_genossenschaft.py::test_create_member` | 🔄 | P1 |
| Geno | BR-GENO-002: Geschäftsanteile | TC-F13-002 | Geschäftsanteile-Verwaltung (Zeichnung/Kündigung) | — | `tests/test_genossenschaft.py::test_shares_management` | 🔄 | P1 |
| Geno | BR-GENO-003: Dividende | TC-F13-003 | Dividendenberechnung auf Geschäftsanteilbasis | — | `tests/test_genossenschaft.py::test_dividend_calculation` | 🔄 | P1 |
| Geno | BR-GENO-004: Protokoll | TC-F13-004 | Mitgliederversammlung-Protokoll erstellen | `admin/genossenschaft.spec.ts` → "Protokoll" | — | ✏️ | P1 |
| Geno | BR-GENO-005: Mitgliederliste | TC-F13-005 | Mitgliederliste mit Filter und Export | `admin/genossenschaft.spec.ts` → "Liste" | `tests/test_genossenschaft.py::test_member_list_export` | 🔄 | P1 |

**F13 Coverage:** 5/5 Test Cases definiert | Automation: 3 in Entwicklung, 1 manuell, 1 in Entwicklung

---

## F14 — Webshop-Integration (L3-Connect)

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| Webshop | BR-WEB-001: Order-Import | TC-F14-001 | Webshop-Bestellung als ERP-Auftrag anlegen | — | `tests/test_l3_connect.py::test_order_import` | ✅ | P1 |
| Webshop | BR-WEB-002: Artikel-Sync | TC-F14-002 | Artikelstamm in Webshop synchronisieren | — | `tests/test_l3_connect.py::test_article_sync` | ✅ | P1 |
| Webshop | BR-WEB-003: Lagerbestand-Sync | TC-F14-003 | Lagerbestandsänderung an Webshop übertragen | — | `tests/test_l3_connect.py::test_stock_sync` | 🔄 | P1 |
| Webshop | BR-WEB-004: Status-Rückmeldung | TC-F14-004 | Bestellstatus-Updates an Webshop | — | `tests/test_l3_connect.py::test_status_callback` | 🔄 | P1 |
| Webshop | BR-WEB-005: Fehlerprotokoll | TC-F14-005 | Sync-Fehler protokollieren und nachverarbeiten | — | `tests/test_l3_connect.py::test_sync_error_handling` | ✅ | P1 |

**F14 Coverage:** 5/5 Test Cases definiert | Automation: 3 automatisiert, 2 in Entwicklung

---

## F15 — Process Kernel (Workflow-Engine)

| Feature | Business Req. | Test Case ID | Gherkin-Szenario | Playwright-Test | pytest-Test | Status | Risk |
|---|---|---|---|---|---|---|---|
| ProcessKernel | BR-PK-001: Instanz-CRUD | TC-F15-001 | Workflow-Instanz anlegen und führen | — | `tests/process_kernel/` (alle 903 Tests) | ✅ | P0 |
| ProcessKernel | BR-PK-002: Regression Wave 1-17 | TC-F15-002 | Regression aller 903 Wave-Tests | — | `pytest tests/ -m process_kernel` | ✅ | P0 |
| ProcessKernel | BR-PK-003: Genehmigungsworkflow | TC-F15-003 | Einreichen → Genehmigen → Ablehnen | — | `tests/test_ap_approval_workflow.py` (13 Tests) | ✅ | P0 |
| ProcessKernel | BR-PK-004: Agent-Actions | TC-F15-004 | Agent-Action via API auslösen | — | `tests/test_flow_spines.py::test_agent_action` | ✅ | P0 |
| ProcessKernel | BR-PK-005: Tenant-Isolation | TC-F15-005 | Workflow-Instanzen tenant-isoliert | — | `tests/test_tenant_isolation.py::test_workflow_isolation` | ✅ | P0 |
| ProcessKernel | BR-PK-006: Idempotenz | TC-F15-006 | ActionExecutionService — idempotente Ausführung | — | `tests/process_kernel/wave17/test_action_execution.py` | ✅ | P0 |

**F15 Coverage:** 6/6 Test Cases definiert | Automation: 6 automatisiert (100 %, 903 Tests)

---

## Gesamtübersicht Automationsstatus

| Feature | Test Cases | ✅ Automatisiert | 🔄 In Entwicklung | ✏️ Manuell | ⏳ Geplant | Coverage |
|---|---|---|---|---|---|---|
| F01 Ernte-Annahme | 10 | 8 | 2 | 0 | 0 | 100 % |
| F02 Agrar-Kontrakte | 9 | 7 | 2 | 0 | 0 | 100 % |
| F03 Agrar-Abrechnung | 9 | 2 | 5 | 1 | 1 | 100 % |
| F04 POS DSFinV-K | 7 | 5 | 2 | 0 | 0 | 100 % |
| F05 POS Retoure | 7 | 1 | 4 | 2 | 0 | 100 % |
| F06 POS Offline | 11 | 0 | 4 | 3 | 4 | 100 % |
| F07 Gelangensb. | 6 | 6 | 0 | 0 | 0 | 100 % |
| F08 Sanktionsprüfung | 5 | 5 | 0 | 0 | 0 | 100 % |
| F09 LKSG | 6 | 2 | 3 | 0 | 1 | 100 % |
| F10 Intrastat | 7 | 6 | 1 | 0 | 0 | 100 % |
| F11 GS1/SSCC | 5 | 3 | 1 | 0 | 1 | 100 % |
| F12 eBilanz | 5 | 1 | 3 | 0 | 1 | 100 % |
| F13 Genossenschaft | 5 | 0 | 4 | 1 | 0 | 100 % |
| F14 Webshop/L3 | 5 | 3 | 2 | 0 | 0 | 100 % |
| F15 Process Kernel | 6 | 6 | 0 | 0 | 0 | 100 % |
| **GESAMT** | **103** | **55 (53 %)** | **33 (32 %)** | **7 (7 %)** | **8 (8 %)** | **100 %** |

---

## Nicht-funktionale Test Cases

| Kategorie | Test Case ID | Beschreibung | Testwerkzeug | Status | Risk |
|---|---|---|---|---|---|
| Performance | TC-NFR-001 | GET Listendaten P95 ≤ 200 ms | k6 | ⏳ | P0 |
| Performance | TC-NFR-002 | POST Mutationen P95 ≤ 500 ms | k6 | ⏳ | P1 |
| Performance | TC-NFR-003 | DSFinV-K-Export P95 ≤ 5.000 ms | k6 | ⏳ | P1 |
| Security | TC-NFR-004 | 401 bei fehlendem Bearer-Token (alle Endpoints) | pytest parametrize | 🔄 | P0 |
| Security | TC-NFR-005 | 403 bei falschem Tenant-ID (alle Endpoints) | pytest parametrize | 🔄 | P0 |
| Security | TC-NFR-006 | SQL-Injection-Schutz | sqlmap safe-mode | ⏳ | P0 |
| Security | TC-NFR-007 | XSS-Schutz Frontend | OWASP ZAP | ⏳ | P0 |
| Accessibility | TC-NFR-008 | WCAG 2.2 AA — 0 Level-A/AA-Verstöße | axe-core/Playwright | 🔄 | P1 |
| Accessibility | TC-NFR-009 | Touch-Targets POS ≥ 44 × 44 px | axe-core | ⏳ | P1 |
| DSGVO | TC-NFR-010 | Kein PII in Anwendungs-Logs | Log-Scan-Script | 🔄 | P0 |
| DSGVO | TC-NFR-011 | Tenant-Datentrennung absolut | pytest multi-tenant | ✅ | P0 |
| GoBD | TC-NFR-012 | Buchungssätze unveränderbar nach Buchung | pytest | ✅ | P0 |
| GoBD | TC-NFR-013 | Audit-Trail vollständig (AuditMiddleware) | pytest | ✅ | P0 |

---

*Erstellt gemäß IEEE 829-2008 / ISTQB Requirements Traceability*  
*Stand: 2026-05-18 — wird mit jedem Release aktualisiert*
