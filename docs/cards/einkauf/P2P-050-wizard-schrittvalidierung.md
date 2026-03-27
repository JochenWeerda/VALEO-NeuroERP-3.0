# Card: P2P-050 - Wizard-Schrittvalidierung in der Bestellmaske

## 1. Einordnung
- Prozessbereich: Einkauf
- Workflow: Procure-to-Pay
- Teilprozess: Schrittvalidierung im Bestell-Wizard
- Rolle(n): Einkauf, Disposition, operativer Sachbearbeiter
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Fehler frueh im Wizard stoppen statt erst beim finalen Speichern.
- Fachliche Beschreibung: Vor dem Wechsel von `Lieferant` nach `Positionen` sowie von `Positionen` nach `Lieferung` werden Pflichtfelder geprueft und bei Fehlern ueber Toasts rueckgemeldet.
- Geschaeftlicher Nutzen: Weniger Sackgassen in spaeteren Schritten, geringere Fehlbedienung im Tagesgeschaeft.

## 3. Start / Trigger
- Startbedingung: Nutzer befindet sich in der Bestellmaske und klickt auf `Weiter`.
- Ausloeser: Wizard-Navigation vorwaerts.
- Startpunkt-Typ:
  - [ ] Standardstart
  - [x] Alternativstart
  - [ ] Externer Import
  - [x] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: Standard-Wizard in `Bestellung anlegen`.

## 4. Vorbedingungen
- Muss vorhanden sein: Aktiver Wizard-Schritt und erfasste Formulardaten.
- Muss geprueft sein: Lieferant und Liefertermin bzw. gueltige Positionen.
- Ausschlussbedingungen: Rueckwaertsnavigation wird nicht blockiert.
- Abhaengige Vorprozesse: keine; gilt fuer Direktstart und Vorbelegung.

## 5. Eingaben
- Stammdaten: Lieferant.
- Bewegungsdaten: Liefertermin, Positionen.
- Pflichtfelder: Lieferant, Liefertermin, mindestens eine Position mit Artikel und Menge > 0.
- Optionale Felder: Lieferadresse, Notizen, Incoterms, Zahlungsbedingung.
- Vorbelegte Werte: duerfen aus Workflow-Handover oder Vorbelegung stammen.
- Externe Datenquellen: keine zusaetzlichen fuer diesen Schritt.

## 6. UI / Systembezug
- Seite / Maske: `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`
- Dialog / Untermaske: `packages/frontend-web/src/components/patterns/Wizard.tsx`
- Button / Aktion: `Weiter`
- Status vor Ausfuehrung: Schritt offen, Daten unvollstaendig oder vollstaendig.
- Status nach Ausfuehrung: Entweder naechster Schritt aktiv oder Fehler-Toast sichtbar.
- Sichtbare Felder: Lieferant, Liefertermin, Positionen.
- Fehlende Felder / Aktionen: Fehler-Toast bei fehlgeschlagener Vorbelegung bleibt weiterhin optional.

## 7. Aktion
- Benutzeraktion: `Weiter` klicken.
- Systemaktion: `Wizard` ruft additiv `getStepValidationError(stepId)` auf.
- Automatische Folgeaktion: Bei Fehler bleibt der Nutzer im aktuellen Schritt.
- Synchron / asynchron: asynchron kompatibel, aktuell synchron genutzt.
- Notwendige Bestaetigung: keine.

## 8. Geschaeftsregeln
- Validierungsregeln: Lieferant und Liefertermin sind im ersten Schritt Pflicht; Positionen muessen Artikel, Menge > 0 und Preis >= 0 haben.
- Preis-/Mengenlogik: Preise duerfen null, aber nicht negativ sein.
- Berechtigungen: unveraendert.
- Pflichtpruefungen: vor jedem Vorwaertsschritt und nochmals vor `Abschliessen`.
- Sonderregeln: Vorwaertssprung per Step-Klick wird ebenfalls vom Wizard-Hook abgefangen.
- Verbote / Sperren: Kein Vorwaertswechsel mit leeren Pflichtdaten.

