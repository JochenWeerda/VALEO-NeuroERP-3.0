# Browser-Use Checklists

## Zweck

Diese Checklisten schaerfen die UI-, CRUD- und Live-Betriebspruefung fuer Workflow-Cards.

Die priorisierte E2E-Matrix fuer die naechsten Abnahmelaeufe liegt in
[e2e-crud-acceptance-matrix-2026-04-24.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/quality-assurance/e2e-crud-acceptance-matrix-2026-04-24.md).

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

### VK-014: Settlement-Kampagnenreferenz

1. Aus `Erntefenster-Konfiguration` den CTA `Settlement-Abschluss pruefen` fuer eine Kampagne oeffnen.
2. In `Annahme-Abrechnung` ein neues Settlement im Kampagnenkontext speichern.
3. Erwartung: Save-Request enthaelt `campaign_id`.
4. Danach in die Kampagnenliste zurueckkehren und den Abschluss erneut oeffnen.
5. Erwartung: Das neue Settlement erscheint unter derselben Kampagne auch dann, wenn spaeter weitere Kampagnen mit aehnlichem Datumsfenster existieren.
6. Einen Datensatz mit abweichender `campaign_id` im selben Datumsfenster pruefen.
7. Erwartung: Er darf im aktuellen Kampagnenabschluss nicht auftauchen.
8. Legacy-Datensatz ohne `campaign_id` im gueltigen Datumsfenster pruefen.
9. Erwartung: Er bleibt ueber den Fallback sichtbar, bis ein Backfill existiert.

### VK-015: Settlement-Kampagnen-Backfill

1. `Erntefenster-Konfiguration` mit einer Kampagne oeffnen, in der mindestens ein Legacy-Settlement ohne `campaign_id` sichtbar ist.
2. Erwartung: Die Kampagnenkarte zeigt den Hinweis auf Alt-Settlements mit Datumsfenster-Fallback.
3. Auf `Alt-Daten zuordnen` klicken.
4. Erwartung: Es wird kein neuer Dialog geoeffnet; stattdessen erscheint ein Ergebnis-Toast.
5. Kampagnenkarte erneut laden.
6. Erwartung: Eindeutige Legacy-Datensaetze haben jetzt `campaign_id` und fallen nicht mehr nur ueber den Fallback auf.
7. Kampagne mit ueberlappendem Fenster oder bewusst ambigem Legacy-Datensatz pruefen.
8. Erwartung: Der Datensatz bleibt ohne neue Referenz; der Toast meldet offene Ambiguitaet statt Blindmigration.

### VK-016: Queue-CTA und Artikel-API

1. `Annahme-Warteschlange` oeffnen und einen Eintrag mit Status `abgeschlossen` pruefen.
2. Erwartung: Zusaetzlich zu `Bearbeiten` erscheint `Ernte-Annahme anlegen`.
3. CTA klicken.
4. Erwartung: Navigation nach `/agrar/ernte-annahme-erfassung` mit restart-sicherem Query-Handover.
5. In der Zielmaske Artikel-Nr., Bezeichnung, Kennzeichen und Bemerkungen pruefen.
6. Erwartung: `queueEntryId` ist in den Bemerkungen sichtbar; bei eindeutiger Artikelsuche ist eine kanonische Artikel-Nr. gesetzt.
7. Einen nicht abgeschlossenen Queue-Eintrag pruefen.
8. Erwartung: Dort erscheint kein CTA `Ernte-Annahme anlegen`.

### VK-017: Queue-Contract mit echter article_id

1. `LKW-Registrierung` oeffnen und den Lieferungs-Schritt erreichen.
2. Erwartung: Die Artikelauswahl kommt aus `/api/v1/articles` statt aus einer harten lokalen Liste.
3. Einen Artikel waehlen und die Registrierung abschliessen.
4. Erwartung: Der Queue-Eintrag ist angelegt; Folgepfade fuehren dieselbe `article_id` mit.
5. Den angelegten Eintrag in `Annahme-Warteschlange` oeffnen und ueber `Bearbeiten` in den Qualitaets-Check gehen.
6. Erwartung: Der Qualitaets-Check navigiert mit `articleId` in die Ernte-Annahme.
7. Alternativ den CTA `Ernte-Annahme anlegen` aus der Queue pruefen.
8. Erwartung: Die Ernte-Annahme zeigt die `article_id` direkt, ohne auf den Textlookup angewiesen zu sein.
9. `QR-Scanner` mit einem gueltigen Artikelcode pruefen.
10. Erwartung: Der POST bricht nicht mit 404; der Queue-Pfad nutzt denselben Registrierungs-Contract bzw. den Alias.

### VK-018: Klaerungsprozess gesperrte Ware

1. Einen Queue-Eintrag via QP mit Ergebnis `gesperrt` abschliessen.
2. Erwartung: Queue-Status zeigt `gesperrt`; es gibt einen CTA `Klaerung starten`.
3. CTA anklicken.
4. Erwartung: Klaerungsmaske oeffnet mit Kennzeichen, Lieferant, Artikel und QP-Referenz.
5. Ohne Begruendung speichern versuchen.
6. Erwartung: Validierung blockiert, Toast/Meldung sichtbar.
7. Entscheidung `Sonderfreigabe` mit Begruendung speichern.
8. Erwartung: Queue-Status aktualisiert sich; Handover in Ernte-Annahme ist moeglich.
9. Entscheidung `Endgueltig gesperrt` pruefen.
10. Erwartung: Eintrag bleibt gesperrt, kein Handover in die Ernte-Annahme.

### VK-019: Queue-Repair historische article_id

1. Einen Queue-Eintrag ohne `article_id` oeffnen.
2. Erwartung: CTA `Artikel reparieren` ist sichtbar.
3. CTA klicken.
4. Erwartung: Bei eindeutiger Zuordnung wird `article_id` gesetzt und die Queue refresht.
5. Eintrag mit mehrdeutigem Artikelnamen pruefen.
6. Erwartung: Kein Update, Hinweis-Toast mit Grund.
