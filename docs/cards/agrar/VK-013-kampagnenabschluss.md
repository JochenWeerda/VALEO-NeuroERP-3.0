# Card: VK-013 - Ernte-Kampagnenabschluss ueber bestehende Standardmasken

## 1. Einordnung
- Prozessbereich: Agrar / Harvest-to-Settlement
- Workflow: Erntefenster -> Settlement-Pruefung -> Kampagnenabschluss
- Teilprozess: Kampagnenbezogene Gesamtsicht und Abschlussreife
- Rolle(n): Disposition, Agrar-Sachbearbeitung, Betriebsleitung
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Eine Erntekampagne ueber alle zugehoerigen Settlements fachlich pruefbar machen.
- Fachliche Beschreibung: Die Kampagnenliste zeigt pro Kampagne aggregierte Settlement-KPIs und oeffnet bei Bedarf die gefilterte Abrechnungsansicht.
- Geschaeftlicher Nutzen: Offene oder verbuchte Ernteabrechnungen sind erstmals je Kampagne sichtbar, ohne Listen manuell auszuwerten.

## 3. Start / Trigger
- Startbedingung: Kampagnen und erste Settlements liegen vor.
- Ausloeser: Anwender oeffnet `Erntefenster-Konfiguration` oder klickt `Settlement-Abschluss pruefen`.
- Startpunkt-Typ:
  - [x] Standardstart
  - [ ] Alternativstart
  - [ ] Externer Import
  - [x] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: UI in `erntefenster-konfig.tsx`

## 4. Vorbedingungen
- Muss vorhanden sein: Erntefenster-Kampagnen aus `/api/v1/admin/erntefenster-campaigns`
- Muss geprueft sein: Settlements muessen `created_at`, `status`, `approval_status`, `net_amount_eur`, `total_deductions_eur` liefern.
- Ausschlussbedingungen: Keine Kampagnen oder keine lesbaren Settlements
- Abhaengige Vorprozesse: Ernte-Annahme und Settlement-Anlage (`VK-010` bis `VK-012`)

## 5. Eingaben
- Stammdaten: Kampagnenname, Zeitraum, Produktgruppen
- Bewegungsdaten: Settlement-Datum, Netto, Abzuege, Freigabestatus
- Pflichtfelder: `campaignStart`, `campaignEnd` fuer gefilterte Abschlusspruefung
- Optionale Felder: `campaignId`, `campaignName`
- Vorbelegte Werte: Query-Parameter werden aus der Kampagnenliste generiert
- Externe Datenquellen: `/api/v1/admin/erntefenster-campaigns`, `/api/v1/agrar/settlements`

## 6. UI / Systembezug
- Seite / Maske: `agrar/erntefenster-konfig.tsx`, `annahme/abrechnung.tsx`
- Dialog / Untermaske: keine
- Button / Aktion: `Settlement-Abschluss pruefen`
- Status vor Ausfuehrung: Kampagne sichtbar, Settlement-Liste ungefiltert
- Status nach Ausfuehrung: Settlement-Liste auf Kampagnenfenster eingegrenzt
- Sichtbare Felder: Settlements, Netto gesamt, Abzuege gesamt, offene Settlements, Kampagnenfenster
- Fehlende Felder / Aktionen: explizite Kampagnen-ID am Settlement, serverseitiger Abschlussstatus

## 7. Aktion
- Benutzeraktion: Kampagne lesen und CTA fuer Settlement-Abschluss klicken.
- Systemaktion: Settlements nach `created_at` im Kampagnenzeitraum filtern, Summen berechnen und in die Abrechnungsmaske navigieren.
- Automatische Folgeaktion: Abrechnungsmaske rendert nur die gefilterten Settlements.
- Synchron / asynchron: asynchron ueber React Query
- Notwendige Bestaetigung: keine

## 8. Geschaeftsregeln
- Validierungsregeln: Ein Settlement zaehlt nur, wenn `created_at` innerhalb `campaignStart` und `campaignEnd` liegt.
- Preis-/Mengenlogik: `net_amount_eur` und `total_deductions_eur` werden je Kampagne aufsummiert.
- Berechtigungen: keine slice-spezifischen Aenderungen
- Pflichtpruefungen: offene Settlements sind Datensaetze mit `status !== posted` oder `approval_status !== VERBUCHT`
- Sonderregeln: `Keine Settlements`, `Abschluss offen`, `Abschlussbereit`, `Laufend`
- Verbote / Sperren: kein eigener Abschluss-Writeback in diesem Slice

