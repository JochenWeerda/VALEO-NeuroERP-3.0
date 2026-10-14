# PORTAL-CONTEXT-001: Lohndienst und Empfehlungen persistent, Portalrollen, Kontowahl, keine Ersatzkunden

Stand: 2026-10-14 · Slice `PORTAL-CONTEXT-001-20261014` · Nutzerentscheidung PORTAL-CONTEXT-001 vom 14.10.2026
(Abschnitte 1–6), im Anschluss an TENANT-DOC-001 und ALTBELEG-QUARANTAENE

## Befund vorher

- Lohndienst-Auftraege und Empfehlungen lagen nur im Arbeitsspeicher eines Prozesses (`_STORE`/`_SVC_CACHE`): nach
  Neustart weg, je Prozess verschieden, ohne Version, Historie oder Idempotenz.
- `portal_innendienst.py`: Mandant aus dem rohen Kopf `X-Tenant-ID`, keine Rolle; jede Anmeldung las die Schlagkartei
  jedes Kunden. Die Massnahmenabfrage nannte nicht vorhandene Spalten (`schlag_name`, `fahrer`); ein Fehler wurde zur
  leeren Liste — sie lieferte nie Daten. Die Tests dazu liefen gegen eine gefaelschte Datenbank, die genau das
  verdeckte, und schrieben "DB-Fehler ergibt leere Liste" fest.
- Portalrolle wurde gespeichert, aber nirgends ausgewertet: jede zugeordnete Rolle sah alles.
- Demo-/Ersatzkunden: Portal-Layout (`Musterhof GmbH`, `K-2024-001`), Uebersicht, Lohndienste, Empfehlungen und
  interne Kunden-Schlagkartei (`K-10001`); Seed-Skript mit Standardmandant und `dev-token`.

## Umsetzung

### Persistenz (Migration `portal_lohndienst_persistenz_20261014`, additiv)

- `domain_portal.lohndienst_auftraege`: Pflicht `tenant_id`, `customer_id` (FK `domain_crm.customers`),
  `schlag_ids` (nur Schlaege des Kontos), Statusmaschine als CHECK, optimistische `version`, Lohndienstleister-Zuweisung,
  Akteur/Zeit. Nicht loeschbar (Trigger) — storniert wird.
- `domain_portal.lohndienst_ereignisse`: jede statusrelevante Aenderung (anlegen, bestaetigen, einplanen, abschliessen,
  stornieren) mit Vorher/Nachher, Version, Akteur, Kanal (`portal`/`intern`), Idempotenzschluessel und Anfrage-Hash,
  Stand als Snapshot. Nur fortschreibbar (Trigger gegen UPDATE/DELETE/TRUNCATE). `UNIQUE (auftrag_id, version)` und
  `UNIQUE (tenant_id, idempotenz_schluessel)`: zwei Prozesse koennen weder denselben Stand zweimal fortschreiben noch
  dieselbe Anfrage zweimal ausfuehren.
- `domain_portal.empfehlungen`: Herkunft `regel` oder `ki` (dann `modell` Pflicht), eindeutig je Ausloeser
  (Kunde, Typ, Kontext, Artikel, Ziel) — dieselbe Erzeugung legt nichts doppelt an. Gesehen mit Person und Zeit.
- `domain_portal.kundenzugaenge`: Portalrollen erweitert, `schlag_ids` fuer Mitarbeiter.

### Dienste und Wege

- `app/services/portal_lohndienst_service.py`: deterministische Statusmaschine (Aktion → genau ein Uebergang),
  Pflicht-Idempotenzschluessel (Wiederholung liefert das gespeicherte Ergebnis, anderer Inhalt = 409), Version
  (veraltet = 409 mit aktueller Version), parallele Gewinner werden als Wiederholung erkannt.
