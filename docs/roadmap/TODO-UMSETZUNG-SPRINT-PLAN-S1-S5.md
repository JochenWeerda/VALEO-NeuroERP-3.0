# TODO-Umsetzung: Sprint-Plan S1–S5 (Meilensteine M-01–M-12)

**Zweck:** Issue-/Sprint-Zuordnung für die einheitlich nummerierte Umsetzungs-Roadmap (Auth-Vertrag, erp-domain, E2E früh, CRM, DSGVO, FiBu, Strecke, OCR). Die Reihenfolge **M-01 → M-12** ist die fachlich-logische Kette; Sprints bündeln Arbeitspakete für Planung und Reviews.

**Tracking:** Nach größeren Abschlüssen `python scripts/update_todos.py --repo-only` ausführen und `docs/TODO-next-slices.md` prüfen (Slice-Volumen sollte sinken).

**Workboard:** Eintrag **TODO-SPRINT-001** in [`docs/agent-ops/active-workboard.md`](../agent-ops/active-workboard.md).

---

## Meilensteine (Kurzüberblick)

| ID | Kurzname | Inhalt |
|----|----------|--------|
| **M-01** | Auth-Vertrag | Technischer Vertrag Tenant/User/Service-Account/Fehlerbilder (ADR/RFC) |
| **M-02** | Pagination Contract | erp-domain: Listen-JSON + Repo `totalCount` filtergleich |
| **M-03** | Pagination Rollout | erp-domain: alle Controller auf M-02 |
| **M-04** | ERP Actor | erp-domain: Umsetzung M-01, kein blindes `system` in Prod |
| **M-05** | E2E Auth | Playwright-Helper an M-01; CRM-E2E-Specs stabil |
| **M-06** | CRM Auth | FastAPI `Depends`, Rollout crm-* |
| **M-07** | CRM E-Mail | eine Konfiguration + Sende-/Queue-Pfad |
| **M-08** | GDPR Export | Orchestrierung, Timeouts, Fehler transparent |
| **M-09** | GDPR Löschung | inkl. Retention, Ausnahmen, Audit, Idempotenz (siehe **M3.0–M3.4 Legal/ERP-Policy**) |
| **M-10** | FiBu Perioden | `is_closed`, `balance_check` echt; Warn/Hard-Fail dokumentiert |
| **M-11** | Strecke DB | Migration, Rollback-Strategie, optional Dev-Seed |
| **M-12** | Einkauf OCR | Teilprojekt, Feature-Flag, Pilotkorpus |

---

## Sprint-Zuordnung (S1–S5)

| Sprint | Meilensteine | Schwerpunkt |
|--------|--------------|-------------|
| **S1** | M-01, M-02 | Gemeinsamer Auth-/Tenant-Vertrag; Pagination-Kern (Contract + Repos) legt das Fundament für alle APIs und Tests. |
| **S2** | M-03, M-04, M-05 | ERP-Listen fertig; Actor/Tenant im erp-domain; **E2E-Auth früh**, damit UI-Regression parallel zu CRM (S3) möglich ist. |
| **S3** | M-06, M-07 | CRM-Plattform: Authentifizierung über Dienste; danach eine E-Mail-/Queue-Basis für Marketing/GDPR/Consent/Communication. |
| **S4** | M-08, M-09, M-10 | DSGVO Export → Löschung (mit Legal zu **M-09 / M3.0 Policy-Foundation vor produktiver Erasure-Orchestrierung**); FiBu-Perioden/Saldo parallel (Finance-Team), technisch entkoppelt von CRM-Slice. |
| **S5** | M-11, M-12 | Strecke produktionsnah (Persistenz + Migrations-/Rollback-Disziplin); OCR als **gleitendes** Teilprojekt mit niedriger Kopplung. |

---

## M3.0–M3.4 — Legal/ERP-Domain: Policy-gestützte Lösch- und Retention-Architektur

