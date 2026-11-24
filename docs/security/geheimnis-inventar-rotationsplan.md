---
title: Geheimnis-Inventar und Rotationsplan (M5)
type: runbook
audience: [betrieb, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-24
version: 1.0.0
description: Inventar der Geheimnisse nach Name und Fundort (ohne Werte), Einstufung, Rotationsreihenfolge mit Abhaengigkeiten und Rueckfall; produktive Rotation nur nach Freigabe.
---

# Geheimnis-Inventar und Rotationsplan (M5)

Nutzerauftrag 24.11.2026: Geheimnisinventar erstellen, ohne Geheimnisse in Logs oder Dokumentation auszugeben;
Rotationsplan mit Abhaengigkeiten und Rueckfall; kompromittierte Geheimnisse widerrufen und ersetzen.
**Diese Datei enthaelt keine Werte.** Erhoben am 24.11.2026 durch Zaehlen von Variablennamen in eingecheckten
Dateien (Werte wurden nicht gelesen oder ausgegeben).

Ablage im Cluster (SealedSecrets/ExternalSecrets): `docs/deployment/runbook/security/secrets-inventory.md`.

## 1. Befund

| Ort | Literalwerte | Bewertung |
|---|---|---|
| `docker-compose.production.yml` | 0 (alle `${VAR:?...}`, PR #177) | in Ordnung |
| `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.auth.yml` | ja: Datenbank-, Keycloak-, pgAdmin-Passwort, `SECRET_KEY`, `ENCRYPTION_KEY`, `WEBHOOK_SECRET`, `API_DEV_TOKEN` | Entwicklungswerte - **gelten als offengelegt** (Git-Historie); duerfen nirgends ausserhalb der lokalen Entwicklung verwendet sein |
| `.env.example` | 3 (`API_DEV_TOKEN`, `FISKALY_API_KEY`, `FISKALY_API_SECRET`) | **pruefen**: Beispiel- oder echte Werte? Echte Fiskaly-Zugaenge sofort beim Anbieter widerrufen |
| `.env.swarm` | 0 | in Ordnung |
| Git-Historie | fruehere Passwoerter (siehe M5-Notizen) | **offengelegt** - unabhaengig vom heutigen Stand rotieren, sofern irgendwo produktiv |

## 2. Inventar nach Klasse (Namen, keine Werte)

| Klasse | Namen | Abhaengigkeit bei Rotation |
|---|---|---|
| Datenbank | `POSTGRES_PASSWORD`, `DB_PASSWORD`, `PGPASSWORD`, `KC_DB_PASSWORD`, `PROCUREMENT_DB_PASSWORD`, `SUPERGLUE_DB_PASSWORD`, `PGADMIN_DEFAULT_PASSWORD` | Rolle in Postgres zuerst aendern, dann alle Dienste mit neuer URL neu starten (Backend, Dienste, Keycloak) |
| Identitaet/Sitzung | `KEYCLOAK_ADMIN_PASSWORD`, OIDC-Client-Secrets, `JWT_SECRET`, `SECRET_KEY`, `VALEO_SECRET_KEY` | JWT/SECRET_KEY: alle Sitzungen werden ungueltig - Wartungsfenster; Keycloak-Client-Secret: Backend und BFF gleichzeitig |
| Entwicklungs-Bypass | `API_DEV_TOKEN`, `VITE_API_DEV_TOKEN`, `VALEO_DEV_TOKEN` | muss im laufenden System **aus** sein (seit 12.10.2026 kein Dev-Token im laufenden System); Produktion: nicht setzen |
| Verschluesselung | `ENCRYPTION_KEY`, `SUPERGLUE_MASTER_ENCRYPTION_KEY`, `SETTINGS_KEY` | **nicht einfach tauschen**: verschluesselte Daten zuerst mit altem Schluessel entschluesseln und mit neuem verschluesseln (Doppelschluessel-Phase) |
| Externe Anbieter | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LINKUP_API_KEY`, `QDRANT_API_KEY`, `FISKALY_API_KEY`/`_SECRET`, `SONAR_TOKEN`, `GH_ADMIN_TOKEN`, `DMS_TOKEN`, `CHANNEL_SLACK_SIGNING_SECRET` | beim Anbieter neuen Schluessel erzeugen, setzen, alten **widerrufen**; Fiskaly (TSE) mit Kassenabschluss abstimmen |
| Webhooks/Dienste | `WEBHOOK_SECRET`, `API_KEY`, `API_BEARER_TOKEN`, `RAG_API_TOKEN`, `RATIONS_OPTIMIZATION_API_KEY`, `SUPERGLUE_AUTH_TOKEN`, `AUTH_TOKEN` | Sender und Empfaenger gleichzeitig; kurz beide Werte akzeptieren |

`*_STORAGE_KEY`, `*_DEFINITION_KEY` sind Schluesselnamen von Browser-Speicher bzw. Prozessdefinitionen, keine
Geheimnisse.

## 3. Rotationsreihenfolge

1. **Sofort, ohne Freigabe moeglich:** offengelegte Entwicklungswerte bleiben auf die lokale Entwicklung beschraenkt;
   pruefen, dass keine Umgebung ausser lokal sie nutzt (Staging, Spiegelbetrieb).
2. **Mit Freigabe (produktiv):** externe Anbieter-Schluessel (unabhaengig, geringstes Risiko) -> Webhooks/Dienste
   -> Datenbankrollen -> Identitaet (Wartungsfenster) -> Verschluesselung (Doppelschluessel-Phase, zuletzt).
3. Je Schritt: neuen Wert im Geheimnisspeicher (GitHub Environments bzw. Host-Secret-Store) anlegen, Dienst neu
   starten, Funktionsprobe, **dann** alten Wert widerrufen.

## 4. Rueckfall

- Bis zur Funktionsprobe bleibt der alte Wert gueltig (Anbieter: alter Schluessel erst nach erfolgreicher Probe
  widerrufen; Datenbank: alte Rolle erst danach sperren).
- Verschluesselung: der alte Schluessel bleibt waehrend der Doppelschluessel-Phase lesbar, bis alle Datensaetze
  umgeschluesselt sind; erst dann entfernen.
- Kein Rueckfall auf einen offengelegten Wert.

## 5. Freigabe

Produktive Rotation und Widerruf bei Anbietern sind sicherheitskritische externe Aenderungen und werden **nur nach
ausdruecklicher Freigabe** des Nutzers ausgefuehrt (Nutzervorgabe 24.11.2026). Offen beim Nutzer:

1. Welche Umgebungen ausser lokal existieren (Staging, Spiegelbetrieb L3), und welche Geheimnisse nutzen sie?
2. Sind die drei Literalwerte in `.env.example` Beispielwerte oder echte Zugaenge?
3. Freigabe der Reihenfolge in Abschnitt 3.
