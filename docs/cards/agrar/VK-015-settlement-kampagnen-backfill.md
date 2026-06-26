---
card_id: VK-015
chain: harvest-to-settlement
chain_step: 10
card_type: process-step
flow_spine: flow-spine-harvest-to-settlement
workflow_doc: docs/workflows/vk-015-settlement-kampagnen-backfill.md
---
# Card: VK-015 - Legacy-Settlements kampagnenbezogen nachziehen

## 1. Einordnung
- Prozessbereich: Agrar / Harvest-to-Settlement
- Workflow: Kampagnenabschluss / Datenrepair
- Teilprozess: Nachtraegliche Zuordnung historischer Settlements ohne `campaign_id`
- Rolle(n): Agrar-Sachbearbeitung, Betriebsleitung
- Prioritaet: hoch
- Status: abgeschlossen

## 2. Fachlicher Zweck
- Ziel des Schrittes: Alt-Datensaetze aus dem Legacy-Fallback kontrolliert auf eine echte Kampagnenreferenz heben.
- Fachliche Beschreibung: Auf der Kampagnenkarte wird ein Repair-CTA angeboten, der nur eindeutige Legacy-Settlements der ausgewaehlten Kampagne zuordnet.
- Geschaeftlicher Nutzen: Historische Kampagnen werden belastbarer auswertbar, ohne falsche Massenmigration zu riskieren.

## 3. Start / Trigger
- Startbedingung: Kampagnenkarte zeigt Legacy-Settlements ohne `campaign_id`.
- Ausloeser: Benutzer klickt `Alt-Daten zuordnen`.
- Startpunkt-Typ:
  - [x] Standardstart
  - [ ] Alternativstart
  - [ ] Externer Import
  - [x] Manueller Direktstart
  - [ ] Systemtrigger
- Quelle des Triggers: `packages/frontend-web/src/pages/agrar/erntefenster-konfig.tsx`

## 4. Vorbedingungen
- Muss vorhanden sein: Erntefenster-Kampagne in Tenant-Settings
- Muss geprueft sein: Settlement hat noch keine `campaign_id`
- Ausschlussbedingungen: Kampagnenfenster ungueltig oder Datensatz bereits referenziert
- Abhaengige Vorprozesse: `VK-013`, `VK-014`

## 5. Eingaben
- Stammdaten: `campaign_id`, Kampagnenzeitfenster
- Bewegungsdaten: Legacy-Settlement mit `created_at`
- Pflichtfelder: `campaign_id`
- Optionale Felder: `dry_run` im Backend-Contract
- Vorbelegte Werte: Kampagnen-ID aus der Kampagnenkarte
- Externe Datenquellen: Tenant-Settings `erntefenster_campaigns`, `AgrarSettlement`

## 6. UI / Systembezug
- Seite / Maske: `agrar/erntefenster-konfig.tsx`
- Dialog / Untermaske: keine
- Button / Aktion: `Alt-Daten zuordnen`
- Status vor Ausfuehrung: Kampagne mit Legacy-Hinweis
- Status nach Ausfuehrung: Legacy-Hinweis reduziert oder ambige Restfaelle bleiben sichtbar
- Sichtbare Felder: Legacy-Hinweis, Kampagnen-KPI, CTA
- Fehlende Felder / Aktionen: keine manuelle Umpraegung einzelner Datensaetze

## 7. Aktion
- Benutzeraktion: kampagnenbezogenen Repair ausloesen
- Systemaktion: Legacy-Settlements ohne Referenz pruefen und bei Eindeutigkeit `campaign_id` setzen
- Automatische Folgeaktion: Settlement-Summaries invalidieren und Kampagnenkarte neu rendern
- Synchron / asynchron: asynchron ueber API und React Query
- Notwendige Bestaetigung: keine

## 8. Geschaeftsregeln
- Validierungsregeln: Nur `campaign_id IS NULL` ist repair-faehig.
- Preis-/Mengenlogik: unveraendert
- Berechtigungen: keine zusaetzlichen Rollenerweiterungen im Slice
- Pflichtpruefungen: Kampagne muss existieren; Datumsfenster muss gueltig sein
- Sonderregeln: Bei ueberlappenden Kampagnen wird nicht migriert
- Verbote / Sperren: bestehende `campaign_id` nicht ueberschreiben

## 9. Ergebnisse
- Output-Daten: Repair-Ergebnis mit `updated_count`, `ambiguous_count`, `skipped_count`
- Erzeugte Belege / Datensaetze: keine
- Geaenderte Status: Settlement erhaelt ggf. `campaign_id`
- Folgeprozess Standard: Kampagnenabschluss arbeitet danach referenzbasierter
- Folgeprozess alternativ: ambige Faelle bleiben auf Legacy-Fallback

