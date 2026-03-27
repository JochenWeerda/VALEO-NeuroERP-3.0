# Card: P2P-020 - Direktbestellung in Standardmaske erfassen

## 1. Einordnung
- Prozessbereich: Einkauf
- Workflow: Procure-to-Pay
- Teilprozess: Direktbestellung
- Rolle(n): Einkauf, Disposition, operativer Sachbearbeiter
- Prioritaet: hoch
- Status: in arbeit

## 2. Fachlicher Zweck
- Ziel des Schrittes: Einen Flow-Spine-Beschaffungsvorgang in eine belastbare Bestellung ueberfuehren.
- Fachliche Beschreibung: Nach dem Einstieg aus dem Prozessraum werden Lieferant, Positionen, Termine, Preise, Lieferadresse und Notizen in der Standardmaske gepflegt.
- Geschaeftlicher Nutzen: Beschaffung kann ohne Medienbruch direkt vom Workflow in den Beleg uebergehen.

## 3. Start / Trigger
- Startbedingung: Ein `Procure-to-Pay`-Vorgang wurde im Flow Spine angelegt.
- Ausloeser: Klick auf den Flow-Spine-Start fuer `Direktbestellung`, `Bedarfsmeldung` oder `Rahmenabruf`.
- Startpunkt-Typ:
  - [x] Standardstart
  - [x] Alternativstart
  - [ ] Externer Import
  - [ ] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: `FlowSpineWorkspace` erzeugt URL-Parameter fuer die Bestellmaske.

## 4. Vorbedingungen
- Muss vorhanden sein: Workflow-Kontext oder manueller Einstieg in `/einkauf/bestellungen/neu`.
- Muss geprueft sein: Lieferant und mindestens eine valide Position.
- Ausschlussbedingungen: Keine fachlich nutzbare Anlage ohne Lieferant oder leerer Position.
- Abhaengige Vorprozesse: Optional Requisition, Vertrag oder RFQ fuer Vorbelegung.

## 5. Eingaben
- Stammdaten: Lieferant, Zahlungsbedingung, Incoterms, Lieferadresse.
- Bewegungsdaten: Liefertermin, Positionen, Mengen, Preise.
- Pflichtfelder: Lieferant, Liefertermin, mindestens eine Position mit Artikel und Menge > 0.
- Optionale Felder: Notizen, Lieferadresse, Incoterms, Referenzen auf Requisition, Vertrag, RFQ.
- Vorbelegte Werte: Liefertermin +14 Tage, `net30`, eine leere Positionszeile, Workflow-Notizen aus Handover.
- Externe Datenquellen: Optional `/api/purchase-workflow/requisitions/{id}`, `/api/contracts/{id}`, `/api/purchase-workflow/rfqs/{id}`.

## 6. UI / Systembezug
- Seite / Maske: `packages/frontend-web/src/pages/einkauf/bestellung-anlegen.tsx`
- Dialog / Untermaske: Wizard mit Schritten Lieferant, Positionen, Lieferung, Zusammenfassung.
- Button / Aktion: `Abschliessen` im Wizard.
- Status vor Ausfuehrung: Flow-Spine-Vorgang vorhanden, Bestellung noch nicht gespeichert.
- Status nach Ausfuehrung: Bestellung als `ENTWURF` angelegt, Rueckkehr zur Bestellliste.
- Sichtbare Felder: Lieferant, Liefertermin, Zahlungsbedingung, Incoterms, Lieferadresse, Positionen, Notizen.
- Fehlende Felder / Aktionen: Inline-Fehlhinweise pro Schritt fehlen weiterhin; Toast-Validierung ist vorhanden.

## 7. Aktion
- Benutzeraktion: Bestellkopf und Positionen pflegen, dann Wizard abschliessen.
- Systemaktion: Frontend validiert Mindestdaten und sendet `POST /api/v1/purchase-orders`.
- Automatische Folgeaktion: Navigation zur Bestellliste.
- Synchron / asynchron: synchron mit API-Call.
- Notwendige Bestaetigung: keine separate Bestaetigung.

## 8. Geschaeftsregeln
- Validierungsregeln: Lieferant darf nicht leer sein; jede Position benoetigt Artikel und Menge > 0; Preis darf nicht negativ sein.
- Preis-/Mengenlogik: Summen werden clientseitig angezeigt, Steuer standardmaessig `19%`.
- Berechtigungen: Einkauf-Schreibrechte werden vorausgesetzt.
- Pflichtpruefungen: Workflow-Handover darf keine fachlich leere Bestellung erzeugen.
- Sonderregeln: Lieferadresse wird ueber `shippingAddress` an den aktuellen Backend-Contract uebergeben.
- Verbote / Sperren: Kein fachlich leerer Entwurf ueber den Direktbestellpfad.

