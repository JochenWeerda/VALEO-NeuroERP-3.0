# Auth- und Tenant-Konzept (VALEO NeuroERP)

**Zweck:** Einheitliche Nutzung von Mandant (Tenant) und Benutzer (User) im Frontend und Backend. Alle Masken und APIs sollen Tenant/User aus diesem Konzept beziehen, keine fest codierten IDs.

**Verbindlicher API-Vertrag (Tenant, Subjekt, Fehlercodes):** [ADR: Auth- und Tenant-Kontext](architecture/adr-2026-04-24-auth-tenant-context.md) (**M-01**). Diese Seite ergänzt die ADR um Frontend- und Dependency-Konventionen.

---

## 1. Backend

### 1.1 Tenant

- **Quelle:** HTTP-Header `X-Tenant-ID` (vom Frontend bei jedem Request gesendet).
- **Dependency:** `get_tenant_id(x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"))` in `app/core/tenant.py`.
- **Fallback:** `get_current_tenant_id()` (z. B. aus Middleware) oder `settings.DEFAULT_TENANT_ID` — nur wo ausdrücklich für **Dev/Staging** konfiguriert. In **Produktion** kein stiller Standard-Mandant auf **schreibenden** Pfaden; bei fehlendem Tenant gilt die ADR (**400** / Gateway, keine stillen `system`-Audits außerhalb definierter Ausnahmen).
- **Verwendung:** In Endpoints `tenant_id: str = Depends(get_tenant_id)`; alle tenant-sensiblen Abfragen filtern nach dieser ID.

### 1.2 User (optional im Backend)

- **Quelle:** JWT-Bearer-Token; Subjekt und Claims (sub, email, name, roles) können bei Bedarf aus dem Token ausgelesen werden.
- **Hinweis:** Aktuell setzt das Backend User-Infos oft nur in Audit-Logs (z. B. `user_id`/`user_email` aus Request-Body). Eine zentrale `get_current_user()`-Dependency kann ergänzt werden, wenn Endpoints explizit den aktuellen Benutzer brauchen.

---

## 2. Frontend

### 2.1 Tenant

- **Hook:** `useTenant()` aus `@/hooks/useTenant`.
- **Rückgabe:** `{ tenantId: string, setTenantId: (id: string) => void }`.
- **Quelle:** `localStorage.getItem('tenant_id')` bzw. `sessionStorage.getItem('tenant_id')`, sonst `VITE_TENANT_ID` oder Fallback-UUID (typisch **lokal/Dev**; produktive Builds müssen einen gültigen Mandanten setzen — siehe ADR M-01).
- **API-Client:** `apiClient` (axios) setzt in jedem Request automatisch `X-Tenant-ID` aus derselben Quelle (localStorage/sessionStorage/Default). Seiten, die nur API aufrufen, brauchen `useTenant()` nur, wenn sie `tenant_id` in Request-Body oder Query-Parametern mitschicken müssen.

### 2.2 User (Auth)

- **Hook:** `useAuth()` aus `@/hooks/useAuth`.
- **Rückgabe:** `{ user, loading, isAuthenticated, login, logout, handleCallback, hasScope, hasRole }`.
- **User-Typ:** `User { sub, email, name, scopes, roles, exp }` (aus JWT oder Dev-Mock).
- **Verwendung:** `user?.sub` (User-ID), `user?.email`, `user?.name` für Audit, Anzeige, oder Stammdaten (z. B. `created_by`, `user_email`).

### 2.3 Empfohlene Verwendung in Masken

- **Neue/ Bearbeitung Stammdaten:** Beim Speichern `tenant_id` und ggf. `user_id`/`user_email` aus Kontext setzen:
  - `const { tenantId } = useTenant()`
  - `const { user } = useAuth()`
  - Payload: `tenant_id: tenantId`, `user_id: user?.sub ?? ''`, `user_email: user?.email ?? ''`
- **API-Aufrufe mit tenant_id in URL/Query:** `tenant_id` aus `useTenant()` verwenden, z. B. `?tenant_id=${tenantId}`.
- **Keine festen Werte:** Weder `'00000000-0000-0000-0000-000000000001'` noch `'dev-user'`/`'user@example.com'` in Masken-Logik; stattdessen immer aus Hooks.

---

## 3. Kunden-/Debitoren-Suche