## 10. Verzweigungen / Loops / Rueckspruenge
- Entscheidungspunkt: Liegt der Legacy-Datensatz eindeutig nur in dieser Kampagne?
- Moegliche Alternativen: Zuordnen oder ambig offen lassen
- Ruecksprung moeglich zu: Kampagnenkarte erneut pruefen
- Schleife moeglich: Repair pro Kampagne wiederholen
- Abbruchpfad: keine Legacy-Datensaetze vorhanden
- Sprungpfad: keine
- Direkteinstieg moeglich: ja, ueber den CTA

## 11. Fehlerfaelle / Edge Cases
- Typische Fehler: Kampagne existiert nicht mehr, ungueltiges Zeitfenster, Settlement ohne `created_at`
- Fachliche Sonderfaelle: ueberlappende Kampagnenfenster
- Technische Sonderfaelle: Tenant-Settings ohne Kampagnenliste
- Teilmengen / Splittung: mehrere Legacy-Settlements derselben Kampagne sind zulaessig
- Storno / Korrektur: kein Teil dieses Slices
- Ruecknahme / Retoure: kein Teil dieses Slices
- Preisabweichung: unveraendert
- Bestandsproblem: kein Teil dieses Slices
- Medienbruch moeglich: nur fuer ambige Restfaelle

## 12. CRUD-Pruefung
- Create moeglich: nein
- Read / Suchen moeglich: ja, Kampagnenkarte zeigt Legacy-Hinweis
- Update moeglich: ja, kontrolliert fuer `campaign_id`
- Delete fachlich zulaessig: nein
- Storno statt Delete: unveraendert auf Settlement-Ebene
- Historisierung vorhanden: Settlement-Datensatz bleibt nachvollziehbar, Zuordnung wird persistiert
- Audit / Nachvollziehbarkeit: besser als reiner Datumsfenster-Fallback
- UI vollstaendig fuer CRUD: teilweise, bewusst nur Repair statt Voll-Editor
- Browser-Use pruefbar: ja

## 13. Soll-Ist-Bewertung
- Soll-Prozess: Historische Datensaetze koennen sicher nachgezogen werden.
- Ist-Umsetzung: Kampagnenbezogener Repair fuer eindeutige Faelle ist vorhanden.
- Abweichung: Ambige Faelle bleiben offen.
- Fehlende Umsetzung: tenantweiter Ambiguitaets-Report
- Unklare Umsetzung: keine
- Workaround aktuell noetig: nur fuer ueberlappende Kampagnen

## 14. Risiko
- Risiko-Level:
  - [ ] kritisch
  - [x] hoch
  - [ ] mittel
  - [ ] niedrig
- Risiko-Beschreibung: Ueberlappende Kampagnen brauchen weiterhin fachliche Klaerung ausserhalb des automatischen Repairs.
- Auswirkung im Tagesgeschaeft: Historische Kampagnen werden grossenteils sauber, einzelne Restfaelle bleiben manuell zu pruefen.
- Betroffene Rollen: Agrar-Sachbearbeitung, Betriebsleitung
- Betroffene Folgeprozesse: Kampagnenabschluss, Reporting

## 15. Empfehlung
- Empfohlene Massnahme: Repair-CTA auf Standardkarte beibehalten und anschliessend Queue-/Artikel-API priorisieren.
- Fachlich: Kampagnenfenster moeglichst nicht ueberlappen lassen.
- Technisch: spaeter Ambiguitaets-Report oder Dry-Run-Ansicht ergaenzen.
- UI-seitig: Legacy-Hinweis sichtbar halten, bis keine Restfaelle mehr vorhanden sind.
- Prioritaet der Umsetzung: hoch
- Sofortmassnahme: kampagnenbezogener Backfill fuer eindeutige Legacy-Datensaetze
- Spaetere Optimierung: tenantweite Repair-Uebersicht

## 16. Annahmen
- Annahme 1: `created_at` ist fuer Legacy-Daten die einzig belastbare Zuordnungsbasis.
- Annahme 2: Nicht-Zuordnen ist bei Kampagnenueberlappung fachlich sicherer als heuristisches Raten.
- Offene Fragen: Soll spaeter ein expliziter Freigabe- oder Dry-Run-Dialog fuer Repair-Aktionen ergaenzt werden?

## 17. Testhinweise
- Positiver Testfall: Legacy-Settlement im eindeutigen Kampagnenfenster wird per CTA referenziert.
- Negativer Testfall: Settlement in ueberlappenden Kampagnenfenstern bleibt ohne `campaign_id`.
- Edge-Case-Test: Legacy-Settlement ohne lesbares `created_at` wird uebersprungen.
- Browser-Use-Pruefschritt: Kampagnenkarte mit Legacy-Hinweis oeffnen, `Alt-Daten zuordnen` klicken, danach Karte erneut pruefen.
- Erwartetes Ergebnis: Eindeutige Alt-Daten erhalten `campaign_id`; ambige Faelle bleiben offen.
