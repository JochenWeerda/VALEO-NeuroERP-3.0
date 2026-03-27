# Browser-Use Checklists

## Zweck

Diese Checklisten schaerfen die UI-, CRUD- und Live-Betriebspruefung fuer Workflow-Cards.

## Pflichtfragen pro Card

- Kann ein Anwender diesen Schritt real in der UI ausfuehren?
- Gibt es alle noetigen Felder, Buttons und Statuswechsel?
- Ist Create moeglich?
- Ist Read / Suchen moeglich?
- Ist Update moeglich?
- Ist Delete fachlich zulaessig oder braucht es Storno/Abschluss?
- Sind alle Pflichtdaten erfassbar?
- Gibt es fachlich sinnvolle Standardwerte?
- Gibt es Sackgassen oder unlogische Uebergaenge?
- Was passiert bei Abbruch, Teilbearbeitung oder Korrektur?
- Ist der Schritt fuer den Live-Betrieb belastbar?

## Browser-Use-Pruefreihenfolge

1. Einstieg in den Workflow
2. Datensatz anlegen
3. Datensatz wiederfinden
4. Bearbeiten / fortsetzen
5. Statuswechsel ausloesen
6. Sonderfall testen
7. Korrektur / Storno / Ruecksprung pruefen
8. Folgeprozess oeffnen

## Besonderer Fokus

- Pflichtfelder und Standardwerte
- Uebergabe zwischen Masken
- Sichtbarkeit kritischer Felder
- Teilmengen
- Preis- und Mengenkorrekturen
- externe Uebernahmen
- Statusfortschreibung
- Auditierbarkeit

## Procure-to-Pay: Bestellung anlegen

### Direktbestellung aus Flow Spine

1. `Procure-to-Pay` im Flow Spine oeffnen und in die Bestellmaske wechseln.
2. Workflow-Handover-Banner, Vorgangsnummer und Einstiegsart pruefen.
3. Im Lieferanten-Schritt `Weiter` ohne Lieferant klicken.
4. Erwartung: Fehler-Toast, kein Schrittwechsel.
5. Lieferant und Liefertermin erfassen und in den Positionsschritt wechseln.
6. Im Positionsschritt `Weiter` ohne gueltigen Artikel klicken.
7. Erwartung: Fehler-Toast, kein Schrittwechsel.
8. Position ergaenzen, bis zur Zusammenfassung wechseln und speichern.
9. Rueckkehr in die Bestellliste und Wiederauffindbarkeit pruefen.

### Vorbelegung aus Bedarfsmeldung, RFQ oder Vertrag

1. Bestellmaske mit `?requisitionId=...`, `?rfqId=...` oder `?contractId=...` aufrufen.
2. Vorbelegungs-Badge, uebernommene Felder und Erfolgstoast pruefen.
3. Wenn Lieferant nicht aus der Quelle kommt, `Weiter` ohne Nachpflege klicken.
4. Erwartung: Schrittvalidierung blockiert im Lieferanten-Schritt.
5. Fehlende Pflichtdaten ergaenzen und den Wizard-Pfad bis zur Zusammenfassung durchlaufen.
6. Ruecksprung in fruehere Schritte testen; Vorbelegungsdaten muessen editierbar bleiben.
7. Bestellung speichern und Rueckkehr in die Bestellliste pruefen.

### Fehlerpfad bei gescheiterter Vorbelegung

1. Vorbelegung mit absichtlich ungueltiger `requisitionId`, `rfqId` oder `contractId` ausloesen.
2. Erwartung: Kein Crash, kein Schrittwechsel, Fehler-Toast sichtbar.
3. Maske muss trotz Fehler weiter editierbar bleiben.

## Harvest-to-Settlement: Ernte-Annahme

### Handover in die Spezialmaske

1. `Harvest-to-Settlement` im Flow Spine oeffnen und Ernte-Annahme starten.
2. Workflow-Handover-Banner, Vorgangsnummer und Einstiegsart pruefen.
3. Bemerkungsfeld auf `Workflow-Vorgang`, `Einstieg`, `Anlieferer` und `Subject` pruefen.
4. Erwartung: Maske bleibt stabil renderbar; kein Re-Render-Loop.
5. Maske schliessen und erneut ueber denselben Flow-Fall oeffnen.
6. Erwartung: Banner und Bemerkungen bleiben reproduzierbar.

### Erster Erfassungs- und Ladepfad

1. Neue Ernte-Annahme mit Harvest-Handover oeffnen und einen ersten Speicherversuch vorbereiten.
2. Bestehende Ernte-Annahme per ID oeffnen.
3. Erwartung: Handover und Edit-Mode koennen nebeneinander bestehen; Felder bleiben bedienbar.

### VK-011: Qualitaets-Check -> Ernte-Annahme

1. LKW-Registrierung oeffnen und im ersten Schritt ohne Kennzeichen auf `Weiter` klicken.
2. Erwartung: destructive Toast, kein Schrittwechsel.
3. Kennzeichen erfassen, in Schritt 2 ohne Lieferant oder Artikel erneut `Weiter` klicken.
4. Erwartung: Wizard blockiert erneut und bleibt im Lieferungs-Schritt.
5. LKW vollstaendig registrieren, in der Warteschlange zur Qualitaetspruefung gehen und mit `freigegeben` oder `bedingt` abschliessen.
6. Erwartung: Navigation direkt in `/agrar/ernte-annahme-erfassung` mit Query-Handover.
7. Fahrzeug-Kennzeichen, Artikelname sowie Bemerkungen fuer Lieferschein, Qualitaetspruefung und Qualitaetsprotokoll pruefen.
8. Browser neu laden.
9. Erwartung: Vorbelegung bleibt restart-sicher erhalten.

### VK-013: Ernte-Kampagnenabschluss

1. `Erntefenster-Konfiguration` oeffnen und eine Kampagne mit vorhandenem Zeitraum aufrufen.
2. Erwartung: Jede Kampagne zeigt Abschlussstatus, Anzahl Settlements, Netto gesamt, offene Settlements und Abzuege gesamt.
3. Kampagne mit mindestens einem offenen oder noch nicht verbuchten Settlement pruefen.
4. Erwartung: Status `Abschluss offen`.
5. Auf `Settlement-Abschluss pruefen` klicken.
6. Erwartung: Navigation nach `/annahme/abrechnung` mit `campaignName`, `campaignStart` und `campaignEnd`.
7. In der Abrechnungsmaske Kampagnenkarte und gefilterte Settlement-Liste pruefen.
8. Erwartung: Nur Settlements innerhalb des Kampagnenfensters sind sichtbar; Datensaetze ausserhalb des Fensters fehlen.
9. Optional einen offenen Settlement-Datensatz freigeben oder verbuchen und die Kampagnenliste erneut laden.
10. Erwartung: KPI und Abschlussstatus aktualisieren sich konsistent.
