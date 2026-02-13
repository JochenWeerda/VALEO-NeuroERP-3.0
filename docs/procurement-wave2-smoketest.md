# Procurement Wave 2 Smoketest

Stand: 2026-02-13
Code-Referenz: HEAD 5bdde358 + lokale Aenderungen (noch nicht committed)
Scope: Supplier Dokumente, PO Kommunikation, Audit Drilldown

## Voraussetzungen
- Backend laeuft lokal mit API unter /api/v1
- Frontend laeuft lokal
- Testdaten: mindestens 1 Lieferant und 1 Bestellung vorhanden

## 1. Lieferanten-Dokumente
1. Navigation: Einkauf -> Lieferanten-Dokumente oeffnen.
2. Supplier ID eingeben und Liste laden.
Erwartung: Kein Crash, bei leerer Liste ein sauberer Leerzustand.
3. Dokument anlegen (Name + Typ + Kategorie).
Erwartung: Eintrag erscheint in der Tabelle nach erfolgreichem Request.
4. Dokument loeschen.
Erwartung: Eintrag verschwindet; API antwortet ohne Fehler.
5. Fehlerfall testen (ungueltige Supplier ID).
Erwartung: Fehlerzustand wird sichtbar (ErrorState), kein Mock-Fallback.

## 2. PO-Kommunikation in Bestellungs-Detail
1. Einkauf -> Bestellung oeffnen.
2. Versanddialog oeffnen, Methode Email senden.
Erwartung: POST auf /api/v1/purchase-orders/{id}/communications/email erfolgreich.
3. Versanddialog oeffnen, Methode Portal senden.
Erwartung: POST auf /api/v1/purchase-orders/{id}/communications/portal erfolgreich.
4. Kommunikationshistorie pruefen.
Erwartung: Beide Eintraege werden im Kommunikations-Card angezeigt.
5. Fehlerfall (Bestellung ohne ID / nicht gespeichert).
Erwartung: Validierungsmeldung, kein stilles Fallback.

## 3. Audit Trail Drilldown
1. Einkauf -> Audit Drilldown oeffnen.
2. docType + docId aus existierender Bestellung eingeben, Laden klicken.
Erwartung: Ereignisliste wird geladen.
3. CSV Export ausfuehren.
Erwartung: Datei wird heruntergeladen, Inhalte enthalten Zeilen pro Event.
4. Fehlerfall mit ungueltiger docId.
Erwartung: Fehlerzustand sichtbar, keine Mock-Daten.

## 4. Regression Kurzcheck
1. Einkauf -> Lieferantenbewertung, Service Entry Sheets, EDI Portal oeffnen.
Erwartung: Seiten laden weiterhin und verwenden API-Hooks.
2. Navigation pruefen.
Erwartung: Neue Menuepunkte sichtbar: Lieferanten-Dokumente, Audit Drilldown.

## Ergebnisprotokoll
- [ ] Lieferanten-Dokumente: OK
- [ ] PO-Kommunikation: OK
- [ ] Audit Drilldown + CSV: OK
- [ ] Regression: OK
- [ ] Kein Mock-Fallback beobachtet
