---
title: Active Workboard
type: reference
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-23
version: 3.3.0
description: Aktives Arbeits-Board fuer laufende und abgeschlossene Slices — kanonisches Format mit Von/Owner/Stand/Ziel/Dateibesitz/Abnahme-Feldern.
---

# Active Workboard

> M0-Bereinigung 23.11.2026: Hier stehen nur offene Eintraege (offen, reserviert, in Arbeit, zur Abnahme), jeder mit Meilenstein-ID nach docs/roadmap/fahrplan-verkaufsprodukt.md. Abgeschlossene und Altabschnitte ohne Status stehen woertlich in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md). Statuswoerter: offen, reserviert, in Arbeit, zur Abnahme, abgeschlossen, verworfen. Abgeschlossenes wandert beim naechsten Aufraeumen ins Archiv.

## PREISE-OHNE-SCHEINWERTE-20261104 — lokal abgenommen, Codex

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex (Slice Preisquellen). **Stand:** reserviert 2026-11-04. **Ziel:** Historie und Kundenpreis nur aus fachlich passenden Quellen oder mit ausdruecklichem 404 liefern. **Dateibesitz:** ausschliesslich die zwei Preis-Endpunkte in `mask_frontend_bridges.py`, zugehoerige Tests und eigene QA; Workboard-Integration durch Lead. **Abnahme:** keine erfundenen Preise, Kunden oder Daten; Mandanten-/Auth-Vertrag unveraendert; negative Vertragstests ohne DB-Abfragen. **Stand:** Implementierung und HTTP-/OpenAPI-Vertragstest mit produktivem Fehlerhandler geprueft (1 passed, Exit 0, ohne DB); generierte Projektionen synchronisiert; alle Doc-Generator-Checks, Pagination, Godfile, SQL-Fstrings und fuenf Feldvertraege gruen; Doc-Drift 0. **Ergebnis:** Beide Wege liefern 404 ohne erfundene Daten und ohne DB-Abfrage. Tagespreishistorie und Kundenvereinbarungen erfordern Artikel bzw. Kunde und … (gekuerzt; Volltext unter PREISE-OHNE-SCHEINWERTE-20261104 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## ADAPTIVE-WORKSPACE-20261022 — reserviert, Cursor Grok (Phase-1 Lead)

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Cursor Grok. **Stand:** reserviert 2026-10-22. **Ziel:** Adaptive Workspace Framework INNERHALB von VALEO, Phase 1 — zentrale Registry fuer Module/Views/typisierte Fachaktionen/User-Context; Command Center (Strg+K) auf berechtigte Fachaktionen; deterministische Priorisierung (KI nur leerer Hook); Pin/Fixieren der Startseite. **Dateibesitz (exklusiv):** `packages/frontend-web/src/workspace/**`, `packages/frontend-web/src/app/navigation/**`, Command-Palette-Mapping (`command-palette-model.ts` / `CommandPalette.tsx`), `docs/architecture/adaptive-workspace-framework.md`, Slice-YAML, Workboard, eigene Tests. **Nicht anfassen:** Inbox/Documents/CaptureScreenHost; Touren/Dispo/Fuhrpark-Godfiles; `mcp_execution_service.py` / `mask_action_runtime_service.py` / NATS-Core; Geschwister-Docs `adaptive-workspace-inbox.md`, `-disposition.md`, `-events-mcp.md`, `-erpclow-lessons.md`; Codex … (gekuerzt; Volltext unter ADAPTIVE-WORKSPACE-20261022 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## UIX-MASKENFAMILIEN-TAXONOMIE-20261022 — offen (Plan), Cursor Composer

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** — (Status `offen`, nicht reserviert). **Stand:** Planartefakt 2026-10-22. **Ziel:** Beleg-Vererbungsprinzip systemweit auf Ein-/Ausgabemasken: Kategorien Beleg/Stamm/Liste/Worklist/Ausnahme, Parent-Vertraege, reale Cluster aus Inventar (941 Routen / ~61 runtime_wired / ~120 legacy / ~760 hand_built) und ScreenDefinitions, Roadmap P0–P3. **Artefakt:** `docs/architecture/uix/maskenfamilien-taxonomie.md`; Slice-YAML `docs/agent-ops/slices/UIX-MASKENFAMILIEN-TAXONOMIE-20261022.yaml`; Handshake `docs/agent-ops/handshakes/maskenfamilien-taxonomie-20261022.md`. **Nicht anfassen:** Beleg-Slice `UIX-BELEG-FAMILIE-VERERBUNG-20261022` (bleibt separat offen); STUDIO-BELEG-THEME / STUDIO-MODEL / CI-GRUEN; Touren/Training/Bestellvorschlag; keine Page-Migration. **Abnahme:** Taxonomie + Roadmap + Handshake; keine Implementierungspflicht.

## UIX-BELEG-FAMILIE-VERERBUNG-20261022 — offen (Plan), Cursor Composer

Meilenstein: M1 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** — (Status `offen`, nicht reserviert). **Stand:** Planartefakt 2026-10-22. **Ziel:** Eingehende/ausgehende Belegfolgen als Parent/Child-Familie einer Maske planen (Taxonomie, Vererbungsmodell ScreenDefinition/Studio, Mapping ~9–14 Einstiege, Migrationsreihenfolge, Abgrenzung Studio-Import vs Runtime). **Artefakt:** `docs/architecture/uix/beleg-maskenfamilie-vererbung.md`; Slice-YAML `docs/agent-ops/slices/UIX-BELEG-FAMILIE-VERERBUNG-20261022.yaml`; Querverweis in `docs/design/beleg-studio-variantenmatrix.md`. Systemweite Erweiterung: `docs/architecture/uix/maskenfamilien-taxonomie.md`. **Nicht anfassen:** STUDIO-BELEG-THEME / STUDIO-MODEL / `screen_definitions_beleg.py` / `document_screen_versions.json` ohne Codex-Handshake; Bestellung-Create/Listen-WIP nicht ueberschreiben. **Abnahme dieses Plan-Slices:** Doku vollstaendig; keine Implementierungspflicht.

## MASK-STUDIO-ROLLOUT-20261020 - in Arbeit, Claude Code

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Claude Code. **Stand:** in Arbeit 2026-10-20. **Nutzerziel:** alle Masken Studio-kompatibel (Nutzerentscheid 19.10.: nur Studio-generierte Masken). **Ziel:** handgebaute (477) und Altmuster-Routen (102) in ScreenDefinitions ueberfuehren, in Wellen nach Familien, Reihenfolge Landhandel-Kern -> Finanzen -> CRM/Personal/Admin; vorher je Bereich Altlasten sichten (verwaist/Scheinseite -> entfernen statt umbauen). Laufzeit-Aktivierung nativer Masken aus dem Studio bleibt unveraendert (Sicherheitsentscheidung der Studio-Slices, eigene Nutzerentscheidung). **Dateibesitz je Welle:** betroffene Seiten unter `packages/frontend-web/src/pages/`, ihre Aliase/Routengruppen, neue ScreenDefinitions/Builder, eigene Tests, Ratsche und generierte Projektionen. Masken mit aktivem fremdem Claim werden uebersprungen. **Welle 0 erledigt:** sechs Scheinseiten/acht Routen entfernt (Ratsche 483->477, … (gekuerzt; Volltext unter MASK-STUDIO-ROLLOUT-20261020 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## MASK-CLI-20261019 - reserviert, Claude Code

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Claude Code. **Stand:** reserviert 2026-10-19. **Nutzerauftrag:** CLI fuer Maskenaktionen (Folge aus MASK-STUDIO-INVENTAR). **Ziel:** Kommandozeile `python -m valeo_cli` als reiner Client derselben Fachkommandos wie Maske und MCP: Aktionsvertrag live aus `GET /api/v1/masks/{id}/screen-definition` (mandantengenau), Request wie useActionRuntime (Pfadparameter, Eingabefelder, `_mode`/`_auditReason`/`_idempotencyKey`), Bestaetigung/Pflichtgrund/Agentensperre wie ActionRuntime; Rechte und Mandant ausschliesslich serverseitig. Anmeldung per OAuth Device Authorization Grant (Mensch meldet sich im Browser an, SSO/MFA/Passkey), alternativ Token aus Umgebung fuer Automatisierung; keine Passwoerter in der CLI. Nicht unterstuetzte Wege (commandBinding-Adapter docflow/harvest, inputFlow humanForm, Aktionen ohne Endpunkt) werden mit Grund abgewiesen und zaehlen in der Ratsche weiter als … (gekuerzt; Volltext unter MASK-CLI-20261019 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## AUDIT-IDENTITY-INTEGRITY-20261019 - reserviert, Codex

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex. **Nutzerauftrag:** Vier im Review zu7dbc168df bestaetigte Restbefunde schliessen. **Dateibesitz:** app/core/akteur.py nur unverkuerzte Kennung und FK-gebundene tenant-/providergebundene Nutzeraufloesung; app/infrastructure/models/__init__.py ausschliesslich AuditLog-FK-Metadaten an frisches Migrationsschema angleichen; sales_delivery_notes.py ausschliesslich Attestierungszuordnung/Identitaetsprovenienz; app/core/fibu_audit.py erforderliche Auditfehler/Transaktionsgrenze und schrittweise zugehoerige Aufrufer nach expliziter Erweiterung; eigene SQL-/Negativtests, QA/Workboard. **Abnahme:** Providerkennung ungleich lokaler PK, Fremdmandant/fehlende Zuordnung gesperrt statt system, SQL-Fehler kein stiller Fallback, Auditkennung unverkuerzt, keine fingierte atomare Gesamtfreigabe fuer unveraenderte Aufrufer. Bestehender valeo_probe und eigene Rollbackdaten, keine neue … (gekuerzt; Volltext unter AUDIT-IDENTITY-INTEGRITY-20261019 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-MIGRATION-ENGINE-20261020 - in arbeit, Codex

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nutzerentscheid: Funktionsmigration, automatische Verdrahtung und erforderliche
Schema-/Tabellengenerierung werden funktionale Bestandteile des vorhandenen
Studios. Owner Codex. Erster Lieferumfang: typisierter serverseitiger
Migrationsplan, kataloggebundene automatische Bindung und additive versionierte
Alembic-Artefakte, Zugriff ueber vorhandene Studio-API und CLI. Dateibesitz neue
app/services/studio_migration.py, app/api/v1/schemas/studio_migration.py,
studio_drafts.py ausschliesslich neuer Planweg/Kataloghinweis, valeo_cli/studio.py
nur Planbefehl, eigene Tests, Architekturprefix, betroffene generierte
API-/Inventar-/Handbuchprojektionen und Platform-Doku. Keine fremden
MASK-STUDIO-ROLLOUT-Seiten/Builder. Abnahme: unregistrierte Commands/URLs,
mehrdeutige Bindungen, SQL-/Namensinjektion und ueberschriebene Identitaetsfelder
sperren; Artefakt-/Definitionshash bindet Freigabeplan; … (gekuerzt; Volltext unter STUDIO-MIGRATION-ENGINE-20261020 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-GENERATED-ENTITIES-20261021 - in arbeit, Codex

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nutzerauftrag: allgemeine CRUD-/Tabellengenerierung und Fachkettenabnahme.
Eigener Gesamtclaim STUDIO-MIGRATION-ENGINE wird fortgesetzt. Besitz neuer
studio_entity_contracts/compiler/commands sowie eigener Tests; bestehender
Migrationscompiler nur notwendige gemeinsame Schemagenerierung, eigene CLI-
Unterbefehle und Studio-Authoringroute nur Anschluss. Keine fremden Fuhrpark-
oder Maskenseiten. Gemeinsamer Vertrag generiert typisierte Domaincommands,
Schemaartefakt, ScreenDefinition und Kanalspezifikationen. Ausschliesslich neue
Studio-Stammdatentabellen; Fachbuchungen, Zahlungen und Bestaende bleiben in
registrierten Fachcommands. Rollen aus bestehendem Bereichsmodell, Mandant aus
verifizierter Identitaet, Idempotenz/Version/Audit transaktional. Keine freie
SQL-Ausfuehrung oder Aktivierung durch MCP. Bestehende Register statt zweiter
Rechteverwaltung; ungepruefte Writes bleiben … (gekuerzt; Volltext unter STUDIO-GENERATED-ENTITIES-20261021 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-ENTITY-RELEASE-20261021 - reserviert, Codex

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Gesamtziel: Studio voll funktionsfaehig, alle Masken ueber CLI mit belastbarem
Qualitaetsnachweis migrieren. Naechster Integrationsslice: eigenes
studio.entity.v1-Freigabeprofil fuer registrierte generierte Stammdaten.
Besitz: neues studio_entity_simulation.py, studio_release.py nur Profilauswahl/
Nachweispruefung; studio_process_simulation.py nur Artefaktbindung; Entitycompiler
nur Profil-/Registrierungsprojektion, Commandrouter/-service nur gemeinsamer
Bereitstellungscheck. Eigene Unit-/SQL-/Freigabetests und generierte Projektionen.
Kein pauschales Oeffnen von grain.v1, keine fremden Fachmasken oder Gateabsenkung.
Simulation: vorhandener valeo_probe, echte Domaincommands und zurueckgerollte
synthetische Daten/Outbox; kein neuer Container/DB/Reset. Testtabellen nur eigene
eindeutig bezeichnete Artefakte, kontrollierte eigene Bereinigung.
Abnahme: serverseitige Registrierung und … (gekuerzt; Volltext unter STUDIO-ENTITY-RELEASE-20261021 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-MODEL-20261015 — in Arbeit, Codex

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex. **Stand:** in Arbeit 2026-10-15. **Ziel:** Optionales echtes Sprachmodell fuer kataloggebundene Anforderungsinterpretation, ohne unkontingentierte Agentenaufrufe. **Dateibesitz:** llm_gateway.py nur additive metered response; neue studio_semantic_model.py; Erweiterungen im eigenen Semantic-Dialog/API/UI-Claim und eigene Tests/Doku. config/architecture-domain-prefixes.yaml nur neue Studio-Servicezuordnung, generierte eigene Architektur-/Service-/OpenAPI-Projektionen. **Abnahme:** vorhandenes Modellgateway und Kontingentnebenbuch wiederverwenden; vor Aufruf reservieren; verifizierter Budgeteigentuemer/Mandant, begrenzte Eingabe/Ausgabe; kein Wiederholungs-Doppellauf; fehlende Nutzungsdaten/unklare Fehler behalten Reservierung, keine erfundenen Tokenwerte. Modellvorschlag serverseitig strikt auf Vertrag und erlaubte Felder beschraenken. **Risiko:** Positive … (gekuerzt; Volltext unter STUDIO-MODEL-20261015 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-SEMANTIC-20261015 — in Arbeit, Codex

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex. **Stand:** in Arbeit 2026-10-15. **Ziel:** Nutzerplan fuer dialogfaehiges Studio verbindlich integrieren; anschliessend fachsprachliche Getreideannahme ohne erfundene Datenbindungen ueber bestehende Meridian-Engine nachweisen. **Dateibesitz:** neue docs/architecture/studio-semantic-standard.md, eigener Governance-/QA-/Workboard-Abschnitt; spaetere Codeintegration nur nach erweitertem Dateiclaim. **Abnahme dieser ersten Etappe:** STUDIO-SEMANTIC-001, fuenf Phasen und pruefbare Referenzszenarien dokumentiert; CI-Nachlauf der Baselinesenkung exakt berichtet. **Risiken:** vier Vorlagen sind kein Agentendialog; Berechnungsvorschau ist kein Freigabenachweis. Gesamt-CI und develop-Identitaetssperre bleiben sichtbar. Keine neue DB/Container, kein fremder CI-Dateibesitz.

**Zwischenergebnis:** STUDIO-SEMANTIC-001 uebernommen und Governance verknuepft; CI-Nachlauf der … (gekuerzt; Volltext unter STUDIO-SEMANTIC-20261015 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## CI-GRUEN-20261014 — in Arbeit, Codex (uebernommen)

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Zwischenstand 1:** 87 Testdateien von der Produktions-App mit abgeschafftem Dev-Token auf die Test-App `app.main` bzw. ausdrueckliche Testgrenze (`tests/testgrenze.py`: `ersetze_bearer`, `ALLE_FACHROLLEN`) umgestellt — darunter 28, die CI wegen fehlendem Identity-Provider still uebersprungen hat. **Gefunden und behoben:** `ap_memo_booking` ohne Mandant (Regression aus ALTBELEG-QUARANTAENE: Memo-Buchung scheiterte); `token_type == "dev"`-Sonderwege in `rbac`/`security`/Lagerpruefung entfernt (gaben Admin-Rechte bzw. liessen jede Pruefung aus), Lagerpruefung auf Fachrollen `LAGER_*`, totes `app/core/inventory_permissions.py` entfernt; Etikettendruck gab rohes SQL samt Parametern an den Client. Offen fuer Codex: `test_posting_services` (Self-Billing-Eingangssteuer, aktiver Slice SELF-BILLING-ATOMIC).

**Zwischenstand 2:** UAT-Vertrag getrennt (ohne Anmeldung → main:app, Fachpruefungen → … (gekuerzt; Volltext unter CI-GRUEN-20261014 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## MCP-WRITE-CANONICAL-ENFORCEMENT — offen

Meilenstein: Strang A (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** offen. **Ziel:** Separaten MCP-ERP-Ausfuehrungsdienst und Command-/Capability-/Superglue-Pfade gemaess MCP-WRITE-001 bis 015 inventarisieren und durchsetzen; keine Schreibfreischaltung ohne versionierte Domain-Commands und Agentenrollen-Nachweise. **Dateibesitz:** vor Umsetzung separat claimen. **Abnahme:** Mandant/Rechte/Idempotenz/Version/Freigabe/Transaktion/Audit/Outbox sowie Gleichwertigkeit der Adapter.

## LOGIN-VARIANTS-20261013 — in arbeit, Codex

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex, Chat 01a0f3fc. **Von:** Auftraggeber: Anmeldeprozess in allen Varianten testen, real im Browser mit Screenshots. **Ziel:** nachvollziehbare Testmatrix fuer Providerlogin, PKCE/Callback, Token-/Mandanten-/Rollenbindung, Refresh, Logout, Widerruf, MFA-/Kennwortablauf und Dienste. **Dateibesitz:** lib/auth.test.ts nur neue Varianten, gegebenenfalls Authquellen innerhalb bestehender Elternclaims; eigene QA/Handbuch samt ausschliesslich echten synthetischen Screenshots; eigene Provider-Testfixture-/Pruefskripte. **Abnahme:** automatische Verträge und reale Browsernachweise getrennt; kein fingierter Erfolg, keine persönlichen Kennungen/Passwörter/OTP in Git oder Screenshots; persönliche MFA bleibt vertagt, Kennwortänderung im Browser erforderlichenfalls Benutzerhandoff. Vorhandener Prüfstand, keine DB/Container/Reset. Provider-Testdaten nur eigene synthetische Kennungen, … (gekuerzt; Volltext unter LOGIN-VARIANTS-20261013 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## IDENTITY-ADMIN-HANDBUCH-20261012 — in arbeit, Codex

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex, Chat 01a0f3fc. **Von:** Auftraggeber: Testanmeldung, Mandanten-/Administrator-/Nutzer-/Agentenverwaltung mit Handbuch-Screenshots und hierarchischen Kontingenten. **Ziel:** echte Verwaltungswege, Loeschschutz ab erster Buchung, Sperre statt Loeschen, kontingentgebundene Unterdelegation und nachvollziehbares Verbrauchsnebenbuch. **Dateibesitz:** app/api/v1/endpoints/tenants.py, neues app/services/tenant_lifecycle_service.py; neue identity_quota-Module und eigene Tests; neue native Verwaltungs-ScreenDefinitions in eigenem Modul samt eng begrenzter Registry-Anbindung, neue thin-wrapper Routen (kein fremdes Maskenstyling); docs/benutzerhandbuch/identity-administration.md samt ausschliesslich synthetischen Screenshots, eigene QA/Workboard/ADR083-Ergaenzung. Bestehender IDENTITY-CONTROL-Claim behaelt Provider/User-/Agent-API und deren Integration. **Abnahme:** … (gekuerzt; Volltext unter IDENTITY-ADMIN-HANDBUCH-20261012 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## IDENTITY-INTEGRATION-REST-20261012 — in arbeit, Codex

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex, Chat 01a0f3fc. **Von:** Auftraggeber „rest bitte auch noch umsetzen“. **Ziel:** offene Sitzungs-, Agenten-, Freigabe- und Ressourcenvertraege in vorhandene Wege integrieren. **Dateibesitz:** app/auth/oidc.py und dependencies.py nur zentrale verifizierte Identitaet; operator_agent.py samt operator_agent_service.py und agent_proposal_repository.py/model/schemas nur Tokenurheber, Inhaltsbindung, Idempotenz und Ausfuehrungsgrenze; frontend hooks/useAuth.ts, lib/api-client.ts und axios.ts nur Authkonfiguration/Refresh/Logout, ProtectedRoute.tsx nur OIDC-Bypass-Hunk (fremdes Styling erhalten); config/architecture-domain-prefixes.yaml nur neue eigene Identitaetsmodule; eigene Tests/QA/ADR und Plattform-Domainpack. Elternclaim IDENTITY-CONTROL behaelt Sessionmodule, Neuro-Broker/Gateway und lib/auth.ts. **Abnahme:** kein frei gelieferter Urheber/Rolle, kein dev/HS-Fallback, … (gekuerzt; Volltext unter IDENTITY-INTEGRATION-REST-20261012 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## IDENTITY-CONTROL-20261012 — in arbeit, Codex

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex, Chat 01a0f3fc. **Von:** Auftraggeber „Rest auch noch umsetzen“. **Ziel:** ERP-Providerbetrieb, administratives Mandantenprofil, Sitzungswiderruf, Agentenmandate, inhaltsgebundene Freigaben und atomare Ressourcenbegrenzung an vorhandenen Ausfuehrungswegen integrieren.
**Dateibesitz:** config/keycloak/realm-export.json, realm-staging.json und neues user-profile.json; neuer scripts/provision_identity_provider.py; app/core/config.py nur Identitaets-/Sitzungs-/Limitfelder; neue core-Identitaetsmodule und identity_management-Endpoint samt API-Registrierung; main.py/core/security.py/deps_oidc.py nur gemeinsame Enforcement-/Streaming-Anbindung; services/neuro_tool_broker.py, neuro_tool_execution.py und llm_gateway.py nur Autorisierung/Budget; frontend lib/auth.ts nur vorhandene Anmeldung/Logout (kein fremdes Masken-WIP); neue Tests/QA/Proposed ADR/Runbook/Domainpack/Inventare … (gekuerzt; Volltext unter IDENTITY-CONTROL-20261012 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## IDENTITY-ARCHITECTURE-IMPLEMENTATION-20261012 — in arbeit, Codex

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex, Chat 01a0f3fc. **Von:** Auftraggeber „setze den Architekturentwurf um“. **Ziel:** vorhandene OIDC-Validierung verbindlich machen, Default-/Dev-/HS-Identitaetsumgehung entfernen; HTTP und WebSockets denselben geprueften Mandanten verwenden lassen. Bestandteil der Umsetzung, kein Gesamtabschluss der Sitzungs-/Agentenarchitektur.
**Dateibesitz:** docs/architecture/security/central-identity-agent-management-proposal.md fuer Umsetzungslieferstand; eigener QA-/Workboard-Plan. Ausfuehrender Code bekommt weiterhin abgegrenzte Unterclaims.
**Abnahme:** echte RSA-Token, fehlende Claims/Signatur/Dev/HS abweisen; fremde Header/Querywerte vor Fachzugriff, nicht-API-Routen ebenfalls authentifizieren; Querytoken nur SSE/WS. WS-Kontext nicht frei waehlen und nach Ablauf keine Fachwirkung. Bestehende Nachbarvertraege und explizite Callback-Vertraege pruefen. Keine … (gekuerzt; Volltext unter IDENTITY-ARCHITECTURE-IMPLEMENTATION-20261012 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## SYSTEM-TENANT-BOUNDARY-20261012 — in arbeit, Codex

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex, Chat 01a0f3fc. **Von:** Auftraggeber „dann schliesse diese Sicherheitsluecke systemweit“. **Ziel:** verbindlicher verifizierter Mandantenkontext vor allen geschuetzten API-Fachzugriffen; kein permissiver Missing-Claim-/Dev-/Headerfallback. Zentrale Path-/Query-/Body-Bindung und Inventar aller Umgehungsflaechen, schrittweise echte zwei-Mandanten-Abnahme. Breite Rollen und explizite Shared-Data-Policies bleiben getrennte Rechte.
**Dateibesitz:** main.py nur Bearer-/Mandantenmiddleware und abschliessende Routebindung; app/auth/tenant.py zentraler vorhandener Claimvertrag; app/core/tenant.py und app/auth/deps.py/deps_oidc.py nur Wiederverwendung verifizierter Requestidentitaet; neues zentrales Route-Binding-Modul und Tests/QA/Proposed ADR/Workboard. Bank-/SEPA-Folgeobjekte und WebSocket-/MCP-Kontext nach eigenem abgegrenztem Unterclaim. Keine … (gekuerzt; Volltext unter SYSTEM-TENANT-BOUNDARY-20261012 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## FINANCE-BANK-ACTIONS-TOKEN-CONTEXT-20261012 — offen

Meilenstein: M3 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** unbesetzt. **Von:** Codex, Rollenschnitt FINANCE-BANK-ACTIONS-ROLES-20261012. **Ziel:** Bank-/Finanzaktionsmandant an verifizierte Tokenmitgliedschaft binden; eigene SEPA-/Raten-/Mahn-default-Fallbacks entfernen, Mahnstufenoperator aus Token, Folgeobjekte fuer denselben Kontext pruefen. **Dateibesitz:** vor Claim Bank-/Finanzaktions- und Serviceverbraucher klaeren; keine Uebernahme von Claudes aktivem Kontenplan-Praxis-/Tokenclaim. **Abnahme:** echte Tokens/Providerkonfiguration, zwei Mandanten, fremde Header/Referenzen ohne Fachwrite/Datenabfluss, Rechte/Widerruf und atomarer Urheber/Auditvertrag; Tests im bestehenden gemeinsamen Pruefstand, keine neue DB/Container/Reset. **Risiko:** bestehende Finanzrollen verwenden legacy JWT-Deps, WhatsApp verifizierte OIDC-Deps; zentralen bestehenden Vertrag konsolidieren, keine weitere Auth-Parallelpipeline. **Lieferung bisher:** nur … (gekuerzt; Volltext unter FINANCE-BANK-ACTIONS-TOKEN-CONTEXT-20261012 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## WHATSAPP-EMERGENCY-ALLOCATION-20261012 — offen

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** unbesetzt. **Ziel:** seltene Last-minute-Ausnahme auf kanonischer Auftrags-/Dispositionsebene: freigegebene Kammerumverteilung, akzeptierte Ersatz-Teilmenge und Restmengen beider Kunden; originalen Wunsch und operative Abweichung trennen. **Dateibesitz:** vor Claim Verbraucher-/Schemaabgleich, kein paralleles Auftragsmodell. **Abnahme:** Mengenbilanz/richtige Artikel-/Chargen; menschliche Dispositions- und belegte Ersatzfreigabe; zwei autorisierte Kunden ohne gegenseitigen Datenauszug; konkurrierende Allokation/Replay/Rollback/Ruecknahme ohne Doppelbindung; Folgetermin nur bei Verfuegbarkeit, Ausnahme nicht als normale Mengen-/Sortenpraeferenz lernen. **Risiken:** Kammer-/Kesselvertrag fuer Bestelleingang nicht nachgewiesen, Rations-Einzelfutterassistenz keine Freigabe fuer Kraftfuttermischung oder Transport. **Abhaengigkeiten:** INBOX-TRUST, ORDER-HISTORY, DELIVERY-PLANNING; … (gekuerzt; Volltext unter WHATSAPP-EMERGENCY-ALLOCATION-20261012 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## KONTENPLAN-VERIFIED-SHARED-POLICY-20261012 — offen

Meilenstein: M3 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** unbesetzt. **Von:** Codex, Hinweis und Codeabgleich zu Claudes fbc4aedb6. **Befund:** Kontenplan-Query-/Rumpfumgehung repariert; get_tenant_id aus app/core/tenant.py nimmt weiterhin X-Tenant-ID mit Default statt verifizierter Tokenbindung. _konto erlaubt system auch fuer Aendern/Deaktivieren; gemeinsame Lesbarkeit und allgemeine Pflege sind unterschiedliche Rechte. Keine Gegenreparatur in fremdem Slice vorgenommen. **Ziel:** bestehende verifizierte Guards und explizite Pflegepolicy fuer gemeinsamen Rahmen konsolidieren. **Abnahme:** fremder Header mit echtem Token abgewiesen, system fuer erlaubte Leser sichtbar, fehlende gemeinsame Pflegerechte ohne globale Mutation, zwei echte Mandanten. **Risiko:** bestehende Kontenplan- und Benutzer-/Maskenvertraege vorher pruefen; eigener Claim/Dateibesitz noetig. Kein Reset/neue Testdatenbank.

## WHATSAPP-INBOX-TRUST-20261011 — offen

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** unbesetzt. **Ziel:** Eingangsrechte, mandantengepruefte Kunden-/Artikelreferenzen, Tokenurheber und atomarer Eingangs-/Korrektur-Replay vor Historienlernen. **Dateigrenzen vor Claim:** whatsapp_intake Endpoint/Service, passende Tests und eigener Doku-Nachweis. **Abnahme:** zwei echte Mandanten, fremde Referenzen, kein Default-/Headerbypass, konkurrierender Replay, Original/Korrektur nachvollziehbar. **Risiko:** bestehender globaler Kundenlookup. Vertrag: ../workflows/whatsapp-order-learning.md.

## WHATSAPP-ORDER-HISTORY-20261011 — offen

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** unbesetzt. **Ziel:** kanonische Silo-/Gebinde-/Einheitenvertraege und begrenzte autorisierte Auftragsgeschichte. **Abnahme:** Verbraucher-/Schemaabgleich; Artikelvarianten/Lieferstellen getrennt, keine zweite JSON-Auftragshistorie. **Abhaengigkeit:** INBOX-TRUST; eigene Dateigrenzen/Claim vor Umsetzung. Vertrag: ../workflows/whatsapp-order-learning.md.

## WHATSAPP-LEARNING-ENGINE-20261011 — offen

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** unbesetzt. **Ziel:** heuristisch lernende feldbezogene Vorschlaege, Kalibrierung und menschliche Korrektur; keine starre Letztauftrag-Kopie. **Abnahme:** zeitlich getrennte Bewertungsdaten, verbesserter Folgefall nach Korrektur, Cold Start/Ambiguitaet, explizite Angaben erhalten, kein Feedback-Replay/Trainingsleck. **Abhaengigkeit:** INBOX-TRUST und ORDER-HISTORY; eigene Dateigrenzen/Claim. Vertrag: ../workflows/whatsapp-order-learning.md.

## WHATSAPP-DELIVERY-PLANNING-20261011 — offen

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** unbesetzt. **Ziel:** aktuelle Verfuegbarkeit und feste woechentliche Stueckguttour, Alternativen und persistente Kundeninformation bei fehlendem Folgetag. **Abnahme:** Kapazitaet/Annahmeschluss/Feiertag/Wochenwechsel/ausdruecklicher Wunsch; kein Termin ohne Quelle, keine doppelte Meldung. **Risiko:** Browser-Versand bleibt eigener offener Claim; eigene Dateigrenzen/Claim. Vertrag: ../workflows/whatsapp-order-learning.md.

## WHATSAPP-WEB-INTEGRATION-20261011 — offen

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** unbesetzt. **Ziel:** Browsertransport gemaess docs/workflows/whatsapp-web-computer-use.md implementieren; Meta-/Simulatorwege nach Verbraucheranalyse konsolidieren. **Abnahme:** verifizierte Konto-/Mandantenbindung; dauerhafte idempotente Eingangs-/Versandnachweise; echte Negativ- und Wiederanlauftests; autorisierter Browser-Testversand mit benanntem Empfaenger. **Risiken:** vorhandener Header-/Default-Mandant im Webhook, fluechtige Outbox, paralleler Bestellsimulator. Vor Umsetzung eigene Dateigrenzen/Claim festlegen.

## QUALITY-GATE-MASK-CONTRACT-20261011 — in arbeit, Codex

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex, Chat 01a0f3fc. **Ziel:** Sechs echte CI-Regressionsbefunde aus Run 38124045945 schliessen: Fuhrpark-Aktionsberechtigungen, konkurrierende Personal-Stubs und pruefbare neue Personal-Commandvertraege.
**Dateibesitz:** fokussierte Hunks app/core/screen_definitions_capture.py; tests/test_bewerbermanagement_ordnung_vertrag.py, test_bewerbung_erklaerung_fassung_vertrag.py, test_personal_bewerbungen_roles.py, test_mask_input_flow_contracts.py; eigener QA-/Workboard-/Meridian-Doku-Block und daraus nachweislich driftende Generatorartefakte.
**Abnahme:** native Readiness und Command-Inventar streng gruen; neue Personal-Commands tatsaechlich gegen Rollenmatrix vor DB-Zugriff pruefen, keine pauschale Modell-/Routenausnahme. Vollsuite 17296 gruen/6 rot als Ausgangsnachweis. Keine DB/Container/Reset, keine Gate-Abschwaechung, fremde Hunkbereiche schuetzen.

**Zwischenabnahme / … (gekuerzt; Volltext unter QUALITY-GATE-MASK-CONTRACT-20261011 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## QUALITY-GATE-SONAR-BACKEND-20261011 — in arbeit, Codex

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex, Chat 01a0f3fc. **Ziel:** Echte verbliebene Sonar-Backendbefunde beheben: Newsletter-Log-Injection, Freigeber-Parameterueberschreibung, unerreichbarer Kulturreturn und redundante Mengenbedingungen.
**Dateibesitz:** app/api/v1/endpoints/compat.py, ap_invoices.py, agrar_wetter.py, inventory_operations.py; modules/einkauf/services/bestellvorschlag_service.py; neue fokussierte Tests, eigene QA/Doku-Hunks und committed Generatorartefakte bei messbarem Drift.
**Abnahme:** echte Verhaltenspruefungen ohne DB/SMTP-Nachrichten, Code-/API-Vertraege unveraendert, keine Gate-Ausnahme. XML-Namensraeume und Masken-Passwortfeld sind gesondert zu bewertende Scannerbefunde, nicht blind umzuschreiben. Fremdes WIP schuetzen; Gesamt-Sonar-Abnahme weiter offen.

**Zwischenabnahme:** Fuenf Backend-Befunde korrigiert; fuenf echte Verhaltensvertraege gruen, gemeinsam mit staged MCP-Vertraegen … (gekuerzt; Volltext unter QUALITY-GATE-SONAR-BACKEND-20261011 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## QUALITY-GATE-CATALOG-SYNC-20261011 — in arbeit, Codex

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex, Chat 01a0f3fc. **Ziel:** Durch MCP-Drift verdeckten physischen Katalogdrift schliessen: committed Fuhrpark-Migration fuegt tenant_id auf vier Tabellen hinzu; committed Katalog fuehrt diese Spalten noch nicht.
**Dateibesitz:** docs/admin/table-catalog.json und .md ausschliesslich im isolierten Lieferindex, eigene QA-Doku, eigener Workboard-Block. Fremde Arbeitsfassungen beider Katalogdateien bleiben byteweise erhalten.
**Abnahme:** Katalog aus realem frischen GitHub-Job nach committed Migration, kanonische Darstellung/Lineage vergleichen, Quality Gate erneut vollstaendig. Keine lokale Migration/Reset/DB-/Containeranlage; bestehende CI-Job-Datenbank.

**Abnahme:** Echte CI-Ernte 38122841810: 670 Tabellen unveraendert, genau vier additive tenant_id-Spalten, sieben Code-Verbraucherzuordnungen korrigiert. Keine PK/FK-Aenderung, keine fehlende Lineage. JSON/Markdown … (gekuerzt; Volltext unter QUALITY-GATE-CATALOG-SYNC-20261011 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## QUALITY-GATE-MCP-DRIFT-20261011 — in arbeit, Codex

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex, Chat 01a0f3fc. **Ziel:** Quality Gate MCP-Referenzdrift aus Run 38121252132 beheben und Wiederholung durch staged Registry-/Referenzvertrag verhindern.
**Dateibesitz:** scripts/generate_mcp_tool_reference.py, scripts/run-staged-checks.cjs, docs/schnittstellen/mcp-tools.md, neuer fokussierter Generator-Test, eigene QA-Doku, eigener Workboard-Block und README-CI-Nachweis. **Abnahme:** Generatorsequenz aus isoliertem committed Lieferstand, staged Drift-Negativtests, GitHub Quality Gate auf Ergebniscommit erfolgreich; main push/develop Sync.
**Risiken:** Fremdes WIP nicht integrieren; Tests ohne neue DB/Container. Weitere durch den ersten Abbruch verdeckte Fehler bei Auftreten im Gate ebenfalls diagnostizieren.

**Zwischenabnahme:** Referenz aus committed Registry auf 56 Tools regeneriert; sieben staged Drift-Vertraege bestanden. GitHub-Folgeabnahme nach Ergebnis-Push; … (gekuerzt; Volltext unter QUALITY-GATE-MCP-DRIFT-20261011 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## CI-RUN-REPAIR-20261005 — in arbeit, Codex (Chat 01a0f3fc)

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**FUHRPARK-PUBLISH-NORMALIZATION-20261009 (reserviert):** Owner Codex-01a0f3fc. Abschlusskontrolle: private Index-Publikation hat Windows-CRLF in eigenen Textartefakten erhalten und dadurch grosse rein formale Diffs erzeugt. Ausschliesslich33 eigene Lieferdateien plus eigenen Folgefix auf kanonische LF normalisieren, byteweise Gleichheit nach Zeilenendnormalisierung beweisen. Keine Fachcodeaenderung, keine fremden Arbeitsdateien/Staging, keine DB/Container;581 Tests bleiben semantisch identisch.

**FUHRPARK-CI-CONSUMERS-20261009 (abgeschlossen):** Owner Codex-01a0f3fc. Zwoelf bestehende Fuhrpark-Vertiefungsvertraege auf eigene rollback-isolierte Probe-Fahrzeuge und verifizierte Testclaims umgestellt; keine fremden Entwicklungsdaten/Seed-Skips. Drei fehlende Slice-Pflichtfelder im roten GitHub-DocsGovernance ergaenzt; lokaler Check genau1 Slice gruen. Isoliert final581 Tests ohne Skip … (gekuerzt; Volltext unter CI-RUN-REPAIR-20261005 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## BANK-RECONCILIATION-PROOF-20261001 — in Arbeit, Codex (Chat 01a0f3fc)

Meilenstein: M3 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex-01a0f3fc. **Ziel:** Gespeicherte mandantengebundene GL-Konto-ID
statt verlorenem gl_account_number; Saldenvergleich mit Konto-/Tenantbindung,
expliziter Datenvollstaendigkeit und ohne verschluckte Lesefehler.
**Dateibesitz:** bank_accounts.py, bank_reconciliation.py, finance_actions.py nur
Bank-Run, zugehoerige Schemas, zentrale Bank-TS-Vertraege/Optionshooks,
eigene Bank-GL-Migration und Tests/QA/ADR/Slice; bank-abgleich.tsx nur
Vertragsintegration, bank-stamm/bankkonten-stamm nur GL-Vertrag; eigene
Workboard/Gaps/Finance-API-Abschnitte und abgegrenzte OpenAPI-Vertragshunks.
**Abnahme:** Fremdkonto/-tenant 404; SQL-Fehler sichtbar; CSV ohne Banksaldo
kein erfolgreicher Saldenbeleg; fehlender GL-Link/Journalnachweis ungeklärt;
PARTIAL/Unknown-Zaehler und Dezimalwerte typisiert; reale PostgreSQL-Vertraege.
**Risiken:** Fremde EUDR-Migrationen aktiv: keine gemeinsame … (gekuerzt; Volltext unter BANK-RECONCILIATION-PROOF-20261001 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## OPENAPI-DRIFT-REFRESH-20260930 — reserviert, Codex

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Ziel:** Den vom Quality-Gate belegten OpenAPI-Drift aus einem sauberen HEAD
regenerieren, ohne parallele CRM-/Meridian-Routen aus dem Arbeitsbaum zu
veroeffentlichen.
**Dateibesitz:** `docs/schnittstellen/openapi.json`, eigene Slice-/QA-Doku und
dieser Abschnitt.
**Abnahme:** Generator-Check bytegenau gruen; Pfadzahl dokumentiert; Doku-Gates
gruen; keine fremden Arbeitsbaumdateien im Commit.
**Risiken:** Jeder spaetere Router-Commit muss die Spezifikation erneut
regenerieren; der Workflow bleibt bewusst read-only und fail-closed.

## BUSINESS-TIME-RATCHET-20260930 — reserviert, Codex

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Ziel:** Neue direkte Ableitungen fachlicher Tageswerte aus Host- oder UTC-Zeit
systemweit verhindern. Ein AST-basiertes Ratchet-Gate misst den vorhandenen
Altbestand unter `app/`, blockiert neue oder verschobene Verstoesse und zwingt
bei Abbau zur abgesenkten Baseline.
**Dateibesitz:** `scripts/check_business_time_usage.py`,
`config/business_time_usage_baseline.json`,
`tests/test_business_time_usage_gate.py`, `.github/workflows/quality-gate.yml`
(nur neuer Gate-Schritt), eigene Slice-/QA-Doku, BUSINESS-TIME-Abschnitt in
Open-Gaps und dieser Abschnitt.
**Abnahme:** Direkte `date.today()`- sowie `datetime.now/utcnow().date()`-Muster
werden aliasfest erkannt; der Bestand ist exakt inventarisiert; neue, verschobene
oder wieder eingefuehrte Verstoesse lassen das Gate fehlschlagen; Abbau verlangt
eine kleinere Baseline; Unit-Tests, Gate und Doku-Gates sind gruen.
**Risiken:** Der Bestand … (gekuerzt; Volltext unter BUSINESS-TIME-RATCHET-20260930 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## HOME-UIX-ANWENDER-BEDIENWEGE — Touch, Sprache, Agent 2026-09-17, Cursor

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Stand:** in Arbeit 2026-09-29, Code auf main (`e7aa92913`). BWA, Bilanz, GuV und Lastschriften:
Arbeit zuerst, Theater nur Desktop, 44 px. CSV-Export der Bilanz ohne Global-Intercept.
Sprache findet BWA-Auswertung / GuV-Rechnung / Lastschriften-Debitoren / Bilanz.
Ablage: Export umgeht den Global-Intercept, Folgezeile nur Desktop.
KIM, Auftrag, Rechnung und Lieferschein: size=sm weg, Schaltflaechen 44 px, Struktur bleibt Claude.
Register-Tabs zentral `min-h-touch`. ELSTER und Bankabgleich: Arbeit zuerst, Theater nur Desktop.
Sprache findet elster-online und bankabgleich.
`sales.invoice.propose` speichert einen ausstehenden Rechnungsvorschlag und bucht nicht.
Naechste: weitere MCP-Schreibadapter.

**Ziel:** Produktive Einstiege per Finger, Stimme und ehrlichem Agent-Vertrag
bedienbar machen; Lücken dokumentieren statt Dynamics-MCP vortäuschen.

**Dateibesitz:** `TopBar.tsx`, … (gekuerzt; Volltext unter HOME-UIX-ANWENDER-BEDIENWEGE in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## FSX-ARTIKEL-IMPORT - reserviert 2026-09-15

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Claude Code. **Ziel:** Kanonisches XML-Zwischenformat fuer den
Artikelstamm aus Lieferantenangeboten — fuenf getrennte Ebenen
(Artikel → Variante → Lieferantenartikel → Gebinde → Kondition), Preisbasis mit
Menge und Einheit, Gebinde und Logistikeinheit strikt getrennt, unklare
Quellwerte als `sourceValue` erhalten.
**Dateibesitz:** `docs/design/artikel-import-format.md`, Schema-Datei,
`app/services/article_import.py`, Tests, Slice, dieser Abschnitt.
**Abgrenzung:** **kein** Schreiben in `domain_inventory.articles` in diesem
Slice. Erst Format, Parser und Pruefung; die Uebernahme in den Stammsatz ist ein
eigener Schritt mit eigener Abnahme.
**Abnahme:** Das Beispiel GENO-Saaten/WWH Hycard laeuft durch; „BKH" bekommt
keine gedeutete Bedeutung; 49 x 25 kg = 1225 kg wird geprueft statt geglaubt;
Preis ohne Preisbasis wird abgewiesen.

## FSX-MENGENMODELL - reserviert 2026-09-15

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Claude Code. **Ziel:** Positionsbezogenes n:m-Mengenmodell (K5) mit
Einheiten- und Gebindesystem des Agrarhandels — dt als Standardgroesse, PSM-Pack
mit rollenabhaengiger Aufloesung.
**Dateibesitz:** neues `docs/design/agrar-mengen-gebinde-modell.md`, Modell und
Migration fuer die Positionszuordnung, zugehoerige Tests, Slice, dieser Abschnitt.
**Abgrenzung:** kein Eingriff in bestehende Belegmasken oder in
`docflow_source_proposals`. Erst Recherche und Modell, dann Code.
**Abnahme:** Einheiten belegt recherchiert (Quellen genannt); dt als
Standardgroesse; Pack-Aufloesung und -Sperre modelliert; Split/Merge auf
Positionsebene mit Restmengenfuehrung.

## FSX-LS-KONSOLIDIERUNG - reserviert 2026-09-15

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Claude Code. **Ziel:** Die dritte, aeltere `capture-then-resolve`-Umsetzung
in `pages/verkauf/lieferschein-erfassung.tsx` auf `document-flow-spine.ts`
zurueckfuehren — eigener Slice, weil sie den Speicherpfad einer produktiven
Maske beruehrt.
**Dateibesitz:** `pages/verkauf/lieferschein-erfassung.tsx` (nur der
Workflow-Abschnitt), zugehoerige Tests, `docs/agent-ops/slices/FSX-LS-KONSOLIDIERUNG.yaml`,
dieser Abschnitt.
**Abgrenzung:** kein Eingriff in die Belegerfassung selbst (Positionen, Mengen,
Speichern). Nur die Verknuepfung danach.
**Abnahme:** bestehende Lieferschein-Tests unveraendert gruen; Verhalten der
Verknuepfung identisch; keine dritte Entscheidungslogik mehr im Repo.

## RESTFEHLER-20260911 - in arbeit

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Von:** User-Auftrag „alle restlichen Fehler beheben" nach SPEC-P0-05.
**Owner:** Cursor Auto. **Stand:** in arbeit 2026-09-11.
**Ziel:** Den roten Restbestand aus Vollsuite und CI-Gates an der Ursache
schliessen — keine Schwellensenkung, keine Testentschaerfung.
**Dateibesitz:** dieser Abschnitt, Slice-YAML `RESTFEHLER-20260911`,
`services/ai/requirements.txt`, `app/core/business_time.py`,
`app/services/feed_inventory_link_service.py`,
`app/api/v1/endpoints/produktion_mischfutter.py`,
`app/api/v1/endpoints/logistik_frachtbriefe.py`,
`app/services/sales_posting_service.py`,
`app/services/harvest_acceptance_service.py` (nur Datumsfallback),
`app/services/procurement_service.py` (nur Datumsfallback),
`app/services/ap_invoice_kernel_posting.py` (nur Datumsfallback),
`app/services/agrar_settlement_service.py` (nur Datumsfallback),
`app/services/settlement_drying_service.py` (nur … (gekuerzt; Volltext unter RESTFEHLER-20260911 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## DESIGN-STATUS-COLORS-020 - in Arbeit

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Von:** Welle 6 aus DESIGN-STATUS-COLORS-019, User-Auftrag „Rest nach Best
Practice abschliessen, weniger ist mehr". **Owner:** Claude Code.
**Stand:** wieder aufgenommen 2026-09-14 — der User hat die Zurueckstellung
aufgehoben. Regel und Messung unten gelten unveraendert: **Rueckbau statt
Umfaerben**. Vorgeschichte: am selben Tag zurueckgestellt, der damals bereits
angewandte Codemod war vollstaendig zurueckgenommen worden (119 Dateien).
**Dateibesitz:** `docs/agent-ops/slices/DESIGN-STATUS-COLORS-020.yaml`, dieser
Abschnitt, Dateien unter `packages/frontend-web/src` mit rohen Palettenklassen.

**Leitbild (SAP Fiori, Semantic Colors):** Die semantischen Farben sind fuer
**Zustand und Kritikalitaet** reserviert. Ikonen im Inhaltsbereich **erben die
Textfarbe**; farbig werden sie nur als Statusanzeige. Farbe darf nie der
einzige Traeger einer Information sein.

**Der Befund widerspricht … (gekuerzt; Volltext unter DESIGN-STATUS-COLORS-020 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## DESIGN-STATUS-COLORS-018 - in arbeit

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Von:** Welle 4 aus DESIGN-STATUS-COLORS-017. **Owner:** Claude Code.
**Stand:** in arbeit 2026-09-13, geclaimt durch Claude Code.
**Ziel:** Den Restbestand roher Palette-Statusfarben schliessen — Hinweisboxen,
sonstige getoente Flaechen, Ikonflaechen und die zurueckgestellten Tabellen.
**Dateibesitz:** `docs/agent-ops/slices/DESIGN-STATUS-COLORS-018.yaml`, dieser
Abschnitt, `components/ui/callout.tsx` (neu), `components/ui/alert.tsx` und
Dateien unter `packages/frontend-web/src` mit rohen Status-Flaechenklassen.
**Abgrenzung:** RESTFEHLER-20260911 (Cursor) haelt `lib/api/produktion.ts` und
`pages/produktion/mischfutter-produktion.tsx` im geteilten Arbeitsbaum — beide
fasse ich nicht an, solange der Slice laeuft.
**Abnahme:** Callout vorhanden und variantengleich mit Alert, Bloecke auf 0 bzw.
begruendet ausgenommen, `tsc --noEmit` exit 0, Vitest identisch zur Baseline.

**Messung … (gekuerzt; Volltext unter DESIGN-STATUS-COLORS-018 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## DESIGN-STATUS-COLORS-015 - in arbeit

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Von:** Aufgeschobener Sweep aus dem Frontend-Design-Audit, aufgenommen waehrend
der Wartezeit auf den Dependency-Graph-Refresh in SECURITY-ARCHIVE-DEPS-20260910.
**Owner:** Claude Code. **Stand:** in arbeit 2026-09-10.
**Ziel:** Rohe Palette-Statusfarben durch die theme-bewussten Utilities
`text-status-success|warning|error|info` ersetzen (Welle 1: eindeutige Faelle).
**Dateibesitz:** `docs/agent-ops/slices/DESIGN-STATUS-COLORS-015.yaml`, dieser
Abschnitt und ausschliesslich Dateien unter `packages/frontend-web/src` mit
rohen Status-Textklassen ohne `bg-`/`border-`-Begleiter.
**Abgrenzung:** Codex' Arbeitsstand umfasst `package.json`-Manifeste,
`docker-compose.yml`, Inventardokumente und Meridian-Builder/Runtime — **keine
einzige Datei unter `packages/frontend-web/src`**. Vor dem Commit erneut geprueft.
**Abnahme:** Welle-1-Vorkommen auf 0, TypeScript und Vitest gruen,
Badge-Tripel … (gekuerzt; Volltext unter DESIGN-STATUS-COLORS-015 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## L3-JOURNAL-SOURCE-20260910 - in arbeit

Meilenstein: M3 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Von:** User-Auftrag zur Parallelaufgabe fuer Claude Code.
**Owner:** Claude Code.
**Stand:** in arbeit 2026-09-10, geclaimt durch Claude Code.

**Ziel:** HTTP 500 bei `GET /api/v1/journal-entries/` an der Ursache beheben:
der Lesevertrag lehnt vorhandene fachliche `source`-Werte ab.

**Dateibesitz:** `app/api/v1/schemas/finance.py`, falls erforderlich
`app/api/v1/endpoints/journal_entries.py`, neue fokussierte Journal-Source-Tests,
dieser Abschnitt, eigene Slice-YAML und eigener Abnahmebericht. Bestehende
Buchungsservices, historische Migrationen und Buchungsdaten nur lesen.
Weitere Dateien erst nach Abstimmung ueber diesen Abschnitt.

**Abnahme:** Reale Journal-Liste HTTP 200; vorhandene Herkunft unveraendert
sichtbar; Regressionen fuer fachliche Quellen und weiterhin ungueltige
Schreibeingaben; vorhandene Journal-Tests gruen; isolierter Commit + Push.

**Risiken:** Keine historische … (gekuerzt; Volltext unter L3-JOURNAL-SOURCE-20260910 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## ADDRESS-VALUE-OBJECT — kanonisches Adressmodell (P2-Fundament)

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Von:** Claude
**Owner:** Claude
**Stand:** in Arbeit 2026-07-05 — kanonisches Adress-Value-Object `app/core/address.py` (Alias-Normalisierung country/countryCode/plz/zip/ort/…, Freitext- und JSON-String-Parsing, Geo lat/lon), bidirektionale Adapter (flach↔VO, JSONB↔VO), 21 Unit-Tests; ADR-038; erste Adoption in customer_service.py (Ad-hoc-Alias-Handling ersetzt). Nicht-brechend: Bestandsspeicherformen bleiben, Migration schrittweise ueber Adapter (Plan im ADR).
**Ziel:** Adressmodell-Vereinheitlichung (vom User angestossen) — eine kanonische Repraesentation statt flach-vs-JSONB-Divergenz.
**Dateibesitz:** `app/core/address.py`, `tests/test_address_value_object.py`, `docs/adr/adr-038-address-value-object.md`, `app/services/customer_service.py`, `mkdocs.yml`.
**Abnahme:** VO-Tests + customer-Tests gruen; ADR-Nav aktuell; Doku-Drift 0.

## A7-RESPONSE-MODEL-TYPING — API-Vertragshaertung + PII-Praevention

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Von:** Claude
**Owner:** Claude
**Stand:** in Arbeit 2026-07-05 — 55 untypisierte Routen mit response_model versehen (66->14, 99,6%), CI-Schwelle 80->20 gezogen; OpenAPI-Spec regeneriert. PII-Praevention: scripts/check_no_pii_data.py (Muster+Inhalt) in pre-commit + CI-Path-Guard, Art.-33-Meldeentwurf entfernt (Vorfall vom Verantwortlichen als nicht meldepflichtig eingestuft). SQL-S608-Review abgeschlossen (artifacts/appsec-s608-review.md): 121 Stellen musterbelegt sicher (Identifier aus Literalen/festen Listen/Pydantic-Whitelist, Werte gebunden).
**Ziel:** SPEC-P1-06 (response_model-Gate absenken) + SPEC-P0-04-Praevention (kein erneuter Lead-Daten-Push).
**Dateibesitz:** `app/api/v1/endpoints/*.py`, `.github/workflows/quality-gate.yml`, `scripts/check_no_pii_data.py`, `scripts/run-staged-checks.cjs`, `.pii-guard-allow.txt`, `docs/schnittstellen/openapi.json`.
**Abnahme:** … (gekuerzt; Volltext unter A7-RESPONSE-MODEL-TYPING in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## AUDIT-1/2/5 — ISO-27001-/SOC-2-Readiness + Audit-Orchestrator

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Von:** Claude
**Owner:** Claude
**Stand:** in Arbeit 2026-07-05 — `config/audit/iso27001-annex-a-matrix.yaml` (93/93 Controls: 33 conform, 12 minor, 48 external_gate, 0 offener major) und `config/audit/soc2-tsc-matrix.yaml` (CC1-CC9/A1/C1/PI1) angelegt; SOC-2-Profil in `simulate_external_assessors.py`; `scripts/check_audit_matrices.py` (fail-closed Vollstaendigkeits-/Konsistenzcheck) und `scripts/aggregate_audit_dashboard.py` (Ampel je Standard, external_gates nie als bestanden) neu; Orchestrator-Workflow `.github/workflows/audit-simulation.yml` (nightly + Release-Tag).
**Ziel:** AUDIT-1 (ISO Annex-A-SoA 93/93 mit Verdikt), AUDIT-2 (SOC-2-TSC-Matrix + Profil), AUDIT-5 (maschinenlesbares Dashboard). LLM-/Agenten-Zugriffe als eigenes Risiko erfasst.
**Dateibesitz:** `config/audit/*.yaml`, `scripts/check_audit_matrices.py`, `scripts/aggregate_audit_dashboard.py`, … (gekuerzt; Volltext unter AUDIT-1/2/5 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## SPEC-P0-04-PII-REMEDIATION — Repo-Hygiene & PII-Bereinigung

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Von:** Codex
**Owner:** Codex
**Stand:** reserviert 2026-07-02 — Fortsetzung der bereits begonnenen PII-/Repo-Hygiene-Remediation auf Branch `fix/pii-remediation`.
**Ziel:** SPEC-P0-04 aus dem Production-Readiness-Audit abschliessen: PII-/Tmp-/Build-Artefakte entfernen, `.gitignore` haerten, gitleaks-Baseline auditieren, History-Purge-Plan und DSB-Bewertung dokumentieren.
**Dateibesitz:** `.gitignore`, `.gitleaks-baseline.json`, `scripts/purge_pii_history.sh`, `artifacts/pii-remediation-report.md`, `docs/project-context/open-gaps-and-known-issues.md`, `docs/agent-ops/slices/SPEC-P0-04-PII-REMEDIATION.yaml`, `docs/agent-ops/active-workboard.md`.
**Abnahme:** Arbeitsbaum enthaelt keine getrackten PII-/Tmp-/Build-Artefakte aus SPEC-P0-04; Scan-Ergebnisse und DSB-Bewertung liegen in `artifacts/pii-remediation-report.md`; History-Purge-Plan ist dokumentiert; Slice-Verify und relevante … (gekuerzt; Volltext unter SPEC-P0-04-PII-REMEDIATION in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## UIX-047 — AP-Freigabe CommandEndpoint + Bestätigungsdialog-Fortsetzung

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Von:** Cursor Agent
**Owner:** Cursor Agent
**Stand:** in arbeit 2026-07-01 — `freigeben` für `finance/ap-invoice` mit Stub-Endpoint `/api/v1/finance/ap/invoices/{entity_id}/actions/freigeben` verdrahtet; folgt auf UIX-046 (neue_bestellung, mahnen, AlertDialog).
**Ziel:** Weitere gestubte Actions schrittweise auf `commandEndpoint` umstellen — AP-Freigabe als nächster P2-Kandidat mit `requiresConfirmation`.
**Dateibesitz:** `app/api/v1/endpoints/ap_invoices.py`, `app/core/screen_definitions.py`, `tests/test_uix046_048_command_endpoints_safety.py`.
**Abnahme:** pytest UIX-046/048-Suite grün inkl. freigeben-Contract-Tests.

## STUDIO-BELEG-THEME-20261016 - in arbeit, Codex

Meilenstein: M1 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex. **Nutzerauftrag:** Gemeinsame Belegmasken mit versionierten Varianten vollstaendig Studio-faehig machen; Themeuebernahme und Lesbarkeit einschliesslich Dunkelansicht pruefen. **Dateibesitz:** additive Belegvarianten-Vertraege und deren Anbindung an bestehende Studio-Definitionen; gezielte zentrale Theme-Kontrastvertraege und E2E-Abnahme, eigene Doku. Bestehende Claims CI-SOURCE-REPAIR und STUDIO-NATIVE-BASELINES bleiben bei Codex. **Abnahme:** reproduzierbare Basis-/Variantenbindung, keine Freigabeumgehung; globale Themes statt Masken-Sonderfarben, nachgewiesene Text-/Bedienelementkontraste und reale Screenshots. Keine neuen DB/Container. Fremde Arbeitskopien bleiben geschuetzt.

**STUDIO-BELEG-THEME Teilabnahme Kontext:** Nutzerhinweis umgesetzt: Ernte-Abrechnungssteuerung nur im ausdruecklichen Fachzugang harvestControls=1; keine permanente Zeile im allgemeinen … (gekuerzt; Volltext unter STUDIO-BELEG-THEME-20261016 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## MIGRATION-PARITY-REPAIR-20261022 — reserviert, Codex

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex. **Ziel:** Nachgewiesene Funktionsverluste und falsche Runtime-/Freigabezaehlung aus abgeschlossenen Cursor-Batches korrigieren. **Besitz:** DATEV-ScreenDefinition (eigener gezielter Builder statt generischer Nebenbuchliste), zentraler deklarativer Download-/Formularvertrag und zugehoerige Renderer/Compiler; Masken-Routen-Inventar und made_by_studio_gates ausschliesslich Nachweisstrenge fuer Legacy-Wrapper; neue gezielte Regressionen, QA/Workboard und betroffene generierte Projektionen. Adaptive Workspace, Touren/Training/Bestellvorschlag und fremde WIP bleiben unberuehrt. Keine neue DB/Container, keine pauschalen Reverts oder erfundenen Freigaben. **Abnahme:** echter DATEV-Transport mit Typauswahl/CSV/Fehler/Download, Wrapper allein ergibt nie Runtimefreigabe, Feld-/Transportparitaet und aktuelle Tests. Isolierte HEAD-Ansicht artifacts/migration-repair-source; alte … (gekuerzt; Volltext unter MIGRATION-PARITY-REPAIR-20261022 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## MIGRATION-CI-REPAIR-20261023 — reserviert, Codex

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex. **Ziel:** Bestaetigte PR38-CI-Regressionsursachen schliessen, keine Test-/Baseline-Abschwaechung. **Dateibesitz:** screen_definitions.py samt Registrierung und Agentenmetadaten; TanStack-Routengenerator/geschlossener Suchparametervertrag; generierte Nachweise, betroffene Slice-YAML nur CI-Metadaten, eigene QA/Handshake. Abhaengigkeiten zuerst offiziell verifizieren. **Abnahme:** bestehende795 Masken-Sicherheitsfaelle, frisch generierte Routentypen und Generatorchecks; Folge-CI. **Risiken:** aktive Workspace-Quelldateien bleiben fremdem Claim vorbehalten; keine neue DB/Container/Reset.

**MIGRATION-CI-REPAIR Erweiterung:** doc_drift_report.py nur echte transitive Importerreichbarkeit pruefen (positive und negative Regressionen, keine Suffix-Ausnahme fuer Legacy); requirements.txt nur offiziell bestaetigte Updates GitPython3.2.1/Black26.10.1 und zusammenpassende … (gekuerzt; Volltext unter MIGRATION-CI-REPAIR-20261023 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## SECURITY-PATCHES-20261023 — reserviert, Codex

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Owner:** Codex. **Ziel:** Drei offiziell bestaetigte neue Sicherheitsluecken ohne die unvollstaendige Maskenmigration auf main schliessen. **Dateibesitz:** requirements.txt nur GitPython/Black/kohaerente OpenTelemetry-Gruppe; neuer isolierter OTel-Kompatibilitaetstest und QA, eigener Workboard-Absatz. **Abnahme:** frische Gesamtaufloesung155 Pakete ohne bekannte Schwachstellen; echte HTTP-/SQL-Spans ohne externe Uebertragung. Keine neue DB, kein Container, kein Reset; bestehende Rollen- und Mandantenvertraege unveraendert.

**SECURITY-PATCHES-20261023 abgeschlossen:** Drei bestaetigte Advisory-Korrekturen als kohaerente Versionsgruppe. Frische155er-Gesamtaufloesung auditiert ohne bekannte Schwachstellen; echter HTTP-/SQL-Trace-Kompatibilitaetstest gruen. Keine Ausnahme, keine Datenbank-/Docker-Ressource. QA docs/quality-assurance/security-patches-20261023.md. Keine Aktivierung der … (gekuerzt; Volltext unter SECURITY-PATCHES-20261023 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## RUNTIME-SOURCE-SYNC-20261023 - reserviert, Codex

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Ziel:** laufende lokale Frontend-/Backendfassung mit nachgewiesenem Code synchronisieren. **Besitz:** lokales Frontendbuild/Neuerstellen ohne andereServices; gezielte Wiederanbindung belegter bereitscommitteter Dokumenten-Sicherheitsvertraege in app/documents/repository.py (aktueller Rootdiff entfernt ausschliesslich Exceptions, insert-only, Zeilensperre, Tenantunveraenderlichkeit und generische Fehlerlogs; keine neueFunktion). VorherigeArbeitskopie lokalgesichert. Keine blindenFremdreverts, keinDBreset. Backendimportpreflight vorNeustart; regulaererSchema-Vorlauf separat. QA local-frontend-refresh-20261023.md.

**RUNTIME-SOURCE-SYNC Zwischenstand:** Frontend auf3000 ersetzt, Image9dc7e71d9f4f healthy/HTTP200, neueStartflaeche real sichtbar. Vier Backendimport-Vertragsbrueche und belegte Auth-/Dokument-Rechteruecknahmen gezielt auf veroeffentlichten Stand synchronisiert, Inbox-Mount … (gekuerzt; Volltext unter RUNTIME-SOURCE-SYNC-20261023 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-CANONICAL-BINDINGS-20261023 - reserviert, Codex

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: reale falsche Stamm-API-/Feldbindungen und OpenAPI-Pfadtemplateabgleich zentral korrigieren. Besitz: app/core/screen_definitions_stamm.py ausschliesslich Hausbank, Mengeneinheit, individuelleArtikelnummer, Anlage; app/services/made_by_studio_gates.py nur OpenAPI-Routenmatching; jeweils eigene gezielte Regressionstests und QA. Aenderungen in gepruefter PR38-Ansicht, Root nur nach Diffpruefung synchronisieren. Bestehende Domainrouter/Rechte bleiben fuehrend, keine Ersatzendpunkte oder fingierte Migrationsfreigabe. Fachliche Editvertraege nur bei vorhandenem autorisierten Domaincommand; fehlende Paritaet sichtbar lassen. Kein DB/Container/Reset, keine fremden Workspace-Dateien.

**STUDIO-CANONICAL-BINDINGS API-Erweiterung:** Zwei echte Detail-Lesevertraege fehlen bisher vollstaendig. Besitz eng um GET in bestehenden artikel_mengeneinheiten.py und individuelle_artikelnummern.py … (gekuerzt; Volltext unter STUDIO-CANONICAL-BINDINGS-20261023 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-CLOSURE-PARALLEL-20261023 - reserviert, Codex Lead

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nutzerklarstellung: Commit/Push bleiben freigegeben; die angehaengte NoCommit-Notiz war keine neue Nutzervorgabe. Ziel bleibt vollstaendige Studio-Funktion und CLI-Migration aller Masken mit echter Fachparitaet.

- API-CONTRACTS, delegierter Owner api_contracts:22 offene Datenquellenvertraege; Besitz betroffene bestehende Domainrouter sowie ScreenDefinition-Builderdateien stamm/capture/batch13/batch15 nur fuer die22 konkret gemeldeten Bindungen. Asset-Projektion mit folgendem Slice abstimmen. Vorhandene Fachmodelle/Rollen/Commands fuehrend, kein erfundenes Mapping und kein paralleles CRUD.
- RUNTIME-EVIDENCE, delegierter Owner runtime_closure:54 konkret gemeldete Runtimewege; Besitz betroffene Frontend-Seiteneinstiege und zentrale Runtime-Evidenzanalyse samt eigenen Tests. Keine generischen Legacy-Wrapper/unsichtbaren Runtime-Alibis, kein Verlust bestehender Fachfunktionen. Gesperrte … (gekuerzt; Volltext unter STUDIO-CLOSURE-PARALLEL-20261023 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## ADAPTIVE-WORKSPACE-REVIEW-20261023 - reserviert, Codex

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nutzerauftrag: acht ausdruecklich benannte Root-Dateien pruefen (Framework/Events-Doku, Agrar-/SSE-Tests, live-signals, Workspaceevents, QualityAPI undRepository). Besitz nur neuer QA-Bericht und eigene Reproduktionsartefakte; keine fremden produktiven Workspacequellen aendern. Abnahme: belegte Befunde priorisieren, Tests gegen Root ausfuehren, bestehenden valeo_probe nur eigeneTestzeilen/keinReset. Studio-Slices bleiben eigenstaendige laufende Integration; Subagenten durch Nutzungslimit gestoppt, uncommittete Ergebnisse bewahren.

**ADAPTIVE-WORKSPACE-REVIEW Ergebnis:** Pruefung abgeschlossen,9 Befunde offen (5P1/4P2).76Unit+3echtePG+4Frontendfaelle bestanden; eigeneReproducer bestaetigen405,Nullwertverlust,SSEvorCommit,Retryverlust undNATS-Umschlagbruch. Keine derachtQuellenkorrigiert, keinReset/neueDB. QA adaptive-workspace-review-20261023.md; … (gekuerzt; Volltext unter ADAPTIVE-WORKSPACE-REVIEW-20261023 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## ADAPTIVE-WORKSPACE-CLOSURE-20261024 - reserviert, Codex Lead

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nutzerauftrag: sieben restliche Reviewbefunde AW-R01/02/03/04/05/06/09 schliessen. Besitzer api_contracts: QualityAPI, QualityRepo, benoetigte Servicevertraege und eigene Tests fuer Tokenurheber, Pflichttenant/Parent, atomare Finalisierung/Updates und echten Listen-GET. Besitzer runtime_closure: live-signals.ts und eigene Wiederverbindungs-/Queue-/Auth-Tests. Lead: Outbox/NATS/IntegrationEvent und Workspace-Umschlag nur fuer Commitgrenze und tatsaechlichen Tenanttransport, eigene Serializer-/Rollbacktests, Integrationsartefakte/Doku/Commit/Push. Fremde Vorarbeiten erhalten; keine konkurrierende Bearbeitung derselben Abschnitte, Finalize-Outboxparameter mit API-Owner abstimmen. Keine neueDB/Container/Reset. Bestehender valeo_probe nur nach Status und eigene Daten/Rollbacks. Ziel: sieben belegte Befunde mit negativen und positiven Vertragen; keine fingierte … (gekuerzt; Volltext unter ADAPTIVE-WORKSPACE-CLOSURE-20261024 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## PR38-CI-FOLLOWUP-20261024 - reserviert, Codex Lead

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nachlauf auf7bc7e37fa: CI rot in Migration/Backend/Frontend und Dependencysecurity. Enger Besitz: api_contracts diagnostiziert und repariert fehlende Alembic-Vorgaenger und frisches Schema-/Inventardrift; entity_projection uebertraegt bereits abgenommene Securityfixes aus PR39 nach exaktem Quellenvergleich, keine Paketpauschalupdates; runtime_closure diagnostiziert echte Frontendregressionen und veraltete Strukturtests, entfernt keine fachliche Abnahme. Lead integriert, testet und aktualisiert Artefakte/QA/GitHub. Alle Edits in repair-view; Root nur nach Diffreview. Keine neueDB/Container/Reset, kein Tabellenkatalog aus unvollstaendiger lokaler DB. Vorhandene restliche Studioarbeit bewahren.


**PR38-CI-FOLLOWUP Migrationsmeilenstein:** Fehlende dms_inbox_tenant_20261022 wiederhergestellt; Singlehead und Syntax geprueft,437 Migrationsdateien inhaltlich identisch zum separat abgenommenen … (gekuerzt; Volltext unter PR38-CI-FOLLOWUP-20261024 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## PENDING-INTEGRATION-20261024 - reserviert, Codex Lead

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
### NATIVE-DETAIL-ROUTE-PARITY-20261027 - reserviert, native_batch_contracts

Ziel: 19 historische Detailmasken-Routen gegen kanonische ScreenDefinitions und getrennte Anlage-/Entity-Vertraege pruefen; 17 nachgewiesene falsche oder unregistrierte Bindungen gezielt reparieren. Besitz nur der betroffenen Page-Wrapper, drei eigene Routenvertragstests, eigene Builder-Fixtures/Paritaets- und Mounttests sowie QA. Abnahme: bestehende Fach-/Create-Wege bleiben erhalten; mindestens zwei echte geroutete Mounts fuer Entity und Create; keine pauschale Native-Freigabe fuer fachlich offene Routen. Risiken: Customer-360 ist moeglicherweise Cockpit statt editierbare Detailmaske; fachlich unpassende Ersatzdefinitionen nicht umetikettieren. Keine Backend-, RLS-, Inbox-, Vite-, DB- oder Migrationsaenderung; nur private View.

Nutzerauftrag: alle uebrigen offenen Aenderungen commit-/pushfaehig … (gekuerzt; Volltext unter PENDING-INTEGRATION-20261024 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-CRM-ACTIVITIES-RUNTIME-20261029 — reserviert, Codex Lead

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Ziel:** Aktivitätenliste funktional über Studio bedienen, ohne Suche, Status-/Typfilter, Meine Aktivitäten, Kalenderauswahl, Kennzahlen, CSV, Neu- und Detailnavigation zu verlieren.
**Dateibesitz:** `app/core/screen_definitions_listen.py` nur Aktivitätenbuilder; `app/services/studio_list_contracts.py`; neuer gemeinsamer Listenpreset-Service; `app/services/mask_table_query.py`; `app/api/v1/schemas/mask_data_contracts.py`; Query-Adapter in `mask_screen_definition.py`; `app/api/v1/schemas/crm.py` nur Activity-Leseprojektion; zentrale Frontend-Schema-/RenderPlan-/Listenruntime-/Preset-Renderer; `pages/crm/aktivitaeten.tsx`; CLI-Datenleseoptionen; eigene gezielte Tests/Fixtures; abgeleitete Vertragsartefakte und CRM-/QA-/Handoff-Dokumentation. Andere Builder/Schreibwege bleiben unverändert.
**Vertrag:** Vordefinierte Auswahlfilter werden serverseitig aus registrierten Metadaten auf den … (gekuerzt; Volltext unter STUDIO-CRM-ACTIVITIES-RUNTIME-20261029 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## CRM-ACTIVITY-CANONICAL-20261029 — reserviert, Codex Lead

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nutzerauftrag: Vereinheitlichung autonom nach Best Practice uebernehmen. Fuehrendes bereits beschlossenes Modell ist domain_crm.activities (Migration mandant_finanz_crm_20261007); keine neue Parallelquelle. Besitz: activities.py/API-Activity-Schemas; app/crm/router.py nur Aktivitaeten-CRUD/Timeline/Export; Activity-Infrastrukturmodell; neuer gemeinsamer CRM-Aktivitaetenservice/Commandvertrag; CRM-360 und MCP-Adapter nur Aktivitaetenanlage; neuer additiver Alembic-Schritt/gezielte Pruefstandabnahme; betroffene Listen-/Objektdefinitionen und CRM-Frontend-Service/Seiten; enge Tests, Generatoren, Architekturentscheidung und Doku. Der lesende Inventaragent bearbeitet keine Dateien. Die drei Nebensammlungen muessen echt gespeichert und atomar veraendert werden; Mandant/Urheber ausschliesslich verifiziert, Versionsschutz/Idempotenz/Audit/Outbox fuer Writes. Vorhandene Fremddaten nicht still … (gekuerzt; Volltext unter CRM-ACTIVITY-CANONICAL-20261029 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-RUNTIME46-CLOSURE-20261029 — reserviert, Codex Lead

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nutzerauftrag: verbleibende46Runtimepunkte funktional schliessen; vorhandene Migrationen und Nachweise wiederverwenden. Keine reine Marker-/Wrappermigration. Pflicht: bestehende Bedienwege, Rollen/Mandant, Fehlerzustand, Fachaktionen und Datenparitaet; echte Aliase nur nach belegter kanonischer Zielbindung stilllegen. Lead besitzt Integration/Artefakte/Gates/CI/SQLfenster, neue gemeinsame Verträge ausser unten und Statusdoku.

**Unterclaim WORKFLOWS, runtime_workflows:** neun pages/workflow/flow-spine-*.tsx ohne Studioseite; app/core/screen_definitions_domain_batch15.py nur neun flowSpineBuilder; components/workflow/FlowSpineWorkspace.tsx nur echte Aufteilung bestehender Funktion; neue FlowSpine-Runtime/Renderer. Zentraler Besitz schema.ts, render-plan/types.ts/schema-compiler.ts, useUniversalMaskRuntime, UniversalMaskRenderer und UniversalNativeCockpitPage ausschliesslich … (gekuerzt; Volltext unter STUDIO-RUNTIME46-CLOSURE-20261029 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-RUNTIME46-RESUME-20261030 — reserviert, Codex Lead

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Fortsetzung des ausdruecklichen Nutzerauftrags aus PR90. Isolierter Checkout auf 662dfaed; gemischte Root-/Indexaenderungen bleiben unangetastet. Besitz: bereits begonnene Runtime46-Vertraege, Angebots-/Lieferlisten-Dateiimport/Druck/Arbeitsfokus, Annahme/Waage-Spezialrenderer und eng notwendige Mandanten-/Referenzschutzkorrekturen; Tests, Generatorprojektionen und Statusdoku. Bestehende Unterclaims werden im Nutzerauftrag fortgesetzt, keine doppelte Neuentwicklung. Teilung: Lead gemeinsame Integration/Backend/Sicherheit/Tests/Git; sales_integration NativeListPage/Listenbedienung samt eigenen UI-Tests; intake_integration spezialisierte Annahme-/Waagenoberflaechen, feste Definitionen und Seiten. Kein fremder aktiver Workspacebesitz, keine neue DB/Container/Reset. Altzeilen ohne belegten Mandanten bleiben NULL und gesperrt. Abschluss erst mit benannten Testbelegen; strukturelle Gates und … (gekuerzt; Volltext unter STUDIO-RUNTIME46-RESUME-20261030 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-UMBAU-RUNTIME46 — offen (Nutzerentscheidung 02.11.2026: Weg 2)

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Der Codex-Stand ca50c46f7 ("runtime46") brachte Seiten an der Studio-Regel vorbei. Sie stehen seit
CI-DAUERROT-20261102 als dokumentierte Altlast in config/mask_studio_ratchet.json und werden in einem
eigenen Auftrag zu Studio-Masken umgebaut (danach Ratsche wieder senken).
Handgebaute Routen (20): admin/control-center, admin/webhooks, annahme/abrechnung, annahme/lkw-registrierung,
annahme/qualitaets-check, annahme/warteschlange, einkauf/lieferschein-erfassung, finance/bank-abgleich,
finance/dunning, finance/mahnlauf, finance/mahnwesen, lager/materialfluss, mahnwesen/mahnlauf,
studio/workspace-composition-preview, verkauf/kunde/:id, verkauf/kunde/neu, verkauf/kunden-stamm/:id,
waage, waage/neu, waage/wiegungen.
Altmuster-Routen (5): admin/control-center/agent-ops, admin/control-center/superglue, admin/screen-studio,
annahme/rohware, einkauf/bestellungen/neu.
Nicht deklarierte … (gekuerzt; Volltext unter STUDIO-UMBAU-RUNTIME46 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## PSM-ZULASSUNGEN-20261104 — in Arbeit, Codex

Meilenstein: M3 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: PSM-Zulassungen ueber mandantengebundenen echten PSM-Leseweg und native Studio-Liste; ersetztes Register nur nach sicherer Datenpruefung entfernen.
Dateibesitz: PSM-Projektion und Schema, betroffene Studio-Definitionen und UI-Verbraucher, zugehoerige Migration, gezielte Tests sowie QA/Meridian-Doku. Integration nach Batch 8/9 durch Lead.
Abnahme: typisierter Feldvertrag, Mandant aus Anmeldung, keine erfundenen Werte, native Maske, Entfernung der ersetzten Tabelle ohne CASCADE, gezielte Tests und Generatoren im koordinierten Fenster.
Risiken: Verbraucher vor Tabellenentfernung vollstaendig pruefen; ungemergte Migration ausschliesslich transaktional pruefen; keine neue Testdatenbank.


PSM-ZULASSUNGEN Zwischenstand: lokale PSM-Projektion und native Liste vorbereitet. Der Ablaufzaehler betrachtet alle Seiten in der Betriebszeitzone. Nach vorrangiger Nutzerentscheidung vom 04.11.2026 … (gekuerzt; Volltext unter PSM-ZULASSUNGEN-20261104 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## GESAMTINTEGRATION-20261105 — lokal abgenommen, Codex Lead

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: die vollstaendig gruenen PR-Staende 104/106/108/110/111/112 in einem eigenen pruefbaren Integrationszweig zusammenfuehren. Basis PSM 2a43fd5dc einschliesslich der Tabellenstilllegungen; zusaetzlich Omnibox 29c5e8ea0, Preis 059c7e744 und VVVO d991345d7. Besitz: Konfliktaufloesung dieser eigenen Slices, generierte Projektionen, gemeinsame gezielte Pruefung und eigener QA/Handshake. Keine fremden Hauptbaumdateien uebernehmen, keine Live-Migration oder Rechtevergabe. Abnahme: gemeinsame Verträge, Artefaktabgleich und Gesamt-CI; Branch-Schutz bleibt aktiv, reguläre Review erforderlich.

## CODEX-ROLLOUT-INTEGRATION-20261104 — reserviert, Codex

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: Nutzerauftrag aus codex-uebergabe-20261104 umsetzen. Zuerst PR #102 mit gruenen
Pruefungen integrieren, main nach develop; danach #103 auf main nachziehen, Generatoren
und CI pruefen, integrieren und main erneut nach develop. Anschliessend A bis F der
Uebergabe fachlich schliessen, ohne bestehende Nachweise erneut zu implementieren.
Dateibesitz dieses Integrationsclaims: eigener Worktree artifacts/rollout-integration-20261104,
Integrationsnachweise und dieser Workboard-Anhang; kein fremder Hauptbaum-Dateibesitz.
Abnahme: Commit-genaue CI-Nachweise, keine abgeschwaechten Tests, keine neue Testdatenbank,
keine ungemergte Migration auf dem Pruefstand gestempelt. Fachslices werden vor Umsetzung
separat mit Dateien und Abnahme reserviert. Stand: #102 Security/Frontend/Smoke gruen,
Backend und Test & Lint laufen; #103 basiert noch auf #102. A/B/C/E/F im Code bestaetigt offen.

## VVVO-MANDANTENFILTER-20261105 — lokal abgenommen, Codex Lead

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: VVVO-Pruefung und Sachkunde-Status nur per ID und Mandant lesen; das VVVO-Update eigenstaendig mandantenfiltern und Erfolg nur bei tatsaechlich aktualisierter Zeile melden. Fremde und unbekannte IDs antworten gleich. Dateibesitz: app/services/compliance_vvvo_sachkunde_service.py, eigener PostgreSQL-TEMP-Verhaltenstest, QA/Handshake und dieser Anhang im Branch codex/vvvo-mandantenfilter-20261105. Abnahme: eigene Aenderung, fremde/fehlende ID, unveraenderte Fremddaten und simuliertes Umhaengen zwischen Lesen/Schreiben; bestehende Service-Tests. Keine Registerzusammenfuehrung, Rollenfreigabe, produktive Migration oder neue DB. Pruefstand valeo_probe nach Statuspruefung, nur eigene TEMP-Daten mit Rollback; dies beweist SQL-Praedikate, keine JWT-/RLS-Gesamtfreigabe.

Abnahme VVVO-MANDANTENFILTER: 21 Tests bestanden, Gegenprobe alter Service 3 gezielt rot/1 gruen. Eigene TEMP-Daten … (gekuerzt; Volltext unter VVVO-MANDANTENFILTER-20261105 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## VVVO-FAELLIGKEIT-20261105 — lokal abgenommen, Codex Lead

Meilenstein: M1 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Folgeslice im eigenen VVVO-Zweig: Faelligkeitsliste muss ueberfaellige und heute/bis Stichtag faellige eigene Eintraege sowie offene Eintraege ohne Prueftermin zeigen. NULL bedeutet Klaerungsbedarf, keine behauptete erfolgte Pruefung. Mandantenfilter bleibt fuer die gesamte ODER-Gruppe verbindlich; Stichtag aus business_today statt Serverdatum. Dateibesitz: list_faellige_vvvo_pruefungen im vorhandenen Service, zugehoeriger PostgreSQL-TEMP-Test, abgesenkte Business-Time-Baseline und eigene QA/Handshake. Abnahme: Grenzen 0/30 Tage, NULL, Ueberfaelligkeit, Fremdmandant und Gegenprobe; keine neue API/Maske/Migration.

VVVO-FAELLIGKEIT Recherche-Nachtrag: Nutzer fragt nach Einsatzpflicht der VVVO-Nummer. Besitz zusaetzlich eigene Fachnotiz docs/quality-assurance/vvvo-nummer-fachgrundlagen-20261105.md. Primaerquellen ViehVerkV §26, QS Futtermittelwirtschaft 2026 §4.20.1, Niedersaechsische … (gekuerzt; Volltext unter VVVO-FAELLIGKEIT-20261105 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## STUDIO-WEBHOOKS-NATIVE-20261105 — in Arbeit, Codex Lead

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nutzerauftrag: restliche Masken auf Studio-made, fehlende Funktionen zentral im Designer ergaenzen, CLI/MCP nutzen. Erste Familie Webhooks: echte native Worklist statt Intake-Spezialhost; Anlage, Suche, Abmeldung, Zustellprotokoll und Rollen-/Mandantengrenzen erhalten. Zentrale neue Deklaration readView fuer rein lesende zeilenbezogene Tabellen im Dialog; kein seitenspezifisches Formular. Lead besitzt schema.ts, NativeListPage, neuen zentralen Renderer/Frontendtests, Admin-Builder/Webhook-Seite, Ratschen und Generatoren/QA. Unterclaim readView-Vertrag besitzt nur neue enge Backendvalidierung samt Anbindung in studio_validation.py, CLI-Leseadapter und eigene Tests; keine anderen Dateien oder DB. Agentenwrites bleiben ausdruecklich gesperrt. Abnahme: gleicher GET fuer UI/CLI/MCP, keine Identitaets-/Fremd-URLs, stale Antworten verwerfen, Aktionenrechte vor Aufruf, Geheimnis als Passwort, … (gekuerzt; Volltext unter STUDIO-WEBHOOKS-NATIVE-20261105 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## MCP-ROW-COMMANDS-20261107 — reserviert, Codex Subagent

Meilenstein: Strang A (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Ziel:** Vier Zeilenaktionen mit lokalem Command im MCP-Inventar korrekt und sicher einordnen; CI-Vertrag wiederherstellen ohne abgesenkte Gates. **Dateibesitz:** Generator `scripts/generate_mcp_mask_action_map.py`, belegte fachliche Adapter falls erforderlich, zugehörige Tests, generierte Projektionen, eigene QA/Handshake und dieser Workboard-Eintrag. **Abnahme:** reale Ausführbarkeit und Rechte belegt, Generator- und Vertragstests grün. **Risiko:** `command` allein garantiert keinen MCP-Endpunkt. Keine DB oder Container.

MCP-ROW-COMMANDS-20261107 Erweiterung: HR-Subslice besitzt `app/api/v1/endpoints/training.py`, neuen HR-Fachservice, drei HR-UI-Seiten und zugehörige Tests; Lead des Slices integriert `screen_definitions_capture.py` und Projektionen. Versand: `app/api/v1/endpoints/versandprofile.py`, kanonischer Versandservice, Versand-UI/Tests. Bestehender `valeo_probe` nur nach … (gekuerzt; Volltext unter MCP-ROW-COMMANDS-20261107 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## MCP-ROW-CLI-20261107 — reserviert, Codex Subagent mailbox_replay

Meilenstein: Strang A (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Besitz valeo_cli/cli.py, support.py, gezielte neue CLI-Vertragstests und QA. Ziel volle CLI-Paritaet der vier Zeilencommands: versionierte Eingaben, Idempotenzschluessel bei ungewissem Ausgang erhalten, keine Identitaets-/Mandantenoverrides, bestehende Rollen/Agentenfreigabe beachten. Zentrale Register und ScreenDefinitions verbleiben beim MCP-ROW-COMMANDS-Owner. Keine DB.

## MCP-INVENTUR-COUNT-RELEASE-20261107 — reserviert, Codex Subagent inventory_count_sheet

Meilenstein: Strang A (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
**Ziel:** Inventur-Zählblatt aus bestehender Maskenaktion nur über einen gemeinsamen, versionierten und sicher freigegebenen Fachcommand für UI, REST, CLI und MCP bereitstellen. **Dateibesitz:** zugehörige Inventur-Nebenlauf-Services/Endpoints, `packages/frontend-web/src/pages/lager/inventur-nebenlaeufe.tsx`, passende Tests und eigene QA; zentrale ScreenDefinition, MCP-Registry und Projektionen beim Lead des Slices. **Abnahme:** Mandant/Rollen, atomarer Audit/Outbox, akteur-/payloadgebundene Wiederholung und Kanalparität geprüft; keine DDL oder neue Datenbank, geteilter Prüfstand nur nach Slotkoordination. **Risiko:** bisheriger UI- und Command-Weg unterscheiden sich; bestehender Replayvertrag bindet weder Akteur noch Payload.

## RESPONSE-CONTRACTS-HR-VERSAND-20261107 — reserviert, Codex Subagent row_response_contracts

Meilenstein: Strang A (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Besitz training.py und versandprofile.py, enge Antwortmodell-/Routentests und eigene QA. Acht untypisierte Routen mit realen Antwortvertraegen absichern, keine Gateausnahmen. OpenAPI-Regeneration beim Lead. Keine DB.

## ROW-SERVICE-DOMAIN-MAPPING-20261107 — reserviert, Codex Lead

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Besitz architecture-domain-prefixes.yaml und erzeugter architecture-index.yaml. Neue Dienste command_idempotency→platform, hr_row_delete_commands→hr, versandprofil_commands→logistics im kanonischen Mapping ergaenzen; Vollstaendigkeitsgate unveraendert.

STUDIO-CHANNEL-RELEASE-20261107 Abnahme: Default-Deny bleibt erhalten; explizite Deploymentrollen werden ueber gemeinsamen Binding-Helper in bestehende MCP-Capabilities projiziert. Capability-Test und signierter HTTP/CLI/MCP-SQL-Kanaltest je 1 passed; Scope, Rolle, Confirmation, Tenant, Forgery, Version und Replay geprueft. Probe nach Rollback ohne fremde Sitzungen und Revision ruestlisten_tabelle_20261103 unveraendert. QA studio-channel-release-20261107.md.

## KATALOG-LINEAGE-20261108 — reserviert, Codex Subagent row_response_contracts

Meilenstein: Strang A (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Besitz docs/admin/table-catalog.json und .md, eigene QA. CI-Artefakt13589076577 aus Lauf42410114687/Job128516616359/Head525d3b212 uebernehmen; physische Gleichheit31Schemata/700Tabellen belegt, ausschliesslichLineage. KeineDB/Migration, keineGateaufweichung.

## STUDIO-TEST-LISTEN-FINAL-20261113 — teilweise abgeschlossen, Codex Subagent test_migration_lists

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: groessere Listen-Testgruppe auf echte Studio-Runtime umstellen: neun Agrar-Dateien, betrieb/listen-uix und mask-listen-family-nav. Besitz diese Testdateien, neue gemeinsame Listenverhaltenstests/Fixtures, tests/test_frontend_native_list_fixtures.py und QA studio-test-listen-final-20261113.md. Enge bestaetigte Routingkorrektur packages/frontend-web/src/pages/zertifikate/liste.tsx erlaubt; app/core/screen_definitions_listen.py nur nach erneut belegtem Ziel und Lead-Abstimmung. Keine erfundene Kulturdetailroute. Abnahme: fachliche Navigation/Suche/Export/Aktionen/Rechte, echte Renderer und passende Schema-Fixtures; kein Quelltext-Mimikry und keine Funktionsluecke wegloeschen. Bestehende echte Funktionsluecken separat benennen, erforderliche Erweiterung Lead melden.
AI-Harness: Fachvertrag je Liste aus vorhandenen Wegen und bisherigen gueltigen Erwartungen; Architektur gemeinsame … (gekuerzt; Volltext unter STUDIO-TEST-LISTEN-FINAL-20261113 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## CI-PYTHON-OTEL-20261114 — lokal abgenommen, Codex Subagent ci_dependency_audit

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: aktuelles pip-audit blockiert opentelemetry-api1.45.1 (CVE-2026-126360/GHSA-mf5v-w3w3-f6cg), Herstellerfix1.45.2. Besitz direkte Root-Requirements und nur erforderliche gekoppelte OTel-Pins/zugehoerige Constraints, gezielter Security-Vertrag und QA. Kein Ignore oder Gatebypass. Abnahme: Primaeradvisory und kompatible SDK-/Exporter-Kette, Aufloesung/Imports, ReDoS-Negativ- und validerTrace-Vertrag, aktueller Audit. Keine DB/Container.
AI-Harness: Fach-/Securityvertrag sichere TraceContext-Verarbeitung auch MCP-Metadaten; Architektur bestehende OTel-Instrumentierung, keine Paralleltelemetrie; Daten synthetische Tracewerte; Tests begrenzt auf betroffene Pakete plus Audit; Betrieb keine Vollbuilds/DB; Doku QA/Workboard/Handshake. Externes Gate: Security-Scan auf exaktem Commit.

## CI-STUDIO-PROJEKTIONEN-20261114 — lokal abgenommen, Codex Subagent test_migration_lists

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: drei konkrete rote Backend-Gates auf Main eb42a87fc korrigieren: screen_action_catalog (796/797), screen_list_routes Drift, test_identitaet_je_belegmaske fehlende neue Sortenmaske. Besitz services/ki-usability/app/data/screen_mask_actions.json, config/screen_list_routes.generated.json und tests/test_meridian_beleg_systemweit.py ausschliesslich kanonischer Identitaetseintrag agrar/saatgut/sorte=name. Keine Altlastbaseline erhoehen. Generatoren unveraendert ausser nachweislichem Fehler; passende Generator-/Identitaetstests gezielt ausfuehren.
AI-Harness: Fachvertrag reale Identitaet und aktuelle Kataloge; Architektur vorhandene Generatoren; Daten keine DB; Tests keine PG-/Devtoken-Testfaelle ausfuehren, nur reine Identitaets-/Katalogvertraege; Security keine Freigabe-/Scopeaenderung; Betrieb keine DB/Container/Builds; Doku QA und Lead-Handoff. Externes Gate: CI-Nachlauf, keine … (gekuerzt; Volltext unter CI-STUDIO-PROJEKTIONEN-20261114 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## ACTION-MATRIX-NACHWEIS-20261114 — lokal abgenommen, Codex Subagent test_migration_workflows

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: Nutzerbefund action-matrix-report.md (32 Gaps/38 Aktionen) ehrlich integrieren: zwei green/vier partial sind nur YAML-Status, ohne Aktions-ID/Testfall/Run/SHA-Verknuepfung und mit schwachen/veralteten Tests. Besitz scripts/generate_action_matrix_report.py, generierter Bericht, neue gezielte Generatorvertraege und QA action-matrix-audit-20261114.md. Bestehende acht YAML-Gaps nicht gruenfaerben, keine API-/Browserabnahme vortaeuschen. Abnahme: deklarierte Statuszahlen deutlich von verifiziertem Laufnachweis trennen; Tags/Dateiexistenz duerfen kein bestandenes Ergebnis erzeugen. Nachweisbedarf/konkrete alte-Routen-/Fehlerakzeptanzbefunde dokumentieren; fehlerhafte/duplizierte/ungueltige Matrixeintraege nicht still als gruen behandeln. --check bleibt hart.
AI-Harness: Fachvertrag Nachweis fachlicher Wirkung statt Navigation/503; Architektur bestehende Matrix und Evidencekette, kein … (gekuerzt; Volltext unter ACTION-MATRIX-NACHWEIS-20261114 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## CI-134-NACHLAUF-20261114 — lokal abgenommen, Codex Subagent ci_dependency_audit

Meilenstein: M5 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: konkrete roten Jobs von PR134/e733d8828 beheben (Backend, Frontend, Scanner-Reproduktion). Besitz zunaechst Analyse exakter Logs, danach nur durch Lead zugewiesene eindeutig betroffene Dateien, eigene Tests/QA. Keine Gates/Schwellen senken oder pauschale Wiederholung; bestandene Security-Audits erhalten. Abnahme gezielte Regression und exakter CI-Nachlauf. Keine DB/Container pro Test. Workboard/Integration Lead.

## STUDIO-TEILMENGEN-20261114 — lokal abgenommen, Codex Lead

Meilenstein: M2 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: bestehende DocFlow-Teilumwandlung sicher in der gemeinsamen Studio-Belegmaske bedienbar machen; Versions-/Idempotenz-/Rollen-/Mandantenvertrag erhalten. Dateibesitz app/core/beleg_maske_parent.py, app/services/docflow_belegaktionen.py und nur erforderliche vorhandene Docflow-Adapter/Schema/Runtimekomponenten nach Istpruefung, gezielte Tests, QA/Handbuch/Generatorprojektionen. Keine eigene Fachlogik oder neue Tabellen; kanonische DocflowConvertRequest verwenden. Abnahme: explizite Positionsmengen, negative Mengen/ueber Rest/fremde Position abgewiesen, keine unbeabsichtigte Volluebernahme, sichere Wiederholung und fachlicher Readback. Annahme: bestehende API-Umwandlung bleibt einziger Domain-Command; Browser-/OIDC-Nachweis separat bis real erbracht. Doku/Open-Gaps/Handshakes nachziehen.

CI-134-NACHLAUF Ergebnis: Security-Summary e733d8828 erfolgreich. Vollsuite nur ein echter … (gekuerzt; Volltext unter STUDIO-TEILMENGEN-20261114 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## PROBE-DATENRECHTE-20261114 — lokal abgenommen, Codex Subagent test_migration_workflows

Meilenstein: M0 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: bestehende technische Datenrechte nach Schemaaufbau gezielt anwenden koennen, ohne clusterweite Rollen, Passwoerter, BYPASSRLS, Eigentum oder fremde Schemata zu veraendern. Besitz scripts/provision_db_roles.py, eigene enge Unit-/CLI-Vertraege und QA. Bestehende DML-/USAGE-Politik zentral wiederverwenden; explizite Schema-/Datrollenliste, Default Plan/optional Rollback, unbekannte/reservierte Namen ablehnen. Wartungsanwendung durch Lead ausschliesslich auf bestehendem valeo_probe nach Status-/Nutzungskontrolle, keine neue DB/Container, kein Reset/Tabellen-DDL. Nicht fuer Produktionsdaten verwenden.

## DOCFLOW-TEILMENGEN-SQL-20261114 — lokal abgenommen, Codex Lead

Meilenstein: M1 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: echte PostgreSQL-Wirkung der Studio-Teilumwandlung nachweisen: Optionsabruf, Vorschau, 4 aus10, Readback/Rest6, Replay, Versions-/Uebermengen-/Fremdpositions-/Mandantenfehler, keine Doppelwirkung. Besitz neue gezielte PostgreSQL-Testdatei, QA/Handshake/Open-Gaps und Workboard. Vorhandenen valeo_probe nur als valeo_agent nutzen, eigene synthetische Datensaetze in aeusserer Transaktion mit Savepoints und Rollback; keine Datenbankkopie, keine dauerhaften Testdaten, keine Migration/Reset. Fachkommandos und reale Rollen-/Tenantgrenzen beibehalten; SQL-/API-Abnahme getrennt von noch fehlender Browser-/OIDC-Abnahme ausweisen. Lokale Berechtigungsluecke nicht durch Fachtests als Superuser umgehen.

Nachlauf15.11: 82 gezielte No-DB-Consumer-/Rechte-/Improvement-Vertraege gruen, drei echte PG-Teilmengen-/Replay-/RLS-Faelle gruen ohneSkip. Pruefstand … (gekuerzt; Volltext unter DOCFLOW-TEILMENGEN-SQL-20261114 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## RLS-ALTTEST-BESTELLUNGEN-20261115 — reserviert, Codex Lead

Meilenstein: M1 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: genau2alteTestbestellungenmitLieferantenverweisineinenanderenMandanten blockierenregulaeresEinkauf-RLS. LesenderNachweis: 2Bestellkoepfe(Statusbestellt,Testmandant00000000-0000-0000-0000-000000000001)und3Positionen; bei11geprueftenBestell-ID-SpaltenkeineweiterenVerweise, einzigerFKzeigtvonPositionenzumKopf. AufgrundbestehenderUserfreigabeAlt-TestdatenentfernenstattMandantenzuerraten: vollstaendige lokaleSicherunggenaudieser5Zeilen, atomareUUID-/Status-/Tenant-/Referenzvorbedingungen, Reihenfolge3Positionen/2Koepfe, HashvergleichalleranderenZeilen. AbbruchbeiAbweichung, keineFremdschluessel-/RLS-/Rechteaenderung, keinpauschalerReset. NurvorhandenencrashendenBackendkurzfuerOperationsfensterstoppen/starten; keineanderenDienste/DB/Container. LeadDokumentationimInventoryOperationsnachlauf/Handshake, keinevertraulichenZeilendatennachGitHub.

INVENTORY-AISLE-DRIFT-20261115 und … (gekuerzt; Volltext unter RLS-ALTTEST-BESTELLUNGEN-20261115 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## M0-CI-GESAMTBASIS-20261115 — reserviert, Codex Lead

Meilenstein M0 des freigegebenen Verkaufsprodukt-Fahrplans. Ziel: rote main-
Workflows Quality Gate/Sonar, CI/CD, E2E Full UAT und Runtime API Sweep konkret
auseinanderhalten und beheben. Besitz betroffene CI-/Evidenzvertraege und enge
Nachweistests, eigene QA/Handshake; Workboard-Bereinigung zunaechst nur eigene
nachweislich fertige Claims. Fremde Claude-Altclaims bleiben bei Claude. Kein
Gate senken, keine Baselineverschiebung oder Quellen aus Coverage ausblenden.
Der laufende PR137 muss erst auf dem gemeinsamen Dokumentationsstand abgenommen
werden. Weitere main-Merges bitte ueber den Integrationslead koordinieren,
damit Quellen nicht erneut waehrend einer Vollsuite fortgeschrieben werden.
Branches und einzelne Tests auf bestehenden eigenen Pruefstaenden bleiben frei.
Keine neuen Testdatenbanken/Container, keine fremden Prozesse abbrechen.

M0-CI-GESAMTBASIS-20261115 Erweiterung vor … (gekuerzt; Volltext unter M0-CI-GESAMTBASIS-20261115 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## BELEG-052-ALTSPEICHER-DROP-S5-20261117 — zur Abnahme, Claude Code (M1)

Owner: Claude Code. Stand: in Arbeit; PR nach Merge von S4. Meilenstein: M1 laut docs/roadmap/fahrplan-verkaufsprodukt.md.
Ziel: DocFlow ist der einzige Belegspeicher. Migration beleg_altspeicher_entfernen_20261117 entfernt die Sichten domain_crm.sales_orders/_items und die Tabellen der alten Speicher (Lieferschein, Quittung, Rechnung, Gutschrift, Bestellung, Auftrags-Ursprungsdaten) - Inhalt laut Nutzerentscheidung 10.11.2026 Testdaten; haelt an bei gebuchten Altrechnungen/-gutschriften bestehender Mandanten. Rueckweg legt die Speicher leer wieder an (DDL per pg_dump aus frischer DB, beleg_altspeicher_entfernen_20261117.sql).
Mit entfernt: ORM-Modelle (sales_invoice_models, EinkaufBestellung/-Position), Freigabe-Subjekte sales_credit_note und finance_sales_invoice (ohne Aufrufer), Demo-Seeds Verkauf/Logistik, Tabellenzuordnung, Tabellenkatalog (707 -> 696), Indizes in … (gekuerzt; Volltext unter BELEG-052-ALTSPEICHER-DROP-S5-20261117 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## M0-ROHWARE-TENANT-20261115 — reserviert, Codex

Meilenstein M0/M2: vor Aktivierung der Rohware-Schemata ausschliesslich geprueften
Mandantenkontext in allen zehn Lese-/Schreibwegen durchsetzen. Aktuell optionaler
Querymandant bei Listen, payloadmandant bei Anlage und ungefilterte Einzelwege.
Dateibesitz app/api/v1/endpoints/rohware_schema.py, neuer enger Test
 tests/test_rohware_schema_tenant_contract.py, eigene QA; Lead besitzt Doku/Integration.
Keine Tabelle erfinden, keine Migration/DDL/DB/Docker, kein neuer Sicherheitskern;
bestehende Rollen und get_tenant_id nutzen. Existierende Fachregeln und berechnete
Werte erhalten; Fremdbeleg/-zeile wie nicht vorhanden, Payload kann Mandant nicht
ueberschreiben. Guards vor Lesen/Mutation, keine DB-Details in Antworten. Gegenproben
mit zwei isolierten Kontexten, verweigerten Mutationen und erhaltenem Zustand;
wo Datenbankgrenzen simuliert werden, ausdruecklich keine echte RLS-Abnahme … (gekuerzt; Volltext unter M0-ROHWARE-TENANT-20261115 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## M0-SCHEMA-BUDGET-ROHWARE-20261115 — reserviert, Codex

Nutzerauftrag15.11: fehlende Tabellen und Routen ergaenzen. Strukturentscheidung:
Budgetplaene/-zeilen in domain_finance als tenantgebundene Tabellen einfuehren;
Konten referenzieren das fuehrende Journal domain_erp.chart_of_accounts, optionale
Kostenstellen domain_finance.kostenstellen. Rohware nutzt den vorhandenen
Stamm domain_shared.rohware_abrechnungsschemata, erweitert um Gueltigkeit,
Bearbeitungsstatus/Version und zugeordnete Formelpositionen, keinen zweiten
unabhaengigen Schema-Katalog. Vorhandene Gruppen-/Qualitaets-/Staffelverbraucher
erhalten; Gruppenzuordnung mandantensicher. Die bestehende Pfadabweichung
GET /rohware/gruppen/{gruppe_id}/schemata schliessen. Ein eigener Budget-
Positions-Leseweg nur wenn realer vorhandener Verbraucher ihn benoetigt.

Besitz Budget-Subagent: app/api/v1/endpoints/budget_planning.py, Migration
alembic/versions/budget_planning_schema_20261115.py … (gekuerzt; Volltext unter M0-SCHEMA-BUDGET-ROHWARE-20261115 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## M0-ROHWARE-FORMEL-SAFETY-20261115 — reserviert, Codex

Vor Aktivierung neuer Tabellen gefunden: _eval_formula nutzt echtes eval mit
leerem builtins-Dict, aber ohne AST-Zugriffsbeschraenkung. Objektzugriffe bleiben
damit prinzipiell moeglich. Besitz Sicherheitsagent: neue reine begrenzte
Arithmetik app/services/rohware_formula.py, nur _eval_formula und Testrechnungs-
Eingabe-/Fehlerpfad in app/api/v1/endpoints/rohware_schema.py, neue enge
Formel-Sicherheitsvertraege und QA. Vorhandene gueltige Mathematik/Funktionen
erhalten; kein eval/compile, keine Attribute/Subscripts/Comprehensions/Lambdas/
Importe, begrenzte Formelgroesse/AST-Tiefe und nur endliche Zahlen. Ungueltige
Testrechnung darf keinen scheinbar gueltigen Gesamtpreis liefern.
Lead ersetzt zusaetzlich ausschliesslich konstante SQL-Identifier-Fstrings im
neuen Schemadienst durch gleichwertige Literalabfragen, statt Scanner-Ausnahmen
aufzunehmen. Keine … (gekuerzt; Volltext unter M0-ROHWARE-FORMEL-SAFETY-20261115 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## M0-LOCAL-SCHEMA-ROLLOUT-20261116 — lokal abgenommen, Codex Lead; Preview-Integration offen

Ziel: abgenommenen main a5f60738a lokal bereitstellen. Besitz: bestehende
Backend-/Frontend-Container im Projekt valeo-neuro-erp, fuenf ausschliesslich
gemergte Migrationen in valeo_neuro_erp, eigene private Betriebsartefakte,
eigene QA/Handshake/Workboard. Keine fremden Dienste oder Testdatenbanken.
Abnahme: Sicherung mit validiertem Archiv, Quellen-/Rollen-/Aktivitaetspruefung,
transaktionale Rollback-Probe, kanonisches Alembic, gesunde bestehende Dienste
und lesende Auth-/Routenpruefung. Keine lokalen Fachtest-Schreibdaten und kein
Reset/Prune. Bei Fremdnutzung warten, bei Abweichung abbrechen. Quelle und alle
68 erfolgreichen PR-Pruefungen sind vor Ausfuehrung verifiziert; Review-Ausnahme
betraf nur die externe Review, kein Testgate. main/develop auf a5f60738a.

M0-LOCAL-SCHEMA-ROLLOUT-20261116 Erweiterung vor Edit: Nutzer meldet SSO Failed to fetch.
Lesend bestaetigt: … (gekuerzt; Volltext unter M0-LOCAL-SCHEMA-ROLLOUT-20261116 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## WORKSPACE-HOME-USABILITY-20261116 — lokal abgenommen, Codex Lead; GitHub-Integration offen

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nutzerbefund: Start zeigt technische Diagnosen, doppelte operative Listen und
eine ueberladene Zusammenstellung. Ziel: ruhiger, rollenbezogener Einstieg
innerhalb des bestehenden Studio-/Meridian-Vertrags, keine Parallelseite.
Besitz: AdaptiveWorkspaceLayer, home-composition, AgrarChainWidget und zugehoerige
Projektionen/Tests, start-dashboard-Zusammenstellung, gemeinsame spezialisierte
Disposition-/Kompositionspraesentation und eng betroffene Tests; eigene QA,
Meridian-Doku und Handshake. Delegation nur mit getrennten Dateien.
Abnahme: keine rohen UUID-/Reasoncode-Diagnosen im Standardbild, fachliche
Navigation erhalten, operative Details bewusst oeffnen, keine Berechtigungen
erweitern oder Fehler als leere Daten tarnen. Gezielte Verhaltenstests, Typpruefung
und visuelle Hell-/Dunkelpruefung; nur ein Build zur lokalen Bereitstellung.
Keine DB-Schreibtests, neuen Container oder … (gekuerzt; Volltext unter WORKSPACE-HOME-USABILITY-20261116 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## GROUPED-APP-LAUNCHER-20261116 — lokal abgenommen, Codex Lead; GitHub-Integration offen

Meilenstein: M4 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Nutzerpraezisierung mit drei Bildern: Start ist primaer funktional gruppierter
App-/Masken-Launcher, kein Dashboard. Vorhandene Launchpad-Komponenten und
Navigations-/Studio-Kataloge weiterverwenden. Besitz: LaunchpadBoard,
launchpad-spaces, AdaptiveWorkspaceLayer, start-dashboard und eng betroffene
Tests/visueller Harness; eigene QA/Design-Doku/Handshake. Getrennte Delegation
Board versus Home-Integration. Abnahme: Symbolstarter nach Fachgruppen,
Direktnavigation, Suche, Personalisierung und Theme; keine Kennzahlen/Tafeln
auf dem Standardstart, bestehende operative Komposition getrennt erreichbar.
Keine Attrappen, Rechteerweiterung, neue Datenbank oder Container.

GROUPED-APP-LAUNCHER-20261116 implementiert: Nutzerbilder praezisieren Appstarter statt Dashboard. Default zeigt vorhandene Navigation als gruppierte Symbole und echte Maskenlinks mit Suche; keine operativen Dashboard-GETs. … (gekuerzt; Volltext unter GROUPED-APP-LAUNCHER-20261116 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## CUSTOMER-MASTER-COMPLETENESS-20261117 — reserviert, Codex Lead

Meilenstein: M3 (Zuordnung M0-Bereinigung 23.11.2026, bitte pruefen).
Ziel: sichtbare Kunden-/Kundenkartenfelder gegen vorhandenes Feldregister und
Nutzerreferenz Kundenstammdaten Extraktion pruefen und vollstaendige native
Studio-Pflege mit Bank-/Zahlungs-/Steuerungsdaten wiederherstellen. Kein
Rueckbau auf handgemachte Maske, keine pauschale Freigabe interner Daten im
Kundenportal. Bestehende Modelle/Adapter nutzen, keine zweite Kundenquelle.
Besitz: betroffene kanonische CRM-ScreenDefinitions, Kundenfeldprojektionen
und deren vorhandene native Routen/Vertraege nach Inventar; eigene QA,
Feldparitaetsmatrix und Workboard/Handshake. Referenzchat/Anhang nur fuer
Feldnamen/Fachfunktionen, keine Echtdaten oder Originalscreens nach Git.
Vor Aenderungen an Persistenz/Schema Dateibesitz konkret nachtragen.
Abnahme: Bestandsfeldinventar, sichtbare/bedienbare Gruppen, echte Speicher-
und Wiederlesevertraege, Rollen-/Mandantengrenzen, passende Browserabnahme.

## RUNTIME-FIVE-503-20261117 — reserviert, Codex Lead

Ziel: fuenf noch offene Runtime503 aus M0-Nachlauf konkret zuordnen und
beheben; keine erfundenen Erfolgswerte oder gelockerten Fehler-Gates.
Zunaechst Diagnose vorhandener Nachweise ohne DB-Aenderung; Dateibesitz
vor jeweiliger Umsetzung konkretisieren. Keine neuen DB/Container.

MAIN-INTEGRATION abgeschlossen: PR151 nach vollstaendig gruener gemeinsamer
CI samt SonarCloud am 17.11.2026 nach main integriert. Main f9630be04,
Inhalt identisch zum abgenommenen Head14c2f81c5. Formale Codeowner-Sperre
mit vorhandener Nutzer-/Administratorfreigabe uebersteuert, Schutzregeln
unveraendert; keine technischen Gates umgangen. Separater main-Nachlauf
bleibt auf aktuellem Mergecommit zu beobachten.

RUNTIME-FIVE-503 Erweiterung vor Edit: runtime_503_audit besitzt ausschliesslich Dockerfile (echten Driftbericht im Backendimage verfuegbar machen), channels.py (korrekte Eingabevalidierung des … (gekuerzt; Volltext unter RUNTIME-FIVE-503-20261117 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## M0-VOR-PUSH-PRUEFKETTE-20261119 — zur Abnahme, Claude Code (M0)

Owner: Claude Code. Meilenstein: M0 (gruene Basis). Nutzerauftrag 19.11.2026: wiederkehrende CI-Rotursachen (nicht registrierte Routen/Tabellen/Masken, nicht aktualisierte Verzeichnisse, Drift der Test-DB) nicht mehr vergessen.
Ergebnis: scripts/vor_push.py (Pruefstand wie CI, alle Register, betroffene Tests gestaffelt, stiller DB-Skip = Fehler), scripts/tabellenkatalog_lineage.py (Lineage ohne DB), tests/test_vor_push.py, CLAUDE.md-Abschnitt. Ein lokaler Claude-Code-Hook blockiert jeden Push bei Rot.
Befund dabei: valeo_probe nur aus Alembic (ohne Seed und Rollen) liess Inventur- und POS-Retoure-Tests lokal scheitern, die als "Umgebung" galten.
Dateibesitz: scripts/vor_push.py, scripts/tabellenkatalog_lineage.py, tests/test_vor_push.py, CLAUDE.md (Abschnitt).

## M3-JOURNAL-SCHREIBER-20261119 — zur Abnahme, Claude Code (M3)

Owner: Claude Code. Meilenstein: M3 laut docs/roadmap/fahrplan-verkaufsprodukt.md (Integritaet: Periodensteuerung fuer alle Schreiber).
Ziel erreicht: Das Journal wird nur ueber FinanceTransactionService geschrieben. Ratsche tests/test_journal_schreiber_ratsche.py: Rohschreiber 9 -> 0.
Umgestellt: Abgrenzung, Buchungsvorlagen, Massenimport, Konnektorlaeufe, POS-Tagesabschluss. Ohne Journal: Periodenabschluss (Scheinkopf), Lagergeld (keine USt/OP), Bestandskorrektur/Inventur (Menge als Betrag), manueller OP-Ausgleich. Offene Posten lesen das Nebenbuch domain_erp statt des leeren public.offene_posten.
Offen: POS-Umsatzsteuer (Handshake an Codex docs/agent-ops/handshakes/claude-an-codex-pos-umsatzsteuer-20261119.md), Lagergeld-Abrechnung als Ausgangsrechnung, Bestandsbewertung, Migration public.offene_posten entfernen (nach #157), Saldenvortrag/Jahresabschluss.
Dateibesitz: … (gekuerzt; Volltext unter M3-JOURNAL-SCHREIBER-20261119 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## M3-STORNO-GEBUCHT-20261123 — zur Abnahme, Claude Code (M3)

Owner: Claude Code. Meilenstein: M3 (Integritaet Journal/Abschluss). PR #164.
Befund: FinanceTransactionService.reverse setzt das Original auf reversed und bucht die Gegenbuchung posted. Abschluss, UStVA, Bilanz/GuV/BWA, Kontenblatt, Kontenabfrage, Nebenbuch-Abstimmung (subsidiary_ledger), Bankabgleich und DATEV-Export zaehlten nur posted -> jeder Storno als negative Buchung (Entwicklungsdatenbank: drei Faelle).
Ergebnis: status IN ('posted', 'reversed') an allen Stellen; Ratsche und Datenbankprobe tests/test_journal_storno_gebucht.py.
Folgend (eigene PRs): #165 Schein-Fibu (public.offene_posten/buchungen/konten/anlagen) entfernt + Nebenbuch-Abstimmung echt; #167 Finanz-Altwege ohne Migration; #166 POS-Umsatzsteuer je Satz (auf #161).
Dateibesitz: bank_reconciliation.py, chart_of_accounts.py, financial_reports.py, subsidiary_ledger_reconciliation.py, finance/ustva.py, … (gekuerzt; Volltext unter M3-STORNO-GEBUCHT-20261123 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## M3-FIBU-ALTSPEICHER-20261123 — zur Abnahme, Claude Code (M3)

Owner: Claude Code. Meilenstein: M3. PRs #165 (Schein-Fibu), #167 (Finanz-Altwege, gestapelt auf #165).
- PR #165: app/routers/fibu_router.py und public.offene_posten/buchungen/konten/anlagen entfernt (Buchen am Journal vorbei, Mahnstufe ohne Mahnung, Zahlungslauf ohne Zahlung); Nebenbuch-Abstimmung je Nebenbuch gegen Sammelkonto (SKR03 1400/1600) ueber posted+reversed; public.nebenbuch_abstimmungen erstmals per Migration mit RLS.
- PR #167: Wechselkurse, Buchungsschemata, Kostenstellen, Abschlusschecklisten, Intercompany in app/finance/router.py (Tabellen ohne Migration, DELETE Checkliste ohne Wirkung, zwei unerreichbare Wege) entfernt; fuehrend /exchange-rates, /booking-templates, /kostenrechnung, /closing-checklists. Ratsche tests/test_finance_modelle_frisch.py.
Dateibesitz: app/finance/router.py, models.py, schemas.py, steuerschluessel.py (DEBITORENKONTO), app/core/container_config.py, … (gekuerzt; Volltext unter M3-FIBU-ALTSPEICHER-20261123 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))

## M2-FIBU-PLATZHALTERQUELLEN-20261123 — offen (M2)

Meilenstein: M2. Aus #165: Sieben Masken lasen ihre Liste aus dem entfernten Altweg /api/v1/fibu/anlagen bzw. /fibu/kreditoren, obwohl sie fachlich anderes zeigen (Bilanz und GuV zeigten Anlagen): fibu/atlas, fibu/bilanz, fibu/guv, fibu/monatswerte, fibu/sachkonto, fibu/sicherheiten, rezepte/editor. Gate C entfaellt dort ehrlich (studio_screen_versions.json); Eintraege stehen in config/mask_endpoint_altlast.json.
Ziel: Bilanz/GuV an /api/v1/financial-reports/balance-sheet bzw. /profit-loss mit passendem Berichts-Maskentyp (kein Listenmuster), Sachkonto an /chart-of-accounts, die uebrigen an ihren Fachweg anbinden oder entfernen. fibu/anlagen ist in #165 bereits an /finance/asset-accounting/assets angebunden.

## CUSTOMER-MASTER-PROFILE-UEBERNAHME-20261119 — zur Abnahme, Claude Code (M2, Codex-Pause)

Owner: Claude Code (uebernommen von Codex, PR #153, Codex ruht 19.-22.11.2026). Branch claude/uebernahme-kundenstamm-20261119.
Codex' Stand unveraendert uebernommen; dazu: main eingemergt; ADR in die Pflichtform gebracht (Status/Datum, Kontext, Entscheidung, Konsequenzen); Aktion stammdaten_pflegen als high mit Bestaetigung (Server verlangt Begruendung; aendert Bank/Steuer); Reiter-Vertrag auf die kanonischen partner_*-Gruppen; Zahlungsbedingung/Standardtour/Spediteur bis zum Lookup in unsupportedFields (keine Eingabe technischer Schluessel); USt-IdNr./EU-Betriebsnummer als fachliche Kennung freigegeben.
Mitbehoben, weil Codex' strengerer Feldvertrag (produktive OpenAPI statt Test-App) es aufdeckte: ueberdeckte GET /einkauf/anfragen(/{id}) in app/einkauf/router.py entfernt (die OpenAPI zeigte den toten untypisierten Weg).

## M2-MASKENFELDER-PRODUKTIV-20261119 — offen, Claude Code (M2)

Seit der Feldvertrag gegen die produktive OpenAPI prueft (PR #153): crm/betriebsprofil (vvvo_nr, ort, status fehlen in BetriebsProfil und in der Tabelle), crm/kontakt (position fehlt), finance/bank-stamm (Kopf liest die Nebenbuchabstimmung statt des Bankstamms). In config/mask_field_contract_altlast.json als Abweichung gefuehrt, darf nur schrumpfen. Dazu Lookups fuer Zahlungsbedingung, Standardtour, Spediteur im Kundenprofil.

## M3-KASSENABSCHLUSS-EIN-WEG-20261119 — zur Abnahme, Claude Code (M3, Codex-Pause)

Owner: Claude Code (Kasse ist sonst Codex' Bahn, FIN-CONTROL-001; Codex ruht 19.-22.11.2026). Meilenstein M3 (echter Kassen-/Tagesabschluss).
Ein Weg: POST /pos/tagesabschluss (fiskalischer Abschluss, Buchung ueber den Buchungsdienst) schreibt jetzt auch den Stand des Kassentags in domain_pos.pos_tagesabschluesse (Z-Bon zeigte nach echtem Abschluss "offen").
Entfernt: POST /kasse/tagesabschluss (meldete "gebucht" ohne Buchung), pos_tagesabschluss_actions (ueberdeckter POST, Statuswechsel, simulierte TSE-Signatur SIM-SIG) samt Dienst, UAT-Skript, Tests, Coverage-Baselines; ungenutzter Frontend-Hook useKasseTagesabschlussSubmit.
Offen: Maskenaktion "Tagesabschluss buchen" in kasse/tagesabschluss; Umsatzsteuer je Satz (nach S5-Merge, Migration vat_breakdown).

## M3-EIN-MAHNWEG-20261123 — zur Abnahme, Claude Code (M3)

Owner: Claude Code. Meilenstein: M3 ("Ein Mahnweg statt drei").
Befund: /dunning/process|run (eigene Stufen-/Gebuehrenlogik), /finance/mahnlauf/run (FinanceDunningService) und "Mahnstufe eskalieren" samt Maskenaktion open-items/{id}/actions/mahnen (eigener Verlauf domain_finance.finance_mahnstufen_audit, keine Mahnung, keine Stufe am Posten) liefen nebeneinander. Der Mahnlauf eskalierte bei jedem Lauf (zweimal am Tag = Stufe 2) und setzte ohne Mahnregeln erfundene Gebuehren 5/10/20 EUR an. POST /dunning legte Mahnungen an Regeln und Fristen vorbei an; PUT /dunning/{id}/paid zifferte den Posten ohne Zahlungsbuchung aus.
Ergebnis: FinanceDunningService.run_dunning ist der eine Weg (Auswahl Rechnung/Posten/Debitor, Stichtag, commit-Schalter); erneute Mahnung erst nach Ablauf der Frist der letzten Mahnung; hoechste Stufe mahnt nicht endlos; ohne Regeln 409; prozentuale Gebuehr und … (gekuerzt; Volltext unter M3-EIN-MAHNWEG-20261123 in [archive/workboard-bis-2026-11-23.md](archive/workboard-bis-2026-11-23.md))


## M3-MAHNSTUFEN-VERLAUF-ENTFERNEN-20261123 — zur Abnahme, Claude Code (M3)
Meilenstein: M3 (ein Mahnweg, Nachzug zu #168). domain_finance.finance_mahnstufen_audit hat seit dem einen Mahnweg keinen Leser und keinen Schreiber mehr; Migration mahnstufen_verlauf_entfernen_20261123 entfernt sie (haelt bei Zeilen bestehender Mandanten an; Rueckweg aus pg_dump mit RLS).
## M2-NAVIGATION-PLATZHALTER-20261123 — zur Abnahme, Claude Code (M2)
Meilenstein: M2. Sechs Maskenaktionen standen als "nicht verfuegbar" (stubReason), obwohl sie nur navigieren: Fahrer -> Tourenplanung/Dokumentenablage, Fahrzeug-Stamm -> Fahrzeugliste, Bewerbungen/Einwilligung -> Einwilligungserklaerungen und zurueck zu den Bewerbungen. Jetzt navigationRoute + localEffect "navigation" auf bestehende Zielmasken; Ratsche aktionen_nicht_verfuegbar 24 -> 18. Offen bleiben 18 echte Platzhalter (Drucken, Unfallanzeige, Einwilligung erteilen/widerrufen, Profile, Frachtprobe ...).
Dateibesitz: app/core/screen_definitions_capture.py, app/core/screen_governance.py, tests/test_bewerbung_einwilligung_masken.py, erzeugte Kataloge.
## M2-CONTROL-CENTER-NACHWEIS-20261123 — zur Abnahme, Claude Code (M2)
Meilenstein: M2. Das Control-Center laeuft ueber den Fach-Host IntakeWeighingPage mit registriertem Admin-Renderer (ControlCenterSurface, useDomainDispatch); die Nachweiskette app/core/mask_runtime_evidence.py kannte admin_workbench nicht und fuehrte die Route als "handgebaut". Eintrag ergaenzt, Ratsche handgebaut_routen 3 -> 2, Studio-Katalog Gate E. Verbleibend handgebaut: annahme/abrechnung, lager/materialfluss.
## M0-VOR-PUSH-FIXTURVERTRAG-20261123 — zur Abnahme, Claude Code (M0)
Meilenstein: M0. scripts/vor_push.py nimmt tests/test_multi_domain_uix_fixture_contract.py immer mit (woertliche Kopien der ScreenDefinitions im Frontend; #172 war erst in CI rot). Hook-Kopie ~/.claude/hooks/vor_push.py nachgezogen.
## M3-SALDENVORTRAG-20261123 — zur Abnahme, Claude Code (M3)
Meilenstein: M3 (Hauptbuch: Saldenvortrag, Jahresabschluss). Neue Fachaktion POST /api/v1/finance/closing/saldenvortrag (FINANCE_ADMIN): erst wenn alle zwoelf Perioden des Jahres gesperrt sind, eine Eroeffnungsbuchung am 01.01. des Folgejahres - Bestandskonten gegen 9000, Jahresergebnis auf 0860 Gewinnvortrag / 0868 Verlustvortrag (SKR04 2970/2978); gebucht = posted+reversed; ein Jahr nur einmal (409). SKR03-Einrichtung legt 9000/0860/0868 an.
Offen: GuV-/Bilanz-Abschlussbuchungen (Abschlusskonten) und Ergebnisverwendung als eigene Schnitte; Maskenaktion im Abschluss-Cockpit.
Dateibesitz: app/services/finance_saldenvortrag_service.py, app/api/v1/endpoints/finance_actions.py (Saldenvortrag), app/finance/steuerschluessel.py (SKR03_KONTEN), tests/test_saldenvortrag.py.
## M3-POS-UMSATZSTEUER-20261119 — zur Abnahme, Claude Code (M3)
Meilenstein: M3. PR #166. Handshake docs/agent-ops/handshakes/claude-an-codex-pos-umsatzsteuer-20261119.md (Codex-Pause, von Claude umgesetzt).
Befund: POST /pos/tagesabschluss buchte den ganzen Kassenumsatz brutto auf 8400, ohne Umsatzsteuer.
Ergebnis: Kassiervorgang speichert Brutto je Satz (pos_fiscal_transactions.vat_breakdown, Migration pos_ust_je_satz_20261119); Abschluss bucht je Satz Erloes netto und Umsatzsteuer ueber genau einen Verkaufs-Steuerschluessel aus domain_erp.tax_keys; Altvorgaenge ohne Saetze sperren; alle Pruefungen vor der TSE-Signatur.
Dateibesitz: app/api/v1/endpoints/compat.py (Tagesabschluss), app/finance/steuerschluessel.py (kassen_verkaufsschluessel), app/services/fiscalization/service.py, app/services/pos_accounting_service.py, Tests test_pos_umsatzsteuer_je_satz, test_process_kernel_wave1_contracts.

## M5-PRODUKTION-GEHEIMNISSE-PFLICHT-20261124 — zur Abnahme, Claude Code (M5)
Meilenstein: M5 (Produktions-Compose ohne Vorgabepasswoerter und ohne Dev-Token). docker-compose.production.yml: alle Geheimnisse (Postgres, OIDC-Client, Keycloak-DB/-Admin, Grafana-Admin) als ${VAR:?...} - ohne gesetztes Geheimnis bricht der Start ab statt mit leerem Kennwort zu laufen. Vertragstest tests/test_produktion_compose_geheimnisse.py (Pflicht, keine Vorgabewerte, kein API_DEV_TOKEN). check_production_readiness --contract-only: ready.
Offen in M5: Geheimnisse rotieren (Passwoerter stehen in der Git-Historie, s. README-DOKU-20261110), Sicherung mit Restore-Probe, Mandanten-Anlage als ein Kommando, Agent-Schreibfreigabe schliessen (Nutzerentscheid vor Go-Live).

## M2-HARVEST-INSPECT - reserviert, Codex Lead
Besitz: inspect_rule in der Ernte-Regeldefinition und generierte Register. Vorhandene Zeilenauswahl als lokale Aktion freistellen und Ratsche pruefen.

M2-HARVEST-INSPECT: vorhandene Regelwahl als lokale Aktion load_row deklariert. Sie verwendet bereits geladene Regelzeilen und denselben Handler wie die Zeilenauswahl. Zwei Fachvertraege gruen, Inventar 18 -> 17 nicht verfuegbare Aktionen, uebrige Ratschen unveraendert. Browserabnahme offen.

## M2-TOUR-NAVIGATION - reserviert, Codex

Ziel: Disposition und Beladung als bestehende lokale Navigation deklarieren. Dateibesitz: Tour-Definition und daraus erzeugte Inventare. Abnahme: beide Zielrouten und genaue Ratschen-Differenz. Browsernachweis offen.

M2-TOUR-NAVIGATION umgesetzt: Dispo-Arbeitsraum und Beladung verwenden den vorhandenen Browser-Handler. Python-Definition, Frontend-Fallback und Versionenkatalog sind synchron. Mit der Regelinspektion sinken die nicht verfuegbaren Aktionen von 18 auf 15. Browserabnahme offen.

## M2-FEED-NAVIGATION - reserviert, Codex

Ziel: drei bestehende Navigationen der Fuetterungsberatung deklarieren. Dateibesitz: ScreenDefinitions der Fuetterungsberatung und erzeugter Versionskatalog. Abnahme: vorhandene Zielrouten, unveraenderte Rollen und Inventar.

M2-FEED-NAVIGATION umgesetzt: Bestandsliste und mobile Fuetterungsdokumentation sind in drei Aktionen als Browser-Navigation deklariert. Zielrouten und vorhandene Handler abgeglichen. Geprueft: Studio-Inventar 292 -> 289 auf diesem Zweig, 15 nicht verfuegbare Aktionen. Browserabnahme offen.

## M2-LOCAL-PRINT - reserviert, Codex

Ziel: vorhandenen Browserdruck fuer Fuetterungsplan, Fremdware, Inventur und Abfrage-Center deklarieren. Dateibesitz: ScreenDefinitions und erzeugte Inventare. Abnahme: Handlerabgleich und Studio-Ratsche.

M2-LOCAL-PRINT umgesetzt. Alle vier UI-Handler oeffnen den Browserdruck; es entsteht kein Server-Command. Studio-Ratsche 289 -> 285 undeklarierte Aktionen. Versionskatalog synchron, Katalog der Agentenwerkzeuge unveraendert. Die vorherige Fuetterungsnavigation ist mit sieben Definitionstests abgenommen.

## M2-WORKSPACE-PRODUCTION-NAV - reserviert, Codex

Ziel: bestehende Navigation zur Druckmaske und zum zuletzt geoeffneten Dokument deklarieren. Dateibesitz: zugehoerige ScreenDefinitions. Abnahme: Handler, Zielroute, Inventar.

M2-WORKSPACE-PRODUCTION-NAV umgesetzt. Druckaktion fuehrt zur vorhandenen Druckmaske; Dokumentaktion nutzt den vorhandenen Link der eigenen Historie. Studio-Inventar 285 -> 283. Browserabnahme offen.

## M2-PRUEFKORB-NAV - reserviert, Codex

Ziel: vorhandenen Belegsprung deklarieren. Dateibesitz: Definition des Pruefkorbs und abgeleiteter Versionskatalog. Abnahme: serverseitige Belegroute, bestehender UI-Handler und Studio-Inventar.

M2-PRUEFKORB-NAV umgesetzt: Zum Beleg nutzt die serverseitig abgeleitete Belegroute. Drei gezielte Maskenvertraege bestanden, Studio-Inventar 283 -> 282 auf diesem Zweig. Browserabnahme offen.

## M2-ADMIN-BRANCHES-RUNTIME - reserviert, Codex

Befund: /admin/branches hat keinen ID-Parameter und mountet ausschliesslich MadeByStudioDetailRuntimeWire. Deshalb endet der normale Einstieg vor dem Datenabruf bei der Datensatzauswahl. Die Detaildefinition erwartet bezeichnung/status, die vorhandene mandantengebundene Branch-API liefert branch_number/name/is_active. Folgeauftrag: Listenquelle am Einstieg anbinden, Auswahl und typgerechte Details belegen. Bearbeiten erst mit passendem Feldschema, bestehender Admin-Autorisierung und einem registrierten Kommando anbinden; ein Deklarationswechsel allein behebt den Laufzeitfehler nicht.

Listeneinstieg umgesetzt: /admin/branches liest den vorhandenen mandantengebundenen Listenvertrag und zeigt Nummer, Name und Aktivstatus. Regressionstest und Studio-Inventar gruen. Die unwirksame Bearbeitungsdeklaration wurde entfernt; typisierte Detailansicht und Rollen-/Command-Anbindung der Bearbeitung sowie Browserabnahme bleiben offen.

Detailansicht umgesetzt: Aus der Niederlassungsliste zur Studio-Objektseite. Die Ansicht liest den vorhandenen mandantengebundenen Detailvertrag und zeigt Nummer, Namen, Aktivstatus und Zeitstempel. Zwei Vertragspruefungen sowie Studio-Gates A/B/C/E gruen. Bearbeitung und Browserabnahme offen.

Schreibvertrag vorbereitet: Adressen werden beim Anlegen und Aendern als echtes JSON gebunden, einschliesslich Apostroph, Boolean und null. SQLAlchemy-Bindung und bestehende Lesemaske mit vier gezielten Tests geprueft. Freigabe der Studio-Bearbeitung steht aus.

PostgreSQL-Abnahme bestanden: Auf valeo_probe (mahnstufen_verlauf_entfernen_20261123) wurden Anlegen, Aendern und erneutes Lesen einer JSONB-Adresse geprueft. Der Test legt seinen eigenen Mandantendatensatz fuer den Fremdschluessel in derselben Transaktion an und rollt beide Datensaetze zurueck. Drei Tests bestanden.

Niederlassungs-Update liefert die in derselben SQL-Anweisung geaenderte Zeile zurueck. Der Mandantenfilter bleibt Teil des Updates. Das vermeidet zwei Leseabfragen und eine konkurrierende Neulesung nach dem Commit. Drei gezielte Tests auf valeo_probe bestanden; Studio-Schreibbindung weiter offen.

Versionsschutz fuer Niederlassungen: REST liefert eine aus updated_at abgeleitete ganzzahlige Version und akzeptiert expected_version. Abgleich im mandantengebundenen UPDATE, bei veraltetem Stand 409. Bestehende PUT-Aufrufe ohne Version bleiben kompatibel. OpenAPI nachgezogen, fuenf Tests inklusive Konfliktnachweis auf valeo_probe bestanden. Die verpflichtend versionsgebundene Studio-/CLI-/MCP-Aktion bleibt offen.

Umbenennen in der Studio-Detailmaske umgesetzt. Der Admin-Endpunkt verwendet den bestehenden mandantengebundenen Versionsschutz sowie die gemeinsame Laufzeit fuer Trockenlauf, Idempotenz, Audit und Outbox. CLI-Register erzeugt; MCP klassifiziert die Aktion als gesperrt. Sechs Tests inklusive PostgreSQL-Trockenlauf, Ausfuehrung und Replay sowie Studio-Inventar gruen. Browser und MCP-Freigabe bleiben offen.

CLI-Vertrag belegt: Die Kommandozeile verwendet die echte Studio-Definition und sendet Version, Auditgrund und Idempotenzschluessel an den Umbenennungs-Endpunkt. Der Test prueft den HTTP-Aufruf gegen das Backend-Schema mit simuliertem Transport. Ein Agent wird dabei vor dem Schreibaufruf abgewiesen. Browserabnahme offen.

HTTP-Abnahme im ASGI-Test: Admin-Rolle, Pflichtversion, Idempotenz und Auditgrund geprueft. Fehlender Auditgrund wird vor der Ausfuehrung mit 422 abgewiesen; der Trockenlauf funktioniert ohne Schreibmetadaten. Sieben Tests gruen. Laufender Docker-Dienst: /api/v1/openapi.json antwortete nicht innerhalb von 30 Sekunden, Auslieferungsstand und Browserabnahme sind damit offen.

Browserabnahme konkret eingegrenzt: Lokales Backend-Image accepted-a5f60738a und Frontend-Image portal-3b750ff68 melden healthy. Die serverseitige Umbenennung fehlt im laufenden Backend nachweislich. Fuer die Sichtpruefung ist ein gemeinsam aus demselben freigegebenen Stand gebautes Frontend und Backend erforderlich. PR #179 (21cf2416f) wartet auf CI und Pflichtreview.

Frontend-Abnahme auf Komponentenebene: Umbenennen ueber echten Eingabedialog, Vorbelegung, Trockenlauf, Vorschau und Begründigung. Der Ausfuehrungsaufruf sendet nur Name, gelesene Version und Auditgrund. Ein neuer und 17 angrenzende Vitest-Faelle gruen. Reale Browserabnahme bleibt offen.

## M2-READVIEW-IMPORT - reserviert, Codex

Ziel: direkten Rueckimport des Lese-Dialogs in das Mask-Builder-Paket aufloesen. Dateibesitz: ReadViewDialog.tsx. Abnahme: bestehender Test des Lese-Dialogs.

Lese-Dialog importiert Renderer und Laufzeit direkt. 13 Vitest-Faelle bestanden. Weitere Rueckimporte und Auswirkungen auf die Rollup-Warnungen sind offen.

Folgeschritt M2-READVIEW-IMPORT: direkter Import in UniversalNativeDetailPage und UniversalNativeCockpitPage; betroffene Vitest-Mocks auf dieselben Module umstellen.
## M3-LAGERGELD-RECHNUNG-20261124 — zur Abnahme, Claude Code (M3)
Meilenstein: M3 (Lagergeld als Ausgangsrechnung). Der Lagergeld-Lauf stand auf "posted" ohne Rechnung, Erloes oder offenen Posten. Neu: POST /api/v1/inventory/storage-fees/runs/{run_id}/rechnungen legt je Einlagerer einen DocFlow-Rechnungsentwurf (sales_invoice, Quelle lagergeld) mit einer Position je Lagergeld-Zeile an; Verkaufs-Steuerschluessel ausdruecklich (keine Vorgabe), wiederholbar ohne Doppel. Freigabe und Buchung ueber die Belegmaske.
Dateibesitz: app/services/lagergeld_rechnung.py, app/domains/inventory/api/storage_fees.py, tests/test_lagergeld_rechnung.py.

M2-READVIEW-IMPORT: Detail- und Cockpit-Maske verwenden direkte Modulimporte. Die 77 Mask-Builder-Testdateien sind mit 562 Tests gruen. main b881f45da integriert, beide Workboard-Eintraege erhalten, OpenAPI-Drift-Check gruen.

## M0-I18NEXT-DEPENDENCY - reserviert, Codex

Ziel: Auditbefund GHSA-6jcc-5g8w-32mx durch korrigierte i18next-Version schliessen. Dateibesitz: Frontend-Paket, pnpm-Lock und Migrationsnachweis. Abnahme: Installations- und i18n-Vertrag.

GHSA-6jcc-5g8w-32mx behoben: i18next 26.3.4 im Frontend und Lockfile. Frozen-Lockfile-Installation, produktives Node-Audit (0 Befunde), TypeScript und zehn Frontend-Tests bestanden. GitHub-Nachlauf offen.

Nachweis fuer den Major-Wechsel: Echter i18next-Laufzeittest mit Deutsch, Englisch und Spanisch inklusive Speicherung der Sprachauswahl. 19 Vitest-Faelle inklusive Bestellvorschlag und Prozessstudio bestanden.

## M0-KI-ROUTER-DUPLIKAT - reserviert, Codex

Ziel: zweiten Mount desselben KI-Usability-Routers unter /api/v1 entfernen. Dateibesitz: KI-Mount in main.py und generierte API-Doku. Abnahme: bestehende Pfade bleiben erhalten, doppelte OpenAPI-Operationen der KI entfallen.

Doppelten KI-Usability-Mount entfernt. 4.052 HTTP-Operationen behalten unveraenderte Methoden, Pfade und IDs. OpenAPI zeigt nun die Bearer-Pflicht der beiden Aktionsabfragen. Drei KI-Duplikatwarnungen entfallen, acht POS-/Reporting-/CRM-Warnungen bleiben separat offen.

## M0-POS-REPORTS-ROUTER-DUPLIKATE - reserviert, Codex

Ziel: zwei verdeckte Platzhalter fuer Zahlarten und Berichtsexport entfernen. Dateibesitz: deren Routendeklarationen und OpenAPI. Abnahme: fuehrende Handler und Pfade bleiben erhalten.

Verdeckten statischen Zahlarten-Handler und leeren Berichtsexport entfernt. OpenAPI beschreibt jetzt die bereits wirksamen Handler. Abgleich: 3.221 Pfade, unveraenderte Methoden und Operation-IDs; nur die beiden erwarteten GET-Vertraege geaendert. Sechs CRM-Duplikatwarnungen offen.

## M0-CRM-ROUTER-DUPLIKATE - reserviert, Codex

Ziel: sechs ueberschattete CRM-Registrierungen entfernen. Dateibesitz: betroffene Dekoratoren in app/crm/router.py, API-Artefakte. Abnahme: alle HTTP-Pfade und IDs bleiben erhalten, OpenAPI beschreibt die zuerst registrierten Handler.

Sechs ueberschattete CRM-Registrierungen entfernt. OpenAPI ohne Duplikatwarnungen erzeugt. 3.221 Pfade, Methoden und IDs erhalten. Das Endpoint-Inventar zur Entfernung des Reporting-Stubs nachgezogen.
## M0-I18NEXT-GHSA-6JCC-20261123 — in arbeit, Cursor (M0)
Meilenstein: M0 (main ohne rote Laeufe). Owner: Cursor.
Befund: Advisory GHSA-6jcc-5g8w-32mx (i18next deepExtend, DoS, moderate, veroeffentlicht 23.11.2026 20:53 UTC) sperrt den Node-Dependency-Gate aller PRs (i18next 25.5.3, behoben ab 26.3.4).
Ziel: Herstellerfix statt Backport (ADR-080): i18next auf ^26.3.4 im Frontend, Lockfile; react-i18next 16 erlaubt i18next >= 25.10.9. Code nutzt keine in 26.0.0 entfernte Option (initImmediate, interpolation.format, simplifyPluralSuffix).
Dateibesitz: packages/frontend-web/package.json (nur i18next), pnpm-lock.yaml, QA docs/quality-assurance/i18next-ghsa-6jcc-20261123.md.
Abnahme: Dependency Scan, Python and Node Dependency Audit, Frontend-Tests und -Build gruen.

main 4859a973d integriert. Dessen i18next-Aufloesung 26.7.2 uebernommen; Frozen-Lockfile-Installation und echter Sprachwechseltest gruen.

Review PR 179: Rollenzuordnung aus dem Endpunkt erzeugt (admin erforderlich), HTTP prueft jetzt menschliche Identitaet entsprechend CLI und Studio. 10 HTTP-Tests, 17 Frontend-Rollentests sowie 11 Registrierungs- und OpenAPI-Vertraege bestanden. GitHub-Pflichtreview braucht eine berechtigte Kennung ausserhalb der PR-Autorenschaft.

## M2-ADMIN-USERS-LIST - reserviert, Codex

Ziel: /admin/users mit der bestehenden Studio-Benutzerliste verdrahten; keine zweite fachliche Liste. Dateibesitz: beide Definitionen, Routeneinstieg und abgeleitete Artefakte. Abnahme: gleiche Spalten, Datenquelle und Listenlaufzeit.

/admin/users verwendet denselben Studio-Listenbuilder und denselben geschuetzten Lese-Endpunkt wie /admin/benutzer. Unwirksame Bearbeitungsdeklaration entfiel. Zwei Regressionstests und Studio-Gates A/B/C/E gruen; 280 undeklarierte Aktionen auf diesem Zweig. Browserabnahme offen.

## M2-ADMIN-TENANTS-LIST - reserviert, Codex

Ziel: Mandanteneinstieg als Studio-Liste ueber den kanonischen, serverseitig autorisierten Leseweg. Dateibesitz: ScreenDefinition, Einstieg und erzeugte Kataloge. Abnahme: Felder und paginierter GET-Vertrag.

Mandanteneinstieg als Studio-Liste umgesetzt. Der bestehende Lifecycle-Dienst bestimmt weiterhin den sichtbaren Verwaltungsbereich. Die Liste zeigt Name, Domain und Aktivstatus und verwendet die gemeinsame Projektion fuer Pagination. Drei Vertragspruefungen und Studio-Inventar gruen. Browserabnahme und Lifecycle-Aktionen in Studio offen.

## M0-L3-ARCHITECTURE-CI - reserviert, Codex

Ziel: Architekturindex nach aktuellen Routen abgleichen und den beschaedigten Vorspann der L3-Zuordnung entfernen. Abnahme: CI-Validatoren.

## M0-I18NEXT-GHSA-6JCC-20261123 — abgeschlossen, Cursor (M0)
Meilenstein: M0 (main ohne rote Laeufe). Owner: Cursor.
Befund: Advisory GHSA-6jcc-5g8w-32mx (i18next deepExtend, DoS, moderate, veroeffentlicht 23.11.2026 20:53 UTC) sperrte den Node-Dependency-Gate aller PRs (i18next 25.5.3, behoben ab 26.3.4).
Ergebnis: Herstellerfix (ADR-080) — i18next ^26.3.4, Lock 26.7.2; gemergt als #183 (4859a973d).

## M0-VOR-PUSH-SPERRE-20261124 — zur Abnahme, Claude Code (M0)
Meilenstein: M0. scripts/vor_push.py nimmt selbst die Pruefstand-Sperre (%TEMP%/valeo_vor_push.lock, PID-Pruefung, verwaiste Sperre wird uebernommen, Frist 45 min). Bisher sperrte nur der Claude-Code-Hook; eine Sitzung, die vor_push direkt aufrief, baute valeo_probe mitten in fremden Laeufen neu auf. Der Hook setzt VALEO_PRUEFSTAND_SPERRE=gehalten (keine Doppelsperre). Gilt damit fuer Claude, Cursor und Codex, sobald sie scripts/vor_push.py aus main nutzen.

## M0-E2E-FULL-UAT-20261123 — in arbeit, Cursor (M0)
Meilenstein: M0 (main ohne rote Laeufe). Owner: Cursor. Abgegrenzter Teil aus M0-CI-GESAMTBASIS-20261115 (Codex); Sonar-Abdeckung und Runtime API Sweep bleiben bei Codex. Handshake: docs/agent-ops/handshakes/cursor-an-codex-m0-e2e-full-uat-20261123.md.
Befund (Lauf 45156197226, main bbe18fb8f): alle 21 roten @full-Tests (CRM 360 16, Zahlungsabgleich 3, POS-Fiskalisierung 2) stehen auf der SSO-Anmeldeseite. .github/workflows/e2e-full.yml startet weder Test-Keycloak noch Postgres/Redis, installiert keine Python-Abhaengigkeiten und migriert nicht; seit dem Wegfall des Dev-Tokens (12.10.2026) ist der Lauf deshalb unangemeldet. Workflow rot seit mindestens 09.11.2026.
Ziel: Full-UAT-Workflow wie e2e-critical.yml mit echter Anmeldung (scripts/ci/e2e_keycloak.sh), Datenbank und Backend; Browser-Specs mit echter Sitzung; danach echte Fachfehler einzeln beheben. Keine Gates senken, keine Tests entschaerfen oder ueberspringen.
Dateibesitz: .github/workflows/e2e-full.yml, playwright.config.ts (nur Projekt full), playwright.anmeldung.mjs (Browser-Sitzung als storageState), .gitignore (nur playwright/.auth/), playwright-tests/helpers/anmeldung.ts, playwright-tests/specs/crm/crm360-*.spec.ts, playwright-tests/specs/finance/payment-matching.spec.ts, playwright-tests/specs/pos/fiscalization-admin.spec.ts, QA docs/quality-assurance/m0-e2e-full-uat-20261123.md.
Abnahme: workflow_dispatch von e2e-full.yml auf dem Branch gruen; danach naechtlicher Lauf auf main gruen.
Stand 23.11.2026: Anmeldung und Stack laufen (Lauf 45173550757). Restliche Fehlschlaege pruefen Funktionen der Altmasken, die in den Studio-Masken fehlen. Nutzerentscheid 23.11.2026: Specs auf die heutigen Masken umschreiben; Tests fuer fehlende Funktionen bleiben als test.fixme mit Luecken-ID stehen und werden mit Schliessen der Luecke wieder scharf. Zahlungsabgleich: Import und Saldenvergleich echt geprueft, Zuordnung -> M3-BANK-ZUORDNUNG-UI. POS: Tagesabschluss -> M3-KASSENABSCHLUSS-EIN-WEG-20261119 (offen: Maskenaktion). CRM: crm360-model-based und crm360-revenue-handover (gemockte KIM-API gegen das entfallene Cockpit #crm-main-viewport) ersetzt durch crm360-kundenakte.spec.ts gegen den echten Stack (Neuanlage, Register, Bearbeiten, Aktivitaet samt Pflichtfeldfehler); fehlende Cockpit-Funktionen -> M4-CRM-KUNDENAKTE-PARITAET. Zusaetzlicher Dateibesitz: playwright-tests/specs/crm/crm360-*.ts, playwright-tests/helpers/interactionGuard.ts (nur expectCrm360RoundTrip entfernt).
Fachfehler aus Lauf 45281437646 behoben: Sprungnavigation der durchgehenden Belegseite (SectionPageRenderer) landete zu frueh, weil auf dem Weg nachgeladene Abschnitte das Ziel verschoben (Kundenakte: Klick auf "Praesente" endet bei "Historie"). Das Ziel bleibt nach dem Sprung JUMP_PIN_MS lang angeheftet und wird bei Hoehenaenderung nachgefuehrt; eigenes Scrollen (Rad, Touch, Zeiger, Scrolltasten) loest es. Dateibesitz zusaetzlich: packages/frontend-web/src/components/mask-builder/renderers/SectionPageRenderer.tsx, packages/frontend-web/src/__tests__/components/mask-builder/section-page.test.tsx. Befund 422 bei Aktivitaet anlegen -> Codex (CRM-ACTIVITY-CANONICAL-20261029, Handshake-Nachtrag).
Stand 23.11.2026 abends: workflow_dispatch-Lauf 45285135642 auf d8963888a gruen (9 bestanden, 15 test.fixme mit Luecken-ID, 0 rot). Offen: Merge von PR #182, danach naechtlicher Lauf auf main. Nach Merge #183 (i18next) Branch auf aktuellen main gebracht.

## M3-BANK-ZUORDNUNG-UI-20261123 — offen, P1 (M3, Bahn Fibu)
Befund aus M0-E2E-FULL-UAT: finance/bank-abgleich (bank-surface.tsx) kann Kontoauszuege importieren und Salden vergleichen, bietet aber weder manuelle Zuordnung einer Bankzeile zu einem offenen Posten noch Zuordnungsvorschlaege noch Abgleichkennzahlen. Das Backend hat /api/v1/finance/auto-matching/match und /match/{line_id}/apply. Abnahme: die drei test.fixme in playwright-tests/specs/finance/payment-matching.spec.ts sind scharf und gruen.

## M4-CRM-KUNDENAKTE-PARITAET-20261123 — offen, P1 (M4, Bahn CRM)
Befund aus M0-E2E-FULL-UAT: Die native Kundenakte crm/customer-360 bietet Bearbeiten, Aktivitaet anlegen und die Pflege der sechs Partner-Untertabellen; die Schnellaktionen des frueheren Cockpits fehlen: Drucken, Waehlen/TAPI mit Kontaktprotokoll, Ansprechpartner-Detail, KI-Zusammenfassung, Angebot/Auftrag mit Kundenkontext anlegen, Beleg aus dem Register oeffnen (keine Zeilenroute), Sprung in finance/op-debitoren mit Kundenfilter, Lead-Register und Karte, Unterlagenablage (Register Dokumente zeigt offene Posten). Abnahme: die test.fixme in playwright-tests/specs/crm/crm360-kundenakte.spec.ts sind scharf und gruen; Teilschliessungen pro Aktion erlaubt.

main 5f5888862 integriert. Architekturindex frisch und vollstaendig (1.146 Routen, 349 Dienste, 474 Endpoint-Module). L3-YAML-Vorspann repariert; Validator meldet 8 Tabellen, 26 Zuordnungen, 0 Fehler, 0 Warnungen. CI behandelt einen Validatorfehler jetzt als Fehler. Kein L3-Datenimport durchgefuehrt.

Mandantenliste: Laufzeitvertrag mit 51 synthetischen Zeilen geprueft. Der gemeinsame Datenleser ruft beide Seiten mit skip=0 und skip=50 ab und leitet das Bearer-Token ohne Mandantenheader weiter. Der Transport war simuliert.

## M2-ADMIN-API-KEYS-LIST - reserviert, Codex

Ziel: API-Schluessel-Einstieg an die bereits autorisierte Metadatenliste anbinden. Dateibesitz: ScreenDefinition, Routeneinstieg und generierte Artefakte. Abnahme: Schema, bestehender GET und Studio-Gates.

API-Schluessel-Einstieg als Studio-Liste umgesetzt. Verwendet den geschuetzten GET fuer Schluesselmetadaten statt der Benutzer-Detailquelle. Keine Schreib- oder Exportaktion deklariert. Vertragstest und Studio-Inventar gruen; Browserabnahme offen.

CLI-Register nach Entfernung der wirkungslosen Admin-Aktionen neu erzeugt. 380 ausfuehrbare CLI-Aktionen; zwei ueberholte Eintraege aus der Statistik entfernt. CLI-, MCP- und Listenrouten-Generatoren ohne Drift.

## M0-COMMAND-MONITOR-TENANT - reserviert, Codex

Ziel: Betriebszaehler des Command Monitors auf den geprueften aktiven Mandanten begrenzen. Dateibesitz: Overview-Handler, Idempotenz-Store und zugehoeriger Vertragstest. Abnahme: lokale und Gesamtstatistik des Stores.

Command-Monitor-Overview zeigt Store-Zaehler und ausgefuehrte Kommandos des geprueften Mandanten. Der statische Capability-Katalog bleibt global. Drei Tests gruen, OpenAPI unveraendert und reproduzierbar. Weitere Monitoring-Wege sind nicht Teil dieses Nachweises.

Einzelabrufe nach Ausfuehrungs-ID und Idempotenzschluessel sind an den aktiven Mandanten gebunden. Eigene Eintraege bleiben in beiden Abrufen verfuegbar; fremde und unbekannte Eintraege liefern HTTP 404.

Der Ausfuehrungs-Endpunkt weist einen abweichenden Mandanten im Request vor dem Idempotenz-Lookup und vor der Kommandoausfuehrung mit HTTP 403 ab. Der HTTP-Vertrag prueft auch den abgewiesenen Replay nach einem Mandantenwechsel.

Abnahme: gezielter Lauf fuer Wave 17/18/85 mit 27 bestandenen und einem uebersprungenen Test. Studio-Folgebefund: /admin/command-monitor verwendet eine generische Artikel-Detaildefinition mit unwirksamer Bearbeiten-Aktion, obwohl die vorhandene Ansicht den Idempotenz-Overview liest. Die separate Definition process/background-jobs beansprucht dieselbe Browserroute, zeigt jedoch die Job-Queue. Bei der Migration getrennte fachliche Routen und einen gleichwertigen Monitor-Nachweis vorsehen.

Command-Monitor-Oberflaeche liest den JSON-Inhalt der Antwort und trennt den Abfragecache nach Mandant und Benutzer. Ein Frontend-Regressionstest prueft Datenprojektion, Mandantenwechsel und fehlende Identitaet. Die Studio-Routentrennung bleibt offen.

PR 179: Der CI-Integritaetscheck meldete den Process-Kernel-Router mit 6115 gegen 6100 Zeilen. Die fachliche Overview-Berechnung liegt jetzt im bestehenden Idempotenzmodul, HTTP-Pfad und Antwort bleiben gleich. Der Router ist auf 6092 Zeilen gesunken und der Grenzwert wurde entsprechend abgesenkt.