- **Backend:** `GET /api/v1/crm/customers?search=...&limit=...` (Suche in Anzeigename, Kundennummer, E-Mail). Alternativ Debitoren-API, falls Rechnungen an Debitoren gebunden sind.
- **Frontend:** Suchfeld mit Debounce; bei Eingabe Abfrage an Customers-API; Auswahl setzt `customerId` und Anzeigename. Einheitliches Pattern für alle Masken, die „Kunde“ oder „Debitor“ auswählen (z. B. Rechnungserfassung, Lieferschein).

---

## 4. TSE (Technische Sicherheitseinrichtung) und Offline (POS)

### 4.1 TSE

- **Zweck:** GoBD-konforme Aufzeichnung von Kassenvorgängen (Beleg, Signatur, Zeitstempel).
- **Backend:** Eigene TSE-Integration (z. B. Fiskaly, Swissbit); Endpoints für Signatur/Registrierung von Transaktionen.
- **Frontend (POS):** Beim Abschluss einer Transaktion `saveTSETransaction(...)` aufrufen (oder äquivalenten API-Call), bevor die Buchung als abgeschlossen gilt. Aktuell in `pos/terminal.tsx` als TODO; Implementierung hängt von gewählter TSE-API ab.
- **Konzept:** Keine „stille“ Buchung ohne TSE-Signatur in produktivem Betrieb; Dev/Test mit TSE-Stub oder Flag „TSE umgehen“ möglich.

### 4.2 Offline-Queue (POS)

- **Zweck:** Verkäufe auch bei Netzausfall erfassen und später synchronisieren.
- **Konzept:** Lokale Queue (IndexedDB/Storage); beim Wiedererreichen des Netzes Upload an Backend; Backend verarbeitet nacheinander, idempotent (z. B. über `client_request_id`). In `pos/terminal.tsx` aktuell als TODO; Implementierung erfordert definiertes Offline-API (z. B. `POST /api/v1/pos/offline-sync` mit Liste von Transaktionen).

---

## 5. erp-domain (Node / Express)

Für **`packages/erp-domain`** gilt derselbe Vertrag wie in der ADR (M-01), technisch gebündelt in:

| Bestandteil | Pfad |
|-------------|------|
| Tenant / Actor / Fehlerbehandlung | `packages/erp-domain/src/presentation/utils/request-context.ts` (`resolveTenantId`, `resolveActorId`, `respondControllerError`, …) |
| Finanz-Stammdaten-Router | `packages/erp-domain/src/presentation/controllers/finanz*.controller.ts` (nutzen `resolveTenantId` und mandantenbezogene Services) |
| Listen-/Paging-Hilfen Finanz | `packages/erp-domain/src/presentation/utils/finanz-http.ts` |
| Datenbank: Mandantenspalte Finanz | Migrationen `migrations/sql/erp/001_finance_core.sql`, `003_finanz_tenant_id.sql` |
| Lokale Qualität & DB (Repo-Wurzel) | `pnpm test:erp-domain` (Jest `packages/erp-domain`), `pnpm migrate:erp-finanz` (beide Finanz-SQLs); Details [erp-finanz-multitenancy.md](erp-finanz-multitenancy.md) |

**Ausführliche Beschreibung** (Schema `finanz`, `_legacy`, SQL-Runner, Purchase-Order-Tenant): [**ERP: Finanz & Mandant (Multitenancy)**](erp-finanz-multitenancy.md).

---

## 6. Zusammenfassung

| Thema           | Backend                    | Frontend                          |
|-----------------|----------------------------|------------------------------------|
| Tenant          | `get_tenant_id()` (Header) | `useTenant().tenantId`             |
| User            | Optional aus JWT           | `useAuth().user` (sub, email, name)|
| Kunden-Suche    | `GET /crm/customers?search=` | Suchfeld + API, Auswahl → ID/Name |
| TSE             | TSE-Service anbinden       | Nach Buchung TSE-Signatur anfordern|
| Offline (POS)   | Sync-Endpoint für Queue    | Lokale Queue + Sync bei Online     |

**Regel:** Keine hardcodierten Tenant- oder User-IDs in Masken; immer `useTenant()` und `useAuth()` nutzen. Kundenauswahl über echte Suche (Customers/Debitoren-API).