- `app/api/v1/endpoints/portal_lohndienst.py`: Kopf `X-Idempotency-Key` Pflicht; anlegen mit `lohndienst_beauftragen`
  (Innendienst zusaetzlich `sales_order` bearbeiten); bestaetigen (Freigabe) und einplanen nur Innendienst;
  abschliessen Innendienst oder zugewiesener Lohndienstleister; stornieren im Portal nur, solange angefragt; neue Wege
  `/disposition` (Innendienst, alle Auftraege des Mandanten) und `/{id}/historie`. Portalnutzer sehen weder die
  Anmeldung des Lohndienstleisters noch die des Innendiensts (Datenminimierung).
- `app/api/v1/endpoints/portal_intelligence.py`: neu `GET /portal/empfehlungen` (eigenes Konto); Erzeugen nur
  Innendienst fuer Kunden des Mandanten.
- `app/api/v1/endpoints/portal_innendienst.py`: Mandant aus der Anmeldung, Kunde ueber `portal_kunde` (Pfad = gewaehlter
  Kunde, sonst 404), echte Spalten, keine verschluckten Fehler; Potentialanalyse nur mit Fachrolle des Hauses.

### Portalrollen zentral (`app/auth/portal_kunde.py`, keine zweite Rollenverwaltung)

`PORTAL_RECHTE` bildet die sieben Rollen als Vorlagen auf Funktionen ab; `portal_recht(...)` prueft sie an jedem
Portalweg (Uebersicht, Verkauf, Kontrakte, Finanzen, Feldbuch lesen/erfassen/verwalten, Auswertungen,
Lohndienst lesen/beauftragen/ausfuehren, Empfehlungen, Zugaenge verwalten):

| Rolle | Funktionen |
| --- | --- |
| inhaber | alles des eigenen Betriebs inkl. Benutzerverwaltung (ohne Aussendienst/Lohndienstleister vergeben) |
| betriebsleiter | Verkauf, Kontrakte, Feldbuch inkl. Verwalten, Auswertungen, Lohndienst beauftragen, Empfehlungen |
| mitarbeiter | Feldbuch lesen und Massnahmen erfassen — nur zugewiesene Schlaege; Lohndienst lesen |
| buchhaltung | Finanzen (Rechnungen, Dokumente) |
| berater | Feldbuch lesen, Auswertungen, Empfehlungen |
| lohndienstleister | nur zugewiesene Auftraege mit noetigen Schlagangaben; abschliessen |
| aussendienst | zugeordnete Kunden, nur mit Fachrolle des Hauses; Verkauf, Kontrakte, Feldbuch lesen, Auswertungen, Lohndienst, Empfehlungen |

Keine Portalrolle oeffnet alle Kunden eines Mandanten. Interne Betreuung (Innendienst ohne Zuordnung) waehlt einen
Kunden des Mandanten; Schreibwege pruefen zusaetzlich die Fachrollen des Hauses. Startseite zeigt nur erlaubte Kacheln.
Die Portalwege aus `compat.py` liegen jetzt in `portal_kundenwege.py`, Feldbuch-Rechte in
`app/agrar/feldbuch/portal_zugang.py`, Feldbuch-Schemas in `app/api/v1/schemas/portal_feldbuch_schemas.py` (Pfade,
Funktionsnamen, Vertrag unveraendert; beide Dateien wieder unter ihrer Godfile-Baseline, Baseline gesenkt).
Die Schemadatei gab es schon als verwaiste Altfassung ohne einen einzigen Importeur und mit abweichenden
Feldern; sie enthaelt jetzt die tatsaechlich genutzten Schemas.

### Frontend

- `lib/portal-konto.ts` + `components/portal/PortalKontoWahl.tsx`: aktives Konto nur im Arbeitsspeicher (kein
  localStorage ohne Einwilligung); eines → automatisch, mehrere → Auswahl vor jedem Kundeninhalt, keines → Hinweis,
  Innendienst → Kundenwahl. `lib/api-client.ts` schickt `X-Kundenkonto` fuer Portalwege.
- Portal-Layout ohne Demo-Kunden, Navigation nach Rechten; Uebersicht, Lohndienste, Empfehlungen, interne
  Kunden-Schlagkartei ohne `K-10001`; Lohndienst-Anlage mit Idempotenzschluessel je Anfrage.