**Einordnung:** Ergänzende Meilenstein-Kette vor **dem produktiven** Einsatz von Datenexport (**M3.1**), Löschung/Anonymisierung (**M3.2**) und FiBu-/GoBD-Themen (**M3.3**) im Kernsystem. Über **M-08/M-09** hinaus, falls CRM-only zuerst; für **ERP-/FiBu-/GoBD-relevante** Bestände zwingende Vorstufe.

**Ziel:** Lösch-, Anonymisierungs- und Verarbeitungs­einschränkungs-Prozesse laufen nicht als direkte technische DELETE-Kaskade, sondern über eine **zentrale Policy- und Retention-Entscheidungsschicht** mit revisionssicherem Nachweis.

**Leitlinie:** Nicht „löschen und hoffen“, sondern **Policy-Entscheidung → nur erlaubte Aktion → Audit mit Policy-Version und Grund** — im Einklang mit Art. 17 DSGVO einschl. Ausnahmen; für Deutschland zusätzlich **Einschränkung der Verarbeitung** (Art. 18 DSGVO) dort, wo Aufbewahrungspflichten entgegenstehen. Für produktive Systeme keine GoBD-/Retention-Interpretation „nur aus dem Kopf“: **aktuell freigegebene regulatorische/policy-seitige Leitlinien** (z. B. BMF-Verwaltungsanweisungen) einbeziehen; **Legal/Datenschutz/Fachbereich** freigen die Policy-Matrix.

### M3.0 — Legal/ERP-Domain Policy Foundation (Voraussetzung)

**ADR (Entwurf):** [adr-2026-05-06-erasure-decision-api-and-audit.md](../architecture/adr-2026-05-06-erasure-decision-api-and-audit.md)

**Policy-Rahmen (Entwurf):** [erasure-retention-audit-policy.md](../policies/erasure-retention-audit-policy.md)

> **Verbindliche Produktfreigabe-Leitplanke:** Produktive Löschung, Anonymisierung oder Entkopplung personenbezogener Daten mit möglichem ERP-, FiBu-, Rechnungs-, GoBD- oder Auditbezug ist erst zulässig, wenn eine versionierte Policy-Entscheidung vorliegt, der evaluate/execute-Split umgesetzt ist, jede relevante Entscheidung auditierbar persistiert wird und Architektur, Legal, Datenschutz sowie ERP-Fachbereich die Policy-Matrix abgenommen haben.

Deliverables:

- Datenklassifikation für CRM-, ERP-, FiBu-, Audit- und Belegdaten.
- Retention-/Legal-Hold-Modell inkl. GoBD-/steuerlicher Aufbewahrungsgründe (als **konfigurierbare/review-fähige** Regeln, nicht als versteckte Annahmen im Orchestrierungscode).
- **Policy-Entscheidungsservice** (Service oder sauber gekapseltes Modul): Rückgabe strukturierter Entscheidung, z. B. `{ decision, reason, retention_until?, allowed_actions[], requires_legal_review }`.
- **State Machine** für Erasure-Anträge (z. B. REQUESTED → … → POLICY_CHECKED → APPROVED_* / DENIED_RETENTION / LEGAL_REVIEW_REQUIRED → EXECUTED → VERIFIED → CLOSED).
- **First-Class Blocker-Konzept** (GoBD-, Steuer-, offene Posten, Legal Hold, vertragliche Fristen, Audit-Pflicht) — API-taugliche Codes/Messages.
- Persistenter, möglichst manipulationssicherer **Audit-Trail** mit Tenant, Zeitstempel, Policy-Version, Korrelation — **minimal personenbezogen** (`subject_ref`, `actor_ref`/Hash statt Klarnamen in sensiblen Events).

Abnahme (Minimal): Policy-Engine liefert für definierte Szenario-Fälle reproduzierbare Entscheidungen; Legal/Privacy haben die erste Policy-Matrix abgenommen.

**Nicht-Ziel:** Go-Live ohne Legal-/Datenschutz-Review.

### M3.1 — Datenexport (auf Policy abgestützt)

