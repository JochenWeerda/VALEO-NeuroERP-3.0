# FiBu Backend Code Inventory

Stand: aktuelle Codebasis `VALEO-NeuroERP-3.0`

Ziel dieser Übersicht ist es, alle vorhandenen Backend-Bausteine mit FiBu-Bezug zu erfassen, ihren Reifegrad zu bewerten und Hinweise zur Wiederverwendung im geplanten GoBD-konformen Finanz-Stack zu liefern.

---

## 1. Node/TypeScript Finance Domain (dupliziert in `packages/finance-domain` & `domains/finance`)

| Aspekt | Details |
| --- | --- |
| Funktionsumfang | Vollständig strukturierte Clean-Architecture-Domain mit Application-Services (`ledger-service`, `ap-invoice-service`, `ar-invoice-service`, `tax-compliance-service`, `bank-reconciliation-service`, `forecasting-service`, `zugferd-adapter-service`, `ai-bookkeeper-service`, `audit-assist-service`). |
| Technologiestack | TypeScript, Node.js, tsup Bundling, Clean Architecture (entities, repositories, services), EventBus-Abstraktionen, Messaging Layer (Kafka/NATS placeholder), Observability Helpers. |
| Artefakte | Dockerfile, docker-compose, tsconfig, README (umfangreiche Beschreibung + Quickstart), Tests (`tests/unit`, `tests/integration`), Dist-Ordner mit kompilierten Artefakten. |
| Domain-Objekte | `src/core/entities` (AP/AR Invoice, Ledger, Accounting Period), `src/core/domain-events/finance-domain-events.ts`, `src/core/constants/finance-constants.ts`. |
| Infrastruktur | `src/infrastructure` liefert Repos (Postgres), Cache, Messaging, External Services, Observability, Security. |
| Präsentationsschicht | `src/presentation/controllers/finance-api-controller.ts`. |
| Reuse-Potenzial | **Hoch** für Domänenlogik, Event-Modelle und Tests – jedoch NodeJS. Für Python-Microservices müssten Portierung/Wrapper bedacht werden. Eventuelle Konsolidierung (nur ein Source-Verzeichnis behalten) nötig. |
| Risiken | Doppelte Codebasis (`packages/` vs. `domains/`), keine direkte Integration in Python-Service-Landschaft, heterogener Stack. |

## 2. Python Microservice Stub `services/finance`

| Aspekt | Details |
| --- | --- |
| Datei | `services/finance/main.py` + `Dockerfile`. |
| Inhalt | FastAPI-App-Skelett (Prometheus, Correlation Middleware, `/health`, `/ready`), aber alle Referenzen (`app.core.config`, `app.domains.finance.api`, `app.middleware.*`) existieren in `services/finance` **nicht**. `app/`-Verzeichnis fehlt komplett. |
| Status | Nicht lauffähig. Dockerfile erwartet `requirements.txt` und `app/`-Ordner, die nicht vorhanden sind. |
| Reuse-Potenzial | Nur als Template für Logging/Middleware-Setup; ansonsten vollständiger Neuaufbau nötig. |

## 3. Zentrale Python-Schemas & Contracts

| Pfad | Beschreibung |
| --- | --- |
| `app/api/v1/schemas/finance.py` | Umfangreiche Pydantic-Schemas für Konten, Journal Entries, Reporting, OPs. Kann direkt in künftigen FastAPI-Services verwendet werden. Prüfen auf Konsistenz mit `packages/shared/contracts`. |
| `packages/shared/contracts/src/finance-schemas.ts` | Zod-basierte Contracts (Accounts, JournalEntry, Invoice, Payment, Budget, Reporting, TaxRecord). Grundlage für Frontend/Events; wichtig für Anti-Corruption-Layer. |

## 4. Frontend & API Clients

| Pfad | Beschreibung |
| --- | --- |
| `packages/frontend-web/src/lib/services/finance-service.ts` | Axios-Service mit Endpunkten (`/api/v1/chart-of-accounts`, `/journal-entries`, Posting etc.). Erwartet ein funktionsfähiges Finance-Backend mit REST-API. |
| Weitere UI-Komponenten | (Belegmasken/Views) müssen in Phase 0 noch detailliert inventarisiert werden (separater Task *fibu-code-inventory-frontend*). |

## 5. CI/CD & Observability Assets

| Pfad | Beschreibung |
| --- | --- |
| `.github/workflows/finance-domain-ci.yml` | CI-Pipeline für die Node-Domain (Tests, Build). |
| `monitoring/grafana/dashboards/finance-domain-dashboard.json` | Dashboard für Finance KPIs. |
| `docs/uAT/checklisten/FINANCE.md` etc. | Dokumentation/Checklisten mit FiBu-Bezug. |

## 6. Identifizierte Gaps & Hinweise zur Wiederverwendung

1. **Technologiebruch**: Domänenlogik (Node/TS) vs. Zielarchitektur (Python/FastAPI). Optionen:
   - a) Portieren kritischer Services (`ledger`, `journal`, `period`) nach Python.
   - b) Wrapper/Microservice in Node beibehalten → zusätzliche Betriebskomplexität.
2. **Duplizierte Quellen**: `packages/finance-domain` und `domains/finance` scheinen identisch → Konsolidierung erforderlich, um Inkonsistenzen zu vermeiden.
3. **Fehlende Python-Implementierung**: `services/finance` referenziert nicht existierende Module. Für GoBD-konforme Umsetzung ist ein komplett neuer Service-Stack notwendig (`fibu-core`, `fibu-master-data`, etc.).
4. **APIs & Contracts**: Pydantic- und Zod-Schemas bieten gute Ausgangsbasis für neue Services und Middleware-Mappings. Notwendig: Abgleich mit `docs/specs/fibu_architektur_spezifikation.md` (Kontenrahmen, Periodenmodell, OP-Definitionen).
5. **Tests**: Node-Domain liefert Unit/Integration-Tests; können als Referenz für Business Rules dienen. Für Python-Neuentwicklung sollten äquivalente Tests (pytest) abgeleitet werden.
6. **Observability**: Grafana-Dashboard existiert, aber Metriknamen beziehen sich auf Node-Domain. Beim Neubau neue Prometheus-Metriken definieren oder vorhandene Labels übernehmen.

---

## 7. Nächste Schritte (Input für Phase 0 & 1)

- Konsolidieren, welche Teile von `packages/finance-domain` übernommen/portiert werden (Ledger-Modelle, Eventdefinitionen, Services).
- Entfernen oder archivieren der doppelten `domains/finance`-Struktur, um Missverständnisse zu vermeiden.
- Festlegen, ob `packages/shared/contracts/src/finance-schemas.ts` als „Single Source of Truth“ für Events/API dienen soll und wie Pydantic-Schemas synchron gehalten werden.
- Dokumentieren, welche externen Dependencies (Kafka, OCR, AI) in der neuen Architektur tatsächlich benötigt werden (siehe README Versprechen vs. real implementierte Repos).
- `services/finance` komplett neu aufsetzen (neue Package-Struktur, Settings, DB-Migrations). Stubs sollten entfernt werden, sobald neuer Service existiert.