## 9. Ergebnisse
- Output-Daten: kampagnenbezogene KPI-Sicht und gefilterte Settlement-Liste
- Erzeugte Belege / Datensaetze: keine neuen Belege
- Geaenderte Status: keine persistenten Statusaenderungen
- Folgeprozess Standard: Settlement-Freigabe, FIBU-Verbuchung oder Storno in `abrechnung.tsx`
- Folgeprozess alternativ: Sandbox-Pruefung fuer denselben Kampagnenkontext

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: Gibt es Settlements im Kampagnenzeitraum?
- Moegliche Alternativen: `Keine Settlements`, `Abschluss offen`, `Abschlussbereit`, `Laufend`
- Ruecksprung moeglich zu: Kampagnenliste
- Schleife moeglich: ja, nach neuen oder verbuchten Settlements erneute Pruefung
- Abbruchpfad: keine Kampagnen oder leere Filterliste
- Sprungpfad: direkter Sprung in `annahme/abrechnung`
- Direkteinstieg moeglich: ja, ueber Query-Parameter auf `annahme/abrechnung`

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: Kampagne ohne Settlements, Settlement ausserhalb des Datumsfensters, Query ohne Start-/Enddatum
- Fachliche Sonderfaelle: ueberlappende Kampagnen koennen denselben Settlement technisch einschliessen
- Technische Sonderfaelle: fehlendes `created_at` fuehrt zum Ausschluss aus der Kampagnenaggregation
- Teilmengen / Splittung: mehrere Settlements innerhalb derselben Kampagne werden addiert
- Storno / Korrektur: erfolgt weiterhin in der Abrechnungsmaske
- Ruecknahme / Retoure: nicht relevant
- Preisabweichung: ueber bestehende Settlement-Pruefung sichtbar
- Bestandsproblem: nicht Teil dieses Slices
- Medienbruch moeglich: ja, solange kein dedizierter Kampagnenabschluss-Beleg existiert

## 12. CRUD-Pruefung
- Create moeglich: Kampagne anlegen ja, Abschlussbeleg nein
- Read / Suchen moeglich: ja
- Update moeglich: indirekt ueber bestehende Settlement-Aktionen
- Delete fachlich zulaessig: nein
- Storno statt Delete: ja, auf Settlement-Ebene
- Historisierung vorhanden: teilweise ueber bestehende Settlement-Historie
- Audit / Nachvollziehbarkeit: vorhanden fuer Einzel-Settlements, nicht fuer Kampagnenaggregation
- UI vollstaendig fuer CRUD: nein, Abschluss ist nur lesend/filternd
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Kampagne oeffnen, Gesamtabrechnung sehen, offene Settlements sofort erkennen und in den Abschluss wechseln.
- Ist-Umsetzung: KPI-Read-Modell und Filter-Navigation sind vorhanden; der Abschluss nutzt die bestehende Abrechnungsmaske.
- Abweichung: keine explizite Kampagnenverknuepfung auf Settlement-Ebene
- Fehlende Umsetzung: serverseitiger Kampagnenabschluss, Abschlussjournal oder dedizierter Abschlussstatus
- Unklare Umsetzung: fachliche Behandlung ueberlappender Kampagnen
- Workaround aktuell noetig: Datumsfenster als Proxy fuer Kampagnenzuordnung

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Die Zuordnung ueber `created_at` ist fachlich nur ein Proxy und kann bei Ueberlappungen oder Nachbuchungen falsch aggregieren.
- Auswirkung im Tagesgeschaeft: Kampagnenabschluss kann manuell nachgeprueft werden, ist aber noch nicht revisionssicher.
- Betroffene Rollen: Agrar-Sachbearbeitung, Betriebsleitung
- Betroffene Folgeprozesse: Freigabe, Verbuchung, Kampagnenreporting

## 15. Empfehlung
- Empfohlene Massnahme: Echte Kampagnenreferenz oder dedizierten Abschluss-Endpoint im Backend einfuehren.
- Fachlich: Kampagnenabschluss klar von Tages-Settlement-Pruefung abgrenzen.
- Technisch: Settlement-Contract um Kampagnenbezug erweitern und Aggregation serverseitig anbieten.
- UI-seitig: CTA spaeter um expliziten Abschlussbericht oder Export erweitern.
- Prioritaet der Umsetzung: hoch
- Sofortmassnahme: aktuelle UI-Filterung und KPI-Sicht nutzen
- Spaetere Optimierung: persistenter Abschlussstatus, Drilldown und Export

## 16. Annahmen
- Annahme 1: `created_at` ist derzeit die einzig belastbare Zuordnungsinformation zwischen Kampagne und Settlement.
- Annahme 2: Die bestehende Abrechnungsmaske ist der fachlich richtige Abschlussort fuer den Slice.
- Offene Fragen: Duerfen Kampagnenfenster ueberlappen, und falls ja, wie wird der Settlement-Kampagnenbezug fachlich definiert?

## 17. Testhinweise
- Positiver Testfall: Kampagne mit einem verbuchten Settlement im Zeitraum zeigt KPI und navigiert in eine Liste nur mit diesem Settlement.
- Negativer Testfall: Settlement ausserhalb des Zeitraums darf im Kampagnenabschluss nicht erscheinen.
- Edge-Case-Test: Kampagne ohne Settlements zeigt `Keine Settlements`.
- Browser-Use-Pruefschritt: In `Erntefenster-Konfiguration` CTA `Settlement-Abschluss pruefen` klicken und die KPI-/Filterkonsistenz in `annahme/abrechnung` pruefen.
- Erwartetes Ergebnis: Nur kampagnenrelevante Settlements sind sichtbar; offene Drafts bleiben als offen erkennbar.