- `scripts/seed_simulation_rations_acker.py`: `--umgebung entwicklung|test`, `--tenant`, `--kundenkonto` und Token
  Pflicht, Vorpruefung am Server.

## Nachweis (frische Datenbank `valeo_probe`)

- `tests/test_portal_lohndienst_persistenz.py` (17): Auftrag ueberlebt den Prozess (eigener Python-Prozess liest ihn);
  vier parallele Prozesse mit demselben Schluessel → genau ein Auftrag, ein Ereignis; vier parallele Prozesse auf
  denselben Stand → genau einer ok, drei Konflikt; Wiederholung idempotent, fremder Inhalt 409, ohne Schluessel 422;
  veraltete Version 409; Statusmaschine; Historie vollstaendig, nur fortschreibbar, Auftrag nicht loeschbar;
  Rollenmatrix (betriebsleiter/mitarbeiter/buchhaltung/berater × 9 Wege); Portal-Storno nur angefragt, keine Freigabe;
  Lohndienstleister nur zugewiesen, mit Schlagangaben; Aussendienst nur mit Fachrolle; Inhaber verwaltet eigene
  Benutzer; Mitarbeiter nur zugewiesene Schlaege; Empfehlungen ohne Dubletten (auch aus drei Prozessen), Herkunft,
  kontogebunden, KI ohne Modell abgewiesen; Mandantengrenze; Innendienst-Sicht mit echten Spalten.
- Regression 140 + 150 Faelle gruen (Portal, Feldbuch, Dokumentspeicher, Kanonik, Mandantenpflicht).
- Frontend: `tsc` (typecheck) sauber, ESLint sauber, Vitest der betroffenen Seiten 14/14.
- Gates im Worktree: SQL-f-Strings, Pagination, OpenAPI-Doku, Response-Models, tote Transaktionen, Bind-Casts,
  Mandantenisolation, Code-Inventare, Agent-Handbuch, MCP-Referenz gruen; Godfile: `compat.py` 3518 → 3403,
  `portal_feldbuch.py` 2041 → 1946.
- Vorbestehend rot, nicht durch diesen Slice: 401 mit altem Dev-Token (`test_disposition_crud`,
  `test_process_kernel_wave6_supplier`, `test_small_endpoints_wave57` wf_trigger), Godfile `payment_runs`/
  `sales_credit_notes`, Architektur-Index `tenant_lifecycle_service`.
- Entfernt: `tests/test_portal_innendienst.py` (Fake-Datenbank, schrieb verschluckte Fehler fest) — ersetzt durch Test
  gegen die echte Datenbank.

## Sichtpruefung (echter OIDC/PKCE-Ablauf, 14.10.2026)

Gewachsene Datenbank vorher gesichert (`valeo_neuro_erp-full-20261014-vor-portal-migration.dump`, sha256
`c87b15cd…`, ausserhalb des Repos) und auf `portal_lohndienst_persistenz_20261014` migriert. Zwei synthetische
Keycloak-Kennungen (Mandant per Attribut, Zugangsdaten nur lokal, nie im Repo) und Zuordnungen: Betriebsinhaber auf
„Hof Janssen GbR“ und „Agrargenossenschaft Wesermarsch“, Betriebsmitarbeiter auf „Hof Janssen GbR“ mit einem
zugewiesenen Schlag. Anmeldung jeweils ueber „Mit SSO anmelden“ → Keycloak-Formular → Ruecksprung (kein gesetztes
Token), Vite :3001, Backend-Container mit dem neuen Code.

