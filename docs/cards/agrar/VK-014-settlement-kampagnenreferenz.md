# Card: VK-014 - Settlement-Kampagnenreferenz statt Zeitfenster-Proxy

## 1. Einordnung
- Prozessbereich: Agrar / Harvest-to-Settlement
- Workflow: Kampagnenabschluss / Settlement-Anlage
- Teilprozess: Eindeutige Zuordnung von Settlements zu Erntefenster-Kampagnen
- Rolle(n): Agrar-Sachbearbeitung, Betriebsleitung
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Settlements einer Kampagne explizit und nicht nur ueber technische Zeitfenster zuordnen.
- Fachliche Beschreibung: Die Settlement-Anlage uebernimmt `campaign_id` aus dem Kampagnenkontext; Read- und Listenansichten nutzen diese Referenz bevorzugt.
- Geschaeftlicher Nutzen: Kampagnenabschluss wird belastbarer, nachvollziehbarer und weniger fehleranfaellig bei Ueberlappungen oder Nachbuchungen.

## 3. Start / Trigger
- Startbedingung: Anwender kommt aus dem Kampagnenabschluss in die Abrechnungsmaske oder liest Settlements im Kampagnenkontext.
- Ausloeser: Kampagnenbezogene Settlement-Anlage oder Kampagnen-Read-Modell
- Startpunkt-Typ:
  - [x] Standardstart
  - [x] Alternativstart
  - [ ] Externer Import
  - [ ] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: Query-Parameter `campaignId` aus `erntefenster-konfig.tsx`

## 4. Vorbedingungen
- Muss vorhanden sein: Kampagne mit `id` in den Tenant-Settings
- Muss geprueft sein: Settlement-Contract und Datenbankschema muessen `campaign_id` akzeptieren
- Ausschlussbedingungen: keine Kampagne im Kontext
- Abhaengige Vorprozesse: `VK-013` Kampagnenabschluss ueber Standardmasken

## 5. Eingaben
- Stammdaten: `campaign_id`, `campaignName`, `campaignStart`, `campaignEnd`
- Bewegungsdaten: Settlement-Werte wie Lieferant, Artikel, Mengen und Abzuege
- Pflichtfelder: `supplier_id`, Mengen, Preis; `campaign_id` nur im Kampagnenkontext
- Optionale Felder: `campaign_id` bei freier Settlement-Anlage
- Vorbelegte Werte: `campaign_id` aus Query-Parametern
- Externe Datenquellen: `/api/v1/admin/erntefenster-campaigns`, `/api/v1/agrar/settlements`

## 6. UI / Systembezug
- Seite / Maske: `agrar/erntefenster-konfig.tsx`, `annahme/abrechnung.tsx`
- Dialog / Untermaske: keine
- Button / Aktion: `Settlement-Abschluss pruefen`, `Settlement speichern`
- Status vor Ausfuehrung: Kampagnenliste oder Settlement-Entwurf
- Status nach Ausfuehrung: Settlement mit Kampagnenreferenz gespeichert oder referenzbasiert gefiltert
- Sichtbare Felder: Kampagnenkarte, Settlement-Liste, KPI
- Fehlende Felder / Aktionen: keine UI fuer nachtraegliche Aenderung von `campaign_id`

## 7. Aktion
- Benutzeraktion: Settlement aus Kampagnenkontext speichern oder Kampagnenabschluss lesen.
- Systemaktion: `campaign_id` persistieren und bei Reads im Frontend bevorzugt fuer die Zuordnung verwenden.
- Automatische Folgeaktion: Legacy-Settlements ohne Referenz werden weiterhin ueber `created_at` eingeordnet.
- Synchron / asynchron: asynchron ueber API und React Query
- Notwendige Bestaetigung: keine

## 8. Geschaeftsregeln
- Validierungsregeln: Bei vorhandener `campaign_id` ist diese die kanonische Zuordnungsbasis.
- Preis-/Mengenlogik: unveraendert
- Berechtigungen: keine zusaetzlichen Rollenregeln
- Pflichtpruefungen: Query-Context darf `campaign_id` nur additiv weitergeben
- Sonderregeln: Legacy-Fallback ueber `created_at` nur wenn `campaign_id` fehlt
- Verbote / Sperren: kein Ueberschreiben einer bestehenden `campaign_id` im Slice

