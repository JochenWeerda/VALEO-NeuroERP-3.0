---
title: Action-Matrix O2C — kanonischer HTTP-Vertrag
status: aktiv
last_reviewed: 2026-11-15
owner: Codex
---

# ACTION-MATRIX-O2C-HTTP-20261115

Arbeitsbasis: Branch `codex/o2c-real-contract-20261115`, Claim `ACTION-MATRIX-O2C-HTTP-20261115`,
Produktbasis `e9ae5cab6` (integrierter, auf `e8a2e92d5` gepruefter Stand). Der Nachweis ist vorbereitet, noch nicht fachlich
abgenommen. Keine Matrix-Statusanhebung und kein erfolgreicher HTTP-Lauf behauptet.

## Aenderung und Testidentitaeten

`playwright-tests/specs/e2e-matrix/o2c-semantic-chain.spec.ts` ersetzt die alten
GET-Health-Proben und die fehlerakzeptierende Prozesskette durch zwei eigenstaendige
`@critical`-Vertraege:

- `o2c-001 @critical — signed sales role creates and reads a real tenant order`:
  signierte POWER-Anmeldung, eigene echte Kundenanlage mit HTTP-Readback,
  serverseitiger Maskenkontext und gefilterte echte Partnerauswahl,
  Auftrag mit zwei Positionen ueber `POST /api/v1/docflow/`, separater HTTP-Readback
  mit Mandant, Partner, Typ, Status, Positionen und exakten Summen.
- `o2c-002 @critical — partial delivery persists, replay and rejected writes preserve quantities`:
  eigener Auftrag; explizit 4 von 10 Einheiten der ersten Position, zweite ausgelassen;
  Folgebeleg mit Quellen-ID/Quellpositions-ID, Menge und Summen; Restmengen 6 und 3;
  Replay mit gleicher Ziel-ID; fehlendes Token 401, Readonly-Schreiben 403,
  Header-/Query-Mandantenspoofing 403, alte Version 409, Uebermenge 400.
  Readback von Quelle, Ziel und Restmengen nach Replay/abgelehnten Kommandos.

Positive Create-/Convert-Aufrufe verlangen exakt 200, den aktuellen kanonischen
Statuscode. Fehlercodes sind ausschliesslich ausdrueckliche Gegenproben.
Keine Ersatz-IDs, bedingten Erfolgsassertionen oder Skips bei fehlenden Voraussetzungen.

Die entfernten Rechnungs-, Zahlungs-, Mahn- und DATEV-Mock-Schritte akzeptierten
404/422/503 und bewiesen keine Wirkung. Ihre fachlichen Ziele bleiben offen; es
werden weder Ersatzrouten noch Abnahmen fuer `o2c-003/004` oder externe Gates erfunden.

## Voraussetzungen fuer den koordinierten Lauf

- Tatsächliches `main:app` unter `PLAYWRIGHT_BASE_URL` und echte OIDC-Pruefung.
- `VALEO_USER_POWER`/`VALEO_PASS_POWER` sowie `VALEO_USER_READ`/`VALEO_PASS_READ`;
  Anmeldung ueber vorhandenes `holeTokens()` in `playwright-tests/helpers/anmeldung.ts`.
  Anbieter konfiguriert durch `VALEO_OIDC_TOKEN_URL`/`VALEO_OIDC_CLIENT_ID`.
  Keine Dev-Tokens oder Nutzung des Admin-Tokens fuer diese beiden Tests.
- `VALEO_E2E_TENANT` muss zu den signierten Kennungen passen; Standard ist der
  bestehende Testmandant `00000000-0000-0000-0000-000000000001`.
- GlobalSetup bleibt unveraendert `playwright.anmeldung.mjs`: vorhandene Admin-
  Konfiguration kann dort weiterhin eine Anmeldung ausloesen. Die O2C-Tests verwenden
  ausschliesslich ihre POWER-/READ-Tokens.