| Bild | Befund |
| --- | --- |
| ![Kontowahl](../benutzerhandbuch/img/portal-context-20261014/01-kontowahl.jpg) | Zwei Betriebe → Auswahl vor jedem Kundeninhalt |
| ![Inhaber](../benutzerhandbuch/img/portal-context-20261014/02-inhaber-uebersicht.jpg) | Betrieb und Kundennummer aus der Zuordnung, Kacheln mit echten Kennzahlen |
| ![Lohndienst](../benutzerhandbuch/img/portal-context-20261014/03-lohndienst-angefragt.jpg) | Lohndienst angefragt (201, persistent), Liste des Kontos |
| ![Mitarbeiter](../benutzerhandbuch/img/portal-context-20261014/04-mitarbeiter-uebersicht.jpg) | Mitarbeiter: Navigation nur Uebersicht/Ackerschlagkartei, keine Kacheln, keine Bestell-/Lohndienstknoepfe |
| ![Feldbuch](../benutzerhandbuch/img/portal-context-20261014/05-mitarbeiter-feldbuch.jpg) | Nur der zugewiesene Schlag; nur Sammelduengung und Info; Arbeitskontext mit Betrieb und Rolle |

Die Sichtpruefung fand vier Fehler, die kein Test fand — alle behoben:

1. Die Uebersicht suchte Kennzahlen unter Bezeichnungen, die das Backend nie liefert: alle Kacheln zeigten immer 0.
   Jetzt die gelieferten Bezeichnungen; fehlt eine (Rolle darf sie nicht sehen), entfaellt die Kachel.
2. Die Uebersicht begruesste mit dem Platzhalter „Portal-Kunde / PORTAL“ — jetzt Betrieb und Kundennummer.
3. Schaltflaechen und Schnellzugriffe ohne Recht (Bestellportal, Lohndienst buchen, Feldbuch-Import,
   Jahreswechsel, Export, Schlaege pflegen) wurden angezeigt und haetten 403 geliefert — jetzt nach Portalrecht
   ausgeblendet (der Server prueft unveraendert).
4. Der Feldbuch-Arbeitskontext nahm Rolle und Betriebsname aus Query/Body (Standard „betriebsleiter“, Name = rohe
   Kunden-ID) — jetzt aus Anmeldung und CRM, mit deutscher Rollenbezeichnung; Parameter entfernt.

Hinweis Bedienung: Die Kontowahl liegt nur im Arbeitsspeicher; nach einem harten Neuladen fragt das Portal bei
mehreren Betrieben erneut (bewusst, kein localStorage ohne Einwilligung).

Die Testkennungen, ihre Zuordnungen und der angefragte Testauftrag bleiben in der Entwicklungsumgebung fuer weitere
Sichtpruefungen (Zuordnungen werden widerrufen, Auftraege storniert — geloescht wird beides nicht).

## Nebenbefunde

- `docker-compose.yml` enthaelt das Keycloak-Admin-Kennwort im Klartext (committet).
- Die 18 Schlaege des Entwicklungsmandanten gehoeren dem Ersatzkunden `dev-customer` (alter Rueckfall des
  Feldbuchs) und sind jetzt fuer niemanden erreichbar — Klaerung/Bereinigung braucht eine Entscheidung.
- Die Glocke im Portalkopf zeigt eine feste Zahl (3), keine echten Benachrichtigungen.
- `tsconfig.typecheck.json` (fokussierte Typpruefung) erfasst `pages/portal`, `layouts` und grosse Teile von `lib`
  nicht; geprueft wurde deshalb mit der vollen Konfiguration (einziger Fehler: fremde Datei `lib/api/studio.ts`).

## Offen

- **MCP/CLI:** Lohndienst und Empfehlungen sind noch nicht als Agentenwerkzeuge registriert (MCP-Vertraege bearbeitet
  derzeit Codex); die Fachaktion liegt im Dienst, ein Werkzeug ruft denselben Dienst.
- Profilseite des Betriebs und Pflegemaske der Zugaenge (Mask Builder) fehlen.
- `customer_orders.order_number`, `documents.doc_number`, `customers.customer_number` systemweit statt je Mandant
  eindeutig.
- Gewachsene Datenbank: Migrationen der Portal-Slices vom 14.10. noch anzuwenden (Sichtpruefung).