## 9. Ergebnisse
- Output-Daten: Settlement mit `campaign_id`
- Erzeugte Belege / Datensaetze: keine neuen Dokumenttypen, nur erweiterter Settlement-Contract
- Geaenderte Status: keine neuen Stati
- Folgeprozess Standard: Kampagnenabschluss liest jetzt referenzbasiert
- Folgeprozess alternativ: Alt-Daten bleiben ueber Zeitfenster sichtbar

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: Hat das Settlement bereits `campaign_id`?
- Moegliche Alternativen: Referenzpfad oder Legacy-Fallback
- Ruecksprung moeglich zu: Kampagnenliste / Abrechnungsmaske
- Schleife moeglich: wiederholtes Lesen nach neuen Settlements
- Abbruchpfad: kein Kampagnenkontext, dann normales Settlement ohne Referenz
- Sprungpfad: Kampagnen-CTA -> Settlement-Maske
- Direkteinstieg moeglich: ja, ueber Query-Parameter

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: Alt-Daten ohne `campaign_id`, Kampagnenkontext fehlt, falsche Kampagnen-ID im Query-String
- Fachliche Sonderfaelle: Ueberlappende Kampagnenfenster
- Technische Sonderfaelle: bestaehende Datenbank ohne neues Schema vor Migration
- Teilmengen / Splittung: mehrere Settlements derselben Kampagne bleiben moeglich
- Storno / Korrektur: unveraendert auf Settlement-Ebene
- Ruecknahme / Retoure: nicht Teil dieses Slices
- Preisabweichung: unveraendert
- Bestandsproblem: nicht Teil dieses Slices
- Medienbruch moeglich: nur fuer Alt-Daten ohne Referenz

## 12. CRUD-Pruefung
- Create moeglich: ja, jetzt mit `campaign_id`
- Read / Suchen moeglich: ja, referenzbasiert mit Fallback
- Update moeglich: nicht fuer `campaign_id` im Slice
- Delete fachlich zulaessig: nein
- Storno statt Delete: ja
- Historisierung vorhanden: Settlement-Historie ja, Kampagnenzuordnung ab jetzt im Datensatz
- Audit / Nachvollziehbarkeit: verbessert gegenueber reinem Datumsfenster
- UI vollstaendig fuer CRUD: teilweise, da `campaign_id` nicht nachtraeglich editierbar ist
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Kampagnenzuordnung erfolgt explizit und reproduzierbar.
- Ist-Umsetzung: `campaign_id` ist im Contract und Frontend wirksam.
- Abweichung: Alt-Daten brauchen weiterhin Datumsfenster-Fallback.
- Fehlende Umsetzung: Backfill oder Repair-Flow fuer Bestandsdaten
- Unklare Umsetzung: keine
- Workaround aktuell noetig: nur fuer Alt-Settlements ohne Referenz

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Ohne Backfill bleiben historische Settlements teils weiterhin vom Fallback abhaengig.
- Auswirkung im Tagesgeschaeft: Neue Kampagnen sind sauber, historische Kampagnen ggf. nur teilsauber.
- Betroffene Rollen: Agrar-Sachbearbeitung, Betriebsleitung
- Betroffene Folgeprozesse: Kampagnenabschluss, Reporting

## 15. Empfehlung
- Empfohlene Massnahme: Folge-Slice fuer Alt-Daten-Backfill oder nachtraegliche Zuordnungspruefung.
- Fachlich: neue Settlements nur noch mit Kampagnenreferenz anlegen, wenn aus Kampagnenkontext gestartet.
- Technisch: `campaign_id` auch serverseitig in Listenreads aktiver nutzen.
- UI-seitig: optional spaeter Sichtbarkeit der Kampagnen-ID in der Settlement-Detailansicht ergaenzen.
- Prioritaet der Umsetzung: hoch
- Sofortmassnahme: referenzbasierte Persistenz und Read-Logik
- Spaetere Optimierung: Repair-Workflow fuer Alt-Daten

## 16. Annahmen
- Annahme 1: Eine String-Referenz auf die Tenant-Settings-Kampagne reicht fachlich fuer den aktuellen Scope.
- Annahme 2: Legacy-Datumsfenster-Fallback ist bis zu einem Backfill gewollt.
- Offene Fragen: Soll `campaign_id` spaeter manuell korrigierbar sein?

## 17. Testhinweise
- Positiver Testfall: Settlement aus Kampagnenkontext speichern und danach nur unter dieser Kampagne wiederfinden.
- Negativer Testfall: Settlement mit anderer `campaign_id` darf trotz passendem Datum nicht unter der falschen Kampagne erscheinen.
- Edge-Case-Test: Legacy-Settlement ohne `campaign_id` bleibt ueber das Datumsfenster sichtbar.
- Browser-Use-Pruefschritt: Kampagnenkontext oeffnen, Settlement speichern, anschliessend Kampagnenabschluss erneut pruefen.
- Erwartetes Ergebnis: Neue Settlements werden referenzbasiert zugeordnet; Alt-Daten bleiben sichtbar.
