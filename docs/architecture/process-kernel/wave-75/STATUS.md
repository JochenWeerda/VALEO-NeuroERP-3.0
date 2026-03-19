# Wave 75 — Security Hardening: HTTP Security Headers + RBAC Fine-Grained Contracts

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-19
**Tests:** 49 passed, 0 failed
**Gap:** 049 — Security-Hardening (OIDC, RBAC fein, Secrets, Audit)

## Lieferumfang

### A) Security Headers Middleware (`app/middleware/security_headers.py`)
Neue Starlette-Middleware, die allen HTTP-Antworten des Backends Security-Header hinzufügt:

| Header | Wert | Zweck |
|--------|------|-------|
| `X-Content-Type-Options` | `nosniff` | Verhindert MIME-Sniffing (OWASP A05) |
| `X-Frame-Options` | `DENY` | Clickjacking-Schutz (OWASP A05) |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Referrer-Leakage minimieren |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=(), payment=()` | Browser-APIs deaktivieren |
| `X-XSS-Protection` | `0` | Legacy-Filter deaktiviert (CSP übernimmt) |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | HTTPS erzwingen (nur Produktion) |
| `Content-Security-Policy` | Modus-abhängig | Ressourcen-Quellen einschränken |

- Debug-Modus: HSTS deaktiviert, CSP erlaubt `unsafe-eval` für Vite HMR
- Produktionsmodus: HSTS aktiv, CSP ohne `unsafe-eval`, `frame-ancestors 'none'`, `form-action 'self'`
- Eigene Endpoint-Header werden **nicht überschrieben**
- Hilfsfunktion `build_security_headers(is_debug)` für Tests und Dokumentation

### B) Produktions-Startup-Guard (`main.py`)
- SC-AUTH-002: Wenn `APP_ENV == "production"` und `API_DEV_TOKEN` gesetzt ist, wird beim Startup ein `RuntimeError` ausgelöst
- Verhindert, dass Dev-Tokens in Produktionsumgebungen aktiv sind

### C) RBAC Fein-granular (Kontrakt-Tests)
- `sachbearbeiter` → darf **nicht** `ZAHLUNGSLAUF_STARTEN` oder `SETTLEMENT_FREIGEBEN`
- `buchhaltung` → darf `SETTLEMENT_FREIGEBEN`, `ZAHLUNGSLAUF_STARTEN`, **nicht** `KONTRAKT_STORNIEREN`
- `leiter` → hat breite Rechte inkl. `AGENT_APPROVAL_GEBEN`
- `admin` → alle Permissions
- `agent_system` → **nicht** `SETTLEMENT_FREIGEBEN` (Human-Gate)
- Unbekannte Rollen → keine Permissions

### D) Secret-Klassifikations-Registry
- `password`, `api_key`, `access_token` → `STRENG_VERTRAULICH`, `loggen_erlaubt=False`
- `iban`, `steuernummer`, `kontonummer` → `VERTRAULICH`, `loggen_erlaubt=False`
- `tenant_id`, `email`, `user_id` → `INTERN`, `loggen_erlaubt=True`

### E) Security-Posture-Evaluation
- Keine offenen kritischen Findings → `gesamtbewertung = "GUT"`
- Kritisches Finding → `gesamtbewertung = "KRITISCH"`
- Geschlossene Findings (`status_offen=False`) werden nicht gezählt

## Test-Abdeckung (49 Tests)

- `TestStaticSecurityHeaders` (8): Alle Pflicht-Header in jeder Antwort
- `TestSecurityHeadersModes` (8): HSTS/CSP Debug vs. Produktion
- `TestRBACFineGrained` (15): Rollen-Permission-Matrix
- `TestSecretKlassifikation` (8): Klassifikationsregeln
- `TestSecurityPosture` (6): Gesamtbewertung
- `TestDevTokenProductionGuard` (5): Startup-Guard-Kontrakt

## OWASP-Referenzen

- A01:2021 — Broken Access Control (RBAC, Tenant-Isolation)
- A02:2021 — Cryptographic Failures (IBAN-Verschlüsselung, Secret-Klassifikation)
- A05:2021 — Security Misconfiguration (Security Headers, Dev-Token-Guard)
- A07:2021 — Identification & Authentication Failures (OIDC, Bearer-Token)
- A09:2021 — Security Logging & Monitoring Failures (Audit-Trail)
