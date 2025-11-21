# ADR-002: FiBu-Frontend – API-Layer & Middleware-Strategie

## Status
Accepted – 2025-11-14

## Kontext
- Es existiert ein umfangreicher React-Client mit Mask Builder, React Query und `financeService` (Axios) gegen `/api/v1/*` (Finance-Routen).
- Die neuen FiBu-Microservices werden in mehrere Bounded Contexts zerlegt (`fibu-core`, `fibu-master-data`, `fibu-op`, `fibu-ar`, …) und sollten größtenteils Event-Driven / service-spezifische APIs bereitstellen.
- Um andere Domains (Workflow, Inventory, Sales) nicht massiv umzubauen, ist ein `fibu-gateway` (Anti-Corruption Layer) geplant.

## Entscheidung
1. **Der bestehende monolithische Axios-Client `financeService` wird ersetzt** durch ein modulares API-Layer:
   - je Microservice ein isoliertes Client-Modul (z. B. `services/api/fibuCoreClient.ts`, `fibuOpClient.ts`).
   - zentrale Query-Key-Konvention bleibt erhalten (`queryKeys.finance.*`), aber wird auf neue Clients gemappt.
2. **Der Frontend-Datenfluss wird konsequent über das Middleware-/Gateway-Schema geführt**:
   - UI konsumiert nur definierte Contracts des Gateways (REST/GraphQL).
   - Direkter Zugriff auf interne Microservice-Endpoints wird vermieden, um spätere Schnittstellenänderungen isolieren zu können.
3. **Mask Builder & Form-Komponenten bleiben erhalten**, erhalten jedoch eine dünne Abstraktion für Datensourcen (Fetch-/Submit-Adapter), um neue Services leichter anzubinden.
4. **Frontendspezifische Dokumentation** (z. B. in `docs/specs/fibu_frontend_inventory.md`) wird kontinuierlich aktualisiert, sobald neue Services live gehen.

## Konsequenzen
- **Pro**:
  - Stabilere Contracts zwischen Frontend und Middleware, weniger Brüche bei Service-Neuentwicklungen.
  - Sauberer Mandanten-/Rollen-Support (Gateway kann Kontext injizieren).
  - Mask Builder kann unabhängig weiterentwickelt werden, da Datenzugriffe klar gekapselt sind.
- **Contra**:
  - Kurzfristiger Mehraufwand, weil bestehende Axios-Aufrufe umgebaut werden müssen.
  - Gateway wird kritischer Pfad (muss hochverfügbar und versioniert betrieben werden).
- **Ausblick**:
  - Wenn Quell-Domains langfristig native FiBu-Events erzeugen, kann die Middleware verschlankt oder abgeschaltet werden.
  - ADR referenziert Phase‑1/8 Aufgaben (middleware-design, middleware-guardrails).