## 9. Ergebnisse
- Output-Daten: unveraenderter Bestellentwurf im Client-State.
- Erzeugte Belege / Datensaetze: keine, solange nur Schrittwechsel erfolgt.
- Geaenderte Status: Wizard-Schritt aktiv/inaktiv.
- Folgeprozess Standard: Lieferung, Zusammenfassung, Speichern.
- Folgeprozess alternativ: Ruecksprung und Korrektur.

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: Validierung erfolgreich?
- Moegliche Alternativen: Fehler-Toast statt Schrittwechsel.
- Ruecksprung moeglich zu: allen frueheren Schritten.
- Schleife moeglich: ja, Korrektur und erneutes `Weiter`.
- Abbruchpfad: `Abbrechen` zur Bestellliste.
- Sprungpfad: Klick auf spaetere Steps nur bei gueltigem aktuellem Schritt.
- Direkteinstieg moeglich: ja, ueber Flow-Spine- oder Vorbelegungsparameter.

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: leerer Lieferant, fehlender Liefertermin, leere Position.
- Fachliche Sonderfaelle: Vorbelegte Anfrage ohne Lieferant blockiert bewusst im ersten Schritt.
- Technische Sonderfaelle: Wizard-Hook bleibt optional und darf bestehende Wizards nicht brechen.
- Teilmengen / Splittung: nicht Teil dieses Slices.
- Storno / Korrektur: Korrektur im Wizard durch Ruecksprung.
- Ruecknahme / Retoure: nicht Teil dieses Slices.
- Preisabweichung: negativer Preis blockiert Schrittwechsel.
- Bestandsproblem: nicht Teil dieses Slices.
- Medienbruch moeglich: nein, da gleiche Standardmaske verwendet wird.

## 12. CRUD-Pruefung
- Create moeglich: ja
- Read / Suchen moeglich: nicht Teil dieses Slices
- Update moeglich: ja
- Delete fachlich zulaessig: nein
- Storno statt Delete: ja, spaeter im Prozess
- Historisierung vorhanden: nur bei echtem Speichern
- Audit / Nachvollziehbarkeit: Validierungsblock ist ueber Tests abgesichert
- UI vollstaendig fuer CRUD: fuer den Anlagepfad jetzt belastbarer
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Nutzer kann nur mit sinnvollen Daten in spaetere Schritte wechseln.
- Ist-Umsetzung: Schrittvalidierung im Standard-Wizard plus P2P-spezifische Regeln umgesetzt.
- Abweichung: keine fuer den P2P-Anlagepfad dieses Slices.
- Fehlende Umsetzung: Fehler-Toast fuer fehlgeschlagene Vorbelegung bleibt separat.
- Unklare Umsetzung: keine.
- Workaround aktuell noetig: keiner.

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Vor diesem Slice konnten Anwender leere Pflichtschritte passieren und Fehler erst spaet sehen.
- Auswirkung im Tagesgeschaeft: Verwirrung im Wizard und spaete Fehlererkennung.
- Betroffene Rollen: Einkauf, Disposition.
- Betroffene Folgeprozesse: Bestellung anlegen, Freigabevorbereitung.

## 15. Empfehlung
- Empfohlene Massnahme: Generische Schrittvalidierung ueber den Standard-Wizard beibehalten.
- Fachlich: Lieferant und Positionen bleiben harte Mindestanforderungen vor dem Abschluss.
- Technisch: Weitere prozesskritische Wizards auf denselben Hook umstellen statt lokale Sonderlogik aufzubauen.
- UI-seitig: Fehler direkt im Schritt sichtbar oder als Toast ausgeben; P2P nutzt aktuell Toast.
- Prioritaet der Umsetzung: sofort
- Sofortmassnahme: in diesem Slice umgesetzt
- Spaetere Optimierung: Inline-Fehlhinweise und Fehler-Toast fuer Vorbelegungsfehler.

## 16. Annahmen
- Annahme 1: Rueckwaertsnavigation soll nicht durch Validierung blockiert werden.
- Annahme 2: Lieferadresse und Notizen bleiben optional.
- Offene Fragen: Soll der generische Wizard mittelfristig auch Inline-Fehlerzustand pro Step visualisieren?

## 17. Testhinweise
- Positiver Testfall: Mit Lieferant, Liefertermin und gueltiger Position funktioniert der Schrittwechsel bis zum Abschluss.
- Negativer Testfall: Ohne Lieferant bleibt der Nutzer im ersten Schritt und erhaelt einen Fehler-Toast.
- Edge-Case-Test: Workflow-Handover ohne Position darf nicht in die Lieferung springen, bis eine Position gepflegt ist.
- Browser-Use-Pruefschritt: Bestellung anlegen oeffnen, `Weiter` ohne Lieferant klicken, Fehler pruefen, Daten ergaenzen, erneut weitergehen.
- Erwartetes Ergebnis: Kein Vorwaertsschritt mit unvollstaendigen Pflichtdaten; Abschluss bleibt moeglich, sobald alle Pflichtdaten vorhanden sind.
