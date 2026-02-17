# Lieferschein-Erfassung - UAT Test-Anleitung (Live im Browser)

**Datum:** 2025-01-16  
**Zweck:** Schritt-für-Schritt Anleitung für manuellen Test im Browser

## Vorbereitung

1. **Browser öffnen:** Öffnen Sie `http://localhost:3000/verkauf/lieferschein-erfassung` in Ihrem Browser
2. **Browser-Entwicklertools:** Öffnen Sie die Browser-Konsole (F12) um Fehler zu sehen
3. **Bereit:** Warten Sie auf meine Anweisungen

## Test-Workflow (Schritt für Schritt)

### Schritt 1: Seitenaufruf ✅
- **Aktion:** Seite sollte bereits geöffnet sein
- **Erwartung:** Lieferschein-Erfassungsmaske ist sichtbar
- **Prüfen:** 
  - Sidebar ist eingeklappt (nur Icons)
  - Lieferschein-Nr. ist auto-generiert
  - Alle Felder sind leer

### Schritt 2: Sidebar-Toggle (Strg+B)
- **Aktion:** Drücken Sie `Strg+B` (oder `Ctrl+B` auf Mac)
- **Erwartung:** Sidebar wird ein-/ausgeklappt
- **Prüfen:** Text-Labels werden sichtbar/unsichtbar

### Schritt 3: Kundenauswahl öffnen (Strg+F1)
- **Aktion:** Drücken Sie `Strg+F1`
- **Erwartung:** Dialog "AUSWAHL KUNDEN" öffnet sich
- **Prüfen:** 
  - Dialog erscheint
  - Tabs: ALLE, INTERESSENTEN, AKTIVE, EHEMALIGE
  - Suchfeld ist vorhanden

### Schritt 4: Kunde auswählen
- **Aktion:** 
  1. Geben Sie einen Suchbegriff ein (z.B. "Test" oder "Kunde")
  2. Wählen Sie einen Kunden aus der Liste aus
  3. Klicken Sie auf "OK"
- **Erwartung:** 
  - Dialog schließt sich
  - Debitor-Kto. Feld wird gefüllt
  - Kundenadresse wird angezeigt

### Schritt 5: Artikelauswahl öffnen (Strg+F2)
- **Aktion:** Drücken Sie `Strg+F2`
- **Erwartung:** Dialog "Artikel suchen" öffnet sich
- **Prüfen:** 
  - Dialog erscheint
  - Matchcode-Feld ist vorhanden
  - Tabs: alle Artikel, Artikel-Gruppe, etc.

### Schritt 6: Artikel auswählen
- **Aktion:** 
  1. Geben Sie einen Suchbegriff ein (z.B. "Artikel" oder "Test")
  2. Wählen Sie einen Artikel aus der Liste aus
  3. Klicken Sie auf "OK"
- **Erwartung:** 
  - Dialog schließt sich
  - Artikel-Nr. und Bezeichnung werden in Positions-Details gefüllt
  - Listenpreis wird geladen

### Schritt 7: Menge eingeben
- **Aktion:** 
  1. Geben Sie eine Menge ein (z.B. "10")
  2. Drücken Sie Tab oder Enter
- **Erwartung:** 
  - Netto-Preis und Betrag werden berechnet
  - MWSt wird berechnet

### Schritt 8: Position OK (Strg+F3)
- **Aktion:** Drücken Sie `Strg+F3` (oder klicken Sie auf "Zeile OK")
- **Erwartung:** 
  - Position wird in Positionen-Grid übernommen
  - Summen werden aktualisiert
  - Nächste Position (20) wird vorbereitet

### Schritt 9: Beleg speichern (Strg+F4)
- **Aktion:** Drücken Sie `Strg+F4` (oder klicken Sie auf "Speichern")
- **Erwartung:** 
  - Toast-Nachricht: "Lieferschein erfolgreich gespeichert"
  - Lieferschein-Nr. bleibt erhalten
  - Status bleibt "Draft"

### Schritt 10: Beleg drucken (Strg+F5)
- **Aktion:** Drücken Sie `Strg+F5` (oder klicken Sie auf "LS drucken")
- **Erwartung:** 
  - Dialog "LIEFERSCHEIN DRUCKEN" öffnet sich
  - Formularvorlage kann ausgewählt werden
  - Drucker kann ausgewählt werden

### Schritt 11: Druck bestätigen
- **Aktion:** 
  1. Wählen Sie Formularvorlage (z.B. "W00005")
  2. Klicken Sie auf "Druck OK - beenden"
- **Erwartung:** 
  - Dialog schließt sich
  - Beleg wird gebucht (Status: "gedruckt")
  - Toast-Nachricht: "Lieferschein erfolgreich gedruckt und gebucht"

### Schritt 12: Shortcuts-Panel (Strg+N)
- **Aktion:** Drücken Sie `Strg+N`
- **Erwartung:** 
  - Shortcuts-Panel erscheint am rechten Bildschirmrand
  - Alle Shortcuts sind aufgelistet

## Fehlerbehebung

### Dialog öffnet sich nicht
- **Prüfen:** Browser-Konsole auf Fehler (F12)
- **Prüfen:** Network-Tab auf API-Fehler
- **Lösung:** Seite neu laden (F5)

### Shortcut funktioniert nicht
- **Prüfen:** Fokus ist auf der Seite (nicht in einem Input-Feld)
- **Prüfen:** Kein anderer Shortcut-Handler ist aktiv
- **Lösung:** Seite neu laden (F5)

### API-Fehler
- **Prüfen:** Backend läuft (Docker)
- **Prüfen:** API-Endpunkte sind erreichbar
- **Lösung:** Backend neu starten

## Screenshots

Alle Screenshots wurden gespeichert in:
- `workflow-01-start.png` - Initialer Zustand
- `workflow-02-customer-dialog-open.png` - Nach Strg+F1
- `workflow-03-article-dialog-open.png` - Nach Strg+F2
- `workflow-04-position-ok.png` - Nach Strg+F3
- `workflow-05-saved.png` - Nach Strg+F4
- `workflow-06-print-dialog.png` - Nach Strg+F5

## Nächste Schritte

Nach dem Test:
1. **Fehler dokumentieren:** Alle gefundenen Fehler notieren
2. **Verbesserungen vorschlagen:** UX-Verbesserungen notieren
3. **Performance prüfen:** Ladezeiten messen
4. **Browser-Kompatibilität:** In verschiedenen Browsern testen

