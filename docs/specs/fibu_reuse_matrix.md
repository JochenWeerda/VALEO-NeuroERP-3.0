# FiBu Reuse Matrix (Backend & Frontend)

Die folgende Matrix fasst den aktuellen Stand aller FiBu-relevanten Codeartefakte zusammen und bewertet sie anhand der Kriterien:

- **Architecture Fit** – passt zum Zielbild (Microservices, Events, GoBD)?
- **Technical Debt** – Pflegezustand, Duplikate, fehlende Abhängigkeiten.
- **Test Coverage / Confidence** – existieren Tests bzw. Dokumentation?
- **Compliance Readiness** – Nähe zu GoBD/gesetzlichen Anforderungen.

Bewertungsskala: **Reuse as is**, **Refactor & Reuse**, **Replace / Neu implementieren**.

---

## Backend

| Komponente | Bereich | Stack | Bewertung | Begründung / Maßnahmen |
| --- | --- | --- | --- | --- |
| `packages/finance-domain` (TS) | Domänenlogik (Ledger, AP/AR, Tax, AI) | Node/TypeScript | **Refactor & Reuse** | Fachlich vollständig, gute Tests & README. Muss für Python-Services portiert oder via Wrapper angebunden werden. Doppelte Quelle mit `domains/finance` konsolidieren. |
| `domains/finance` (TS) | Duplikat der o. g. Domain | Node/TypeScript | **Replace** | Enthält dieselben Dateien → führt zu Drift. Empfohlen: eine Quelle archivieren, andere als Referenz beibehalten. |
| `services/finance/` | FastAPI-Stubs | Python | **Replace** | Referenziert nicht existierende Module (`app.core.*`), keine Schemas/Repos. Komplett neu aufsetzen (Phase 2). |
| `app/api/v1/schemas/finance.py` | Pydantic-Schemas | Python | **Reuse as is** | Umfangreiche Validierung für Konten & Journal; muss mit Shared Contracts synchron gehalten werden. |
| `packages/shared/contracts/src/finance-schemas.ts` | Cross-Domain Events/API Contracts | TypeScript | **Reuse as is** | Saubere Zod-Definitionen. Basis für Middleware/Event-Mapping. |
| `.github/workflows/finance-domain-ci.yml` | CI für TS-Domain | YAML | **Refactor** | Nützlich für Referenz-Builds. Sollte erweitert werden, sobald neue Python-Services existieren. |
| `monitoring/grafana/dashboards/finance-domain-dashboard.json` | Observability | Grafana | **Refactor & Reuse** | Dashboard existiert; Metriknamen müssen an neue Services angepasst werden. |
| `docs/specs/fibu_architektur_spezifikation.md` | Zielarchitektur | Markdown | **Reuse as is** | Dient als Referenz für alle Phasen. |

## Frontend

| Komponente | Bereich | Bewertung | Hinweise |
| --- | --- | --- | --- |
| `src/pages/finance/chart-of-accounts.tsx` etc. | CRUD-Views (Konten, Debitoren, Kreditoren, OP, Bank) | **Refactor & Reuse** | UI + Validierungen vorhanden; muss an neue APIs (GraphQL/REST) gekoppelt werden. |
| `src/pages/finance/buchungserfassung.tsx`, `abschluss.tsx`, `ustva.tsx` | Mask Builder-Formulare | **Refactor & Reuse** | Maskenkonfigurationen solide. GoBD-Hinweise bereits enthalten. Benötigen echte Endpunkte & Document Linking. |
| `src/pages/finance/mahnwesen.tsx`, `zahlungslauf-kreditoren.tsx`, `lastschriften-debitoren.tsx` | AR/AP Workflows | **Refactor & Reuse** | Flow vorhanden (Statuskarten, Actions). Abhängigkeit zu OP-Service & Payment APIs. |
| `src/lib/services/finance-service.ts` | Axios-Client | **Replace** | Eng gekoppelt an alte REST-Endpunkte, keine Mandantenauswahl. Empfehlung: modulare API-Layer pro Microservice oder GraphQL. |
| `src/config/mask-builder-valeo-modern.json` + Mask Builder Komponenten | UX-Engine | **Reuse as is** | Generische Engine funktioniert. Muss ggf. Stabilitätsbugs beheben (ts-ignore). |
| Navigation (Sidebar/Command Palette) | Menüführung | **Reuse as is** | Nur Berechtigungen/Feature Flags aktualisieren. |

## Cross-Cutting

| Thema | Bewertung | Maßnahmen |
| --- | --- | --- |
| **Middleware / Anti-Corruption Layer** | **Neu implementieren** | `fibu-gateway` gemäß Phase‑1 Plan aufbauen, Contracts aus Shared Schemas & Pydantic ableiten. |
| **GoBD-Compliance** | **Refactor** | Audit-Trail, Hash-Chains, Unveränderbarkeit im Backend implementieren; UI-Verknüpfung Buchung ↔ Beleg sicherstellen. |
| **Multi-Tenancy & Roles** | **Replace** | Frontend nutzt Hardcoded Tenant; Backend noch ohne Auth. Globale AuthZ/Approval-Policies definieren. |
| **Observability & Alerting** | **Refactor** | Bestehende Grafana-Dashboard & Prometheus-Middleware adaptieren, Metriken pro Service definieren. |

---

## Fazit

- **Was wir behalten können:** Domänenlogik (TS), Pydantic/Zod-Schemas, vorhandene React-Views & Mask Builder, Dokumentation/READMEs.
- **Was neu entsteht:** Python-Microservices (`fibu-core`, `fibu-master-data`, …) inkl. GoBD-Storage, Middleware/Adapter-Schicht, aktualisierter API-Client.
- **Sofortige Schritte:** Konsolidierung der TypeScript-Domain (eine Quelle), Neuaufbau des Finance-Service, Definition verbindlicher Event-/API-Kontrakte, Frontend-API-Layer modularisieren.