## 9. Ergebnisse
- Output-Daten: Neue Bestellung mit serverseitig vergebener Bestellnummer.
- Erzeugte Belege / Datensaetze: Purchase Order im Compat-Contract.
- Geaenderte Status: `ENTWURF`.
- Folgeprozess Standard: Freigabe, Versand an Lieferant, Wareneingang.
- Folgeprozess alternativ: Ruecksprung zur Korrektur oder spaetere Bearbeitung.

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: Sind Pflichtdaten und Positionen vollstaendig?
- Moegliche Alternativen: Bedarfsmeldung oder Rahmenabruf mit Vorbelegung.
- Ruecksprung moeglich zu: Vorige Wizard-Schritte.
- Schleife moeglich: Ja, Korrektur bis valide Daten vorliegen.
- Abbruchpfad: Wizard abbrechen und zur Bestellliste zurueck.
- Sprungpfad: Manueller Einstieg ohne Flow Spine bleibt moeglich.
- Direkteinstieg moeglich: Ja, ueber `/einkauf/bestellungen/neu`.

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: Leerer Lieferant, Position ohne Artikel, Menge `0`, negativer Preis.
- Fachliche Sonderfaelle: Bedarf wird spaeter aus Vertrag oder RFQ vorbelegt.
- Technische Sonderfaelle: API-Fehler beim Speichern; instabiler Workflow-Handover ohne memoisierten Kontext.
- Teilmengen / Splittung: Noch nicht Teil dieses Slice.
- Storno / Korrektur: Nach Speicherung ueber Bestelldetail und Storno.
- Ruecknahme / Retoure: Nachgelagerter Prozess.
- Preisabweichung: Manuell pflegbar, aber ohne gesonderte Warnlogik.
- Bestandsproblem: Nicht Teil der Bestellanlage.
- Medienbruch moeglich: reduziert durch Workflow-Handover-Banner und Vorbelegung.

## 12. CRUD-Pruefung
- Create moeglich: ja
- Read / Suchen moeglich: ja, ueber Bestellliste
- Update moeglich: ja, ueber Detailmaske
- Delete fachlich zulaessig: nein
- Storno statt Delete: ja
- Historisierung vorhanden: teilweise, ueber Detailmaske/Audit
- Audit / Nachvollziehbarkeit: vorhanden, aber nicht Teil dieses Slice
- UI vollstaendig fuer CRUD: fuer den Anlagepfad belastbar; Schrittvalidierung ist ueber `P2P-050` nachgezogen
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Flow-Spine-Fall startet sauberen Handover in eine valide Direktbestellung.
- Ist-Umsetzung: Handover und Standardmaske vorhanden.
- Abweichung: Vor diesem Slice fehlten Mindestvalidierung, stabiler Handover-Kontext und die Lieferadresse traf den Persistenz-Contract nicht.
- Fehlende Umsetzung: vertiefte Alternativpfad-Checks und weiterfuehrende Browser-Use-Doku fuer Vorbelegungsvarianten.
- Unklare Umsetzung: Serverseitige Pflichtfeldvalidierung im Compat-Endpoint.
- Workaround aktuell noetig: keiner nach dem Frontend-Fix fuer den Direktpfad.

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Ohne Frontend-Haertung konnten Workflow-Einstiege in eine Render-Schleife laufen, leere Beschaffungsvorgaenge als Bestellung gespeichert werden und die Lieferadresse verlor sich im Backend-Contract.
- Auswirkung im Tagesgeschaeft: Fehlerhafte oder unvollstaendige Bestellentwuerfe, Nacharbeit und Medienbruch.
- Betroffene Rollen: Einkauf, Disposition.
- Betroffene Folgeprozesse: Freigabe, Lieferantenkommunikation, Wareneingang.

## 15. Empfehlung
- Empfohlene Massnahme: Mindestvalidierung und konsistente Lieferadress-Uebergabe direkt in der Standardmaske.
- Fachlich: Keine neue Spezialmaske, sondern Standardpfad absichern.
- Technisch: `shippingAddress` im Payload setzen und Submission mit klarer Fehlermeldung blockieren.
- UI-seitig: Validierungsfehler als Toast sichtbar machen.
- Prioritaet der Umsetzung: sofort
- Sofortmassnahme: in diesem Slice umgesetzt
- Spaetere Optimierung: Inline-Fehlhinweise im Wizard und weiterfuehrende Vorbelegungs-Checks.

## 16. Annahmen
- Annahme 1: `shippingAddress` ist das kanonische Persistenzfeld im aktuellen Purchase-Order-Endpoint.
- Annahme 2: Direktbestellung ist der priorisierte Standardstart fuer den ersten P2P-Workflow-Slice.
- Offene Fragen: Soll der Backend-Compat-Endpoint spaeter dieselbe Mindestvalidierung erzwingen?

## 17. Testhinweise
- Positiver Testfall: Workflow-Handover fuellt Lieferant/Notizen vor, valide Position wird erfasst, Bestellung wird gespeichert.
- Negativer Testfall: Abschluss ohne Lieferant oder mit leerer Position wird blockiert.
- Edge-Case-Test: Lieferadresse aus der Standardmaske landet im API-Payload unter `shippingAddress`.
- Browser-Use-Pruefschritt: Flow Spine oeffnen, Direktbestellung starten, Pflichtdaten pflegen, speichern, Rueckkehr in Bestellliste pruefen.
- Erwartetes Ergebnis: Kein leerer Entwurf; Lieferadresse und Workflow-Kontext bleiben im Belegfluss erhalten.
