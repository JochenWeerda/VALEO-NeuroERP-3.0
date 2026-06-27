---
title: AI-assisted Enterprise Development Standard
type: reference
audience: [entwickler, agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Accepted-Standard fuer AI-gestuetzte Enterprise-Entwicklung in VALEO NeuroERP — Slice-Workflow, Governance, Qualitaetsgates.
---

# AI-assisted Enterprise Development Standard

**Status:** Accepted
**Datum:** 2026-06-23
**Quelle:** Auswertung des Nutzer-Transkripts "Der Moment, der die Softwareentwicklung geaendert hat!" fuer VALEO NeuroERP.

**Umsetzungsplan:** `docs/project-context/ai-assisted-development-implementation-plan-2026-06-23.md`

## 1. Kernaussage fuer VALEO

KI-gestuetzte Entwicklung ist fuer VALEO kein "Vibe Coding", sondern ein beschleunigter Enterprise-Engineering-Prozess. Der Produktivitaetsgewinn entsteht nicht durch ungeprueft generierten Code, sondern durch einen harten Harness aus Anforderungen, Architekturregeln, Tests, Dokumentation, Review-Gates und Agentenkoordination.

Die relevante Lehre aus dem Transkript ist nicht der behauptete Beschleunigungsfaktor. Relevant ist:

- Grosse Systeme koennen mit KI schneller gebaut werden, wenn Anforderungen und Leitplanken maschinenlesbar sind.
- Qualitaet steigt nur, wenn Architektur- und Testregeln vor der Codegenerierung explizit sind.
- Der erfahrene Entwickler bleibt verantwortlich fuer Architektur, Priorisierung, Risiko, Review und Abnahme.
- Dokumentation muss laufend gegen Code und Tests synchronisiert werden.
- Kosten, Datenschutz, Anbieterabhaengigkeit, Haftung und Security muessen als Engineering-Gates behandelt werden.

## 2. Was nicht uebernommen wird

VALEO uebernimmt keine unbewiesenen Marketing-Schluesse aus dem Transkript:

- Kein pauschaler Produktivitaetsfaktor als Planungsbasis.
- Keine Annahme, dass KI semantische Verantwortung traegt.
- Keine Absenkung von Review-, Security-, Audit- oder Fachabnahmestandards.
- Keine ungepruefte Modell- oder Vendor-Bindung.
- Keine Akzeptanz von Code ohne reproduzierbare Tests und fachliche Evidenz.

Jeder KI-Beitrag ist ein Vorschlag, bis er durch Gates belegt ist.

## 3. Der VALEO Harness

Jeder groessere Slice muss in VALEO aus diesen Bausteinen bestehen:

| Ebene | Mindeststandard |
|-------|-----------------|
| Fachlicher Vertrag | User Story, Akzeptanzkriterien, betroffene Domain, Soll-Prozess, Randfaelle |
| Architekturvertrag | ADR/Statusbezug, erlaubte Module, Dateibesitz, Schnittstellen, Migrationsrisiko |
| Datenvertrag | Schema, Tenant-Scope, Idempotenz, Auditfelder, Versionierung, Rueckwaertskompatibilitaet |
| Testvertrag | Unit, Contract, Integration, Playwright/Workflow-Test je Risiko |
| Security-Vertrag | Auth, Tenant-Isolation, Secrets, PII, Injection, SSRF, XSS, Audit |
| Betriebsvertrag | Healthcheck, Logs, Observability, Rollback, Feature Flag oder Kill Switch bei Risiko |
| Dokumentationsvertrag | Workboard, Slice-YAML, relevante Fach-/QA-/Runbook-Doku |

Ohne diese Bausteine ist ein Slice nicht "fertig", auch wenn Code kompiliert.

## 4. Best Practices fuer Agentenarbeit

### 4.1 Kontext vor Code

Vor jeder Umsetzung muessen Agenten lesen:

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/architecture/process-kernel/STATUS.md`
4. `docs/agent-ops/active-workboard.md`
5. relevante Fach-, Workflow- und QA-Dokumente

Danach erst wird entschieden, ob ein neuer Slice noetig ist oder bestehende Arbeit fortgesetzt wird.

### 4.2 Kleine, beweisbare Slices

KI wird am staerksten, wenn Aufgaben klein genug fuer harte Abnahme sind. Fuer VALEO gilt:

- Ein Slice hat klaren Dateibesitz.
- Ein Slice hat messbare Abnahmekriterien.
- Ein Slice hat Tests oder einen begruendeten externen Gate.
- Ein Slice wird nicht mit fremdem uncommitted WIP vermischt.
- Konflikte werden ueber das Workboard geloest, nicht durch Reverts.

### 4.3 Deterministische Workflows vor Agentenmagie

Wo Geschaeftslogik deterministisch ist, muss sie als Workflow, Policy, Rule Engine, Contract oder BPMN-/Action-Matrix abgebildet werden. KI darf assistieren, aber nicht verdeckt entscheiden.

Beispiele:

- CRM360-Klickvertrag statt blindem UI-Crawler.
- POS/TSE-UAT mit Mock-Zertifikat und Belegnachweis statt Sichtpruefung.
- WMS-Silo-Lot-Buchung als transaktionaler Service statt UI-only-Verknuepfung.
- Payroll/FiBu/DATEV als Exportvertrag mit externem Gate statt behaupteter Zertifizierung.

### 4.4 Nightly Documentation Sync

Das Transkript betont zu Recht, dass Doku sonst schnell vom Code abweicht. Fuer VALEO ist daraus der Zielstandard:

- Nightly oder CI-Job prueft, ob geaenderte Codebereiche passende Doku-Updates haben.
- API-/Route-/Action-Inventare werden generiert und versioniert.
- Offene Gaps werden nicht in Chatverlaeufen versteckt, sondern in `open-gaps-and-known-issues.md`, Workboard oder Slice-YAML dokumentiert.
- Bei Drift zwischen Doku und Code gilt der Drift als Fehler, nicht als Nebensache.

## 5. Qualitaetsmetriken

VALEO bewertet KI-gestuetzte Arbeit nicht nach erzeugten Lines of Code, sondern nach belastbarer Evidenz:

| Metrik | Ziel |
|--------|------|
| Kritische Pfade getestet | Pflicht fuer ERP-Kernprozesse |
| Contract-/API-Tests | Pflicht fuer neue oder geaenderte Endpunkte |
| Playwright/Workflow-Tests | Pflicht fuer fachliche UI-Flows mit Navigation, CRUD, Back-Verhalten |
| Security-Audit | Pflicht bei Auth, Tenant, Zahlungs-, POS-, HR-, FiBu-, DMS- und Integrationscode |
| Doku-Sync | Pflicht bei jeder relevanten fachlichen Aenderung |
| Structural Debt | Keine bewusste Architekturabweichung ohne ADR oder dokumentierte Ausnahme |
| Build/Type/Lint | Muss gruene Gates haben oder explizit als bestehender externer Blocker dokumentiert sein |

Coverage allein reicht nicht. Tests muessen die fachlich kritischen Pfade abdecken.

## 6. Rolle des Entwicklers

Der Entwickler wird nicht durch den Agenten ersetzt. Die Rolle verschiebt sich:

- Anforderungen in pruefbare Vertrage zerlegen.
- Architekturleitplanken setzen.
- Modell, Tool und Ausfuehrungsmodus passend waehlen.
- Agentenergebnisse reviewen und haerten.
- Risiken gegen Datenschutz, Security, Betrieb und Kosten bewerten.
- Fachliche Plausibilitaet pruefen.
- Externe Gates organisieren, wo rechtliche oder zertifizierende Abnahme noetig ist.

Fuer VALEO ist Senioritaet damit noch wichtiger: Ohne gute Leitplanken produziert KI schneller falsche Systemteile.

## 7. Modell- und Anbieterstrategie

VALEO darf sich nicht auf ein einzelnes Modell oder einen einzelnen Anbieter festlegen.

Mindestregeln:

- Agenten- und Toolvertraege muessen modellneutral dokumentiert werden.
- Prompts, Akzeptanzkriterien und Tests gehoeren ins Repo, nicht nur in Chatverlaeufe.
- Kritische Architekturentscheidungen duerfen nicht nur aus Modellantworten entstehen.
- Fuer vertrauliche Daten gelten Datenschutz- und Datenresidenzregeln aus den ADRs.
- Lokale oder alternative Modelle sind fuer sensible, wiederholbare oder kostenintensive Aufgaben zu pruefen.
- Bei Anbieterstoerung muss das Projekt mit anderem Modell oder ohne Agenten fortfuehrbar bleiben.

## 8. Security, Haftung und Compliance

KI-generierter Code ist in VALEO nicht weniger haftungsrelevant als handgeschriebener Code. Fuer risikobehaftete Bereiche gelten mindestens externe oder simulierte Prueferstandards:

- POS/TSE: Beleg, Tagesabschluss, DSFinV-K/TSE-Kontext, Zahlungsarten, Fibu-Uebergabe.
- FiBu/Payroll: DATEV-/Kanzlei-Testimport, Buchungssatz-Balance, Periodenabgrenzung, Korrekturpfade.
- HR: DSGVO, Rollenrechte, Protokollierung, gesetzliche Fristen.
- DMS/OCR: Nachvollziehbarkeit, Audit Evidence, Retention.
- WMS/Produktion/QS: Charge, Lot, Sperre/Freigabe, Trace, GMP+/VLOG-Nachweise.
- Externe Agenten: Least Privilege, delegierte Kontexte, Human Approval fuer irreversible Aktionen.

Wenn ein Bereich zertifizierungs- oder prueferrelevant ist, darf VALEO intern nur "simuliert bestanden" dokumentieren, bis das externe Gate real abgeschlossen ist.

## 9. Umgang mit Geschwindigkeit

Hohe Geschwindigkeit ist nur wertvoll, wenn sie wartbare Geschwindigkeit bleibt.

Deshalb gilt:

- Erst Harness, dann Umsetzung.
- Erst Contract, dann UI.
- Erst transaktionale Domain-Logik, dann Visualisierung.
- Erst reproduzierbarer Test, dann Release-Behauptung.
- Erst kleine Slices, dann breite Rollouts.

Wenn KI-Arbeit zu grossen, schwer reviewbaren Diff-Bloecken fuehrt, ist der Prozess falsch geschnitten.

## 10. Konkrete Konsequenzen fuer die weitere VALEO-Entwicklung

1. Fuer neue Domain-Vertiefungen wird vorab eine Action-/Contract-Matrix erstellt.
2. Fuer alle kritischen UI-Flows werden semantische Playwright-Tests bevorzugt.
3. Fuer alle Cross-Domain-Prozesse wird ein fachlicher E2E-Beleg verlangt.
4. Agenten muessen Workboard-Dateibesitz strikt einhalten.
5. Doku-Drift wird als Release-Risiko behandelt.
6. Externe Gates werden explizit getrennt von internen Simulationen dokumentiert.
7. Major Updates bei Sicherheitsluecken werden ueber Kompatibilitaetsmatrix, Contract-Tests, Canary/Feature Flag und Rollback-Plan gefuehrt.
8. Wiederkehrende Agentenfehler werden als Prozessfehler analysiert: fehlender Kontext, zu grosser Slice, unklare Akzeptanz, fehlender Test oder paralleler Dateikonflikt.

## 11. Mindest-Definition of Done fuer AI-Slices

Ein AI-unterstuetzter Slice ist erst abgeschlossen, wenn:

- Code kompiliert und relevante Tests laufen.
- Fachlicher Soll-Prozess nachweisbar erfuellt ist.
- Security- und Tenant-Risiken geprueft sind.
- Doku aktualisiert ist.
- Workboard/Slice-YAML den finalen Stand zeigt.
- Offene externe Gates klar benannt sind.
- Keine fremden WIP-Aenderungen versehentlich gebuendelt wurden.

Diese Definition gilt auch dann, wenn der Agent "fertig" meldet.
