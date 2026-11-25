---
title: Umgebungen und Agentenrechte (M5)
type: reference
audience: [betrieb, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-25
version: 1.0.0
description: Zielmodell LOCAL/CI/STAGING/PRODUCTION, tatsaechlicher Bestand im Repository, Agentenmatrix je Umgebung und der Schalter VALEO_UMGEBUNG.
---

# Umgebungen und Agentenrechte (M5)

Nutzerentscheid 25.11.2026. Geheimnisse: `docs/security/geheimnis-inventar-rotationsplan.md`.

## 1. Bestand (Stand 25.11.2026, aus dem Repository ermittelt)

| Umgebung | Artefakte | Tatsaechlich in Betrieb |
|---|---|---|
| LOCAL | `docker-compose.yml`, `docker-compose.dev.yml`, Dev-Datenbank `valeo_neuro_erp` | **ja** |
| CI/TEST | GitHub Actions (`ci.yml`, `quality-gate.yml`, `release-gates.yml` u. a.), `docker-compose.test.yml`, Pruefstand `valeo_probe` | **ja** |
| STAGING | `docker-compose.staging.yml`, `docker-compose.staging-infra.yml`, Workflow `deploy-staging.yml` (Push auf `develop`, baut Images) | **nein** - kein Zielhost belegt; die letzten Laeufe scheiterten |
| PRODUCTION | `docker-compose.production.yml` (Pflichtgeheimnisse, PR #177), Job in `ci.yml` nur bei `vars.ENABLE_DEPLOY == 'true'`, GitHub-Environment `production` | **nein** - `ENABLE_DEPLOY` nicht gesetzt, keine Instanz bekannt |

Nutzerangabe: Ausser lokal sind keine Umgebungen bekannt. STAGING ist Voraussetzung fuer den Spiegelbetrieb (M6).

## 2. Schalter `VALEO_UMGEBUNG`

`app/core/umgebung.py`: `local`, `ci`, `staging`, `production`. **Nicht gesetzt oder unbekannt = production.** Eine
vergessene Einstellung gibt nie mehr Rechte. Gesetzt ist `local` in `docker-compose.yml` (Backend) und in
`.env.example`. CI und Tests laufen bewusst ohne den Schalter und pruefen so den geschlossenen Normalfall.

## 3. Agentenmatrix

| Handlung eines KI-Agenten | LOCAL / CI | STAGING / PRODUCTION |
|---|---|---|
| Lesen, Auswertungen, Entwuerfe vorbereiten | erlaubt (Rolle) | erlaubt (Rolle) |
| Schreiben ueber deklarierte Kommandowege | autonom, nur synthetische Daten | nur ausdruecklich je Aktion freigegebene `write_capabilities` (Default Deny) |
| Aktionen mit `forbiddenForAgents` (z. B. Buchen, Saldenvortrag) | gesperrt | gesperrt |
| Aktionen mit `humanApprovalRequired` (z. B. Zahlungen) | Freigabe durch eine Person | Freigabe durch eine Person |
| Gebuchte Belege aendern | verboten (Datenbank sperrt) | verboten |
| Eigene Rechte erweitern, Zugangsdaten aendern | verboten | verboten |

Pruefung: `app/services/mcp_write_capability.py` (`development_release` = `agenten_autonom()`); Ratschen in
`tests/test_umgebung_agentenmatrix.py`, `tests/test_mcp_write_capability.py`.

## 4. Offen

1. STAGING aufbauen (Zielhost, Geheimnisspeicher, Deploy) - Voraussetzung fuer M6.
2. Freigabeliste `write_capabilities` fuer STAGING/PRODUCTION fachlich fuellen (Vorschlag: Belegentwuerfe anlegen,
   Auswertungen).
3. Fiskaly-Zugaenge: aus `.env.example` entfernt (25.11.2026); falls je echt, beim Anbieter widerrufen.
