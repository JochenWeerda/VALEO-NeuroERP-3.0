# Mandant der Anfrage ist der Mandant der Anmeldung

Stand: 2026-10-12 · Slice `MANDANT-TOKEN-BINDUNG-20261012` · Auftrag: „Anmeldedienst den Mandanten im
Token mitgeben lassen" · Hinweis von Codex (`KONTENPLAN-VERIFIED-SHARED-POLICY-20261012`, erste Hälfte)

## Befund

Die Middleware `tenant_enforcement.py` prüfte den Kopf `X-Tenant-ID` nur auf seine Form. Wer
angemeldet war, konnte jeden Mandanten hineinschreiben; 326 Dateien unter `app/` beziehen den
Mandanten von dort. Die Rollen der Finanzwege und der Mandantenfilter im Kontenplan schützten damit
nur vor dem Versehen, nicht vor dem Vorsatz.

## Was der Anmeldedienst liefert

- **Hauptrealm** (`config/keycloak/realm-export.json`, Entwicklung und Produktion): Der Mapper
  `tenant_id` (Benutzerattribut → Claim im Access-Token) stand schon im Client-Scope `roles`, den
  beide Clients standardmäßig tragen. Die drei mitgelieferten Benutzer haben das Attribut.
- **Staging-Realm** (`realm-staging.json`): hatte keinen Mapper – ergänzt, am Client. Die vier
  Testbenutzer haben das Attribut `tenant_id` noch **nicht**.

## Entscheidung

Gebunden wird an **einer** Stelle: `require_bearer_token` in `app/core/security.py`. Die Abhängigkeit
hängt am Hauptrouter und damit an jedem API-Weg.

| Token | Anfrage | Ergebnis |
|---|---|---|
| nennt genau einen Mandanten (`tenant_id` oder `mandanten_id`, Text oder einelementige Liste) | derselbe Mandant | läuft |
| nennt genau einen Mandanten | anderer Mandant im Kopf | 403 „Der Mandant der Anfrage (X-Tenant-ID) ist nicht der Mandant der Anmeldung." |
| nennt mehrere Mandanten | gleich welcher | 403 |
| nennt keinen | gleich welcher | läuft – bis `OIDC_TENANT_CLAIM_REQUIRED=true`, dann 403 |
| Dev-Token | gleich welcher | läuft (nur Entwicklung; in Produktion verbietet der Startwächter den Dev-Token) |

Das Token als Query-Parameter (SSE, WebSocket) wird genauso gebunden.

**Warum der Schalter:** Ein fehlender Claim sofort als Fehler hätte jeden ausgesperrt, dessen
Benutzer das Attribut noch nicht hat (Staging heute, jede gewachsene Installation). So gilt ab sofort:
*Wer einen Mandanten im Token hat, kommt in keinen anderen.* Die Lücke für Tokens ohne Mandant
schließt der Schalter, sobald die Benutzer gepflegt sind.

**Oberfläche:** `lib/api-client.ts` nimmt den Mandanten aus dem Token, sobald es einen nennt
(`lib/tenant-from-token.ts`), sonst wie bisher aus dem Browser-Speicher. Ein alter Wert im Speicher
ließe sonst jede Anfrage mit 403 enden.

## Geänderte Dateien

- `app/core/security.py` – `_bind_tenant`, an beiden Stellen nach der Signaturprüfung
- `app/core/config.py`, `.env.example` – `OIDC_TENANT_CLAIM_REQUIRED` (aus)
- `config/keycloak/realm-staging.json` – Mapper `tenant_id`
- `packages/frontend-web/src/lib/tenant-from-token.ts` (neu), `lib/api-client.ts`
- `tests/test_mandant_token_bindung.py`, `src/__tests__/lib/tenant-from-token.test.ts` (neu)

Nicht angefasst: `app/auth/tenant.py` (`get_verified_tenant_id`, Codex) – die strengere Prüfung
dort (Mandant Pflicht) gilt an ihren Wegen weiter.

## Nachweis

| Prüfung | Ergebnis |
|---|---|
| `tests/test_mandant_token_bindung.py` – echte Mandanten-Middleware davor, nur die Signaturprüfung ersetzt; dazu: beide Realm-Dateien geben `tenant_id` ins Access-Token | 16 bestanden |
| 17 Testdateien rund um Token, Middleware und Realm | 359 bestanden, 2 übersprungen |
| `tenant-from-token.test.ts` | 4 bestanden |
| `tsc --noEmit`, ESLint | ohne Fehler |
| Laufendes Entwicklungs-Backend: Dev-Token, eigener Mandant | 200 |
| Laufendes Entwicklungs-Backend: unsigniertes Token mit fremdem Mandanten | abgelehnt (503, kein Anmeldedienst in der Entwicklung erreichbar) |

**Nicht geprüft:** ein echtes, von Keycloak signiertes Token gegen das laufende Backend. In der
Entwicklungsumgebung läuft kein Keycloak; die Bindung selbst ist mit ersetzter Signaturprüfung
belegt, der Mapper nur über die Realm-Datei.

## Vor einer Inbetriebnahme

1. Jedem Benutzer im Anmeldedienst das Attribut `tenant_id` geben (ein Wert).
2. Prüfen, dass ein frisch ausgestelltes Access-Token den Claim `tenant_id` trägt.
3. Dann `OIDC_TENANT_CLAIM_REQUIRED=true` setzen.
4. Ein laufender Realm übernimmt eine geänderte Realm-Datei **nicht** von selbst (Import nur beim
   ersten Start): Den Mapper im Staging-Keycloak von Hand anlegen oder den Realm neu importieren.

## Offen

- **Bis Schritt 3 bleibt die Lücke für Tokens ohne Mandant.** Das ist der Stand jeder Installation,
  deren Benutzer das Attribut nicht haben.
- **Der mitgelieferte Benutzer `admin` hat den Mandanten `system`.** Er ist damit an `system`
  gebunden und kommt nicht mehr in den Mandanten eines Hauses. Wer ein Haus administriert, braucht
  dort den Mandanten des Hauses.
- **Mehrere Häuser je Benutzer** gibt es nicht: Ein Token mit mehreren Mandanten wird abgelehnt.
- **`lib/mcp.ts`** setzt `X-Tenant-ID` weiter aus dem Speicher (BFF-Weg, nicht geprüft).
- **Wege außerhalb des Hauptrouters** (falls es welche unter `/api` gibt) hängen nicht an
  `require_bearer_token`; nicht vermessen.
