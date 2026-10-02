---
title: Kanonische Konto-IDs im Journalservice
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-02
version: 1.0.0
---

# Kanonische Konto-IDs im Journalservice

## Vertrag und Rueckbau

Journalzeilen des FinanceTransactionService enthalten ausschliesslich
account_id. Die globale OR-Abfrage fuer ID oder Nummer und der accountId-
Fallback sind entfernt. Konto-IDs werden genau im eigenen Mandanten auf
aktiv, deleted_at IS NULL und nicht Summenkonto geprueft. Fremde oder globale
Templatekonten ohne eigenen Tenant sind keine erlaubten Buchungsziele.

Bestehende nummernkonfigurierte Verbraucher loesen Kontonummern ausdruecklich
ueber account_id_for_number auf, bevor sie Journalzeilen konstruieren:
Sales, Agrar-Settlement, Einkauf, Harvest, Procurement, Asset Accounting,
Genossenschaft, Logistics Freight und Mischfutter-Produktion. Die bestehenden
API-Felder und ihre fachlichen Nummernkonfigurationen bleiben erhalten;
es gibt keinen Alias im kanonischen Journalvertrag.

Die Konto-ID-Pruefung aller Zeilen erfolgt vor Stempel/Kopf/Zeilenpersistenz
in einer einzigen gebundenen IN-Abfrage mit deduplizierten IDs und FOR SHARE.
Die Anzahl der Zeilen erzeugt keine einzelnen Validierungsabfragen. Der
Guard prueft auch zusaetzliche konkurrierende Felder bei vorhandener account_id.
Nummernlookup ist ein expliziter Leseschritt; kein automatisches Konto erzeugen.

Die unbenutzte konkurrierende _create_gl_booking_and_op-Funktion aus
finance_invoices und ihr alleiniger _ensure_account-/Tax-Helfer sind entfernt.
Aktive Rechnungswege delegieren bereits an SalesPostingService. Dessen
_ensure_account erzeugte automatisch Konten und committete vor der Buchung;
auch dieser Altweg ist entfernt. Fehlende eigene Konten brauchen einen
explizit konfigurierten Kontenplan, keine geratenen Minimaldaten.

## Nachweise

186 Tests bestanden (6.10 Sekunden), davon 26 neue Kontoreferenz-Vertraege:
16 echte PostgreSQL-Faelle, neun AST-Vertragswaechter fuer die genannten
Verbraucher und ein Retirement-Vertrag. Nummer/ID-Kollision ueber Tenant-
grenzen, fehlende/inaktive/geloeschte/Summenkonten, camelCase und fehlende
Referenzen sind abgedeckt. Ungueltige Referenzen erzeugen keine Journal-
Schreibzugriffe; 200 Zeilen verwenden genau eine Validierungsabfrage.
Regressionen: Journalstempel, Service, Posting, CRM-Handover, Kontentrennung,
Storno, Agrar-Settlement, Harvest und Procurement. Lokaler Log:
artifacts/journal-account-tests.log. Ruff der geaenderten Kern-/Testdateien
bestanden; Whitespace-Check bestanden.

Vorhandener valeo_probe, eigene kleine chart_of_accounts-Schemakopie fuer
reale Konto-Vertraege, Transaktionsrollback und gezieltes Schema-Cleanup.
Keine neue Datenbank oder Dockerinstanz, kein gemeinsamer Reset/Migrationslauf.
Die echten Tabellenbegriffe deleted_at und Kontonummernlaenge 20 sind durch
PostgreSQL geprueft; keine abweichenden Testtabellen zur Simulation erfunden.

Agent-Handbuch --check im gemeinsamen Worktree noch rot (index,
masken-api-katalog, agent-process-manifest). Parallel uncommitted sind fuenf
neue ScreenDefinitions in screen_definitions.py/capture hinzugekommen.
Keine fremden generierten Handbuchdateien ungeprueft veroeffentlicht.
Eigene Aenderung fuegt keine API-Route, Maske, DTO oder Domain-Grenze hinzu.

## Weiter offen

Globale account_number-UQ, Tenant-Komposit-FKs anderer Journalwege und
kontenplanbezogene Konfiguration sind nicht durch diesen Service-Guard geloest.
Andere Journal-Schreiber sind noch separat zu harmonisieren. Mehrere
Verbraucher fangen Buchungsfehler weiter ab, obwohl vorgelagerte Fachzustände
bereits geschrieben sind; ihre Atomizitaet ist keine bestandene Abnahme.
Hash-Payload, Draft-Delete, Betragsdubletten, zeilenweiser Bank/GL-Beleglink
und gemeinsame Bank-Migrationsintegration bleiben offen. Die kanonische
Konto-ID ist hier fuer den Service und alle neun bekannten Nummernverbraucher
abgenommen, nicht fuer das gesamte Projekt. Minor: vorhandener Service,
keine neue Fachfunktionalitaet oder externe API-Form.

Zusaetzlich belegt: validate_balanced akzeptiert leere/Nullbetragsjournale;
produktion_mischfutter erzeugt noch ausdrueckliche Nullbetragsplatzhalter
bei fehlendem Preismodell. Das ist keine reale Produktionskostenbuchung
und bleibt als Betrags-/Bewertungsgap offen.
