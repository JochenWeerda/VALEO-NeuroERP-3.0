# Index: „Geplant“ – Umsetzungspotenzial

**Prinzip:** Überall, wo „geplant“ oder „Geplant“ im Projekt vorkommt, kann noch die Umsetzung erfolgen. Dieser Index listet die relevanten Stellen zur Priorisierung und Abarbeitung.

**Erstellt:** 2026-03-05 | **Aktualisiert:** 2026-03-05 (Bulk-Umsetzung)

---

## 1. Architektur & APIs

| Quelle | Beschreibung | Status |
|--------|--------------|--------|
| [ADR-002](adr/adr-002-fibu-frontend-api-layer.md) | **Fibu-Gateway** (Anti-Corruption Layer) | ✅ **Implementiert** — `services/finance/fibu-gateway/` |
| [UX-STANDARD-VALEO.md](UX-STANDARD-VALEO.md) | **KI-Usability-Microservices** (Sprachsteuerung, Action Registry) | ✅ **Implementiert** — Backend integriert in Haupt-App (`/api/v1/actions`, `/api/v1/voice/resolve`), optional Microservice `services/ki-usability/` |

---

## 2. FiBu / Schnittstellen

| Quelle | Beschreibung | Status |
|--------|--------------|--------|
| [schnittstellen-center.tsx](../packages/frontend-web/src/pages/fibu/schnittstellen-center.tsx) | Connectoren mit `status: 'planned'` | ✅ **ATLAS, ELSTER, Anlagen-Import** als geplante Connectoren ergänzt; Umsetzung der APIs pending |
| [gap-closure](../.cursor/plans/gap-closure_master_plan_ab0cb3b1.plan.md) | Anlagenbuchhaltung, Intercompany | Optional, bei Bedarf |

---

## 3. Compliance & Sicherheit

| Quelle | Beschreibung | Status |
|--------|--------------|--------|
| [iso27001-gap-analysis.md](compliance/iso27001-gap-analysis.md) | Quarterly Access-Review (geplant) | ✅ **Prozess dokumentiert** — [iso27001-quarterly-review-process.md](compliance/iso27001-quarterly-review-process.md) |
| [SECURITY-FOUNDATION-AUDIT.md](../SECURITY-FOUNDATION-AUDIT.md) | Export-/Restore-Ratelimits (geplant) | ✅ **Implementiert** — `@limiter.limit` auf Policy Export (10/min) und Restore (5/min) |
| [operator-runbooks.md](operator-runbooks.md) | Export 10/min, Restore 5/min | ✅ **Abschnitt 6a** + Rate-Limits in `policies.py`, `policy/router.py` |

---

## 4. Domain-Status (bereits implementiert)

Diese Stellen nutzen „geplant“ als **fachlichen Status**, nicht als technische TODO:

| Quelle | Verwendung |
|--------|------------|
| `kampagnen.tsx`, `aussaat/liste.tsx`, `biodiversitaet.tsx` | Status-Badge für Kampagnen/Aussaaten/Flächen |
| `operations/models.py`, `alembic/...` | `status = "geplant"` in Aufträgen, Planungen |
| `anlieferavis` | `geplantesAnlieferDatum` – Feld vorhanden |
| `einkauf_bestellvorschlag` | `geplante_auslagerung` – Feld vorhanden |

---

## 5. Noch offen (Umsetzungspotenzial)

| Quelle | Beschreibung |
|--------|--------------|
| ATLAS-Connector | Platzhalter-Seite `/fibu/atlas` vorhanden; Backend-API für Zollanmeldungen folgt |
| ELSTER-Online-Connector | Platzhalter-Seite `/fibu/elster-online` vorhanden; direkte Übermittlung folgt |
| Anlagen-Import (CSV/DATEV) | Anlagen-Suite hat Import-Wizard; erweiterter DATEV-Import optional |
| PAM (Privileged-Access-Management) | iso27001-gap-analysis A.9.2 |
| Encryption-at-Rest | PostgreSQL TDE, Redis-Modul |

---

## 6. Sprints / Roadmap (Referenz)

| Quelle | Kontext |
|--------|---------|
| `swarm/status/sprint-*.md`, `swarm/missions/*.md` | Sprint-Status „Geplant“ – historisch |
| [docs/roadmap/status/](../docs/roadmap/) | ELSTER/ATLAS-Schnittstellen |

---

## 7. Checklisten (Prozess)

| Quelle | Verwendung |
|--------|------------|
| `RELEASE-RUNBOOK.md`, `DEPLOYMENT-PLAN.md`, `PRE-DEPLOYMENT-CHECK.md` | Maintenance-Window, Post-Mortem, UAT-Slots „geplant“ – organisatorisch |

---

*Bei jeder Abarbeitung: Status in dieser Tabelle aktualisieren.*
