# CRM360 Revenue-Handover-Klicktest

Stand: 2026-06-08

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

Die Browserausfuehrung verwendet deterministische API-Fixtures. Sie beweist
die Verdrahtung, den Kontexttransport und die Zielmasken, aber keine
produktive Buchung oder persistente Finanzverarbeitung. Dieser Nachweis
erfordert einen separaten UAT-Durchstich mit isolierten, aufraeumbaren
Backend-Testdaten.
