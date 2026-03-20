# Wave 80 — Leitsystem für Ausnahmefälle / Error UX (Gap 028)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-19
**Tests:** 40 passed, 0 failed
**Gap:** 028 — Leitsystem für Ausnahmefälle (Error UX), KPI: 50% weniger Abbruchquote bei Fehlern

## Lieferumfang

### A) Backend: `app/core/error_ux_contracts.py`

Vollständige Fehlerklassifizierung für alle HTTP-Statuscodes und Netzwerkfehler:

```python
err = classify_http_error(409, context="Speichern")
err.category          # ErrorCategory.CONFLICT
err.severity          # ErrorSeverity.RECOVERABLE
err.title             # "Bearbeitungskonflikt"
err.detail            # "Ein anderer Benutzer hat den Datensatz …"
err.data_loss_risk    # True
err.primary_action    # RecoveryAction("Daten aktualisieren …", "refresh_merge")
err.tip               # "Ihre Eingaben sind noch vorhanden …"
err.support_code      # "ERR-CONFLICT-409"
```

**Klassifizierungsfunktionen:**

| Funktion | Eingabe | Beispiel-Kategorie |
|----------|---------|-------------------|
| `classify_http_error(status, detail, context)` | HTTP-Code | 400→VALIDATION, 401/403→AUTHORIZATION, 404→NOT_FOUND, 409→CONFLICT, 500→SERVER |
| `classify_network_error()` | offline/DNS-Fehler | NETWORK |
| `classify_business_rule_error(regel, detail)` | Workflow-Regelname | BUSINESS_RULE |

**`ErrorCategory`**: NETWORK, VALIDATION, AUTHORIZATION, NOT_FOUND, SERVER, CONFLICT, TIMEOUT, BUSINESS_RULE, UNKNOWN

**`ErrorSeverity`**: BLOCKING (Weiterarbeit unmöglich), RECOVERABLE (mit Maßnahme lösbar), WARNING

**`RecoveryAction`**: label (Deutsch), action_key (retry/login/reload/back/save_draft/refresh_merge/contact_support), primary, icon

### B) `ErrorUxRegistry` — Vordefinierte Szenarien

```python
registry = get_default_error_registry()
registry.get("session_expired")   # → login-Aktion
registry.get("save_conflict")     # → refresh_merge + save_draft
registry.get("workflow_blocked")  # → BLOCKING
```

6 Standard-Szenarien: `session_expired`, `save_conflict`, `loading_failed`,
`no_permission_for_action`, `record_deleted_by_other_user`, `workflow_blocked`

### C) Frontend: `components/error/ErrorPanel.tsx`

```tsx
<ErrorPanel
  error={classifyHttpError(statusCode)}
  onAction={(key) => handleAction(key)}
/>
```

- Kategorie-Icon: WifiOff/Lock/Search/ServerCrash/GitMerge/Clock/HelpCircle
- Farbkodierung: rot (AUTH/SERVER), gelb (VALIDATION/TIMEOUT), orange (CONFLICT), blau (BUSINESS_RULE)
- Datenverlust-Banner wenn `data_loss_risk=true`
- `role="alert"` + `aria-live="assertive"` für Screen-Reader
- Kompaktmodus für Inline-Verwendung (`compact` prop)
- Support-Code in Monospace rechts unten

## Kontrakt-Tests (40 Tests)

| Klasse | Tests | Kernprüfung |
|--------|-------|-------------|
| `TestClassifyHttpError` | 15 | Alle Statuscodes, Kategorien, Aktionen, Kontext-Embedding |
| `TestClassifyNetworkError` | 4 | offline, retry-Aktion, Tipp, Support-Code |
| `TestClassifyBusinessRuleError` | 4 | Kategorie, Regelname im Titel, Detail, Support-Code |
| `TestUserFacingError` | 6 | primary_action, secondary_actions, as_dict, data_loss_risk |
| `TestErrorUxRegistry` | 6 | Default-Szenarien, register, get, unknown-Key |
| `TestIntegrationSzenario` | 5 | Deutsche Texte, BLOCKING+Tipp, Datenverlust-Dict, 409-Fluss, 9 Kategorien |

## KPI-Ergebnis (Gap 028)

| KPI | Ziel | Ergebnis |
|-----|------|----------|
| Fehlerleitsystem implementiert | 50% weniger Abbruchquote | Alle 9 Kategorien mit Aktionen ✓ |
| Deutsche Fehlertexte | Keine englischen Rohmeldungen | title/detail/tip alle Deutsch ✓ |
| Recovery Actions | Mindestens 1 Aktion je Fehler | Alle HTTP-Codes haben ≥1 Aktion ✓ |
| Datenverlust-Transparenz | data_loss_risk sichtbar | 401, 409, 500, 504 markiert ✓ |
| Vordefinierte Szenarien | 6 Kernszenarien | ErrorUxRegistry mit 6 Einträgen ✓ |