Export nur nach Identität/Scope; Quellenliste und verwendete Policy-Version im Export-Manifest/Audit nachvollziehbar.

### M3.2 — Löschung / Anonymisierung / Einschränkung

Technische Umsetzung **nur** der von M3.0 erlaubten Aktionen (delete vs. anonymize vs. pseudonymize vs. restrict); Ablehnungen und Teilerfolge sind API- und Audit-first.

### M3.3 — ERP/FiBu Retention & Legal Holds

Blocker aus Belege/Buchungen/Offerten mit Belegbezug/Forderungen als echte Daten, nicht Kommentare; **kein Hard-Delete** aufbewahrungspflichtiger Belege während gültiger Frist (unveränderbare Speicherung / technische Ableitung je nach Produktkonzept — mit Legal abstimmen).

### M3.4 — Audit / Proof Package

Nachweisbündel für Audits/Beschwerden (Export der Entscheidungskette, Policy-Version, ausgeführte und verweigerte Schritte, Korrelations-IDs).

### API-Orientierung (Ziel-Schnittstellen, keine CRUD-Shortcuts)

Dedizierte Endpoints statt generischem `DELETE /customers/{id}` wo ERP/FiBu betroffen ist, z. B.:

- `POST /privacy/erasure-requests` · `POST …/evaluate` · `POST …/execute` · `GET …/audit`
- ERP-nah: `POST /erp/subjects/{id}/pseudonymize` · `POST …/restrict-processing` · `GET …/retention-blockers` · `GET …/legal-holds`

(Die konkrete Router-Hierarchie an eure bestehende API-/Gateway-Konvention anbinden.)

---

## Abhängigkeiten (für die Sprint-Planung)

- **M-04** und **M-05** setzen **M-01** voraus; **M-03** baut auf **M-02**.
- **M-06**–**M-09** profitieren von **M-01** (Kontext in Logs und APIs); **M-08**/**M-09** logisch nach **M-06** (identifizierbarer Actor).
- **M-09 / produktive Erasure-Logik** setzt fachlich **M3.0 (Policy-/Retention-Schicht)** voraus: keine naive „DELETE überall“-Orchestrierung für ERP-/FiBu-/GoBD-nahe Daten ohne Entscheidungsservice, Statusmodell und revisionssicheren Audit (Details unten).
- **M-10** kann in **S4** parallel zu **M-08** laufen, wenn Kapazität getrennt ist (Finance vs. CRM/Legal).
- **M-11** und **M-12** sind gegenüber **M-01**–**M-07** weitgehend unabhängig; **M-12** nur koordinieren, wenn Einkauf dieselben Secrets/Deployments nutzt.

---

## Sprint-Exit-Kriterien (Minimal)

| Sprint | Exit (Definition of Done auf Roadmap-Ebene) |
|--------|-----------------------------------------------|
| S1 | M-01 abgenommen; M-02 mindestens ein Domänencluster + Contract-Doc gemerged. |
| S2 | Keine offenen Pagination-TODOs im erp-domain-Zielpfad; M-04 Review; E2E-Basis grün für vereinbarte CRM-Specs. |
| S3 | CRM-Dienste ohne produktives Blind-`system` (Ausnahmen dokumentiert); ein gemeinsamer Mail-/Send-Pfad nutzbar. |
| S4 | Export und Löschpfad mit Legal/Privacy abgestimmt; **Erasure-/Retention-Policy (M3.0)** freigegeben oder bewusst nur CRM-reine Fälle; FiBu-Flags aus echter Datenlage. |
| S5 | Strecke in Staging mit Migration/Rollback getestet; OCR nur nach Milestone-Definition (Pilot/Flag). |

---

*Stand: Sprint-/Meilenstein-Struktur abgestimmt mit der detaillierten Roadmap (Meilensteine M-01–M-12). Anpassungen an Teamkapazität: Meilensteine innerhalb eines Sprints umsortieren, nicht die IDs wechseln.*
