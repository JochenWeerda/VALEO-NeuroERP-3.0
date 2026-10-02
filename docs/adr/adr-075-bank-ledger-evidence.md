---
title: ADR-075 Explizite Bank-Hauptbuchverbindung und Saldennachweis
type: adr
audience: [architektur, entwickler, qa]
owner: domain/finance
status: proposed
last_reviewed: 2026-10-02
version: 1.0.0
---

# ADR-075 Explizite Bank-Hauptbuchverbindung und Saldennachweis

**Status:** Proposed
**Datum:** 2026-10-02

## Kontext

BankAccounts akzeptierte gl_account_number, speicherte die Auswahl aber nicht.
Lesen und Abgleich ersetzten die Verbindung durch gleiche Kontonummern.
Der Vergleich nahm den Tenant aus der URL, pruefte die Kontobindung des Auszugs
nicht und behandelte fehlende Journale als Nullsaldo. Lesefehler wurden zu
einer leeren Differenzliste. Summary hatte andere Feldnamen, floats und eine
offene DTO-Huelle. PARTIAL/Unknown verschwanden aus der Zusammenfassung.

## Entscheidung

Ein nullable gl_account_id an bank_accounts ist die explizite Verbindung.
Composite-FK auf chart_of_accounts(id,tenant_id) plus Check fuer vorhandenen
Tenant bei gesetztem Link; keine Ableitung oder Rueckfuellung aus Nummern.
Create/Update pruefen ein aktives buchbares ASSET-Konto der Kategorie bank
im eigenen Tenant. Kein geratener Kontenplan-Eintrag. gl_account_number
entfaellt und wird als unbekanntes Payloadfeld abgewiesen. Der begrenzte
ledger-options-Endpunkt dient der Korrektur dieser vorhandenen Auswahl.

Ein Bank-ReconciliationResult fuer Reconcile und Summary, Geldwerte als
Decimal/JSON-String und fehlender Nachweis als null. Difference und
is_balanced werden aus belegten Werten abgeleitet. MAPPING_REQUIRED,
NO_POSTED_ENTRIES und CSV_SYNTHETIC bleiben INCOMPLETE. Der Tenant kommt aus
dem gemeinsamen Header-Vertrag; fremdes Konto/Statement liefert 404.

Auszug, Zeilen, begrenzte Differenzseite und Hauptbuch werden mit einer
SQL-Abfrage in demselben PostgreSQL-MVCC-Snapshot gelesen. Posted-Journale
bis einschliesslich Stichtag: eigene Mandanten, gleiche Waehrung, mindestens
zwei korrekte Buchungszeilen, ausgeglichene Summen und passende Kopfbetraege.
Konkurrierende debit/debit_amount und credit/credit_amount muessen exakt
uebereinstimmen; kein stiller Fallback. Bank MATCHED braucht eigenen OP-Link.
Vollstaendigkeit, Saldenarithmetik und Dateivertrag werden ebenfalls geprueft.
Lesefehler sichtbar als 500, Datenwiderspruch als 409, kein SQL im Fehlertext.
Differenzen maximal 100 pro Seite, Gesamtzahl und PARTIAL/Unknown explizit.

Bestehende Masken nutzen gemeinsame TS-Vertraege und Optionshooks. Kein
Redesign: typisierte Daten-/Aktionsintegration im transitional ObjectPage-
Muster. Strategische Umstellung weiterhin durch ScreenDefinition/RenderPlan/
UniversalMaskRuntime; diese Masken werden dadurch nicht generatorReady.

## Konsequenzen

Migrationsstand ist Voraussetzung fuer den neuen Bankvertrag. Historische
Bankkonten bleiben explizit unverbunden, bis ein eigenes Hauptbuchkonto
gewaehlt wird. Keine Archive oder Kompatibilitaetsadapter fuer Entwicklungs-
Altlasten. Der gemeinsame Pruefstand wird waehrend fremder Nutzung nicht
migriert; die echte Migration ist im eigenen Schema desselben valeo_probe
getestet. Parallel uncommitted EUDR-Fortsetzungen brauchen einen koordinierten
Merge-Head, bevor die gemeinsame Integration als abgeschlossen gelten kann.

BALANCES_EQUAL ist ein Salden- und OP-Zuordnungsnachweis, kein zeilenweiser
Bank/Journal-Beleglink. Journalbetragsdubletten, globale Kontenaufloesung im
FinanceTransactionService, verschluckte GoBD-Stempelfehler, globale
Kontennummer-Eindeutigkeit und Audit/RBAC der Bankstammpflege bleiben offene
kanonische Folgethemen. Kein Go-Live oder fachliche Gesamtabnahme.