- POWER-Kennung muss die vorhandene CRM-Schreibrolle besitzen. Jeder Testversuch
  legt einen eigenen Kunden ueber `POST /api/v1/crm/customers/` an (exakt 201),
  liest ihn frisch mit `GET /api/v1/crm/customers/{id}` (exakt 200) und prueft ID,
  Mandant, eindeutige Kundennummer und Firmenname. Der lokale Mandantenanker wird
  in `CustomerService.create_customer` auch bei erreichbarem crm-core ueber
  `upsert_monolith_stub` geschrieben und committed; bei Verbindungsfehler ueber
  `_create_in_monolith_db`. Keine Annahme eines gemeinsam genutzten externen Speichers.
- Aktive native Definition `GET /api/v1/masks/beleg/sales-order/screen-definition`
  muss gueltigen `creationContext` liefern. Echte mandanteneigene Kundenquelle:
  `GET /api/v1/belege/sales_order/partner-auswahl?q=<eigene_Kundennummer>&limit=2`.
  Genau ein Treffer mit exakt der angelegten Kunden-ID ist erforderlich. Leere,
  mehrdeutige oder abweichende Auswahl scheitert ausdruecklich; keine erfundene Partner-ID.
- Vorhandener gemeinsamer PostgreSQL-Pruefstand bzw. Job-Datenbank mit vollstaendigen
  Migrationen fuer DocFlow, Nummernkreise, Idempotenz, Historie und Outbox. Lokal vor
  Freigabe `python scripts/pruefstand_db.py --status`; kein Reset/neue DB/Container.

Jeder Testversuch verwendet eigene UUID-basierte Kunden-/Beleg-/Kommandoschluessel und
frische HTTP-Kontexte. HTTP-Schreibbefehle committen real; die eindeutig benannten
eigenen Kunden samt Geschaeftspartnerbruecke und Belege bleiben als Evidenz stehen. Kein Rollback vorgetaeuscht und keine
pauschale Bereinigung. Ein koordinierter Wiederholungslauf erzeugt weitere eigene
Kunden und Belege. Es gibt keine geteilten Prozessketten-IDs zwischen Tests/Workern.

Echte Fremdtoken-Isolation bleibt offen: Die bisherigen CI-Identitaeten aus
`scripts/ci/e2e_identitaeten.py` liegen im selben Mandanten. Spoofing-403 ersetzt
keinen Zugriff mit gueltigem zweitem Mandanten-Token. Ebenso kein UI-/Browsernachweis,
keine Finance-, Versand-, Rechnungs- oder externe Providerwirkung.

## Lokale Pruefung und Grenzen

Ausschliesslich statische/Collection-Pruefungen ohne API, OIDC, DB oder Container:

- `npx tsc --noEmit --skipLibCheck --target ES2022 --module commonjs --moduleResolution node --types node playwright-tests/specs/e2e-matrix/o2c-semantic-chain.spec.ts`
  erfolgreich. Prueft eigene Spec und importierten Login-Helfer; keine Gesamtprojekt-
  oder Abhaengigkeits-Typabnahme (`skipLibCheck`).
- `npx playwright test --config=playwright.config.critical.ts --list --workers=2 o2c-semantic-chain.spec.ts`
  erfolgreich: genau zwei Tests gesammelt. `--list` fuehrt keine Fachaktion aus.
- npm meldet bestehende unbekannte Konfigurationsschluessel `public-hoist-pattern`
  und `shamefully-hoist`; kein Testfehler.

Lead koordiniert erst den echten Lauf mit maximal zwei Workern und vorhandenen
Ressourcen. Erst dessen erfolgreiches Ergebnis auf benannter Commit-SHA erlaubt
entsprechende Evidenzverknuepfung; auch das ist keine automatische Statusanhebung.

Dateibesitz unveraendert: O2C-Spec und diese QA; keine Aenderung an Auth, CI,
Produktquellen, Matrix-YAML, Generator, gemeinsamen Docs oder Datenbank.

