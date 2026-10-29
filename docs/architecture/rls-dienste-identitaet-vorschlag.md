---
title: Dienste unter services/* — vertrauenswürdige Identität und Mandantenbindung (Vorschlag)
type: architecture
audience: [agent, entwickler]
owner: Claude Code
status: vorschlag
last_reviewed: 2026-10-27
version: 0.1.0
description: Architekturvorschlag, wie die Dienste unter services/* den Mandanten aus einem geprüften Token statt aus Kopfzeile, Body oder 'default' beziehen, bevor ihre Tabellen RLS bekommen.
---

# Dienste unter `services/*` — Identität und Mandantenbindung

**Status: Vorschlag zur Entscheidung.** Bis zur Entscheidung bekommt keine Tabelle mit
Ursache `dienst` (20 Tabellen, `docs/admin/rls-exceptions.json`) eine Policy, und kein
Dienst darf eine RLS-Tabelle lesen (Vertrag aus P6).

## 1. Befund

| Punkt | Stand |
|---|---|
| Authentisierung | Die CRM-Dienste (`crm-core`, `-sales`, `-service`, `-workflow`, `-analytics`, `-communication`, `-ai`, `-multichannel`) und `inventory` prüfen **kein** Bearer-Token. Teilprüfungen gibt es nur in `crm-gdpr`, `crm-marketing`, `crm-security`, `dms-adapter` und `compliance`. |
| Mandant | Er stammt aus der Kopfzeile `X-Tenant-ID` (`finance`, `inventory`, `dms-adapter`, `crm-gdpr`) oder ist fest `settings.DEFAULT_TENANT_ID`. `crm-core` filtert z. B. jede Kunden- und Lead-Abfrage auf den Standardmandanten. |
| Erreichbarkeit | Compose veröffentlicht die Ports (`5400`, `5600`–`5900` …) auf dem Host. Wer den Port erreicht, wählt den Mandanten frei. |
| Datenbank | Alle Dienste verbinden als `valeo_app` (#51). Eigene Engine, kein `app.tenant_id` je Transaktion. |
| Gemeinsame Tabellen | `domain_crm.activities`/`farm_profiles`, `public.crm_*`, `public.inventory_*` (Eigentum des inventory-Dienstes, #53), `domain_erp.chart_of_accounts` (finance). |

Damit ist der Mandant in den Diensten **nicht** vertrauenswürdig. Eine RLS-Policy würde nur
die Kopfzeile bestätigen, die der Aufrufer ohnehin frei wählt. Deshalb gibt es keine
RLS-Freigabe auf Basis von Kopfzeilen, Body-Feldern oder `default`.

## 2. Vorschlag

**A. Dieselbe Identität wie das Backend (empfohlen).** Jeder Dienst prüft das OIDC-Bearer-Token
selbst: Signatur über JWKS, `iss`, `aud`, `exp`. Den Mandanten bezieht er mit derselben
Regel wie das Backend (`app/core/tenant_binding.checked_tenant`). Kopfzeilen und
Body-Selektoren dürfen den Token-Mandanten nur bestätigen, nie ersetzen (`bind_headers`,
`check_body_selectors`).

- Gemeinsamer Code: ein kleines Python-Paket, z. B. `packages/py-tenant-binding`, oder eine
  versionierte Kopie mit Gleichlauftest gegen `app/core/tenant_binding.py`. Kein Import
  des Backends in die Dienste.
- Je Request wird der Mandant in eine ContextVar gelegt. Auf der Dienst-Engine setzt jede
  Transaktion `set_config('app.tenant_id', …, true)`, das Muster aus
  `app/core/rls_session.py`. Für asyncpg geschieht das im `begin`-Ereignis der Sitzung.
- Ohne geprüften Mandanten antwortet der Dienst mit 401/403. Es gibt keinen Rückfall.
- Je Dienst eine eigene Rolle (`valeo_svc_<dienst>`, ohne BYPASSRLS) statt `valeo_app`. So
  bleiben Zugriffe zuordenbar, und Rechte lassen sich je Tabelle vergeben.

**B. Dienst-zu-Dienst und Hintergrundarbeit.** Die Weitergabe des Nutzertokens
(on-behalf-of) ist der Normalfall. Jobs ohne Nutzer holen ein Client-Credentials-Token mit
ausdrücklichem Mandanten-Claim. Ein Job ohne Mandanten-Claim läuft nur in
`cross_tenant_scope` über `valeo_system`, mit Grund, analog `@cross_tenant_job` (P6).

**C. Verworfen:** eine signierte interne Kopfzeile vom Backend (HMAC). Sie verschiebt das
Vertrauen auf ein gemeinsames Geheimnis, deckt direkte Aufrufe nicht ab und braucht eine
zweite Prüfregel neben OIDC.

## 3. Reihenfolge je Dienst

1. Token-Prüfung als Middleware, Ports nur im Compose-Netz (nicht auf dem Host).
2. `DEFAULT_TENANT_ID`/`'default'` und Kopfzeilen-Mandanten entfernen. Vertragstest je
   Dienst nach dem Muster von `tests/test_rls_p1_tenant_context.py`.
3. `app.tenant_id` je Transaktion und eigene Rolle.
4. Dann erst die Policies der Dienst-Tabellen in einem Domain-Slice (getrennte Form, siehe
   `rls-domaenen-entscheidungsmatrix.md` §3).

Reihenfolge der Dienste: `inventory` zuerst (führt `public.inventory_*` allein), danach
`crm-core` (fester Standardmandant, größte Wirkung), dann `finance` und die übrigen
CRM-Dienste. `ai`/`ki-usability` lesen Backend-Tabellen nur über Wortfunde der Heuristik.
Das ist vor der Einordnung zu prüfen.

## 4. Offene Entscheidungen (Nutzer/Codex)

- Option A bestätigen, oder die Dienste zurückbauen und ins Backend ziehen. Die
  strategische Leitlinie „keine Microservice-Zerlegung“ spricht für Letzteres bei Diensten
  ohne eigenständige Last.
- Ob Dienstrollen je Dienst gewünscht sind. Das ändert `scripts/provision_db_roles.py`
  (P6, Codex-Besitz nach Integration).
