# CRM360 Revenue-Handover-Klicktest

Stand: 2026-06-09

## Ziel

Der Test fuehrt den CRM360-Folgeprozess im echten Browser durch:

`Kunde -> Angebot -> Auftrag -> Lieferschein -> Rechnung -> OP`

Dabei werden nicht nur URLs, sondern auch sichtbarer Kundenkontext,
Quellbelege, Belegpositionen, Zielmasken sowie Console-, Page-, HTTP- und
404-Fehler geprueft.

## Umsetzung

- Gemeinsamer typisierter Handover-Vertrag fuer Kunde und Quellbelege
- Sichtbare Vorbelegung des Kunden in der Angebotserfassung
- Direkter Sprung vom konvertierten Angebot zum erzeugten Auftrag
- Uebergabe der Auftragspositionen an die kanonische Lieferscheinmaske
- Direkter Sprung vom Lieferschein zur kanonischen Rechnungsmaske
- Vollstaendiger Kontext beim Wechsel von Rechnung zu OP-Debitoren
- Stabile `data-action-id`-Vertraege fuer die Folgeprozess-Aktionen
- Korrigiertes API-Response-Modell fuer `convert-to-order`

## Behobene Fehler

| Befund | Ergebnis |
| --- | --- |
| Angebot-zu-Auftrag lieferte ein anderes Schema als deklariert | passendes Response-Modell eingefuehrt |
| Kundenkontext war in Folgemasken nicht durchgaengig sichtbar | gemeinsamer Search-/Handover-Vertrag |
| Lieferschein lud nur den Kunden, aber keine Auftragspositionen | Positionen werden aus dem Auftrag uebernommen |
| Lieferschein oeffnete nach Konvertierung eine unpassende Rechnungsroute | kanonischer Invoice-Editor mit Rechnungs-ID |
| Prozessmodell verwendete eine nicht kanonische Lieferscheinroute | Route auf `/verkauf/lieferschein-erfassung` korrigiert |

## Verifikation

- Kombinierte Playwright-Suite: 11 Tests bestanden
- Frontend-Typecheck: bestanden
- Playwright-Typecheck: bestanden
- Produktions-Build: bestanden
- Backend-Sicherheitstest fuer Sales Offers: 3 Tests bestanden
- Routing-Integritaet und Navigation-Targets: bestanden

## Grenze

Die Browserausfuehrung verwendet deterministische API-Fixtures. Ergaenzend
steht mit `scripts/uat/crm360_revenue_handover_uat.py` nun ein persistenter
Dev-UAT gegen die realen Backend-Vertraege bereit.

## Persistenter UAT

Ausfuehrung:

```powershell
python scripts/uat/crm360_revenue_handover_uat.py --execute
```

Der Lauf:

- verweigert Produktionsumgebungen und ist ohne `--execute` wirkungslos
- erzeugt einen eindeutig markierten, tenant-isolierten Kunden
- persistiert Angebot, Auftrag, Lieferschein und Docflow-Rechnung
- validiert Positionen, Kundenkontext und Quellbelegbeziehungen
- loescht den offenen Rechnungsentwurf ueber den oeffentlichen API-Vertrag
- entfernt im `finally` alle erzeugten Artefakte exakt nach ihren IDs

Live-Ergebnis am 2026-06-08: `status=passed`. Die anschliessende
Residuenpruefung ergab fuer Kunden, Angebote, Lieferscheine, Docflow-Belege
und Outbox-Ereignisse jeweils `0`.

## Zusaetzlich behobene Backendfehler

| Befund | Korrektur |
| --- | --- |
| Lieferscheinerzeugung schrieb in veraltete Spalten | SQL auf kanonisches Delivery-Schema umgestellt |
| Dev-Datenbank enthielt trotz Alembic-Stand keine nutzbare Delivery-Struktur | idempotente Repair-Migration ergaenzt |
| Docflow-Link wurde vor dem Ziel-Header geschrieben | FK-konforme Einfuegereihenfolge hergestellt |
| Fehler im optionalen Audit wurde geschluckt, markierte aber die Fachtransaktion als abgebrochen | Audit in SQL-Savepoint isoliert |
| Offene Docflow-Entwuerfe hatten keinen kontrollierten Cleanup-Vertrag | tenant-isoliertes Soft-Delete fuer `draft` und `open` ergaenzt |

Eine finale Finanzbuchung oder OP-Erzeugung wird bewusst nicht automatisch
zurueckgeloescht.

## Finanz-UAT mit Storno

Der vollstaendige, revisionssichere Durchstich wird explizit aktiviert:

```powershell
python scripts/uat/crm360_revenue_handover_uat.py --execute --include-posting
```

Dieser Modus prueft zusaetzlich:

- Docflow-Posting ist bei Wiederholung idempotent
- JournalEntry besitzt Status `posted` und ist in Soll/Haben ausgeglichen
- Debitoren-OP enthaelt Rechnungsnummer, Kunde und Bruttobetrag
- Storno erzeugt eine separate GoBD-Gegenbuchung
- Originalrechnung und Docflow-Beleg wechseln auf `reversed`
- OP wechselt auf `storniert` und Restbetrag `0`

Gebuchte Daten werden in diesem Modus nicht hart geloescht. Die vollstaendig
reversierte Kette bleibt als Auditnachweis in der Dev-Datenbank erhalten.

Live-Nachweis vom 2026-06-09:

- Rechnung `SIV-2026-000005`
- Original-Journal `019eaa9c-468a-77fa-adb1-15beb2e28ed9`
- Gegenbuchung `019eaa9c-4729-77b4-bf91-08aae841f1ee`
- OP `019eaa9c-46c9-7870-91b0-ff35e4318b6f`
- Original und Gegenbuchung jeweils Soll/Haben `20,00 EUR`
- OP `storniert`, `open_amount=0`, `offen=0`
- keine verwaisten Sales-Invoice-Journalentwuerfe

Zusaetzlich behoben:

- verpflichtendes `journal_entry_lines.line_number` wurde nicht geschrieben
- ORM kannte kanonische `debit_amount`/`credit_amount`-Spalten nicht
- Kontonummern wurden faelschlich als Konto-IDs in den FK geschrieben
- global eindeutige Kontonummern wurden tenant-spezifisch gesucht und doppelt angelegt
- freie technische `posted_by`-Werte kollidierten mit dem User-FK
- Finance-Invoice und Docflow verwendeten unterschiedliche Postinglogik
